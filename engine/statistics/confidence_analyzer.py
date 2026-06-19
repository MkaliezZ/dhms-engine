"""Confidence overlays for DHMS v2 cross-model measurements."""

from math import sqrt
from typing import Mapping, Sequence

from significance_test import mean, variance


def confidence_interval(values: Sequence[float], z_value: float = 1.96) -> dict[str, float]:
    avg = mean(values)
    if len(values) < 2:
        return {"mean": round(avg, 6), "lower": round(avg, 6), "upper": round(avg, 6)}
    margin = z_value * sqrt(variance(values) / len(values))
    return {"mean": round(avg, 6), "lower": round(avg - margin, 6), "upper": round(avg + margin, 6)}


def stability_confidence(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return round(max(0.0, 1.0 - variance(values)), 6)


def cross_model_agreement_score(model_metric_means: Mapping[str, Mapping[str, float]]) -> float:
    if len(model_metric_means) < 2:
        return 1.0
    metric_names = sorted(next(iter(model_metric_means.values())).keys())
    spreads = []
    for metric in metric_names:
        values = [metrics[metric] for metrics in model_metric_means.values()]
        spreads.append(max(values) - min(values))
    return round(max(0.0, 1.0 - mean(spreads)), 6)

