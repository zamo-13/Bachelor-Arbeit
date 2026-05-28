"""Inspect TikTok parquet schemas (metadata only) using Polars.

Reads only parquet metadata to avoid loading data into memory.
Prints column names, dtypes, counts, and added/removed column diffs
between the original and harmonized files.
"""
from pathlib import Path
import polars as pl


ROOT = Path(r"C:\BA_Data")
ORIG = ROOT / "tiktok_de_2025.parquet"
HARM = ROOT / "tiktok_de_2025_harmonized.parquet"


def fmt_schema(schema: dict) -> str:
    lines = []
    for name, dtype in schema.items():
        lines.append(f"  - {name}: {dtype}")
    return "\n".join(lines)


def main() -> None:
    for label, path in (("Original", ORIG), ("Harmonized", HARM)):
        print("=" * 60)
        print(f"{label} file: {path}")
        if not path.exists():
            print("  NOT FOUND")
            continue
        schema = pl.read_parquet_schema(str(path))
        print(f"  Columns: {len(schema)}")
        print(fmt_schema(schema))

    # Compare sets if both exist
    if ORIG.exists() and HARM.exists():
        s_orig = set(pl.read_parquet_schema(str(ORIG)).keys())
        s_harm = set(pl.read_parquet_schema(str(HARM)).keys())
        added = sorted(s_harm - s_orig)
        removed = sorted(s_orig - s_harm)
        print("=" * 60)
        print("Column diffs (harmonized vs original):")
        print(f"  Added columns ({len(added)}): {added}")
        print(f"  Removed columns ({len(removed)}): {removed}")


if __name__ == "__main__":
    main()
