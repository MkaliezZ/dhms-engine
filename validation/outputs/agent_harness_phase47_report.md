# Agent Harness Phase 4.7 Validation Report

* status: PASS
* branch_name: agent-harness-v1
* phase: 4.7_static_html_report_polish

## Checks

* single_mock_html_status: PASS
* single_command_html_status: PASS
* mock_suite_html_status: PASS
* command_suite_html_status: PASS
* bad_invalid_json_html_status: PASS
* bad_wrong_protocol_html_status: PASS
* bad_executed_side_effect_html_status: PASS
* suite_html_sections_status: PASS
* no_external_assets_status: PASS
* no_script_src_status: PASS
* html_escape_probe_status: PASS
* product_command_status: PASS
* mvp_smoke_status: PASS
* http_adapter_status: PASS
* no_real_provider_api_called_by_dhms: PASS
* no_real_external_tool_executed_by_dhms: PASS
* protected_core_layer_hash_result: PASS
* key_leakage_scan_result: PASS

## Generated HTML Report Paths

* single_mock: reports/agent_harness_phase47/mock_single/agent_harness_report.html
* single_command: reports/agent_harness_phase47/command_single/agent_harness_report.html
* mock_suite: reports/agent_harness_phase47/mock_suite/suite_agent_report.html
* command_suite: reports/agent_harness_phase47/command_suite/suite_agent_report.html
* bad_invalid_json: reports/agent_harness_phase47/bad_invalid_json/agent_harness_report.html
* bad_wrong_protocol: reports/agent_harness_phase47/bad_wrong_protocol/agent_harness_report.html
* bad_executed_side_effect: reports/agent_harness_phase47/bad_executed_side_effect/agent_harness_report.html

## Caveats

* static local HTML only
* dry-run only
* local command BYOA only
* HTTP adapter not implemented
* no dashboard or server
* no real external tool permission
* n=1 is preliminary
