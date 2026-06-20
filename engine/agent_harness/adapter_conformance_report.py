"""JSON and Markdown reports for adapter conformance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .adapter_conformance_html_report import write_adapter_conformance_html_report


def write_adapter_conformance_reports(report: dict[str, Any], output_dir: str | Path) -> dict[str, str]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / "adapter_conformance_report.json"
    md_path = output_path / "adapter_conformance_report.md"
    html_path = output_path / "adapter_conformance_report.html"
    report_paths = {"json": str(json_path), "markdown": str(md_path), "html": str(html_path)}
    report_with_paths = dict(report)
    report_with_paths["report_paths"] = report_paths
    json_path.write_text(json.dumps(report_with_paths, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(build_adapter_conformance_markdown(report_with_paths), encoding="utf-8")
    write_adapter_conformance_html_report(report_with_paths, html_path)
    return report_paths


def build_adapter_conformance_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# DHMS Adapter Conformance Report",
        "",
        "## Executive Summary",
        "",
        f"* conformance_version: {report.get('conformance_version')}",
        f"* adapter_command: {report.get('adapter_command')}",
        f"* protocol_version: {report.get('protocol_version')}",
        f"* overall_status: {report.get('overall_status')}",
        f"* adapter_readiness_score: {report.get('adapter_readiness_score')}",
        f"* blocking_failures: {len(report.get('blocking_failures', []))}",
        f"* pass_count: {report.get('pass_count')}",
        f"* fail_count: {report.get('fail_count')}",
        f"* warning_count: {report.get('warning_count')}",
        "",
        "## Blocking Failures",
        "",
    ]
    failures = report.get("blocking_failures", [])
    if failures:
        lines.extend(f"* {item}" for item in failures)
    else:
        lines.append("* None")
    lines.extend(["", "## Check Results", ""])
    for item in report.get("check_results", []):
        lines.extend(
            [
                f"### {item.get('check_id')}",
                "",
                f"* name: {item.get('name')}",
                f"* status: {item.get('status')}",
                f"* severity: {item.get('severity')}",
                f"* category: {item.get('category')}",
                f"* evidence: {json.dumps(item.get('evidence', {}), sort_keys=True)}",
                f"* recommendation: {item.get('recommendation')}",
                "",
            ]
        )
    lines.extend(["## Probe Results", ""])
    for item in report.get("probe_results", []):
        suffix = ""
        if item.get("primary_failure") == "timeout":
            suffix = (
                f"; timeout_source={item.get('timeout_source') or 'unknown'}"
                f"; timeout_seconds={item.get('timeout_seconds') or 'unknown'}"
                f"; duration_seconds={item.get('duration_seconds') or 'unknown'}"
            )
        lines.extend(
            [
                f"* {item.get('case_id')}: {item.get('status')} ({item.get('primary_failure')}) - {item.get('focus')}{suffix}",
            ]
        )
        if item.get("stdout_preview"):
            lines.append(f"  * stdout_preview: {json.dumps(item.get('stdout_preview'))}")
        if item.get("stderr_preview"):
            lines.append(f"  * stderr_preview: {json.dumps(item.get('stderr_preview'))}")
    lines.extend(["", "## Safety Results", ""])
    safety_ids = {"dry_run_true", "no_executed_side_effect", "attempted_side_effects_blocked", "tool_calls_not_executed", "stderr_secret_safety"}
    for item in report.get("check_results", []):
        if item.get("check_id") in safety_ids:
            lines.append(f"* {item.get('check_id')}: {item.get('status')}")
    lines.extend(["", "## Recommendations", ""])
    recommendations = [
        item.get("recommendation")
        for item in report.get("check_results", [])
        if item.get("status") != "PASS" and item.get("recommendation")
    ]
    if recommendations:
        lines.extend(f"* {item}" for item in recommendations)
    else:
        lines.append("* Adapter passed conformance checks. Run full Agent Harness suites next.")
    lines.extend(["", "## Caveats", ""])
    lines.extend(f"* {item}" for item in report.get("caveats", []))
    lines.append("* Not production certification.")
    lines.append("")
    return "\n".join(lines)
