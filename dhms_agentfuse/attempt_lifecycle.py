"""Neutral, attempt-scoped lifecycle evidence; no dispatch or retry control."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from typing import Any

from .evidence_lifecycle import ExecutionLifecycleEvidence, is_strict_pre_dispatch
from .evidence_schema import NonExecutionEvidence

ATTEMPT_LIFECYCLE_SCHEMA_VERSION = "agentfuse-attempt-lifecycle-evidence-schema-v0.3"


@dataclass(frozen=True)
class AttemptLifecycleEvidenceRecord:
    """Lifecycle facts for one attempt, independent of any policy decision.

    ``logical_action_ref`` correlates attempts but carries no shared outcome.
    ``attempt_ref`` identifies this attempt and scopes all attached evidence.
    For an original dispatch without a reported denial stage, use the existing
    lifecycle ``block_stage='unknown'``; do not fabricate a denial decision.
    Hosts own reference allocation, evidence collection, retries and recovery.
    """

    record_id: str
    schema_version: str
    logical_action_ref: str
    attempt_ref: str
    lifecycle: ExecutionLifecycleEvidence
    non_execution: NonExecutionEvidence | None = None

    def __post_init__(self) -> None:
        for field_name in ("record_id", "logical_action_ref", "attempt_ref"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.schema_version != ATTEMPT_LIFECYCLE_SCHEMA_VERSION:
            raise ValueError(f"schema_version must be {ATTEMPT_LIFECYCLE_SCHEMA_VERSION}")
        if not isinstance(self.lifecycle, ExecutionLifecycleEvidence):
            raise ValueError("lifecycle must be ExecutionLifecycleEvidence")
        if self.non_execution is not None:
            if not isinstance(self.non_execution, NonExecutionEvidence):
                raise ValueError("non_execution must be NonExecutionEvidence or None")
            if not is_strict_pre_dispatch(self.lifecycle):
                raise ValueError(
                    "non-execution evidence requires strict pre_dispatch lifecycle evidence"
                )

    def to_dict(self) -> dict[str, Any]:
        """Serialize this attempt alone without importing sibling evidence."""

        return asdict(self)


def correlate_attempt_lifecycle_records(
    records: Iterable[AttemptLifecycleEvidenceRecord],
) -> dict[str, tuple[AttemptLifecycleEvidenceRecord, ...]]:
    """Group intact records by logical action, rejecting duplicate attempt refs.

    Uniqueness is checked across the supplied collection, including across
    different logical actions. Each group retains input order, not inferred
    chronology. Nothing is merged, deduplicated, reconciled or executed.
    This collection check is not a persistent ledger or exactly-once guarantee.
    """

    seen_attempts: set[str] = set()
    groups: dict[str, list[AttemptLifecycleEvidenceRecord]] = {}
    for record in records:
        if not isinstance(record, AttemptLifecycleEvidenceRecord):
            raise ValueError("records must contain AttemptLifecycleEvidenceRecord values")
        if record.attempt_ref in seen_attempts:
            raise ValueError(f"duplicate attempt_ref: {record.attempt_ref}")
        seen_attempts.add(record.attempt_ref)
        groups.setdefault(record.logical_action_ref, []).append(record)
    return {action_ref: tuple(attempts) for action_ref, attempts in groups.items()}
