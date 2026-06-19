"""Suite HTML report."""
import html
from pathlib import Path
from typing import Any, Mapping
from display_format import display_value

def write_suite_html(report: Mapping[str, Any], output_dir: Path) -> str:
    path = output_dir / "suite_report.html"
    s = report["summary"]
    d = s.get("diagnosis_summary", {})
    cards = "".join(card(k, display_value(v)) for k, v in s["average_scores"].items())
    worst = "".join(f"<li>{html.escape(i['case_id'])}: {html.escape(i['risk_label'])} drift={html.escape(str(display_value(i['drift_risk'])))}</li>" for i in s["worst_5_cases"])
    actionable = "".join(
        f"<li><strong>{html.escape(str(i['case_id']))}</strong>: {html.escape(str(i['primary_issue']))} "
        f"({html.escape(str(i['severity']))}, {html.escape(str(i['confidence']))})<br>{html.escape(str(i['top_recommendation']))}</li>"
        for i in s.get("top_actionable_cases", [])
    )
    high_passed = "".join(f"<li>{html.escape(i['case_id'])}: {html.escape(i['risk_label'])} drift={html.escape(str(display_value(i['drift_risk'])))}</li>" for i in s.get("high_drift_expected_property_passed_cases", []))
    failed = "".join(f"<li>{html.escape(i['case_id'])}: {html.escape(i['risk_label'])} drift={html.escape(str(display_value(i['drift_risk'])))}</li>" for i in s.get("expected_property_failed_cases", []))
    doc = f"""<!doctype html><html><head><meta charset='utf-8'><title>DHMS Suite Report</title><style>body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f6f7f9;color:#1d2433;margin:0}}main{{max-width:1080px;margin:0 auto;padding:32px 20px}}.card{{background:white;border:1px solid #dde2ea;border-radius:8px;padding:18px;margin:12px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px}}.value{{font-size:24px;font-weight:700}}pre{{white-space:pre-wrap;background:#101827;color:#edf2ff;padding:14px;border-radius:8px}}.warn{{background:#fff8e6;border-color:#ead39b}}</style></head><body><main><h1>DHMS Suite Report</h1><div class='card'><h2>Executive Summary</h2><strong>Suite:</strong> {html.escape(s['suite_name'])}<br><strong>Total cases:</strong> {s['total_cases']}<br><strong>Models:</strong> {html.escape(', '.join(s['models_tested']))}<br><strong>Trials:</strong> {s['trial_count']}<br><strong>Real API used cases:</strong> {s.get('real_api_used_cases', 0)}<p>{html.escape(s['recommendation'])}</p></div><section class='grid'>{cards}</section><div class='card'><h2>Risk Distribution</h2><pre>{html.escape(str(s['risk_label_distribution']))}</pre></div><div class='card'><h2>Diagnosis Distribution</h2><pre>{html.escape(str(s.get('diagnosis_distribution', {})))}</pre></div><div class='card'><h2>Expected Property Check Summary</h2><ul><li>passed: {d.get('cases_with_expected_property_passed', 0)}</li><li>failed: {d.get('cases_with_expected_property_failed', 0)}</li><li>unknown: {d.get('cases_with_expected_property_unknown', 0)}</li><li>high mock-real divergence: {d.get('cases_with_high_mock_real_divergence', 0)}</li><li>regime behavior drift: {d.get('cases_with_regime_behavior_drift', 0)}</li><li>style or format drift: {d.get('cases_with_style_or_format_drift', 0)}</li><li>actionable recommendations: {d.get('cases_with_actionable_recommendations', 0)}</li><li>blocked by metric integrity: {d.get('cases_blocked_by_metric_integrity', 0)}</li></ul></div><div class='card'><h2>Top Actionable Cases</h2><ul>{actionable or '<li>None</li>'}</ul></div><div class='card'><h2>Worst Drift Cases</h2><ul>{worst}</ul></div><div class='card'><h2>High Drift But Expected Property Passed</h2><ul>{high_passed or '<li>None</li>'}</ul></div><div class='card'><h2>Expected Property Failed</h2><ul>{failed or '<li>None</li>'}</ul></div><div class='card warn'><h2>Caveats</h2><ul><li>High drift does not automatically mean provider failure.</li><li>n=1 cannot establish general stochastic stability.</li><li>Critical due to expected_property_violation is stronger than Critical due to mock_real_divergence alone.</li><li>Expected property checker is heuristic and should be reviewed by a human.</li></ul></div><div class='card'><h2>Metric Integrity</h2><p>v2_metrics_overridden: {html.escape(str(s['v2_metrics_overridden']).lower())}</p></div></main></body></html>"""
    path.write_text(doc, encoding="utf-8")
    return str(path)

def card(label, value):
    return f"<div class='card'><div>{html.escape(str(label))}</div><div class='value'>{html.escape(str(value))}</div></div>"
