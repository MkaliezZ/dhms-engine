#!/usr/bin/env python3
"""Smoke validation for the DHMS v3.1 LangChain interception harness."""

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

REQUIRED_RESULT_KEYS = (
    "dhms_interception_version",
    "langchain_available",
    "langchain_agent_harness_created",
    "source",
    "observed_tool_call",
    "converted_proposal",
    "gate_result",
    "intercepted_before_execution",
    "tool_execution_attempted",
    "tool_execution_allowed",
    "execution_authorized",
    "runtime_behaviors_added",
    "interception_trace",
)

TRACE_REQUIRED_KEYS = (
    "real_langchain_installed_or_imported",
    "real_langchain_agent_harness_created",
    "langchain_message_or_tool_call_observed",
    "converted_to_dhms_proposal",
    "routed_through_controlled_proposal_gate",
    "tool_not_executed",
    "model_provider_not_called",
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

TRACE_TRUE_ASSERTION_KEYS = tuple(
    key
    for key in TRACE_REQUIRED_KEYS
    if key not in {"real_langchain_installed_or_imported", "real_langchain_agent_harness_created"}
)


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _load_example(relative_path: str) -> Dict[str, Any]:
    with (ROOT_DIR / relative_path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AssertionError(f"{relative_path}: example must be a JSON object")
    return data


def _validate_interception(
    result: Dict[str, Any],
    expected_id: str,
    expected_decision: str,
    expected_blocked_capabilities: List[str],
) -> None:
    for key in REQUIRED_RESULT_KEYS:
        if key not in result:
            raise AssertionError(f"{expected_id}: missing result key {key}")

    observed = result["observed_tool_call"]
    if observed.get("id") != expected_id:
        raise AssertionError(f"{expected_id}: observed tool call id mismatch")
    if result["gate_result"]["proposal_id"] != expected_id:
        raise AssertionError(f"{expected_id}: gate proposal id mismatch")
    if result["gate_result"]["decision"] != expected_decision:
        raise AssertionError(f"{expected_id}: unexpected decision {result['gate_result']['decision']}")

    blocked_capabilities = result["gate_result"].get("blocked_capabilities", [])
    if not isinstance(blocked_capabilities, list):
        raise AssertionError(f"{expected_id}: blocked_capabilities must be a list")
    for blocked_capability in expected_blocked_capabilities:
        if blocked_capability not in blocked_capabilities:
            raise AssertionError(f"{expected_id}: missing blocked capability {blocked_capability}")

    if result["intercepted_before_execution"] is not True:
        raise AssertionError(f"{expected_id}: intercepted_before_execution must be true")
    if result["tool_execution_attempted"] is not False:
        raise AssertionError(f"{expected_id}: tool_execution_attempted must be false")
    if result["tool_execution_allowed"] is not False:
        raise AssertionError(f"{expected_id}: tool_execution_allowed must be false")
    if result["execution_authorized"] is not False:
        raise AssertionError(f"{expected_id}: execution_authorized must be false")
    if result["runtime_behaviors_added"] != 0:
        raise AssertionError(f"{expected_id}: runtime_behaviors_added must be 0")
    if result["gate_result"]["execution_authorized"] is not False:
        raise AssertionError(f"{expected_id}: gate_result.execution_authorized must be false")
    if result["gate_result"]["runtime_behaviors_added"] != 0:
        raise AssertionError(f"{expected_id}: gate_result.runtime_behaviors_added must be 0")

    trace = result["interception_trace"]
    for key in TRACE_REQUIRED_KEYS:
        if key not in trace:
            raise AssertionError(f"{expected_id}: missing interception_trace key {key}")
    for key in TRACE_TRUE_ASSERTION_KEYS:
        if trace[key] is not True:
            raise AssertionError(f"{expected_id}: interception_trace {key} must be true")


def run_validation() -> None:
    harness = create_dhms_langchain_agent_harness()
    langchain_is_available = bool(harness["langchain_available"])
    harness_created = bool(harness["langchain_agent_harness_created"])
    if langchain_is_available and not harness_created:
        raise AssertionError("LangChain is available but the harness was not created")

    results = []
    for relative_path, expected_id, expected_decision, expected_blocked in EXAMPLES:
        example = _load_example(relative_path)
        result = intercept_langchain_tool_call(example, relative_path)
        _validate_interception(result, expected_id, expected_decision, expected_blocked)
        if result["langchain_available"] != langchain_is_available:
            raise AssertionError(f"{expected_id}: langchain availability mismatch")
        if result["langchain_agent_harness_created"] != harness_created:
            raise AssertionError(f"{expected_id}: harness created mismatch")
        results.append(result)

    if langchain_is_available:
        try:
            from langchain_core.messages import AIMessage  # type: ignore
        except Exception as exc:  # pragma: no cover - depends on installed version
            raise AssertionError(f"LangChain is available but AIMessage import failed: {exc}") from exc
        message = AIMessage(content="", tool_calls=[_load_example(EXAMPLES[0][0])])
        message_result = intercept_langchain_ai_message(message, "validation:real_langchain_ai_message")
        _validate_interception(message_result, EXAMPLES[0][1], EXAMPLES[0][2], EXAMPLES[0][3])

    release_candidate_count = sum(1 for result in results if result["gate_result"]["decision"] == "RELEASE_CANDIDATE")
    fail_closed_count = sum(1 for result in results if result["gate_result"]["decision"] == "FAIL_CLOSED")
    hold_for_review_count = sum(1 for result in results if result["gate_result"]["decision"] == "HOLD_FOR_REVIEW")
    runtime_behaviors_added = sum(result["runtime_behaviors_added"] for result in results)

    if len(results) != 3:
        raise AssertionError("expected exactly 3 validated interceptions")
    if release_candidate_count != 1 or fail_closed_count != 2 or hold_for_review_count != 0:
        raise AssertionError("unexpected interception decision distribution")
    if any(result["tool_execution_attempted"] is not False for result in results):
        raise AssertionError("tool_execution_attempted must remain false")
    if any(result["tool_execution_allowed"] is not False for result in results):
        raise AssertionError("tool_execution_allowed must remain false")
    if any(result["execution_authorized"] is not False for result in results):
        raise AssertionError("execution_authorized must remain false")
    if runtime_behaviors_added != 0:
        raise AssertionError("runtime_behaviors_added must remain 0")

    print("DHMS_REAL_LANGCHAIN_AGENT_INTERCEPTION_MINIMAL_HARNESS_PASS")
    print("validated_interceptions=3")
    print(f"langchain_available={_bool_text(langchain_is_available)}")
    print(f"langchain_agent_harness_created={_bool_text(harness_created)}")
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
    print("runtime_behaviors_added=0")


def main() -> int:
    try:
        run_validation()
    except AssertionError as exc:
        print(f"DHMS LangChain interception smoke validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
