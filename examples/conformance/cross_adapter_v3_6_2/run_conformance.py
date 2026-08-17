#!/usr/bin/env python3
"""Run provider-neutral AgentFuse v3.6.2 conformance cases."""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
from typing import Any, Callable, Mapping


_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
if str(_REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY_ROOT))

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import END, START
from langgraph.graph import MessagesState, StateGraph
from langgraph.types import interrupt

from dhms_agentfuse import LangGraphRuntimeGuardAdapter, RuntimeGuard, ToolCallRequest
from examples.runtime_guard.consumer_integration_contract_demo import (
    aconsume_decision,
    consume_decision,
)


FIXTURE_PATH = Path(__file__).with_name("fixtures.json")
FINAL_VERDICT = "AGENTFUSE_CROSS_ADAPTER_CONFORMANCE_V3_6_2_PASS"
ADAPTER_IDS = ("python-runtime-guard", "provider-neutral-reference", "langgraph-tool-node")
_SYNTHETIC_SENTINEL = "agentfuse-v3.6.2-synthetic-sentinel"


@dataclass(frozen=True)
class ConformanceResult:
    """Bounded test/report data; not an AgentFuse evidence-schema revision."""

    fixture_version: str
    adapter_id: str
    case_id: str
    policy_decision: str | None
    policy_reason: str | None
    dispatch_observed: bool | None
    handler_started: bool | None
    execution_outcome: str | None
    interruption_observed: bool | None
    safe_output: bool
    terminal_settlement_count: int | None
    identity_preserved: bool | None
    verdict: str
    verdict_reason: str


def load_fixture_document(path: Path = FIXTURE_PATH) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("fixture_version") != "agentfuse-cross-adapter-conformance-v3.6.2":
        raise ValueError("unexpected fixture version")
    if document.get("canonical_policy_actions") != ["allow", "block"]:
        raise ValueError("canonical actions must remain allow|block")
    cases = document.get("cases")
    if not isinstance(cases, list) or len(cases) != 14:
        raise ValueError("the v3.6.2 fixture set must contain exactly 14 cases")
    case_ids = [case.get("case_id") for case in cases]
    if len(set(case_ids)) != len(case_ids):
        raise ValueError("fixture case_id values must be unique")
    return document


def fixture_arguments(document: Mapping[str, Any]) -> dict[str, Any]:
    if document["arguments_profile"] != "synthetic_sensitive_v1":
        raise ValueError("unsupported arguments profile")
    return {
        "operation": "conformance",
        "protected": {"token": _SYNTHETIC_SENTINEL},
    }


def _request(document: Mapping[str, Any], case: Mapping[str, Any], call_id: str | None = None) -> ToolCallRequest:
    return ToolCallRequest(
        tool_call_id=call_id or str(case["tool_call_id"]),
        tool_name=str(case["tool_name"]),
        arguments=fixture_arguments(document),
        safe_metadata={"fixture_version": document["fixture_version"], "case_id": case["case_id"]},
    )


def _guard(case: Mapping[str, Any]) -> RuntimeGuard:
    policy_config = case["policy"]
    policy_mode = case["policy_mode"]
    policy: Callable[[ToolCallRequest], Any] | None = None
    if policy_mode == "exception":
        def raise_policy_error(_request: ToolCallRequest) -> Any:
            raise RuntimeError("synthetic policy failure")

        policy = raise_policy_error
    elif policy_mode == "invalid":
        policy = lambda _request: {"action": "allow"}
    elif policy_mode != "static":
        raise ValueError(f"unsupported policy_mode={policy_mode!r}")
    return RuntimeGuard(
        allow_tools=policy_config["allow_tools"],
        deny_tools=policy_config["deny_tools"],
        default_action=policy_config["default_action"],
        policy=policy,
    )


def _assert_policy(document: Mapping[str, Any], case: Mapping[str, Any], decision: Any) -> None:
    expected = case["expected_policy"]
    assert decision.action == expected["decision"]
    assert decision.reason_code == expected["reason"]
    assert decision.action in document["canonical_policy_actions"]
    assert decision.evidence.trace_metadata.args_hash == document["expected_arguments_digest"]


def _safe(*values: Any) -> bool:
    rendered = json.dumps(values, sort_keys=True, default=str, separators=(",", ":"))
    return _SYNTHETIC_SENTINEL not in rendered


