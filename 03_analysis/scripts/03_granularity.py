"""Reporting granularity analysis for TikTok and X (v1 records, DE scope).

Computes, using a single lazy scan and one .collect() call on the aggregated
result:

  1. Full distribution of decision_visibility values per platform (count + %).
  2. Summary metric: the proportion of rows where decision_visibility equals
     DECISION_VISIBILITY_OTHER versus all specific visibility values, per
     platform.  This proportion serves as the operationalised proxy for
     reporting granularity: a higher OTHER share indicates lower granularity.

The summary is derived from the already-aggregated in-memory result so that no
second scan of the parquet files is performed.

Note: the boundary-bleed category filter is NOT applied here because category
is not loaded for this script.  The decision_visibility distribution is
examined across all v1 records regardless of category.

Addresses RQ1 (Comparative Architecture) and RQ2 (Event Dynamics): whether
automation reliance correlates with a reduction in reporting granularity, and
whether granularity decreases during the election period.

Usage:
    python 03_analysis/scripts/03_granularity.py [--data-dir PATH]
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

_PARQUET_FILES: dict[str, str] = {
    "TikTok": "tiktok_de_2025.parquet",
    "X": "x_de_2025.parquet",
}

_OTHER_VISIBILITY = "DECISION_VISIBILITY_OTHER"  # matched via str.contains; values are stored as JSON arrays


def _scan_filtered(data_root: Path) -> pl.LazyFrame:
    frames: list[pl.LazyFrame] = []
    for _, fname in _PARQUET_FILES.items():
        path = data_root / fname
        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")
        schema_names = pl.scan_parquet(str(path)).collect_schema().names()
        has_api = "api_version" in schema_names
        load_cols = ["platform_name", "decision_visibility"]
        if has_api:
            load_cols.append("api_version")
        lf = pl.scan_parquet(str(path)).select(load_cols)
        if has_api:
            lf = lf.filter(pl.col("api_version") == "v1").drop("api_version")
        frames.append(lf)
    return pl.concat(frames)


def main(data_root: Path) -> None:
    lf = _scan_filtered(data_root)

    # Stream the group_by/agg to avoid materialising 830M rows; the window
    # proportion is applied after collect because .over() is not supported
    # by the streaming engine.
    dist = (
        lf.group_by(["platform_name", "decision_visibility"])
        .agg(pl.len().alias("count"))
        .collect(engine="streaming")
        .with_columns(
            (pl.col("count") / pl.col("count").sum().over("platform_name") * 100)
            .alias("pct")
        )
        .sort(["platform_name", "count"], descending=[False, True])
    )

    print("\n=== Decision Visibility Distribution (v1, DE scope) ===\n")
    with pl.Config(tbl_rows=50):
        print(dist)

    # Summary derived from the already-collected small frame — no second scan.
    # Null decision_visibility rows are excluded from the OTHER/SPECIFIC ratio
    # (they represent missing reporting, not a specific visibility decision).
    # decision_visibility is stored as a JSON array string ("["VALUE"]"), so
    # .str.contains() is used instead of == to match the substring.
    summary = (
        dist
        .filter(pl.col("decision_visibility").is_not_null())
        .with_columns(
            pl.when(pl.col("decision_visibility").str.contains(_OTHER_VISIBILITY))
            .then(pl.lit("OTHER"))
            .otherwise(pl.lit("SPECIFIC"))
            .alias("visibility_class")
        )
        .group_by(["platform_name", "visibility_class"])
        .agg(pl.col("count").sum().alias("count"))
        .with_columns(
            (pl.col("count") / pl.col("count").sum().over("platform_name") * 100)
            .alias("pct")
        )
        .filter(pl.col("visibility_class") == "OTHER")
        .sort("platform_name")
    )

    print(f"\n--- {_OTHER_VISIBILITY} share per platform ---")
    print(summary)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    dist_rows = "\n".join(
        f"| {r['platform_name']} | {r['decision_visibility']} | {r['count']:,} | {r['pct']:.2f}% |"
        for r in dist.iter_rows(named=True)
    )
    summary_rows = "\n".join(
        f"| {r['platform_name']} | {r['pct']:.2f}% |"
        for r in summary.iter_rows(named=True)
    )
    entry = (
        f"\n## Granularity (decision_visibility) — {ts}\n\n"
        f"Script: `03_analysis/scripts/03_granularity.py`\n\n"
        f"### Full distribution\n\n"
        f"| platform_name | decision_visibility | count | pct |\n"
        f"| --- | --- | --- | --- |\n"
        f"{dist_rows}\n\n"
        f"### DECISION_VISIBILITY_OTHER share\n\n"
        f"| platform_name | other_visibility_pct |\n"
        f"| --- | --- |\n"
        f"{summary_rows}\n"
    )

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.write_text("# Data Profile — After Preparation\n\n", encoding="utf-8")
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(entry)
    print(f"\nAppended to: {LOG_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Decision visibility distribution per platform."
    )
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_ROOT)
    args = parser.parse_args()
    main(args.data_dir)
