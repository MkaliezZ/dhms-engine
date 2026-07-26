"""Public pre-dispatch decision API tests."""

from __future__ import annotations

import asyncio
import inspect
import json

from dhms_agentfuse import (
    RuntimeGuard,
    RuntimeGuardDecision,
    RuntimePolicyDecision,
    ToolCallRequest,
)
from dhms_agentfuse.evidence_schema import SCHEMA_VERSION


def _call(
    name: str = "read",
    arguments: dict[str, object] | None = None,
) -> ToolCallRequest:
    return ToolCallRequest(
        tool_call_id=f"decision-{name}-001",
        tool_name=name,
        arguments=arguments or {"value": "safe"},
    )


def test_public_sync_allow_decision_never_invokes_handler() -> None:
    handler_invocations = 0

    def handler(value: str) -> str:
        nonlocal handler_invocations
        handler_invocations += 1
        return value

    decision = RuntimeGuard(default_action="allow").evaluate(_call())

    assert isinstance(decision, RuntimeGuardDecision)
    assert decision.action == "allow"
    assert handler_invocations == 0
    assert "handler" not in inspect.signature(RuntimeGuard.evaluate).parameters


def test_public_sync_deny_decision_never_dispatches() -> None:
    decision = RuntimeGuard(deny_tools={"delete"}).evaluate(_call("delete"))

    assert decision.action == "block"
    assert decision.reason_code == "explicit_denylist"
    assert decision.evidence.non_execution is not None
    assert not hasattr(decision, "dispatch_occurred")


def test_public_default_policy_blocks() -> None:
    decision = RuntimeGuard().evaluate(_call())

    assert decision.action == "block"
    assert decision.reason_code == "policy_denied"


def test_public_allowlist_allows_matching_tool() -> None:
    decision = RuntimeGuard(allow_tools={"read"}).evaluate(_call())

    assert decision.action == "allow"
    assert decision.reason_code == "allowed"
    assert decision.policy_id == "runtime-guard:allowlist"


def test_public_custom_policy_allows() -> None:
    decision = RuntimeGuard(
        policy=lambda request: RuntimePolicyDecision.allow(
            reason_code="custom_allowed",
            policy_id="policy:custom-allow",
        )
    ).evaluate(_call())

    assert decision.action == "allow"
    assert decision.reason_code == "custom_allowed"
    assert decision.policy_id == "policy:custom-allow"


def test_public_custom_policy_blocks() -> None:
    decision = RuntimeGuard(
        policy=lambda request: RuntimePolicyDecision.block(
            reason_code="custom_blocked",
            policy_id="policy:custom-block",
        )
    ).evaluate(_call())

    assert decision.action == "block"
    assert decision.reason_code == "custom_blocked"
    assert decision.policy_id == "policy:custom-block"


def test_public_policy_exception_fails_closed() -> None:
    def policy(request: ToolCallRequest) -> str:
        raise RuntimeError("RAW_POLICY_EXCEPTION")

    decision = RuntimeGuard(policy=policy).evaluate(_call())
    serialized = json.dumps(decision.to_safe_dict(), sort_keys=True)

    assert decision.action == "block"
    assert decision.reason_code == "policy_exception"
    assert "RAW_POLICY_EXCEPTION" not in serialized


def test_public_invalid_policy_decision_fails_closed() -> None:
    decision = RuntimeGuard(policy=lambda request: {"action": "allow"}).evaluate(_call())

    assert decision.action == "block"
    assert decision.reason_code == "invalid_policy_decision"


def test_public_aevaluate_awaits_async_policy_without_dispatch() -> None:
    policy_calls = 0
    handler_invocations = 0

    async def policy(request: ToolCallRequest) -> str:
        nonlocal policy_calls
        policy_calls += 1
        return "allow"

    async def handler(value: str) -> str:
        nonlocal handler_invocations
        handler_invocations += 1
        return value

    decision = asyncio.run(RuntimeGuard(policy=policy).aevaluate(_call()))

    assert decision.action == "allow"
    assert policy_calls == 1
    assert handler_invocations == 0
    assert "handler" not in inspect.signature(RuntimeGuard.aevaluate).parameters


def test_public_evaluate_rejects_async_only_policy_safely() -> None:
    async def policy(request: ToolCallRequest) -> str:
        return "allow"

    decision = RuntimeGuard(policy=policy).evaluate(_call())

    assert decision.action == "block"
    assert decision.reason_code == "invalid_policy_decision"


def test_public_aevaluate_policy_exception_fails_closed() -> None:
    async def policy(request: ToolCallRequest) -> str:
        raise RuntimeError("RAW_ASYNC_POLICY_EXCEPTION")

    decision = asyncio.run(RuntimeGuard(policy=policy).aevaluate(_call()))

    assert decision.action == "block"
    assert decision.reason_code == "policy_exception"


def test_public_decision_uses_canonical_evidence_schema() -> None:
    decision = RuntimeGuard(allow_tools={"read"}).evaluate(_call())

    assert decision.evidence.schema_version == SCHEMA_VERSION
    assert decision.evidence.boundary_decision.decision == decision.action
    assert decision.evidence.boundary_decision.policy_id == decision.policy_id


def test_public_decision_safe_output_redacts_arguments() -> None:
    decision = RuntimeGuard(default_action="allow").evaluate(
        _call(arguments={"token": "RAW_SECRET_ARGUMENT"})
    )
    serialized = json.dumps(decision.to_safe_dict(), sort_keys=True)

    assert "RAW_SECRET_ARGUMENT" not in serialized
    assert "RAW_SECRET_ARGUMENT" not in repr(decision)


def test_public_decision_matches_sync_invoke_pre_dispatch_policy() -> None:
    guard = RuntimeGuard(allow_tools={"read"})
    decision = guard.evaluate(_call())
    result = guard.invoke(tool_call=_call(), handler=lambda value: value)

    assert result.decision == decision.action
    assert result.reason_code == decision.reason_code
    assert result.evidence == decision.evidence


def test_public_decision_matches_async_invoke_pre_dispatch_policy() -> None:
    guard = RuntimeGuard(deny_tools={"read"})
    decision = asyncio.run(guard.aevaluate(_call()))
    result = asyncio.run(
        guard.ainvoke(tool_call=_call(), handler=lambda value: value)
    )

    assert result.decision == decision.action
    assert result.reason_code == decision.reason_code
    assert result.evidence == decision.evidence


def test_public_decision_has_no_handler_or_dispatch_fields() -> None:
    decision = RuntimeGuard(default_action="allow").evaluate(_call())

    assert set(decision.to_safe_dict()) == {
        "tool_call_id",
        "tool_name",
        "action",
        "reason_code",
        "policy_id",
        "evidence",
    }
    assert not hasattr(decision, "return_value")
    assert not hasattr(decision, "handler_started")