def _result(
    document: Mapping[str, Any],
    case: Mapping[str, Any],
    adapter_id: str,
    *,
    policy_decision: str | None,
    policy_reason: str | None,
    dispatch_observed: bool | None,
    handler_started: bool | None,
    execution_outcome: str | None,
    interruption_observed: bool | None,
    safe_output: bool,
    terminal_settlement_count: int | None,
    identity_preserved: bool | None,
    verdict: str = "PASS",
    verdict_reason: str = "all applicable invariants passed",
) -> ConformanceResult:
    return ConformanceResult(
        fixture_version=str(document["fixture_version"]),
        adapter_id=adapter_id,
        case_id=str(case["case_id"]),
        policy_decision=policy_decision,
        policy_reason=policy_reason,
        dispatch_observed=dispatch_observed,
        handler_started=handler_started,
        execution_outcome=execution_outcome,
        interruption_observed=interruption_observed,
        safe_output=safe_output,
        terminal_settlement_count=terminal_settlement_count,
        identity_preserved=identity_preserved,
        verdict=verdict,
        verdict_reason=verdict_reason,
    )


def _not_applicable(
    document: Mapping[str, Any],
    case: Mapping[str, Any],
    adapter_id: str,
    reason: str,
) -> ConformanceResult:
    return _result(
        document,
        case,
        adapter_id,
        policy_decision=None,
        policy_reason=None,
        dispatch_observed=None,
        handler_started=None,
        execution_outcome=None,
        interruption_observed=None,
        safe_output=True,
        terminal_settlement_count=None,
        identity_preserved=None,
        verdict="NOT_APPLICABLE",
        verdict_reason=reason,
    )


def _failed(document: Mapping[str, Any], case: Mapping[str, Any], adapter_id: str, error: BaseException) -> ConformanceResult:
    return _result(
        document,
        case,
        adapter_id,
        policy_decision=None,
        policy_reason=None,
        dispatch_observed=None,
        handler_started=None,
        execution_outcome=None,
        interruption_observed=None,
        safe_output=True,
        terminal_settlement_count=None,
        identity_preserved=None,
        verdict="FAIL",
        verdict_reason=f"{type(error).__name__}: {error}",
    )


