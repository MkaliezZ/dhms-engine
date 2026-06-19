"""Deterministic statistical helpers for DHMS v1 measurement."""

from typing import Any, Mapping, Sequence


REGIME_NAMES = ("DHMS-A", "DHMS-B", "DHMS-C")


def mean(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def variance(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    return sum((value - avg) ** 2 for value in values) / len(values)


def text_divergence(left: str, right: str) -> float:
    if left == right:
        return 0.0
    left_tokens = set(left.split())
    right_tokens = set(right.split())
    if not left_tokens and not right_tokens:
        return 0.0
    union = left_tokens.union(right_tokens)
    intersection = left_tokens.intersection(right_tokens)
    token_distance = 1.0 - (len(intersection) / len(union)) if union else 0.0
    length_distance = abs(len(left) - len(right)) / max(len(left), len(right), 1)
    return round((token_distance + length_distance) / 2.0, 6)


def compute_regime_divergence_scores(run_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    pair_values = {"A_vs_B": [], "A_vs_C": [], "B_vs_C": []}
    for result in run_results:
        regimes = result["regime_results"]
        a = regimes["DHMS-A"]["response"]
        b = regimes["DHMS-B"]["response"]
        c = regimes["DHMS-C"]["response"]
        pair_values["A_vs_B"].append(text_divergence(a, b))
        pair_values["A_vs_C"].append(text_divergence(a, c))
        pair_values["B_vs_C"].append(text_divergence(b, c))

    return {
        pair: {
            "mean": round(mean(values), 6),
            "variance": round(variance(values), 6),
            "values": [round(value, 6) for value in values],
        }
        for pair, values in pair_values.items()
    }


def compute_stability_distributions(run_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    distributions = {}
    for regime_name in REGIME_NAMES:
        responses = [result["regime_results"][regime_name]["response"] for result in run_results]
        unique_count = len(set(responses))
        repeat_count = len(responses)
        stability = 1.0 if repeat_count == 0 else 1.0 - ((unique_count - 1) / max(repeat_count - 1, 1))
        distributions[regime_name] = {
            "runs": repeat_count,
            "unique_responses": unique_count,
            "stability": round(stability, 6),
        }
    return distributions


def compute_sensitivity_variance(run_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    values = []
    for result in run_results:
        regimes = result["regime_results"]
        values.append(text_divergence(regimes["DHMS-A"]["response"], regimes["DHMS-B"]["response"]))
    return {
        "mean": round(mean(values), 6),
        "variance": round(variance(values), 6),
        "values": [round(value, 6) for value in values],
    }

