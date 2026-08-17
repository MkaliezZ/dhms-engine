#!/usr/bin/env python3
"""Run one wheel-installed AgentFuse LangGraph compatibility cell."""

from __future__ import annotations

import argparse
import json
from importlib.metadata import version
from pathlib import Path
import platform
import sys
from typing import Any

import dhms_agentfuse
from dhms_agentfuse import LangGraphRuntimeGuardAdapter, RuntimeGuard
from dhms_agentfuse.integrations import get_integration
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import MessagesState, StateGraph


MATRIX_VERSION = "agentfuse-compatibility-matrix-v3.7.2"
INTEGRATION_ID = "langgraph-tool-node"
ALLOW_CALL_ID = "compat-allow-001"
BLOCK_CALL_ID = "compat-block-001"
SYNTHETIC_PROTECTED_ARGUMENT = "synthetic-protected-value-v3-7-2"
FINAL_VERDICT = "AGENTFUSE_COMPATIBILITY_PROBE_V3_7_2_PASS"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _tool_call(name: str, call_id: str) -> dict[str, Any]:
    return {
        "name": name,
        "args": {"value": SYNTHETIC_PROTECTED_ARGUMENT},
        "id": call_id,
        "type": "tool_call",
    }


def _terminal_message(output: dict[str, Any]) -> ToolMessage:
    messages = [message for message in output["messages"] if isinstance(message, ToolMessage)]
    _require(len(messages) == 1, "expected exactly one terminal ToolMessage")
    return messages[0]


def _outside_forbidden_root(forbidden_root: Path | None) -> bool | None:
    if forbidden_root is None:
        return None
    package_origin = Path(dhms_agentfuse.__file__).resolve()
    try:
        package_origin.relative_to(forbidden_root.resolve())
    except ValueError:
        return True
    return False


def run_probe(
    *,
    expected_python_version: str,
    expected_langgraph_version: str,
    expected_package_version: str,
    forbidden_import_root: Path | None = None,
) -> dict[str, Any]:
    """Exercise allow and block through the installed wrapped ToolNode path."""

    profile = get_integration(INTEGRATION_ID)
    observed_python_version = platform.python_version()
    observed_langgraph_version = version("langgraph")
    observed_package_version = version("dhms-agentfuse")
    import_origin_outside_root = _outside_forbidden_root(forbidden_import_root)

    _require(
        f"{sys.version_info.major}.{sys.version_info.minor}" == expected_python_version,
        f"expected Python {expected_python_version}, found {observed_python_version}",
    )
    _require(
        observed_langgraph_version == expected_langgraph_version,
        f"expected langgraph {expected_langgraph_version}, found {observed_langgraph_version}",
    )
    _require(
        observed_package_version == expected_package_version,
        f"expected dhms-agentfuse {expected_package_version}, found {observed_package_version}",
    )
    if forbidden_import_root is not None:
        _require(import_origin_outside_root is True, "dhms_agentfuse imported from forbidden source root")

    counts = {"trusted_summary": 0, "restricted_mutation": 0}

    @tool
    def trusted_summary(value: str) -> str:
        """Return one synthetic in-memory summary."""

        counts["trusted_summary"] += 1
        return "synthetic-summary-complete"

    @tool
    def restricted_mutation(value: str) -> str:
        """Represent a protected mutation with an in-memory counter."""

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
        graph.invoke(
            {
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[_tool_call("trusted_summary", ALLOW_CALL_ID)],
                    )
                ]
            }
        )
    )
    block_message = _terminal_message(
        graph.invoke(
            {
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[_tool_call("restricted_mutation", BLOCK_CALL_ID)],
                    )
                ]
            }
        )
    )
    allow_receipt = adapter.receipt_for(ALLOW_CALL_ID)
    block_receipt = adapter.receipt_for(BLOCK_CALL_ID)

    result = {
        "matrix_version": MATRIX_VERSION,
        "integration_id": profile.integration_id,
        "package_version": observed_package_version,
        "python_version": observed_python_version,
        "profile_frozen_tested_version": profile.tested_version,
        "candidate_langgraph_version": expected_langgraph_version,
        "observed_langgraph_version": observed_langgraph_version,
        "observed_langchain_core_version": version("langchain-core"),
        "source_isolation": {
            "forbidden_root_checked": forbidden_import_root is not None,
            "import_origin_outside_forbidden_root": import_origin_outside_root,
        },
        "requirements": {
            "api_key_required": False,
            "model_call_required": False,
            "network_required_at_runtime": False,
        },
        "cases": {
            "allow": {
                "decision": allow_receipt.decision,
                "execution_outcome": allow_receipt.outcome,
                "handler_started": allow_receipt.handler_started,
                "handler_count": counts["trusted_summary"],
                "tool_call_identity_preserved": (
                    allow_message.tool_call_id == allow_receipt.tool_call_id == ALLOW_CALL_ID
                ),
            },
            "block": {
                "decision": block_receipt.decision,
                "execution_outcome": block_receipt.outcome,
                "dispatch_observed": block_receipt.dispatch_occurred,
                "handler_started": block_receipt.handler_started,
                "handler_count": counts["restricted_mutation"],
                "tool_call_identity_preserved": (
                    block_message.tool_call_id == block_receipt.tool_call_id == BLOCK_CALL_ID
                ),
            },
        },
        "verdict": "PASS",
    }
    _validate_result(result)
    return result


def _validate_result(result: dict[str, Any]) -> None:
    allow = result["cases"]["allow"]
    block = result["cases"]["block"]
    _require(result["integration_id"] == INTEGRATION_ID, "unexpected integration profile")
    _require(result["profile_frozen_tested_version"] == "1.2.11", "profile provenance changed")
    _require(allow["decision"] == "allow", "allow decision changed")
    _require(allow["execution_outcome"] == "executed", "allow outcome was not executed")
    _require(allow["handler_started"] is True, "allowed handler did not start")
    _require(allow["handler_count"] == 1, "allowed handler count was not one")
    _require(allow["tool_call_identity_preserved"] is True, "allow identity changed")
    _require(block["decision"] == "block", "block decision changed")
    _require(block["execution_outcome"] == "not_executed", "block outcome changed")
    _require(block["dispatch_observed"] is False, "blocked dispatch was observed")
    _require(block["handler_started"] is False, "blocked handler started")
    _require(block["handler_count"] == 0, "blocked handler count was not zero")
    _require(block["tool_call_identity_preserved"] is True, "block identity changed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-python-version", required=True)
    parser.add_argument("--expected-langgraph-version", required=True)
    parser.add_argument("--expected-package-version", default="3.7.2")
    parser.add_argument("--forbid-import-root", type=Path)
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()
    result = run_probe(
        expected_python_version=args.expected_python_version,
        expected_langgraph_version=args.expected_langgraph_version,
        expected_package_version=args.expected_package_version,
        forbidden_import_root=args.forbid_import_root,
    )
    serialized = json.dumps(result, sort_keys=True, separators=(",", ":"))
    _require(SYNTHETIC_PROTECTED_ARGUMENT not in serialized, "protected argument leaked")
    if args.json_only:
        print(serialized)
        return
    print(json.dumps(result, indent=2, sort_keys=True))
    print(FINAL_VERDICT)


if __name__ == "__main__":
    main()
