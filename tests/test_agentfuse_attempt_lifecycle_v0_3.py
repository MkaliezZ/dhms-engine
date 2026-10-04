"""Attempt correlation and exact redacted artifact mapping, without runtime replay."""

from dataclasses import FrozenInstanceError, replace
from copy import deepcopy
import hashlib
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


# Exact external issue #15 replay. The SHA-256 was computed from the sole JSON
# block fetched from the issue body, not from our earlier comment-derived fixture.
ISSUE15_FIXTURE_PATH = Path(__file__).parent / "fixtures/attempt_lifecycle_v0_3_external_issue_15.json"
ISSUE15_ARTIFACT_SHA256 = "7fd524dd3910c77da89f1376f40b1b89d7f5d2e96980512b5621ded25386dd41"


@pytest.fixture
def issue15_artifact():
    return json.loads(ISSUE15_FIXTURE_PATH.read_text(encoding="utf-8"))


def _map_issue15_attempts(artifact):
    """Test-local projection of exact source facts, without host operations.

    Local record IDs label the mapping output. Source-native decision, runtime,
    receiver and rejection metadata stay in the external fixture. In particular,
    no v0.1 NonExecutionEvidence metadata are synthesized.
    """

    return tuple(
        AttemptLifecycleEvidenceRecord(
            record_id=f"fixture:external-issue-15:{attempt['attempt_ref']}",
            schema_version=ATTEMPT_LIFECYCLE_SCHEMA_VERSION,
            logical_action_ref=artifact["logical_action_ref"],
            attempt_ref=attempt["attempt_ref"],
            lifecycle=ExecutionLifecycleEvidence(
                block_stage="unknown" if attempt["block_stage"] == "none" else attempt["block_stage"],
                dispatch_state=attempt["dispatch_state"],
                execution_state=attempt["execution_state"],
                side_effect_state=attempt["side_effect_state"],
            ),
            non_execution=None,
        )
        for attempt in artifact["attempts"]
    )


@pytest.fixture
def issue15_records(issue15_artifact):
    return _map_issue15_attempts(issue15_artifact)


def test_issue15_fixture_matches_exact_fetched_json_block():
    raw = ISSUE15_FIXTURE_PATH.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == ISSUE15_ARTIFACT_SHA256
    assert raw.endswith(b"\n")


def test_issue15_external_schema_context_and_redactions_are_preserved(issue15_artifact):
    assert issue15_artifact["schema"] == "shadow.redacted-attempt-trace.v1"
    assert issue15_artifact["source_context"] == "crewAIInc/crewAI#5802"
    assert issue15_artifact["redactions"] == [
        "filesystem paths", "credentials", "host identifiers", "unrelated ledger entries"
    ]
    assert set(issue15_artifact) == {
        "schema", "logical_action_ref", "source_context", "attempts",
        "derived_host_policy", "redactions",
    }


def test_issue15_two_distinct_attempt_refs_and_logical_action_are_preserved(issue15_artifact, issue15_records):
    assert issue15_artifact["logical_action_ref"] == "agent-contracts-reality-pilot-001"
    assert len(issue15_artifact["attempts"]) == len(issue15_records) == 2
    assert [record.attempt_ref for record in issue15_records] == [
        attempt["attempt_ref"] for attempt in issue15_artifact["attempts"]
    ]
    assert issue15_records[0].attempt_ref != issue15_records[1].attempt_ref
    assert all(
        record.logical_action_ref == issue15_artifact["logical_action_ref"]
        for record in issue15_records
    )


def test_issue15_original_none_stage_maps_to_unknown_without_denial_or_success(issue15_artifact, issue15_records):
    source = issue15_artifact["attempts"][0]
    original = issue15_records[0]
    assert source["policy_decision"] == "allow"
    assert source["block_stage"] == "none"
    assert original.lifecycle.to_dict() == {
        "block_stage": "unknown",
        "dispatch_state": "started",
        "execution_state": "unknown",
        "side_effect_state": "observed",
    }
    assert original.non_execution is None
    assert not is_strict_pre_dispatch(original.lifecycle)
    assert "boundary_decision" not in original.to_dict()


def test_issue15_blocked_retry_maps_to_strict_lifecycle_without_v01_metadata(issue15_artifact, issue15_records):
    source = issue15_artifact["attempts"][1]
    retry = issue15_records[1]
    assert source["policy_decision"] == "deny"
    assert retry.lifecycle.to_dict() == {
        "block_stage": "pre_dispatch",
        "dispatch_state": "not_started",
        "execution_state": "not_executed",
        "side_effect_state": "proven_none",
    }
    assert is_strict_pre_dispatch(retry.lifecycle)
    assert retry.non_execution is None


