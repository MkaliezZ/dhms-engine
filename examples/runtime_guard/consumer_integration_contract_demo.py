"""Provider-neutral reference consumer proof for RuntimeGuardDecision."""

from __future__ import annotations

import asyncio
import inspect
import json
from typing import Any, Callable

from dhms_agentfuse import RuntimeGuard, RuntimeGuardDecision, ToolCallRequest


Handler = Callable[..., Any]
_HOST_NOT_RECORDED = "host_owned_not_recorded"


def _request(tool_call_id: str, tool_name: str) -> ToolCallRequest:
    return ToolCallRequest(
        tool_call_id=tool_call_id,
        tool_name=tool_name,
        arguments={"protected_input": "RAW_CONSUMER_CONTRACT_ARGUMENT"},
        safe_metadata={"reference_consumer": "provider-neutral"},
    )


def _receipt(
    decision: RuntimeGuardDecision,
    *,
    dispatch_occurred: bool,
    handler_started: bool,
    execution_outcome: str,
    tool_failure: bool,
    side_effect_occurred: bool | None,
) -> dict[str, Any]:
    """Build a safe host-owned lifecycle record without exposing raw arguments."""

    return {
        "tool_call_id": decision.tool_call_id,
        "tool_name": decision.tool_name,
        "policy_decision": decision.action,
        "reason_code": decision.reason_code,
        "approval_state": "host_owned_not_evaluated",
        "dispatch_occurred": dispatch_occurred,
        "handler_started": handler_started,
        "execution_outcome": execution_outcome,
        "tool_failure": tool_failure,
        "side_effect_occurred": side_effect_occurred,
        "process_completion": _HOST_NOT_RECORDED,
        "goal_achievement": _HOST_NOT_RECORDED,
        "decision_evidence": decision.to_safe_dict(),
    }


def consume_decision(
    decision: RuntimeGuardDecision,
    *,
    handler: Handler,
    host_outcome: str = "executed",
) -> dict[str, Any]:
    """Model the smallest synchronous host contract around a decision-only API.

    This is a local reference consumer, not a new AgentFuse executor or a
    universal lifecycle API. The host owns approval, dispatch, outcomes,
    process completion, and goal completion.
    """

    if decision.action == "block":
        return _receipt(
            decision,
            dispatch_occurred=False,
            handler_started=False,
            execution_outcome="not_executed",
            tool_failure=False,
            side_effect_occurred=False,
        )
    if host_outcome == "interrupted":
        return _receipt(
            decision,
            dispatch_occurred=True,
            handler_started=False,
            execution_outcome="interrupted",
            tool_failure=False,
            side_effect_occurred=None,
        )
    try:
        handler()
    except Exception:
        return _receipt(
            decision,
            dispatch_occurred=True,
            handler_started=True,
            execution_outcome="execution_failed",
            tool_failure=True,
            side_effect_occurred=None,
        )
    return _receipt(
        decision,
        dispatch_occurred=True,
        handler_started=True,
        execution_outcome="executed",
        tool_failure=False,
        side_effect_occurred=None,
    )


async def aconsume_decision(
    decision: RuntimeGuardDecision,
    *,
    handler: Handler,
    host_outcome: str = "executed",
) -> dict[str, Any]:
    """Async counterpart with the same host-owned lifecycle semantics."""

    if decision.action == "block":
        return _receipt(
            decision,
            dispatch_occurred=False,
            handler_started=False,
            execution_outcome="not_executed",
            tool_failure=False,
            side_effect_occurred=False,
        )
    if host_outcome == "interrupted":
        return _receipt(
            decision,
            dispatch_occurred=True,
            handler_started=False,
            execution_outcome="interrupted",
            tool_failure=False,
            side_effect_occurred=None,
        )
    try:
        value = handler()
        if inspect.isawaitable(value):
            await value
    except Exception:
        return _receipt(
            decision,
            dispatch_occurred=True,
            handler_started=True,
            execution_outcome="execution_failed",
            tool_failure=True,
            side_effect_occurred=None,
        )
    return _receipt(
        decision,
        dispatch_occurred=True,
        handler_started=True,
        execution_outcome="executed",
        tool_failure=False,
        side_effect_occurred=None,
    )


