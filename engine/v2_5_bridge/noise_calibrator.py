"""Noise calibration for DHMS V2.5 bridge outputs."""

import math
from typing import Any, Mapping


REGIME_NAMES = ("DHMS-A", "DHMS-B", "DHMS-C")


def estimate_noise(real_api_results: Mapping[str, Any]) -> dict[str, Any]:
    per_model = {}
    for model_name, model_result in real_api_results.items():
        per_model[model_name] = _estimate_model_noise(model_result["per_run_results"])
    return {
        "per_model_noise": per_model,
        "overall_stochastic_variance": round(_mean([item["stochastic_variance"] for item in per_model.values()]), 6),
        "overall_entropy_approximation": round(_mean([item["response_entropy_approximation"] for item in per_model.values()]), 6),
        "overall_regime_sensitivity_amplification": round(_mean([item["regime_sensitivity_amplification_factor"] for item in per_model.values()]), 6),
    }


def _estimate_model_noise(run_results: list[Mapping[str, Any]]) -> dict[str, Any]:
    regime_instability = {}
    regime_entropy = {}
    for regime in REGIME_NAMES:
        responses = [result["regime_results"][regime]["response"] for result in run_results]
        regime_instability[regime] = _variance_from_uniqueness(responses)
        regime_entropy[regime] = _entropy_approximation(responses)
    sensitivity_values = [float(result["metric_results"]["sensitivity"]) for result in run_results]
    isolation_values = [float(result["metric_results"]["isolation_strength"]) for result in run_results]
    amplification = _mean(sensitivity_values) / max(_mean(isolation_values), 1e-9)
    return {
        "stochastic_variance": round(_mean(list(regime_instability.values())), 6),
        "response_entropy_approximation": round(_mean(list(regime_entropy.values())), 6),
        "regime_sensitivity_amplification_factor": round(amplification, 6),
        "regime_instability": {key: round(value, 6) for key, value in regime_instability.items()},
        "regime_entropy": {key: round(value, 6) for key, value in regime_entropy.items()},
    }


def _variance_from_uniqueness(values: list[str]) -> float:
    if len(values) < 2:
        return 0.0
    return (len(set(values)) - 1) / (len(values) - 1)


def _entropy_approximation(values: list[str]) -> float:
    if not values:
        return 0.0
    total = len(values)
    counts = {value: values.count(value) for value in set(values)}
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log(p, 2)
    normalizer = math.log(max(total, 2), 2)
    return entropy / normalizer if normalizer else 0.0


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)

