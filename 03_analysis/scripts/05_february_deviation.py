"""February deviation analysis: moderation intensity and automation rate
shift between January and February 2025 (v1 records, DE scope).

Imports Script 4's normalised monthly intensity table via importlib (the
filename starts with a digit, making standard import syntax invalid) to
avoid duplicating the AMAR computation logic.

The automation-rate deviation is computed inline with a fresh lazy scan
limited to January and February records only, so only two months of data
are aggregated — the scan predicate is pushed into the parquet reader.

Computes two deviation tables, each with columns:
    platform_name | jan_rate | feb_rate | pct_deviation

  1. Normalised intensity deviation:
         pct_deviation = ((feb_intensity - jan_intensity) / jan_intensity) * 100

  2. FULLY_AUTOMATED proportion deviation:
         pct_deviation = ((feb_auto_pct - jan_auto_pct) / jan_auto_pct) * 100

Addresses RQ2 (Event Dynamics): the German snap election took place on
23 February 2025.  A positive pct_deviation in both metrics for February
relative to January is the expected signature of event-driven moderation
escalation and increased automation reliance.

Usage:
    python 03_analysis/scripts/05_february_deviation.py [--data-dir PATH]
"""
from __future__ import annotations

import argparse
import importlib.util
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

# ---------------------------------------------------------------------------
# Import Script 4's compute function without duplicating computation logic.
# Standard import syntax is invalid because the filename starts with "04_".
# ---------------------------------------------------------------------------
_S4_PATH = Path(__file__).parent / "04_amar_time_series.py"
_s4_spec = importlib.util.spec_from_file_location("amar_time_series", _S4_PATH)
_s4_mod = importlib.util.module_from_spec(_s4_spec)
_s4_spec.loader.exec_module(_s4_mod)

compute_monthly_intensity: callable = _s4_mod.compute_monthly_intensity
DEFAULT_DATA_ROOT: Path = _s4_mod.DEFAULT_DATA_ROOT

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

_BOUNDARY_BLEED: list[str] = [
    "OTHER_VIOLATION_TC",
    "CYBER_VIOLENCE",
    "UNSAFE_AND_PROHIBITED_PRODUCTS",
]

_FULLY_AUTOMATED = "AUTOMATED_DECISION_FULLY"
_JAN = "2025-01"
_FEB = "2025-02"


def _deviation_table(monthly: pl.DataFrame, rate_col: str) -> pl.DataFrame:
    """Pivot jan/feb rows into columns and compute percentage deviation."""
    jan = (
        monthly
        .filter(pl.col("month") == _JAN)
        .select(["platform_name", pl.col(rate_col).alias("jan_rate")])
    )
    feb = (
        monthly
        .filter(pl.col("month") == _FEB)
        .select(["platform_name", pl.col(rate_col).alias("feb_rate")])
    )
    return (
        jan.join(feb, on="platform_name", how="inner")
        .with_columns(
            ((pl.col("feb_rate") - pl.col("jan_rate")) / pl.col("jan_rate") * 100)
            .round(2)
            .alias("pct_deviation")
        )
        .sort("platform_name")
    )


def _compute_auto_monthly(data_root: Path) -> pl.DataFrame:
    """Lazy scan for FULLY_AUTOMATED proportion in Jan and Feb only."""
    frames: list[pl.LazyFrame] = []
    for _, fname in _PARQUET_FILES.items():
        path = data_root / fname
        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")
        schema_names = pl.scan_parquet(str(path)).collect_schema().names()
        has_api = "api_version" in schema_names
        load_cols = ["platform_name", "category", "automated_decision", "application_date"]
        if has_api:
            load_cols.append("api_version")
        lf = pl.scan_parquet(str(path)).select(load_cols)
        if has_api:
            lf = lf.filter(pl.col("api_version") == "v1").drop("api_version")
        frames.append(lf)

    return (
        pl.concat(frames)
        .filter(~pl.col("category").is_in(_BOUNDARY_BLEED))
        .with_columns(
            pl.col("application_date").dt.strftime("%Y-%m").alias("month")
        )
        .filter(pl.col("month").is_in([_JAN, _FEB]))
        .group_by(["platform_name", "month", "automated_decision"])
        .agg(pl.len().alias("count"))
        .collect(engine="streaming")
        .with_columns(
            (
                pl.col("count")
                / pl.col("count").sum().over(["platform_name", "month"])
                * 100
            ).alias("auto_pct")
        )
        .filter(pl.col("automated_decision") == _FULLY_AUTOMATED)
        .select(["platform_name", "month", "auto_pct"])
    )


def _fmt_rows(df: pl.DataFrame) -> str:
    return "\n".join(
        f"| {r['platform_name']} | {r['jan_rate']:.4f} | {r['feb_rate']:.4f} | {r['pct_deviation']:+.2f}% |"
        for r in df.iter_rows(named=True)
    )


def main(data_root: Path) -> None:
    # --- 1: Intensity deviation (via Script 4's function) ---
    intensity = compute_monthly_intensity(data_root)
    intensity_dev = _deviation_table(intensity, "intensity_rate")

    print("\n=== February Intensity Deviation (v1, DE scope) ===\n")
    print(intensity_dev)

    # --- 2: Automation-rate deviation (inline lazy computation) ---
    auto_monthly = _compute_auto_monthly(data_root)
    auto_dev = _deviation_table(auto_monthly, "auto_pct")

    print("\n=== February Automation-Rate Deviation (v1, DE scope) ===\n")
    print(auto_dev)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = (
        f"\n## February Deviation (vs January baseline) — {ts}\n\n"
        f"Script: `03_analysis/scripts/05_february_deviation.py`\n\n"
        f"### Moderation intensity (AMAR-normalised, per million recipients)\n\n"
        f"| platform_name | jan_rate | feb_rate | pct_deviation |\n"
        f"| --- | --- | --- | --- |\n"
        f"{_fmt_rows(intensity_dev)}\n\n"
        f"### FULLY_AUTOMATED proportion\n\n"
        f"| platform_name | jan_rate | feb_rate | pct_deviation |\n"
        f"| --- | --- | --- | --- |\n"
        f"{_fmt_rows(auto_dev)}\n"
    )

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.write_text("# Data Profile — After Preparation\n\n", encoding="utf-8")
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(entry)
    print(f"\nAppended to: {LOG_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="February vs January deviation in intensity and automation rate."
    )
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_ROOT)
    args = parser.parse_args()
    main(args.data_dir)
