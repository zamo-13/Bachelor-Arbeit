"""Low-memory streaming rename/drop for harmonized parquet files.

This script uses Polars lazy `scan_parquet` + `sink_parquet` to avoid
loading full datasets into memory. For each harmonized parquet file it:
  - creates a lazy pipeline that renames `application_date_raw` -> `application_date`
  - drops `application_date_harmonized`
  - writes to a temporary parquet file using streaming
  - atomically replaces the original file with the temp file

Run carefully: files are replaced in-place after successful write.
"""
from __future__ import annotations

from pathlib import Path
import sys
import polars as pl


ROOT = Path(r"C:\BA_Data")
FILES = [
    ROOT / "tiktok_de_2025_harmonized.parquet",
    ROOT / "x_de_2025_harmonized.parquet",
]


def process_file(path: Path) -> None:
    print(f"Processing: {path}")
    if not path.exists():
        print(f"  Skipping (not found): {path}")
        return

    tmp = path.with_suffix(path.suffix + ".tmp")

    # Build a lazy pipeline: rename application_date_raw -> application_date,
    # drop application_date_harmonized, keep all other columns unchanged.
    lf = (
        pl.scan_parquet(str(path))
        .with_columns(pl.col("application_date_raw").alias("application_date"))
        .drop(["application_date_raw", "application_date_harmonized"])
    )

    # Write streaming to a temporary file. This avoids collecting into memory.
    lf.sink_parquet(str(tmp))

    # Replace original file atomically
    tmp.replace(path)
    print(f"  Replaced: {path}")


def main() -> None:
    for f in FILES:
        try:
            process_file(f)
        except Exception as e:
            print(f"Error processing {f}: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
