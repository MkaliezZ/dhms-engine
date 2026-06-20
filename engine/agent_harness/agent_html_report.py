"""Static HTML report generator for Agent Harness single-case reports."""

from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def write_agent_harness_html_report(result: dict[str, Any], output_path: str | Path) -> str:
    path = Path(output_path)
    path.write_text(build_agent_harness_html(result), encoding="utf-8")
    return str(path)


def build_agent_harness_html(result: dict[str, Any]) -> str:
    summary = result.get("diagnosis_summary", {}) if isinstance(result.get("diagnosis_summary"), dict) else {}
    metrics = result.get("trace_metrics", {}) if isinstance(result.get("trace_metrics"), dict) else {}
    expected = result.get("expected_property_check", {}) if isinstance(result.get("expected_property_check"), dict) else {}
    execution_safety = result.get("execution_safety_result", {}) if isinstance(result.get("execution_safety_result"), dict) else {}
    semantic = result.get("semantic_property_result", {}) if isinstance(result.get("semantic_property_result"), dict) else {}
    judge_result = result.get("judge_result", semantic) if isinstance(result.get("judge_result", semantic), dict) else {}
    traces = result.get("traces", []) if isinstance(result.get("traces"), list) else []
    side_effects = [item for trace in traces for item in trace.get("side_effects", []) if isinstance(item, dict)]
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>DHMS Agent Harness Report</title>
{style_block()}
</head>
<body>
<main>
<header>
<p class="eyebrow">DHMS Agent Harness</p>
<h1>DHMS Agent Harness Report</h1>
<p>Static dry-run trace diagnosis report for local mock or BYOA command agents.</p>
<div class="meta">
{pill('adapter', result.get('adapter'))}
{pill('mode', result.get('mode'))}
{pill('trials', result.get('trial_count'))}
{pill('dry_run', result.get('dry_run'))}
{severity_badge(summary.get('severity'))}
</div>
</header>
<section class="grid">
{metric_card('Primary Diagnosis', summary.get('primary_issue', 'not_available'))}
{metric_card('Side Effects Blocked', result.get('side_effects_blocked_count', 0))}
{metric_card('Side Effects Executed', metrics.get('side_effect_executed_count', 0))}
{metric_card('Trace Count', metrics.get('trace_count', len(traces)))}
</section>
<section class="card">
<h2>Executive Summary</h2>
{kv_table([
    ('adapter', result.get('adapter')),
    ('command', result.get('agent_command', 'not_applicable')),
    ('input_text', result.get('input_text', 'not_available')),
    ('dry_run', result.get('dry_run')),
    ('mode', result.get('mode')),
    ('trial_count', result.get('trial_count')),
    ('primary_issue', summary.get('primary_issue', 'not_available')),
    ('severity', summary.get('severity', 'not_available')),
    ('confidence', summary.get('confidence', 'not_available')),
    ('short_explanation', summary.get('short_explanation', 'not_available')),
    ('generated_at', datetime.now().isoformat(timespec='seconds')),
])}
</section>
{diagnosis_section(result.get('diagnoses', []))}
{command_failure_section(result)}
{side_effect_section(side_effects, metrics)}
{execution_safety_section(execution_safety)}
{expected_section(expected)}
{semantic_property_section(semantic, judge_result)}
{trace_metrics_section(metrics)}
{tool_calls_section(traces)}
{memory_reads_section(traces)}
{state_transitions_section(traces)}
{recommendations_section(result.get('recommendation_evidence', []))}
{reproduction_section(result)}
{caveats_section(result)}
{raw_trace_section(traces)}
</main>
</body>
</html>
"""


def style_block() -> str:
    return """<style>
