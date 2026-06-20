# Agent Harness Phase 5 Adapter Conformance Validation Report

* status: PASS
* branch_name: agent-harness-v1
* phase: 5_adapter_conformance_test_kit
* sample_readiness_score: 100

## Checks

* sample_conformance_status: PASS
* bad_invalid_json_status: PASS
* bad_wrong_protocol_status: PASS
* bad_dry_run_false_status: PASS
* bad_executed_side_effect_status: PASS
* bad_missing_trace_status: PASS
* bad_timeout_status: PASS
* conformance_json_report_status: PASS
* conformance_md_report_status: PASS
* conformance_html_report_status: PASS
* product_command_status: PASS
* single_mock_status: PASS
* single_command_status: PASS
* mock_suite_status: PASS
* command_suite_status: PASS
* mvp_smoke_status: PASS
* phase48_readiness_status: PASS
* http_adapter_status: PASS
* preview_tag_status: PASS
* no_real_provider_api_called_by_dhms: PASS
* no_real_external_tool_executed_by_dhms: PASS
* protected_core_layer_hash_result: PASS
* key_leakage_scan_result: PASS

## Generated Report Paths

* sample_json_agent: reports/adapter_conformance/sample_json_agent/adapter_conformance_report.json
* sample_json_agent_markdown: reports/adapter_conformance/sample_json_agent/adapter_conformance_report.md
* sample_json_agent_html: reports/adapter_conformance/sample_json_agent/adapter_conformance_report.html
* bad_invalid_json: reports/adapter_conformance/bad_invalid_json/adapter_conformance_report.json
* bad_invalid_json_markdown: reports/adapter_conformance/bad_invalid_json/adapter_conformance_report.md
* bad_invalid_json_html: reports/adapter_conformance/bad_invalid_json/adapter_conformance_report.html
* bad_wrong_protocol: reports/adapter_conformance/bad_wrong_protocol/adapter_conformance_report.json
* bad_wrong_protocol_markdown: reports/adapter_conformance/bad_wrong_protocol/adapter_conformance_report.md
* bad_wrong_protocol_html: reports/adapter_conformance/bad_wrong_protocol/adapter_conformance_report.html
* bad_dry_run_false: reports/adapter_conformance/bad_dry_run_false/adapter_conformance_report.json
* bad_dry_run_false_markdown: reports/adapter_conformance/bad_dry_run_false/adapter_conformance_report.md
* bad_dry_run_false_html: reports/adapter_conformance/bad_dry_run_false/adapter_conformance_report.html
* bad_executed_side_effect: reports/adapter_conformance/bad_executed_side_effect/adapter_conformance_report.json
* bad_executed_side_effect_markdown: reports/adapter_conformance/bad_executed_side_effect/adapter_conformance_report.md
* bad_executed_side_effect_html: reports/adapter_conformance/bad_executed_side_effect/adapter_conformance_report.html
* bad_missing_trace: reports/adapter_conformance/bad_missing_trace/adapter_conformance_report.json
* bad_missing_trace_markdown: reports/adapter_conformance/bad_missing_trace/adapter_conformance_report.md
* bad_missing_trace_html: reports/adapter_conformance/bad_missing_trace/adapter_conformance_report.html
* bad_timeout: reports/adapter_conformance/bad_timeout/adapter_conformance_report.json
* bad_timeout_markdown: reports/adapter_conformance/bad_timeout/adapter_conformance_report.md
* bad_timeout_html: reports/adapter_conformance/bad_timeout/adapter_conformance_report.html
* phase5_report_json: validation/outputs/agent_harness_phase5_conformance_report.json
* phase5_report_md: validation/outputs/agent_harness_phase5_conformance_report.md

## Caveats

* adapter conformance is not production certification
* dry-run only
* local BYOA command agents only
* HTTP adapter not implemented
* sample agents are not production agents
