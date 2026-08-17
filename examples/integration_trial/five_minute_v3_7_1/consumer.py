"""Small public-API LangGraph consumer for the AgentFuse v3.7.1 trial."""

from __future__ import annotations

from importlib.metadata import version
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import MessagesState, StateGraph

from dhms_agentfuse import LangGraphRuntimeGuardAdapter, RuntimeGuard
from dhms_agentfuse.integrations import get_integration


TRIAL_VERSION = "agentfuse-five-minute-integration-trial-v3.7.1"
INTEGRATION_ID = "langgraph-tool-node"
ALLOW_CALL_ID = "trial-allow-001"
BLOCK_CALL_ID = "trial-block-001"
SYNTHETIC_PROTECTED_ARGUMENT = "synthetic-protected-value-v3-7-1"


def _tool_call(name: str, call_id: str) -> dict[str, Any]:
    return {
        "name": name,
        "args": {"value": SYNTHETIC_PROTECTED_ARGUMENT},
        "id": call_id,
        "type": "tool_call",
    }


def _terminal_message(output: dict[str, Any]) -> ToolMessage:
    messages = [message for message in output["messages"] if isinstance(message, ToolMessage)]
    if len(messages) != 1:
        raise RuntimeError("expected exactly one terminal ToolMessage")
    return messages[0]


def run_trial() -> dict[str, Any]:
    """Run one allowed and one blocked call through a real LangGraph ToolNode."""

    profile = get_integration(INTEGRATION_ID)
    observed_version = version("langgraph")
    if observed_version != profile.tested_version:
        raise RuntimeError(
            f"trial requires langgraph {profile.tested_version}, found {observed_version}"
        )

    counts = {"trusted_summary": 0, "restricted_mutation": 0}

    @tool
    def trusted_summary(value: str) -> str:
        """Return an in-memory synthetic summary."""

        counts["trusted_summary"] += 1
        return "synthetic-summary-complete"

    @tool
    def restricted_mutation(value: str) -> str:
        """Represent a protected mutation using only an in-memory counter."""

        counts["restricted_mutation"] += 1
        return "synthetic-mutation-complete"

    adapter = LangGraphRuntimeGuardAdapter(
        RuntimeGuard(
            allow_tools={"trusted_summary"},
            deny_tools={"restricted_mutation"},
            default_action="block",
        )
    )
    builder = StateGraph(MessagesState)
    builder.add_node("tools", adapter.create_tool_node([trusted_summary, restricted_mutation]))
    builder.set_entry_point("tools")
    builder.set_finish_point("tools")
    graph = builder.compile()

    allow_message = _terminal_message(
        graph.invoke({"messages": [AIMessage(content="", tool_calls=[_tool_call("trusted_summary", ALLOW_CALL_ID)])]})
    )
    block_message = _terminal_message(
        graph.invoke({"messages": [AIMessage(content="", tool_calls=[_tool_call("restricted_mutation", BLOCK_CALL_ID)])]})
    )
    allow_receipt = adapter.receipt_for(ALLOW_CALL_ID)
    block_receipt = adapter.receipt_for(BLOCK_CALL_ID)

    result = {
        "trial_version": TRIAL_VERSION,
        "integration_id": profile.integration_id,
        "runtime": {
            "name": profile.tested_runtime,
            "expected_version": profile.tested_version,
            "observed_version": observed_version,
        },
        "requirements": {
            "api_key_required": False,
            "network_required_at_runtime": False,
            "model_call_required": False,
        },
        "cases": [
            {
                "case_id": "allow",
                "tool_call_id": ALLOW_CALL_ID,
                "policy_decision": allow_receipt.decision,
                "execution_outcome": allow_receipt.outcome,
                "protected_handler_started": allow_receipt.handler_started,
                "protected_handler_count": counts["trusted_summary"],
                "tool_call_identity_preserved": allow_message.tool_call_id == allow_receipt.tool_call_id == ALLOW_CALL_ID,
                "verdict": "PASS",
            },
            {
                "case_id": "block",
                "tool_call_id": BLOCK_CALL_ID,
                "policy_decision": block_receipt.decision,
                "execution_outcome": block_receipt.outcome,
                "dispatch_observed": block_receipt.dispatch_occurred,
                "protected_handler_started": block_receipt.handler_started,
                "protected_handler_count": counts["restricted_mutation"],
                "tool_call_identity_preserved": block_message.tool_call_id == block_receipt.tool_call_id == BLOCK_CALL_ID,
                "verdict": "PASS",
            },
        ],
        "verdict": "PASS",
    }
    _validate(result)
    return result


def _validate(result: dict[str, Any]) -> None:
    allow, block = result["cases"]
    assert result["integration_id"] == INTEGRATION_ID
    assert result["runtime"]["observed_version"] == "1.2.11"
    assert allow["policy_decision"] == "allow"
    assert allow["execution_outcome"] == "executed"
    assert allow["protected_handler_started"] is True
    assert allow["protected_handler_count"] == 1
    assert allow["tool_call_identity_preserved"] is True
    assert block["policy_decision"] == "block"
    assert block["execution_outcome"] == "not_executed"
    assert block["dispatch_observed"] is False
    assert block["protected_handler_started"] is False
    assert block["protected_handler_count"] == 0
    assert block["tool_call_identity_preserved"] is True
