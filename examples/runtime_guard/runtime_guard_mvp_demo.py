#!/usr/bin/env python3
"""Deterministic incident-shaped AgentFuse Runtime Guard MVP demo."""

from __future__ import annotations

import json

from dhms_agentfuse import GuardedInvocation, RuntimeGuard, ToolCallRequest


FINAL_VERDICT = "AGENTFUSE_RUNTIME_GUARD_MVP_DEMO_PASS"


def run_demo() -> dict[str, object]:
    counters = {
        "delete_file": 0,
        "execute_production_sql": 0,
        "send_external_message": 0,
        "read_project_summary": 0,
    }

    def delete_file(path: str) -> str:
        counters["delete_file"] += 1
        return "synthetic-delete-result"

    def execute_production_sql(statement: str) -> str:
        counters["execute_production_sql"] += 1
        return "synthetic-sql-result"

    def send_external_message(body: str) -> str:
        counters["send_external_message"] += 1
        return "synthetic-message-result"

    def read_project_summary(project: str) -> str:
        counters["read_project_summary"] += 1
        return f"synthetic-summary:{project}"

    guard = RuntimeGuard(
        allow_tools={"read_project_summary"},
        deny_tools={"delete_file", "execute_production_sql", "send_external_message"},
        default_action="block",
    )
    invocations = [
        GuardedInvocation(
            ToolCallRequest("call-delete-001", "delete_file", {"path": "synthetic-example.txt"}),
            delete_file,
        ),
        GuardedInvocation(
            ToolCallRequest(
                "call-sql-001",
                "execute_production_sql",
                {"statement": "SYNTHETIC_PROTECTED_SQL_TEXT"},
            ),
            execute_production_sql,
        ),
        GuardedInvocation(
            ToolCallRequest(
                "call-message-001",
                "send_external_message",
                {"body": "SYNTHETIC_PROTECTED_MESSAGE_BODY"},
            ),
            send_external_message,
        ),
        GuardedInvocation(
            ToolCallRequest(
                "call-read-001",
                "read_project_summary",
                {"project": "agentfuse-local-demo"},
            ),
            read_project_summary,
        ),
    ]
    results = guard.invoke_batch(invocations=invocations)
    records = [result.to_safe_dict() for result in results]
    summary: dict[str, object] = {
        "batch_completed": len(results) == len(invocations),
        "input_order_preserved": [result.tool_call_id for result in results]
        == [invocation.tool_call.tool_call_id for invocation in invocations],
        "handler_execution_counts": counters,
        "results": records,
        "no_real_file_operation": True,
        "no_real_sql_execution": True,
        "no_real_external_message": True,
        "no_network_or_provider_call": True,
        "final_verdict": FINAL_VERDICT,
    }
    _validate(summary)
    return summary


def _validate(summary: dict[str, object]) -> None:
    counters = summary["handler_execution_counts"]
    assert isinstance(counters, dict)
    assert counters == {
        "delete_file": 0,
        "execute_production_sql": 0,
        "send_external_message": 0,
        "read_project_summary": 1,
    }
    results = summary["results"]
    assert isinstance(results, list)
    assert [result["outcome"] for result in results] == [
        "not_executed",
        "not_executed",
        "not_executed",
        "executed",
    ]
    assert summary["batch_completed"] is True
    assert summary["input_order_preserved"] is True


def main() -> None:
    summary = run_demo()
    results = {result["tool_name"]: result for result in summary["results"]}
    for tool_name in ("delete_file", "read_project_summary"):
        result = results[tool_name]
        print(f"{tool_name}:")
        print(f"decision={result['decision']}")
        print(f"outcome={result['outcome']}")
        print(f"handler_invoked={str(result['handler_invoked']).lower()}")
        print()
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(FINAL_VERDICT)


if __name__ == "__main__":
    main()
