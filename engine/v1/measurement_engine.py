"""DHMS v1 measurement aggregation."""

from typing import Any, Mapping, Sequence

from statistical_analyzer import (
    compute_regime_divergence_scores,
    compute_sensitivity_variance,
    compute_stability_distributions,
    mean,
)


METRIC_NAMES = ("stability", "sensitivity", "specificity", "isolation_strength")


def build_measurement(run_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if not run_results:
        raise ValueError("measurement requires at least one run result")

    metric_series = {
        name: [float(result["metric_results"][name]) for result in run_results]
        for name in METRIC_NAMES
    }
    stability_distribution = compute_stability_distributions(run_results)
    sensitivity_variance = compute_sensitivity_variance(run_results)
    regime_divergence = compute_regime_divergence_scores(run_results)

    aggregated_metrics = {
        "stability": round(mean([item["stability"] for item in stability_distribution.values()]), 6),
        "sensitivity": round(sensitivity_variance["mean"], 6),
        "specificity": round(mean(metric_series["specificity"]), 6),
        "isolation_strength": round(mean(metric_series["isolation_strength"]), 6),
    }

    return {
        "aggregated_metrics": aggregated_metrics,
        "metric_distributions": {
            "stability": stability_distribution,
            "sensitivity": sensitivity_variance,
            "specificity": {
                "mean": aggregated_metrics["specificity"],
                "values": [round(value, 6) for value in metric_series["specificity"]],
            },
            "isolation_strength": {
                "mean": aggregated_metrics["isolation_strength"],
                "values": [round(value, 6) for value in metric_series["isolation_strength"]],
            },
        },
        "regime_comparison": {
            "divergence_scores": regime_divergence,
            "input_identity_preserved": all(
                result["perturbation_summary"]["input_preserved"] for result in run_results
            ),
            "comparison_count": len(run_results),
        },
    }

