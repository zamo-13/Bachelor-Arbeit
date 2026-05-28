# Copilot Instructions For This Repository

## Documentation First For Data Cleaning Work

When a task touches data cleaning in 02_data_cleaning, always update project documentation before ending the response.

Required updates:
- Append one new row in 02_data_cleaning/docs/methods_worklog.md under Methods Timeline for each completed substantive step.
- If the step includes a non-trivial methodological choice, add or update an entry in 02_data_cleaning/docs/cleaning_decisions.md and reference its Decision ID in the worklog row.
- Include concise evidence in the worklog row (counts, output path, validation check).

## Scope Rules

Apply this behavior to tasks involving:
- notebooks in 02_data_cleaning/notebooks
- scripts in 02_data_cleaning/scripts
- outputs in 02_data_cleaning/data_intermediate
- data handling decisions for tiktok___full or x___full

## End-Of-Task Checklist

Before finalizing a response for in-scope tasks:
1. Verify methods_worklog.md was updated.
2. Verify cleaning_decisions.md is updated if methodology changed.
3. Mention the added Step ID(s) in the response.
