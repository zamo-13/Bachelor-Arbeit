# Data Cleaning

This folder contains the full data cleaning workflow for the thesis project.

## Purpose

The goal of this phase is to transform extracted raw data into a documented, analysis-ready dataset while preserving reproducibility and methodological transparency.

## Folder Structure

- `data_input/`: immutable inputs for this phase
- `data_intermediate/`: temporary outputs from cleaning/profiling steps
- `data_clean/`: final cleaned datasets used in later phases
- `notebooks/`: exploratory and documented cleaning notebooks
- `scripts/`: reusable Python scripts/functions for cleaning operations
- `docs/`: methodological notes and explicit cleaning decisions
- `logs/`: process logs and run summaries
- `metadata/`: data dictionary and schema-level metadata

## Workflow

1. Copy or link source data into `data_input/`.
2. Run profiling notebook(s) in `notebooks/`.
3. Record every non-trivial decision in `docs/cleaning_decisions.md`.
4. Update variable definitions in `metadata/data_dictionary.md`.
5. Export cleaned data to `data_clean/`.

## Reproducibility Standard

- Every transformation must be either code-based (not manual) or explicitly justified in `docs/cleaning_decisions.md`.
- Notebook runs should be date-traceable and executable end-to-end.
- Intermediate and final outputs should be clearly named and versioned.
