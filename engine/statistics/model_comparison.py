"""Cross-model comparison utilities for DHMS v2."""

from typing import Any, Mapping

from confidence_analyzer import confidence_interval, cross_model_agreement_score, stability_confidence
from significance_test import difference_of_means_test, effect_size, variance_ratio


METRIC_NAMES = ("stability", "sensitivity", "specificity", "isolation_strength")


def compare_models(per_model_results: Mapping[str, Any]) -> dict[str, Any]:
    metric_series = _metric_series(per_model_results)
    model_metric_means = {
        model: {metric: round(sum(values) / len(values), 6) for metric, values in metrics.items()}
        for model, metrics in metric_series.items()
    }
    return {
        "per_model_metric_means": model_metric_means,
        "cross_model_variance": _cross_model_variance(model_metric_means),
        "pairwise_metric_tests": _pairwise_tests(metric_series),
        "confidence_scores": {
            "cross_model_agreement": cross_model_agreement_score(model_metric_means),
            "stability_confidence_by_model": {
                model: stability_confidence(metrics["stability"])
                for model, metrics in metric_series.items()
            },
            "confidence_intervals": {
                model: {metric: confidence_interval(values) for metric, values in metrics.items()}
                for model, metrics in metric_series.items()
            },
        },
        "regime_divergence_by_model": _regime_divergence_by_model(per_model_results),
    }


def _metric_series(per_model_results: Mapping[str, Any]) -> dict[str, dict[str, list[float]]]:
    series = {}
    for model, model_result in per_model_results.items():
        series[model] = {metric: [] for metric in METRIC_NAMES}
        for run_result in model_result["per_run_results"]:
            for metric in METRIC_NAMES:
                series[model][metric].append(float(run_result["metric_results"][metric]))
    return series


def _cross_model_variance(model_metric_means: Mapping[str, Mapping[str, float]]) -> dict[str, float]:
    output = {}
    for metric in METRIC_NAMES:
        values = [metrics[metric] for metrics in model_metric_means.values()]
        if len(values) < 2:
            output[metric] = 0.0
        else:
            avg = sum(values) / len(values)
            output[metric] = round(sum((value - avg) ** 2 for value in values) / len(values), 6)
    return output


def _pairwise_tests(metric_series: Mapping[str, Mapping[str, list[float]]]) -> dict[str, Any]:
    models = list(metric_series.keys())
    tests = {}
    for left_index, left in enumerate(models):
        for right in models[left_index + 1:]:
            key = f"{left}_vs_{right}"
            tests[key] = {}
            for metric in METRIC_NAMES:
                left_values = metric_series[left][metric]
                right_values = metric_series[right][metric]
                tests[key][metric] = {
                    "difference_of_means": difference_of_means_test(left_values, right_values),
                    "effect_size": effect_size(left_values, right_values),
                    "variance_ratio": variance_ratio(left_values, right_values),
                }
    return tests


def _regime_divergence_by_model(per_model_results: Mapping[str, Any]) -> dict[str, Any]:
    output = {}
    for model, model_result in per_model_results.items():
        divergences = []
        for run_result in model_result["per_run_results"]:
            metrics = run_result["metric_results"]
            divergences.append({
                "sensitivity": metrics["sensitivity"],
                "isolation_strength": metrics["isolation_strength"],
            })
        output[model] = divergences
    return output

