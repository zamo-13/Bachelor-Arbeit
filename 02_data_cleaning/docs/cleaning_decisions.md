# Cleaning Decisions

This log documents the key methodological decisions made during data cleaning.

## How to use this log

For each non-trivial cleaning action, record:
- what was observed,
- what decision was made,
- why this decision was made,
- what potential impact it has on analysis.

## Decision Template

### Decision ID: CD-YYYYMMDD-XX

- Date:
- Dataset / File:
- Variable(s) affected:
- Problem observed:
- Decision taken:
- Rationale (methodological reason):
- Expected impact on analysis:
- Reversible: Yes/No
- Code reference (notebook/script + section):
- Validation check performed:

## Decision Log

### Decision ID: CD-20260426-01

- Date: 2026-04-26
- Dataset / File: C:\Users\MoZa\OneDrive - Universität Paderborn\0_UPB\BA\DSA-Data\tiktok___full\daily_dumps_chunked\sor-tiktok-2025-01-01-full\part-0000.parquet
- Variable(s) affected: decision_monetary, end_date_account_restriction, account_type
- Problem observed:
	- Initial profiling on one parquet part produced 1,000,000 rows and 37 columns.
	- Three variables showed 100.0% missingness: decision_monetary, end_date_account_restriction, account_type.
	- Exact duplicate rows: 0.
- Decision taken: Keep these variables for now; flag them for domain review in the next cleaning step.
- Rationale (methodological reason): Avoid premature variable deletion before checking whether complete missingness is structurally expected by platform, period, or reporting schema.
- Expected impact on analysis: Protects internal validity and reduces the risk of unjustified feature removal that could bias later interpretation.
- Reversible: Yes
- Code reference (notebook/script + section): 02_data_cleaning/scripts/filter_split_save_de_polars.py (sections: Select input file, Load data, missing_summary, duplicate check)
- Validation check performed:
	- Input file existence check passed.
	- Data loaded successfully.
	- Missingness summary and duplicate checks executed.

### Decision ID: CD-20260426-02

- Date: 2026-04-26
- Dataset / File: C:\Users\MoZa\OneDrive - Universität Paderborn\0_UPB\BA\DSA-Data\tiktok___full\daily_dumps_chunked\sor-tiktok-2025-01-01-full\part-0000.parquet
- Variable(s) affected: uuid, category, content_type, automated_detection, automated_decision, territorial_scope, application_date, platform_name, decision_visibility
- Problem observed:
	- The raw DSA files contain many additional columns not required for the current research questions.
	- Retaining all columns increases RAM usage and slows analysis scripts.
- Decision taken: Restrict the working analytical dataset to the 9 thesis-relevant columns listed above.
- Rationale (methodological reason):
	- The retained columns directly support core analytical dimensions: unique records, harm category, content modality, automation indicators, temporal filtering, platform comparison, territorial scope, and visibility outcome.
	- Removing non-essential columns at this stage improves computational efficiency while preserving variables needed for validity of planned analyses.
- Expected impact on analysis:
	- Positive: reduced memory footprint and faster iteration.
	- Risk: potential loss of contextual fields not currently modeled; this is accepted and documented for scope control.
- Reversible: Yes
- Code reference (notebook/script + section): 02_data_cleaning/scripts/batch_select_columns.py (sections: KEEP_COLUMNS, column validation, export)
- Validation check performed:
	- Expected column existence check before selection.
	- uuid uniqueness check and duplicate-row check after selection.
	- Missingness summary exported for retained columns.

### Decision ID: CD-20260429-01

- Date: 2026-04-29
- Dataset / File: C:\BA_Data\tiktok_de_2025.parquet; C:\BA_Data\x_de_2025.parquet
- Variable(s) affected: application_date
- Problem observed:
	- application_date column contains timestamps with time component stored as datetime[ms].
	- Inspection of 100% of rows (TikTok: 999,079,277; X: 183,324) shows all times are 00:00:00 (midnight).
	- Zero rows have non-midnight times across both platforms.
- Decision taken: Truncate application_date to date-only (remove time component), converting from datetime[ms] to date type.
- Rationale (methodological reason):
	- The time component carries no information (100% are midnight values).
	- Analysis scope is at the daily grain; sub-daily granularity is not needed.
	- Removing zero-variance fields reduces storage and simplifies downstream code.
	- This is consistent with data quality best practices (remove uninformative noise).
- Expected impact on analysis:
	- Positive: reduced file size, simpler date comparisons, clearer intent of "decision date" granularity.
	- Risk: none—no information loss since all times were identical.
- Reversible: Yes (original raw parquets under C:\BA_Data\tiktok___full\ and x___full\ are unchanged)
- Code reference (notebook/script + section): 
	- Inspection: 02_data_cleaning/scripts/filter_split_save_de_polars.py
	- Implementation: 02_data_cleaning/scripts/harmonize_sor_polars.py (to be implemented in next step)
- Validation check performed:
	- Scanned 100% of rows in both tiktok_de_2025.parquet and x_de_2025.parquet.
	- Confirmed: TikTok 999,079,277/999,079,277 rows (100%) have time = 00:00:00.
	- Confirmed: X 183,324/183,324 rows (100%) have time = 00:00:00.
	- Pre- and post-truncation counts to be recorded in data_profile.md after harmonization run.

### Decision ID: CD-20260429-02

- Date: 2026-04-29
- Dataset / File: C:\BA_Data\tiktok_de_2025.parquet; C:\BA_Data\x_de_2025.parquet
- Variable(s) affected: category, api_version
- Problem observed:
	- STATEMENT_CATEGORY_CYBER_VIOLENCE appears in v1 records despite being an official v2 category.
	- STATEMENT_CATEGORY_PORNOGRAPHY_OR_SEXUALIZED_CONTENT appears in v2 records despite being removed in the official v2 schema.
- Decision taken: Treat both as data anomalies with no action taken beyond documented many-to-one mapping to Super-Clusters; preserve original labels in category_raw and harmonize via category_harmonized.
- Rationale (methodological reason):
	- The original labels are retained for traceability.
	- The anomalies are documented rather than corrected because the user-provided mapping table defines the harmonized interpretation.
	- Avoids silently rewriting source evidence.
- Expected impact on analysis:
	- Positive: preserves auditability and makes the exceptional cases explicit.
	- Risk: analysts must use category_harmonized for interpretation and category_raw for provenance.
- Reversible: Yes
- Code reference (notebook/script + section): 03_harmonization/scripts/harmonize_categories_polars.py (planned)
- Validation check performed:
	- Mapping table saved to 03_harmonization/taxonomy_mapping_v1_v2.csv.
	- Anomaly cases will be checked during harmonization validation for unmapped values.
