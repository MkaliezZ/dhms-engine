"""Attempt correlation and the publicly reported #5802 mapping, not replay."""

from dataclasses import FrozenInstanceError, replace
import itertools
import json
from pathlib import Path

import pytest

from dhms_agentfuse import (
    ATTEMPT_LIFECYCLE_SCHEMA_VERSION,
    BLOCK_STAGES,
    DISPATCH_STATES,
    EXECUTION_LIFECYCLE_STATES,
    LIFECYCLE_SCHEMA_VERSION,
    SIDE_EFFECT_STATES,
    AttemptLifecycleEvidenceRecord,
    ExecutionLifecycleEvidence,
    LifecycleEvidenceRecord,
    correlate_attempt_lifecycle_records,
    is_strict_pre_dispatch,
    pre_dispatch_policy_denial_lifecycle_evidence,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures/attempt_lifecycle_v0_3_external_report.json"
ACTION_REF = "agent-contracts-reality-pilot-001"


@pytest.fixture
def reported_attempts():
    """Only comment-supplied lifecycle facts; no artifact or receiver execution."""

    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return tuple(
        AttemptLifecycleEvidenceRecord(
            **{key: value for key, value in record.items() if key != "lifecycle"},
            lifecycle=ExecutionLifecycleEvidence(**record["lifecycle"]),
        )
        for record in payload["records"]
    )


def test_external_report_fixture_is_not_an_artifact_replay(reported_attempts):
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert payload["source"] == {
        "discussion_url": "https://github.com/crewAIInc/crewAI/issues/6221#issuecomment-5975614702",
        "reporter": "impartshadow",
        "retained_artifact_issue": "crewAIInc/crewAI#5802",
        "external_reported_trace_fixture": True,
        "real_external_trace_mapping_reported": True,
        "independent_artifact_replay": False,
    }
    assert [record.to_dict() for record in reported_attempts] == payload["records"]


def test_original_host_dispatch_is_representable_without_policy_denial(reported_attempts):
    original, _ = reported_attempts
    assert original.lifecycle.to_dict() == {
        "block_stage": "unknown",
        "dispatch_state": "started",
        "execution_state": "unknown",
        "side_effect_state": "observed",
    }
    assert original.non_execution is None
    assert "boundary_decision" not in original.to_dict()
    assert not is_strict_pre_dispatch(original.lifecycle)


def test_blocked_retry_is_independently_strict(reported_attempts):
    _, retry = reported_attempts
    assert retry.lifecycle.to_dict() == {
        "block_stage": "pre_dispatch",
        "dispatch_state": "not_started",
        "execution_state": "not_executed",
        "side_effect_state": "proven_none",
    }
    assert is_strict_pre_dispatch(retry.lifecycle)


def test_strict_retry_may_carry_non_execution_evidence(reported_attempts):
    # This denial metadata is a synthetic v0.2 example, NOT external #5802 data.
    synthetic_denial = pre_dispatch_policy_denial_lifecycle_evidence().non_execution
    _, retry = reported_attempts
    record = replace(retry, record_id="synthetic:strict-retry", non_execution=synthetic_denial)
    assert record.non_execution is synthetic_denial
    assert record.to_dict()["non_execution"] == synthetic_denial.to_dict()


def test_original_must_not_receive_retry_non_execution_evidence(reported_attempts):
    original, _ = reported_attempts
    synthetic_denial = pre_dispatch_policy_denial_lifecycle_evidence().non_execution
    with pytest.raises(ValueError, match="strict pre_dispatch"):
        replace(original, non_execution=synthetic_denial)


def test_two_attempts_correlate_without_merging_evidence(reported_attempts):
    original, retry = reported_attempts
    groups = correlate_attempt_lifecycle_records(reported_attempts)
    assert tuple(groups) == (ACTION_REF,)
    assert groups[ACTION_REF] == (original, retry)
    assert groups[ACTION_REF][0] is original
    assert groups[ACTION_REF][1] is retry
    assert original.attempt_ref == f"{ACTION_REF}:attempt:1"
    assert retry.attempt_ref == f"{ACTION_REF}:attempt:2"
    assert original.attempt_ref != retry.attempt_ref
    assert original.lifecycle.side_effect_state == "observed"
    assert retry.lifecycle.side_effect_state == "proven_none"
    assert original.lifecycle.execution_state == "unknown"
    assert retry.lifecycle.execution_state == "not_executed"


def test_correlation_does_not_infer_chronology_or_recovery(reported_attempts):
    original, retry = reported_attempts
    groups = correlate_attempt_lifecycle_records(iter((retry, original)))
    assert groups[ACTION_REF] == (retry, original)
    assert original.lifecycle.execution_state == "unknown"


@pytest.mark.parametrize("different_action", [False, True])
def test_duplicate_attempt_ref_is_rejected_even_across_actions(reported_attempts, different_action):
    original, retry = reported_attempts
    duplicate = replace(
        retry,
        attempt_ref=original.attempt_ref,
        logical_action_ref="another-action" if different_action else ACTION_REF,
    )
    with pytest.raises(ValueError, match="duplicate attempt_ref"):
        correlate_attempt_lifecycle_records((original, duplicate))


def test_duplicate_input_is_not_silently_deduplicated(reported_attempts):
    original, _ = reported_attempts
    with pytest.raises(ValueError, match="duplicate attempt_ref"):
        correlate_attempt_lifecycle_records((original, original))


def test_multiple_actions_and_future_attempts_keep_independent_records(reported_attempts):
    original, retry = reported_attempts
    future = replace(retry, record_id="future", attempt_ref=f"{ACTION_REF}:attempt:3")
    other = replace(original, record_id="other", logical_action_ref="other", attempt_ref="other:1")
    groups = correlate_attempt_lifecycle_records((original, other, retry, future))
    assert groups[ACTION_REF] == (original, retry, future)
    assert groups["other"] == (other,)
    assert correlate_attempt_lifecycle_records(()) == {}


def test_evidence_is_immutable_and_serialization_cannot_contaminate_siblings(reported_attempts):
    original, retry = reported_attempts
    with pytest.raises(FrozenInstanceError):
        retry.lifecycle = original.lifecycle
    with pytest.raises(FrozenInstanceError):
        retry.lifecycle.side_effect_state = "observed"
    serialized = original.to_dict()
    serialized["lifecycle"]["side_effect_state"] = "proven_none"
    assert original.lifecycle.side_effect_state == "observed"
    assert retry.lifecycle.side_effect_state == "proven_none"
    assert retry.non_execution is None


def test_copying_observed_side_effect_into_strict_retry_is_rejected(reported_attempts):
    original, retry = reported_attempts
    with pytest.raises(ValueError, match="pre_dispatch block requires side_effect_state"):
        replace(retry.lifecycle, side_effect_state=original.lifecycle.side_effect_state)


@pytest.mark.parametrize("effect", ["observed", "possible", "unknown"])
def test_non_strict_prior_evidence_does_not_license_automatic_redispatch(reported_attempts, effect):
    original, retry = reported_attempts
    prior = replace(original, lifecycle=replace(original.lifecycle, side_effect_state=effect))
    records = correlate_attempt_lifecycle_records((prior, retry))[ACTION_REF]
    # A host may use this necessary evidence condition; it is not a retry instruction.
    assert not all(is_strict_pre_dispatch(record.lifecycle) for record in records)
    assert prior.lifecycle.execution_state == "unknown"


def test_strict_prior_evidence_is_only_a_potential_host_retry_precondition(reported_attempts):
    _, retry = reported_attempts
    assert all(is_strict_pre_dispatch(record.lifecycle) for record in (retry,))
    # The envelope/correlation result contains no retry permission or operation.
    assert set(retry.to_dict()) == {
        "record_id", "schema_version", "logical_action_ref", "attempt_ref",
        "lifecycle", "non_execution",
    }


def test_unknown_and_observed_are_not_converted_to_execution_success(reported_attempts):
    original, _ = reported_attempts
    serialized = correlate_attempt_lifecycle_records(reported_attempts)[ACTION_REF][0].to_dict()
    assert serialized["lifecycle"]["execution_state"] == "unknown"
    assert serialized["lifecycle"]["side_effect_state"] == "observed"
    assert serialized["lifecycle"]["execution_state"] not in {"not_executed", "executed"}


def test_unknown_dispatch_and_side_effect_remain_unknown(reported_attempts):
    original, _ = reported_attempts
    unknown = replace(original, lifecycle=ExecutionLifecycleEvidence("unknown", "unknown", "unknown", "unknown"))
    assert set(unknown.to_dict()["lifecycle"].values()) == {"unknown"}
    assert unknown.non_execution is None


def test_collection_uniqueness_is_not_a_global_exactly_once_ledger(reported_attempts):
    first = correlate_attempt_lifecycle_records(reported_attempts)
    second = correlate_attempt_lifecycle_records(reported_attempts)
    assert first == second
    assert first is not second
    assert second[ACTION_REF][0].lifecycle.execution_state == "unknown"


def test_non_execution_attachment_boundary_across_all_valid_lifecycle_states(reported_attempts):
    original, _ = reported_attempts
    synthetic_denial = pre_dispatch_policy_denial_lifecycle_evidence().non_execution
    accepted = 0
    rejected = 0
    for states in itertools.product(
        BLOCK_STAGES, DISPATCH_STATES, EXECUTION_LIFECYCLE_STATES, SIDE_EFFECT_STATES
    ):
        try:
            lifecycle = ExecutionLifecycleEvidence(*states)
        except ValueError:
            continue
        strict = states == ("pre_dispatch", "not_started", "not_executed", "proven_none")
        if strict:
            record = replace(original, lifecycle=lifecycle, non_execution=synthetic_denial)
            assert record.non_execution is synthetic_denial
            accepted += 1
        else:
            with pytest.raises(ValueError, match="strict pre_dispatch"):
                replace(original, lifecycle=lifecycle, non_execution=synthetic_denial)
            rejected += 1
    assert accepted == 1
    assert rejected > 0


@pytest.mark.parametrize("field_name", ["record_id", "logical_action_ref", "attempt_ref"])
@pytest.mark.parametrize("invalid", ["", " ", None, 123])
def test_attempt_identity_requires_nonempty_strings(reported_attempts, field_name, invalid):
    with pytest.raises(ValueError, match=field_name):
        replace(reported_attempts[0], **{field_name: invalid})


def test_attempt_schema_version_is_separate_from_existing_v02(reported_attempts):
    assert LIFECYCLE_SCHEMA_VERSION == "agentfuse-evidence-lifecycle-schema-v0.2"
    with pytest.raises(ValueError, match="schema_version"):
        replace(reported_attempts[0], schema_version=LIFECYCLE_SCHEMA_VERSION)


def test_unvalidated_evidence_and_non_attempt_collection_members_are_rejected(reported_attempts):
    original, _ = reported_attempts
    with pytest.raises(ValueError, match="lifecycle must be"):
        replace(original, lifecycle=original.lifecycle.to_dict())
    with pytest.raises(ValueError, match="non_execution must be"):
        replace(original, non_execution={"status": "not_executed"})
    with pytest.raises(ValueError, match="records must contain"):
        correlate_attempt_lifecycle_records((original.to_dict(),))


def test_existing_denial_record_still_rejects_allow(reported_attempts):
    denial = pre_dispatch_policy_denial_lifecycle_evidence()
    assert isinstance(denial, LifecycleEvidenceRecord)
    assert denial.schema_version == LIFECYCLE_SCHEMA_VERSION
    assert denial.boundary_decision.decision == "block"
    assert denial.non_execution is not None
    with pytest.raises(ValueError, match="denial-like"):
        replace(
            denial,
            boundary_decision=replace(denial.boundary_decision, decision="allow"),
            trace_metadata=replace(denial.trace_metadata, decision="allow"),
            lifecycle=reported_attempts[0].lifecycle,
            non_execution=None,
        )
