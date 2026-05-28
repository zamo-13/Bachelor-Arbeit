# Harmonization: run instructions

Purpose: reproduce the category harmonization and documentation generation steps.

Quick run (PowerShell):

1. Activate your virtual environment (if any):

```powershell
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned)
& ".venv\Scripts\Activate.ps1"
```

2. (Optional) override the default data root and mapping path using environment variables.
- Default data root: C:\\BA_Data (used when `BA_DATA_ROOT` is not set).
- Default mapping CSV: the repository file 03_harmonization/taxonomy_mapping_v1_v2.csv.

Example (set and run):

```powershell
$env:BA_DATA_ROOT = 'C:\\BA_Data'
$env:MAPPING_PATH = 'C:\\Path\\To\\Repo\\03_harmonization\\taxonomy_mapping_v1_v2.csv'
python 03_harmonization/scripts/harmonize_categories_polars.py
```

3. Generate mapping documentation (after harmonization completes):

```powershell
python 03_harmonization/scripts/generate_mapping_documentation.py
```

Notes:
- The harmonization script respects `BA_DATA_ROOT` and `MAPPING_PATH` environment variables.
- The script performs basic validation: unmapped categories and row-count preservation.
- See 03_harmonization/harmonization_log.md for provenance and interpretation notes.
