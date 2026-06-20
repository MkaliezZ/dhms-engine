"""Static HTML report generator for Agent Harness suite reports."""

from __future__ import annotations

import html
import json
import os
from pathlib import Path
from typing import Any


def write_agent_suite_html_report(suite_result: dict[str, Any], output_path: str | Path) -> str:
    path = Path(output_path)
    path.write_text(build_agent_suite_html(suite_result, path), encoding="utf-8")
    return str(path)


def build_agent_suite_html(result: dict[str, Any], output_path: Path) -> str:
    summary = result.get("summary", {}) if isinstance(result.get("summary"), dict) else {}
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>DHMS Agent Harness Suite Report</title>
{style_block()}
</head>
<body>
<main>
<header>
<p class="eyebrow">DHMS Agent Harness</p>
<h1>DHMS Agent Harness Suite Report</h1>
<p>Static aggregate dry-run diagnosis report for agent case suites.</p>
<div class="meta">
{pill('suite', result.get('suite_name'))}
{pill('run_id', result.get('suite_run_id'))}
{pill('adapter', result.get('adapter'))}
{pill('trial_count', result.get('trial_count'))}
{pill('dry_run_all_cases', summary.get('dry_run_all_cases'))}
{severity_badge(summary.get('suite_severity'))}
</div>
</header>
{executive_summary(summary)}
{aggregate_metrics(summary)}
{diagnosis_distribution(summary)}
{expected_summary(summary)}
{semantic_summary(summary)}
{side_effect_summary(summary)}
{command_failure_summary(summary)}
{top_actionable_cases(summary)}
{per_case_paths(result, output_path)}
{reproduction_commands(result)}
{caveats_section(result)}
</main>
</body>
</html>
"""


def style_block() -> str:
    return """<style>
