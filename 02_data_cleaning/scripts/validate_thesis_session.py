"""Validate a thesis session and append a concise governance log entry.

Expected inputs:
- Repository-local thesis docs and logs under 02_data_cleaning/docs and 02_data_cleaning/logs.

Outputs:
- A short validation report in the console.
- An appended session entry in 02_data_cleaning/logs/thesis_governance_session_log.md.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LOG_FILE = ROOT / "02_data_cleaning" / "logs" / "thesis_governance_session_log.md"
WORKLOG = ROOT / "02_data_cleaning" / "docs" / "methods_worklog.md"
DECISIONS = ROOT / "02_data_cleaning" / "docs" / "cleaning_decisions.md"


def main() -> None:
    checks = [
        (WORKLOG.exists(), "methods_worklog.md exists"),
        (DECISIONS.exists(), "cleaning_decisions.md exists"),
        (LOG_FILE.exists(), "session log exists"),
    ]

    warnings = []
    for passed, label in checks:
        if not passed:
            warnings.append(label)

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = [
        "",
        f"- Date: {date.today().isoformat()}",
        "- Session focus: Thesis governance validation",
        "- Validation script: 02_data_cleaning/scripts/validate_thesis_session.py",
        f"- Checklist result: {'passed' if not warnings else 'passed with warnings'}",
        f"- Warnings: {', '.join(warnings) if warnings else 'none'}",
        "- Log status: appended",
    ]

    if not LOG_FILE.exists():
        LOG_FILE.write_text(
            "# Thesis Governance Session Log\n\n"
            "This log records end-of-session validation notes for thesis work in this repository.\n\n"
            "## Entry Template\n\n"
            "- Date:\n"
            "- Session focus:\n"
            "- Validation script:\n"
            "- Checklist result:\n"
            "- Warnings:\n"
            "- Log status:\n\n"
            "## Sessions\n",
            encoding="utf-8",
        )

    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(entry) + "\n")

    print("Thesis session validation complete.")
    for passed, label in checks:
        print(f"- {'OK' if passed else 'WARN'}: {label}")


if __name__ == "__main__":
    main()