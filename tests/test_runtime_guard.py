"""Focused behavioral tests for the AgentFuse Runtime Guard MVP."""

from __future__ import annotations

import asyncio
import json

from dhms_agentfuse import (
    GuardedInvocation,
    RuntimeGuard,
    RuntimePolicyDecision,
    ToolCallRequest,
)


def _call(name: str = "read", arguments: dict[str, object] | None = None) -> ToolCallRequest:
    return ToolCallRequest(
        tool_call_id=f"call-{name}-001",
        tool_name=name,
        arguments=arguments or {"value": "safe"},
    )


def test_explicit_denylist_prevents_sync_handler_execution() -> None:
    calls = 0

    def handler(value: str) -> str:
        nonlocal calls
        calls += 1
        return value

    result = RuntimeGuard(deny_tools={"delete"}).invoke(
        tool_call=_call("delete"), handler=handler
    )

    assert calls == 0
    assert result.decision == "block"
    assert result.reason_code == "explicit_denylist"
    assert result.outcome == "not_executed"
    assert result.evidence.non_execution is not None


def test_allowlist_miss_prevents_sync_handler_execution() -> None:
    calls = 0

    def handler(value: str) -> str:
        nonlocal calls
        calls += 1
        return value

    result = RuntimeGuard(allow_tools={"read"}).invoke(
        tool_call=_call("write"), handler=handler
    )

    assert calls == 0
    assert result.reason_code == "not_allowlisted"
    assert result.outcome == "not_executed"


def test_custom_policy_block_prevents_execution() -> None:
    result = RuntimeGuard(
        default_action="allow",
        policy=lambda request: RuntimePolicyDecision.block("policy_denied"),
    ).invoke(tool_call=_call(), handler=lambda value: value)

    assert result.decision == "block"
    assert result.dispatch_occurred is False


def test_custom_policy_can_inspect_arguments_before_dispatch() -> None:
    observed: list[str] = []

    def policy(request: ToolCallRequest) -> RuntimePolicyDecision:
        observed.append(str(request.arguments["risk"]))
        return RuntimePolicyDecision.block("policy_denied")

    result = RuntimeGuard(policy=policy).invoke(
        tool_call=_call("write", {"risk": "high"}),
        handler=lambda risk: risk,
    )

    assert observed == ["high"]
    assert result.handler_started is False


def test_blocked_arguments_never_reach_handler() -> None:
    received: list[dict[str, object]] = []

    def handler(**arguments: object) -> None:
        received.append(arguments)

    RuntimeGuard(deny_tools={"delete"}).invoke(
        tool_call=_call("delete", {"secret": "RAW_BLOCKED_ARGUMENT"}),
        handler=handler,
    )

    assert received == []


def test_custom_policy_is_evaluated_exactly_once() -> None:
    evaluations = 0

    def policy(request: ToolCallRequest) -> str:
        nonlocal evaluations
        evaluations += 1
        return "allow"

    RuntimeGuard(policy=policy).invoke(tool_call=_call(), handler=lambda value: value)

    assert evaluations == 1


def test_policy_exception_fails_closed_without_raw_exception_text() -> None:
    def policy(request: ToolCallRequest) -> str:
        raise RuntimeError("RAW_POLICY_EXCEPTION_MUST_NOT_APPEAR")

    result = RuntimeGuard(policy=policy).invoke(
        tool_call=_call(), handler=lambda value: value
    )
    serialized = json.dumps(result.to_safe_dict(), sort_keys=True)

    assert result.reason_code == "policy_exception"
    assert result.outcome == "not_executed"
    assert "RAW_POLICY_EXCEPTION_MUST_NOT_APPEAR" not in serialized


def test_invalid_policy_return_fails_closed() -> None:
    result = RuntimeGuard(policy=lambda request: {"action": "allow"}).invoke(
        tool_call=_call(), handler=lambda value: value
    )

    assert result.reason_code == "invalid_policy_decision"
    assert result.handler_started is False


def test_explicit_denial_and_policy_failure_have_distinct_reasons() -> None:
    denied = RuntimeGuard(deny_tools={"read"}).invoke(
        tool_call=_call(), handler=lambda value: value
    )
    failed = RuntimeGuard(policy=lambda request: object()).invoke(
        tool_call=_call(), handler=lambda value: value
    )

    assert denied.reason_code == "explicit_denylist"
    assert failed.reason_code == "invalid_policy_decision"


