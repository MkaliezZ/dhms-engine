"""Metric interpretation lock for DHMS binding validation."""

from typing import Mapping, Any


class MetricLockError(ValueError):
    """Raised when metrics attempt to influence behavior or semantics."""


ALLOWED_METRICS = frozenset(
    {
        "stability",
        "sensitivity",
        "specificity",
        "isolation_strength",
    }
)
FORBIDDEN_METRIC_AUTHORITIES = frozenset(
    {
        "modify_input",
        "modify_memory",
        "modify_perturbation",
        "modify_regime",
        "modify_execution",
        "define_memory",
        "define_perturbation",
        "define_regime",
        "define_metric_semantics",
        "override_spec",
        "override_contract",
    }
)


def _fail(message: str) -> None:
    raise MetricLockError(message)


def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail(f"{name} must be a mapping.")
    return value


def validate_metric_lock(metrics: Any) -> Mapping[str, Any]:
    """Ensure metrics remain interpretation-only and implementation-agnostic."""
    profile = _require_mapping(metrics, "metrics")
    declared = set(profile.get("declared_metrics", ()))
    if not declared:
        _fail("metrics must declare interpretation categories.")

    unknown = declared.difference(ALLOWED_METRICS)
    if unknown:
        _fail(f"metrics introduce unsupported categories: {', '.join(sorted(unknown))}.")

    authorities = set(profile.get("authorities", ()))
    forbidden = authorities.intersection(FORBIDDEN_METRIC_AUTHORITIES)
    if forbidden:
        _fail(f"metrics claim forbidden authority: {', '.join(sorted(forbidden))}.")

    if profile.get("interpretation_only") is not True:
        _fail("metrics must be marked interpretation_only=True.")
    if profile.get("can_modify_behavior") is not False:
        _fail("metrics must not modify system behavior.")
    if profile.get("implementation_agnostic") is not True:
        _fail("metrics must be implementation-agnostic.")

    return profile

