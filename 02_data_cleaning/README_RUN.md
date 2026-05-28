# Data Cleaning — Quick Runbook

This runbook shows the minimal commands to reproduce the data-cleaning outputs used in the thesis. It assumes a Python virtual environment with `polars` and `pandas` installed (see `requirements.txt`).

1) Activate your virtual environment (example PowerShell):

```powershell
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned)
& ".venv\Scripts\Activate.ps1"
pip install -r requirements.txt
```

2) (Optional) point the scripts to your external data root. By default the scripts look for `C:\BA_Data`.

3) Dry-run column selection (preview files):

```powershell
python 02_data_cleaning/scripts/batch_select_columns.py --input-root "C:/path/to/DSA-Data" --output-root 02_data_cleaning/data_intermediate --platform tiktok___full --dry-run
```

4) Run full column selection to create reduced 9-column parquet outputs:

```powershell
python 02_data_cleaning/scripts/batch_select_columns.py --input-root "C:/path/to/DSA-Data" --output-root 02_data_cleaning/data_intermediate --platform tiktok___full
python 02_data_cleaning/scripts/batch_select_columns.py --input-root "C:/path/to/DSA-Data" --output-root 02_data_cleaning/data_intermediate --platform x___full
```

5) Produce the DE-filtered, per-platform yearly parquet files (uses `BA_DATA_ROOT` env var if set):

```powershell
python 02_data_cleaning/scripts/filter_split_save_de_polars.py --data-dir "C:/BA_Data"
```

Notes:
- The scripts append validation logs under `02_data_cleaning/logs/` and require you to update `02_data_cleaning/docs/methods_worklog.md` for each substantive run.
- `filter_split_save_de_polars.py` writes `C:\BA_Data\tiktok_de_2025.parquet` and `C:\BA_Data\x_de_2025.parquet` by default (or under the provided `--data-dir`).
