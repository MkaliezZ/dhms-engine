#!/usr/bin/env python3
"""Strict v3.2.1 validation for the real LangChain agent-loop boundary."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dhms_agentfuse.langchain_agent_loop_boundary import (  # noqa: E402
    protected_dangerous_sql_mutation_payload,
    run_dhms_guarded_langchain_agent_loop_scenario,
)


VALIDATED_RUNS = 3
HARNESS_PATH = ROOT_DIR / "dhms_agentfuse/langchain_agent_loop_boundary.py"
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


def _expect(result: Dict[str, Any], key: str, expected: Any, run_index: int) -> None:
    actual = result.get(key)
    if actual != expected:
        raise AssertionError(f"run {run_index}: {key} expected {expected!r}, got {actual!r}")


def _expect_true(result: Dict[str, Any], key: str, run_index: int) -> None:
    _expect(result, key, True, run_index)


def _expect_false(result: Dict[str, Any], key: str, run_index: int) -> None:
    _expect(result, key, False, run_index)


def _scan_harness_source() -> None:
    source = HARNESS_PATH.read_text(encoding="utf-8")
    failures = [
        name
        for name, pattern in FORBIDDEN_SOURCE_PATTERNS.items()
        if re.search(pattern, source, flags=re.MULTILINE)
    ]
    if failures:
        raise AssertionError(f"forbidden runtime import/API patterns found: {', '.join(failures)}")


def _validate_run(result: Dict[str, Any], run_index: int) -> None:
    _expect_true(result, "langchain_available", run_index)
    _expect_true(result, "real_create_agent_imported", run_index)
    _expect_true(result, "real_langchain_agent_object_created", run_index)
    _expect_true(result, "agent_loop_invoked", run_index)
    _expect_true(result, "agent_loop_completed", run_index)
    _expect_true(result, "fake_messages_driver_used", run_index)
    _expect_false(result, "model_provider_called", run_index)
    _expect_true(result, "langchain_tool_invocation_boundary_reached", run_index)
    _expect_true(result, "langchain_tool_wrapper_invoked", run_index)
    _expect_true(result, "dhms_pre_tool_guard_invoked", run_index)
    _expect_true(result, "protected_tool_was_executable", run_index)
    _expect_false(result, "protected_tool_body_executed", run_index)
    _expect(result, "side_effect_sentinel_before", 0, run_index)
    _expect(result, "side_effect_sentinel_after", 0, run_index)
    _expect(result, "side_effect_sentinel_delta", 0, run_index)
    _expect(result, "guarded_tool_wrapper_invocation_count", 1, run_index)
    _expect(result, "dhms_guard_invocation_count", 1, run_index)
    _expect(result, "protected_payload_body_invocation_count", 0, run_index)
    _expect(result, "gate_decision", "FAIL_CLOSED", run_index)
    if "sql_mutation" not in result.get("blocked_capabilities", []):
        raise AssertionError(f"run {run_index}: blocked_capabilities must include sql_mutation")
    _expect_false(result, "execution_authorized", run_index)
    _expect(result, "runtime_behaviors_added", 0, run_index)

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
        _expect_true(result, key, run_index)


def _all(results: List[Dict[str, Any]], key: str, expected: Any) -> bool:
    return all(result.get(key) == expected for result in results)


def run_validation() -> None:
    try:
        import langchain  # noqa: F401
        from langchain.agents import create_agent  # noqa: F401
    except Exception as exc:  # pragma: no cover - depends on local dependency install
        raise AssertionError(f"real LangChain dependency validation failed: {exc}") from exc

    if not callable(protected_dangerous_sql_mutation_payload):
        raise AssertionError("protected payload body must be callable")

    _scan_harness_source()

    results = []
    for run_index in range(1, VALIDATED_RUNS + 1):
        result = run_dhms_guarded_langchain_agent_loop_scenario()
        _validate_run(result, run_index)
        results.append(result)

    if len(results) != VALIDATED_RUNS:
        raise AssertionError(f"validated_runs expected {VALIDATED_RUNS}, got {len(results)}")

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

    if sentinel_failure_count != 0:
        raise AssertionError("sentinel_failure_count must be 0")
    if protected_payload_body_execution_count != 0:
        raise AssertionError("protected_payload_body_execution_count must be 0")
    if runtime_behaviors_added != 0:
        raise AssertionError("runtime_behaviors_added must be 0")

    print("DHMS_REAL_LANGCHAIN_AGENT_LOOP_BOUNDARY_VALIDATION_PASS")
    print("validated_runs=3")
    print("langchain_available=true")
    print("real_create_agent_imported=true")
    print("real_langchain_agent_object_created=true")
    print(f"all_agent_loop_invoked={str(_all(results, 'agent_loop_invoked', True)).lower()}")
    print(f"all_agent_loop_completed={str(_all(results, 'agent_loop_completed', True)).lower()}")
    print(f"all_fake_messages_driver_used={str(_all(results, 'fake_messages_driver_used', True)).lower()}")
    print(f"all_model_providers_not_called={str(_all(results, 'model_provider_called', False)).lower()}")
    print(
        "all_tool_boundaries_reached="
        f"{str(_all(results, 'langchain_tool_invocation_boundary_reached', True)).lower()}"
    )
    print(f"all_tool_wrappers_invoked={str(_all(results, 'langchain_tool_wrapper_invoked', True)).lower()}")
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
    print(f"all_gate_decisions_fail_closed={str(_all(results, 'gate_decision', 'FAIL_CLOSED')).lower()}")
    print(
        "all_blocked_capabilities_sql_mutation="
        f"{str(all('sql_mutation' in result.get('blocked_capabilities', []) for result in results)).lower()}"
    )
    print(f"all_execution_authorized_false={str(_all(results, 'execution_authorized', False)).lower()}")
    print(f"all_runtime_behaviors_added_zero={str(_all(results, 'runtime_behaviors_added', 0)).lower()}")
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
        print(f"DHMS LangChain agent-loop boundary validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
