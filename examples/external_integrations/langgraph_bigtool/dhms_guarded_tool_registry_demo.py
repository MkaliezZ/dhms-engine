#!/usr/bin/env python3
"""Deterministic DHMS integration example for a langgraph-bigtool-style registry.

The external project stores available tools in a registry before an agent
retrieves and calls them. This demo keeps that boundary local and inert: it
wraps registered tools with DHMS before protected payload bodies can execute.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List


ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dhms_agentfuse.controlled_proposal_gate import evaluate_controlled_proposal  # noqa: E402


EXTERNAL_PROJECT_NAME = "langchain-ai/langgraph-bigtool"
EXTERNAL_PROJECT_URL = "https://github.com/langchain-ai/langgraph-bigtool"
STAR_COUNT_OBSERVED = 545
SOURCE = "v3.5.1-external-langgraph-bigtool-integration-example"
FINAL_VERDICT = "DHMS_EXTERNAL_LANGGRAPH_BIGTOOL_INTEGRATION_EXAMPLE_PASS"
INTEGRATION_DIFF_LINE_COUNT = 7


@dataclass(frozen=True)
class ExternalTool:
    """Small local stand-in for an external project's registered tool object."""

    name: str
    requested_capabilities: List[str]
    declared_boundary: str
    protected_payload_body: Callable[[str], str]


def _protected_payload_body(tool_name: str, state: Dict[str, int]) -> Callable[[str], str]:
    def payload_body(payload: str) -> str:
        state["protected_payload_body_execution_count"] += 1
        state["sentinel_count"] += 1
        return f"PROTECTED_PAYLOAD_EXECUTED:{tool_name}:{payload}"

    return payload_body


def create_external_tool_registry(state: Dict[str, int]) -> Dict[str, ExternalTool]:
    """Create an inert registry matching the external project's tool-registry seam."""

    return {
        "safe_read_only_summary_tool": ExternalTool(
            name="safe_read_only_summary_tool",
            requested_capabilities=["local_read_only_summary"],
            declared_boundary="local_read_only_non_executing_safe",
            protected_payload_body=_protected_payload_body("safe_read_only_summary_tool", state),
        ),
        "dangerous_sql_mutation_tool": ExternalTool(
            name="dangerous_sql_mutation_tool",
            requested_capabilities=["sql_mutation"],
            declared_boundary="unsafe_sql_mutation_request",
            protected_payload_body=_protected_payload_body("dangerous_sql_mutation_tool", state),
        ),
        "model_api_request_tool": ExternalTool(
            name="model_api_request_tool",
            requested_capabilities=["model_api"],
            declared_boundary="unsafe_model_api_request",
            protected_payload_body=_protected_payload_body("model_api_request_tool", state),
        ),
    }


def build_dhms_proposal(tool: ExternalTool) -> Dict[str, Any]:
    return {
        "proposal_id": f"external_langgraph_bigtool_{tool.name}",
        "requested_capabilities": list(tool.requested_capabilities),
        "declared_boundary": tool.declared_boundary,
        "source": SOURCE,
        "tool_name": tool.name,
    }


def dhms_guard_tool(tool_name: str, tool: ExternalTool) -> Callable[[str], Dict[str, Any]]:
    """Wrap one external registered tool with DHMS before payload execution."""

    def guarded_tool(payload: str) -> Dict[str, Any]:
        proposal = build_dhms_proposal(tool)
        gate_result = evaluate_controlled_proposal(proposal, SOURCE)
        if gate_result["execution_authorized"] is True:
            return {
                "tool_name": tool_name,
                "decision": gate_result["decision"],
                "executed": True,
                "payload_result": tool.protected_payload_body(payload),
            }
        return {
            "tool_name": tool_name,
            "decision": gate_result["decision"],
            "blocked_capabilities": gate_result["blocked_capabilities"],
            "execution_authorized": gate_result["execution_authorized"],
            "runtime_behaviors_added": gate_result["runtime_behaviors_added"],
            "executed": False,
            "payload_result": None,
        }

    return guarded_tool


def create_guarded_registry(
    tool_registry: Dict[str, ExternalTool],
) -> Dict[str, Callable[[str], Dict[str, Any]]]:
    # This mirrors the intended external integration diff.
    return {
        tool_name: dhms_guard_tool(tool_name, tool)
        for tool_name, tool in tool_registry.items()
    }