def run_python_runtime_guard(document: Mapping[str, Any], case: Mapping[str, Any]) -> ConformanceResult:
    adapter_id = "python-runtime-guard"
    if case["host_scenario"] == "interrupt":
        return _not_applicable(
            document,
            case,
            adapter_id,
            "RuntimeGuard.invoke has no host interruption surface; the reference consumer and LangGraph own that lifecycle fact",
        )
    try:
        guard = _guard(case)
        request = _request(document, case)
        decision = guard.evaluate(request)
        _assert_policy(document, case, decision)
        counter = 0

        def handler(**_arguments: Any) -> str:
            nonlocal counter
            counter += 1
            if case["host_scenario"] == "handler_failure":
                raise RuntimeError("synthetic handler failure")
            return "ok"

        scenario = case["host_scenario"]
        if scenario == "decision_only":
            safe = _safe(decision.to_safe_dict())
            assert counter == 0 and safe
            return _result(
                document, case, adapter_id,
                policy_decision=decision.action, policy_reason=decision.reason_code,
                dispatch_observed=False, handler_started=False, execution_outcome="not_observed",
                interruption_observed=False, safe_output=safe, terminal_settlement_count=None,
                identity_preserved=decision.tool_call_id == request.tool_call_id,
            )
        if scenario == "reevaluate":
            repeated = guard.evaluate(request)
            assert decision.to_safe_dict() == repeated.to_safe_dict()
            safe = _safe(decision.to_safe_dict(), repeated.to_safe_dict())
            assert safe
            return _result(
                document, case, adapter_id,
                policy_decision=decision.action, policy_reason=decision.reason_code,
                dispatch_observed=False, handler_started=False, execution_outcome="not_observed",
                interruption_observed=False, safe_output=safe, terminal_settlement_count=None,
                identity_preserved=True,
            )
        if scenario == "identity":
            second_id = str(case["secondary_tool_call_id"])
            second = guard.evaluate(_request(document, case, second_id))
            assert {decision.tool_call_id, second.tool_call_id} == {request.tool_call_id, second_id}
            assert decision.evidence.trace_metadata.args_hash == second.evidence.trace_metadata.args_hash
            safe = _safe(decision.to_safe_dict(), second.to_safe_dict())
            assert safe
            return _result(
                document, case, adapter_id,
                policy_decision=decision.action, policy_reason=decision.reason_code,
                dispatch_observed=False, handler_started=False, execution_outcome="not_observed",
                interruption_observed=False, safe_output=safe, terminal_settlement_count=None,
                identity_preserved=True,
            )
        if scenario == "sync_async_parity":
            async_decision = asyncio.run(guard.aevaluate(request))
            assert decision.to_safe_dict() == async_decision.to_safe_dict()
            sync_result = guard.invoke(tool_call=request, handler=handler)
            async_result = asyncio.run(guard.ainvoke(tool_call=request, handler=handler))
            assert (sync_result.decision, sync_result.outcome) == (async_result.decision, async_result.outcome)
            safe = _safe(sync_result.to_safe_dict(), async_result.to_safe_dict())
            assert counter == 2 and safe
            return _result(
                document, case, adapter_id,
                policy_decision=decision.action, policy_reason=decision.reason_code,
                dispatch_observed=True, handler_started=True, execution_outcome="executed",
                interruption_observed=False, safe_output=safe, terminal_settlement_count=2,
                identity_preserved=True,
            )
        receipt = guard.invoke(tool_call=request, handler=handler)
        expected_block = decision.action == "block"
        if expected_block:
            assert counter == 0
            assert not receipt.dispatch_occurred and not receipt.handler_started
            assert receipt.outcome == "not_executed" and not receipt.tool_failure
        elif scenario == "handler_failure":
            assert counter == 1 and receipt.decision == "allow"
            assert receipt.outcome == "execution_failed" and receipt.tool_failure
        else:
            assert counter == 1 and receipt.decision == "allow" and receipt.outcome == "executed"
        safe = _safe(decision.to_safe_dict(), receipt.to_safe_dict())
        assert safe
        return _result(
            document, case, adapter_id,
            policy_decision=decision.action, policy_reason=decision.reason_code,
            dispatch_observed=receipt.dispatch_occurred, handler_started=receipt.handler_started,
            execution_outcome=receipt.outcome, interruption_observed=receipt.outcome == "interrupted",
            safe_output=safe, terminal_settlement_count=1,
            identity_preserved=receipt.tool_call_id == request.tool_call_id,
        )
    except BaseException as error:
        return _failed(document, case, adapter_id, error)


def run_reference_consumer(document: Mapping[str, Any], case: Mapping[str, Any]) -> ConformanceResult:
    adapter_id = "provider-neutral-reference"
    try:
        guard = _guard(case)
        request = _request(document, case)
        decision = guard.evaluate(request)
        _assert_policy(document, case, decision)
        counter = 0

        def handler() -> None:
            nonlocal counter
            counter += 1
            if case["host_scenario"] == "handler_failure":
                raise RuntimeError("synthetic handler failure")

        scenario = case["host_scenario"]
        host_outcome = "interrupted" if scenario == "interrupt" else "executed"
        if scenario == "reevaluate":
            repeated = guard.evaluate(request)
            assert decision.to_safe_dict() == repeated.to_safe_dict()
        if scenario == "identity":
            second_id = str(case["secondary_tool_call_id"])
            second = guard.evaluate(_request(document, case, second_id))
            first_receipt = consume_decision(decision, handler=handler)
            second_receipt = consume_decision(second, handler=handler)
            assert [first_receipt["tool_call_id"], second_receipt["tool_call_id"]] == [request.tool_call_id, second_id]
            receipt = first_receipt
            settlement_count = 2
            identity_preserved = True
        elif scenario == "sync_async_parity":
            sync_receipt = consume_decision(decision, handler=handler)

            async def async_handler() -> None:
                nonlocal counter
                counter += 1

            async_decision = asyncio.run(guard.aevaluate(request))
            async_receipt = asyncio.run(aconsume_decision(async_decision, handler=async_handler))
            semantic_keys = ("policy_decision", "reason_code", "execution_outcome", "tool_failure")
            assert tuple(sync_receipt[key] for key in semantic_keys) == tuple(async_receipt[key] for key in semantic_keys)
            receipt = sync_receipt
            settlement_count = 2
            identity_preserved = True
        else:
            receipt = consume_decision(decision, handler=handler, host_outcome=host_outcome)
            settlement_count = 1
            identity_preserved = receipt["tool_call_id"] == request.tool_call_id
        if decision.action == "block":
            assert counter == 0
            assert receipt["dispatch_occurred"] is False
            assert receipt["execution_outcome"] == "not_executed"
            assert receipt["tool_failure"] is False
        elif scenario == "handler_failure":
            assert receipt["policy_decision"] == "allow"
            assert receipt["execution_outcome"] == "execution_failed"
        elif scenario == "interrupt":
            assert counter == 0
            assert receipt["policy_decision"] == "allow"
            assert receipt["execution_outcome"] == "interrupted"
            assert receipt["tool_failure"] is False
        safe = _safe(receipt, decision.to_safe_dict())
        assert safe
        return _result(
            document, case, adapter_id,
            policy_decision=decision.action, policy_reason=decision.reason_code,
            dispatch_observed=bool(receipt["dispatch_occurred"]),
            handler_started=bool(receipt["handler_started"]),
            execution_outcome=str(receipt["execution_outcome"]),
            interruption_observed=receipt["execution_outcome"] == "interrupted",
            safe_output=safe, terminal_settlement_count=settlement_count,
            identity_preserved=identity_preserved,
        )
    except BaseException as error:
        return _failed(document, case, adapter_id, error)


