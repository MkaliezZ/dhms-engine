#!/usr/bin/env python3
"""Validate the DHMS v3.2.0 real LangChain agent-loop pre-tool boundary."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dhms_agentfuse.langchain_agent_loop_boundary import (  # noqa: E402
    run_dhms_guarded_langchain_agent_loop_scenario,
)


EXAMPLE_PATH = ROOT_DIR / "examples/langchain_agent_loop/dangerous_sql_mutation_tool_call.json"


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _load_example() -> Dict[str, Any]:
    with EXAMPLE_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AssertionError("example fixture must be a JSON object")
    return data


def _expect(result: Dict[str, Any], key: str, expected: Any) -> None:
    actual = result.get(key)
    if actual != expected:
        raise AssertionError(f"{key} expected {expected!r}, got {actual!r}")


def _expect_true(result: Dict[str, Any], key: str) -> None:
    _expect(result, key, True)


def _expect_false(result: Dict[str, Any], key: str) -> None:
    _expect(result, key, False)


def run_validation() -> None:
    try:
        import langchain  # noqa: F401
        from langchain.agents import create_agent  # noqa: F401
    except Exception as exc:  # pragma: no cover - depends on local dependency install
        raise AssertionError(f"real LangChain dependency validation failed: {exc}") from exc

    example = _load_example()
    result = run_dhms_guarded_langchain_agent_loop_scenario()

    _expect(result, "scenario_id", example["scenario_id"])
    _expect(result, "gate_decision", example["expected_gate_decision"])
    if example["expected_blocked_capability"] not in result.get("blocked_capabilities", []):
        raise AssertionError("blocked_capabilities must include sql_mutation")
    _expect(result, "side_effect_sentinel_before", 0)
    _expect(result, "side_effect_sentinel_after", example["expected_side_effect_sentinel_after"])
    _expect(result, "side_effect_sentinel_delta", 0)
    _expect(result, "protected_payload_body_invocation_count", 0)
    _expect(result, "protected_tool_body_executed", example["expected_protected_tool_body_executed"])
    _expect(result, "execution_authorized", example["expected_execution_authorized"])
    _expect(result, "runtime_behaviors_added", example["expected_runtime_behaviors_added"])

    _expect_true(result, "langchain_available")
    _expect_true(result, "real_create_agent_imported")
    _expect_true(result, "real_langchain_agent_object_created")
    _expect_true(result, "agent_loop_invoked")
    _expect_true(result, "agent_loop_completed")
    _expect_true(result, "fake_messages_driver_used")
    _expect_false(result, "model_provider_called")
    _expect_true(result, "langchain_tool_invocation_boundary_reached")
    _expect_true(result, "langchain_tool_wrapper_invoked")
    _expect_true(result, "dhms_pre_tool_guard_invoked")
    _expect_true(result, "protected_tool_was_executable")

    if result.get("guarded_tool_wrapper_invocation_count", 0) < 1:
        raise AssertionError("guarded_tool_wrapper_invocation_count must be >= 1")
    if result.get("dhms_guard_invocation_count", 0) < 1:
        raise AssertionError("dhms_guard_invocation_count must be >= 1")
    if result.get("agent_loop_message_count", 0) < 3:
        raise AssertionError("agent loop must include user, AI tool-call, and tool result messages")
    if result.get("protected_tool_body_executed") is True:
        raise AssertionError("protected tool body must not execute")
    if result.get("side_effect_sentinel_after") != 0:
        raise AssertionError("side_effect_sentinel_after must remain 0")

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

    blocked_capabilities = ",".join(result["blocked_capabilities"])
    print("DHMS_REAL_LANGCHAIN_AGENT_LOOP_PRE_TOOL_BOUNDARY_HARNESS_PASS")
    print("langchain_available=true")
    print("real_create_agent_imported=true")
    print("real_langchain_agent_object_created=true")
    print("agent_loop_invoked=true")
    print("fake_messages_driver_used=true")
    print("model_provider_called=false")
    print("langchain_tool_invocation_boundary_reached=true")
    print("langchain_tool_wrapper_invoked=true")
    print("dhms_pre_tool_guard_invoked=true")
    print("protected_tool_was_executable=true")
    print("protected_tool_body_executed=false")
    print("side_effect_sentinel_before=0")
    print("side_effect_sentinel_after=0")
    print("side_effect_sentinel_delta=0")
    print(f"guarded_tool_wrapper_invocation_count={result['guarded_tool_wrapper_invocation_count']}")
    print(f"dhms_guard_invocation_count={result['dhms_guard_invocation_count']}")
    print("protected_payload_body_invocation_count=0")
    print("gate_decision=FAIL_CLOSED")
    print(f"blocked_capabilities={blocked_capabilities}")
    print("execution_authorized=false")
    print("runtime_behaviors_added=0")
    print("no_sql_execution=true")
    print("no_db_access=true")
    print("no_model_provider_call=true")
    print("no_network=true")
    print("no_subprocess=true")
    print("no_env_access=true")
    print("no_credentials=true")
    print("no_user_data=true")
    print("no_file_mutation=true")


def main() -> int:
    try:
        run_validation()
    except AssertionError as exc:
        print(f"DHMS LangChain agent-loop pre-tool boundary validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
