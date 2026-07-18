"""Contract tests for the two trial-ready Runtime Guard demos."""

from __future__ import annotations

import json

from examples.runtime_guard.langgraph_runtime_guard_demo import run_demo as run_langgraph_demo
from examples.runtime_guard.runtime_guard_mvp_demo import run_demo as run_runtime_demo


def test_runtime_guard_demo_is_incident_shaped_and_deterministic() -> None:
    first = run_runtime_demo()
    second = run_runtime_demo()

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["handler_execution_counts"] == {
        "delete_file": 0,
        "execute_production_sql": 0,
        "send_external_message": 0,
        "read_project_summary": 1,
    }
    assert first["final_verdict"] == "AGENTFUSE_RUNTIME_GUARD_MVP_DEMO_PASS"


def test_langgraph_runtime_guard_demo_uses_real_dispatch_and_is_deterministic() -> None:
    first = run_langgraph_demo()
    second = run_langgraph_demo()

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["real_langgraph_graph_invoked"] is True
    assert first["real_tool_node_dispatch"] is True
    assert first["handler_execution_counts"] == {
        "delete_file": 0,
        "execute_production_sql": 1,
        "read_project_summary": 1,
    }
    assert first["final_verdict"] == "AGENTFUSE_LANGGRAPH_RUNTIME_GUARD_DEMO_PASS"


def test_demo_outputs_exclude_protected_payloads() -> None:
    serialized = json.dumps(
        {"runtime": run_runtime_demo(), "langgraph": run_langgraph_demo()},
        sort_keys=True,
    )

    assert "SYNTHETIC_PROTECTED_SQL_TEXT" not in serialized
    assert "SYNTHETIC_PROTECTED_MESSAGE_BODY" not in serialized
    assert "SYNTHETIC_PROTECTED_EXCEPTION_TEXT" not in serialized
