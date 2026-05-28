"""Batch column selection script for DSA parquet dataset reduction.

This script processes daily-chunked parquet files from the DSA database
(stored as part-*.parquet files under daily_dumps_chunked/) and selects
only the thesis-relevant 9 columns for downstream analysis.

The script supports both:
  - Copying selected columns to a new output directory (default)
  - In-place replacement of the original part files (with backup recommended)

Usage examples:
  # Dry run to preview files to be processed
  python batch_select_columns.py --input-root C:/DSA-Data \
    --output-root 02_data_cleaning/data_intermediate --platform tiktok___full --dry-run

  # Process TikTok files and write to output folder
  python batch_select_columns.py --input-root C:/DSA-Data \
    --output-root 02_data_cleaning/data_intermediate --platform tiktok___full

  # Process only files from January 2025
  python batch_select_columns.py --input-root C:/DSA-Data \
    --output-root 02_data_cleaning/data_intermediate --platform tiktok___full \
    --day-prefix sor-tiktok-2025-01
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd

# Columns selected for thesis-relevant analysis from the full DSA schema.
# These 9 columns capture decision classification, platform metadata, and decision visibility.
KEEP_COLUMNS = [
    "uuid",
    "category",
    "content_type",
    "automated_detection",
    "automated_decision",
    "territorial_scope",
    "application_date",
    "platform_name",
    "decision_visibility",
]


def iter_day_folders(chunked_root: Path) -> Iterable[Path]:
    """Yield daily dump folders in sorted order.
    
    Args:
        chunked_root: Path to the daily_dumps_chunked directory.
    
    Yields:
        Paths to subdirectories (each representing a day of dumps).
    """
    # Sort alphabetically so that folders process in date order (e.g., sor-tiktok-2025-01-01, ...)
    for path in sorted(chunked_root.iterdir()):
        if path.is_dir():
            yield path


def iter_part_files(day_folder: Path) -> Iterable[Path]:
    """Yield parquet part files from a daily folder in sorted order.
    
    Args:
        day_folder: Path to a daily dump folder (e.g., sor-tiktok-2025-01-01).
    
    Yields:
        Paths to part-*.parquet files in sorted order.
    """
    # Each daily folder contains one or more part-*.parquet files (split for manageability).
    for path in sorted(day_folder.glob("part-*.parquet")):
        if path.is_file():
            yield path


def process_part(
    source_file: Path,
    output_file: Path,
    keep_columns: list[str],
    overwrite: bool,
    in_place_replace: bool,
) -> dict:
    """Process a single parquet part file: select columns and write output.
    
    Handles three main workflows:
      1. Copy-to-output (default): Read source, select columns, write to output location.
      2. In-place replace: Write reduced file to temporary location, then replace original.
      3. Skip logic: Skip existing outputs unless --overwrite is set.
    
    Args:
        source_file: Full path to the part-*.parquet file to process.
        output_file: Destination path for the reduced parquet output (or source if in_place_replace).
        keep_columns: List of column names to retain from the source file.
        overwrite: If True, reprocess even if output already exists.
        in_place_replace: If True, replace source file in-place; otherwise write to output_file.
    
    Returns:
        Dictionary with keys:
          - source_file, output_file: str, file paths
          - status: str, one of 'processed', 'replaced_in_place', 'skipped_exists',
            'skipped_already_reduced', 'error_missing_columns:...'
          - rows, cols_in, cols_out, dropped_cols: int or None (counts of records/columns)
    """
    # Skip if output already exists and overwrite is False (copy-to-output mode).
    if not in_place_replace and output_file.exists() and not overwrite:
        return {
            "source_file": str(source_file),
            "output_file": str(output_file),
            "status": "skipped_exists",
            "rows": None,
            "cols_in": None,
            "cols_out": None,
            "dropped_cols": None,
        }

    # Load the full parquet file from disk.
    df = pd.read_parquet(source_file)

    # Validate that all required columns exist in the source file.
    missing = [c for c in keep_columns if c not in df.columns]
    if missing:
        return {
            "source_file": str(source_file),
            "output_file": str(output_file),
            "status": f"error_missing_columns:{','.join(missing)}",
            "rows": None,
            "cols_in": len(df.columns),
            "cols_out": None,
            "dropped_cols": None,
        }

    # Select only the thesis-relevant columns.
    selected = df[keep_columns].copy()

    if in_place_replace:
        # In-place mode: check if the file is already reduced; if so, skip unless --overwrite.
        if list(df.columns) == keep_columns and not overwrite:
            return {
                "source_file": str(source_file),
                "output_file": str(source_file),
                "status": "skipped_already_reduced",
                "rows": len(df),
                "cols_in": len(df.columns),
                "cols_out": len(df.columns),
                "dropped_cols": 0,
            }

        # Write to a temporary file first, then atomically replace the original.
        # This protects against corruption if the process is interrupted.
        temp_file = source_file.with_suffix(source_file.suffix + ".tmp")
        selected.to_parquet(temp_file, index=False)
        temp_file.replace(source_file)
        target_file = source_file
        status = "replaced_in_place"
    else:
        # Copy-to-output mode: write the selected columns to the output location.
        output_file.parent.mkdir(parents=True, exist_ok=True)
        selected.to_parquet(output_file, index=False)
        target_file = output_file
        status = "processed"

    return {
        "source_file": str(source_file),
        "output_file": str(target_file),
        "status": status,
        "rows": len(selected),
        "cols_in": len(df.columns),
        "cols_out": len(selected.columns),
        "dropped_cols": len(df.columns) - len(selected.columns),
    }


def main() -> None:
    """Parse CLI arguments and orchestrate batch column selection.
    
    Discovers all daily folders under daily_dumps_chunked, iterates through their
    part-*.parquet files, and applies column selection. Outputs a summary CSV
    tracking the status of each file processed (or discovered in dry-run mode).
    """
    parser = argparse.ArgumentParser(
        description="Select thesis-relevant columns from DSA chunked parquet files."
    )
    parser.add_argument(
        "--input-root",
        type=Path,
        required=True,
        help="Root data path, e.g. C:/.../DSA-Data",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        required=True,
        help="Output base folder in the repository, e.g. 02_data_cleaning/data_intermediate",
    )
    parser.add_argument(
        "--platform",
        type=str,
        choices=["tiktok___full", "x___full"],
        required=True,
        help="Platform folder name under input-root.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite already processed output files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List discovered files and write no outputs.",
    )
    parser.add_argument(
        "--max-parts",
        type=int,
        default=None,
        help="Optional cap for processed part files (useful for testing).",
    )
    parser.add_argument(
        "--day-prefix",
        type=str,
        default=None,
        help=(
            "Optional day-folder prefix filter, e.g. 'sor-tiktok-2025-01' "
            "or 'sor-x-2025-02'."
        ),
    )
    parser.add_argument(
        "--in-place-replace",
        action="store_true",
        help=(
            "Replace original part-*.parquet files with reduced 9-column versions. "
            "Use only when you have a full backup."
        ),
    )

    args = parser.parse_args()

    # Construct the path to the chunked data directory.
    # Expected structure: {input_root}/{platform}/daily_dumps_chunked/
    platform_root = args.input_root / args.platform
    chunked_root = platform_root / "daily_dumps_chunked"

    if not chunked_root.exists():
        raise FileNotFoundError(f"Chunked folder not found: {chunked_root}")

    # Output directory mirrors the platform name for clarity and reproducibility.
    # Files are reduced from full schema to 9-column format.
    output_platform_root = args.output_root / f"{args.platform}_selected_9cols"
    summary_rows: list[dict] = []

    processed_count = 0
    discovered_count = 0

    # Iterate through all daily folders, optionally filtered by day_prefix.
    for day_folder in iter_day_folders(chunked_root):
        # Apply optional day prefix filter (e.g., 'sor-tiktok-2025-01' for January 2025 TikTok data).
        if args.day_prefix and not day_folder.name.startswith(args.day_prefix):
            continue

        # Process each parquet part file in the day folder.
        for part_file in iter_part_files(day_folder):
            discovered_count += 1
            # Preserve the relative folder structure (year/month/day) in the output.
            rel = part_file.relative_to(chunked_root)
            out_file = part_file if args.in_place_replace else output_platform_root / rel

            if args.dry_run:
                # In dry-run mode, just record what would be processed without writing.
                summary_rows.append(
                    {
                        "source_file": str(part_file),
                        "output_file": str(out_file),
                        "status": "dry_run",
                        "rows": None,
                        "cols_in": None,
                        "cols_out": None,
                        "dropped_cols": None,
                    }
                )
            else:
                # Actually process the file.
                result = process_part(
                    source_file=part_file,
                    output_file=out_file,
                    keep_columns=KEEP_COLUMNS,
                    overwrite=args.overwrite,
                    in_place_replace=args.in_place_replace,
                )
                summary_rows.append(result)
                # Count successful completions (exclude skips and errors).
                if result["status"] in ("processed", "replaced_in_place"):
                    processed_count += 1

            # Optional cap on the number of files to process (useful for testing small batches).
            if args.max_parts is not None and discovered_count >= args.max_parts:
                break
        if args.max_parts is not None and discovered_count >= args.max_parts:
            break

    # Collect all results into a summary DataFrame and write to CSV for auditability.
    summary_df = pd.DataFrame(summary_rows)
    output_platform_root.mkdir(parents=True, exist_ok=True)

    # Differentiate dry-run summaries from actual processing summaries.
    summary_name = (
        f"{args.platform}_selected_9cols_dry_run_summary.csv"
        if args.dry_run
        else f"{args.platform}_selected_9cols_processing_summary.csv"
    )
    summary_path = output_platform_root / summary_name
    summary_df.to_csv(summary_path, index=False)

    # Print summary statistics to console.
    print(f"Platform: {args.platform}")
    print(f"In-place replace: {args.in_place_replace}")
    if args.day_prefix:
        print(f"Day prefix filter: {args.day_prefix}")
    print(f"Discovered part files: {discovered_count}")
    if not args.dry_run:
        print(f"Processed part files: {processed_count}")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
