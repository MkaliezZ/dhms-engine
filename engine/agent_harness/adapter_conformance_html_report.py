"""Static HTML report generator for adapter conformance reports."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def write_adapter_conformance_html_report(report: dict[str, Any], output_path: str | Path) -> str:
    path = Path(output_path)
    path.write_text(build_adapter_conformance_html(report), encoding="utf-8")
    return str(path)


def build_adapter_conformance_html(report: dict[str, Any]) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>DHMS Adapter Conformance Report</title>
{style_block()}
</head>
<body>
<main>
<header>
<p class="eyebrow">DHMS Agent Harness</p>
<h1>Adapter Conformance Report</h1>
<p>Local dry-run protocol conformance report for BYOA command-agent wrappers.</p>
<div class="meta">
{badge('overall', report.get('overall_status'))}
{pill('score', report.get('adapter_readiness_score'))}
{pill('protocol', report.get('protocol_version'))}
</div>
</header>
<section class="grid">
{metric_card('Overall Status', report.get('overall_status'))}
{metric_card('Readiness Score', report.get('adapter_readiness_score'))}
{metric_card('Blocking Failures', len(report.get('blocking_failures', [])))}
{metric_card('Warnings', report.get('warning_count'))}
</section>
<section class="card">
<h2>Executive Summary</h2>
{kv_table([
    ('adapter_command', report.get('adapter_command')),
    ('overall_status', report.get('overall_status')),
    ('adapter_readiness_score', report.get('adapter_readiness_score')),
    ('pass_count', report.get('pass_count')),
    ('fail_count', report.get('fail_count')),
    ('warning_count', report.get('warning_count')),
    ('generated_at', report.get('generated_at')),
])}
</section>
{blocking_failures_section(report.get('blocking_failures', []))}
{check_results_section(report.get('check_results', []))}
{probe_results_section(report.get('probe_results', []))}
{recommendations_section(report.get('check_results', []))}
{caveats_section(report.get('caveats', []))}
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
.meta { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.pill, .badge { display: inline-block; border-radius: 6px; border: 1px solid #ccd5e3; background: #f8fafc; color: #1f2a3a; padding: 5px 8px; font-size: 13px; font-weight: 650; overflow-wrap: anywhere; }
header .pill, header .badge { background: #23314d; border-color: #405277; color: white; }
.pass { background: #eaf7ee; border-color: #acd7b6; color: #18512a; }
.warn { background: #fff1d6; border-color: #e7bd73; color: #694300; }
.fail { background: #ffe7e7; border-color: #f3a6a6; color: #7d1010; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin: 18px 0; }
.card { background: white; border: 1px solid #dce3ef; border-radius: 8px; padding: 18px; margin: 16px 0; box-shadow: 0 1px 2px rgba(15, 23, 42, .04); }
.metric .label { color: #667389; font-size: 13px; }
.metric .value { margin-top: 5px; font-size: 22px; font-weight: 750; overflow-wrap: anywhere; }
.kv, .data { width: 100%; border-collapse: collapse; }
.kv th, .kv td, .data th, .data td { padding: 8px 10px; border-top: 1px solid #e6ebf3; text-align: left; vertical-align: top; }
.kv th, .data th { color: #637086; font-size: 13px; }
.kv th { width: 230px; }
pre { margin: 0; background: #111827; color: #eef2ff; border-radius: 8px; padding: 12px; overflow: auto; white-space: pre-wrap; overflow-wrap: anywhere; }
</style>"""


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def pill(label: str, value: Any) -> str:
    return f'<span class="pill">{esc(label)}: {esc(value)}</span>'


def badge(label: str, value: Any) -> str:
    status = str(value or "unknown").lower()
    css = status if status in {"pass", "warn", "fail"} else ""
    return f'<span class="badge {esc(css)}">{esc(label)}: {esc(value)}</span>'


def metric_card(label: str, value: Any) -> str:
    return f'<div class="card metric"><div class="label">{esc(label)}</div><div class="value">{esc(value)}</div></div>'


def kv_table(rows: list[tuple[str, Any]]) -> str:
    body = "".join(f"<tr><th>{esc(key)}</th><td>{format_value(value)}</td></tr>" for key, value in rows)
    return f'<table class="kv"><tbody>{body}</tbody></table>'


def format_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return f"<pre>{esc(json.dumps(value, indent=2, sort_keys=True))}</pre>"
    return esc(value)


def blocking_failures_section(items: Any) -> str:
    failures = items if isinstance(items, list) else []
    if not failures:
        return '<section class="card"><h2>Blocking Failures</h2><p>None.</p></section>'
    return '<section class="card"><h2>Blocking Failures</h2><ul>' + "".join(f"<li>{esc(item)}</li>" for item in failures) + "</ul></section>"


def check_results_section(items: Any) -> str:
    rows = []
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        rows.append(
            "<tr>"
            f"<td>{badge('', item.get('status'))}</td>"
            f"<td>{esc(item.get('check_id'))}</td>"
            f"<td>{esc(item.get('category'))}</td>"
            f"<td>{esc(item.get('severity'))}</td>"
            f"<td>{esc(item.get('name'))}</td>"
            f"<td>{format_value(item.get('evidence', {}))}</td>"
            "</tr>"
        )
    return table_section("Check Results", ["status", "check_id", "category", "severity", "name", "evidence"], rows)


def probe_results_section(items: Any) -> str:
    rows = []
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        rows.append(
            "<tr>"
            f"<td>{esc(item.get('case_id'))}</td>"
            f"<td>{esc(item.get('name'))}</td>"
            f"<td>{esc(item.get('status'))}</td>"
            f"<td>{esc(item.get('primary_failure'))}</td>"
            f"<td>{esc(item.get('focus'))}</td>"
            "</tr>"
        )
    return table_section("Probe Results", ["case_id", "name", "status", "primary_failure", "focus"], rows)


def recommendations_section(items: Any) -> str:
    recs = []
    for item in items if isinstance(items, list) else []:
        if isinstance(item, dict) and item.get("status") != "PASS" and item.get("recommendation"):
            recs.append(f"<li>{esc(item.get('recommendation'))}</li>")
    if not recs:
        recs.append("<li>Adapter passed conformance checks. Run full agent suites next.</li>")
    return '<section class="card"><h2>Recommendations</h2><ul>' + "".join(recs) + "</ul></section>"


def caveats_section(items: Any) -> str:
    caveats = items if isinstance(items, list) else []
    caveats = list(caveats) + ["Not production certification."]
    return '<section class="card"><h2>Caveats</h2><ul>' + "".join(f"<li>{esc(item)}</li>" for item in caveats) + "</ul></section>"


def table_section(title: str, headers: list[str], rows: list[str]) -> str:
    if not rows:
        return f'<section class="card"><h2>{esc(title)}</h2><p>None recorded.</p></section>'
    head = "".join(f"<th>{esc(header)}</th>" for header in headers)
    return f'<section class="card"><h2>{esc(title)}</h2><table class="data"><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></section>'
