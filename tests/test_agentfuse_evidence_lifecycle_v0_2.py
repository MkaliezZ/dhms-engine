"""Tests for AgentFuse Evidence Lifecycle Schema v0.2."""

from __future__ import annotations

from dataclasses import replace

import pytest

from dhms_agentfuse import (
    BLOCK_STAGES,
    DISPATCH_STATES,
    EXECUTION_LIFECYCLE_STATES,
    LIFECYCLE_SCHEMA_VERSION,
    SIDE_EFFECT_STATES,
    AgentFuseEvidenceRecord,
    ExecutionLifecycleEvidence,
    LifecycleEvidenceRecord,
    NonExecutionEvidence,
    ambiguous_post_dispatch_lifecycle_evidence,
    is_strict_pre_dispatch,
    lifecycle_example_records,
    partial_execution_denial_lifecycle_evidence,
    post_dispatch_denial_race_lifecycle_evidence,
    pre_dispatch_policy_denial_lifecycle_evidence,
    sql_mutation_block_evidence,
)
from dhms_agentfuse.evidence_lifecycle import (
    ExecutionLifecycleEvidence as ModuleExecutionLifecycleEvidence,
)


def test_v01_strict_pre_dispatch_denial_remains_valid():
    record = pre_dispatch_policy_denial_lifecycle_evidence()

    assert record.boundary_decision.decision == "block"
    assert record.lifecycle.block_stage == "pre_dispatch"
    assert record.lifecycle.dispatch_state == "not_started"
    assert record.lifecycle.execution_state == "not_executed"
    assert record.lifecycle.side_effect_state == "proven_none"
    assert is_strict_pre_dispatch(record.lifecycle)
    assert record.non_execution is not None
    assert record.non_execution.execution == "not_started"
    assert record.non_execution.payload_executed is False
    assert record.non_execution.side_effect_occurred is False


