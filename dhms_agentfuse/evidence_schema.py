"""AgentFuse Evidence Schema v0.1.

The schema is a minimal, in-memory representation for guarded agent tool-call
evidence. It does not execute tools, call runtimes, inspect raw inputs, or
authorize side effects.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


SCHEMA_VERSION = "agentfuse-evidence-schema-v0.1"

POLICY_RESOLUTION_OUTCOMES = {"resolved", "ambiguous", "no_match"}
MATCH_STAGES = {"exact", "pattern", "capability", "fallback"}
MATCH_KINDS = {"exact", "glob", "regex", "capability", "none"}
NON_EXECUTION_STATUSES = {"not_executed"}
NON_EXECUTION_REASONS = {
    "policy_denied",
    "explicit_denylist",
    "not_allowlisted",
    "policy_exception",
    "invalid_policy_decision",
    "approval_error",
    "user_cancelled",
    "needs_confirmation",
    "ambiguous_policy",
    "no_matching_policy",
}
EXECUTION_STATES = {"not_started"}
BOUNDARY_TYPES = {"server", "tool", "call"}
BOUNDARY_DECISIONS = {"allow", "block", "escalate", "transform"}


def _ensure_non_empty_string(value: str | None, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")


def _ensure_string_list(values: list[str], field_name: str) -> None:
    if not isinstance(values, list):
        raise ValueError(f"{field_name} must be a list")
    for value in values:
        if not isinstance(value, str) or not value:
            raise ValueError(f"{field_name} must contain non-empty strings")


@dataclass(frozen=True)
class PolicyResolutionEvidence:
    """Auditable policy-resolution evidence for a proposed tool call."""

    policy_resolution_outcome: str
    match_stage: str
    matched_policy_key: str | None
    match_kind: str
    priority: int | None
    candidate_policy_keys: list[str] = field(default_factory=list)
    fallback_reason: str | None = None

    def __post_init__(self) -> None:
        if self.policy_resolution_outcome not in POLICY_RESOLUTION_OUTCOMES:
            raise ValueError(f"unknown policy_resolution_outcome: {self.policy_resolution_outcome}")
        if self.match_stage not in MATCH_STAGES:
            raise ValueError(f"unknown match_stage: {self.match_stage}")
        if self.match_kind not in MATCH_KINDS:
            raise ValueError(f"unknown match_kind: {self.match_kind}")
        if self.priority is not None and not isinstance(self.priority, int):
            raise ValueError("priority must be an int or None")
        _ensure_string_list(self.candidate_policy_keys, "candidate_policy_keys")

        if self.policy_resolution_outcome == "resolved":
            if self.fallback_reason is not None:
                raise ValueError("resolved policy resolution must not include fallback_reason")
            _ensure_non_empty_string(self.matched_policy_key, "matched_policy_key")
        else:
            _ensure_non_empty_string(self.fallback_reason, "fallback_reason")

        if self.policy_resolution_outcome == "ambiguous" and len(self.candidate_policy_keys) < 2:
            raise ValueError("ambiguous policy resolution requires at least two candidate policy keys")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NonExecutionEvidence:
    """Machine-readable evidence that a denied tool call did not execute."""

    status: str
    reason: str
    execution: str
    payload_executed: bool
    tool_failure: bool
    side_effect_occurred: bool
    approval_id: str
    call_id: str
    result_ref: str

    def __post_init__(self) -> None:
        if self.status not in NON_EXECUTION_STATUSES:
            raise ValueError(f"unknown non-execution status: {self.status}")
        if self.reason not in NON_EXECUTION_REASONS:
            raise ValueError(f"unknown non-execution reason: {self.reason}")
        if self.execution not in EXECUTION_STATES:
            raise ValueError(f"unknown execution state: {self.execution}")
        for field_name in ("approval_id", "call_id", "result_ref"):
            _ensure_non_empty_string(getattr(self, field_name), field_name)
        if self.execution != "not_started":
            raise ValueError("non-execution evidence requires execution='not_started'")
        if self.payload_executed:
            raise ValueError("non-execution evidence requires payload_executed=False")
        if self.side_effect_occurred:
            raise ValueError("non-execution evidence requires side_effect_occurred=False")
        if self.reason in {"policy_denied", "ambiguous_policy", "no_matching_policy"} and self.tool_failure:
            raise ValueError("policy denial must not be reported as a tool failure")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LayeredBoundaryDecision:
    """Layered server/tool/call policy decision evidence."""

    boundary_type: str
    decision: str
    policy_id: str
    policy_hash: str
    reason_code: str
    decisive_gate: bool

    def __post_init__(self) -> None:
        if self.boundary_type not in BOUNDARY_TYPES:
            raise ValueError(f"unknown boundary_type: {self.boundary_type}")
        if self.decision not in BOUNDARY_DECISIONS:
            raise ValueError(f"unknown boundary decision: {self.decision}")
        for field_name in ("policy_id", "policy_hash", "reason_code"):
            _ensure_non_empty_string(getattr(self, field_name), field_name)
        if self.decisive_gate and self.boundary_type != "call":
            raise ValueError("only a call-level boundary can be the decisive gate")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SafeTraceMetadata:
    """Safe trace metadata for model-visible or audit-visible records."""

    tool_name: str
    decision: str
    policy_id: str
    policy_hash: str
    reason_code: str
    boundary_type: str
    args_hash: str
    evidence_ref: str
    raw_inputs_in_trace: bool = False
    model_visible_trace_sanitized: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "tool_name",
            "decision",
            "policy_id",
            "policy_hash",
            "reason_code",
            "boundary_type",
            "args_hash",
            "evidence_ref",
        ):
            _ensure_non_empty_string(getattr(self, field_name), field_name)
        if self.decision not in BOUNDARY_DECISIONS:
            raise ValueError(f"unknown trace decision: {self.decision}")
        if self.boundary_type not in BOUNDARY_TYPES:
            raise ValueError(f"unknown trace boundary_type: {self.boundary_type}")
        if self.raw_inputs_in_trace:
            raise ValueError("safe trace metadata must not include raw inputs by default")
        if not self.model_visible_trace_sanitized:
            raise ValueError("model-visible trace metadata must remain sanitized")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentFuseEvidenceRecord:
    """Small combined evidence record for one guarded tool-call proposal."""

    record_id: str
    schema_version: str
    policy_resolution: PolicyResolutionEvidence
    boundary_decision: LayeredBoundaryDecision
    trace_metadata: SafeTraceMetadata
    non_execution: NonExecutionEvidence | None = None

    def __post_init__(self) -> None:
        _ensure_non_empty_string(self.record_id, "record_id")
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
        if self.boundary_decision.decision in {"block", "escalate"} and self.non_execution is None:
            raise ValueError("blocked or escalated calls require non-execution evidence")
        if self.boundary_decision.decision == "allow" and self.non_execution is not None:
            raise ValueError("allowed records must not include non-execution evidence")
        if self.boundary_decision.decision != self.trace_metadata.decision:
            raise ValueError("boundary decision must match trace decision")
        if self.boundary_decision.boundary_type != self.trace_metadata.boundary_type:
            raise ValueError("boundary type must match trace boundary type")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def safe_read_only_summary_evidence() -> AgentFuseEvidenceRecord:
    """Create a deterministic allow evidence example for a read-only summary tool."""

    policy = PolicyResolutionEvidence(
        policy_resolution_outcome="resolved",
        match_stage="capability",
        matched_policy_key="capability:local_read_only_summary",
        match_kind="capability",
        priority=100,
        candidate_policy_keys=["capability:local_read_only_summary"],
        fallback_reason=None,
    )
    boundary = LayeredBoundaryDecision(
        boundary_type="call",
        decision="allow",
        policy_id="policy-safe-read-only-summary",
        policy_hash="sha256:safe-read-only-summary-v0",
        reason_code="release_candidate",
        decisive_gate=True,
    )
    trace = SafeTraceMetadata(
        tool_name="safe_read_only_summary_tool",
        decision="allow",
        policy_id=boundary.policy_id,
        policy_hash=boundary.policy_hash,
        reason_code=boundary.reason_code,
        boundary_type=boundary.boundary_type,
        args_hash="sha256:inert-summary-args",
        evidence_ref="evidence:safe-read-only-summary:001",
    )
    return AgentFuseEvidenceRecord(
        record_id="agentfuse-evidence-safe-read-only-summary-001",
        schema_version=SCHEMA_VERSION,
        policy_resolution=policy,
        boundary_decision=boundary,
        trace_metadata=trace,
    )


def sql_mutation_block_evidence() -> AgentFuseEvidenceRecord:
    """Create deterministic block evidence for a SQL mutation proposal."""

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
        evidence_ref="evidence:sql-mutation-block:001",
    )
    non_execution = NonExecutionEvidence(
        status="not_executed",
        reason="policy_denied",
        execution="not_started",
        payload_executed=False,
        tool_failure=False,
        side_effect_occurred=False,
        approval_id="approval:sql-mutation:block:001",
        call_id="call:dangerous_sql_mutation_tool:001",
        result_ref="result:not_executed:sql-mutation:001",
    )
    return AgentFuseEvidenceRecord(
        record_id="agentfuse-evidence-sql-mutation-block-001",
        schema_version=SCHEMA_VERSION,
        policy_resolution=policy,
        boundary_decision=boundary,
        trace_metadata=trace,
        non_execution=non_execution,
    )


def ambiguous_pattern_overlap_evidence() -> AgentFuseEvidenceRecord:
    """Create deterministic fail-closed evidence for ambiguous pattern overlap."""

    policy = PolicyResolutionEvidence(
        policy_resolution_outcome="ambiguous",
        match_stage="pattern",
        matched_policy_key=None,
        match_kind="glob",
        priority=None,
        candidate_policy_keys=["glob:sql_*", "glob:*_mutation_tool"],
        fallback_reason="multiple_matches_failed_tie_break",
    )
    boundary = LayeredBoundaryDecision(
        boundary_type="call",
        decision="block",
        policy_id="policy-ambiguous-pattern-overlap",
        policy_hash="sha256:ambiguous-pattern-overlap-v0",
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
        evidence_ref="evidence:ambiguous-pattern-overlap:001",
    )
    non_execution = NonExecutionEvidence(
        status="not_executed",
        reason="ambiguous_policy",
        execution="not_started",
        payload_executed=False,
        tool_failure=False,
        side_effect_occurred=False,
        approval_id="approval:ambiguous-pattern:block:001",
        call_id="call:ambiguous_policy_tool:001",
        result_ref="result:not_executed:ambiguous-pattern:001",
    )
    return AgentFuseEvidenceRecord(
        record_id="agentfuse-evidence-ambiguous-pattern-overlap-001",
        schema_version=SCHEMA_VERSION,
        policy_resolution=policy,
        boundary_decision=boundary,
        trace_metadata=trace,
        non_execution=non_execution,
    )


def mcp_file_network_boundary_evidence() -> AgentFuseEvidenceRecord:
    """Create deterministic layered evidence for an MCP-style file/network tool."""

    policy = PolicyResolutionEvidence(
        policy_resolution_outcome="resolved",
        match_stage="capability",
        matched_policy_key="capability:mcp_file_network_restricted",
        match_kind="capability",
        priority=50,
        candidate_policy_keys=["capability:mcp_file_network_restricted"],
        fallback_reason=None,
    )
    boundary = LayeredBoundaryDecision(
        boundary_type="call",
        decision="block",
        policy_id="policy-mcp-file-network-boundary",
        policy_hash="sha256:mcp-file-network-boundary-v0",
        reason_code="policy_denied",
        decisive_gate=True,
    )
    trace = SafeTraceMetadata(
        tool_name="mcp_file_network_tool",
        decision="block",
        policy_id=boundary.policy_id,
        policy_hash=boundary.policy_hash,
        reason_code=boundary.reason_code,
        boundary_type=boundary.boundary_type,
        args_hash="sha256:redacted-mcp-file-network-args",
        evidence_ref="evidence:mcp-file-network-boundary:001",
    )
    non_execution = NonExecutionEvidence(
        status="not_executed",
        reason="policy_denied",
        execution="not_started",
        payload_executed=False,
        tool_failure=False,
        side_effect_occurred=False,
        approval_id="approval:mcp-file-network:block:001",
        call_id="call:mcp_file_network_tool:001",
        result_ref="result:not_executed:mcp-file-network:001",
    )
    return AgentFuseEvidenceRecord(
        record_id="agentfuse-evidence-mcp-file-network-boundary-001",
        schema_version=SCHEMA_VERSION,
        policy_resolution=policy,
        boundary_decision=boundary,
        trace_metadata=trace,
        non_execution=non_execution,
    )


def example_evidence_records() -> list[dict[str, Any]]:
    """Return deterministic JSON-serializable examples for documentation/tests."""

    return [
        safe_read_only_summary_evidence().to_dict(),
        sql_mutation_block_evidence().to_dict(),
        ambiguous_pattern_overlap_evidence().to_dict(),
        mcp_file_network_boundary_evidence().to_dict(),
    ]
