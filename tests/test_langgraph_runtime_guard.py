"""Real LangGraph ToolNode tests for the AgentFuse Runtime Guard adapter."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import MessagesState, StateGraph

from dhms_agentfuse import LangGraphRuntimeGuardAdapter, RuntimeGuard


def _run_graph(
    calls: list[dict[str, Any]],
) -> tuple[dict[str, int], list[ToolMessage], LangGraphRuntimeGuardAdapter]:
    counters = {"delete_file": 0, "read_summary": 0, "failing_tool": 0}

    @tool
    def delete_file(path: str) -> str:
        """Synthetic deletion handler."""

        counters["delete_file"] += 1
        return "deleted"

    @tool
    def read_summary(value: str) -> str:
        """Read a synthetic summary."""

        counters["read_summary"] += 1
        return f"summary:{value}"

    @tool
    def failing_tool(value: str) -> str:
        """Raise after starting without performing an external side effect."""

        counters["failing_tool"] += 1
        raise RuntimeError("RAW_LANGGRAPH_FAILURE_MUST_NOT_APPEAR")

    adapter = LangGraphRuntimeGuardAdapter(
        RuntimeGuard(
            allow_tools={"read_summary", "failing_tool"},
            deny_tools={"delete_file"},
        )
    )
    builder = StateGraph(MessagesState)
    builder.add_node(
        "tools", adapter.create_tool_node([delete_file, read_summary, failing_tool])
    )
    builder.set_entry_point("tools")
    builder.set_finish_point("tools")
    graph = builder.compile()
    output = graph.invoke({"messages": [AIMessage(content="", tool_calls=calls)]})
    messages = [message for message in output["messages"] if isinstance(message, ToolMessage)]
    return counters, messages, adapter


def _call(name: str, call_id: str) -> dict[str, Any]:
    argument_name = "path" if name == "delete_file" else "value"
    return {
        "name": name,
        "args": {argument_name: "RAW_PROTECTED_LANGGRAPH_ARGUMENT"},
        "id": call_id,
        "type": "tool_call",
    }


def test_real_langgraph_blocked_handler_count_remains_zero() -> None:
    counters, messages, adapter = _run_graph([_call("delete_file", "call-blocked")])

    assert counters["delete_file"] == 0
    assert messages[0].tool_call_id == "call-blocked"
    assert adapter.receipt_for("call-blocked").outcome == "not_executed"


def test_real_langgraph_allowed_handler_executes_once() -> None:
    counters, messages, adapter = _run_graph([_call("read_summary", "call-allowed")])

    assert counters["read_summary"] == 1
    assert messages[0].status == "success"
    assert adapter.receipt_for("call-allowed").outcome == "executed"


def test_terminal_tool_result_preserves_original_call_id() -> None:
    _, messages, adapter = _run_graph([_call("delete_file", "stable-tool-call-id")])

    assert messages[0].tool_call_id == "stable-tool-call-id"
    assert adapter.receipt_for("stable-tool-call-id").tool_call_id == "stable-tool-call-id"


def test_mixed_calls_receive_terminal_results_and_allowed_sibling_continues() -> None:
    calls = [
        _call("delete_file", "call-blocked"),
        _call("read_summary", "call-allowed"),
    ]
    counters, messages, adapter = _run_graph(calls)

    assert [message.tool_call_id for message in messages] == ["call-blocked", "call-allowed"]
    assert counters == {"delete_file": 0, "read_summary": 1, "failing_tool": 0}
    assert len(adapter.receipts) == 2


def test_allowed_handler_failure_remains_transcript_complete() -> None:
    counters, messages, adapter = _run_graph([_call("failing_tool", "call-failure")])
    receipt = adapter.receipt_for("call-failure")

    assert counters["failing_tool"] == 1
    assert len(messages) == 1
    assert messages[0].status == "error"
    assert messages[0].tool_call_id == "call-failure"
    assert receipt.decision == "allow"
    assert receipt.outcome == "execution_failed"
    assert receipt.side_effect_occurred is None


def test_denial_is_not_represented_as_successful_execution() -> None:
    _, messages, adapter = _run_graph([_call("delete_file", "call-blocked")])
    receipt = adapter.receipt_for("call-blocked")

    assert messages[0].status == "error"
    assert receipt.tool_failure is False
    assert receipt.outcome == "not_executed"


def test_evidence_receipt_is_generated_by_adapter_guard_path() -> None:
    _, _, adapter = _run_graph([_call("delete_file", "call-evidence")])
    receipt = adapter.receipt_for("call-evidence")

    assert receipt.evidence.record_id == "runtime-guard-evidence:call-evidence"
    assert receipt.evidence.non_execution is not None
    assert receipt.evidence.non_execution.call_id == "call-evidence"


def test_langgraph_default_outputs_redact_blocked_arguments_and_exceptions() -> None:
    _, messages, adapter = _run_graph(
        [
            _call("delete_file", "call-blocked"),
            _call("failing_tool", "call-failure"),
        ]
    )
    serialized = json.dumps(
        {
            "messages": [message.content for message in messages],
            "receipts": [receipt.to_safe_dict() for receipt in adapter.receipts],
        },
        sort_keys=True,
    )

    assert "RAW_PROTECTED_LANGGRAPH_ARGUMENT" not in serialized
    assert "RAW_LANGGRAPH_FAILURE_MUST_NOT_APPEAR" not in serialized


def test_real_langgraph_async_tool_path_is_guarded() -> None:
    counters = {"async_read": 0}

    @tool
    async def async_read(value: str) -> str:
        """Read a deterministic value asynchronously."""

        counters["async_read"] += 1
        return f"async:{value}"

    adapter = LangGraphRuntimeGuardAdapter(RuntimeGuard(allow_tools={"async_read"}))
    builder = StateGraph(MessagesState)
    builder.add_node("tools", adapter.create_tool_node([async_read]))
    builder.set_entry_point("tools")
    builder.set_finish_point("tools")
    graph = builder.compile()
    output = asyncio.run(
        graph.ainvoke(
            {
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[_call("async_read", "call-async")],
                    )
                ]
            }
        )
    )

    messages = [message for message in output["messages"] if isinstance(message, ToolMessage)]
    assert counters["async_read"] == 1
    assert messages[0].tool_call_id == "call-async"
    assert adapter.receipt_for("call-async").outcome == "executed"


def test_unregistered_allowed_tool_does_not_claim_handler_started() -> None:
    @tool
    def registered_tool(value: str) -> str:
        """Return a registered deterministic value."""

        return value

    adapter = LangGraphRuntimeGuardAdapter(
        RuntimeGuard(allow_tools={"missing_tool", "registered_tool"})
    )
    builder = StateGraph(MessagesState)
    builder.add_node("tools", adapter.create_tool_node([registered_tool]))
    builder.set_entry_point("tools")
    builder.set_finish_point("tools")
    graph = builder.compile()
    output = graph.invoke(
        {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[_call("missing_tool", "call-missing")],
                )
            ]
        }
    )
    receipt = adapter.receipt_for("call-missing")

    assert isinstance(output["messages"][-1], ToolMessage)
    assert receipt.handler_started is False
    assert receipt.failure_category == "unregistered_tool"
    assert receipt.side_effect_occurred is False


def test_tool_input_validation_error_does_not_claim_handler_started() -> None:
    counters = {"read": 0}

    @tool
    def read_summary(value: str) -> str:
        """Read a deterministic summary."""

        counters["read"] += 1
        return value

    adapter = LangGraphRuntimeGuardAdapter(RuntimeGuard(allow_tools={"read_summary"}))
    builder = StateGraph(MessagesState)
    builder.add_node("tools", adapter.create_tool_node([read_summary]))
    builder.set_entry_point("tools")
    builder.set_finish_point("tools")
    graph = builder.compile()
    graph.invoke(
        {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "read_summary",
                            "args": {},
                            "id": "call-invalid-input",
                            "type": "tool_call",
                        }
                    ],
                )
            ]
        }
    )
    receipt = adapter.receipt_for("call-invalid-input")

    assert counters["read"] == 0
    assert receipt.handler_started is False
    assert receipt.failure_category == "tool_input_error"
    assert receipt.side_effect_occurred is False
