#!/usr/bin/env python3
"""Strict v3.1.1 validation for real LangChain dependency and harness creation."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dhms_agentfuse.langchain_interception import (  # noqa: E402
    create_dhms_langchain_agent_harness,
    intercept_langchain_ai_message,
    intercept_langchain_tool_call,
)


EXAMPLES: Tuple[Tuple[str, str, str, List[str]], ...] = (
    (
        "examples/langchain_interception/safe_read_only_tool_call.json",
        "langchain_tool_call_safe_read_only_summary_001",
        "RELEASE_CANDIDATE",
        [],
    ),
    (
        "examples/langchain_interception/drop_table_tool_call.json",
        "langchain_tool_call_drop_table_001",
        "FAIL_CLOSED",
        ["sql_mutation"],
    ),
    (
        "examples/langchain_interception/model_api_tool_call.json",
        "langchain_tool_call_model_api_request_001",
        "FAIL_CLOSED",
        ["model_api"],
    ),
)

TRACE_REQUIRED_KEYS = (
    "real_langchain_installed_or_imported",
    "real_create_agent_imported",
    "real_langchain_agent_harness_created",
    "real_langchain_agent_object_created",
    "real_langchain_ai_message_path_validated",
    "langchain_message_or_tool_call_observed",
    "converted_to_dhms_proposal",
    "routed_through_controlled_proposal_gate",
    "tool_not_executed",
    "model_provider_not_called",
    "fake_or_local_model_used",
    "no_sql_execution",
    "no_db_access",
    "no_sql_database_toolkit",
    "no_model_api",
    "no_network",
    "no_subprocess",
    "no_env_access",
    "no_credentials",
    "no_user_data",
    "no_file_mutation",
    "no_kerniq",
    "no_e2b",
    "no_production_runtime",
)


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _load_example(relative_path: str) -> Dict[str, Any]:
    with (ROOT_DIR / relative_path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AssertionError(f"{relative_path}: expected JSON object")
    return data


def _ai_message_tool_call(example: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": example.get("id"),
        "name": example.get("name"),
        "args": example.get("args", {}),
        "type": example.get("type", "tool_call"),
    }


def _assert_harness(harness: Dict[str, Any]) -> None:
    if harness.get("langchain_available") is not True:
        raise AssertionError("langchain_available must be true")
    if harness.get("langchain_agent_harness_created") is not True:
        raise AssertionError("langchain_agent_harness_created must be true")
    if harness.get("real_create_agent_imported") is not True:
        raise AssertionError("real_create_agent_imported must be true")
    if harness.get("real_langchain_agent_object_created") is not True:
        raise AssertionError("real_langchain_agent_object_created must be true")
    if harness.get("fake_or_local_model_used") is not True:
        raise AssertionError("fake_or_local_model_used must be true")
    if harness.get("model_provider_called") is not False:
        raise AssertionError("model_provider_called must be false")
    if harness.get("inert_tools_defined") is not True:
        raise AssertionError("inert_tools_defined must be true")
    if harness.get("tool_execution_attempted") is not False:
        raise AssertionError("tool_execution_attempted must be false")
    if harness.get("tool_execution_allowed") is not False:
        raise AssertionError("tool_execution_allowed must be false")
    if harness.get("runtime_behaviors_added") != 0:
        raise AssertionError("runtime_behaviors_added must be 0")
    if harness.get("real_langchain_ai_message_path_validated") is not True:
        raise AssertionError("real_langchain_ai_message_path_validated must be true")


def _assert_interception(
    result: Dict[str, Any],
    expected_id: str,
    expected_decision: str,
    expected_blocked_capabilities: List[str],
) -> None:
    if result.get("langchain_available") is not True:
        raise AssertionError(f"{expected_id}: langchain_available must be true")
    if result.get("langchain_agent_harness_created") is not True:
        raise AssertionError(f"{expected_id}: langchain_agent_harness_created must be true")
    if result.get("real_create_agent_imported") is not True:
        raise AssertionError(f"{expected_id}: real_create_agent_imported must be true")
    if result.get("real_langchain_agent_object_created") is not True:
        raise AssertionError(f"{expected_id}: real_langchain_agent_object_created must be true")
    if result.get("intercepted_before_execution") is not True:
        raise AssertionError(f"{expected_id}: intercepted_before_execution must be true")
    if result.get("tool_execution_attempted") is not False:
        raise AssertionError(f"{expected_id}: tool_execution_attempted must be false")
    if result.get("tool_execution_allowed") is not False:
        raise AssertionError(f"{expected_id}: tool_execution_allowed must be false")
    if result.get("execution_authorized") is not False:
        raise AssertionError(f"{expected_id}: execution_authorized must be false")
    if result.get("runtime_behaviors_added") != 0:
        raise AssertionError(f"{expected_id}: runtime_behaviors_added must be 0")

    observed = result.get("observed_tool_call")
    if not isinstance(observed, dict) or observed.get("id") != expected_id:
        raise AssertionError(f"{expected_id}: observed tool call id mismatch")
    gate_result = result.get("gate_result")
    if not isinstance(gate_result, dict):
        raise AssertionError(f"{expected_id}: gate_result must be an object")
    if gate_result.get("proposal_id") != expected_id:
        raise AssertionError(f"{expected_id}: gate_result proposal id mismatch")
    if gate_result.get("decision") != expected_decision:
        raise AssertionError(f"{expected_id}: unexpected decision {gate_result.get('decision')}")
    if gate_result.get("execution_authorized") is not False:
        raise AssertionError(f"{expected_id}: gate_result execution_authorized must be false")
    if gate_result.get("runtime_behaviors_added") != 0:
        raise AssertionError(f"{expected_id}: gate_result runtime_behaviors_added must be 0")

    blocked_capabilities = gate_result.get("blocked_capabilities")
    if not isinstance(blocked_capabilities, list):
        raise AssertionError(f"{expected_id}: blocked_capabilities must be a list")
    for blocked_capability in expected_blocked_capabilities:
        if blocked_capability not in blocked_capabilities:
            raise AssertionError(f"{expected_id}: missing blocked capability {blocked_capability}")

    trace = result.get("interception_trace")
    if not isinstance(trace, dict):
        raise AssertionError(f"{expected_id}: interception_trace must be an object")
    for key in TRACE_REQUIRED_KEYS:
        if key not in trace:
            raise AssertionError(f"{expected_id}: missing trace key {key}")
        if trace[key] is not True:
            raise AssertionError(f"{expected_id}: trace key {key} must be true")


def run_validation() -> None:
    try:
        import langchain  # noqa: F401
        from langchain.agents import create_agent  # noqa: F401
        from langchain_core.messages import AIMessage
    except Exception as exc:  # pragma: no cover - depends on local dependency install
        raise AssertionError(f"real LangChain dependency validation failed: {exc}") from exc

    harness = create_dhms_langchain_agent_harness()
    _assert_harness(harness)

    results = []
    for relative_path, expected_id, expected_decision, expected_blocked in EXAMPLES:
        example = _load_example(relative_path)
        result = intercept_langchain_tool_call(example, relative_path)
        _assert_interception(result, expected_id, expected_decision, expected_blocked)
        results.append(result)

    message = AIMessage(content="", tool_calls=[_ai_message_tool_call(_load_example(EXAMPLES[0][0]))])
    message_result = intercept_langchain_ai_message(message, "validation:real_langchain_ai_message")
    _assert_interception(message_result, EXAMPLES[0][1], EXAMPLES[0][2], EXAMPLES[0][3])

    if len(results) != 3:
        raise AssertionError("expected exactly 3 validated interceptions")

    release_candidate_count = sum(1 for result in results if result["gate_result"]["decision"] == "RELEASE_CANDIDATE")
    fail_closed_count = sum(1 for result in results if result["gate_result"]["decision"] == "FAIL_CLOSED")
    hold_for_review_count = sum(1 for result in results if result["gate_result"]["decision"] == "HOLD_FOR_REVIEW")
    runtime_behaviors_added = sum(result["runtime_behaviors_added"] for result in results)

    if release_candidate_count != 1:
        raise AssertionError("release_candidate count must be 1")
    if fail_closed_count != 2:
        raise AssertionError("fail_closed count must be 2")
    if hold_for_review_count != 0:
        raise AssertionError("hold_for_review count must be 0")
    if runtime_behaviors_added != 0:
        raise AssertionError("runtime_behaviors_added must be 0")

    print("DHMS_REAL_LANGCHAIN_DEPENDENCY_AND_AGENT_HARNESS_VALIDATION_PASS")
    print("langchain_available=true")
    print("langchain_agent_harness_created=true")
    print("real_create_agent_imported=true")
    print("real_langchain_agent_object_created=true")
    print("real_langchain_ai_message_path_validated=true")
    print("validated_interceptions=3")
    print("release_candidate=1")
    print("fail_closed=2")
    print("hold_for_review=0")
    print("all_intercepted_before_execution=true")
    print("all_tool_execution_attempted_false=true")
    print("all_tool_execution_allowed_false=true")
    print("all_execution_authorized_false=true")
    print("all_runtime_behaviors_added_zero=true")
    print("all_gate_results_execution_authorized_false=true")
    print("all_gate_results_runtime_behaviors_added_zero=true")
    print("all_interception_trace_keys_present=true")
    print("all_interception_trace_assertions_true=true")
    print("all_tools_not_executed=true")
    print("all_model_providers_not_called=true")
    print(f"runtime_behaviors_added={runtime_behaviors_added}")


def main() -> int:
    try:
        run_validation()
    except AssertionError as exc:
        print(f"DHMS LangChain dependency and harness validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
