"""
Harmonize TikTok and X DSA parquet files using the provided category taxonomy.

Requirements implemented:
- Streaming Polars pipeline
- Many-to-one category mapping via taxonomy_mapping_v1_v2.csv
- Preserve original category as category_raw
- Add category_harmonized from mapping table
- Preserve original application_date as application_date_raw
- Add application_date_harmonized normalized to UTC and truncated to date
- Validate output after writing by scanning only category_harmonized for nulls
- Write unified per-platform harmonized parquet outputs to C:\BA_Data\
"""
from __future__ import annotations

from pathlib import Path

import polars as pl

ROOT = Path(r"C:\BA_Data")
MAPPING_PATH = Path(
    r"c:\Users\MoZa\OneDrive - Universität Paderborn\0_UPB\BA\Repo\Bachelor-Arbeit\03_harmonization\taxonomy_mapping_v1_v2.csv"
)
INPUTS = {
    "tiktok": ROOT / "tiktok_de_2025.parquet",
    "x": ROOT / "x_de_2025.parquet",
}
OUTPUTS = {
    "tiktok": ROOT / "tiktok_de_2025_harmonized.parquet",
    "x": ROOT / "x_de_2025_harmonized.parquet",
}


def load_mapping(path: Path) -> pl.DataFrame:
    return pl.read_csv(path)


def build_lazyframe(input_path: Path, mapping_df: pl.DataFrame) -> pl.LazyFrame:
    schema = pl.read_parquet_schema(str(input_path))
    app_type = schema.get("application_date")
    print(f"Detected application_date type for {input_path.name}: {app_type}")

    if app_type == pl.Date:
        app_date_expr = pl.col("application_date")
    elif app_type == pl.Datetime:
        app_date_expr = pl.col("application_date").dt.replace_time_zone("UTC").dt.date()
    elif app_type == pl.String:
        app_date_expr = (
            pl.col("application_date")
            .str.to_datetime(strict=False)
            .dt.replace_time_zone("UTC")
            .dt.date()
        )
    else:
        raise TypeError(f"Unsupported application_date type: {app_type}")

    return (
        pl.scan_parquet(str(input_path))
        .with_columns(
            category_raw=pl.col("category"),
            application_date_raw=pl.col("application_date").dt.date(),
        )
        .join(
            mapping_df.lazy().select(
                [
                    pl.col("original_category").alias("category_raw"),
                    pl.col("super_cluster").alias("category_harmonized"),
                ]
            ),
            on="category_raw",
            how="left",
        )
        .with_columns(
            application_date_harmonized=app_date_expr,
        )
        .drop(["category", "application_date"])
    )


def validate_output_file(output_path: Path) -> bool:
    unmapped = (
        pl.scan_parquet(str(output_path))
        .select(pl.col("category_harmonized").is_null().sum().alias("nulls"))
        .collect()
    )
    n = unmapped[0, "nulls"]
    if n > 0:
        print(f"WARNING: {n} unmapped records found in output. Check category_raw values.")
        return False

    print("Validation passed: no unmapped categories.")
    return True


def write_harmonized_output(lf: pl.LazyFrame, output_path: Path) -> None:
    # Keep the raw columns and add harmonized ones.
    lf.sink_parquet(str(output_path))


def process_platform(platform: str, input_path: Path, output_path: Path, mapping_df: pl.DataFrame) -> None:
    print(f"Processing {platform}: {input_path}")
    lf = build_lazyframe(input_path, mapping_df)
    write_harmonized_output(lf, output_path)
    print(f"Wrote: {output_path}")

    if not validate_output_file(output_path):
        raise SystemExit(1)


def main() -> None:
    if not MAPPING_PATH.exists():
        raise FileNotFoundError(f"Mapping table not found: {MAPPING_PATH}")

    mapping_df = load_mapping(MAPPING_PATH)

    for platform, input_path in INPUTS.items():
        if platform != "x":
            print(f"Skipping {platform} (already harmonized)")
            continue
        output_path = OUTPUTS[platform]
        if not input_path.exists():
            print(f"WARNING: missing input file {input_path}")
            continue
        process_platform(platform, input_path, output_path, mapping_df)


if __name__ == "__main__":
    main()
