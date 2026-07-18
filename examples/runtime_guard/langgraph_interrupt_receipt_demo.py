#!/usr/bin/env python3
"""Issue-shaped LangGraph interrupt receipt demo for langgraph#8218."""

from __future__ import annotations

import json
from typing import Annotated, Any

from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import interrupt
from typing_extensions import TypedDict

from dhms_agentfuse import LangGraphRuntimeGuardAdapter, RuntimeGuard


FINAL_VERDICT = "AGENTFUSE_LANGGRAPH_INTERRUPT_RECEIPT_DEMO_PASS"
THREAD_ID = "agentfuse-langgraph-8218-interrupt-demo"
TOOL_CALL_ID = "langgraph-8218-call-001"
PRIVATE_INTERRUPT_PAYLOAD = "SYNTHETIC_PRIVATE_APPROVAL_QUESTION"


class State(TypedDict):
    messages: Annotated[list, add_messages]


@tool
def ask_human(question: str) -> str:
    """Pause the graph for a synthetic human response."""

    return interrupt(question)


def _caller(state: State) -> dict[str, Any]:
    return {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "ask_human",
                        "args": {"question": PRIVATE_INTERRUPT_PAYLOAD},
                        "id": TOOL_CALL_ID,
                        "type": "tool_call",
                    }
                ],
            )
        ]
    }


def run_demo() -> dict[str, Any]:
    guard = RuntimeGuard(allow_tools={"ask_human"}, default_action="block")
    adapter = LangGraphRuntimeGuardAdapter(guard)
    builder = StateGraph(State)
    builder.add_node("caller", _caller)
    builder.add_node("tools", adapter.create_tool_node([ask_human]))
    builder.add_edge(START, "caller")
    builder.add_edge("caller", "tools")
    builder.add_edge("tools", END)
    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": THREAD_ID}}

    tools_stream_events: list[str] = []
    for _, mode, payload in graph.stream(
        {"messages": []},
        config=config,
        stream_mode=["tools"],
        subgraphs=True,
    ):
        if mode == "tools":
            tools_stream_events.append(str(payload.get("event", "unknown")))

    state_snapshot = graph.get_state(config)
    interrupts = state_snapshot.interrupts
    receipt = adapter.receipt_for(TOOL_CALL_ID)
    safe_receipt = receipt.to_safe_dict()
    serialized_safe_receipt = json.dumps(safe_receipt, sort_keys=True)
    summary = {
        "tool_name": receipt.tool_name,
        "tool_call_id": receipt.tool_call_id,
        "decision": receipt.decision,
        "dispatch_started": receipt.dispatch_occurred,
        "handler_started": receipt.handler_started,
        "outcome": receipt.outcome,
        "execution_failed": receipt.tool_failure,
        "side_effect_occurred": receipt.side_effect_occurred,
        "non_execution_evidence_present": receipt.evidence.non_execution is not None,
        "graph_interrupt_count": len(interrupts),
        "structured_interrupt_preserved": len(interrupts) == 1
        and interrupts[0].value == PRIVATE_INTERRUPT_PAYLOAD,
        "interrupt_payload_redacted": PRIVATE_INTERRUPT_PAYLOAD
        not in serialized_safe_receipt
        and PRIVATE_INTERRUPT_PAYLOAD not in repr(receipt)
        and "Interrupt(value=" not in serialized_safe_receipt
        and "Interrupt(value=" not in repr(receipt),
        "langgraph_tools_stream_events": tools_stream_events,
        "safe_receipt": safe_receipt,
        "final_verdict": FINAL_VERDICT,
    }
    _validate(summary)
    return summary


def _validate(summary: dict[str, Any]) -> None:
    assert summary["tool_name"] == "ask_human"
    assert summary["tool_call_id"] == TOOL_CALL_ID
    assert summary["decision"] == "allow"
    assert summary["dispatch_started"] is True
    assert summary["handler_started"] is True
    assert summary["outcome"] == "interrupted"
    assert summary["execution_failed"] is False
    assert summary["side_effect_occurred"] is None
    assert summary["non_execution_evidence_present"] is False
    assert summary["graph_interrupt_count"] == 1
    assert summary["structured_interrupt_preserved"] is True
    assert summary["interrupt_payload_redacted"] is True
    safe_receipt = summary["safe_receipt"]
    assert safe_receipt["outcome"] == "interrupted"
    assert safe_receipt["tool_failure"] is False


def main() -> None:
    summary = run_demo()
    print(f"tool_name={summary['tool_name']}")
    print(f"decision={summary['decision']}")
    print(f"dispatch_started={str(summary['dispatch_started']).lower()}")
    print(f"outcome={summary['outcome']}")
    print(f"execution_failed={str(summary['execution_failed']).lower()}")
    print(
        "interrupt_payload_redacted="
        f"{str(summary['interrupt_payload_redacted']).lower()}"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(FINAL_VERDICT)


if __name__ == "__main__":
    main()
