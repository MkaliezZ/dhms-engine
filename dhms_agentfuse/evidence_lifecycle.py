"""AgentFuse Evidence Lifecycle Schema v0.2.

Additive lifecycle evidence that separates a policy denial from the observed
dispatch, execution, and side-effect reality of a tool call. Evidence Schema
v0.1 in ``evidence_schema`` remains valid and semantically unchanged; this
module does not modify or weaken :class:`NonExecutionEvidence`, which still
means a call for which non-execution is affirmatively established.

External technical feedback identified an evidence-modeling gap: a denial that
races with dispatch (policy says block, execution already started and applied
external side effects) cannot be represented truthfully by strict
non-execution evidence alone. This module models that gap without changing any
runtime behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .evidence_schema import (
    LayeredBoundaryDecision,
    NonExecutionEvidence,
    PolicyResolutionEvidence,
    SafeTraceMetadata,
)

LIFECYCLE_SCHEMA_VERSION = "agentfuse-evidence-lifecycle-schema-v0.2"

# Immutable canonical state collections: these define validation semantics and
# must not be mutable through the public API.
BLOCK_STAGES = frozenset({"pre_dispatch", "post_dispatch", "unknown"})
DISPATCH_STATES = frozenset({"not_started", "started", "unknown"})
EXECUTION_LIFECYCLE_STATES = frozenset(
    {"not_executed", "executed", "partially_executed", "unknown"}
)
SIDE_EFFECT_STATES = frozenset({"proven_none", "observed", "possible", "unknown"})


def _ensure_non_empty_string(value: str | None, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")


def is_strict_pre_dispatch(lifecycle: ExecutionLifecycleEvidence) -> bool:
    """Return True when lifecycle evidence establishes strict pre-dispatch non-execution."""

    return (
        lifecycle.block_stage == "pre_dispatch"
        and lifecycle.dispatch_state == "not_started"
        and lifecycle.execution_state == "not_executed"
        and lifecycle.side_effect_state == "proven_none"
    )


@dataclass(frozen=True)
class ExecutionLifecycleEvidence:
    """Execution-reality evidence for one denied or allowed tool call.

    The four states keep policy intent, dispatch reality, execution reality,
    and side-effect reality separate. Missing or ambiguous facts must stay
    ``unknown``; they must never be recorded as proof of non-execution.
    """

    block_stage: str
    dispatch_state: str
    execution_state: str
    side_effect_state: str

    def __post_init__(self) -> None:
        if self.block_stage not in BLOCK_STAGES:
            raise ValueError(f"unknown block_stage: {self.block_stage}")
        if self.dispatch_state not in DISPATCH_STATES:
            raise ValueError(f"unknown dispatch_state: {self.dispatch_state}")
        if self.execution_state not in EXECUTION_LIFECYCLE_STATES:
            raise ValueError(f"unknown execution_state: {self.execution_state}")
        if self.side_effect_state not in SIDE_EFFECT_STATES:
            raise ValueError(f"unknown side_effect_state: {self.side_effect_state}")

        # Invariant A, and by contrapositive Invariants B and D: a proven
        # pre-dispatch block implies strict non-execution, so a started
        # dispatch or an observed side effect can never carry block_stage
        # 'pre_dispatch'.
        if self.block_stage == "pre_dispatch":
            if self.dispatch_state != "not_started":
                raise ValueError("pre_dispatch block requires dispatch_state='not_started'")
            if self.execution_state != "not_executed":
                raise ValueError("pre_dispatch block requires execution_state='not_executed'")
            if self.side_effect_state != "proven_none":
                raise ValueError("pre_dispatch block requires side_effect_state='proven_none'")

        # 'post_dispatch' is definitive: the denial became established after
        # dispatch had already begun, so an unstarted or unknown dispatch
        # contradicts the stage claim itself.
        if self.block_stage == "post_dispatch" and self.dispatch_state != "started":
            raise ValueError("post_dispatch block requires dispatch_state='started'")

        # Invariant C: execution that happened cannot coexist with unstarted dispatch.
        if self.execution_state in {"executed", "partially_executed"}:
            if self.dispatch_state == "not_started":
                raise ValueError(
                    f"execution_state='{self.execution_state}' is incompatible with dispatch_state='not_started'"
                )

        # Side-effect evidence is scoped to this governed tool call: a
        # confirmed unstarted dispatch cannot coexist with observed or possible
        # side effects. 'unknown' remains representable because a not-started
        # dispatch does not prove the absence of side effects.
        if self.dispatch_state == "not_started" and self.side_effect_state in {
            "observed",
            "possible",
        }:
            raise ValueError(
                "dispatch_state='not_started' is incompatible with "
                f"side_effect_state='{self.side_effect_state}'"
            )

        # Invariant E holds by construction: every state set contains 'unknown'
        # and no validation path converts missing facts into proof values.

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LifecycleEvidenceRecord:
    """Combined v0.2 record for denial-like paths: v0.1 policy evidence plus execution-reality evidence.

    Intentionally limited to ``block`` and ``escalate`` decisions: block_stage
    describes the stage at which a denial applies, so allowed or transformed
    calls are out of scope for this v0.2 record.
    """

    record_id: str
    schema_version: str
    policy_resolution: PolicyResolutionEvidence
    boundary_decision: LayeredBoundaryDecision
    trace_metadata: SafeTraceMetadata
    lifecycle: ExecutionLifecycleEvidence
    non_execution: NonExecutionEvidence | None = None

    def __post_init__(self) -> None:
        _ensure_non_empty_string(self.record_id, "record_id")
        if self.schema_version != LIFECYCLE_SCHEMA_VERSION:
            raise ValueError(f"schema_version must be {LIFECYCLE_SCHEMA_VERSION}")
        if self.boundary_decision.decision not in {"block", "escalate"}:
            raise ValueError(
                "lifecycle evidence records require a denial-like boundary decision "
                "('block' or 'escalate')"
            )
        if self.boundary_decision.decision != self.trace_metadata.decision:
            raise ValueError("boundary decision must match trace decision")
        if self.boundary_decision.boundary_type != self.trace_metadata.boundary_type:
            raise ValueError("boundary type must match trace boundary type")

        if self.non_execution is not None:
            if not is_strict_pre_dispatch(self.lifecycle):
                raise ValueError(
                    "non-execution evidence requires strict pre_dispatch lifecycle evidence"
                )

        if self.non_execution is None and is_strict_pre_dispatch(self.lifecycle):
            raise ValueError(
                "strict pre-dispatch blocked or escalated calls require non-execution evidence"
            )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def pre_dispatch_policy_denial_lifecycle_evidence() -> LifecycleEvidenceRecord:
    """Create deterministic v0.2 evidence for a strict pre-dispatch policy denial."""

    policy = PolicyResolutionEvidence(
        policy_resolution_outcome="resolved",
        match_stage="capability",
        matched_policy_key="capability:sql_mutation",
        match_kind="capability",
        priority=10,
        candidate_policy_keys=["capability:sql_mutation"],
        fallback_reason=None,
    )
    boundary = LayeredBoundaryDecision(
        boundary_type="call",
        decision="block",
        policy_id="policy-block-sql-mutation",
        policy_hash="sha256:block-sql-mutation-v0",
        reason_code="policy_denied",
        decisive_gate=True,
    )
    trace = SafeTraceMetadata(
        tool_name="dangerous_sql_mutation_tool",
        decision="block",
        policy_id=boundary.policy_id,
        policy_hash=boundary.policy_hash,
        reason_code=boundary.reason_code,
        boundary_type=boundary.boundary_type,
        args_hash="sha256:redacted-sql-mutation-args",
        evidence_ref="evidence:pre-dispatch-denial-lifecycle:001",
    )
    lifecycle = ExecutionLifecycleEvidence(
        block_stage="pre_dispatch",
        dispatch_state="not_started",
        execution_state="not_executed",
        side_effect_state="proven_none",
    )
    non_execution = NonExecutionEvidence(
        status="not_executed",
        reason="policy_denied",
        execution="not_started",
        payload_executed=False,
        tool_failure=False,
        side_effect_occurred=False,
        approval_id="approval:pre-dispatch-denial-lifecycle:001",
        call_id="call:dangerous_sql_mutation_tool:001",
        result_ref="result:not_executed:pre-dispatch-denial-lifecycle:001",
    )
    return LifecycleEvidenceRecord(
        record_id="agentfuse-evidence-lifecycle-pre-dispatch-denial-001",
        schema_version=LIFECYCLE_SCHEMA_VERSION,
        policy_resolution=policy,
        boundary_decision=boundary,
        trace_metadata=trace,
        lifecycle=lifecycle,
        non_execution=non_execution,
    )


def post_dispatch_denial_race_lifecycle_evidence() -> LifecycleEvidenceRecord:
    """Create deterministic v0.2 evidence for a denial that raced with dispatch.

    Models the counterexample pattern where policy returned a denial after the
    host had already started dispatch, the handler executed, and external side
    effects were applied. Reporting this lifecycle as strict
    ``NonExecutionEvidence`` would contradict reality, so none is attached.
    """

    policy = PolicyResolutionEvidence(
        policy_resolution_outcome="resolved",
        match_stage="capability",
        matched_policy_key="capability:shell_mutation",
        match_kind="capability",
        priority=10,
        candidate_policy_keys=["capability:shell_mutation"],
        fallback_reason=None,
    )
    boundary = LayeredBoundaryDecision(
        boundary_type="call",
        decision="block",
        policy_id="policy-block-shell-mutation",
        policy_hash="sha256:block-shell-mutation-v0",
        reason_code="policy_denied",
        decisive_gate=True,
    )
    trace = SafeTraceMetadata(
        tool_name="shell_mutation_tool",
        decision="block",
        policy_id=boundary.policy_id,
        policy_hash=boundary.policy_hash,
        reason_code=boundary.reason_code,
        boundary_type=boundary.boundary_type,
        args_hash="sha256:redacted-shell-mutation-args",
        evidence_ref="evidence:post-dispatch-denial-race:001",
    )
    lifecycle = ExecutionLifecycleEvidence(
        block_stage="post_dispatch",
        dispatch_state="started",
        execution_state="executed",
        side_effect_state="observed",
    )
    return LifecycleEvidenceRecord(
        record_id="agentfuse-evidence-lifecycle-post-dispatch-denial-race-001",
        schema_version=LIFECYCLE_SCHEMA_VERSION,
        policy_resolution=policy,
        boundary_decision=boundary,
        trace_metadata=trace,
        lifecycle=lifecycle,
    )


def ambiguous_post_dispatch_lifecycle_evidence() -> LifecycleEvidenceRecord:
    """Create deterministic v0.2 evidence for an ambiguous post-dispatch denial."""

    policy = PolicyResolutionEvidence(
        policy_resolution_outcome="ambiguous",
        match_stage="pattern",
        matched_policy_key=None,
        match_kind="glob",
        priority=None,
        candidate_policy_keys=["glob:shell_*", "glob:*_mutation_tool"],
        fallback_reason="multiple_matches_failed_tie_break",
    )
    boundary = LayeredBoundaryDecision(
        boundary_type="call",
        decision="block",
        policy_id="policy-ambiguous-post-dispatch",
        policy_hash="sha256:ambiguous-post-dispatch-v0",
        reason_code="ambiguous_policy",
        decisive_gate=True,
    )
    trace = SafeTraceMetadata(
        tool_name="ambiguous_policy_tool",
        decision="block",
        policy_id=boundary.policy_id,
        policy_hash=boundary.policy_hash,
        reason_code=boundary.reason_code,
        boundary_type=boundary.boundary_type,
        args_hash="sha256:redacted-ambiguous-policy-args",
        evidence_ref="evidence:ambiguous-post-dispatch-lifecycle:001",
    )
    lifecycle = ExecutionLifecycleEvidence(
        block_stage="unknown",
        dispatch_state="unknown",
        execution_state="unknown",
        side_effect_state="unknown",
    )
    return LifecycleEvidenceRecord(
        record_id="agentfuse-evidence-lifecycle-ambiguous-post-dispatch-001",
        schema_version=LIFECYCLE_SCHEMA_VERSION,
        policy_resolution=policy,
        boundary_decision=boundary,
        trace_metadata=trace,
        lifecycle=lifecycle,
    )


def partial_execution_denial_lifecycle_evidence() -> LifecycleEvidenceRecord:
    """Create deterministic v0.2 evidence for a partially executed denial."""

    policy = PolicyResolutionEvidence(
        policy_resolution_outcome="resolved",
        match_stage="capability",
        matched_policy_key="capability:batch_file_mutation",
        match_kind="capability",
        priority=20,
        candidate_policy_keys=["capability:batch_file_mutation"],
        fallback_reason=None,
    )
    boundary = LayeredBoundaryDecision(
        boundary_type="call",
        decision="block",
        policy_id="policy-block-batch-file-mutation",
        policy_hash="sha256:block-batch-file-mutation-v0",
        reason_code="policy_denied",
        decisive_gate=True,
    )
    trace = SafeTraceMetadata(
        tool_name="batch_file_mutation_tool",
        decision="block",
        policy_id=boundary.policy_id,
        policy_hash=boundary.policy_hash,
        reason_code=boundary.reason_code,
        boundary_type=boundary.boundary_type,
        args_hash="sha256:redacted-batch-file-mutation-args",
        evidence_ref="evidence:partial-execution-denial-lifecycle:001",
    )
    lifecycle = ExecutionLifecycleEvidence(
        block_stage="post_dispatch",
        dispatch_state="started",
        execution_state="partially_executed",
        side_effect_state="possible",
    )
    return LifecycleEvidenceRecord(
        record_id="agentfuse-evidence-lifecycle-partial-execution-denial-001",
        schema_version=LIFECYCLE_SCHEMA_VERSION,
        policy_resolution=policy,
        boundary_decision=boundary,
        trace_metadata=trace,
        lifecycle=lifecycle,
    )


def lifecycle_example_records() -> list[dict[str, Any]]:
    """Return deterministic JSON-serializable v0.2 examples for documentation/tests."""

    return [
        pre_dispatch_policy_denial_lifecycle_evidence().to_dict(),
        post_dispatch_denial_race_lifecycle_evidence().to_dict(),
        ambiguous_post_dispatch_lifecycle_evidence().to_dict(),
        partial_execution_denial_lifecycle_evidence().to_dict(),
    ]