def test_issue15_mapping_preserves_all_other_lifecycle_values_exactly(issue15_artifact, issue15_records):
    for source, record in zip(issue15_artifact["attempts"], issue15_records):
        for field in ("dispatch_state", "execution_state", "side_effect_state"):
            assert getattr(record.lifecycle, field) == source[field]
        expected_stage = "unknown" if source["block_stage"] == "none" else source["block_stage"]
        assert record.lifecycle.block_stage == expected_stage


def test_issue15_host_native_rejection_is_not_fabricated_into_agentfuse_denial(issue15_artifact, issue15_records):
    native = issue15_artifact["attempts"][1]["non_execution_evidence"]
    assert native == {
        "reason": "ACTION_ALREADY_RECORDED",
        "receiver_effect_count_before": 1,
        "receiver_effect_count_after": 1,
    }
    for record in issue15_records:
        serialized = record.to_dict()
        assert serialized["non_execution"] is None
        assert not {"approval_id", "call_id", "result_ref", "reason", "policy_decision"} & serialized.keys()
        assert "policy_denied" not in json.dumps(serialized)


def test_issue15_receiver_source_evidence_belongs_only_to_original_attempt(issue15_artifact, issue15_records):
    original_source, retry_source = issue15_artifact["attempts"]
    assert original_source["attempt_ref"] == "agent-contracts-reality-pilot-001:attempt:1"
    assert original_source["receiver_evidence"] == {
        "effect_count": 1,
        "effect_key": "agent-contracts-reality-pilot-001",
    }
    assert "receiver_evidence" not in retry_source
    for record in issue15_records:
        assert "receiver_evidence" not in record.to_dict()
    assert issue15_records[0].lifecycle.side_effect_state == "observed"
    assert issue15_records[1].lifecycle.side_effect_state == "proven_none"


def test_issue15_runtime_source_facts_do_not_become_execution_success(issue15_artifact, issue15_records):
    assert issue15_artifact["attempts"][0]["runtime_evidence"] == {
        "recovered_status": "UNKNOWN",
        "reconciliation_required": True,
        "terminal_acknowledgement": "lost_after_receiver_commit",
    }
    assert issue15_records[0].lifecycle.execution_state == "unknown"
    assert issue15_records[0].lifecycle.execution_state != "executed"
    assert all("runtime_evidence" not in record.to_dict() for record in issue15_records)


def test_issue15_correlation_keeps_two_intact_records_in_one_action(issue15_artifact, issue15_records):
    groups = correlate_attempt_lifecycle_records(issue15_records)
    assert tuple(groups) == (issue15_artifact["logical_action_ref"],)
    correlated = groups[issue15_artifact["logical_action_ref"]]
    assert len(correlated) == 2
    assert correlated[0] is issue15_records[0]
    assert correlated[1] is issue15_records[1]


def test_issue15_retry_proven_none_does_not_erase_or_inherit_original_effect(issue15_artifact, issue15_records):
    before = tuple(record.to_dict() for record in issue15_records)
    correlated = correlate_attempt_lifecycle_records(issue15_records)[issue15_artifact["logical_action_ref"]]
    assert tuple(record.to_dict() for record in correlated) == before
    assert correlated[0].lifecycle.side_effect_state == "observed"
    assert correlated[0].lifecycle.execution_state == "unknown"
    assert correlated[1].lifecycle.side_effect_state == "proven_none"
    assert correlated[1].lifecycle.execution_state == "not_executed"
    assert correlated[0].non_execution is correlated[1].non_execution is None


def test_issue15_derived_reconciliation_policy_remains_host_source_only(issue15_artifact, issue15_records):
    assert issue15_artifact["derived_host_policy"] == {
        "decision": "reconcile_do_not_redispatch",
        "reason": "a prior attempt has observed receiver-side effect evidence while runtime completion remains unknown",
    }
    # The first attempt fails the necessary evidence condition for redispatch;
    # neither the projection nor AgentFuse performs the host's reconciliation.
    assert not all(is_strict_pre_dispatch(record.lifecycle) for record in issue15_records)
    serialized = json.dumps([record.to_dict() for record in issue15_records])
    assert "reconcile_do_not_redispatch" not in serialized
    assert "derived_host_policy" not in serialized


def test_issue15_pure_mapping_never_rewrites_external_artifact(issue15_artifact):
    snapshot = deepcopy(issue15_artifact)
    first = _map_issue15_attempts(issue15_artifact)
    second = _map_issue15_attempts(issue15_artifact)
    assert issue15_artifact == snapshot
    assert first == second
    assert first[0] is not second[0]
    assert issue15_artifact["attempts"][0]["block_stage"] == "none"


def test_issue15_projection_has_only_existing_record_fields_and_no_operations(issue15_records):
    for record in issue15_records:
        assert set(record.to_dict()) == {
            "record_id", "schema_version", "logical_action_ref", "attempt_ref",
            "lifecycle", "non_execution",
        }
        for operation in ("retry", "redispatch", "reconcile", "should_retry"):
            assert not hasattr(record, operation)
