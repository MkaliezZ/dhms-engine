"""Focused contract tests for the per-call denial lifecycle trial demo."""

from __future__ import annotations

import json

from examples.trial.per_call_denial_lifecycle_demo import (
    ALLOWED_CALL_ID,
    ALLOWED_TOOL_NAME,
    DENIED_CALL_ID,
    DENIED_TOOL_NAME,
    _RAW_SENSITIVE_PAYLOAD,
    run_demo,
)


def _records_by_name() -> dict[str, dict[str, object]]:
    return {
        record["tool_name"]: record
        for record in run_demo()["terminal_lifecycle_records"]
    }


def test_allowed_handler_executes_exactly_once() -> None:
    summary = run_demo()

    assert summary["allowed_handler_execution_count"] == 1
    assert _records_by_name()[ALLOWED_TOOL_NAME]["handler_invoked"] is True


def test_denied_handler_never_executes() -> None:
    summary = run_demo()

    assert summary["denied_handler_execution_count"] == 0
    assert summary["denied_handler_invoked"] is False


def test_denied_terminal_result_references_original_call() -> None:
    record = _records_by_name()[DENIED_TOOL_NAME]

    assert record["terminal"] is True
    assert record["tool_call_id"] == DENIED_CALL_ID
    assert record["tool_name"] == DENIED_TOOL_NAME
    assert record["evidence"]["non_execution"]["call_id"] == DENIED_CALL_ID
    assert record["evidence"]["trace_metadata"]["tool_name"] == DENIED_TOOL_NAME


def test_denial_is_not_an_executed_tool_failure() -> None:
    record = _records_by_name()[DENIED_TOOL_NAME]

    assert record["outcome"] == "not_executed"
    assert record["execution"] == "not_started"
    assert record["tool_failure"] is False


def test_allowed_call_continues_after_denial_in_same_batch() -> None:
    summary = run_demo()
    records = summary["terminal_lifecycle_records"]

    assert [record["tool_name"] for record in records] == [DENIED_TOOL_NAME, ALLOWED_TOOL_NAME]
    assert records[1]["tool_call_id"] == ALLOWED_CALL_ID
    assert summary["remaining_allowed_call_continued"] is True
    assert summary["batch_completed"] is True


def test_default_output_excludes_raw_sensitive_payload() -> None:
    serialized = json.dumps(run_demo(), sort_keys=True)

    assert _RAW_SENSITIVE_PAYLOAD not in serialized
    assert run_demo()["safe_trace_only"] is True


def test_machine_readable_denial_reason_is_present() -> None:
    record = _records_by_name()[DENIED_TOOL_NAME]

    assert record["reason_code"] == "policy_denied"
    assert record["evidence"]["non_execution"]["reason"] == "policy_denied"


def test_repeated_runs_are_deterministic() -> None:
    first = json.dumps(run_demo(), sort_keys=True)
    second = json.dumps(run_demo(), sort_keys=True)

    assert first == second
