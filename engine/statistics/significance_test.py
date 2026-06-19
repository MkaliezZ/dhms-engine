"""Classical deterministic significance helpers for DHMS v2."""

from math import erf, sqrt
from typing import Sequence


def mean(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def variance(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    return sum((value - avg) ** 2 for value in values) / (len(values) - 1)


def difference_of_means_test(left: Sequence[float], right: Sequence[float]) -> dict[str, float]:
    left_mean = mean(left)
    right_mean = mean(right)
    left_var = variance(left)
    right_var = variance(right)
    denom = sqrt((left_var / max(len(left), 1)) + (right_var / max(len(right), 1)))
    t_score = 0.0 if denom == 0 else (left_mean - right_mean) / denom
    p_approx = 2.0 * (1.0 - _normal_cdf(abs(t_score)))
    return {
        "left_mean": round(left_mean, 6),
        "right_mean": round(right_mean, 6),
        "difference": round(left_mean - right_mean, 6),
        "t_score_approx": round(t_score, 6),
        "p_value_approx": round(max(0.0, min(1.0, p_approx)), 6),
    }


def effect_size(left: Sequence[float], right: Sequence[float]) -> float:
    left_var = variance(left)
    right_var = variance(right)
    pooled = sqrt((left_var + right_var) / 2.0)
    if pooled == 0:
        return 0.0
    return round((mean(left) - mean(right)) / pooled, 6)


def variance_ratio(left: Sequence[float], right: Sequence[float]) -> float:
    left_var = variance(left)
    right_var = variance(right)
    if right_var == 0:
        return 0.0 if left_var == 0 else float("inf")
    return round(left_var / right_var, 6)


def _normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + erf(value / sqrt(2.0)))

