"""Category distribution analysis for TikTok and X (v1 records, DE scope).

Computes, for each platform, the count and proportional share of each DSA
removal category using a single lazy scan and one .collect() call on the
aggregated result.  The proportion within each platform is derived via a
window expression over the grouped counts so that no full dataset is ever
materialised in memory.

Addresses RQ1 (Comparative Architecture): whether platform modality (video
vs. text) shapes the distribution of removal categories and affects the
comparability of DSA transparency reporting across platforms.

Usage:
    python 03_analysis/scripts/01_category_distribution.py [--data-dir PATH]
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

DEFAULT_DATA_ROOT = Path(r"C:\BA_Data")
LOG_FILE = (
    Path(__file__).resolve().parents[2]
    / "02_data_cleaning"
    / "logs"
    / "data_profile_after_preparation.md"
)

_BOUNDARY_BLEED: list[str] = [
    "OTHER_VIOLATION_TC",
    "CYBER_VIOLENCE",
    "UNSAFE_AND_PROHIBITED_PRODUCTS",
]

_PARQUET_FILES: dict[str, str] = {
    "TikTok": "tiktok_de_2025.parquet",
    "X": "x_de_2025.parquet",
}


def _scan_filtered(data_root: Path) -> pl.LazyFrame:
    frames: list[pl.LazyFrame] = []
    for _, fname in _PARQUET_FILES.items():
        path = data_root / fname
        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")
        schema_names = pl.scan_parquet(str(path)).collect_schema().names()
        has_api = "api_version" in schema_names
        load_cols = ["platform_name", "category"]
        if has_api:
            load_cols.append("api_version")
        lf = pl.scan_parquet(str(path)).select(load_cols)
        if has_api:
            lf = lf.filter(pl.col("api_version") == "v1").drop("api_version")
        frames.append(lf)
    return pl.concat(frames).filter(~pl.col("category").is_in(_BOUNDARY_BLEED))


def main(data_root: Path) -> None:
    lf = _scan_filtered(data_root)

    result = (
        lf.group_by(["platform_name", "category"])
        .agg(pl.len().alias("count"))
        .collect(engine="streaming")
        .with_columns(
            (pl.col("count") / pl.col("count").sum().over("platform_name") * 100)
            .alias("pct")
        )
        .sort(["platform_name", "count"], descending=[False, True])
    )

    print("\n=== Category Distribution (v1, DE scope) ===\n")
    with pl.Config(tbl_rows=100):
        print(result)

    # Derive top category per platform from the already-collected small frame
    top = (
        result
        .group_by("platform_name")
        .agg(
            pl.col("category").sort_by("count", descending=True).first().alias("top_category"),
            pl.col("pct").sort_by("count", descending=True).first().alias("top_pct"),
        )
        .sort("platform_name")
    )
    print("\n--- Top category per platform ---")
    print(top)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    table_rows = "\n".join(
        f"| {r['platform_name']} | {r['top_category']} | {r['top_pct']:.2f}% |"
        for r in top.iter_rows(named=True)
    )
    entry = (
        f"\n## Category Distribution — {ts}\n\n"
        f"Script: `03_analysis/scripts/01_category_distribution.py`\n\n"
        f"| platform_name | top_category | top_pct |\n"
        f"| --- | --- | --- |\n"
        f"{table_rows}\n"
    )

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.write_text("# Data Profile — After Preparation\n\n", encoding="utf-8")
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(entry)
    print(f"\nAppended to: {LOG_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Category distribution per platform.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_ROOT)
    args = parser.parse_args()
    main(args.data_dir)
