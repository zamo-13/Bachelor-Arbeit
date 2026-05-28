"""
Polars streaming pipeline to count, filter by DE from separate TikTok and X
sources, assign api_version, write parquet outputs incrementally, and delete
only original files from the two subdirectory trees.

Usage:
    python filter_split_save_de_polars.py

Requirements:
    - polars

This script avoids collect() on the large source inputs. Counts are obtained by
streaming a tiny aggregation to temporary parquet files and then reading the
small result.
"""

from __future__ import annotations

import datetime
import os
from pathlib import Path
import os
import tempfile
import argparse

import polars as pl

# Default data directory; can be overridden by env var BA_DATA_ROOT or CLI --data-dir
DEFAULT_DATA_DIR = Path(os.environ.get("BA_DATA_ROOT", r"C:\\BA_Data"))
DATA_PROFILE = Path(
    r"C:\Users\MoZa\OneDrive - Universität Paderborn\0_UPB\BA\Repo\Bachelor-Arbeit\02_data_cleaning\logs\data_profile.md"
)


def _stream_count(lf: pl.LazyFrame) -> int:
    fd, temp_name = tempfile.mkstemp(suffix=".parquet", dir=str(DATA_DIR))
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        lf.select(pl.len().alias("row_count")).sink_parquet(temp_path)
        result = pl.read_parquet(temp_path)
        return int(result["row_count"][0])
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _append_data_profile(
    script_name: str,
    tiktok_before: int,
    x_before: int,
    tiktok_after: int,
    x_after: int,
    removed_count: int,
) -> None:
    today = datetime.date.today().isoformat()
    log_lines = [
        "",
        f"- Date: {today}",
        f"- Description: Streaming Polars DE filtering and split run ({script_name})",
        "- Result:",
        f"  - Total TikTok rows before filtering: {tiktok_before}",
        f"  - Total X rows before filtering: {x_before}",
        f"  - Combined total before filtering: {tiktok_before + x_before}",
        f"  - TikTok rows after DE filter: {tiktok_after}",
        f"  - X rows after DE filter: {x_after}",
        f"  - Output file written: {OUT_TIKTOK}",
        f"  - Output file written: {OUT_X}",
        f"  - Number of original files deleted: {removed_count}",
    ]

    DATA_PROFILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PROFILE.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(log_lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Filter and merge DE records into yearly parquet outputs")
    parser.add_argument("--data-dir", type=str, default=None, help="Path to BA data root (overrides BA_DATA_ROOT env var)")
    args = parser.parse_args()

    data_dir = Path(args.data_dir) if args.data_dir else DEFAULT_DATA_DIR
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        return 1

    pattern_tiktok = str(data_dir / "tiktok___full/daily_dumps_chunked/**/*.parquet")
    pattern_x = str(data_dir / "x___full/daily_dumps_chunked/**/*.parquet")
    out_tiktok = data_dir / "tiktok_de_2025.parquet"
    out_x = data_dir / "x_de_2025.parquet"

    lf_tiktok_all = pl.scan_parquet(pattern_tiktok)
    lf_x_all = pl.scan_parquet(pattern_x)

    tiktok_total_count = _stream_count(lf_tiktok_all)
    x_total_count = _stream_count(lf_x_all)
    print(f"Total rows (TikTok, pre-filter): {tiktok_total_count}")
    print(f"Total rows (X, pre-filter): {x_total_count}")
    print(f"Total rows (combined, pre-filter): {tiktok_total_count + x_total_count}")

    cutoff = datetime.date(2025, 7, 1)
    api_expr = (
        pl.when(
            pl.col("application_date").dt.date() < pl.lit(cutoff)
        )
        .then(pl.lit("v1"))
        .otherwise(pl.lit("v2"))
        .alias("api_version")
    )

    # TikTok
    lf_tiktok = (
        pl.scan_parquet(pattern_tiktok)
        .filter(pl.col("territorial_scope").str.contains("DE"))
        .with_columns(api_expr)
    )
    lf_tiktok.sink_parquet(str(out_tiktok))

    # X
    lf_x = (
        pl.scan_parquet(pattern_x)
        .filter(pl.col("territorial_scope").str.contains("DE"))
        .with_columns(api_expr)
    )
    lf_x.sink_parquet(str(out_x))

    tiktok_after_count = _stream_count(pl.scan_parquet(str(out_tiktok)))
    x_after_count = _stream_count(pl.scan_parquet(str(out_x)))
    print(f"Rows after territorial_scope contains 'DE' (TikTok): {tiktok_after_count}")
    print(f"Rows after territorial_scope contains 'DE' (X): {x_after_count}")
    print(f"Rows after territorial_scope contains 'DE' (combined): {tiktok_after_count + x_after_count}")

    tiktok_dir = data_dir / "tiktok___full/daily_dumps_chunked"
    x_dir = data_dir / "x___full/daily_dumps_chunked"

    removed = []
    for subdir in [tiktok_dir, x_dir]:
        if not subdir.exists():
            continue
        for p in subdir.rglob("*.parquet"):
            try:
                file_size = p.stat().st_size
                if file_size <= 0:
                    print(f"Skipping empty file: {p}")
                    continue
                p.unlink()
                removed.append(str(p.relative_to(DATA_DIR)))
            except Exception as e:
                print(f"Failed to remove {p}: {e}")

    print(f"Removed {len(removed)} original parquet files from subdirectories.")
    if removed and len(removed) <= 20:
        for name in removed[:20]:
            print(f"- {name}")
        if len(removed) > 20:
            print(f"... and {len(removed) - 20} more files")

    _append_data_profile(
        Path(__file__).name,
        tiktok_total_count,
        x_total_count,
        tiktok_after_count,
        x_after_count,
        len(removed),
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
