# Data Cleaning Methods Worklog

This document is the central operational log for the data cleaning workflow.
It records what was done, what is currently being done, and what is planned next.

## Why this file exists

Use this as the main chronological source for your thesis Methods section.
It complements (does not replace) the decision-focused log in [cleaning_decisions.md](cleaning_decisions.md).

- methods_worklog.md: timeline of actions, scripts, scope, outputs, and checks.
- cleaning_decisions.md: methodological justifications for non-trivial decisions.

## Update rules

For each relevant step, record:
- date,
- status (done/in-progress/planned),
- objective,
- exact script/notebook used,
- input and output locations,
- validation evidence,
- link to a decision ID when applicable.

Keep entries short and factual.

## Copilot Update Protocol

Use this protocol in any chat session for this repository.

- At the start of a new request, state whether the action should be logged in this worklog.
- After each completed data-cleaning action, append one row to the Methods Timeline table.
- If a step changes methodology or assumptions, also add or reference an entry in cleaning_decisions.md.
- Before ending the session, confirm which Step ID(s) were added.

Quick reminder phrase you can paste in any chat:

"Please execute the task and then update 02_data_cleaning/docs/methods_worklog.md with a new Step ID row before you finish."

## Workflow Scope

- Project area: 02_data_cleaning
- Data source root: C:/Users/MoZa/OneDrive - Universitat Paderborn/0_UPB/BA/DSA-Data
- Platforms in scope: tiktok___full, x___full
- Main processing script: 02_data_cleaning/scripts/batch_select_columns.py

## Methods Timeline

| Step ID | Date | Status | Objective | Artifact Used | Input Scope | Output / Result | Validation / Evidence | Linked Decision |
|---|---|---|---|---|---|---|---|---|
| MG-20260427-01 | 2026-04-27 | done | Create persistent data_profile log for quantitative findings | 02_data_cleaning/logs/data_profile.md | n/a | data_profile.md created | File created and added to repo; validation script present | |
| M-20260426-01 | 2026-04-26 | done | Initial profiling on TikTok sample data | 02_data_cleaning/scripts/filter_split_save_de_polars.py | One parquet part from tiktok___full | Dataset profile produced (rows, columns, missingness, duplicates) | Reported: 1,000,000 rows, 37 columns, 0 duplicate rows | CD-20260426-01 |
| M-20260426-02 | 2026-04-26 | done | Define thesis-relevant analysis columns | 02_data_cleaning/scripts/batch_select_columns.py | TikTok schema review | KEEP_COLUMNS set to 9 variables | Column existence checks and post-selection checks run | CD-20260426-02 |
| M-20260426-03 | 2026-04-26 | done | Dry-run discovery before bulk execution | 02_data_cleaning/scripts/batch_select_columns.py | tiktok___full | Dry-run summary CSV generated | Discovery count logged in summary file | CD-20260426-02 |
| M-20260426-04 | 2026-04-26 | done | In-place replacement for TikTok January | 02_data_cleaning/scripts/batch_select_columns.py | tiktok___full, day prefix sor-tiktok-2025-01 | Original parquet files replaced by reduced 9-column parquet files | Processing summary CSV and sample-column verification | CD-20260426-02 |
| M-20260426-05 | 2026-04-26 | done | In-place replacement for remaining TikTok months | 02_data_cleaning/scripts/batch_select_columns.py | tiktok___full, prefixes 2025-02 to 2025-12 | Remaining months processed in batch loop | Month-by-month discovered/processed counts logged | CD-20260426-02 |
| M-20260426-06 | 2026-04-26 | done | In-place replacement for X January | 02_data_cleaning/scripts/batch_select_columns.py | x___full, day prefix sor-x-2025-01 | January parquet files reduced to 9 columns in original path | Processing summary CSV generated | CD-20260426-02 |
| M-20260426-07 | 2026-04-26 | done | In-place replacement for X remaining months | 02_data_cleaning/scripts/batch_select_columns.py | x___full, prefixes 2025-02 to 2025-12 | Months 02-12 processed | Month-level processed counts logged (including sparse months) | CD-20260426-02 |
| M-20260427-01 | 2026-04-27 | done | Coverage audit for X 2025 folders/files | One-off Python scan in terminal | x___full/daily_dumps_chunked | Coverage table produced: day folders, non-empty days, parquet files per month | Verified totals: 365 day folders, 291 non-empty days, 291 parquet files | - |
| M-20260427-02 | 2026-04-27 | done | File-type confirmation (CSV vs parquet processing) | 02_data_cleaning/scripts/batch_select_columns.py review + folder scan | x___full and tiktok___full | Confirmed processing script targets part-*.parquet only; CSV in raw daily folders not processed | Verified raw X CSV count = 0 for 2025 daily folders | - |
| M-20260427-03 | 2026-04-27 | planned | Begin filtering on DE territorial scope and document inclusion criteria | 02_data_cleaning/scripts/filter_split_save_de_polars.py | Reduced 9-column parquet data | Filtered analytical subset and reproducible filtering log | To be executed and recorded | TBD |
| M-20260602-01 | 2026-06-02 | done | Create date-range filter script for 2025 application_date | 02_data_cleaning/scripts/apply_date_filter.py | C:\BA_Data\tiktok_de_2025.parquet; C:\BA_Data\x_de_2025.parquet | Script saved; filters 2025-01-01 to 2025-12-31 and overwrites in place after backup-folder check | Backup folder existence check and per-platform drop-count print implemented | CD-20260602-01 |
| M-20260602-04 | 2026-06-02 | done | Regenerate TikTok harmonized file from filtered inputs | 03_harmonization/scripts/harmonize_categories_polars.py | C:\BA_Data\tiktok_de_2025.parquet (997,688,267 rows) | tiktok_de_2025_harmonized.parquet (18.3 GB) | Output timestamp 13:26:28; TikTok rows preserved; category and date harmonization applied | - |
| M-20260602-05 | 2026-06-02 | done | Regenerate X harmonized file from filtered inputs | 03_harmonization/scripts/harmonize_categories_polars.py (X-only mode) | C:\BA_Data\x_de_2025.parquet (183,321 rows) | x_de_2025_harmonized.parquet (3.66 MB); row count match verified | Input 183,321 rows → output 183,321 rows; validation passed (no unmapped categories) | - |

## Output Artifacts To Cite In Thesis

- Processing summaries:
  - 02_data_cleaning/data_intermediate/tiktok___full_selected_9cols/tiktok___full_selected_9cols_processing_summary.csv
  - 02_data_cleaning/data_intermediate/x___full_selected_9cols/x___full_selected_9cols_processing_summary.csv
- Dry-run summaries (if generated):
  - 02_data_cleaning/data_intermediate/tiktok___full_selected_9cols/tiktok___full_selected_9cols_dry_run_summary.csv
  - 02_data_cleaning/data_intermediate/x___full_selected_9cols/x___full_selected_9cols_dry_run_summary.csv
- Method decisions:
  - 02_data_cleaning/docs/cleaning_decisions.md

## Notes For Writing The Methods Section

When drafting the thesis text, reference this file for chronology and reproducibility, and reference cleaning_decisions.md for methodological justification.

Recommended split:
- Methods workflow narrative: from methods_worklog.md
- Rationale and trade-offs: from cleaning_decisions.md
- Quantitative execution evidence: from processing_summary.csv files