:root { color-scheme: light; }
body { margin: 0; background: #f5f7fb; color: #1c2430; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.45; }
main { max-width: 1180px; margin: 0 auto; padding: 28px 18px 44px; }
header { background: #172033; color: white; border-radius: 8px; padding: 26px; border: 1px solid #27344d; }
h1 { margin: 0 0 8px; font-size: 30px; letter-spacing: 0; }
h2 { margin: 0 0 12px; font-size: 19px; letter-spacing: 0; }
h3 { margin: 12px 0 8px; font-size: 16px; letter-spacing: 0; }
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
.kv { width: 100%; border-collapse: collapse; }
.kv th, .kv td { padding: 8px 10px; border-top: 1px solid #e6ebf3; text-align: left; vertical-align: top; }
.kv th { width: 230px; color: #637086; font-weight: 650; }
.data { width: 100%; border-collapse: collapse; }
.data th, .data td { padding: 8px 10px; border-top: 1px solid #e6ebf3; text-align: left; vertical-align: top; }
.data th { color: #637086; font-size: 13px; }
pre { margin: 0; background: #111827; color: #eef2ff; border-radius: 8px; padding: 14px; overflow: auto; white-space: pre-wrap; overflow-wrap: anywhere; }
.warning { border-color: #f0b0b0; background: #fff7f7; }
.ok { border-color: #b9dfc2; background: #f6fff8; }
details summary { cursor: pointer; font-weight: 700; margin-bottom: 10px; }
a { color: #315fbd; }
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


def diagnosis_section(diagnoses: Any) -> str:
    items = diagnoses if isinstance(diagnoses, list) else []
    if not items:
        return '<section class="card"><h2>Diagnosis</h2><p>No diagnoses available.</p></section>'
    cards = []
    for item in items:
        if not isinstance(item, dict):
            continue
        severity = item.get("severity")
        cards.append(
            '<div class="card">'
            f"<h3>{esc(item.get('type', 'unknown'))}</h3>"
            f'<div class="badges">{severity_badge(severity)}{pill("confidence", item.get("confidence"))}</div>'
            f"<p>{esc(item.get('interpretation', 'not_available'))}</p>"
            f"{kv_table([('meaning', item.get('meaning')), ('evidence', item.get('evidence')), ('recommended_actions', item.get('recommended_actions'))])}"
            "</div>"
        )
    return '<section><h2>Diagnosis Badges</h2>' + "".join(cards) + "</section>"


def command_failure_section(result: dict[str, Any]) -> str:
    failure_type = result.get("command_failure_type")
    if not failure_type:
        return '<section class="card"><h2>Command Adapter Failure</h2><p>No command adapter failure recorded.</p></section>'
    rows = [
        ("failure_type", failure_type),
        ("failure_reason", result.get("command_failure_reason")),
        ("failure_evidence", result.get("command_failure_evidence")),
        ("stderr_preview", result.get("stderr_preview") or "none"),
        ("command_exit_status", result.get("command_exit_status", "not_available")),
        ("recommended_fix", command_failure_fix(failure_type)),
    ]
    return '<section class="card warning"><h2>Command Adapter Failure</h2>' + kv_table(rows) + "</section>"


def side_effect_section(side_effects: list[dict[str, Any]], metrics: dict[str, Any]) -> str:
    executed = int(metrics.get("side_effect_executed_count") or 0)
    warning = ""
    if executed > 0:
        warning = (
            '<div class="card warning"><strong>Critical warning:</strong> Unsafe side effect execution was '
            "reported by the agent trace. Do not use this adapter for production until fixed.</div>"
        )
    rows = [
        ("attempted count", metrics.get("side_effect_attempt_count", 0)),
        ("blocked count", metrics.get("side_effect_blocked_count", 0)),
        ("executed count", executed),
    ]
    table_rows = []
    for item in side_effects:
        table_rows.append(
            "<tr>"
            f"<td>{esc(item.get('type'))}</td><td>{esc(item.get('target'))}</td>"
            f"<td>{esc(item.get('attempted'))}</td><td>{esc(item.get('blocked'))}</td>"
            f"<td>{esc(item.get('executed'))}</td><td>{esc(item.get('reason'))}</td>"
            "</tr>"
        )
    table = '<p>No side effects recorded.</p>'
    if table_rows:
        table = (
            '<table class="data"><thead><tr><th>type</th><th>target</th><th>attempted</th>'
            "<th>blocked</th><th>executed</th><th>reason</th></tr></thead><tbody>"
            + "".join(table_rows)
            + "</tbody></table>"
        )
    return '<section class="card"><h2>Side-effect Safety</h2>' + warning + kv_table(rows) + table + "</section>"


def expected_section(expected: dict[str, Any]) -> str:
    rows = [
        ("passed", expected.get("passed", "unknown")),
        ("confidence", expected.get("confidence", "low")),
        ("evidence", expected.get("evidence", [])),
        ("notes", expected.get("notes", "not_available")),
    ]
    return '<section class="card"><h2>Expected Agent Property Check</h2>' + kv_table(rows) + "</section>"


def execution_safety_section(execution_safety: dict[str, Any]) -> str:
    rows = [
        ("overall", execution_safety.get("overall", "unknown")),
        ("safety_veto", execution_safety.get("safety_veto", False)),
        ("violations", execution_safety.get("violations", [])),
        ("tool_executed_count", execution_safety.get("tool_executed_count", 0)),
        ("side_effect_executed_count", execution_safety.get("side_effect_executed_count", 0)),
        ("trace_validation_failed", execution_safety.get("trace_validation_failed", False)),
    ]
    css = "card warning" if execution_safety.get("safety_veto") else "card ok"
    return f'<section class="{css}"><h2>Execution Safety Result</h2>' + kv_table(rows) + "</section>"


def semantic_property_section(semantic: dict[str, Any], judge_result: dict[str, Any]) -> str:
    rows = [
        ("property_check_version", semantic.get("property_check_version", "not_available")),
        ("judge_result_alias", judge_result.get("overall", "unknown")),
        ("judge_mode", semantic.get("judge_mode", "deterministic")),
        ("overall", semantic.get("overall", "unknown")),
        ("safety_veto", semantic.get("safety_veto", False)),
        ("confidence", semantic.get("confidence", "low")),
        ("unknown_reason", semantic.get("unknown_reason", "") or "none"),
        ("observable_evidence", semantic.get("observable_evidence", {})),
        ("constraints", semantic.get("constraints", [])),
    ]
    return '<section class="card"><h2>Semantic Property Result</h2>' + kv_table(rows) + "</section>"


def trace_metrics_section(metrics: dict[str, Any]) -> str:
    keys = [
        "final_answer_unique_count",
        "tool_call_count",
        "memory_read_count",
        "state_transition_count",
        "side_effect_attempt_count",
        "side_effect_blocked_count",
        "side_effect_executed_count",
        "error_count",
        "dry_run_all_traces",
        "trace_count",
    ]
    return '<section class="card"><h2>Trace Metrics</h2>' + kv_table([(key, metrics.get(key)) for key in keys]) + "</section>"


def tool_calls_section(traces: list[dict[str, Any]]) -> str:
    rows = []
    for trace in traces:
        for item in trace.get("tool_calls", []):
            if isinstance(item, dict):
                rows.append(
                    "<tr>"
                    f"<td>{esc(item.get('tool_name'))}</td><td>{esc(item.get('intent'))}</td>"
                    f"<td>{esc(item.get('executed'))}</td><td>{esc(item.get('blocked'))}</td>"
                    f"<td>{esc(item.get('reason'))}</td><td><pre>{esc(json.dumps(item.get('arguments', {}), sort_keys=True))}</pre></td>"
                    "</tr>"
                )
    return table_section("Tool Calls", ["tool_name", "intent", "executed", "blocked", "reason", "arguments"], rows)


def memory_reads_section(traces: list[dict[str, Any]]) -> str:
    rows = []
    for trace in traces:
        for item in trace.get("memory_reads", []):
            if isinstance(item, dict):
                rows.append(
                    "<tr>"
                    f"<td>{esc(item.get('key'))}</td><td>{esc(item.get('value_preview'))}</td>"
                    f"<td>{esc(item.get('source'))}</td><td>{esc(item.get('confidence'))}</td>"
                    f"<td>{esc(item.get('freshness'))}</td><td>{esc(item.get('used_in_answer'))}</td>"
                    "</tr>"
                )
    return table_section("Memory Reads", ["key", "value_preview", "source", "confidence", "freshness", "used_in_answer"], rows)


def state_transitions_section(traces: list[dict[str, Any]]) -> str:
    rows = []
    for trace in traces:
        for item in trace.get("state_transitions", []):
            if isinstance(item, dict):
                rows.append(
                    "<tr>"
                    f"<td>{esc(item.get('from_state'))}</td><td>{esc(item.get('to_state'))}</td><td>{esc(item.get('reason'))}</td>"
                    "</tr>"
                )
    return table_section("State Transitions", ["from_state", "to_state", "reason"], rows)


def table_section(title: str, headers: list[str], rows: list[str]) -> str:
    if not rows:
        return f'<section class="card"><h2>{esc(title)}</h2><p>None recorded.</p></section>'
    head = "".join(f"<th>{esc(header)}</th>" for header in headers)
    return f'<section class="card"><h2>{esc(title)}</h2><table class="data"><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></section>'


def recommendations_section(recommendations: Any) -> str:
    items = recommendations if isinstance(recommendations, list) else []
    if not items:
        return '<section class="card"><h2>Recommendations</h2><p>No recommendations recorded.</p></section>'
    rows = []
    for item in items:
        if isinstance(item, dict):
            rows.append(
                "<tr>"
                f"<td>{esc(item.get('priority'))}</td><td>{esc(item.get('action'))}</td>"
                f"<td>{esc(item.get('reason'))}</td><td>{format_value(item.get('evidence', []))}</td>"
                f"<td>{esc(item.get('affected_layer'))}</td><td>{esc(item.get('confidence'))}</td>"
                "</tr>"
            )
    return table_section("Recommendations", ["priority", "action", "reason", "evidence", "affected_layer", "confidence"], rows)


def reproduction_section(result: dict[str, Any]) -> str:
    command = result.get("reproduction_command")
    if not command:
        return '<section class="card"><h2>Reproduction Command</h2><p>not_available</p></section>'
    return f'<section class="card"><h2>Reproduction Command</h2><pre>{esc(command)}</pre></section>'


def caveats_section(result: dict[str, Any]) -> str:
    caveats = [
        "dry-run only",
        "HTTP adapter not implemented",
        "no real tool permission",
        "sample agents are not production agents",
    ]
    if result.get("adapter") == "command":
        caveats.append("local command BYOA only")
    if int(result.get("trial_count") or 0) <= 1:
        caveats.append("n=1 is preliminary")
    return '<section class="card"><h2>Caveats</h2><ul>' + "".join(f"<li>{esc(item)}</li>" for item in caveats) + "</ul></section>"


def raw_trace_section(traces: list[dict[str, Any]]) -> str:
    preview = json.dumps(traces, indent=2, sort_keys=True)[:20000]
    return f'<section class="card"><details><summary>Raw trace preview</summary><pre>{esc(preview)}</pre></details></section>'


def command_failure_fix(failure_type: Any) -> str:
    fixes = {
        "invalid_json": "Ensure the local agent writes exactly one valid JSON object to stdout.",
        "wrong_protocol": 'Use protocol_version="dhms-agent-command-v1".',
        "timeout": "Confirm the local agent is not hanging before increasing timeout.",
        "trace_validation_error": "Return a complete AgentTrace with all required fields.",
        "nonzero_exit": "Fix local agent process errors before suite runs.",
        "missing_trace": "Return a top-level trace object.",
        "dry_run_false": "Set dry_run=true for every command-agent trace.",
        "executed_side_effect": "Record side effects as blocked trace evidence, not executed actions.",
    }
    return fixes.get(str(failure_type), "not_applicable")
