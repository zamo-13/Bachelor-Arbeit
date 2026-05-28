# Data Profile and Quantitative Findings Log

## 1. Raw Data (Pre-Filtering)
<!-- Total row counts before any filtering is applied -->
- Total TikTok rows: 1,002,729,268
- Total X rows : 670,093
- Combined total: 1,003,399,361
## 2. After DE Filtering
<!-- Row counts after territorial_scope DE filter -->
- Date: 2026-04-29
- Description: Streaming Polars DE filtering and split run (filter_split_save_de_polars.py)

- TikTok rows: 999,079,277
- X rows: 183,324
- Number of original files deleted: 1488
## 3. Platform Split
<!-- Row counts per platform after splitting TikTok and X -->

## 4. API Version Split
<!-- Row counts per platform per api_version (v1 and v2) -->

## 5. Harmonization Outputs
<!-- Quantitative findings from taxonomy harmonization and category documentation -->
- Date: 2026-04-30
- Description: Category documentation generation (generate_mapping_documentation.py)
- TikTok v1 rows: 831,613,348
- TikTok v2 rows: 167,465,929
- TikTok total harmonized: 999,079,277 (verified match)
- X v1 rows: 132,194
- X v2 rows: 51,130
- X total harmonized: 183,324 (verified match)

## 6. Analysis Outputs
<!-- Key numeric results from RQ1 and RQ2 analyses -->

## 7. MAU Reference Values
<!-- Official MAU figures per platform used for normalization -->

<!--
IMPORTANT: This file is append-only. Do not delete or overwrite existing entries.
When adding new quantitative findings, append a dated entry with a one-line description and the numeric result.
Example entry format:

- 2026-04-27: Raw rows pre-filter: 123,456 (source: raw_tiktok_2025_de.parquet)

-->

- Date: 2026-04-29
- Description: Streaming Polars DE filtering and split run (filter_split_save_de_polars.py)
- Result:
  - Total TikTok rows before filtering: 1002729268
  - Total X rows before filtering: 670093
  - Combined total before filtering: 1003399361
  - TikTok rows after DE filter: 999079277
  - X rows after DE filter: 183324
  - Output file written: C:\BA_Data\tiktok_de_2025.parquet
  - Output file written: C:\BA_Data\x_de_2025.parquet
  - Number of original files deleted: 1488
