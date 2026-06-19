"""Suite Markdown report."""
from pathlib import Path
from typing import Any, Mapping
from display_format import display_value

def write_suite_markdown(report: Mapping[str, Any], output_dir: Path) -> str:
    path = output_dir / "suite_report.md"
    s = report["summary"]
    d = s.get("diagnosis_summary", {})
    lines = [
        "# DHMS Suite Report",
        "",
        "## Executive Summary",
        "",
        f"* Suite: {s['suite_name']}",
        f"* Total cases: {s['total_cases']}",
        f"* Models: {', '.join(s['models_tested'])}",
        f"* Trials: {s['trial_count']}",
        f"* Real API used cases: {s.get('real_api_used_cases', 0)}",
        f"* Recommendation: {s['recommendation']}",
        "",
        "High drift does not automatically mean provider failure. Critical due to expected_property_violation is stronger evidence than Critical due to mock_real_divergence alone.",
        "",
        "## Average Scores",
        "",
    ]
    for key, value in s["average_scores"].items():
        lines.append(f"* {key}: {display_value(value)}")
    lines += ["", "## Risk Distribution", ""]
    for key, value in s["risk_label_distribution"].items():
        lines.append(f"* {key}: {value}")
    lines += ["", "## Diagnosis Distribution", ""]
    for key, value in sorted(s.get("diagnosis_distribution", {}).items()):
        lines.append(f"* {key}: {value}")
    lines += [
        "",
        "## Expected Property Check Summary",
        "",
        f"* passed: {d.get('cases_with_expected_property_passed', 0)}",
        f"* failed: {d.get('cases_with_expected_property_failed', 0)}",
        f"* unknown: {d.get('cases_with_expected_property_unknown', 0)}",
        f"* high_mock_real_divergence: {d.get('cases_with_high_mock_real_divergence', 0)}",
        f"* regime_behavior_drift: {d.get('cases_with_regime_behavior_drift', 0)}",
        f"* style_or_format_drift: {d.get('cases_with_style_or_format_drift', 0)}",
        f"* actionable_recommendations: {d.get('cases_with_actionable_recommendations', 0)}",
        f"* blocked_by_metric_integrity: {d.get('cases_blocked_by_metric_integrity', 0)}",
        "",
        "## Top Actionable Cases",
        "",
    ]
    for item in s.get("top_actionable_cases", []):
        lines.append(f"* {item['case_id']} - {item['primary_issue']} ({item['severity']}, {item['confidence']}): {item['top_recommendation']}")
    lines += ["", "## Worst Drift Cases", ""]
    for item in s["worst_5_cases"]:
        lines.append(f"* {item['case_id']} - {item['risk_label']} drift={display_value(item['drift_risk'])}")
    lines += ["", "## Cases Where High Drift But Expected Property Passed", ""]
    for item in s.get("high_drift_expected_property_passed_cases", []):
        lines.append(f"* {item['case_id']} - {item['risk_label']} drift={display_value(item['drift_risk'])}")
    lines += ["", "## Cases Where Expected Property Failed", ""]
    for item in s.get("expected_property_failed_cases", []):
        lines.append(f"* {item['case_id']} - {item['risk_label']} drift={display_value(item['drift_risk'])}")
    lines += [
        "",
        "## Recommendations",
        "",
        s["recommendation"],
        "",
        "## Caveats",
        "",
        "* High drift does not automatically mean provider failure.",
        "* n=1 cannot establish general stochastic stability.",
        "* Critical due to expected_property_violation is stronger than Critical due to mock_real_divergence alone.",
        "* Expected property checker is heuristic and should be reviewed by a human.",
        "",
        f"v2_metrics_overridden: {str(s['v2_metrics_overridden']).lower()}",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)
