"""Strict DHMS-A / DHMS-B / DHMS-C regime validation."""

from typing import Mapping, Any


class RegimeValidationError(ValueError):
    """Raised when a DHMS regime set violates binding requirements."""


REQUIRED_REGIMES = ("DHMS-A", "DHMS-B", "DHMS-C")
REQUIRED_FIELDS = frozenset(
    {
        "input_condition",
        "memory_condition",
        "task_framing",
        "evaluation_criterion",
        "observational_procedure",
    }
)
PROTECTED_FIELDS = frozenset(
    {
        "input_condition",
        "task_framing",
        "evaluation_criterion",
        "observational_procedure",
        "metric_profile",
    }
)


def _fail(message: str) -> None:
    raise RegimeValidationError(message)


def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail(f"{name} must be a mapping.")
    return value


def _extract_regimes(regimes: Any) -> dict[str, Mapping[str, Any]]:
    source = _require_mapping(regimes, "regimes")
    if set(source.keys()) != set(REQUIRED_REGIMES):
        expected = ", ".join(REQUIRED_REGIMES)
        _fail(f"regimes must contain exactly: {expected}.")

    normalized: dict[str, Mapping[str, Any]] = {}
    for name in REQUIRED_REGIMES:
        regime = _require_mapping(source[name], name)
        missing = REQUIRED_FIELDS.difference(regime.keys())
        if missing:
            _fail(f"{name} missing required fields: {', '.join(sorted(missing))}.")
        declared = regime.get("name", name)
        if declared != name:
            _fail(f"{name} must not be declared as {declared!r}.")
        normalized[name] = regime
    return normalized


def validate_regime_set(regimes: Any) -> dict[str, Mapping[str, Any]]:
    """Validate DHMS regime consistency without executing an engine."""
    normalized = _extract_regimes(regimes)
    baseline = normalized["DHMS-A"]

    for name in ("DHMS-B", "DHMS-C"):
        regime = normalized[name]
        for field in PROTECTED_FIELDS:
            if field in baseline or field in regime:
                if baseline.get(field) != regime.get(field):
                    _fail(f"{field} must be identical across DHMS-A, DHMS-B, and DHMS-C.")

    if baseline.get("memory_condition") == normalized["DHMS-B"].get("memory_condition"):
        _fail("DHMS-B must contain a memory-condition difference from DHMS-A.")

    if normalized["DHMS-C"].get("memory_condition") == normalized["DHMS-B"].get("memory_condition"):
        _fail("DHMS-C must not collapse into the DHMS-B perturbed-memory condition.")

    return normalized

