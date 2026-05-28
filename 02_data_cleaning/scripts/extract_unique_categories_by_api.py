"""
Extract unique `category` values split by `api_version` from TikTok and X parquet outputs.
Uses lazy Polars scans and only collects the small unique lists.
"""
import polars as pl
from pathlib import Path

FILES = [r"C:\BA_Data\tiktok_de_2025.parquet", r"C:\BA_Data\x_de_2025.parquet"]


def extract_unique_categories(files):
    # Build a combined lazyframe from available files
    lfs = []
    for p in files:
        pth = Path(p)
        print(f"Checking: {pth}")
        if not pth.exists():
            print(f"  WARNING: file not found: {pth}")
            continue
        lfs.append(pl.scan_parquet(str(pth)).select(["api_version", "category"]))

    if not lfs:
        raise SystemExit("No input files found")

    # Concatenate lazyframes and aggregate unique categories grouped by api_version
    combined = pl.concat(lfs)
    agg = combined.group_by("api_version").agg(pl.col("category").unique()).collect(streaming=True)

    # Convert results to python sets
    results = {"v1": set(), "v2": set()}
    for row in agg.iter_rows(named=True):
        ver = row["api_version"]
        cats = row["category"]
        # ensure iterable
        if cats is None:
            continue
        # 'cats' is a Series or list-like depending on polars version
        if hasattr(cats, "to_list"):
            items = cats.to_list()
        else:
            items = list(cats)
        results[ver] = set(items)

    return results


if __name__ == "__main__":
    res = extract_unique_categories(FILES)
    total_v1 = res.get("v1", set())
    total_v2 = res.get("v2", set())

    both = sorted(total_v1 & total_v2)
    v1_only = sorted(total_v1 - total_v2)
    v2_only = sorted(total_v2 - total_v1)

    print("\n=== Category lists by api_version (combined TikTok + X) ===")
    print(f"\nCategories in BOTH (count={len(both)}):")
    for c in both:
        print(f" - {c}")

    print(f"\nCategories ONLY in v1 (count={len(v1_only)}):")
    for c in v1_only:
        print(f" - {c}")

    print(f"\nCategories ONLY in v2 (count={len(v2_only)}):")
    for c in v2_only:
        print(f" - {c}")
