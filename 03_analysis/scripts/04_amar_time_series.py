"""Monthly moderation intensity time series normalised by AMAR for TikTok
and X (v1 records, DE scope).

AMAR (Average Monthly Active Recipients) values are DSA-mandated platform
disclosures for H1 2025:
  - TikTok reports a single H1 figure applied uniformly across all six months.
  - X reports separate Q1 (Jan-Mar) and Q2 (Apr-Jun) figures.

Computes, using a single lazy scan and one .collect() on the monthly
aggregate, the normalised intensity rate:

    intensity_rate = (monthly_count / AMAR) * 1_000_000

The AMAR join is performed on the already-collected small frame (at most
12 rows: 6 months x 2 platforms), so no second parquet scan is needed.

Addresses RQ2 (Event Dynamics): whether the 2025 German snap election
(23 Feb) triggers a measurable spike in normalised moderation intensity
relative to the monthly baseline across the H1 v1 period.

Usage:
    python 03_analysis/scripts/04_amar_time_series.py [--data-dir PATH]
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

AMAR: dict[str, dict[str, int]] = {
    "TikTok": {
        "2025-01": 25_700_000, "2025-02": 25_700_000,
        "2025-03": 25_700_000, "2025-04": 25_700_000,
        "2025-05": 25_700_000, "2025-06": 25_700_000,
    },
    "X": {
        "2025-01": 15_598_407, "2025-02": 15_598_407,
        "2025-03": 15_598_407, "2025-04": 14_929_142,
        "2025-05": 14_929_142, "2025-06": 14_929_142,
    },
}


def _scan_filtered(data_root: Path) -> pl.LazyFrame:
    frames: list[pl.LazyFrame] = []
    for _, fname in _PARQUET_FILES.items():
        path = data_root / fname
        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")
        schema_names = pl.scan_parquet(str(path)).collect_schema().names()
        has_api = "api_version" in schema_names
        load_cols = ["platform_name", "application_date"]
        if has_api:
            load_cols.append("api_version")
        lf = pl.scan_parquet(str(path)).select(load_cols)
        if has_api:
            lf = lf.filter(pl.col("api_version") == "v1").drop("api_version")
        frames.append(lf)
    return pl.concat(frames)


def compute_monthly_intensity(data_root: Path = DEFAULT_DATA_ROOT) -> pl.DataFrame:
    """Return the AMAR-normalised monthly intensity table.

    Columns: platform_name, month (str "YYYY-MM"), raw_count, amar,
    intensity_rate.  At most 12 rows (6 months x 2 platforms).
    """
    lf = _scan_filtered(data_root)

    monthly = (
        lf.with_columns(
            pl.col("application_date").dt.strftime("%Y-%m").alias("month")
        )
        .group_by(["platform_name", "month"])
        .agg(pl.len().alias("raw_count"))
        .collect(engine="streaming")
    )

    amar_df = pl.DataFrame([
        {"platform_name": platform, "month": month, "amar": value}
        for platform, months in AMAR.items()
        for month, value in months.items()
    ])

    return (
        monthly
        .join(amar_df, on=["platform_name", "month"], how="inner")
        .with_columns(
            (pl.col("raw_count") / pl.col("amar") * 1_000_000)
            .round(2)
            .alias("intensity_rate")
        )
        .sort(["platform_name", "month"])
    )


def main(data_root: Path) -> None:
    result = compute_monthly_intensity(data_root)

    print("\n=== Monthly Moderation Intensity (v1, DE scope) ===\n")
    print(result)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    table_rows = "\n".join(
        f"| {r['platform_name']} | {r['month']} | {r['raw_count']:,} | {r['amar']:,} | {r['intensity_rate']:.2f} |"
        for r in result.iter_rows(named=True)
    )
    entry = (
        f"\n## Monthly Intensity (AMAR-normalised) — {ts}\n\n"
        f"Script: `03_analysis/scripts/04_amar_time_series.py`\n\n"
        f"| platform_name | month | raw_count | amar | intensity_rate |\n"
        f"| --- | --- | --- | --- | --- |\n"
        f"{table_rows}\n"
    )

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.write_text("# Data Profile — After Preparation\n\n", encoding="utf-8")
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(entry)
    print(f"\nAppended to: {LOG_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Monthly moderation intensity normalised by AMAR."
    )
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_ROOT)
    args = parser.parse_args()
    main(args.data_dir)
