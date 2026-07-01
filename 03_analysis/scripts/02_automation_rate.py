"""Automation rate analysis for TikTok and X (v1 records, DE scope).

Computes two things using separate lazy scans, each resolved by one .collect()
call on the aggregated result:

  1. Overall proportion of FULLY_AUTOMATED decisions within each platform.
  2. Proportion of FULLY_AUTOMATED decisions broken down by platform x category.

Addresses RQ1 (Comparative Architecture): whether platform modality drives
differences in automation reliance, and whether higher automation corresponds
to reduced reporting granularity.  Also provides the annual baseline for RQ2
(Event Dynamics): comparing automation rates during the election window against
this full-year figure.

Usage:
    python 03_analysis/scripts/02_automation_rate.py [--data-dir PATH]
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

_FULLY_AUTOMATED = "AUTOMATED_DECISION_FULLY"


def _scan_filtered(data_root: Path) -> pl.LazyFrame:
    frames: list[pl.LazyFrame] = []
    for _, fname in _PARQUET_FILES.items():
        path = data_root / fname
        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")
        schema_names = pl.scan_parquet(str(path)).collect_schema().names()
        has_api = "api_version" in schema_names
        load_cols = ["platform_name", "category", "automated_decision"]
        if has_api:
            load_cols.append("api_version")
        lf = pl.scan_parquet(str(path)).select(load_cols)
        if has_api:
            lf = lf.filter(pl.col("api_version") == "v1").drop("api_version")
        frames.append(lf)
    return pl.concat(frames).filter(~pl.col("category").is_in(_BOUNDARY_BLEED))


def main(data_root: Path) -> None:
    lf = _scan_filtered(data_root)

    # --- Computation 1: overall FULLY_AUTOMATED rate per platform ---
    overall = (
        lf.group_by(["platform_name", "automated_decision"])
        .agg(pl.len().alias("count"))
        .collect(engine="streaming")
        .with_columns(
            (pl.col("count") / pl.col("count").sum().over("platform_name") * 100)
            .alias("pct")
        )
        .filter(pl.col("automated_decision") == _FULLY_AUTOMATED)
        .select(["platform_name", "automated_decision", "count", "pct"])
        .sort("platform_name")
    )

    print("\n=== Overall Automation Rate (v1, DE scope) ===\n")
    print(overall)

    # --- Computation 2: FULLY_AUTOMATED rate per platform × category ---
    by_category = (
        lf.group_by(["platform_name", "category", "automated_decision"])
        .agg(pl.len().alias("count"))
        .collect(engine="streaming")
        .with_columns(
            (
                pl.col("count")
                / pl.col("count").sum().over(["platform_name", "category"])
                * 100
            ).alias("pct")
        )
        .filter(pl.col("automated_decision") == _FULLY_AUTOMATED)
        .select(["platform_name", "category", "automated_decision", "count", "pct"])
        .sort(["platform_name", "pct"], descending=[False, True])
    )

    print("\n=== Automation Rate by Category (v1, DE scope) ===\n")
    with pl.Config(tbl_rows=100):
        print(by_category)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    overall_rows = "\n".join(
        f"| {r['platform_name']} | {r['pct']:.2f}% |"
        for r in overall.iter_rows(named=True)
    )
    by_cat_rows = "\n".join(
        f"| {r['platform_name']} | {r['category']} | {r['pct']:.2f}% |"
        for r in by_category.iter_rows(named=True)
    )
    entry = (
        f"\n## Automation Rate — {ts}\n\n"
        f"Script: `03_analysis/scripts/02_automation_rate.py`\n\n"
        f"### Overall FULLY_AUTOMATED rate per platform\n\n"
        f"| platform_name | fully_automated_pct |\n"
        f"| --- | --- |\n"
        f"{overall_rows}\n\n"
        f"### FULLY_AUTOMATED rate per platform x category\n\n"
        f"| platform_name | category | fully_automated_pct |\n"
        f"| --- | --- | --- |\n"
        f"{by_cat_rows}\n"
    )

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.write_text("# Data Profile — After Preparation\n\n", encoding="utf-8")
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(entry)
    print(f"\nAppended to: {LOG_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automation rate per platform and category.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_ROOT)
    args = parser.parse_args()
    main(args.data_dir)
