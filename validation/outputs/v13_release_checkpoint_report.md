# DHMS Product Diagnosis v1.3 Release Checkpoint Report

Status: PASS

## Commands Run
* `PYTHONPYCACHEPREFIX=/tmp/dhms_engine_pycache python3 -m py_compile $(find . -name "*.py" -not -path "./.venv/*")`
* `python3 cli.py test --input "Does this agent stay consistent?" --models mock --n 1 --report --output reports/release_v13_mock_single`
* `python3 cli.py test-suite --suite cases/llm_core --models mock --n 1 --report --output reports/release_v13_llm_core_mock`
* `python3 validation/run_diagnosis_v13_validation.py`
* `python3 cli.py providers models deepseek`

## Results
* Parse check: PASS
* Diagnosis validation: PASS
* Provider:model syntax: PASS: deepseek aliases default, flash, pro resolved
* .gitignore: PASS: .gitignore exists and excludes secrets, caches, reports, raw API outputs, and local noise
* Key leakage scan: PASS: no likely secret values or private key markers found in scanned project files
* Protected directory hashes: PASS: protected directory hashes match the pre-release checkpoint baseline captured before edits
* V2 metric override status: PASS: v2_metrics_overridden=false in validation outputs; no true override detected
* DeepSeek real API demo: SKIPPED: DEEPSEEK_API_KEY may be present, but no paid real API demo was run automatically

## Mock Report Paths
* `reports/release_v13_mock_single/dhms_product_report.json`
* `reports/release_v13_mock_single/dhms_product_report.md`
* `reports/release_v13_mock_single/dhms_product_report.html`
* `reports/release_v13_llm_core_mock/suite_report.json`
* `reports/release_v13_llm_core_mock/suite_report.md`
* `reports/release_v13_llm_core_mock/suite_report.html`

## Remaining Caveats
* The repository was initialized during this checkpoint because the project directory was not previously a git repository.
* Local report directories are intentionally ignored by .gitignore; release validation report summaries under validation/outputs are versionable.
