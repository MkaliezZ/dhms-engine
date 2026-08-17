"""Contract tests for the provider-neutral RuntimeGuardDecision consumer proof."""

from __future__ import annotations

import asyncio
from dataclasses import FrozenInstanceError
import json

import pytest

from dhms_agentfuse import RuntimeGuard, RuntimeGuardDecision, ToolCallRequest
from examples.runtime_guard.consumer_integration_contract_demo import (
    consume_decision,
    run_demo,
    arun_demo,
)


def _request(tool_name: str = "read") -> ToolCallRequest:
    return ToolCallRequest(
        tool_call_id=f"consumer-contract-{tool_name}-001",
        tool_name=tool_name,
        arguments={"protected": "RAW_CONSUMER_CONTRACT_ARGUMENT"},
    )


def _case(summary: dict[str, object], name: str) -> dict[str, object]:
    return summary["case_results"][name]


def test_runtime_guard_decision_is_immutable_and_safely_serialized() -> None:
    decision = RuntimeGuard(default_action="allow").evaluate(_request())

    assert isinstance(decision, RuntimeGuardDecision)
    with pytest.raises(FrozenInstanceError):
        decision.action = "block"  # type: ignore[misc]

    first = json.dumps(decision.to_safe_dict(), sort_keys=True, separators=(",", ":"))
    second = json.dumps(decision.to_safe_dict(), sort_keys=True, separators=(",", ":"))
    assert first == second
    assert "RAW_CONSUMER_CONTRACT_ARGUMENT" not in first


def test_blocked_decision_is_not_dispatched_or_invoked_by_reference_consumer() -> None:
    summary = run_demo()
    blocked = _case(summary, "blocked_before_dispatch")

    assert summary["handler_invocation_counts"]["blocked"] == 0
    assert blocked["policy_decision"] == "block"
    assert blocked["dispatch_occurred"] is False
    assert blocked["handler_started"] is False
    assert blocked["execution_outcome"] == "not_executed"
    assert blocked["tool_failure"] is False


def test_allowed_decision_can_dispatch_and_execute_but_is_not_execution_proof() -> None:
    summary = run_demo()
    executed = _case(summary, "allowed_and_executed")
    interrupted = _case(summary, "allowed_and_interrupted")

    assert summary["handler_invocation_counts"]["executed"] == 1
    assert executed["policy_decision"] == "allow"
    assert executed["dispatch_occurred"] is True
    assert executed["execution_outcome"] == "executed"
    assert interrupted["policy_decision"] == "allow"
    assert interrupted["dispatch_occurred"] is True
    assert interrupted["handler_started"] is False
    assert interrupted["execution_outcome"] == "interrupted"
    assert interrupted["tool_failure"] is False


def test_allowed_handler_failure_is_distinct_from_policy_denial() -> None:
    failed = _case(run_demo(), "allowed_and_handler_failed")

    assert failed["policy_decision"] == "allow"
    assert failed["handler_started"] is True
    assert failed["execution_outcome"] == "execution_failed"
    assert failed["tool_failure"] is True


def test_policy_exception_and_invalid_result_fail_closed_before_reference_dispatch() -> None:
    calls = 0

    def handler() -> None:
        nonlocal calls
        calls += 1

    exception_decision = RuntimeGuard(
        policy=lambda request: (_ for _ in ()).throw(RuntimeError("RAW_POLICY_FAILURE"))
    ).evaluate(_request("exception"))
    invalid_decision = RuntimeGuard(policy=lambda request: {"action": "allow"}).evaluate(
        _request("invalid")
    )

    for decision, reason_code in (
        (exception_decision, "policy_exception"),
        (invalid_decision, "invalid_policy_decision"),
    ):
        receipt = consume_decision(decision, handler=handler)
        assert decision.action == "block"
        assert decision.reason_code == reason_code
        assert receipt["dispatch_occurred"] is False
        assert receipt["execution_outcome"] == "not_executed"
        assert "RAW_POLICY_FAILURE" not in json.dumps(receipt, sort_keys=True)

    assert calls == 0


def test_reference_consumer_safe_output_excludes_protected_arguments() -> None:
    serialized = json.dumps(run_demo(), sort_keys=True)

    assert "RAW_CONSUMER_CONTRACT_ARGUMENT" not in serialized
    assert '"protected_input"' not in serialized


def test_sync_and_async_reference_semantics_are_aligned() -> None:
    sync_summary = run_demo()
    async_summary = asyncio.run(arun_demo())

    assert run_demo() == sync_summary
    assert sync_summary == async_summary
    assert sync_summary["policy_decision_is_not_approval"] is True
    assert sync_summary["policy_decision_is_not_dispatch"] is True
    assert sync_summary["policy_decision_is_not_execution_outcome"] is True
    assert sync_summary["policy_decision_is_not_process_completion"] is True
    assert sync_summary["policy_decision_is_not_goal_achievement"] is True
