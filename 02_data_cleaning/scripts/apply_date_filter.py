from __future__ import annotations

from pathlib import Path

import polars as pl


TIKTOK_PATH = Path(r"C:\BA_Data\tiktok_de_2025.parquet")
X_PATH = Path(r"C:\BA_Data\x_de_2025.parquet")

RAW_DUMP_FOLDERS = [
    Path(r"C:\BA_Data\tiktok___full"),
    Path(r"C:\BA_Data\x___full"),
]

START_DATE = pl.date(2025, 1, 1)
END_DATE = pl.date(2025, 12, 31)


def _assert_backup_folders_exist() -> None:
    missing = [folder for folder in RAW_DUMP_FOLDERS if not folder.exists()]
    if missing:
        missing_paths = ", ".join(str(folder) for folder in missing)
        raise FileNotFoundError(
            "Backup folders missing. Expected raw dump backups at: " f"{missing_paths}"
        )


def _filter_by_date(lf: pl.LazyFrame) -> pl.LazyFrame:
    return lf.filter(
        pl.col("application_date").is_between(START_DATE, END_DATE, closed="both")
    )


def _report_drop_counts(platform: str, original: int, filtered: int) -> None:
    dropped = original - filtered
    print(f"{platform}: dropped {dropped:,} rows (kept {filtered:,} of {original:,}).")


def _process_platform(path: Path, platform: str) -> None:
    lf = pl.scan_parquet(path)
    filtered = _filter_by_date(lf)

    original_count = lf.select(pl.len()).collect().item()
    filtered_count = filtered.select(pl.len()).collect().item()
    _report_drop_counts(platform, original_count, filtered_count)

    temp_path = path.with_name(f"{path.name}.tmp")
    filtered.sink_parquet(temp_path)
    print(f"Temp write complete for {platform}, moving to final location...")
    
    temp_path.replace(path)
    print(f"{platform} written to {path}")


def main() -> None:
    _assert_backup_folders_exist()

    _process_platform(TIKTOK_PATH, "TikTok")
    _process_platform(X_PATH, "X")


if __name__ == "__main__":
    main()
