# Mapping Reference Table

This table documents the taxonomy mapping used for harmonizing v1 and v2 platform labels.
It constitutes the formal mapping protocol for the taxonomy alignment described in thesis Section 3.2.

| original_category | api_version | super_cluster | mapping_type | dsa_legal_basis | notes |
| --- | --- | --- | --- | --- | --- |
| STATEMENT_CATEGORY_ANIMAL_WELFARE | both | ANIMAL_WELFARE | direct | DSA Art. 3(h) | Identical in v1 and v2 |
| STATEMENT_CATEGORY_CYBER_VIOLENCE | both | CYBER_VIOLENCE | present_in_both | DSA Changelog July 2025 | Officially new in v2 but appears in v1 records - document as anomaly |
| STATEMENT_CATEGORY_DATA_PROTECTION_AND_PRIVACY_VIOLATIONS | both | PRIVACY_AND_DATA | direct | DSA Art. 3(h) | Identical in v1 and v2 |
| STATEMENT_CATEGORY_ILLEGAL_OR_HARMFUL_SPEECH | both | HARMFUL_SPEECH | direct | DSA Art. 3(h) | Identical in v1 and v2 |
| STATEMENT_CATEGORY_INTELLECTUAL_PROPERTY_INFRINGEMENTS | both | INTELLECTUAL_PROPERTY | direct | DSA Art. 3(h) | Identical in v1 and v2 |
| STATEMENT_CATEGORY_NEGATIVE_EFFECTS_ON_CIVIC_DISCOURSE_OR_ELECTIONS | both | CIVIC_AND_ELECTIONS | direct | DSA Art. 3(h) | Identical in v1 and v2 |
| STATEMENT_CATEGORY_OTHER_VIOLATION_TC | both | OTHER | renamed_from_v1 | DSA Changelog July 2025 | Maps from v1 SCOPE_OF_PLATFORM_SERVICE |
| STATEMENT_CATEGORY_PORNOGRAPHY_OR_SEXUALIZED_CONTENT | both | SEXUAL_CONTENT | direct | DSA Art. 3(h) | Appears in both despite being removed in official v2 schema |
| STATEMENT_CATEGORY_PROTECTION_OF_MINORS | both | PROTECTION_OF_MINORS | direct | DSA Art. 3(h) | Identical in v1 and v2 |
| STATEMENT_CATEGORY_RISK_FOR_PUBLIC_SECURITY | both | VIOLENCE | direct | DSA Art. 3(h) | Grouped with VIOLENCE per semantic proximity |
| STATEMENT_CATEGORY_SCAMS_AND_FRAUD | both | SCAMS_AND_FRAUD | direct | DSA Art. 3(h) | Identical in v1 and v2 |
| STATEMENT_CATEGORY_SCOPE_OF_PLATFORM_SERVICE | both | OTHER | renamed_to_v2 | DSA Changelog July 2025 | Renamed to OTHER_VIOLATION_TC in v2 |
| STATEMENT_CATEGORY_SELF_HARM | both | SELF_HARM | direct | DSA Art. 3(h) | Identical in v1 and v2 |
| STATEMENT_CATEGORY_UNSAFE_AND_PROHIBITED_PRODUCTS | both | UNSAFE_PRODUCTS | renamed_from_v1 | DSA Changelog July 2025 | Maps from v1 UNSAFE_AND_ILLEGAL_PRODUCTS |
| STATEMENT_CATEGORY_VIOLENCE | both | VIOLENCE | direct | DSA Art. 3(h) | Identical in v1 and v2 |
| STATEMENT_CATEGORY_NON_CONSENSUAL_BEHAVIOUR | v1_only | SEXUAL_CONTENT | removed_in_v2 | DSA Changelog July 2025 | No v2 equivalent - grouped with SEXUAL_CONTENT by semantic proximity |
| STATEMENT_CATEGORY_UNSAFE_AND_ILLEGAL_PRODUCTS | v1_only | UNSAFE_PRODUCTS | renamed_in_v2 | DSA Changelog July 2025 | Renamed to UNSAFE_AND_PROHIBITED_PRODUCTS in v2 |
