"""Self-contained HTML report generator for DHMS Product Diagnosis v1.3."""

import html
from pathlib import Path
from typing import Mapping

from display_format import display_bool, display_value


def write_html_report(product_result: Mapping[str, object], output_dir: Path) -> str:
    path = output_dir / "dhms_product_report.html"
    path.write_text(build_html(product_result), encoding="utf-8")
    return str(path)


def build_html(result: Mapping[str, object]) -> str:
    risk = html.escape(str(result["risk_label"]))
    rec = html.escape(str(result["recommendation"]))
    command = html.escape(str(result["reproduction_command"]))
    models = html.escape(", ".join(result.get("models", [])))
    calibration = result.get("calibration", {})
    baseline = calibration.get("deepseek_smoke_baseline", {})
    current = calibration.get("current_run", {})
    current_models = ", ".join(current.get("real_api_models") or []) or "none"
    expected = result.get("expected_property_check", {})
    diagnosis_summary = result.get("diagnosis_summary", {})
    return f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<title>DHMS Product Report</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #f6f7f9; color: #1d2433; }}
main {{ max-width: 1040px; margin: 0 auto; padding: 32px 20px; }}
header {{ background: #17202f; color: white; padding: 28px; border-radius: 8px; }}
h1 {{ margin: 0 0 8px; font-size: 28px; letter-spacing: 0; }}
h2 {{ font-size: 18px; margin-top: 0; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin: 20px 0; }}
.card {{ background: white; border: 1px solid #dde2ea; border-radius: 8px; padding: 18px; }}
.label {{ color: #596579; font-size: 13px; }}
.value {{ font-size: 26px; font-weight: 700; margin-top: 6px; overflow-wrap: anywhere; }}
.risk {{ display: inline-block; background: #fff1cc; color: #6b4a00; border-radius: 6px; padding: 6px 10px; font-weight: 700; }}
.kv {{ display: grid; grid-template-columns: minmax(170px, 240px) 1fr; gap: 8px 16px; }}
.kv div:nth-child(odd) {{ color: #596579; }}
pre {{ background: #101827; color: #edf2ff; padding: 14px; border-radius: 8px; overflow: auto; }}
.pill {{ display:inline-block; border:1px solid #c8d1df; border-radius:6px; padding:4px 8px; margin:3px 4px 3px 0; background:#f9fbfd; }}
.diag {{ border-left:4px solid #496b9f; }}
.warn {{ background:#fff8e6; border-color:#ead39b; }}
</style>
</head>
<body>
<main>
<header>
<h1>LLM Memory Stability Tester</h1>
<p>Diagnosis-driven DHMS report for controlled memory/context perturbation behavior.</p>
<p class=\"risk\">Risk: {risk}</p>
<p><strong>Primary diagnosis:</strong> {esc(diagnosis_summary.get('primary_issue', 'not_available'))} ({esc(diagnosis_summary.get('confidence', 'not_available'))})</p>
</header>
<section class=\"grid\">
{card('Stability Score', display_value(result['stability_score']))}
{card('Sensitivity Score', display_value(result['sensitivity_score']))}
{card('Isolation Strength', display_value(result['isolation_strength_score']))}
{card('Drift Risk', display_value(result['drift_risk']))}
</section>
<section class=\"card\">
<h2>Case Identity</h2>
<div class=\"kv\">
<div>case_id</div><div>{esc(result.get('case_id', 'not_available'))}</div>
<div>case_path</div><div>{esc(result.get('case_path', 'not_available'))}</div>
<div>case_category</div><div>{esc(result.get('case_category', 'not_available'))}</div>
<div>suite_name</div><div>{esc(result.get('suite_name', 'not_available'))}</div>
<div>suite_run_id</div><div>{esc(result.get('suite_run_id', 'not_available'))}</div>
<div>requested_models</div><div>{esc(', '.join(result.get('requested_models') or result.get('models') or []))}</div>
<div>real_api_used</div><div>{esc(display_bool(result.get('real_api_used')))}</div>
</div>
</section>
<section class=\"grid\">
<div class=\"card\"><h2>DeepSeek Validation Baseline</h2><div class=\"kv\">
<div>Status</div><div>{esc(baseline.get('status', 'not_available'))}</div>
<div>Real API used</div><div>{esc(display_bool(baseline.get('real_api_used')))}</div>
<div>Fallback used</div><div>{esc(display_bool(baseline.get('fallback_used')))}</div>
<div>Total real API calls</div><div>{esc(display_value(baseline.get('total_real_api_calls')))}</div>
</div></div>
<div class=\"card\"><h2>Current Run Real API Status</h2><div class=\"kv\">
<div>Current run real API</div><div>{esc('Yes' if current.get('real_api_used') else 'No')}</div>
<div>Provider/model</div><div>{esc(current_models)}</div>
<div>Fallback used</div><div>{esc(display_bool(current.get('fallback_used')))}</div>
<div>Drift score</div><div>{esc(display_value(current.get('drift_score')))}</div>
<div>Instability index</div><div>{esc(display_value(current.get('instability_index')))}</div>
</div></div>
<div class=\"card\"><h2>V2 Metric Integrity</h2><div class=\"kv\">
<div>Metrics redefined</div><div>false</div>
<div>V2 authoritative</div><div>true</div>
<div>v2_metrics_overridden</div><div>{esc(display_bool(current.get('v2_metrics_overridden')))}</div>
</div></div>
</section>
<section class=\"card warn\">
<h2>Expected Property Check</h2>
<div class=\"kv\">
<div>expected_stability_property</div><div>{esc(result.get('expected_stability_property') or 'not_available')}</div>
<div>passed</div><div>{esc(expected.get('passed', 'unknown'))}</div>
<div>confidence</div><div>{esc(expected.get('confidence', 'low'))}</div>
<div>notes</div><div>{esc(expected.get('notes', 'not_available'))}</div>
</div>
<p>{esc('; '.join(expected.get('evidence', [])))}</p>
</section>
<section class=\"card\">
<h2>Diagnosis Summary</h2>
<div class=\"kv\">
<div>primary_issue</div><div>{esc(diagnosis_summary.get('primary_issue', 'not_available'))}</div>
<div>severity</div><div>{esc(diagnosis_summary.get('severity', 'not_available'))}</div>
<div>confidence</div><div>{esc(diagnosis_summary.get('confidence', 'not_available'))}</div>
<div>is_actionable</div><div>{esc(display_bool(diagnosis_summary.get('is_actionable')))}</div>
</div>
<p>{esc(diagnosis_summary.get('short_explanation', 'not_available'))}</p>
</section>
<section class=\"grid\">
{diagnosis_cards(result.get('diagnoses', []))}
</section>
<section class=\"card\">
<h2>Actionable Recommendations</h2>
{recommendation_list(result.get('recommendation_evidence', []))}
</section>
<section class=\"card\">
<h2>Recommendation</h2>
<p>{esc(rec)}</p>
</section>
<section class=\"card warn\">
<h2>Caveats</h2>
<ul>
<li>High drift does not automatically mean provider failure.</li>
<li>n=1 cannot establish general stochastic stability.</li>
<li>Critical due to expected_property_violation is stronger than Critical due to mock_real_divergence alone.</li>
<li>Expected property checker is heuristic and should be reviewed by a human.</li>
</ul>
</section>
<section class=\"card\">
<h2>Configuration</h2>
<p><strong>Models:</strong> {models}</p>
<p><strong>Trials:</strong> {result['trial_count']}</p>
</section>
<section class=\"card\">
<h2>Reproduction Command</h2>
<pre>{command}</pre>
</section>
</main>
</body>
</html>
"""


def esc(value: object) -> str:
    return html.escape(str(value))


def card(label: str, value: object) -> str:
    return f"<div class=\"card\"><div class=\"label\">{esc(label)}</div><div class=\"value\">{esc(value)}</div></div>"


def diagnosis_cards(diagnoses):
    if not diagnoses:
        return "<div class=\"card\">No diagnosis available.</div>"
    cards = []
    for diagnosis in diagnoses:
        cards.append(
            "<div class=\"card diag\">"
            f"<h2>{esc(diagnosis.get('type', 'unknown'))}</h2>"
            f"<p><span class=\"pill\">{esc(diagnosis.get('severity', 'not_available'))}</span>"
            f"<span class=\"pill\">confidence: {esc(diagnosis.get('confidence', 'not_available'))}</span></p>"
            f"<p>{esc(diagnosis.get('interpretation', 'not_available'))}</p>"
            "</div>"
        )
    return "".join(cards)


def recommendation_list(recommendations):
    if not recommendations:
        return "<p>No actionable recommendation available.</p>"
    items = []
    for rec in recommendations:
        items.append(
            "<li>"
            f"<strong>{esc(rec.get('priority', 'P2'))}</strong> "
            f"{esc(rec.get('action', 'not_available'))}<br>"
            f"<span class=\"label\">{esc(rec.get('affected_layer', 'not_available'))}; confidence={esc(rec.get('confidence', 'not_available'))}</span>"
            "</li>"
        )
    return "<ul>" + "".join(items) + "</ul>"
