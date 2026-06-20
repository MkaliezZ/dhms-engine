# Agent Harness Phase 4.6 Validation Report

* status: PASS
* branch_name: agent-harness-v1
* phase: 4.6_command_failure_label_polish

## Checks

* invalid_json_label_status: PASS
* wrong_protocol_label_status: PASS
* dry_run_false_status: PASS
* executed_side_effect_status: PASS
* sample_command_status: PASS
* mock_suite_status: PASS
* command_suite_status: PASS
* product_command_status: PASS
* http_adapter_status: PASS
* no_real_provider_api_called_by_dhms: PASS
* no_real_external_tool_executed_by_dhms: PASS
* protected_core_layer_hash_result: PASS
* key_leakage_scan_result: PASS

## Generated Report Paths

* invalid_json: reports/agent_harness_phase46/bad_invalid_json/agent_harness_report.md
* wrong_protocol: reports/agent_harness_phase46/bad_wrong_protocol/agent_harness_report.md
* dry_run_false: reports/agent_harness_phase46/bad_dry_run_false/agent_harness_report.md
* executed_side_effect: reports/agent_harness_phase46/bad_executed_side_effect/agent_harness_report.md
* mock_suite: reports/agent_harness_phase46/mock_suite/suite_agent_report.md
* command_suite: reports/agent_harness_phase46/command_suite/suite_agent_report.md

## Caveats

* dry-run only
* local command BYOA only
* HTTP adapter not implemented
* no real external tool permission
* no production agent certification
* n=1 is preliminary
