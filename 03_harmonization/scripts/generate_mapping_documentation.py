r"""Generate markdown documentation for taxonomy harmonization mappings.

This script uses Polars lazy execution only. It scans the harmonized parquet
files in C:\BA_Data, computes per-category summaries for each platform/version
subset, and writes markdown documentation files under 03_harmonization/docs.

The script does not collect full datasets. It only materializes aggregate
results and the small mapping reference table required for documentation.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import polars as pl


ROOT = Path(r"C:\BA_Data")
REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "03_harmonization" / "docs"
MAPPING_PATH = REPO_ROOT / "03_harmonization" / "taxonomy_mapping_v1_v2.csv"

INPUTS = {
    "tiktok": ROOT / "tiktok_de_2025_harmonized.parquet",
    "x": ROOT / "x_de_2025_harmonized.parquet",
}

VERSION_VALUES = ("v1", "v2")

SUMMARY_COLUMNS = ["category_raw", "super_cluster", "record_count", "share_pct"]
MAPPING_COLUMNS = [
    "original_category",
    "api_version",
    "super_cluster",
    "mapping_type",
    "dsa_legal_basis",
    "notes",
]


@dataclass(frozen=True)
class SummaryResult:
    platform: str
    api_version: str
    output_path: Path
    total_records: int
    unique_categories: int


def escape_markdown(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", r"\|").replace("\n", " ")


def format_markdown_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(escape_markdown(row.get(column, "")) for column in columns) + " |")
    return "\n".join([header, separator, *body])


def ensure_output_dir() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)


def validate_inputs() -> None:
    missing = [path for path in INPUTS.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing harmonized parquet input(s): " + ", ".join(str(path) for path in missing))
    if not MAPPING_PATH.exists():
        raise FileNotFoundError(f"Missing mapping CSV: {MAPPING_PATH}")


def load_mapping_reference() -> pl.LazyFrame:
    return pl.scan_csv(str(MAPPING_PATH))


def build_subset_summary(input_path: Path, api_version: str) -> pl.LazyFrame:
    return (
        pl.scan_parquet(str(input_path))
        .filter(pl.col("api_version") == api_version)
        .group_by([pl.col("category_raw"), pl.col("category_harmonized").alias("super_cluster")])
        .agg(pl.len().alias("record_count"))
        .sort("record_count", descending=True)
    )


def compute_subset_stats(input_path: Path, api_version: str) -> tuple[int, int]:
    stats = (
        pl.scan_parquet(str(input_path))
        .filter(pl.col("api_version") == api_version)
        .select(
            [
                pl.len().alias("total_records"),
                pl.col("category_raw").n_unique().alias("unique_categories"),
            ]
        )
        .collect(engine="streaming")
    )
    return int(stats[0, "total_records"]), int(stats[0, "unique_categories"])


def compute_subset_table(input_path: Path, api_version: str) -> tuple[list[dict[str, object]], int, int]:
    total_records, unique_categories = compute_subset_stats(input_path, api_version)

    table_df = (
        build_subset_summary(input_path, api_version)
        .with_columns(
            share_pct=(pl.col("record_count") / pl.lit(total_records) * 100).round(4),
        )
        .select(SUMMARY_COLUMNS)
        .collect(engine="streaming")
    )
    return table_df.to_dicts(), total_records, unique_categories


def write_subset_document(platform: str, api_version: str, output_path: Path) -> SummaryResult:
    input_path = INPUTS[platform]
    rows, total_records, unique_categories = compute_subset_table(input_path, api_version)
    generated_on = date.today().isoformat()

    summary_lines = [
        f"# Categories: {platform.upper()} {api_version}",
        "",
        f"Summary: {total_records:,} total records | {unique_categories:,} unique categories | Generated on {generated_on}",
        "",
        format_markdown_table(rows, SUMMARY_COLUMNS),
        "",
    ]
    output_path.write_text("\n".join(summary_lines), encoding="utf-8")

    return SummaryResult(
        platform=platform,
        api_version=api_version,
        output_path=output_path,
        total_records=total_records,
        unique_categories=unique_categories,
    )


def build_mapping_reference_table() -> tuple[str, int]:
    mapping_rows = (
        load_mapping_reference()
        .select(MAPPING_COLUMNS)
        .collect(engine="streaming")
        .to_dicts()
    )
    intro = [
        "# Mapping Reference Table",
        "",
        "This table documents the taxonomy mapping used for harmonizing v1 and v2 platform labels.",
        "It constitutes the formal mapping protocol for the taxonomy alignment described in thesis Section 3.2.",
        "",
        format_markdown_table(mapping_rows, MAPPING_COLUMNS),
        "",
    ]
    return "\n".join(intro), len(mapping_rows)


def write_mapping_reference_document(output_path: Path) -> int:
    content, row_count = build_mapping_reference_table()
    output_path.write_text(content, encoding="utf-8")
    return row_count


def main() -> None:
    validate_inputs()
    ensure_output_dir()

    results: list[SummaryResult] = []
    for platform in ("tiktok", "x"):
        for api_version in VERSION_VALUES:
            output_path = DOCS_DIR / f"categories_{platform}_{api_version}.md"
            results.append(write_subset_document(platform, api_version, output_path))

    mapping_output = DOCS_DIR / "mapping_reference_table.md"
    mapping_rows = write_mapping_reference_document(mapping_output)

    print("Generated documentation files:")
    for result in results:
        print(
            f"- {result.output_path}: {result.total_records:,} rows "
            f"({result.unique_categories:,} unique categories)"
        )
    print(f"- {mapping_output}: {mapping_rows} rows")


if __name__ == "__main__":
    main()