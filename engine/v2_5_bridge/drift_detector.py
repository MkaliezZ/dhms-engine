"""Drift analysis for DHMS V2.5 real API bridge."""

from typing import Any, Mapping


REGIME_NAMES = ("DHMS-A", "DHMS-B", "DHMS-C")


def text_divergence(left: str, right: str) -> float:
    if left == right:
        return 0.0
    left_tokens = set(str(left).split())
    right_tokens = set(str(right).split())
    if not left_tokens and not right_tokens:
        return 0.0
    union = left_tokens.union(right_tokens)
    intersection = left_tokens.intersection(right_tokens)
    token_distance = 1.0 - (len(intersection) / len(union)) if union else 0.0
    length_distance = abs(len(str(left)) - len(str(right))) / max(len(str(left)), len(str(right)), 1)
    return round((token_distance + length_distance) / 2.0, 6)


def analyze_drift(v2_results: Mapping[str, Any], real_api_results: Mapping[str, Any]) -> dict[str, Any]:
    mock_runs = _reference_runs(v2_results)
    mock_vs_real = {}
    all_model_scores = {}
    for model_name, model_result in real_api_results.items():
        scores = _model_drift_scores(mock_runs, model_result["per_run_results"])
        mock_vs_real[model_name] = scores
        all_model_scores[model_name] = scores["drift_score"]

    cross_api_variance = _variance(list(all_model_scores.values()))
    regime_instability = _regime_instability(real_api_results)
    drift_score = _mean(list(all_model_scores.values()))
    instability_index = _mean(list(regime_instability.values())) if regime_instability else 0.0
    return {
        "drift_score": round(drift_score, 6),
        "instability_index": round(instability_index, 6),
        "mock_vs_real_divergence": mock_vs_real,
        "cross_api_variance": round(cross_api_variance, 6),
        "regime_level_instability": regime_instability,
    }


def _reference_runs(v2_results: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    per_model = v2_results.get("per_model_results", {})
    if "mock" in per_model:
        return per_model["mock"]["per_run_results"]
    return v2_results.get("per_run_results", [])


def _model_drift_scores(reference_runs: list[Mapping[str, Any]], real_runs: list[Mapping[str, Any]]) -> dict[str, Any]:
    scores = []
    by_regime = {name: [] for name in REGIME_NAMES}
    for index, real_run in enumerate(real_runs):
        if not reference_runs:
            continue
        reference = reference_runs[min(index, len(reference_runs) - 1)]
        for regime in REGIME_NAMES:
            score = text_divergence(
                reference["regime_results"][regime]["response"],
                real_run["regime_results"][regime]["response"],
            )
            scores.append(score)
            by_regime[regime].append(score)
    return {
        "drift_score": round(_mean(scores), 6),
        "by_regime": {regime: round(_mean(values), 6) for regime, values in by_regime.items()},
    }


def _regime_instability(real_api_results: Mapping[str, Any]) -> dict[str, float]:
    output = {}
    for regime in REGIME_NAMES:
        responses = []
        for model_result in real_api_results.values():
            for run_result in model_result["per_run_results"]:
                responses.append(run_result["regime_results"][regime]["response"])
        output[regime] = round(_uniqueness_instability(responses), 6)
    return output


def _uniqueness_instability(values: list[str]) -> float:
    if len(values) < 2:
        return 0.0
    return (len(set(values)) - 1) / (len(values) - 1)


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _variance(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    avg = _mean(values)
    return sum((value - avg) ** 2 for value in values) / len(values)

