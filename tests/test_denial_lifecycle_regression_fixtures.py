"""Focused contract checks for provider-neutral denial lifecycle fixtures."""

from __future__ import annotations

import json
from pathlib import Path


FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "trial"
    / "denial_lifecycle_regression_fixtures"
    / "fixtures.json"
)


def _load_fixtures() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _scenario(fixture_id: str) -> dict[str, object]:
    return next(
        scenario
        for scenario in _load_fixtures()["scenarios"]
        if scenario["id"] == fixture_id
    )


def _records_by_tool_name(scenario: dict[str, object]) -> dict[str, dict[str, object]]:
    return {record["tool_name"]: record for record in scenario["terminal_records"]}


def test_fixture_file_parses_and_has_exactly_two_approved_scenarios() -> None:
    fixtures = _load_fixtures()

    assert fixtures["provider_neutral"] is True
    assert [scenario["id"] for scenario in fixtures["scenarios"]] == [
        "single_denied_before_execution",
        "mixed_batch_denial_continuation",
    ]


def test_every_requested_call_has_one_terminal_record_with_preserved_identity() -> None:
    for scenario in _load_fixtures()["scenarios"]:
        requested = [
            (request["tool_call_id"], request["tool_name"])
            for request in scenario["requested_calls"]
        ]
        terminal = [
            (record["tool_call_id"], record["tool_name"])
            for record in scenario["terminal_records"]
        ]

        assert len(terminal) == scenario["expectations"]["terminal_record_count"]
        assert set(terminal) == set(requested)
        assert len(terminal) == len(set(terminal))


def test_single_denied_call_is_terminal_non_execution() -> None:
    record = _scenario("single_denied_before_execution")["terminal_records"][0]

    assert record["decision"] == "block"
    assert record["outcome"] == "not_executed"
    assert record["execution"] == "not_started"
    assert record["handler_invoked"] is False
    assert record["handler_execution_count"] == 0
    assert record["payload_executed"] is False
    assert record["side_effect_occurred"] is False
    assert record["tool_failure"] is False
    assert record["reason_code"] == "policy_denied"


def test_mixed_batch_denied_call_is_terminal_non_execution() -> None:
    record = _records_by_tool_name(_scenario("mixed_batch_denial_continuation"))["dangerous_sql_mutation_tool"]

    assert record["decision"] == "block"
    assert record["outcome"] == "not_executed"
    assert record["execution"] == "not_started"
    assert record["handler_invoked"] is False
    assert record["handler_execution_count"] == 0
    assert record["tool_failure"] is False
    assert record["reason_code"] == "policy_denied"


def test_mixed_batch_allowed_call_executes_once() -> None:
    record = _records_by_tool_name(_scenario("mixed_batch_denial_continuation"))["safe_read_only_summary_tool"]

    assert record["decision"] == "allow"
    assert record["outcome"] == "executed"
    assert record["handler_invoked"] is True
    assert record["handler_execution_count"] == 1


def test_denial_does_not_abort_remaining_allowed_call() -> None:
    scenario = _scenario("mixed_batch_denial_continuation")

    assert scenario["requested_calls"][0]["tool_name"] == "dangerous_sql_mutation_tool"
    assert scenario["expectations"]["batch_completed"] is True
    assert scenario["expectations"]["remaining_allowed_call_continued"] is True
    assert scenario["expectations"]["no_orphaned_tool_request"] is True
    assert scenario["expectations"]["denied_side_effect_count"] == 0


def test_fixture_output_contains_safe_trace_metadata_without_protected_payload() -> None:
    serialized = json.dumps(_load_fixtures(), sort_keys=True)

    assert "RAW_SENSITIVE_TRIAL_PAYLOAD_MUST_NOT_APPEAR" not in serialized
    assert '"payload"' not in serialized
    for scenario in _load_fixtures()["scenarios"]:
        assert scenario["expectations"]["safe_trace_only"] is True
        for record in scenario["terminal_records"]:
            assert record["safe_trace_metadata"] == {
                "raw_inputs_in_trace": False,
                "model_visible_trace_sanitized": True,
            }


def test_fixture_has_no_credential_network_sql_statement_or_filesystem_secret() -> None:
    serialized = json.dumps(_load_fixtures(), sort_keys=True).lower()

    forbidden_fragments = (
        "api_key",
        "authorization:",
        "password",
        "secret=",
        "http://",
        "https://",
        "select ",
        "insert ",
        "update ",
        "delete ",
        "/users/",
        "~/.ssh",
    )
    assert not any(fragment in serialized for fragment in forbidden_fragments)


def test_fixture_serialization_is_deterministic_across_repeated_reads() -> None:
    first = json.dumps(_load_fixtures(), sort_keys=True, separators=(",", ":"))
    second = json.dumps(_load_fixtures(), sort_keys=True, separators=(",", ":"))

    assert first == second


def test_fixture_json_remains_provider_neutral() -> None:
    serialized = json.dumps(_load_fixtures(), sort_keys=True).lower()

    provider_specific_terms = (
        "openai",
        "anthropic",
        "vercel",
        "langgraph",
        "mcp",
        "toolresultblock",
    )
    assert not any(term in serialized for term in provider_specific_terms)
