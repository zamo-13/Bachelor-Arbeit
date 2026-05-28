# Repository Cleanup Log

## Cleanup Session: 2026-04-29

### Reason for Removal

All files in `01_data_extraction/dsa-tdb` (Group C) were removed because:
- The extraction tool (dsa-tdb) served its purpose of downloading DSA Transparency Database records for the full year 2025
- The tool's source code is not needed in this repository after the extraction phase is complete
- The tool source is available at its original upstream repository for future reference
- A permanent provenance note was created in `01_data_extraction/README.md` to document the tool and output location
- Removing these files reduces repository size and eliminates non-thesis code

### Files Deleted

The entire directory tree `01_data_extraction/dsa-tdb/` was removed, including:

#### Root Level Files and Directories
- `.copyright.tmpl`
- `.dockerignore`
- `.editorconfig`
- `.env.template`
- `.git/` (git repository of dsa-tdb tool)
- `.gitignore`
- `.gitlab-ci.yml`
- `.pre-commit-config.yaml`
- `app/` (FastAPI application and Celery task definitions)
- `bandit.yml` (security linter config)
- `CHANGELOG.md`
- `config_aggregation_complete.yaml`
- `config_aggregation_simple.yaml`
- `config_filtering.yaml`
- `CONTRIBUTING.md`
- `data/` (sample data directory)
- `docker-compose.yml`
- `Dockerfile`
- `docs/` (Sphinx documentation build files)
- `Documentation- extracting data.md`
- `dsa_tdb/` (main Python package)
- `LICENSE`
- `notebooks/` (example Jupyter notebooks)
- `NOTICE`
- `poetry.lock`
- `pyproject.toml`
- `README.md`
- `scripts/` (shell scripts for daily routine and downloads)
- `tests/` (unit tests for the tool)

#### Key Subdirectories Removed
- `app/system_resources/` — FastAPI server, Celery worker, Superset config
- `app/system_resources/redis_config/` — Redis configuration
- `app/system_resources/superset_exports/` — Superset metadata exports
- `docs/` — Sphinx documentation, RST files, static assets
- `dsa_tdb/` — Python package modules (cli.py, core.py, etl.py, fetch.py, types.py, utils.py, advanced_utils.py)
- `notebooks/` — Example notebooks (Example.ipynb)
- `scripts/` — Shell automation scripts (daily_routine.sh, download_platform.sh, prepare_advanced_data.sh)
- `tests/` — Test suite and test data

### Verification

- ✓ `01_data_extraction/README.md` preserved (provenance note)
- ✓ No files from Group B (thesis work) were deleted
- ✓ No `.gitkeep` files were affected (none present in dsa-tdb)
- ✓ Session validator executed successfully after cleanup

### Impact

- Repository size reduced by removal of extraction tool source code
- Thesis repository now contains only thesis-related work:
  - Data extraction metadata (`01_data_extraction/README.md`)
  - Data cleaning pipeline (`02_data_cleaning/` scripts, notebooks, logs)
  - Governance infrastructure (validators, worklog, decision logs)
- All original data outputs preserved externally at `C:\BA_Data\`

### Related Documentation

- Provenance note: [01_data_extraction/README.md](../../01_data_extraction/README.md)
- Data profile log: [02_data_cleaning/logs/data_profile.md](data_profile.md)
- Session governance log: [02_data_cleaning/logs/thesis_governance_session_log.md](thesis_governance_session_log.md)
