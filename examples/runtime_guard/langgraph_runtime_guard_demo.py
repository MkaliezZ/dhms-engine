#!/usr/bin/env python3
"""Real installed-LangGraph ToolNode Runtime Guard demo with no model/provider."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import MessagesState, StateGraph

from dhms_agentfuse import LangGraphRuntimeGuardAdapter, RuntimeGuard


FINAL_VERDICT = "AGENTFUSE_LANGGRAPH_RUNTIME_GUARD_DEMO_PASS"


def run_demo() -> dict[str, Any]:
    counters = {
        "delete_file": 0,
        "read_project_summary": 0,
        "execute_production_sql": 0,
    }

    @tool
    def delete_file(path: str) -> str:
        """Synthetic file deletion handler that only increments an in-memory counter."""

        counters["delete_file"] += 1
        return "synthetic-delete-result"

    @tool
    def read_project_summary(project: str) -> str:
        """Return a deterministic in-memory project summary."""

        counters["read_project_summary"] += 1
        return f"synthetic-summary:{project}"

    @tool
    def execute_production_sql(statement: str) -> str:
        """Synthetic failing handler that never connects to a database."""

        counters["execute_production_sql"] += 1
        raise RuntimeError("SYNTHETIC_PROTECTED_EXCEPTION_TEXT")

    guard = RuntimeGuard(
        allow_tools={"read_project_summary", "execute_production_sql"},
        deny_tools={"delete_file"},
        default_action="block",
    )
    adapter = LangGraphRuntimeGuardAdapter(guard)
    builder = StateGraph(MessagesState)
    builder.add_node(
        "tools",
        adapter.create_tool_node(
            [delete_file, read_project_summary, execute_production_sql]
        ),
    )
    builder.set_entry_point("tools")
    builder.set_finish_point("tools")
    graph = builder.compile()

    calls = [
        {
            "name": "delete_file",
            "args": {"path": "synthetic-example.txt"},
            "id": "langgraph-call-delete-001",
            "type": "tool_call",
        },
        {
            "name": "read_project_summary",
            "args": {"project": "agentfuse-local-demo"},
            "id": "langgraph-call-read-001",
            "type": "tool_call",
        },
        {
            "name": "execute_production_sql",
            "args": {"statement": "SYNTHETIC_PROTECTED_SQL_TEXT"},
            "id": "langgraph-call-failure-001",
            "type": "tool_call",
        },
    ]
    output = graph.invoke({"messages": [AIMessage(content="", tool_calls=calls)]})
    terminal_messages = [
        message for message in output["messages"] if isinstance(message, ToolMessage)
    ]
    receipts = [adapter.receipt_for(call["id"]) for call in calls]
    summary = {
        "real_langgraph_graph_compiled": True,
        "real_langgraph_graph_invoked": True,
        "real_tool_node_dispatch": True,
        "handler_execution_counts": counters,
        "tool_messages": [
            {
                "tool_call_id": message.tool_call_id,
                "tool_name": message.name,
                "status": message.status,
                "content": message.content,
            }
            for message in terminal_messages
        ],
        "receipts": [receipt.to_safe_dict() for receipt in receipts],
        "every_call_has_terminal_message": len(terminal_messages) == len(calls),
        "original_call_order_preserved": [message.tool_call_id for message in terminal_messages]
        == [call["id"] for call in calls],
        "no_model_or_provider_call": True,
        "no_real_file_operation": True,
        "no_real_sql_execution": True,
        "no_network": True,
        "final_verdict": FINAL_VERDICT,
    }
    _validate(summary)
    return summary


def _validate(summary: dict[str, Any]) -> None:
    assert summary["handler_execution_counts"] == {
        "delete_file": 0,
        "read_project_summary": 1,
        "execute_production_sql": 1,
    }
    receipts = {receipt["tool_name"]: receipt for receipt in summary["receipts"]}
    assert receipts["delete_file"]["outcome"] == "not_executed"
    assert receipts["read_project_summary"]["outcome"] == "executed"
    assert receipts["execute_production_sql"]["outcome"] == "execution_failed"
    assert receipts["execute_production_sql"]["side_effect_occurred"] is None
    assert summary["every_call_has_terminal_message"] is True
    assert summary["original_call_order_preserved"] is True


def main() -> None:
    summary = run_demo()
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(FINAL_VERDICT)


if __name__ == "__main__":
    main()
