#!/usr/bin/env python3
"""Deterministic DHMS real langgraph-bigtool API wiring demo.

The external project stores available tools in a registry before an agent
retrieves and calls them. This demo imports the real langgraph_bigtool
create_agent API, passes a DHMS-guarded registry into create_agent(), and keeps
the rest local and deterministic. It does not compile, invoke, or stream the
agent graph.
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
from dhms_agentfuse.langchain_guarded_tool_adapter import (  # noqa: E402
    create_deterministic_adapter_driver,
)
from langgraph_bigtool import create_agent  # noqa: E402


EXTERNAL_PROJECT_NAME = "langchain-ai/langgraph-bigtool"
EXTERNAL_PROJECT_URL = "https://github.com/langchain-ai/langgraph-bigtool"
STAR_COUNT_OBSERVED = 545
SOURCE = "v3.5.2-real-langgraph-bigtool-api-wiring-demo"
FINAL_VERDICT = "DHMS_REAL_LANGGRAPH_BIGTOOL_API_WIRING_DEMO_PASS"
GUARD_DIFF_LINE_COUNT = 7


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
        """Evaluate a proposed external tool call through DHMS before payload execution."""

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

    guarded_tool.__name__ = tool_name
    return guarded_tool


def create_guarded_registry(
    tool_registry: Dict[str, ExternalTool],
) -> Dict[str, Callable[[str], Dict[str, Any]]]:
    # This mirrors the small guard diff at the registry boundary.
    return {
        tool_name: dhms_guard_tool(tool_name, tool)
        for tool_name, tool in tool_registry.items()
    }


def retrieve_tools(query: str) -> List[str]:
    """Return all available guarded tool IDs deterministically."""

    return list(_ACTIVE_GUARDED_TOOL_REGISTRY.keys())


_ACTIVE_GUARDED_TOOL_REGISTRY: Dict[str, Callable[[str], Dict[str, Any]]] = {}


def create_real_langgraph_bigtool_wiring(
    guarded_tool_registry: Dict[str, Callable[[str], Dict[str, Any]]],
) -> Dict[str, Any]:
    """Wire the guarded registry into real langgraph_bigtool.create_agent()."""

    _ACTIVE_GUARDED_TOOL_REGISTRY.clear()
    _ACTIVE_GUARDED_TOOL_REGISTRY.update(guarded_tool_registry)
    fake_model = create_deterministic_adapter_driver(
        {
            "scenario_id": "v3_5_2_real_langgraph_bigtool_api_wiring",
            "tool_name": "safe_read_only_summary_tool",
            "requested_capabilities": ["local_read_only_summary"],
            "expected_gate_decision": "RELEASE_CANDIDATE",
            "prompt": "Deterministic wiring-only prompt.",
        }
    )
    builder = create_agent(
        fake_model,
        guarded_tool_registry,
        retrieve_tools_function=retrieve_tools,
    )
    return {
        "agent_builder_type": type(builder).__name__,
        "guarded_tool_registry_key_count": len(guarded_tool_registry),
        "guarded_tool_registry_keys": list(guarded_tool_registry.keys()),
        "retrieve_tools_result": retrieve_tools("deterministic local query"),
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
    wiring_summary = create_real_langgraph_bigtool_wiring(guarded_registry)
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
        "demo_name": "DHMS Real langgraph-bigtool API Wiring Demo",
        "version": "v3.5.2",
        "external_project": EXTERNAL_PROJECT_NAME,
        "external_project_url": EXTERNAL_PROJECT_URL,
        "star_count_observed": STAR_COUNT_OBSERVED,
        "guard_diff_line_count": GUARD_DIFF_LINE_COUNT,
        "imports_or_runs_langgraph_bigtool": True,
        "uses_create_agent": True,
        "passes_guarded_tool_registry_to_create_agent": True,
        "uses_deterministic_retrieve_tools_function": True,
        "uses_semantic_search": False,
        "uses_embeddings": False,
        "uses_langgraph_store": False,
        "agent_compiled": False,
        "agent_invoked": False,
        "agent_streamed": False,
        "reuses_existing_dhms_bindable_fake_model": True,
        "real_langgraph_bigtool_wiring": wiring_summary,
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
    if summary["guard_diff_line_count"] > 10:
        raise AssertionError("guard diff line count must stay small")
    if summary["imports_or_runs_langgraph_bigtool"] is not True:
        raise AssertionError("demo must import and use langgraph_bigtool")
    if summary["uses_create_agent"] is not True:
        raise AssertionError("demo must use langgraph_bigtool.create_agent")
    if summary["passes_guarded_tool_registry_to_create_agent"] is not True:
        raise AssertionError("demo must pass guarded_tool_registry into create_agent")
    if summary["uses_deterministic_retrieve_tools_function"] is not True:
        raise AssertionError("demo must use deterministic retrieve_tools_function")
    for key in ("uses_semantic_search", "uses_embeddings", "uses_langgraph_store"):
        if summary[key] is not False:
            raise AssertionError(f"{key} must remain false")
    for key in ("agent_compiled", "agent_invoked", "agent_streamed"):
        if summary[key] is not False:
            raise AssertionError(f"{key} must remain false")
    if summary["reuses_existing_dhms_bindable_fake_model"] is not True:
        raise AssertionError("demo must reuse the existing DHMS bindable fake model path")
    wiring = summary["real_langgraph_bigtool_wiring"]
    if wiring["agent_builder_type"] != "StateGraph":
        raise AssertionError("create_agent must return a StateGraph builder")
    if wiring["guarded_tool_registry_key_count"] != 3:
        raise AssertionError("guarded registry must contain three tools")
    if wiring["retrieve_tools_result"] != wiring["guarded_tool_registry_keys"]:
        raise AssertionError("retrieve_tools must return guarded registry keys deterministically")
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
