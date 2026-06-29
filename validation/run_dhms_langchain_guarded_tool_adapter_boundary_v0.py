#!/usr/bin/env python3
"""Validate the DHMS v3.3.0 real LangChain guarded tool adapter boundary."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dhms_agentfuse.langchain_guarded_tool_adapter import (  # noqa: E402
    run_guarded_tool_adapter_scenario,
)


ADAPTER_PATH = ROOT_DIR / "dhms_agentfuse/langchain_guarded_tool_adapter.py"
EXAMPLE_PATHS = (
    "examples/langchain_guarded_tool_adapter/safe_read_only_summary_tool_call.json",
    "examples/langchain_guarded_tool_adapter/dangerous_sql_mutation_tool_call.json",
    "examples/langchain_guarded_tool_adapter/model_api_request_tool_call.json",
)
FORBIDDEN_SOURCE_PATTERNS = {
    "requests": r"(^|\n)\s*(import\s+requests|from\s+requests\s+import|requests\.)",
    "urllib": r"(^|\n)\s*(import\s+urllib|from\s+urllib\s+import|urllib\.)",
    "subprocess": r"(^|\n)\s*(import\s+subprocess|from\s+subprocess\s+import|subprocess\.)",
    "os.environ": r"os\.environ",
    "sqlite": r"(^|\n)\s*(import\s+sqlite|from\s+sqlite|sqlite3)",
    "sqlalchemy": r"(^|\n)\s*(import\s+sqlalchemy|from\s+sqlalchemy\s+import|sqlalchemy\.)",
    "SQLDatabaseToolkit": r"\bSQLDatabaseToolkit\b",
    "PythonREPLTool": r"\bPythonREPLTool\b",
    "openai": r"(^|\n)\s*(import\s+openai|from\s+openai\s+import|openai\.)",
    "anthropic": r"(^|\n)\s*(import\s+anthropic|from\s+anthropic\s+import|anthropic\.)",
    "deepseek": r"(^|\n)\s*(import\s+deepseek|from\s+deepseek\s+import|deepseek\.)",
    "qwen": r"(^|\n)\s*(import\s+qwen|from\s+qwen\s+import|qwen\.)",
    "boto3": r"(^|\n)\s*(import\s+boto3|from\s+boto3\s+import|boto3\.)",
    "azure": r"(^|\n)\s*(import\s+azure|from\s+azure\s+import|azure\.)",
    "google.generativeai": (
        r"(^|\n)\s*(import\s+google\.generativeai|from\s+google\.generativeai\s+import|"
        r"google\.generativeai\.)"
    ),
}


def _load_scenario(relative_path: str) -> Dict[str, Any]:
    with (ROOT_DIR / relative_path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AssertionError(f"{relative_path}: scenario must be a JSON object")
    return data


def _scan_adapter_source() -> None:
    source = ADAPTER_PATH.read_text(encoding="utf-8")
    failures = [
        name
        for name, pattern in FORBIDDEN_SOURCE_PATTERNS.items()
        if re.search(pattern, source, flags=re.MULTILINE)
    ]
    if failures:
        raise AssertionError(f"forbidden runtime import/API patterns found: {', '.join(failures)}")


def _expect(result: Dict[str, Any], key: str, expected: Any) -> None:
    actual = result.get(key)
    if actual != expected:
        raise AssertionError(
            f"{result.get('scenario_id', 'unknown')}: {key} expected {expected!r}, got {actual!r}"
        )


def _expect_true(result: Dict[str, Any], key: str) -> None:
    _expect(result, key, True)


def _expect_false(result: Dict[str, Any], key: str) -> None:
    _expect(result, key, False)


def _validate_result(result: Dict[str, Any], scenario: Dict[str, Any]) -> None:
    _expect(result, "scenario_id", scenario["scenario_id"])
    _expect(result, "tool_name", scenario["tool_name"])
    _expect(result, "requested_capabilities", scenario["requested_capabilities"])
    _expect(result, "expected_gate_decision", scenario["expected_gate_decision"])
    _expect_true(result, "langchain_available")
    _expect_true(result, "real_create_agent_imported")
    _expect_true(result, "real_langchain_agent_object_created")
    if not result.get("agent_object_type"):
        raise AssertionError(f"{scenario['scenario_id']}: agent_object_type must be populated")
    _expect_true(result, "agent_loop_invoked")
    _expect_true(result, "agent_loop_completed")
    _expect_true(result, "fake_messages_driver_used")
    _expect_false(result, "model_provider_called")
    _expect_true(result, "langchain_tool_invocation_boundary_reached")
    _expect_true(result, "langchain_tool_wrapper_invoked")
    _expect(result, "guarded_adapter_invocation_count", 1)
    _expect(result, "guarded_tool_wrapper_invocation_count", 1)
    _expect_true(result, "dhms_pre_tool_guard_invoked")
    _expect(result, "dhms_guard_invocation_count", 1)
    _expect_true(result, "protected_tool_was_executable")
    _expect_false(result, "protected_tool_body_executed")
    _expect(result, "protected_payload_body_invocation_count", 0)
    _expect(result, "side_effect_sentinel_before", 0)
    _expect(result, "side_effect_sentinel_after", scenario["expected_side_effect_sentinel_after"])
    _expect(result, "side_effect_sentinel_delta", 0)
    _expect(result, "gate_decision", scenario["expected_gate_decision"])
    _expect(result, "execution_authorized", scenario["expected_execution_authorized"])
    _expect(result, "runtime_behaviors_added", scenario["expected_runtime_behaviors_added"])

    blocked_capabilities = result.get("blocked_capabilities")
    if blocked_capabilities != scenario["expected_blocked_capabilities"]:
        raise AssertionError(
            f"{scenario['scenario_id']}: blocked_capabilities expected "
            f"{scenario['expected_blocked_capabilities']!r}, got {blocked_capabilities!r}"
        )
    if not isinstance(result.get("adapter_result"), str) or not result["adapter_result"]:
        raise AssertionError(f"{scenario['scenario_id']}: adapter_result must be a non-empty string")
    if result.get("side_effect_sentinel_after") != 0:
        raise AssertionError(f"{scenario['scenario_id']}: side_effect_sentinel_after must remain 0")
    if result.get("protected_tool_body_executed") is True:
        raise AssertionError(f"{scenario['scenario_id']}: protected_tool_body_executed must be false")
    if result.get("protected_payload_body_invocation_count") != 0:
        raise AssertionError(f"{scenario['scenario_id']}: protected payload body must not execute")
    if result.get("agent_loop_message_count", 0) < 3:
        raise AssertionError(f"{scenario['scenario_id']}: real agent loop must include tool routing messages")

    for key in (
        "no_sql_execution",
        "no_db_access",
        "no_model_provider_call",
        "no_network",
        "no_subprocess",
        "no_env_access",
        "no_credentials",
        "no_user_data",
        "no_file_mutation",
    ):
        _expect_true(result, key)


def _all(results: List[Dict[str, Any]], key: str, expected: Any) -> bool:
    return all(result.get(key) == expected for result in results)


def run_validation() -> None:
    try:
        import langchain  # noqa: F401
        from langchain.agents import create_agent  # noqa: F401
    except Exception as exc:  # pragma: no cover - depends on local dependency install
        raise AssertionError(f"real LangChain dependency validation failed: {exc}") from exc

    _scan_adapter_source()
    scenarios = [_load_scenario(path) for path in EXAMPLE_PATHS]
    results = []
    for scenario in scenarios:
        result = run_guarded_tool_adapter_scenario(scenario)
        _validate_result(result, scenario)
        results.append(result)

    if len(results) != 3:
        raise AssertionError(f"validated_adapter_scenarios expected 3, got {len(results)}")

    release_candidate = sum(1 for result in results if result.get("gate_decision") == "RELEASE_CANDIDATE")
    fail_closed = sum(1 for result in results if result.get("gate_decision") == "FAIL_CLOSED")
    sentinel_failure_count = sum(
        1
        for result in results
        if result.get("side_effect_sentinel_before") != 0
        or result.get("side_effect_sentinel_after") != 0
        or result.get("side_effect_sentinel_delta") != 0
    )
    protected_payload_body_execution_count = sum(
        int(result.get("protected_payload_body_invocation_count", 0)) for result in results
    )
    runtime_behaviors_added = sum(int(result.get("runtime_behaviors_added", 0)) for result in results)

    if release_candidate != 1:
        raise AssertionError("release_candidate must be 1")
    if fail_closed != 2:
        raise AssertionError("fail_closed must be 2")
    if sentinel_failure_count != 0:
        raise AssertionError("sentinel_failure_count must be 0")
    if protected_payload_body_execution_count != 0:
        raise AssertionError("protected_payload_body_execution_count must be 0")
    if runtime_behaviors_added != 0:
        raise AssertionError("runtime_behaviors_added must be 0")

    expected_decisions_matched = all(
        result.get("gate_decision") == scenario.get("expected_gate_decision")
        for result, scenario in zip(results, scenarios)
    )
    expected_blocked_capabilities_matched = all(
        result.get("blocked_capabilities") == scenario.get("expected_blocked_capabilities")
        for result, scenario in zip(results, scenarios)
    )

    print("DHMS_REAL_LANGCHAIN_GUARDED_TOOL_ADAPTER_BOUNDARY_EXPANSION_PASS")
    print("validated_adapter_scenarios=3")
    print("release_candidate=1")
    print("fail_closed=2")
    print(f"all_langchain_available={str(_all(results, 'langchain_available', True)).lower()}")
    print(f"all_real_create_agent_imported={str(_all(results, 'real_create_agent_imported', True)).lower()}")
    print(
        "all_real_langchain_agent_object_created="
        f"{str(_all(results, 'real_langchain_agent_object_created', True)).lower()}"
    )
    print(f"all_agent_loops_invoked={str(_all(results, 'agent_loop_invoked', True)).lower()}")
    print(f"all_agent_loops_completed={str(_all(results, 'agent_loop_completed', True)).lower()}")
    print(f"all_fake_messages_driver_used={str(_all(results, 'fake_messages_driver_used', True)).lower()}")
    print(f"all_model_providers_not_called={str(_all(results, 'model_provider_called', False)).lower()}")
    print(
        "all_tool_boundaries_reached="
        f"{str(_all(results, 'langchain_tool_invocation_boundary_reached', True)).lower()}"
    )
    print(f"all_tool_wrappers_invoked={str(_all(results, 'langchain_tool_wrapper_invoked', True)).lower()}")
    print(f"all_guarded_adapters_invoked={str(_all(results, 'guarded_adapter_invocation_count', 1)).lower()}")
    print(f"all_dhms_guards_invoked={str(_all(results, 'dhms_pre_tool_guard_invoked', True)).lower()}")
    print(
        "all_protected_tools_were_executable="
        f"{str(_all(results, 'protected_tool_was_executable', True)).lower()}"
    )
    print(
        "all_protected_tool_body_executed_false="
        f"{str(_all(results, 'protected_tool_body_executed', False)).lower()}"
    )
    print(
        "all_side_effect_sentinel_before_zero="
        f"{str(_all(results, 'side_effect_sentinel_before', 0)).lower()}"
    )
    print(
        "all_side_effect_sentinel_after_zero="
        f"{str(_all(results, 'side_effect_sentinel_after', 0)).lower()}"
    )
    print(
        "all_side_effect_sentinel_delta_zero="
        f"{str(_all(results, 'side_effect_sentinel_delta', 0)).lower()}"
    )
    print(
        "all_guarded_adapter_invocation_count_one="
        f"{str(_all(results, 'guarded_adapter_invocation_count', 1)).lower()}"
    )
    print(
        "all_guarded_tool_wrapper_invocation_count_one="
        f"{str(_all(results, 'guarded_tool_wrapper_invocation_count', 1)).lower()}"
    )
    print(
        "all_dhms_guard_invocation_count_one="
        f"{str(_all(results, 'dhms_guard_invocation_count', 1)).lower()}"
    )
    print(
        "all_protected_payload_body_invocation_count_zero="
        f"{str(_all(results, 'protected_payload_body_invocation_count', 0)).lower()}"
    )
    print(f"all_execution_authorized_false={str(_all(results, 'execution_authorized', False)).lower()}")
    print(f"all_runtime_behaviors_added_zero={str(_all(results, 'runtime_behaviors_added', 0)).lower()}")
    print(f"all_expected_gate_decisions_matched={str(expected_decisions_matched).lower()}")
    print(f"all_expected_blocked_capabilities_matched={str(expected_blocked_capabilities_matched).lower()}")
    print(f"all_no_sql_execution={str(_all(results, 'no_sql_execution', True)).lower()}")
    print(f"all_no_db_access={str(_all(results, 'no_db_access', True)).lower()}")
    print(f"all_no_model_provider_call={str(_all(results, 'no_model_provider_call', True)).lower()}")
    print(f"all_no_network={str(_all(results, 'no_network', True)).lower()}")
    print(f"all_no_subprocess={str(_all(results, 'no_subprocess', True)).lower()}")
    print(f"all_no_env_access={str(_all(results, 'no_env_access', True)).lower()}")
    print(f"all_no_credentials={str(_all(results, 'no_credentials', True)).lower()}")
    print(f"all_no_user_data={str(_all(results, 'no_user_data', True)).lower()}")
    print(f"all_no_file_mutation={str(_all(results, 'no_file_mutation', True)).lower()}")
    print(f"sentinel_failure_count={sentinel_failure_count}")
    print(f"protected_payload_body_execution_count={protected_payload_body_execution_count}")
    print(f"runtime_behaviors_added={runtime_behaviors_added}")


def main() -> int:
    try:
        run_validation()
    except AssertionError as exc:
        print(f"DHMS LangChain guarded tool adapter boundary validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
