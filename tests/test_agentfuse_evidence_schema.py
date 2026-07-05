"""Tests for AgentFuse Evidence Schema v0.1."""

from __future__ import annotations

import pytest

from dhms_agentfuse.evidence_schema import (
    LayeredBoundaryDecision,
    NonExecutionEvidence,
    PolicyResolutionEvidence,
    SafeTraceMetadata,
    ambiguous_pattern_overlap_evidence,
    mcp_file_network_boundary_evidence,
    safe_read_only_summary_evidence,
    sql_mutation_block_evidence,
)


def _resolved_policy() -> PolicyResolutionEvidence:
    return PolicyResolutionEvidence(
        policy_resolution_outcome="resolved",
        match_stage="exact",
        matched_policy_key="tool:safe_read_only_summary_tool",
        match_kind="exact",
        priority=100,
        candidate_policy_keys=["tool:safe_read_only_summary_tool"],
        fallback_reason=None,
    )


def _policy_denial() -> NonExecutionEvidence:
    return NonExecutionEvidence(
        status="not_executed",
        reason="policy_denied",
        execution="not_started",
        payload_executed=False,
        tool_failure=False,
        side_effect_occurred=False,
        approval_id="approval:test:001",
        call_id="call:test:001",
        result_ref="result:not_executed:test:001",
    )


def test_resolved_policy_resolution_has_no_fallback_reason() -> None:
    policy = _resolved_policy()

    assert policy.policy_resolution_outcome == "resolved"
    assert policy.fallback_reason is None


def test_unresolved_policy_resolution_requires_fallback_reason() -> None:
    with pytest.raises(ValueError, match="fallback_reason"):
        PolicyResolutionEvidence(
            policy_resolution_outcome="no_match",
            match_stage="fallback",
            matched_policy_key=None,
            match_kind="none",
            priority=None,
            candidate_policy_keys=[],
            fallback_reason=None,
        )


def test_ambiguous_policy_resolution_requires_multiple_candidates() -> None:
    with pytest.raises(ValueError, match="at least two"):
        PolicyResolutionEvidence(
            policy_resolution_outcome="ambiguous",
            match_stage="pattern",
            matched_policy_key=None,
            match_kind="glob",
            priority=None,
            candidate_policy_keys=["glob:sql_*"],
            fallback_reason="multiple_matches_failed_tie_break",
        )


def test_ambiguous_without_fallback_reason_is_invalid() -> None:
    with pytest.raises(ValueError, match="fallback_reason"):
        PolicyResolutionEvidence(
            policy_resolution_outcome="ambiguous",
            match_stage="pattern",
            matched_policy_key=None,
            match_kind="regex",
            priority=None,
            candidate_policy_keys=["regex:sql_.*", "regex:.*_mutation_tool"],
            fallback_reason=None,
        )


def test_overlapping_pattern_policies_fail_closed_with_diagnostic() -> None:
    record = ambiguous_pattern_overlap_evidence()

    assert record.policy_resolution.policy_resolution_outcome == "ambiguous"
    assert record.policy_resolution.fallback_reason == "multiple_matches_failed_tie_break"
    assert len(record.policy_resolution.candidate_policy_keys) >= 2
    assert record.boundary_decision.decision == "block"
    assert record.non_execution is not None
    assert record.non_execution.reason == "ambiguous_policy"


def test_policy_denial_is_not_tool_failure() -> None:
    denial = _policy_denial()

    assert denial.reason == "policy_denied"
    assert denial.tool_failure is False


def test_policy_denial_execution_status_is_not_started() -> None:
    denial = _policy_denial()

    assert denial.status == "not_executed"
    assert denial.execution == "not_started"


def test_policy_denial_payload_executed_false() -> None:
    denial = _policy_denial()

    assert denial.payload_executed is False


def test_policy_denial_side_effect_occurred_false() -> None:
    denial = _policy_denial()

    assert denial.side_effect_occurred is False


def test_safe_trace_metadata_excludes_raw_inputs() -> None:
    trace = SafeTraceMetadata(
        tool_name="dangerous_sql_mutation_tool",
        decision="block",
        policy_id="policy:block:sql",
        policy_hash="sha256:block-sql",
        reason_code="policy_denied",
        boundary_type="call",
        args_hash="sha256:redacted-args",
        evidence_ref="evidence:block:sql:001",
    )

    assert trace.raw_inputs_in_trace is False
    assert trace.model_visible_trace_sanitized is True
    with pytest.raises(ValueError, match="raw inputs"):
        SafeTraceMetadata(
            tool_name="dangerous_sql_mutation_tool",
            decision="block",
            policy_id="policy:block:sql",
            policy_hash="sha256:block-sql",
            reason_code="policy_denied",
            boundary_type="call",
            args_hash="sha256:redacted-args",
            evidence_ref="evidence:block:sql:001",
            raw_inputs_in_trace=True,
        )


def test_call_level_boundary_can_be_decisive_gate() -> None:
    decision = LayeredBoundaryDecision(
        boundary_type="call",
        decision="block",
        policy_id="policy:block:call",
        policy_hash="sha256:block-call",
        reason_code="policy_denied",
        decisive_gate=True,
    )

    assert decision.boundary_type == "call"
    assert decision.decisive_gate is True


def test_deterministic_examples_are_json_serializable() -> None:
    examples = [
        safe_read_only_summary_evidence(),
        sql_mutation_block_evidence(),
        ambiguous_pattern_overlap_evidence(),
        mcp_file_network_boundary_evidence(),
    ]

    assert [example.to_dict()["schema_version"] for example in examples] == [
        "agentfuse-evidence-schema-v0.1",
        "agentfuse-evidence-schema-v0.1",
        "agentfuse-evidence-schema-v0.1",
        "agentfuse-evidence-schema-v0.1",
    ]
