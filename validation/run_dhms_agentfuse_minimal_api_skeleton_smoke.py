#!/usr/bin/env python3
"""Smoke test for the DHMS AgentFuse Minimal API skeleton v0.6.3.

This validation is in-memory only. It does not execute SQL, import sqlite3,
create SQLite databases, invoke OpenClaw, invoke DeepSeek, use provider SDKs,
use agent SDKs, perform HTTP/network calls, perform shell execution, perform
file operation policy, call MCP, or run full suite validation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
root_value = str(ROOT)
if root_value not in sys.path:
    sys.path.insert(0, root_value)

from dhms_agentfuse import ALLOWLISTED_SQL, run_non_executing_agentfuse_flow  # noqa: E402


def main() -> int:
    result = run_smoke()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


def run_smoke() -> dict[str, Any]:
    cases = [
        {
            "case_id": "allowlisted_sql_candidate_held",
            "tool_name": "sql.query",
            "tool_type": "SQL",
            "requested_effect": "read_sandbox_candidate",
            "payload": {"sql": ALLOWLISTED_SQL},
            "expected_decisions": {"ALLOWLIST_CANDIDATE_HELD", "SANDBOX_HELD"},
            "expected_release_eligible": True,
        },
        {
            "case_id": "mutation_sql_blocked",
            "tool_name": "sql.query",
            "tool_type": "SQL",
            "requested_effect": "write_database",
            "payload": {"sql": "DELETE FROM toy_accounts WHERE id = 1;"},
            "expected_decisions": {"BLOCK", "FAIL_CLOSED"},
            "expected_release_eligible": False,
        },
        {
            "case_id": "non_sql_unsupported_blocked",
            "tool_name": "openclaw.runtime",
            "tool_type": "OPENCLAW",
            "requested_effect": "external_runtime_action",
            "payload": {"action": "inert unsupported proposal"},
            "expected_decisions": {"BLOCK", "FAIL_CLOSED"},
            "expected_release_eligible": False,
        },
    ]

    case_results = [evaluate_case(case) for case in cases]
    failed_checks = [
        f"{case_result['case_id']}.{check}"
        for case_result in case_results
        for check in case_result["failed_checks"]
    ]

    executed_count = sum(1 for result in case_results if result["executed"])
    direct_execution_allowed_count = sum(1 for result in case_results if result["direct_execution_allowed"])
    release_eligible_or_held_count = sum(1 for result in case_results if result["release_eligible"])
    blocked_or_fail_closed_count = sum(
        1 for result in case_results if result["decision"] in {"BLOCK", "FAIL_CLOSED"}
    )
    cases_passed = sum(1 for result in case_results if result["passed"])

    if executed_count != 0:
        failed_checks.append("executed_count_not_zero")
    if direct_execution_allowed_count != 0:
        failed_checks.append("direct_execution_allowed_count_not_zero")
    if release_eligible_or_held_count != 1:
        failed_checks.append("release_eligible_or_held_count_not_one")
    if blocked_or_fail_closed_count != 2:
        failed_checks.append("blocked_or_fail_closed_count_not_two")

    status = "PASS" if not failed_checks and cases_passed == 3 else "FAIL"
    return {
        "smoke_name": "DHMS AgentFuse Minimal API Skeleton Smoke",
        "version": "v0.6.3",
        "status": status,
        "cases_total": len(cases),
        "cases_passed": cases_passed,
        "executed_count": executed_count,
        "direct_execution_allowed_count": direct_execution_allowed_count,
        "release_eligible_or_held_count": release_eligible_or_held_count,
        "blocked_or_fail_closed_count": blocked_or_fail_closed_count,
        "failed_checks": failed_checks,
        "sql_executed": False,
        "sqlite_database_created": False,
        "sandbox_created": False,
        "openclaw_invoked": False,
        "deepseek_invoked": False,
        "provider_sdk_invoked": False,
        "agent_sdk_invoked": False,
        "http_adapter_invoked": False,
        "file_shell_mcp_policy_added": False,
        "final_verdict": (
            "DHMS_AGENTFUSE_MINIMAL_API_SKELETON_PASS"
            if status == "PASS"
            else "DHMS_AGENTFUSE_MINIMAL_API_SKELETON_FAIL"
        ),
        "case_results": case_results,
    }


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    trace = run_non_executing_agentfuse_flow(
        source="minimal_api_skeleton_smoke",
        intent_summary=case["case_id"],
        raw_event={"case_id": case["case_id"]},
        tool_name=case["tool_name"],
        tool_type=case["tool_type"],
        requested_effect=case["requested_effect"],
        payload=case["payload"],
        metadata={"smoke_case": case["case_id"]},
    )
    failed_checks: list[str] = []
    decision = trace.safety_decision.decision
    if decision not in case["expected_decisions"]:
        failed_checks.append("unexpected_decision")
    if trace.executed:
        failed_checks.append("trace_executed")
    if trace.execution_result is not None:
        failed_checks.append("trace_has_execution_result")
    if trace.gate_decision.execution_allowed:
        failed_checks.append("gate_execution_allowed")
    if trace.safety_decision.direct_execution_allowed:
        failed_checks.append("direct_execution_allowed")
    if trace.safety_decision.release_eligible != case["expected_release_eligible"]:
        failed_checks.append("release_eligible_mismatch")

    return {
        "case_id": case["case_id"],
        "passed": not failed_checks,
        "decision": decision,
        "gate_state": trace.gate_decision.gate_state,
        "release_eligible": trace.safety_decision.release_eligible,
        "direct_execution_allowed": trace.safety_decision.direct_execution_allowed,
        "execution_allowed": trace.gate_decision.execution_allowed,
        "executed": trace.executed,
        "execution_result": trace.execution_result,
        "failed_checks": failed_checks,
    }


if __name__ == "__main__":
    raise SystemExit(main())
