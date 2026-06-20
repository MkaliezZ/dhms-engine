"""Report writers for Agent Harness suite runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .agent_suite_html_report import write_agent_suite_html_report


SUITE_CAVEATS = [
    "Phase 4 suite runner does not enable real tool execution.",
    "Command adapter is local BYOA dry-run only.",
    "HTTP adapter is not implemented.",
    "n=1 is preliminary.",
    "Sample agents are not production agents.",
]


def write_agent_suite_reports(result: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "suite_agent_report.json"
    md_path = output_dir / "suite_agent_report.md"
    html_path = output_dir / "suite_agent_report.html"
    report_paths = {"json": str(json_path), "markdown": str(md_path), "html": str(html_path)}
    result_with_paths = dict(result)
    result_with_paths["report_paths"] = report_paths
    json_path.write_text(json.dumps(result_with_paths, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(build_agent_suite_markdown(result_with_paths), encoding="utf-8")
    write_agent_suite_html_report(result_with_paths, html_path)
    return report_paths


def build_agent_suite_markdown(result: dict[str, Any]) -> str:
    summary = result.get("summary", {})
    lines = [
        "# DHMS Agent Harness Suite Diagnosis Report",
        "",
        "## Executive Summary",
        "",
        f"* suite_name: {result.get('suite_name')}",
        f"* suite_run_id: {result.get('suite_run_id')}",
        f"* adapter: {result.get('adapter')}",
        f"* trial_count: {result.get('trial_count')}",
        f"* available_case_count: {result.get('available_case_count')}",
        f"* selected_case_count: {result.get('selected_case_count')}",
        f"* max_cases: {result.get('max_cases')}",
        f"* total_cases: {summary.get('total_cases')}",
        f"* suite_severity: {summary.get('suite_severity')}",
        f"* suite_recommendation: {summary.get('suite_recommendation')}",
        "",
        "## Adapter and Dry-Run Status",
        "",
        f"* dry_run_all_cases: {summary.get('dry_run_all_cases')}",
        f"* HTTP adapter: not_implemented",
        f"* real_tool_execution: disabled",
        f"* real_provider_api_calls_by_DHMS: none",
        "",
        "## Aggregate Trace Metrics",
        "",
        f"* total_traces: {summary.get('total_traces')}",
        f"* total_tool_calls: {summary.get('total_tool_calls')}",
        f"* total_memory_reads: {summary.get('total_memory_reads')}",
        f"* total_state_transitions: {summary.get('total_state_transitions')}",
        f"* total_side_effect_attempts: {summary.get('total_side_effect_attempts')}",
        f"* total_side_effects_blocked: {summary.get('total_side_effects_blocked')}",
        f"* total_side_effects_executed: {summary.get('total_side_effects_executed')}",
        f"* cases_with_errors: {summary.get('cases_with_errors')}",
        f"* cases_with_trace_validation_errors: {summary.get('cases_with_trace_validation_errors')}",
        "",
        "## Diagnosis Distribution",
        "",
    ]
    append_mapping(lines, summary.get("diagnosis_distribution", {}))
    lines.extend(["", "## Expected Agent Property Summary", ""])
    lines.extend(
        [
            f"* passed: {summary.get('cases_with_expected_property_passed')}",
            f"* failed: {summary.get('cases_with_expected_property_failed')}",
            f"* unknown: {summary.get('cases_with_expected_property_unknown')}",
            "",
            "## Side-effect Safety Summary",
            "",
            f"* side_effect_risk_cases: {len(summary.get('side_effect_risk_cases', []))}",
            f"* unsafe_execution_cases: {len(summary.get('unsafe_execution_cases', []))}",
            f"* all_attempted_side_effects_blocked: {all_attempted_side_effects_blocked(summary)}",
            "",
            "## Command Adapter Failure Summary",
            "",
        ]
    )
    append_mapping(lines, summary.get("command_failure_summary", {}))
    lines.extend(["", "## Top Actionable Cases", ""])
    append_case_list(lines, summary.get("top_actionable_cases", []))
    lines.extend(["", "## Unsafe Execution Cases", ""])
    append_case_list(lines, summary.get("unsafe_execution_cases", []))
    lines.extend(["", "## Per-case Report Paths", ""])
    for case in result.get("case_results", []):
        paths = case.get("report_paths", {})
        lines.append(f"* {case.get('case_id')}: {paths.get('markdown', 'not_available')}")
    lines.extend(["", "## Reproduction Commands", ""])
    for case in result.get("case_results", []):
        lines.append(f"* {case.get('case_id')}: `{case.get('reproduction_command', 'not_available')}`")
    lines.extend(["", "## Caveats", ""])
    lines.extend(f"* {item}" for item in result.get("caveats", SUITE_CAVEATS))
    lines.append("")
    return "\n".join(lines)


def append_mapping(lines: list[str], mapping: dict[str, Any]) -> None:
    if not mapping:
        lines.append("* none")
        return
    for key, value in sorted(mapping.items()):
        lines.append(f"* {key}: {value}")


def append_case_list(lines: list[str], cases: list[dict[str, Any]]) -> None:
    if not cases:
        lines.append("* none")
        return
    for case in cases:
        lines.append(
            f"* {case.get('case_id')}: severity={case.get('severity')} primary_issue={case.get('primary_issue')} "
            f"expected_property={case.get('expected_property_passed')}"
        )


def all_attempted_side_effects_blocked(summary: dict[str, Any]) -> bool:
    attempts = int(summary.get("total_side_effect_attempts") or 0)
    blocked = int(summary.get("total_side_effects_blocked") or 0)
    executed = int(summary.get("total_side_effects_executed") or 0)
    return attempts > 0 and blocked >= attempts and executed == 0
