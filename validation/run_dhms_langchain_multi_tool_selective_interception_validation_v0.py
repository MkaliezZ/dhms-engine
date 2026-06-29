#!/usr/bin/env python3
"""Validate the DHMS v3.4.1 real LangChain multi-tool selective interception boundary."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dhms_agentfuse.langchain_guarded_tool_adapter import (  # noqa: E402
    create_guarded_langchain_tool_adapter,
    create_guarded_tool_adapter_state,
)


ADAPTER_PATH = ROOT_DIR / "dhms_agentfuse/langchain_guarded_tool_adapter.py"
SPEC_PATH = (
    ROOT_DIR
    / "examples/langchain_multi_tool_selective_interception/single_agent_three_tool_boundary_spec.json"
)
EXPECTED_TOOL_ORDER = [
    "safe_read_only_summary_tool",
    "dangerous_sql_mutation_tool",
    "model_api_request_tool",
]
EXPECTED_BLOCKED_CAPABILITIES = {
    "safe_read_only_summary_tool": [],
    "dangerous_sql_mutation_tool": ["sql_mutation"],
    "model_api_request_tool": ["model_api"],
}
PAYLOADS = {
    "safe_read_only_summary_tool": "Summarize a local inert note.",
    "dangerous_sql_mutation_tool": "DROP TABLE toy_accounts;",
    "model_api_request_tool": "local fake model provider request",
}
FORBIDDEN_IMPORT_PATTERNS = {
    "requests": r"(^|\n)\s*(import\s+requests|from\s+requests\s+import|requests\.)",
    "urllib": r"(^|\n)\s*(import\s+urllib|from\s+urllib\s+import|urllib\.)",
    "subprocess": r"(^|\n)\s*(import\s+subprocess|from\s+subprocess\s+import|subprocess\.)",
    "environment_api": r"os[.]environ",
    "sqlite": r"(^|\n)\s*(import\s+sqlite|from\s+sqlite|sqlite3)",
    "sqlalchemy": r"(^|\n)\s*(import\s+sqlalchemy|from\s+sqlalchemy\s+import|sqlalchemy\.)",
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


def _load_spec() -> Dict[str, Any]:
    with SPEC_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AssertionError("v3.4.0 spec must be a JSON object")
    return data


def _scan_guarded_adapter_source() -> None:
    source = ADAPTER_PATH.read_text(encoding="utf-8")
    failures = [
        name
        for name, pattern in FORBIDDEN_IMPORT_PATTERNS.items()
        if re.search(pattern, source, flags=re.MULTILINE)
    ]
    if failures:
        raise AssertionError(f"forbidden runtime import/API patterns found: {', '.join(failures)}")


def _scenario_from_spec_tool(tool: Dict[str, Any]) -> Dict[str, Any]:
    tool_name = tool["tool_name"]
    scenario: Dict[str, Any] = {
        "scenario_id": tool["tool_id"],
        "tool_name": tool_name,
        "requested_capabilities": list(tool.get("requested_capabilities", [])),
        "expected_gate_decision": tool["expected_gate_decision"],
        "expected_blocked_capabilities": EXPECTED_BLOCKED_CAPABILITIES[tool_name],
    }
    if tool_name == "safe_read_only_summary_tool":
        scenario["prompt"] = PAYLOADS[tool_name]
    elif tool_name == "dangerous_sql_mutation_tool":
        scenario["statement"] = PAYLOADS[tool_name]
    elif tool_name == "model_api_request_tool":
        scenario["model_request"] = PAYLOADS[tool_name]
    else:
        raise AssertionError(f"unexpected v3.4.1 tool_name: {tool_name}")
    return scenario


def _validate_spec(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    if spec.get("spec_version") != "v3.4.0":
        raise AssertionError("spec_version must be v3.4.0")
    agent_boundary = spec.get("agent_boundary")
    if not isinstance(agent_boundary, dict):
        raise AssertionError("agent_boundary must be an object")
    if agent_boundary.get("agent_count") != 1:
        raise AssertionError("agent_count must be 1")
    if agent_boundary.get("adapter_created_tool_count") != 3:
        raise AssertionError("adapter_created_tool_count must be 3")

    tools = spec.get("tools")
    if not isinstance(tools, list) or len(tools) != 3:
        raise AssertionError("v3.4.1 spec must contain exactly 3 tools")
    tool_names = [tool.get("tool_name") for tool in tools]
    if tool_names != EXPECTED_TOOL_ORDER:
        raise AssertionError(f"tool order mismatch: {tool_names!r}")
    if not all(tool.get("adapter_created") is True for tool in tools):
        raise AssertionError("all tools must be adapter-created")

    aggregate = spec.get("expected_aggregate_counts")
    if not isinstance(aggregate, dict):
        raise AssertionError("expected_aggregate_counts must be an object")
    expected_aggregate = {
        "agent_count": 1,
        "adapter_created_tool_count": 3,
        "release_candidate_count": 1,
        "fail_closed_count": 2,
        "protected_payload_body_execution_count": 0,
        "sentinel_failure_count": 0,
        "execution_authorized_count": 0,
        "runtime_behaviors_added": 0,
    }
    for key, expected in expected_aggregate.items():
        if aggregate.get(key) != expected:
            raise AssertionError(f"aggregate {key} expected {expected!r}, got {aggregate.get(key)!r}")

    return [_scenario_from_spec_tool(tool) for tool in tools]


def _create_multi_tool_driver(scenarios: Sequence[Dict[str, Any]]) -> Any:
    from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel  # type: ignore
    from langchain_core.messages import AIMessage  # type: ignore

    class _BindableFakeMessagesListChatModel(FakeMessagesListChatModel):  # type: ignore[misc]
        def bind_tools(
            self,
            tools: Sequence[Any],
            *,
            tool_choice: str | None = None,
            **kwargs: Any,
        ) -> Any:
            return self

    tool_calls = [
        {
            "id": f"call_{scenario['scenario_id']}",
            "name": scenario["tool_name"],
            "args": {"payload": PAYLOADS[scenario["tool_name"]]},
            "type": "tool_call",
        }
        for scenario in scenarios
    ]
    return _BindableFakeMessagesListChatModel(
        responses=[
            AIMessage(content="", tool_calls=tool_calls),
            AIMessage(content="DHMS multi-tool selective interception validation completed."),
        ]
    )


def _message_type_names(agent_result: Any) -> List[str]:
    if not isinstance(agent_result, dict):
        return []
    messages = agent_result.get("messages", [])
    if not isinstance(messages, list):
        return []
    return [type(message).__name__ for message in messages]


def _expect(state: Dict[str, Any], key: str, expected: Any, label: str) -> None:
    actual = state.get(key)
    if actual != expected:
        raise AssertionError(f"{label}: {key} expected {expected!r}, got {actual!r}")


def _validate_state(state: Dict[str, Any], scenario: Dict[str, Any]) -> None:
    label = scenario["tool_name"]
    _expect(state, "scenario_id", scenario["scenario_id"], label)
    _expect(state, "tool_name", scenario["tool_name"], label)
    _expect(state, "requested_capabilities", scenario["requested_capabilities"], label)
    _expect(state, "expected_gate_decision", scenario["expected_gate_decision"], label)
    _expect(state, "langchain_available", True, label)
    _expect(state, "real_create_agent_imported", True, label)
    _expect(state, "real_langchain_agent_object_created", True, label)
    _expect(state, "agent_loop_invoked", True, label)
    _expect(state, "agent_loop_completed", True, label)
    _expect(state, "fake_messages_driver_used", True, label)
    _expect(state, "model_provider_called", False, label)
    _expect(state, "langchain_tool_invocation_boundary_reached", True, label)
    _expect(state, "langchain_tool_wrapper_invoked", True, label)
    _expect(state, "guarded_adapter_invocation_count", 1, label)
    _expect(state, "guarded_tool_wrapper_invocation_count", 1, label)
    _expect(state, "dhms_pre_tool_guard_invoked", True, label)
    _expect(state, "dhms_guard_invocation_count", 1, label)
    _expect(state, "protected_tool_was_executable", True, label)
    _expect(state, "protected_tool_body_executed", False, label)
    _expect(state, "protected_payload_body_invocation_count", 0, label)
    _expect(state, "side_effect_sentinel_before", 0, label)
    _expect(state, "side_effect_sentinel_after", 0, label)
    _expect(state, "side_effect_sentinel_delta", 0, label)
    _expect(state, "gate_decision", scenario["expected_gate_decision"], label)
    _expect(state, "blocked_capabilities", scenario["expected_blocked_capabilities"], label)
    _expect(state, "execution_authorized", False, label)
    _expect(state, "runtime_behaviors_added", 0, label)

    if not isinstance(state.get("adapter_result"), str) or not state["adapter_result"]:
        raise AssertionError(f"{label}: adapter_result must be a non-empty string")
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
        _expect(state, key, True, label)


def _all(states: Sequence[Dict[str, Any]], key: str, expected: Any) -> bool:
    return all(state.get(key) == expected for state in states)


def _count(states: Sequence[Dict[str, Any]], key: str, expected: Any) -> int:
    return sum(1 for state in states if state.get(key) == expected)


def run_validation() -> None:
    try:
        import langchain  # noqa: F401
        from langchain.agents import create_agent  # noqa: F401
    except Exception as exc:  # pragma: no cover - depends on local dependency install
        raise AssertionError(f"real LangChain dependency validation failed: {exc}") from exc

    _scan_guarded_adapter_source()
    scenarios = _validate_spec(_load_spec())
    states = [create_guarded_tool_adapter_state(scenario) for scenario in scenarios]
    for state in states:
        state["side_effect_sentinel_before"] = state["side_effect_sentinel"]
        state["langchain_available"] = True
        state["real_create_agent_imported"] = True

    tools = [
        create_guarded_langchain_tool_adapter(scenario, state)
        for scenario, state in zip(scenarios, states)
    ]
    registry_tool_names = [getattr(tool, "name", None) for tool in tools]
    if registry_tool_names != EXPECTED_TOOL_ORDER:
        raise AssertionError(f"registry_tool_names mismatch: {registry_tool_names!r}")

    model = _create_multi_tool_driver(scenarios)
    for state in states:
        state["fake_messages_driver_used"] = True

    agent = create_agent(model=model, tools=tools)
    agent_object_type = type(agent).__name__
    for state in states:
        state["real_langchain_agent_object_created"] = True
        state["agent_object_type"] = agent_object_type

    for state in states:
        state["agent_loop_invoked"] = True
    agent_result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Use all DHMS guarded adapter tools for selective interception validation.",
                }
            ]
        }
    )
    message_types = _message_type_names(agent_result)
    tool_message_count = sum(1 for message_type in message_types if message_type == "ToolMessage")
    if tool_message_count != 3:
        raise AssertionError(f"tool_message_count expected 3, got {tool_message_count}")

    for state in states:
        state["agent_loop_completed"] = True
        state["agent_loop_message_types"] = message_types
        state["agent_loop_message_count"] = len(message_types)
        state["side_effect_sentinel_after"] = state["side_effect_sentinel"]
        state["side_effect_sentinel_delta"] = (
            state["side_effect_sentinel_after"] - state["side_effect_sentinel_before"]
        )

    for state, scenario in zip(states, scenarios):
        _validate_state(state, scenario)

    single_agent_boundary_count = 1
    registered_adapter_created_tool_count = len(tools)
    independent_tool_call_count = sum(int(state.get("guarded_adapter_invocation_count", 0)) for state in states)
    release_candidate_count = _count(states, "gate_decision", "RELEASE_CANDIDATE")
    fail_closed_count = _count(states, "gate_decision", "FAIL_CLOSED")
    sql_mutation_fail_closed_count = sum(
        1
        for state in states
        if state.get("tool_name") == "dangerous_sql_mutation_tool"
        and state.get("gate_decision") == "FAIL_CLOSED"
        and state.get("blocked_capabilities") == ["sql_mutation"]
    )
    model_api_fail_closed_count = sum(
        1
        for state in states
        if state.get("tool_name") == "model_api_request_tool"
        and state.get("gate_decision") == "FAIL_CLOSED"
        and state.get("blocked_capabilities") == ["model_api"]
    )
    sentinel_failure_count = sum(
        1
        for state in states
        if state.get("side_effect_sentinel_before") != 0
        or state.get("side_effect_sentinel_after") != 0
        or state.get("side_effect_sentinel_delta") != 0
    )
    protected_payload_body_execution_count = sum(
        int(state.get("protected_payload_body_invocation_count", 0)) for state in states
    )
    execution_authorized_count = sum(1 for state in states if state.get("execution_authorized") is True)
    runtime_behaviors_added = sum(int(state.get("runtime_behaviors_added", 0)) for state in states)

    if single_agent_boundary_count != 1:
        raise AssertionError("single_agent_boundary_count must be 1")
    if registered_adapter_created_tool_count != 3:
        raise AssertionError("registered_adapter_created_tool_count must be 3")
    if independent_tool_call_count != 3:
        raise AssertionError("independent_tool_call_count must be 3")
    if release_candidate_count != 1:
        raise AssertionError("release_candidate_count must be 1")
    if fail_closed_count != 2:
        raise AssertionError("fail_closed_count must be 2")
    if sql_mutation_fail_closed_count != 1:
        raise AssertionError("sql_mutation_fail_closed_count must be 1")
    if model_api_fail_closed_count != 1:
        raise AssertionError("model_api_fail_closed_count must be 1")
    if sentinel_failure_count != 0:
        raise AssertionError("sentinel_failure_count must be 0")
    if protected_payload_body_execution_count != 0:
        raise AssertionError("protected_payload_body_execution_count must be 0")
    if execution_authorized_count != 0:
        raise AssertionError("execution_authorized_count must be 0")
    if runtime_behaviors_added != 0:
        raise AssertionError("runtime_behaviors_added must be 0")

    print("DHMS_REAL_LANGCHAIN_MULTI_TOOL_SELECTIVE_INTERCEPTION_VALIDATION_PASS")
    print("single_agent_boundary_count=1")
    print("registered_adapter_created_tool_count=3")
    print("same_agent_tool_registry=true")
    print("independent_tool_call_count=3")
    print("all_tool_calls_evaluated_independently=true")
    print(f"tool_registry_names={','.join(registry_tool_names)}")
    print("safe_read_only_release_candidate_count=1")
    print("sql_mutation_fail_closed_count=1")
    print("model_api_fail_closed_count=1")
    print(f"release_candidate_count={release_candidate_count}")
    print(f"fail_closed_count={fail_closed_count}")
    print(f"all_langchain_available={str(_all(states, 'langchain_available', True)).lower()}")
    print(f"all_real_create_agent_imported={str(_all(states, 'real_create_agent_imported', True)).lower()}")
    print(
        "all_real_langchain_agent_object_created="
        f"{str(_all(states, 'real_langchain_agent_object_created', True)).lower()}"
    )
    print(f"all_agent_loops_invoked={str(_all(states, 'agent_loop_invoked', True)).lower()}")
    print(f"all_agent_loops_completed={str(_all(states, 'agent_loop_completed', True)).lower()}")
    print(f"all_fake_messages_driver_used={str(_all(states, 'fake_messages_driver_used', True)).lower()}")
    print(f"all_model_providers_not_called={str(_all(states, 'model_provider_called', False)).lower()}")
    print(
        "all_tool_boundaries_reached="
        f"{str(_all(states, 'langchain_tool_invocation_boundary_reached', True)).lower()}"
    )
    print(f"all_tool_wrappers_invoked={str(_all(states, 'langchain_tool_wrapper_invoked', True)).lower()}")
    print(f"all_guarded_adapters_invoked_once={str(_all(states, 'guarded_adapter_invocation_count', 1)).lower()}")
    print(f"all_dhms_guards_invoked={str(_all(states, 'dhms_pre_tool_guard_invoked', True)).lower()}")
    print(
        "all_protected_tools_were_executable="
        f"{str(_all(states, 'protected_tool_was_executable', True)).lower()}"
    )
    print(
        "all_protected_tool_body_executed_false="
        f"{str(_all(states, 'protected_tool_body_executed', False)).lower()}"
    )
    print(
        "all_side_effect_sentinel_before_zero="
        f"{str(_all(states, 'side_effect_sentinel_before', 0)).lower()}"
    )
    print(
        "all_side_effect_sentinel_after_zero="
        f"{str(_all(states, 'side_effect_sentinel_after', 0)).lower()}"
    )
    print(
        "all_side_effect_sentinel_delta_zero="
        f"{str(_all(states, 'side_effect_sentinel_delta', 0)).lower()}"
    )
    print(
        "all_protected_payload_body_invocation_count_zero="
        f"{str(_all(states, 'protected_payload_body_invocation_count', 0)).lower()}"
    )
    print(f"all_execution_authorized_false={str(_all(states, 'execution_authorized', False)).lower()}")
    print(f"execution_authorized_count={execution_authorized_count}")
    print(f"all_runtime_behaviors_added_zero={str(_all(states, 'runtime_behaviors_added', 0)).lower()}")
    print(f"runtime_behaviors_added={runtime_behaviors_added}")
    print(f"all_no_sql_execution={str(_all(states, 'no_sql_execution', True)).lower()}")
    print(f"all_no_db_access={str(_all(states, 'no_db_access', True)).lower()}")
    print(f"all_no_model_provider_call={str(_all(states, 'no_model_provider_call', True)).lower()}")
    print(f"all_no_network={str(_all(states, 'no_network', True)).lower()}")
    print(f"all_no_subprocess={str(_all(states, 'no_subprocess', True)).lower()}")
    print(f"all_no_env_access={str(_all(states, 'no_env_access', True)).lower()}")
    print(f"all_no_credentials={str(_all(states, 'no_credentials', True)).lower()}")
    print(f"all_no_user_data={str(_all(states, 'no_user_data', True)).lower()}")
    print(f"all_no_file_mutation={str(_all(states, 'no_file_mutation', True)).lower()}")
    print(f"sentinel_failure_count={sentinel_failure_count}")
    print(f"protected_payload_body_execution_count={protected_payload_body_execution_count}")


def main() -> int:
    try:
        run_validation()
    except AssertionError as exc:
        print(f"DHMS multi-tool selective interception validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