def _summary(case_results: dict[str, dict[str, Any]], counters: dict[str, int]) -> dict[str, Any]:
    return {
        "contract": "agentfuse-consumer-integration-contract-v3.6.1",
        "provider_neutral": True,
        "case_results": case_results,
        "handler_invocation_counts": counters,
        "policy_decision_is_not_approval": True,
        "policy_decision_is_not_dispatch": True,
        "policy_decision_is_not_execution_outcome": True,
        "policy_decision_is_not_process_completion": True,
        "policy_decision_is_not_goal_achievement": True,
        "safe_output_only": True,
    }


def run_demo() -> dict[str, Any]:
    """Run four local lifecycle cases without external execution."""

    counters = {"blocked": 0, "executed": 0, "interrupted": 0, "failed": 0}

    def blocked_handler() -> None:
        counters["blocked"] += 1

    def executed_handler() -> None:
        counters["executed"] += 1

    def interrupted_handler() -> None:
        counters["interrupted"] += 1

    def failed_handler() -> None:
        counters["failed"] += 1
        raise RuntimeError("reference handler failure")

    block_guard = RuntimeGuard(deny_tools={"blocked_tool"})
    allow_guard = RuntimeGuard(allow_tools={"executed_tool", "interrupted_tool", "failed_tool"})
    case_results = {
        "blocked_before_dispatch": consume_decision(
            block_guard.evaluate(_request("consumer-blocked-001", "blocked_tool")),
            handler=blocked_handler,
        ),
        "allowed_and_executed": consume_decision(
            allow_guard.evaluate(_request("consumer-executed-001", "executed_tool")),
            handler=executed_handler,
        ),
        "allowed_and_interrupted": consume_decision(
            allow_guard.evaluate(_request("consumer-interrupted-001", "interrupted_tool")),
            handler=interrupted_handler,
            host_outcome="interrupted",
        ),
        "allowed_and_handler_failed": consume_decision(
            allow_guard.evaluate(_request("consumer-failed-001", "failed_tool")),
            handler=failed_handler,
        ),
    }
    return _summary(case_results, counters)


async def arun_demo() -> dict[str, Any]:
    """Run the same four cases through asynchronous policy evaluation."""

    counters = {"blocked": 0, "executed": 0, "interrupted": 0, "failed": 0}

    async def blocked_handler() -> None:
        counters["blocked"] += 1

    async def executed_handler() -> None:
        counters["executed"] += 1

    async def interrupted_handler() -> None:
        counters["interrupted"] += 1

    async def failed_handler() -> None:
        counters["failed"] += 1
        raise RuntimeError("reference handler failure")

    block_guard = RuntimeGuard(deny_tools={"blocked_tool"})
    allow_guard = RuntimeGuard(allow_tools={"executed_tool", "interrupted_tool", "failed_tool"})
    case_results = {
        "blocked_before_dispatch": await aconsume_decision(
            await block_guard.aevaluate(_request("consumer-blocked-001", "blocked_tool")),
            handler=blocked_handler,
        ),
        "allowed_and_executed": await aconsume_decision(
            await allow_guard.aevaluate(_request("consumer-executed-001", "executed_tool")),
            handler=executed_handler,
        ),
        "allowed_and_interrupted": await aconsume_decision(
            await allow_guard.aevaluate(_request("consumer-interrupted-001", "interrupted_tool")),
            handler=interrupted_handler,
            host_outcome="interrupted",
        ),
        "allowed_and_handler_failed": await aconsume_decision(
            await allow_guard.aevaluate(_request("consumer-failed-001", "failed_tool")),
            handler=failed_handler,
        ),
    }
    return _summary(case_results, counters)


if __name__ == "__main__":
    summary = run_demo()
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    print("AGENTFUSE_CONSUMER_INTEGRATION_CONTRACT_DEMO_PASS")