def _langgraph_tool(case: Mapping[str, Any], counter: dict[str, int]) -> Any:
    tool_name = str(case["tool_name"])
    scenario = case["host_scenario"]
    if scenario == "interrupt":
        @tool(tool_name)
        def interrupting_tool(operation: str, protected: dict[str, str]) -> str:
            """Pause through the real LangGraph interrupt control-flow path."""

            del operation, protected
            counter["count"] += 1
            return interrupt("synthetic host pause")

        return interrupting_tool
    if scenario == "handler_failure":
        @tool(tool_name)
        def failing_tool(operation: str, protected: dict[str, str]) -> str:
            """Fail after the real LangGraph tool body starts."""

            del operation, protected
            counter["count"] += 1
            raise RuntimeError("synthetic handler failure")

        return failing_tool

    @tool(tool_name)
    def successful_tool(operation: str, protected: dict[str, str]) -> str:
        """Complete a deterministic local-only tool body."""

        del operation, protected
        counter["count"] += 1
        return "ok"

    return successful_tool


def _langgraph_call(document: Mapping[str, Any], case: Mapping[str, Any], call_id: str) -> dict[str, Any]:
    return {
        "name": case["tool_name"],
        "args": fixture_arguments(document),
        "id": call_id,
        "type": "tool_call",
    }


def _run_langgraph_once(
    document: Mapping[str, Any],
    case: Mapping[str, Any],
    *,
    async_mode: bool = False,
) -> tuple[int, list[ToolMessage], tuple[Any, ...]]:
    counter = {"count": 0}
    adapter = LangGraphRuntimeGuardAdapter(_guard(case))
    builder = StateGraph(MessagesState)
    builder.add_node("tools", adapter.create_tool_node([_langgraph_tool(case, counter)]))
    builder.add_edge(START, "tools")
    builder.add_edge("tools", END)
    calls = [_langgraph_call(document, case, str(case["tool_call_id"]))]
    if case["host_scenario"] == "identity":
        calls.append(_langgraph_call(document, case, str(case["secondary_tool_call_id"])))
    inputs = {"messages": [AIMessage(content="", tool_calls=calls)]}
    if case["host_scenario"] == "interrupt":
        graph = builder.compile(checkpointer=InMemorySaver())
        config = {"configurable": {"thread_id": str(case["tool_call_id"])}}
        list(graph.stream(inputs, config=config, stream_mode="updates"))
        messages: list[ToolMessage] = []
    else:
        graph = builder.compile()
        if async_mode:
            output = asyncio.run(graph.ainvoke(inputs))
        else:
            output = graph.invoke(inputs)
        messages = [message for message in output["messages"] if isinstance(message, ToolMessage)]
    return counter["count"], messages, adapter.receipts


