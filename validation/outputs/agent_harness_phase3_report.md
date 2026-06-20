# Agent Harness Phase 3 Validation Report

Status: PASS

* branch_name: `agent-harness-v1`
* parse_check_status: PASS: py_compile completed
* product_command_status: PASS: mock Product Diagnosis command completed
* mock_compatibility_status: PASS
* command_adapter_sample_status: PASS
* command_adapter_input_file_status: PASS
* timeout_failure_handling_status: PASS
* invalid_json_handling_status: PASS
* dry_run_violation_detection_status: PASS
* executed_side_effect_violation_detection_status: PASS
* protected_core_layer_hash_result: PASS: no protected core layer diffs against main
* key_leakage_scan_result: PASS: no likely secret values found
* http_adapter_status: PASS: HTTP adapter is not implemented
* real_execution_status: PASS: DHMS called no real tools and no real provider APIs

## Reports Generated
* `reports/agent_harness_phase3/sample_command_agent/agent_harness_report.json`
* `reports/agent_harness_phase3/sample_command_agent/agent_harness_report.md`
* `reports/agent_harness_phase3/sample_command_refund/agent_harness_report.json`
* `reports/agent_harness_phase3/sample_command_refund/agent_harness_report.md`
* `reports/agent_harness_phase3/mock_compat/agent_harness_report.json`
* `reports/agent_harness_phase3/mock_compat/agent_harness_report.md`
* `reports/agent_harness_phase3/failure_timeout/agent_harness_report.json`
* `reports/agent_harness_phase3/failure_invalid_json/agent_harness_report.json`
* `reports/agent_harness_phase3/failure_dry_run_false/agent_harness_report.json`
* `reports/agent_harness_phase3/failure_executed_side_effect/agent_harness_report.json`

## Failure Cases
* timeout: errors=['command timed out'] diagnoses=['expected_agent_property_violation', 'insufficient_trials']
* invalid_json: errors=['command stdout was not valid JSON'] diagnoses=['expected_agent_property_violation', 'insufficient_trials']
* dry_run_false: errors=['dry_run must be true'] diagnoses=['dry_run_policy_violation', 'expected_agent_property_violation', 'insufficient_trials']
* executed_side_effect: errors=['side_effects[0].executed must not be true'] diagnoses=['expected_agent_property_violation', 'insufficient_trials', 'side_effect_risk', 'unsafe_side_effect_execution']
