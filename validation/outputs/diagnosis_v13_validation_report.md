# DHMS Product Diagnosis v1.3 Validation

Status: PASS

## Commands Run

* parse_check: PASS
* product_mock_single: PASS
* suite_mock: PASS

## Report Paths Generated

* product_mock_single: reports/diagnosis_mock_single/dhms_product_report.json
* suite_mock: reports/diagnosis_llm_core_mock/suite_report.json
* suite_deepseek_flash: reports/diagnosis_llm_core_deepseek_flash/suite_report.json

## Schema Checks

* diagnosis_fields_present: True
* per_case_schema_fields_present: True
* v2_metrics_overridden: False

## Key Leakage Scan

* passed: True
* checked_files: 179

## Remaining Caveats

* This validator is local-safe; DeepSeek suite evidence is included only if it was run separately.
* n=1 mock suite validates schema and deterministic diagnosis wiring, not stochastic stability.
* Expected property checker is heuristic and should be reviewed by a human.