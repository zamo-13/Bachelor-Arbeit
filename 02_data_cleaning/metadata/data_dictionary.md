# Data Dictionary

Document all variables used in cleaned outputs.

## Dataset Metadata

- Dataset name:
- Source dataset(s):
- Cleaning notebook/script reference:
- Last updated:
- Number of rows:
- Number of columns:

## Variable Definitions

| Variable Name | Description | Data Type | Unit / Format | Allowed Values / Domain | Missing Value Rule | Derived? (Y/N) | Derivation Logic |
|---|---|---|---|---|---|---|---|
| example_variable | Short definition of what this variable represents | string / int / float / datetime / category | e.g., ISO date format YYYY-MM-DD | e.g., {A,B,C} or range [0, 100] | e.g., NA means not reported | N | - |
| uuid | Unique identifier per moderation decision | string | UUID-like text identifier | Unique per row | NA indicates malformed or missing identifier | N | - |
| category | Reported harm category for the decision | category/string | Controlled label | Platform-reported categories (for example, ILLEGAL_OR_HARMFUL_SPEECH) | NA indicates no category provided | N | - |
| content_type | Content modality associated with the decision | category/string | Text label | video, text, image, other platform values | NA indicates unknown modality | N | - |
| automated_detection | Whether content was detected automatically | boolean/string | True/False or platform encoding | Binary indicator (platform encoding) | NA indicates not specified | N | - |
| automated_decision | Whether final decision was fully automated | boolean/string | True/False or platform encoding | Binary indicator (platform encoding) | NA indicates not specified | N | - |
| territorial_scope | Jurisdiction or countries affected by the decision | string | Country code list or text | Platform-reported territorial values | NA indicates no scope reported | N | - |
| application_date | Date the moderation decision was applied | datetime/string | YYYY-MM-DD (target) | Calendar dates in study period | NA indicates unavailable timestamp | N | - |
| platform_name | Platform source of the decision | category/string | Text label | tiktok, x | NA should not occur in final analytical set | N | - |
| decision_visibility | Moderation outcome impacting visibility | category/string | Text label | removal, restriction, or platform-specific values | NA indicates outcome not reported | N | - |

## Notes

- Use one row per variable in the cleaned dataset.
- If a variable is transformed, describe the transformation in "Derivation Logic".
- Keep names and definitions aligned with analysis notebooks.
