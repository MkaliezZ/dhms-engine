# Agent Harness MVP Smoke Report

* status: PASS
* branch_name: agent-harness-v1
* smoke_version: agent_harness_mvp_smoke_phase4_5

## Checks

* product_command_status: PASS
* single_mock_status: PASS
* single_command_status: PASS
* mock_suite_status: PASS
* command_suite_status: PASS
* invalid_json_bad_agent_status: PASS
* dry_run_false_bad_agent_status: PASS
* executed_side_effect_bad_agent_status: PASS
* wrong_protocol_bad_agent_status: PASS
* http_adapter_status: PASS
* no_real_provider_api_called_by_dhms: PASS
* no_real_external_tool_executed_by_dhms: PASS
* protected_core_layer_hash_result: PASS
* key_leakage_scan_result: PASS

## Report Index

* mock_suite: reports/agent_harness_phase45/mock_suite/suite_agent_report.md
* command_suite: reports/agent_harness_phase45/command_suite/suite_agent_report.md
* bad_invalid_json: reports/agent_harness_phase45/bad_invalid_json/agent_harness_report.md
* bad_dry_run_false: reports/agent_harness_phase45/bad_dry_run_false/agent_harness_report.md
* bad_executed_side_effect: reports/agent_harness_phase45/bad_executed_side_effect/agent_harness_report.md
* bad_wrong_protocol: reports/agent_harness_phase45/bad_wrong_protocol/agent_harness_report.md

## Caveats

* dry-run only
* local command BYOA only
* HTTP adapter not implemented
* no real tool permission
* sample agents are not production agents
* n=1 is preliminary