def test_sync_allow_invokes_handler_once_and_returns_value() -> None:
    calls = 0

    def handler(value: str) -> str:
        nonlocal calls
        calls += 1
        return f"result:{value}"

    result = RuntimeGuard(allow_tools={"read"}).invoke(
        tool_call=_call(), handler=handler
    )

    assert calls == 1
    assert result.handler_started is True
    assert result.execution == "started"
    assert result.outcome == "executed"
    assert result.to_safe_dict()["outcome"] == "executed"
    assert result.return_value == "result:safe"
    assert result.evidence.non_execution is None


def test_sync_handler_exception_is_execution_failure_with_unknown_side_effect() -> None:
    def handler(value: str) -> str:
        raise RuntimeError("RAW_HANDLER_EXCEPTION_MUST_NOT_APPEAR")

    result = RuntimeGuard(allow_tools={"read"}).invoke(
        tool_call=_call(), handler=handler
    )
    serialized = json.dumps(result.to_safe_dict(), sort_keys=True)

    assert result.decision == "allow"
    assert result.handler_started is True
    assert result.outcome == "execution_failed"
    assert result.side_effect_occurred is None
    assert result.evidence.non_execution is None
    assert "RAW_HANDLER_EXCEPTION_MUST_NOT_APPEAR" not in serialized


def test_async_allow_awaits_handler_exactly_once() -> None:
    calls = 0

    async def handler(value: str) -> str:
        nonlocal calls
        calls += 1
        return f"async:{value}"

    result = asyncio.run(
        RuntimeGuard(allow_tools={"read"}).ainvoke(tool_call=_call(), handler=handler)
    )

    assert calls == 1
    assert result.return_value == "async:safe"
    assert result.outcome == "executed"


def test_async_block_never_awaits_handler() -> None:
    calls = 0

    async def handler(value: str) -> str:
        nonlocal calls
        calls += 1
        return value

    result = asyncio.run(
        RuntimeGuard(deny_tools={"read"}).ainvoke(tool_call=_call(), handler=handler)
    )

    assert calls == 0
    assert result.outcome == "not_executed"


def test_async_handler_failure_is_execution_failure() -> None:
    async def handler(value: str) -> str:
        raise RuntimeError("raw async failure")

    result = asyncio.run(
        RuntimeGuard(allow_tools={"read"}).ainvoke(tool_call=_call(), handler=handler)
    )

    assert result.handler_started is True
    assert result.outcome == "execution_failed"
    assert result.side_effect_occurred is None


def test_async_policy_exception_fails_closed() -> None:
    async def policy(request: ToolCallRequest) -> str:
        raise RuntimeError("raw async policy failure")

    result = asyncio.run(
        RuntimeGuard(policy=policy).ainvoke(
            tool_call=_call(), handler=lambda value: value
        )
    )

    assert result.reason_code == "policy_exception"
    assert result.handler_started is False
    assert result.execution == "not_started"
    assert result.outcome == "not_executed"


def test_async_invalid_policy_return_fails_closed() -> None:
    async def policy(request: ToolCallRequest) -> object:
        return object()

    result = asyncio.run(
        RuntimeGuard(policy=policy).ainvoke(
            tool_call=_call(), handler=lambda value: value
        )
    )

    assert result.reason_code == "invalid_policy_decision"
    assert result.handler_started is False


def test_async_policy_is_awaited_once() -> None:
    evaluations = 0

    async def policy(request: ToolCallRequest) -> str:
        nonlocal evaluations
        evaluations += 1
        return "allow"

    result = asyncio.run(
        RuntimeGuard(policy=policy).ainvoke(
            tool_call=_call(), handler=lambda value: value
        )
    )

    assert evaluations == 1
    assert result.outcome == "executed"


def test_original_tool_call_identity_is_preserved() -> None:
    request = ToolCallRequest("stable-id", "stable-name", {})
    result = RuntimeGuard(default_action="block").invoke(
        tool_call=request, handler=lambda: None
    )

    assert result.tool_call_id == "stable-id"
    assert result.tool_name == "stable-name"
    assert result.evidence.non_execution is not None
    assert result.evidence.non_execution.call_id == "stable-id"


