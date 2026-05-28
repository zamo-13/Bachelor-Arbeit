# Harmonization Log

## Purpose
Documents all steps, decisions, and outputs of the taxonomy 
harmonization phase. This folder bridges the API v1 and v2 
schema difference for longitudinal analysis.

## Phase: Category Harmonization
- Date: 2026-04-29
- Script: harmonize_categories_polars.py
- Mapping table: taxonomy_mapping_v1_v2.csv (17 rows)
- Input files: tiktok_de_2025.parquet, x_de_2025.parquet
- Output files: tiktok_de_2025_harmonized.parquet, 
  x_de_2025_harmonized.parquet

### Reproducibility / Rerun
- For a reproducible rerun, see `03_harmonization/README.md` which documents the exact commands.
- The harmonization script now accepts environment overrides:
  - `BA_DATA_ROOT` (default `C:\BA_Data`) — root folder containing input/output parquet files
  - `MAPPING_PATH` — path to the taxonomy CSV (default `03_harmonization/taxonomy_mapping_v1_v2.csv` in the repo)

### Row Count Validation
- TikTok input: 999,079,277
- TikTok output: 999,079,277
- X input: 183,324
- X output: 183,324
- Row counts match: yes

### Mapping Decisions
- Mapping logic: Many-to-One, v2 labels mapped to neutral 
  Super-Cluster names
- Anomaly 1: CYBER_VIOLENCE appears in v1 records despite 
  being an official v2 category. No action taken, preserved 
  in category_raw.
- Anomaly 2: PORNOGRAPHY_OR_SEXUALIZED_CONTENT appears in 
  v2 records despite being removed in official v2 schema. 
  No action taken, preserved in category_raw.

### Validation Result
- Zero unmapped categories in both output files
- Validation method: null count scan on category_harmonized 
  column of output files

### Columns Added
- category_raw: original category value preserved
- category_harmonized: Super-Cluster assignment from mapping
- application_date_raw: original date truncated to Date type
- application_date_harmonized: UTC-normalized Date

### Columns Removed
- category (replaced by category_raw and category_harmonized)
- application_date (replaced by date-only versions)

## Key Findings from Documentation Run
- Date: 2026-04-30
- Script: generate_mapping_documentation.py

### Row Count Verification
- TikTok v1: 831,613,348 rows
- TikTok v2: 167,465,929 rows
- TikTok total: 999,079,277 (matches input)
- X v1: 132,194 rows
- X v2: 51,130 rows
- X total: 183,324 (matches input)
- Status: All counts verified and reconciled

### Notable Patterns
- Pattern 1: TikTok dominant category shifts from HARMFUL_SPEECH at 48.05% in v1 to OTHER_VIOLATION_TC at 67.27% in v2, indicating significant reporting behavior change post-schema transition
- Pattern 2: X CYBER_VIOLENCE increases from 34 records in v1 to 19,143 records in v2, representing the clearest schema transition effect in the dataset
- Pattern 3: TikTok to X record ratio approximately 4,500:1, relevant to automation and scale analysis in RQ1

### Anomaly Confirmation
- CYBER_VIOLENCE in v1 records: 34 for X, 0 for TikTok (negligible)
- PORNOGRAPHY_OR_SEXUALIZED_CONTENT in v2 records: 7 for TikTok, 0 for X (negligible)
- Both anomalies confirmed to be residual and do not significantly impact harmonization quality
