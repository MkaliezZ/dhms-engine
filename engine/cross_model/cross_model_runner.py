"""Cross-model DHMS experiment runner."""

from typing import Any, Mapping

from binding_layer import bind_run
from execution_pipeline import REGIME_NAMES, build_run_request, compute_metrics
from model_router import select_models


def run_cross_model_experiment(mode: str, input_text: str, n: int, models: str) -> dict[str, Any]:
    if n < 1:
        raise ValueError("n must be greater than or equal to 1")
    selected_models = select_models(models)
    per_model_results = {}
    for model in selected_models:
        per_model_results[model.name] = _run_single_model(model, mode, input_text, n)
    return {
        "model_count": len(per_model_results),
        "model_names": list(per_model_results.keys()),
        "per_model_results": per_model_results,
        "regime_consistency_report": _build_regime_consistency_report(per_model_results),
    }


def _run_single_model(model: Any, mode: str, input_text: str, n: int) -> dict[str, Any]:
    per_run_results = []
    for index in range(n):
        run_request = build_run_request(mode, input_text)
        binding_view = bind_run(run_request)
        result = _execute_with_model(run_request, binding_view, model)
        result["trial_index"] = index + 1
        per_run_results.append(result)
    return {
        "model_name": model.name,
        "trial_count": n,
        "per_run_results": per_run_results,
    }


def _execute_with_model(run_request: Mapping[str, Any], binding_view: Mapping[str, Any], model: Any) -> dict[str, Any]:
    regimes = run_request["regimes"]
    requested_mode = run_request.get("requested_mode")
    regime_results = {}
    for name in REGIME_NAMES:
        regime = regimes[name]
        input_text = regime["input_condition"]["text"]
        memory_condition = regime["memory_condition"]
        response = model.generate(input_text, name, memory_condition)
        regime_results[name] = {
            "input_condition": regime["input_condition"],
            "memory_condition": memory_condition,
            "response": response,
            "selected_by_mode": requested_mode == name[-1],
        }
    return {
        "engine_version": "DHMS v2 Cross-Model System",
        "binding_version": binding_view["binding_version"],
        "contract_version": binding_view["contract_version"],
        "requested_mode": requested_mode,
        "execution_permitted": binding_view["execution_permitted"],
        "model_name": model.name,
        "regime_results": regime_results,
        "metric_results": compute_metrics(regime_results),
        "perturbation_summary": {
            "target": run_request["perturbation"]["target"],
            "scope": run_request["perturbation"]["scope"],
            "direction": run_request["perturbation"]["direction"],
            "relation_to_baseline": run_request["perturbation"]["relation_to_baseline"],
            "input_preserved": all(
                regimes[name]["input_condition"] == regimes["DHMS-A"]["input_condition"]
                for name in REGIME_NAMES
            ),
        },
    }


def _build_regime_consistency_report(per_model_results: Mapping[str, Any]) -> dict[str, Any]:
    inputs = []
    perturbations = []
    for model_result in per_model_results.values():
        for run_result in model_result["per_run_results"]:
            regimes = run_result["regime_results"]
            inputs.append(tuple(str(regimes[name]["input_condition"]) for name in REGIME_NAMES))
            perturbations.append(str(run_result["perturbation_summary"]))
    return {
        "input_identity_preserved_within_runs": all(len(set(item)) == 1 for item in inputs),
        "conditions_aligned_across_models": len(set(inputs)) <= 1 and len(set(perturbations)) <= 1,
        "checked_runs": sum(len(result["per_run_results"]) for result in per_model_results.values()),
    }

