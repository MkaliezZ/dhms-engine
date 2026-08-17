"""Immutable metadata for reviewed AgentFuse integration mappings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


IntegrationKind = Literal[
    "canonical",
    "reference",
    "internal_adapter",
    "external_adapter",
]
ImplementationOwner = Literal["dhms", "host", "external_project"]

_INTEGRATION_KINDS = {
    "canonical",
    "reference",
    "internal_adapter",
    "external_adapter",
}
_IMPLEMENTATION_OWNERS = {"dhms", "host", "external_project"}
_CANONICAL_ACTIONS = ("allow", "block")


def _require_text(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _require_text_tuple(name: str, values: tuple[str, ...]) -> None:
    if not isinstance(values, tuple):
        raise TypeError(f"{name} must be a tuple")
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f"{name} must contain only non-empty strings")
    if len(values) != len(set(values)):
        raise ValueError(f"{name} must not contain duplicates")


@dataclass(frozen=True)
class IntegrationProfile:
    """Metadata-only description of one bounded, reviewed integration path.

    ``evidenced_capabilities`` records facts observed or represented in the
    named tested path. It does not transfer ownership of host lifecycle
    behavior to AgentFuse.
    """

    integration_id: str
    runtime_family: str
    integration_kind: IntegrationKind
    implementation_owner: ImplementationOwner
    implementation_reference: str
    canonical_actions: tuple[str, ...]
    decision_boundary: str
    evidenced_capabilities: tuple[str, ...]
    host_owned_facts: tuple[str, ...]
    tested_runtime: str
    tested_version: str | None
    tested_commit: str | None
    fixture_version: str
    fixture_digest: str
    evidence_scope: str
    evidence_references: tuple[str, ...]
    limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in (
            "integration_id",
            "runtime_family",
            "implementation_reference",
            "decision_boundary",
            "tested_runtime",
            "fixture_version",
            "fixture_digest",
            "evidence_scope",
        ):
            _require_text(name, getattr(self, name))
        for name in ("tested_version", "tested_commit"):
            value = getattr(self, name)
            if value is not None:
                _require_text(name, value)
        if self.integration_kind not in _INTEGRATION_KINDS:
            raise ValueError(f"unsupported integration_kind={self.integration_kind!r}")
        if self.implementation_owner not in _IMPLEMENTATION_OWNERS:
            raise ValueError(
                f"unsupported implementation_owner={self.implementation_owner!r}"
            )
        if self.canonical_actions != _CANONICAL_ACTIONS:
            raise ValueError("canonical_actions must remain exactly allow|block")
        for name in (
            "canonical_actions",
            "evidenced_capabilities",
            "host_owned_facts",
            "evidence_references",
            "limitations",
        ):
            _require_text_tuple(name, getattr(self, name))

    def to_safe_dict(self) -> dict[str, Any]:
        """Return deterministic metadata without live runtime objects."""

        return {
            "integration_id": self.integration_id,
            "runtime_family": self.runtime_family,
            "integration_kind": self.integration_kind,
            "implementation_owner": self.implementation_owner,
            "implementation_reference": self.implementation_reference,
            "canonical_actions": list(self.canonical_actions),
            "decision_boundary": self.decision_boundary,
            "evidenced_capabilities": list(self.evidenced_capabilities),
            "host_owned_facts": list(self.host_owned_facts),
            "tested_runtime": self.tested_runtime,
            "tested_version": self.tested_version,
            "tested_commit": self.tested_commit,
            "fixture_version": self.fixture_version,
            "fixture_digest": self.fixture_digest,
            "evidence_scope": self.evidence_scope,
            "evidence_references": list(self.evidence_references),
            "limitations": list(self.limitations),
        }


__all__ = ["IntegrationProfile"]
