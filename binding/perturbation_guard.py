"""Guardrails for DHMS memory perturbations."""

from typing import Mapping, Any


class PerturbationValidationError(ValueError):
    """Raised when a perturbation violates DHMS binding requirements."""


REQUIRED_FIELDS = frozenset({"target", "direction", "relation_to_baseline", "scope"})
FORBIDDEN_SCOPES = frozenset(
    {
        "input_condition",
        "task_framing",
        "evaluation_criterion",
        "observational_procedure",
        "metric_semantics",
        "metric_profile",
        "regime_semantics",
        "spec_semantics",
        "contract_semantics",
    }
)


def _fail(message: str) -> None:
    raise PerturbationValidationError(message)


def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail(f"{name} must be a mapping.")
    return value


def validate_perturbation(
    perturbation: Any,
    *,
    baseline_memory: Any,
    perturbed_memory: Any,
    regime_inputs: Mapping[str, Any],
    protected_fields: Any,
) -> Mapping[str, Any]:
    """Validate that a perturbation is confined to the memory condition."""
    item = _require_mapping(perturbation, "perturbation")
    missing = REQUIRED_FIELDS.difference(item.keys())
    if missing:
        _fail(f"perturbation missing required fields: {', '.join(sorted(missing))}.")

    if item.get("scope") != "memory_condition":
        _fail("perturbation scope must be memory_condition only.")

    if item.get("target") != "memory_condition":
        _fail("perturbation target must be memory_condition only.")

    changed_fields = set(item.get("changed_fields", ("memory_condition",)))
    forbidden_changes = changed_fields.intersection(FORBIDDEN_SCOPES.union(protected_fields))
    forbidden_changes.discard("memory_condition")
    if forbidden_changes:
        _fail(f"perturbation changes forbidden fields: {', '.join(sorted(forbidden_changes))}.")

    if baseline_memory == perturbed_memory:
        _fail("perturbation must create a bounded memory-condition difference from baseline.")

    inputs = list(regime_inputs.values())
    if not inputs or any(value != inputs[0] for value in inputs[1:]):
        _fail("perturbation cannot be evaluated unless regime input identity is preserved.")

    if item.get("alters_input") is True:
        _fail("perturbation must not alter the evaluated input.")
    if item.get("alters_task") is True:
        _fail("perturbation must not alter task framing or task obligation.")
    if item.get("alters_metrics") is True:
        _fail("perturbation must not alter metric semantics or metric profile.")

    if not item.get("direction"):
        _fail("perturbation direction must be fixed before execution.")
    if not item.get("relation_to_baseline"):
        _fail("perturbation relation_to_baseline must be fixed before execution.")

    return item