body { margin: 0; background: #f5f7fb; color: #1c2430; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.45; }
main { max-width: 1180px; margin: 0 auto; padding: 28px 18px 44px; }
header { background: #172033; color: white; border-radius: 8px; padding: 26px; border: 1px solid #27344d; }
h1 { margin: 0 0 8px; font-size: 30px; letter-spacing: 0; }
h2 { margin: 0 0 12px; font-size: 19px; letter-spacing: 0; }
.eyebrow { margin: 0 0 8px; color: #a9b9d8; font-size: 13px; font-weight: 700; text-transform: uppercase; }
.meta, .badges { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.pill, .severity { display: inline-block; border-radius: 6px; border: 1px solid #ccd5e3; background: #f8fafc; color: #1f2a3a; padding: 5px 8px; font-size: 13px; font-weight: 650; overflow-wrap: anywhere; }
header .pill, header .severity { background: #23314d; border-color: #405277; color: white; }
.critical { background: #ffe7e7; border-color: #f3a6a6; color: #7d1010; }
.high { background: #fff1d6; border-color: #e7bd73; color: #694300; }
.medium { background: #eef2ff; border-color: #bcc7ed; color: #243d81; }
.low { background: #eaf7ee; border-color: #acd7b6; color: #18512a; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin: 18px 0; }
.card { background: white; border: 1px solid #dce3ef; border-radius: 8px; padding: 18px; margin: 16px 0; box-shadow: 0 1px 2px rgba(15, 23, 42, .04); }
.metric .label { color: #667389; font-size: 13px; }
.metric .value { margin-top: 5px; font-size: 22px; font-weight: 750; overflow-wrap: anywhere; }
.kv, .data { width: 100%; border-collapse: collapse; }
.kv th, .kv td, .data th, .data td { padding: 8px 10px; border-top: 1px solid #e6ebf3; text-align: left; vertical-align: top; }
.kv th, .data th { color: #637086; font-size: 13px; }
.kv th { width: 240px; }
pre { margin: 0; background: #111827; color: #eef2ff; border-radius: 8px; padding: 14px; overflow: auto; white-space: pre-wrap; overflow-wrap: anywhere; }
.warning { border-color: #f0b0b0; background: #fff7f7; }
.ok { border-color: #b9dfc2; background: #f6fff8; }
a { color: #315fbd; overflow-wrap: anywhere; }
</style>"""


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def pill(label: str, value: Any) -> str:
    return f'<span class="pill">{esc(label)}: {esc(value)}</span>'


def severity_badge(value: Any) -> str:
    severity = str(value or "not_available")
    css = severity.lower() if severity in {"Critical", "High", "Medium", "Low"} else ""
    return f'<span class="severity {esc(css)}">Severity: {esc(severity)}</span>'


def metric_card(label: str, value: Any) -> str:
    return f'<div class="card metric"><div class="label">{esc(label)}</div><div class="value">{esc(value)}</div></div>'


def kv_table(rows: list[tuple[str, Any]]) -> str:
    body = "".join(f"<tr><th>{esc(key)}</th><td>{format_value(value)}</td></tr>" for key, value in rows)
    return f'<table class="kv"><tbody>{body}</tbody></table>'


def format_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return f"<pre>{esc(json.dumps(value, indent=2, sort_keys=True))}</pre>"
    return esc(value)


def executive_summary(summary: dict[str, Any]) -> str:
    return (
        '<section class="grid">'
        + metric_card("Total Cases", summary.get("total_cases"))
        + metric_card("Total Traces", summary.get("total_traces"))
        + metric_card("Cases With Errors", summary.get("cases_with_errors"))
        + metric_card("Suite Severity", summary.get("suite_severity"))
        + "</section>"
        + '<section class="card"><h2>Executive Summary</h2>'
        + kv_table(
            [
                ("total_cases", summary.get("total_cases")),
                ("total_traces", summary.get("total_traces")),
                ("cases_with_errors", summary.get("cases_with_errors")),
                ("side_effects_attempted", summary.get("total_side_effect_attempts")),
                ("side_effects_blocked", summary.get("total_side_effects_blocked")),
                ("side_effects_executed", summary.get("total_side_effects_executed")),
                ("expected_property_passed", summary.get("cases_with_expected_property_passed")),
                ("expected_property_failed", summary.get("cases_with_expected_property_failed")),
                ("expected_property_unknown", summary.get("cases_with_expected_property_unknown")),
                ("semantic_property_passed", summary.get("cases_with_semantic_property_passed")),
                ("semantic_property_failed", summary.get("cases_with_semantic_property_failed")),
                ("semantic_property_unknown", summary.get("cases_with_semantic_property_unknown")),
                ("safety_veto_cases", summary.get("cases_with_safety_veto")),
                ("command_adapter_failure_count", len(summary.get("command_adapter_failure_cases", []))),
                ("suite_recommendation", summary.get("suite_recommendation")),
            ]
        )
        + "</section>"
    )


def aggregate_metrics(summary: dict[str, Any]) -> str:
    keys = [
        "total_tool_calls",
        "total_memory_reads",
        "total_state_transitions",
        "total_side_effect_attempts",
        "total_side_effects_blocked",
        "total_side_effects_executed",
        "cases_with_trace_validation_errors",
    ]
    return '<section class="card"><h2>Aggregate Trace Metrics</h2>' + kv_table([(key, summary.get(key)) for key in keys]) + "</section>"


def diagnosis_distribution(summary: dict[str, Any]) -> str:
    return '<section class="card"><h2>Diagnosis Distribution</h2>' + mapping_table(summary.get("diagnosis_distribution", {})) + "</section>"


def expected_summary(summary: dict[str, Any]) -> str:
    return '<section class="card"><h2>Expected Agent Property Summary</h2>' + kv_table(
        [
            ("passed", summary.get("cases_with_expected_property_passed")),
            ("failed", summary.get("cases_with_expected_property_failed")),
            ("unknown", summary.get("cases_with_expected_property_unknown")),
        ]
    ) + "</section>"


def semantic_summary(summary: dict[str, Any]) -> str:
    return '<section class="card"><h2>Semantic Property Summary</h2>' + kv_table(
        [
            ("passed", summary.get("cases_with_semantic_property_passed")),
            ("failed", summary.get("cases_with_semantic_property_failed")),
            ("unknown", summary.get("cases_with_semantic_property_unknown")),
            ("safety_veto_cases", summary.get("cases_with_safety_veto")),
        ]
    ) + "</section>"


def side_effect_summary(summary: dict[str, Any]) -> str:
    executed = int(summary.get("total_side_effects_executed") or 0)
    attempted = int(summary.get("total_side_effect_attempts") or 0)
    blocked = int(summary.get("total_side_effects_blocked") or 0)
    message = ""
    css = "card"
    if executed > 0:
        message = "<p><strong>Critical warning:</strong> Executed side effects were reported by one or more traces.</p>"
        css = "card warning"
    elif attempted > 0 and blocked >= attempted:
        message = "<p><strong>Dry-run guard working:</strong> All attempted side effects were blocked.</p>"
        css = "card ok"
    return f'<section class="{css}"><h2>Side-effect Safety Summary</h2>{message}' + kv_table(
        [
            ("attempted", attempted),
            ("blocked", blocked),
            ("executed", executed),
            ("side_effect_risk_cases", len(summary.get("side_effect_risk_cases", []))),
            ("unsafe_execution_cases", len(summary.get("unsafe_execution_cases", []))),
        ]
    ) + "</section>"


def command_failure_summary(summary: dict[str, Any]) -> str:
    return '<section class="card"><h2>Command Adapter Failure Summary</h2>' + mapping_table(summary.get("command_failure_summary", {})) + "</section>"


def top_actionable_cases(summary: dict[str, Any]) -> str:
    rows = []
    for case in summary.get("top_actionable_cases", []):
        if not isinstance(case, dict):
            continue
        paths = case.get("report_paths", {}) if isinstance(case.get("report_paths"), dict) else {}
        rows.append(
            "<tr>"
            f"<td>{esc(case.get('case_id'))}</td><td>{esc(case.get('primary_issue'))}</td>"
            f"<td>{esc(case.get('severity'))}</td><td>{esc(case.get('expected_property_passed'))}</td>"
            f"<td>{esc(case.get('semantic_property_result'))}</td><td>{esc(case.get('safety_veto'))}</td>"
            f"<td>{esc(paths.get('markdown', 'not_available'))}</td>"
            "</tr>"
        )
    return table_section("Top Actionable Cases", ["case_id", "primary diagnosis", "severity", "expected_property", "semantic_property", "safety_veto", "per-case report path"], rows)


def per_case_paths(result: dict[str, Any], output_path: Path) -> str:
    rows = []
    output_dir = output_path.parent
    for case in result.get("case_results", []):
        if not isinstance(case, dict):
            continue
        paths = case.get("report_paths", {}) if isinstance(case.get("report_paths"), dict) else {}
        html_path = rel_link(paths.get("html"), output_dir)
        md_path = rel_link(paths.get("markdown"), output_dir)
        json_path = rel_link(paths.get("json"), output_dir)
        rows.append(
            "<tr>"
            f"<td>{esc(case.get('case_id'))}</td>"
            f'<td>{html_anchor(html_path, "html")}</td>'
            f'<td>{html_anchor(md_path, "markdown")}</td>'
            f'<td>{html_anchor(json_path, "json")}</td>'
            "</tr>"
        )
    return table_section("Per-case Report Paths", ["case_id", "agent_harness_report.html", "agent_harness_report.md", "agent_harness_report.json"], rows)


def reproduction_commands(result: dict[str, Any]) -> str:
    rows = []
    for case in result.get("case_results", []):
        if isinstance(case, dict):
            rows.append(f"<tr><td>{esc(case.get('case_id'))}</td><td><pre>{esc(case.get('reproduction_command', 'not_available'))}</pre></td></tr>")
    return table_section("Reproduction Commands", ["case_id", "command"], rows)


def caveats_section(result: dict[str, Any]) -> str:
    caveats = result.get("caveats", [])
    if not isinstance(caveats, list):
        caveats = []
    return '<section class="card"><h2>Caveats</h2><ul>' + "".join(f"<li>{esc(item)}</li>" for item in caveats) + "</ul></section>"


def mapping_table(mapping: Any) -> str:
    if not isinstance(mapping, dict) or not mapping:
        return "<p>None recorded.</p>"
    rows = "".join(f"<tr><th>{esc(key)}</th><td>{esc(value)}</td></tr>" for key, value in sorted(mapping.items()))
    return f'<table class="kv"><tbody>{rows}</tbody></table>'


def table_section(title: str, headers: list[str], rows: list[str]) -> str:
    if not rows:
        return f'<section class="card"><h2>{esc(title)}</h2><p>None recorded.</p></section>'
    head = "".join(f"<th>{esc(header)}</th>" for header in headers)
    return f'<section class="card"><h2>{esc(title)}</h2><table class="data"><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></section>'


def rel_link(path: Any, output_dir: Path) -> str:
    if not path:
        return "not_available"
    value = str(path)
    try:
        return os.path.relpath(value, start=str(output_dir))
    except ValueError:
        return value


def html_anchor(path: str, label: str) -> str:
    if path == "not_available":
        return esc(path)
    return f'<a href="{esc(path)}">{esc(label)}</a>'
