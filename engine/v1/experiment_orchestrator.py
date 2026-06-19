"""Experiment orchestration for DHMS v1 measurement."""

from typing import Any

from binding_layer import bind_run
from execution_pipeline import build_run_request, execute_pipeline
from measurement_engine import build_measurement
from result_summarizer import build_summary


def run_experiment(mode: str, input_text: str, n: int = 1) -> dict[str, Any]:
    if n < 1:
        raise ValueError("n must be greater than or equal to 1")

    per_run_results = []
    for index in range(n):
        run_request = build_run_request(mode, input_text)
        binding_view = bind_run(run_request)
        result = execute_pipeline(run_request, binding_view)
        result["trial_index"] = index + 1
        per_run_results.append(result)

    measurement = build_measurement(per_run_results)
    summary = build_summary(
        mode=mode,
        input_text=input_text,
        n=n,
        measurement=measurement,
        per_run_results=per_run_results,
    )

    first = per_run_results[0]
    return {
        "engine_version": "DHMS v1 Measurement System",
        "compatible_engine": first["engine_version"],
        "binding_version": first["binding_version"],
        "contract_version": first["contract_version"],
        "requested_mode": mode,
        "trial_count": n,
        "execution_permitted": all(result["execution_permitted"] for result in per_run_results),
        "llm_adapter": first["llm_adapter"],
        "regime_results": first["regime_results"],
        "metric_results": measurement["aggregated_metrics"],
        "aggregated_metrics": measurement["aggregated_metrics"],
        "metric_distributions": measurement["metric_distributions"],
        "regime_comparison": measurement["regime_comparison"],
        "perturbation_summary": first["perturbation_summary"],
        "per_run_results": per_run_results,
        "final_summary": summary,
    }

