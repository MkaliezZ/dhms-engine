"""DHMS v2 cross-model orchestration."""

from typing import Any

from cross_model_runner import run_cross_model_experiment
from measurement_engine import build_measurement
from model_comparison import compare_models


def run_v2_experiment(mode: str, input_text: str, n: int = 1, models: str = "mock") -> dict[str, Any]:
    cross_model = run_cross_model_experiment(mode, input_text, n, models)
    per_model_results = cross_model["per_model_results"]
    comparison = compare_models(per_model_results)
    primary_model = cross_model["model_names"][0]
    primary_runs = per_model_results[primary_model]["per_run_results"]
    primary_measurement = build_measurement(primary_runs)
    first = primary_runs[0]

    return {
        "engine_version": "DHMS v2 Cross-Model + Statistical Significance System",
        "compatible_engine": "DHMS v1 Measurement System",
        "binding_version": first["binding_version"],
        "contract_version": first["contract_version"],
        "requested_mode": mode,
        "trial_count": n,
        "model_count": cross_model["model_count"],
        "model_names": cross_model["model_names"],
        "execution_permitted": all(
            run_result["execution_permitted"]
            for model_result in per_model_results.values()
            for run_result in model_result["per_run_results"]
        ),
        "regime_results": first["regime_results"],
        "metric_results": primary_measurement["aggregated_metrics"],
        "aggregated_metrics": primary_measurement["aggregated_metrics"],
        "metric_distributions": primary_measurement["metric_distributions"],
        "regime_comparison": primary_measurement["regime_comparison"],
        "perturbation_summary": first["perturbation_summary"],
        "per_run_results": primary_runs,
        "per_model_results": per_model_results,
        "cross_model_comparison": {
            "model_count": cross_model["model_count"],
            "model_names": cross_model["model_names"],
            "per_model_metric_means": comparison["per_model_metric_means"],
            "cross_model_variance": comparison["cross_model_variance"],
            "regime_divergence_by_model": comparison["regime_divergence_by_model"],
        },
        "statistical_significance_summary": {
            "pairwise_metric_tests": comparison["pairwise_metric_tests"],
            "confidence_scores": comparison["confidence_scores"],
        },
        "effect_size_report": _effect_size_report(comparison["pairwise_metric_tests"]),
        "regime_consistency_report": cross_model["regime_consistency_report"],
        "final_summary": {
            "requested_mode": mode,
            "trial_count": n,
            "model_names": cross_model["model_names"],
            "input_identity_preserved": cross_model["regime_consistency_report"]["input_identity_preserved_within_runs"],
            "conditions_aligned_across_models": cross_model["regime_consistency_report"]["conditions_aligned_across_models"],
            "cross_model_agreement": comparison["confidence_scores"]["cross_model_agreement"],
        },
    }


def _effect_size_report(pairwise_metric_tests: dict[str, Any]) -> dict[str, Any]:
    return {
        pair: {
            metric: values["effect_size"]
            for metric, values in metrics.items()
        }
        for pair, metrics in pairwise_metric_tests.items()
    }