def test_default_request_repr_and_serialization_exclude_arguments() -> None:
    request = ToolCallRequest("call-secret", "read", {"token": "RAW_SECRET"})

    assert "RAW_SECRET" not in repr(request)
    assert "RAW_SECRET" not in json.dumps(request.to_safe_dict(), sort_keys=True)


def test_safe_result_excludes_successful_return_payload() -> None:
    result = RuntimeGuard(allow_tools={"read"}).invoke(
        tool_call=_call(), handler=lambda value: "RAW_SUCCESS_PAYLOAD"
    )

    assert result.return_value == "RAW_SUCCESS_PAYLOAD"
    assert "RAW_SUCCESS_PAYLOAD" not in repr(result)
    assert "RAW_SUCCESS_PAYLOAD" not in json.dumps(result.to_safe_dict(), sort_keys=True)


def test_batch_continues_after_blocked_call() -> None:
    allowed_calls = 0

    def allowed(value: str) -> str:
        nonlocal allowed_calls
        allowed_calls += 1
        return value

    results = RuntimeGuard(allow_tools={"read"}, deny_tools={"delete"}).invoke_batch(
        invocations=[
            GuardedInvocation(_call("delete"), lambda value: value),
            GuardedInvocation(_call("read"), allowed),
        ]
    )

    assert [result.outcome for result in results] == ["not_executed", "executed"]
    assert allowed_calls == 1


def test_batch_continues_after_policy_failure() -> None:
    def policy(request: ToolCallRequest) -> str:
        if request.tool_name == "broken-policy":
            raise RuntimeError("policy failed")
        return "allow"

    results = RuntimeGuard(policy=policy).invoke_batch(
        invocations=[
            GuardedInvocation(_call("broken-policy"), lambda value: value),
            GuardedInvocation(_call("read"), lambda value: value),
        ]
    )

    assert [result.outcome for result in results] == ["not_executed", "executed"]


def test_batch_continues_after_handler_failure_and_returns_one_result_per_input() -> None:
    def failing(value: str) -> str:
        raise RuntimeError("handler failed")

    results = RuntimeGuard(allow_tools={"fail", "read"}).invoke_batch(
        invocations=[
            GuardedInvocation(_call("fail"), failing),
            GuardedInvocation(_call("read"), lambda value: value),
        ]
    )

    assert len(results) == 2
    assert [result.outcome for result in results] == ["execution_failed", "executed"]


def test_async_batch_preserves_order_and_continuation() -> None:
    async def allowed(value: str) -> str:
        return value

    results = asyncio.run(
        RuntimeGuard(allow_tools={"read"}, deny_tools={"delete"}).ainvoke_batch(
            invocations=[
                GuardedInvocation(_call("delete"), allowed),
                GuardedInvocation(_call("read"), allowed),
            ]
        )
    )

    assert [result.tool_name for result in results] == ["delete", "read"]
    assert [result.outcome for result in results] == ["not_executed", "executed"]


def test_denylist_has_precedence_over_allowlist_and_custom_policy() -> None:
    policy_calls = 0

    def policy(request: ToolCallRequest) -> str:
        nonlocal policy_calls
        policy_calls += 1
        return "allow"

    result = RuntimeGuard(
        allow_tools={"delete"}, deny_tools={"delete"}, policy=policy
    ).invoke(tool_call=_call("delete"), handler=lambda value: value)

    assert result.reason_code == "explicit_denylist"
    assert policy_calls == 0


def test_default_action_is_block_unless_explicitly_changed() -> None:
    blocked = RuntimeGuard().invoke(tool_call=_call(), handler=lambda value: value)
    allowed = RuntimeGuard(default_action="allow").invoke(
        tool_call=_call(), handler=lambda value: value
    )

    assert blocked.outcome == "not_executed"
    assert allowed.outcome == "executed"


def test_empty_configured_allowlist_blocks_every_tool() -> None:
    result = RuntimeGuard(allow_tools=set()).invoke(
        tool_call=_call(), handler=lambda value: value
    )

    assert result.reason_code == "not_allowlisted"


def test_sync_invoke_does_not_run_async_handler_implicitly() -> None:
    calls = 0

    async def handler(value: str) -> str:
        nonlocal calls
        calls += 1
        return value

    result = RuntimeGuard(allow_tools={"read"}).invoke(
        tool_call=_call(), handler=handler
    )

    assert calls == 0
    assert result.outcome == "execution_failed"
    assert result.failure_category == "async_handler_requires_ainvoke"
