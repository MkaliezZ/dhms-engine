"""Minimal DHMS execution pipeline."""

from typing import Mapping, Any

from llm_adapter import LLMAdapter


REGIME_NAMES = ("DHMS-A", "DHMS-B", "DHMS-C")


def build_run_request(mode: str, input_text: str) -> dict[str, Any]:
    if mode not in {"A", "B", "C"}:
        raise ValueError("mode must be A, B, or C")

    shared = {
        "input_condition": {"text": input_text},
        "task_framing": {"task": "respond_to_fixed_input"},
        "evaluation_criterion": {"criterion": "observe_behavioral_trace"},
        "observational_procedure": {"procedure": "single_black_box_completion"},
        "metric_profile": {"declared_metrics": ["stability", "sensitivity", "specificity", "isolation_strength"]},
    }

    return {
        "contract_version": "DHMS Contract Layer v1",
        "engine_claims": {"semantic_authority": [], "term_overrides": []},
        "requested_mode": mode,
        "regimes": {
            "DHMS-A": {**shared, "name": "DHMS-A", "memory_condition": {"state": "baseline"}},
            "DHMS-B": {**shared, "name": "DHMS-B", "memory_condition": {"state": "perturbed"}},
            "DHMS-C": {**shared, "name": "DHMS-C", "memory_condition": {"state": "control"}},
        },
        "perturbation": {
            "target": "memory_condition",
            "scope": "memory_condition",
            "direction": "baseline_to_perturbed_memory_condition",
            "relation_to_baseline": "DHMS-B differs from DHMS-A only in memory_condition",
            "changed_fields": ["memory_condition"],
            "alters_input": False,
            "alters_task": False,
            "alters_metrics": False,
        },
        "metrics": {
            "declared_metrics": ["stability", "sensitivity", "specificity", "isolation_strength"],
            "authorities": [],
            "interpretation_only": True,
            "can_modify_behavior": False,
            "implementation_agnostic": True,
        },
    }


def execute_pipeline(run_request: Mapping[str, Any], binding_view: Mapping[str, Any]) -> dict[str, Any]:
    adapter = LLMAdapter()
    regimes = run_request["regimes"]
    requested_mode = run_request.get("requested_mode")

    regime_results = {}
    for name in REGIME_NAMES:
        regime = regimes[name]
        input_text = regime["input_condition"]["text"]
        memory_condition = regime["memory_condition"]
        response = adapter.complete(
            input_text=input_text,
            regime_name=name,
            memory_condition=memory_condition,
        )
        regime_results[name] = {
            "input_condition": regime["input_condition"],
            "memory_condition": memory_condition,
            "response": response,
            "selected_by_mode": requested_mode == name[-1],
        }

    metrics = compute_metrics(regime_results)
    return {
        "engine_version": "DHMS Minimal Engine v0",
        "binding_version": binding_view["binding_version"],
        "contract_version": binding_view["contract_version"],
        "requested_mode": requested_mode,
        "execution_permitted": binding_view["execution_permitted"],
        "llm_adapter": "deterministic_mock" if adapter.uses_mock else "external_black_box",
        "regime_results": regime_results,
        "metric_results": metrics,
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


def compute_metrics(regime_results: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    a = regime_results["DHMS-A"]["response"]
    b = regime_results["DHMS-B"]["response"]
    c = regime_results["DHMS-C"]["response"]
    inputs_identical = len({str(regime_results[name]["input_condition"]) for name in REGIME_NAMES}) == 1
    b_differs_from_a = b != a
    c_differs_from_b = c != b

    return {
        "stability": 1.0,
        "sensitivity": 1.0 if b_differs_from_a else 0.0,
        "specificity": 1.0 if b_differs_from_a and c_differs_from_b and inputs_identical else 0.0,
        "isolation_strength": 1.0 if inputs_identical and b_differs_from_a and c_differs_from_b else 0.0,
    }