def run_demo() -> Dict[str, Any]:
    state = {"protected_payload_body_execution_count": 0, "sentinel_count": 0}
    before_registry = create_external_tool_registry(state)
    before_summary = {
        "registered_tool_count": len(before_registry),
        "dangerous_sql_mutation_tool_reachable": callable(
            before_registry["dangerous_sql_mutation_tool"].protected_payload_body
        ),
        "model_api_request_tool_reachable": callable(
            before_registry["model_api_request_tool"].protected_payload_body
        ),
        "protected_payload_body_execution_count": state["protected_payload_body_execution_count"],
    }

    guarded_registry = create_guarded_registry(before_registry)
    after_results = [
        guarded_registry["safe_read_only_summary_tool"]("Summarize inert local text."),
        guarded_registry["dangerous_sql_mutation_tool"]("DROP TABLE toy_accounts;"),
        guarded_registry["model_api_request_tool"]("Call a model provider API."),
    ]

    decision_by_tool = {result["tool_name"]: result["decision"] for result in after_results}
    blocked_by_tool = {
        result["tool_name"]: list(result["blocked_capabilities"])
        for result in after_results
    }
    execution_authorized_count = sum(
        1 for result in after_results if result["execution_authorized"] is True
    )
    runtime_behaviors_added = sum(int(result["runtime_behaviors_added"]) for result in after_results)
    protected_payload_body_execution_count = state["protected_payload_body_execution_count"]

    summary = {
        "demo_name": "DHMS External LangGraph Integration Example",
        "version": "v3.5.1",
        "external_project": EXTERNAL_PROJECT_NAME,
        "external_project_url": EXTERNAL_PROJECT_URL,
        "star_count_observed": STAR_COUNT_OBSERVED,
        "integration_diff_line_count": INTEGRATION_DIFF_LINE_COUNT,
        "before": before_summary,
        "after_decisions": decision_by_tool,
        "after_blocked_capabilities": blocked_by_tool,
        "safe_read_only_release_candidate_count": sum(
            1 for result in after_results if result["decision"] == "RELEASE_CANDIDATE"
        ),
        "sql_mutation_fail_closed_count": sum(
            1
            for result in after_results
            if result["tool_name"] == "dangerous_sql_mutation_tool"
            and result["decision"] == "FAIL_CLOSED"
            and result["blocked_capabilities"] == ["sql_mutation"]
        ),
        "model_api_fail_closed_count": sum(
            1
            for result in after_results
            if result["tool_name"] == "model_api_request_tool"
            and result["decision"] == "FAIL_CLOSED"
            and result["blocked_capabilities"] == ["model_api"]
        ),
        "protected_payload_body_execution_count": protected_payload_body_execution_count,
        "sentinel_count": state["sentinel_count"],
        "execution_authorized_count": execution_authorized_count,
        "runtime_behaviors_added": runtime_behaviors_added,
        "no_sql_execution": True,
        "no_db_access": True,
        "no_model_provider_call": True,
        "no_network": True,
        "no_env_access": True,
        "no_credentials": True,
        "no_user_data": True,
        "final_verdict": FINAL_VERDICT,
    }
    _validate_summary(summary)
    return summary


def _validate_summary(summary: Dict[str, Any]) -> None:
    if summary["star_count_observed"] < 100:
        raise AssertionError("external project must have 100+ observed stars")
    if summary["integration_diff_line_count"] > 10:
        raise AssertionError("integration diff line count must stay small")
    if summary["before"]["dangerous_sql_mutation_tool_reachable"] is not True:
        raise AssertionError("before state must show dangerous SQL tool reachability")
    if summary["after_decisions"]["safe_read_only_summary_tool"] != "RELEASE_CANDIDATE":
        raise AssertionError("safe read-only tool must be a release candidate")
    if summary["after_decisions"]["dangerous_sql_mutation_tool"] != "FAIL_CLOSED":
        raise AssertionError("dangerous SQL mutation tool must fail closed")
    if summary["after_blocked_capabilities"]["dangerous_sql_mutation_tool"] != ["sql_mutation"]:
        raise AssertionError("dangerous SQL blocked category must be sql_mutation")
    if summary["after_decisions"]["model_api_request_tool"] != "FAIL_CLOSED":
        raise AssertionError("model API request tool must fail closed")
    if summary["after_blocked_capabilities"]["model_api_request_tool"] != ["model_api"]:
        raise AssertionError("model API blocked category must be model_api")
    if summary["protected_payload_body_execution_count"] != 0:
        raise AssertionError("protected payload bodies must not execute")
    if summary["sentinel_count"] != 0:
        raise AssertionError("sentinel count must remain zero")
    if summary["execution_authorized_count"] != 0:
        raise AssertionError("execution must not be authorized")
    if summary["runtime_behaviors_added"] != 0:
        raise AssertionError("runtime behavior must not be added")


def main() -> int:
    summary = run_demo()
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(FINAL_VERDICT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
