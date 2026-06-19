"""Suite aggregation for DHMS Product Layer."""

from collections import Counter
from typing import Any, Mapping, Sequence


def average(values):
    vals = [float(v) for v in values if isinstance(v, (int, float))]
    return round(sum(vals) / len(vals), 6) if vals else 0.0


def summarize_suite(suite_name: str, case_results: Sequence[Mapping[str, Any]], models: str, n: int) -> dict[str, Any]:
    risks = Counter(item["risk_label"] for item in case_results)
    sorted_worst = sorted(case_results, key=lambda item: risk_rank(item["risk_label"]), reverse=True)
    sorted_best = sorted(case_results, key=lambda item: (risk_rank(item["risk_label"]), -item["stability_score"]))
    overridden = any(item.get("calibration", {}).get("current_run", {}).get("v2_metrics_overridden") for item in case_results)
    real_api_used = sum(1 for item in case_results if item.get("calibration", {}).get("current_run", {}).get("real_api_used"))
    skipped = skipped_provider_summary(case_results)
    avg = {
        "stability_score": average([item["stability_score"] for item in case_results]),
        "sensitivity_score": average([item["sensitivity_score"] for item in case_results]),
        "isolation_strength_score": average([item["isolation_strength_score"] for item in case_results]),
        "drift_risk": average([item["drift_risk"] for item in case_results]),
    }
    diagnosis_distribution = count_diagnoses(case_results)
    diagnosis_summary = build_diagnosis_summary(case_results, diagnosis_distribution)
    return {
        "suite_name": suite_name,
        "total_cases": len(case_results),
        "models_tested": [item.strip() for item in models.split(",") if item.strip()],
        "trial_count": n,
        "real_api_used_cases": real_api_used,
        "skipped_provider_summary": skipped,
        "average_scores": avg,
        "risk_label_distribution": dict(risks),
        "worst_5_cases": case_refs(sorted_worst[:5]),
        "critical_cases": case_refs([item for item in case_results if item["risk_label"] == "Critical"]),
        "best_cases": case_refs(sorted_best[:5]),
        "recommendation": recommendation(risks),
        "v2_metrics_overridden": bool(overridden),
        "diagnosis_summary": diagnosis_summary,
        "diagnosis_distribution": diagnosis_distribution,
        "top_actionable_cases": top_actionable_cases(case_results),
        "high_drift_expected_property_passed_cases": case_refs([
            item for item in case_results
            if item.get("drift_risk", 0) >= 0.75 and item.get("expected_property_check", {}).get("passed") is True
        ]),
        "expected_property_failed_cases": case_refs([
            item for item in case_results
            if item.get("expected_property_check", {}).get("passed") is False
        ]),
    }


def risk_rank(label):
    return {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}.get(label, 0)


def case_refs(items):
    return [{"case_id": item["case_id"], "risk_label": item["risk_label"], "stability_score": item["stability_score"], "drift_risk": item["drift_risk"]} for item in items]


def skipped_provider_summary(case_results):
    counts = Counter()
    for item in case_results:
        for status in item.get("calibration", {}).get("current_run", {}).get("provider_statuses", []):
            if status.get("failure_mode") in {"api_key_missing", "model_not_found_or_not_available"}:
                counts[status.get("provider", "unknown")] += 1
    return dict(counts)


def recommendation(risks):
    if risks.get("Critical"):
        return "Investigate critical cases before using memory/context paths in production."
    if risks.get("High"):
        return "Review high-risk cases and rerun with representative real providers."
    if risks.get("Medium"):
        return "Suite shows measurable perturbation sensitivity; review context boundaries."
    return "Suite appears stable in this run; continue monitoring with real provider coverage."


def count_diagnoses(case_results):
    counts = Counter()
    for item in case_results:
        for diagnosis in item.get("diagnoses", []):
            counts[diagnosis.get("type", "unknown")] += 1
    return dict(counts)


def build_diagnosis_summary(case_results, distribution):
    expected = Counter(str(item.get("expected_property_check", {}).get("passed", "unknown")) for item in case_results)
    return {
        "total_cases": len(case_results),
        "cases_with_expected_property_passed": expected.get("True", 0),
        "cases_with_expected_property_failed": expected.get("False", 0),
        "cases_with_expected_property_unknown": expected.get("unknown", 0),
        "cases_with_high_mock_real_divergence": distribution.get("mock_real_divergence", 0),
        "cases_with_regime_behavior_drift": distribution.get("regime_behavior_drift", 0),
        "cases_with_style_or_format_drift": distribution.get("style_or_format_drift", 0),
        "cases_with_actionable_recommendations": sum(1 for item in case_results if item.get("recommendation_evidence")),
        "cases_blocked_by_metric_integrity": distribution.get("metric_integrity_issue", 0),
    }


def top_actionable_cases(case_results):
    def key(item):
        summary = item.get("diagnosis_summary", {})
        return (risk_rank(summary.get("severity")), item.get("drift_risk", 0))

    rows = []
    for item in sorted(case_results, key=key, reverse=True):
        recommendations = item.get("recommendation_evidence", [])
        if not recommendations:
            continue
        summary = item.get("diagnosis_summary", {})
        rows.append({
            "case_id": item.get("case_id"),
            "primary_issue": summary.get("primary_issue"),
            "severity": summary.get("severity"),
            "confidence": summary.get("confidence"),
            "top_recommendation": recommendations[0].get("action"),
        })
        if len(rows) >= 8:
            break
    return rows
