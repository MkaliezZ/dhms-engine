"""DHMS Engine Binding Layer v1.

This module is a semantic firewall between DHMS Contract Layer v1 and any
future engine implementation. It validates a run request before execution and
never performs engine execution itself.
"""

from types import MappingProxyType
from typing import Mapping, Any, Optional

from regime_validator import validate_regime_set
from perturbation_guard import validate_perturbation
from metric_lock import validate_metric_lock
from execution_gate import ExecutionGate, BindingViolation

SPEC_VERSION = "DHMS Isolation Spec v1"
CONTRACT_VERSION = "DHMS Contract Layer v1"
BINDING_VERSION = "DHMS Engine Binding Layer v1"

IMMUTABLE_SPEC_TERMS = frozenset(
    {
        "memory",
        "perturbation",
        "DHMS-A",
        "DHMS-B",
        "DHMS-C",
        "behavioral_trace",
        "metric_category",
    }
)

FORBIDDEN_ENGINE_AUTHORITIES = frozenset(
    {
        "define_memory",
        "redefine_memory",
        "define_perturbation",
        "redefine_perturbation",
        "define_regime",
        "redefine_regime",
        "define_metric_semantics",
        "redefine_metric_semantics",
        "override_spec",
        "override_contract",
    }
)


def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise BindingViolation(f"{name} must be a mapping.")
    return value


def enforce_semantic_immutability(engine_claims: Optional[Mapping[str, Any]]) -> None:
    """Reject any engine-declared authority over DHMS semantics."""
    claims = {} if engine_claims is None else _require_mapping(engine_claims, "engine_claims")
    requested_authority = set(claims.get("semantic_authority", ()))
    forbidden = requested_authority.intersection(FORBIDDEN_ENGINE_AUTHORITIES)
    if forbidden:
        names = ", ".join(sorted(forbidden))
        raise BindingViolation(f"engine may not claim semantic authority: {names}")

    term_overrides = set(claims.get("term_overrides", ()))
    illegal_overrides = term_overrides.intersection(IMMUTABLE_SPEC_TERMS)
    if illegal_overrides:
        names = ", ".join(sorted(illegal_overrides))
        raise BindingViolation(f"engine may not override DHMS terms: {names}")


def bind_run(run_request: Mapping[str, Any]) -> Mapping[str, Any]:
    """Validate a DHMS run request and return a read-only execution view.

    The returned mapping is permission to proceed to an engine layer. It is not
    an engine result and contains no interpretation of outputs.
    """
    request = _require_mapping(run_request, "run_request")
    enforce_semantic_immutability(request.get("engine_claims"))

    regimes = validate_regime_set(request.get("regimes"))
    perturbation = validate_perturbation(
        request.get("perturbation"),
        baseline_memory=regimes["DHMS-A"].get("memory_condition"),
        perturbed_memory=regimes["DHMS-B"].get("memory_condition"),
        regime_inputs={name: regime.get("input_condition") for name, regime in regimes.items()},
        protected_fields={
            "input_condition",
            "task_framing",
            "evaluation_criterion",
            "observational_procedure",
            "metric_profile",
        },
    )
    metric_profile = validate_metric_lock(request.get("metrics"))

    gate = ExecutionGate()
    gate.validate(
        regimes=regimes,
        perturbation=perturbation,
        metrics=metric_profile,
        contract_version=request.get("contract_version"),
    )

    return MappingProxyType(
        {
            "binding_version": BINDING_VERSION,
            "spec_version": SPEC_VERSION,
            "contract_version": CONTRACT_VERSION,
            "regimes": MappingProxyType(dict(regimes)),
            "perturbation": MappingProxyType(dict(perturbation)),
            "metrics": MappingProxyType(dict(metric_profile)),
            "execution_permitted": True,
        }
    )