def run_langgraph(document: Mapping[str, Any], case: Mapping[str, Any]) -> ConformanceResult:
    adapter_id = "langgraph-tool-node"
    try:
        counter, messages, receipts = _run_langgraph_once(document, case)
        assert receipts
        first = receipts[0]
        expected = case["expected_policy"]
        assert first.decision == expected["decision"]
        assert first.reason_code == expected["reason"]
        assert first.evidence.trace_metadata.args_hash == document["expected_arguments_digest"]
        scenario = case["host_scenario"]
        if first.decision == "block":
            assert counter == 0
            assert first.outcome == "not_executed" and not first.tool_failure
            assert not first.dispatch_occurred and not first.handler_started
        elif scenario == "handler_failure":
            assert counter == 1 and first.decision == "allow"
            assert first.outcome == "execution_failed" and first.tool_failure
        elif scenario == "interrupt":
            assert counter == 1 and first.decision == "allow"
            assert first.outcome == "interrupted" and not first.tool_failure
        if scenario == "reevaluate":
            guard = _guard(case)
            request = _request(document, case)
            assert guard.evaluate(request).to_safe_dict() == guard.evaluate(request).to_safe_dict()
        if scenario == "identity":
            expected_ids = [str(case["tool_call_id"]), str(case["secondary_tool_call_id"])]
            assert [receipt.tool_call_id for receipt in receipts] == expected_ids
            assert [message.tool_call_id for message in messages] == expected_ids
        if scenario == "sync_async_parity":
            async_counter, async_messages, async_receipts = _run_langgraph_once(document, case, async_mode=True)
            assert async_counter == counter == 1
            assert [(receipt.decision, receipt.reason_code, receipt.outcome) for receipt in receipts] == [
                (receipt.decision, receipt.reason_code, receipt.outcome) for receipt in async_receipts
            ]
            assert [message.status for message in messages] == [message.status for message in async_messages]
        if scenario == "terminal_settlement":
            assert len(receipts) == 1 and len(messages) == 1
        safe_values = (
            [receipt.to_safe_dict() for receipt in receipts],
            [message.content for message in messages],
        )
        safe = _safe(*safe_values)
        assert safe
        terminal_count = None if scenario == "interrupt" else len(messages)
        return _result(
            document, case, adapter_id,
            policy_decision=first.decision, policy_reason=first.reason_code,
            dispatch_observed=first.dispatch_occurred, handler_started=first.handler_started,
            execution_outcome=first.outcome, interruption_observed=first.outcome == "interrupted",
            safe_output=safe, terminal_settlement_count=terminal_count,
            identity_preserved=(
                [receipt.tool_call_id for receipt in receipts]
                == [str(case["tool_call_id"])]
                + ([str(case["secondary_tool_call_id"])] if scenario == "identity" else [])
            ),
        )
    except BaseException as error:
        return _failed(document, case, adapter_id, error)


def run_conformance(document: Mapping[str, Any] | None = None) -> list[ConformanceResult]:
    fixture_document = dict(document or load_fixture_document())
    runners = (run_python_runtime_guard, run_reference_consumer, run_langgraph)
    results = [
        runner(fixture_document, case)
        for case in fixture_document["cases"]
        for runner in runners
    ]
    return sorted(results, key=lambda result: (result.case_id, ADAPTER_IDS.index(result.adapter_id)))


def render_matrix(results: list[ConformanceResult]) -> str:
    by_case = {(result.case_id, result.adapter_id): result.verdict for result in results}
    headers = ("CASE", *ADAPTER_IDS)
    rows = [headers]
    for case_id in sorted({result.case_id for result in results}):
        rows.append((case_id, *(by_case[(case_id, adapter)] for adapter in ADAPTER_IDS)))
    widths = [max(len(str(row[index])) for row in rows) for index in range(len(headers))]
    return "\n".join(
        "  ".join(str(value).ljust(widths[index]) for index, value in enumerate(row)).rstrip()
        for row in rows
    )


def summary(results: list[ConformanceResult]) -> dict[str, Any]:
    return {
        "fixture_version": results[0].fixture_version if results else None,
        "result_count": len(results),
        "counts": {
            verdict: sum(result.verdict == verdict for result in results)
            for verdict in ("PASS", "FAIL", "NOT_APPLICABLE")
        },
        "results": [asdict(result) for result in results],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()
    results = run_conformance()
    report = summary(results)
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    if not args.json_only:
        print(render_matrix(results))
    if report["counts"]["FAIL"]:
        raise SystemExit("AGENTFUSE_CROSS_ADAPTER_CONFORMANCE_V3_6_2_FAIL")
    print(FINAL_VERDICT)


if __name__ == "__main__":
    main()
