"""Product-friendly summaries derived from DHMS metrics.

This module does not redefine DHMS metrics. It derives developer-facing labels
from existing DHMS outputs.
"""

from typing import Any, Mapping


NOT_APPLICABLE_MOCK_ONLY = "not_applicable_mock_only"


def clamp_score(value: Any) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0
    return round(max(0.0, min(1.0, score)), 6)


def summarize_product_result(dhms_result: Mapping[str, Any], input_text: str, models: str, n: int) -> dict[str, Any]:
    metrics = extract_authoritative_metrics(dhms_result)
    stability = clamp_score(metrics.get("stability", 0.0))
    sensitivity = clamp_score(metrics.get("sensitivity", 0.0))
    isolation = clamp_score(metrics.get("isolation_strength", 0.0))
    calibration = build_calibration(dhms_result)
    drift_risk = derive_drift_risk(dhms_result, sensitivity, isolation, calibration)
    risk_label = risk_label_from_scores(stability, sensitivity, isolation, drift_risk)
    recommendation = recommendation_for(risk_label)
    return {
        "input_summary": summarize_input(input_text),
        "models": [item.strip() for item in models.split(",") if item.strip()],
        "trial_count": n,
        "stability_score": stability,
        "sensitivity_score": sensitivity,
        "isolation_strength_score": isolation,
        "drift_risk": drift_risk,
        "risk_label": risk_label,
        "recommendation": recommendation,
        "summary_zh": chinese_summary(risk_label, stability, sensitivity, isolation),
        "calibration": calibration,
    }


def extract_authoritative_metrics(dhms_result: Mapping[str, Any]) -> Mapping[str, Any]:
    v2 = dhms_result.get("v2_results")
    if isinstance(v2, Mapping):
        return v2.get("metric_results") or v2.get("aggregated_metrics", {})
    return dhms_result.get("metric_results") or dhms_result.get("aggregated_metrics", {})


def build_calibration(dhms_result: Mapping[str, Any]) -> dict[str, Any]:
    baseline = dhms_result.get("real_api_validation_baseline") or {}
    real_api_results = dhms_result.get("real_api_results") or {}
    real_api_models = sorted(real_api_results.keys())
    provider_statuses = [item.get("provider_status", {}) for item in real_api_results.values()]
    fallback_used = any(status.get("fallback_used") for status in provider_statuses) or any(model_result_uses_fallback(item) for item in real_api_results.values())
    current_real_api_used = any(status.get("real_api_used") for status in provider_statuses)
    comparison = dhms_result.get("cross_model_real_world_comparison") or {}
    drift = dhms_result.get("drift_analysis") or {}
    if current_real_api_used:
        drift_score = comparison.get("drift_score", drift.get("drift_score"))
        instability_index = comparison.get("instability_index", drift.get("instability_index"))
    else:
        drift_score = NOT_APPLICABLE_MOCK_ONLY
        instability_index = NOT_APPLICABLE_MOCK_ONLY
    return {
        "deepseek_smoke_baseline": {
            "status": baseline.get("status"),
            "real_api_used": baseline.get("real_api_used"),
            "fallback_used": baseline.get("fallback_used"),
            "total_real_api_calls": baseline.get("total_real_api_calls"),
            "v2_metrics_overridden": baseline.get("v2_metrics_overridden"),
        },
        "current_run": {
            "real_api_used": current_real_api_used,
            "real_api_models": real_api_models,
            "provider_statuses": provider_statuses,
            "fallback_used": fallback_used,
            "drift_score": drift_score,
            "instability_index": instability_index,
            "v2_metrics_overridden": current_v2_metrics_overridden(dhms_result),
        },
    }


def model_result_uses_fallback(model_result: Mapping[str, Any]) -> bool:
    markers = ("fallback_response", "fallback_mock_response", "deepseek_fallback_response", "external_fallback_response")
    for run_result in model_result.get("per_run_results", []):
        for regime_result in run_result.get("regime_results", {}).values():
            response = str(regime_result.get("raw_response") or regime_result.get("response", ""))
            if any(marker in response for marker in markers):
                return True
    return False


def current_v2_metrics_overridden(dhms_result: Mapping[str, Any]) -> bool:
    comparison = dhms_result.get("cross_model_real_world_comparison") or {}
    schema = comparison.get("schema_compatibility") or {}
    value = schema.get("v2_metrics_overridden")
    return bool(value) if value is not None else False


def derive_drift_risk(dhms_result: Mapping[str, Any], sensitivity: float, isolation: float, calibration: Mapping[str, Any]) -> float:
    current = calibration.get("current_run", {})
    drift_score = current.get("drift_score")
    if isinstance(drift_score, (int, float)):
        return clamp_score(drift_score)
    return clamp_score((sensitivity * 0.7) + ((1.0 - isolation) * 0.3))


def risk_label_from_scores(stability: float, sensitivity: float, isolation: float, drift: float) -> str:
    if stability < 0.35 or drift >= 0.85 or (sensitivity >= 0.85 and isolation < 0.45):
        return "Critical"
    if stability < 0.6 or drift >= 0.65 or sensitivity >= 0.7:
        return "High"
    if stability < 0.8 or drift >= 0.35 or sensitivity >= 0.35:
        return "Medium"
    return "Low"


def recommendation_for(label: str) -> str:
    if label == "Low":
        return "Observed behavior suggests low memory/context stability risk in this run. Continue monitoring with representative prompts before production rollout."
    if label == "Medium":
        return "The model shows measurable sensitivity to memory/context perturbation. Review memory injection and retrieval boundaries before production use."
    if label == "High":
        return "Observed behavior indicates elevated instability under perturbation. Add guardrails, inspect context assembly, and rerun DHMS before production use."
    return "High drift requires diagnosis before production use. Investigate perturbation boundaries, expected-property evidence, and mock-real divergence before relying on this memory/context path."


def chinese_summary(label: str, stability: float, sensitivity: float, isolation: float) -> str:
    return f"风险等级：{label}；稳定性={stability}，敏感性={sensitivity}，隔离强度={isolation}。该结论仅表示本次受控扰动下的行为稳定性，不证明内部记忆因果机制。"


def summarize_input(input_text: str) -> dict[str, Any]:
    text = input_text.strip()
    return {
        "characters": len(text),
        "words": len(text.split()),
        "preview": text[:180],
    }