def test_v01_strict_non_execution_evidence_still_accepts_valid_records():
    denial = NonExecutionEvidence(
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

    assert denial.status == "not_executed"
    assert denial.execution == "not_started"


def test_v01_serialization_shape_unchanged():
    record = sql_mutation_block_evidence()
    serialized = record.to_dict()

    assert serialized["schema_version"] == "agentfuse-evidence-schema-v0.1"
    assert set(serialized.keys()) == {
        "record_id",
        "schema_version",
        "policy_resolution",
        "boundary_decision",
        "trace_metadata",
        "non_execution",
    }
    assert serialized["non_execution"]["side_effect_occurred"] is False
    assert serialized["non_execution"]["payload_executed"] is False
    assert serialized["non_execution"]["execution"] == "not_started"


def test_v01_invalid_records_remain_invalid():
    with pytest.raises(ValueError, match="side_effect_occurred=False"):
        NonExecutionEvidence(
            status="not_executed",
            reason="policy_denied",
            execution="not_started",
            payload_executed=False,
            tool_failure=False,
            side_effect_occurred=True,
            approval_id="approval:test:001",
            call_id="call:test:001",
            result_ref="result:not_executed:test:001",
        )

    with pytest.raises(ValueError, match="unknown execution state"):
        NonExecutionEvidence(
            status="not_executed",
            reason="policy_denied",
            execution="started",
            payload_executed=False,
            tool_failure=False,
            side_effect_occurred=False,
            approval_id="approval:test:001",
            call_id="call:test:001",
            result_ref="result:not_executed:test:001",
        )


def test_v01_public_imports_remain_available():
    import dhms_agentfuse

    for symbol in (
        "AgentFuseEvidenceRecord",
        "NonExecutionEvidence",
        "PolicyResolutionEvidence",
        "LayeredBoundaryDecision",
        "SafeTraceMetadata",
        "example_evidence_records",
    ):
        assert hasattr(dhms_agentfuse, symbol)


def test_claude_77185_denial_race_is_representable_without_false_non_execution():
    record = post_dispatch_denial_race_lifecycle_evidence()

    assert record.boundary_decision.decision == "block"
    assert record.lifecycle.block_stage == "post_dispatch"
    assert record.lifecycle.dispatch_state == "started"
    assert record.lifecycle.execution_state == "executed"
    assert record.lifecycle.side_effect_state == "observed"
    assert record.non_execution is None
    assert not is_strict_pre_dispatch(record.lifecycle)


def test_ambiguous_post_dispatch_state_remains_uncertainty():
    record = ambiguous_post_dispatch_lifecycle_evidence()

    assert record.boundary_decision.decision == "block"
    assert record.lifecycle.block_stage == "unknown"
    assert record.lifecycle.dispatch_state == "unknown"
    assert record.lifecycle.execution_state == "unknown"
    assert record.lifecycle.side_effect_state == "unknown"
    assert record.non_execution is None
    assert record.to_dict()["lifecycle"] == {
        "block_stage": "unknown",
        "dispatch_state": "unknown",
        "execution_state": "unknown",
        "side_effect_state": "unknown",
    }


def test_unknown_states_are_not_coerced_into_proof_values():
    for state in ("dispatch_state", "execution_state", "side_effect_state", "block_stage"):
        assert "unknown" in {
            "block_stage": BLOCK_STAGES,
            "dispatch_state": DISPATCH_STATES,
            "execution_state": EXECUTION_LIFECYCLE_STATES,
            "side_effect_state": SIDE_EFFECT_STATES,
        }[state]

    lifecycle = ExecutionLifecycleEvidence(
        block_stage="unknown",
        dispatch_state="unknown",
        execution_state="unknown",
        side_effect_state="unknown",
    )

    assert "False" not in str(lifecycle.to_dict().values())
    assert set(lifecycle.to_dict().values()) == {"unknown"}


def test_partial_execution_with_possible_side_effect_is_not_collapsed():
    record = partial_execution_denial_lifecycle_evidence()

    assert record.lifecycle.dispatch_state == "started"
    assert record.lifecycle.execution_state == "partially_executed"
    assert record.lifecycle.side_effect_state == "possible"
    assert record.non_execution is None


def test_contradiction_pre_dispatch_block_with_started_dispatch_is_rejected():
    with pytest.raises(ValueError, match="pre_dispatch block requires dispatch_state"):
        ExecutionLifecycleEvidence(
            block_stage="pre_dispatch",
            dispatch_state="started",
            execution_state="not_executed",
            side_effect_state="proven_none",
        )


def test_contradiction_executed_with_not_started_dispatch_is_rejected():
    with pytest.raises(ValueError, match="incompatible with dispatch_state='not_started'"):
        ExecutionLifecycleEvidence(
            block_stage="post_dispatch",
            dispatch_state="not_started",
            execution_state="executed",
            side_effect_state="observed",
        )


def test_contradiction_observed_side_effect_with_pre_dispatch_block_is_rejected():
    with pytest.raises(ValueError, match="pre_dispatch block requires side_effect_state"):
        ExecutionLifecycleEvidence(
            block_stage="pre_dispatch",
            dispatch_state="not_started",
            execution_state="not_executed",
            side_effect_state="observed",
        )


def test_contradiction_partially_executed_with_not_started_dispatch_is_rejected():
    with pytest.raises(ValueError, match="incompatible with dispatch_state='not_started'"):
        ExecutionLifecycleEvidence(
            block_stage="unknown",
            dispatch_state="not_started",
            execution_state="partially_executed",
            side_effect_state="possible",
        )


def test_unknown_state_values_outside_canonical_sets_are_rejected():
    with pytest.raises(ValueError, match="unknown block_stage"):
        ExecutionLifecycleEvidence(
            block_stage="mid_dispatch",
            dispatch_state="unknown",
            execution_state="unknown",
            side_effect_state="unknown",
        )

    with pytest.raises(ValueError, match="unknown side_effect_state"):
        ExecutionLifecycleEvidence(
            block_stage="unknown",
            dispatch_state="unknown",
            execution_state="unknown",
            side_effect_state="none",
        )


def test_combined_record_rejects_non_execution_outside_strict_pre_dispatch():
    race = post_dispatch_denial_race_lifecycle_evidence()
    strict_denial = pre_dispatch_policy_denial_lifecycle_evidence()

    with pytest.raises(ValueError, match="strict pre_dispatch lifecycle evidence"):
        LifecycleEvidenceRecord(
            record_id="agentfuse-evidence-lifecycle-contradiction-001",
            schema_version=LIFECYCLE_SCHEMA_VERSION,
            policy_resolution=race.policy_resolution,
            boundary_decision=race.boundary_decision,
            trace_metadata=race.trace_metadata,
            lifecycle=race.lifecycle,
            non_execution=strict_denial.non_execution,
        )


def test_combined_record_requires_non_execution_for_strict_pre_dispatch_block():
    strict = pre_dispatch_policy_denial_lifecycle_evidence()

    with pytest.raises(ValueError, match="require non-execution evidence"):
        LifecycleEvidenceRecord(
            record_id="agentfuse-evidence-lifecycle-contradiction-002",
            schema_version=LIFECYCLE_SCHEMA_VERSION,
            policy_resolution=strict.policy_resolution,
            boundary_decision=strict.boundary_decision,
            trace_metadata=strict.trace_metadata,
            lifecycle=strict.lifecycle,
        )


def test_combined_record_rejects_allow_with_non_execution_evidence():
    strict = pre_dispatch_policy_denial_lifecycle_evidence()
    allow_boundary = replace(strict.boundary_decision, decision="allow")
    allow_trace = replace(strict.trace_metadata, decision="allow")

    with pytest.raises(ValueError, match="must not include non-execution evidence"):
        LifecycleEvidenceRecord(
            record_id="agentfuse-evidence-lifecycle-contradiction-003",
            schema_version=LIFECYCLE_SCHEMA_VERSION,
            policy_resolution=strict.policy_resolution,
            boundary_decision=allow_boundary,
            trace_metadata=allow_trace,
            lifecycle=strict.lifecycle,
            non_execution=strict.non_execution,
        )


def test_lifecycle_examples_are_deterministic_and_json_serializable():
    examples = lifecycle_example_records()

    assert [example["schema_version"] for example in examples] == [
        LIFECYCLE_SCHEMA_VERSION,
        LIFECYCLE_SCHEMA_VERSION,
        LIFECYCLE_SCHEMA_VERSION,
        LIFECYCLE_SCHEMA_VERSION,
    ]
    assert [example["record_id"] for example in examples] == [
        "agentfuse-evidence-lifecycle-pre-dispatch-denial-001",
        "agentfuse-evidence-lifecycle-post-dispatch-denial-race-001",
        "agentfuse-evidence-lifecycle-ambiguous-post-dispatch-001",
        "agentfuse-evidence-lifecycle-partial-execution-denial-001",
    ]
    assert examples == lifecycle_example_records()


def test_module_reexports_reference_the_same_class():
    assert ModuleExecutionLifecycleEvidence is ExecutionLifecycleEvidence
