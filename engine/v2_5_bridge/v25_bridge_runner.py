"""Main orchestration layer for DHMS V2.5 Real API Bridge."""

import sys
from pathlib import Path
from typing import Any, Mapping

CURRENT_DIR = Path(__file__).resolve().parent
ENGINE_DIR = CURRENT_DIR.parent
ROOT_DIR = ENGINE_DIR.parent
PATHS = (
    CURRENT_DIR,
    ENGINE_DIR / "v0",
    ENGINE_DIR / "v1",
    ENGINE_DIR / "cross_model",
    ENGINE_DIR / "statistics",
    ENGINE_DIR / "v2_cross_model",
    ROOT_DIR / "binding",
)
for path in PATHS:
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)

from api_adapters import create_api_model, parse_api_names  # noqa: E402
from drift_detector import analyze_drift  # noqa: E402
from noise_calibrator import estimate_noise  # noqa: E402
from response_normalizer import normalize_model_results  # noqa: E402
from execution_pipeline import REGIME_NAMES, build_run_request, compute_metrics  # noqa: E402
from binding_layer import bind_run  # noqa: E402
from v2_orchestrator import run_v2_experiment  # noqa: E402


def run_v25_bridge(
    mode: str,
    input_text: str,
    n: int = 1,
    models: str = "mock",
    api_models: str = "openai,deepseek,claude",
) -> dict[str, Any]:
    v2_results = run_v2_experiment(mode, input_text, n=n, models=models)
    raw_real_results = _run_real_api_models(mode, input_text, n, api_models)
    real_api_results = normalize_model_results(raw_real_results)
    drift_analysis = analyze_drift(v2_results, real_api_results)
    noise_estimation = estimate_noise(real_api_results)
    return {
        "engine_version": "DHMS V2.5 Real API Bridge Layer",
        "bridge_role": "V2 enrichment only; V2 metrics remain authoritative",
        "v2_results": v2_results,
        "real_api_results": real_api_results,
        "drift_analysis": drift_analysis,
        "noise_estimation": noise_estimation,
        "cross_model_real_world_comparison": _build_real_world_comparison(v2_results, real_api_results, drift_analysis),
    }


def _run_real_api_models(mode: str, input_text: str, n: int, api_models: str) -> dict[str, Any]:
    names = parse_api_names(api_models)
    if not names:
        return {}
    results = {}
    for name in names:
        model = create_api_model(name)
        per_run_results = []
        for index in range(n):
            run_request = build_run_request(mode, input_text)
            binding_view = bind_run(run_request)
            result = _execute_api_trial(run_request, binding_view, model)
            result["trial_index"] = index + 1
            per_run_results.append(result)
        status = model.status() if hasattr(model, "status") else {}
        key = status.get("requested_model_spec") or model.name
        results[key] = {
            "model_name": model.name,
            "provider_status": status,
            "requested_model_spec": status.get("requested_model_spec", name),
            "provider": status.get("provider", model.name),
            "requested_alias": status.get("requested_alias"),
            "resolved_model_id": status.get("resolved_model_id"),
            "trial_count": n,
            "per_run_results": per_run_results,
        }
    return results


def _execute_api_trial(run_request: Mapping[str, Any], binding_view: Mapping[str, Any], model: Any) -> dict[str, Any]:
    regimes = run_request["regimes"]
    requested_mode = run_request.get("requested_mode")
    regime_results = {}
    for regime_name in REGIME_NAMES:
        regime = regimes[regime_name]
        input_text = regime["input_condition"]["text"]
        memory_condition = regime["memory_condition"]
        response = model.generate(input_text, regime_name, memory_condition)
        regime_results[regime_name] = {
            "input_condition": regime["input_condition"],
            "memory_condition": memory_condition,
            "response": response,
            "selected_by_mode": requested_mode == regime_name[-1],
        }
    return {
        "engine_version": "DHMS V2.5 Real API Bridge Layer",
        "binding_version": binding_view["binding_version"],
        "contract_version": binding_view["contract_version"],
        "requested_mode": requested_mode,
        "execution_permitted": binding_view["execution_permitted"],
        "model_name": model.name,
        "provider_status": model.status() if hasattr(model, "status") else {},
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


def _build_real_world_comparison(
    v2_results: Mapping[str, Any],
    real_api_results: Mapping[str, Any],
    drift_analysis: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "v2_model_names": v2_results.get("model_names", []),
        "real_api_model_names": list(real_api_results.keys()),
        "v2_authoritative_metric_results": v2_results.get("metric_results", {}),
        "real_api_metric_results": _real_api_metric_means(real_api_results),
        "drift_score": drift_analysis["drift_score"],
        "instability_index": drift_analysis["instability_index"],
        "schema_compatibility": {
            "contains_v2_results": True,
            "contains_real_api_results": True,
            "v2_metrics_overridden": False,
        },
    }


def _real_api_metric_means(real_api_results: Mapping[str, Any]) -> dict[str, Any]:
    output = {}
    for model_name, model_result in real_api_results.items():
        metric_values = {}
        for run_result in model_result["per_run_results"]:
            for metric, value in run_result["metric_results"].items():
                metric_values.setdefault(metric, []).append(float(value))
        output[model_name] = {
            metric: round(sum(values) / len(values), 6) if values else 0.0
            for metric, values in metric_values.items()
        }
    return output

