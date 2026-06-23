#!/usr/bin/env python3
"""Smoke validation for DHMS AgentFuse Protocol Examples v0.7.1.

The smoke test may use safe local Python subprocesses to run the example
scripts. It does not execute SQL, import sqlite3, create SQLite databases,
invoke OpenClaw, invoke DeepSeek, import provider SDKs, import agent SDKs,
perform HTTP/network calls, perform file operation policy, call MCP, or run
full suite validation.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "examples" / "dhms_agentfuse"
TRACE_EXAMPLES_PATH = EXAMPLES_DIR / "trace_examples.json"

EXAMPLE_COMMANDS = [
    (
        "sql_fuse_allowlisted_candidate",
        EXAMPLES_DIR / "sql_fuse_allowlisted_candidate_example.py",
        "SQL_FUSE_ALLOWLISTED_CANDIDATE_EXAMPLE_PASS",
    ),
    (
        "sql_mutation_blocked",
        EXAMPLES_DIR / "sql_mutation_blocked_example.py",
        "SQL_MUTATION_BLOCKED_EXAMPLE_PASS",
    ),
    (
        "unsupported_non_sql_proposal",
        EXAMPLES_DIR / "unsupported_non_sql_proposal_example.py",
        "UNSUPPORTED_NON_SQL_PROPOSAL_EXAMPLE_PASS",
    ),
]


def main() -> int:
    result = run_smoke()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


def run_smoke() -> dict[str, Any]:
    example_results = [run_example(name, path, verdict) for name, path, verdict in EXAMPLE_COMMANDS]
    trace_validation = validate_trace_examples()

    failed_checks = [
        f"{result['example_name']}.{check}"
        for result in example_results
        for check in result["failed_checks"]
    ]
    failed_checks.extend(trace_validation["failed_checks"])

    examples_passed = sum(1 for result in example_results if result["passed"])
    executed_count = sum(int(result["executed"]) for result in example_results)
    direct_execution_allowed_count = sum(int(result["direct_execution_allowed"]) for result in example_results)
    executed_count += trace_validation["executed_count"]
    direct_execution_allowed_count += trace_validation["direct_execution_allowed_count"]

    if executed_count != 0:
        failed_checks.append("executed_count_not_zero")
    if direct_execution_allowed_count != 0:
        failed_checks.append("direct_execution_allowed_count_not_zero")

    status = "PASS" if not failed_checks and examples_passed == 3 and trace_validation["trace_examples_total"] == 3 else "FAIL"
    return {
        "smoke_name": "DHMS AgentFuse Protocol Examples Smoke",
        "version": "v0.7.1",
        "status": status,
        "examples_total": len(EXAMPLE_COMMANDS),
        "trace_examples_total": trace_validation["trace_examples_total"],
        "examples_passed": examples_passed,
        "executed_count": executed_count,
        "direct_execution_allowed_count": direct_execution_allowed_count,
        "failed_checks": failed_checks,
        "example_results": example_results,
        "trace_validation": trace_validation,
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
            "DHMS_AGENTFUSE_PROTOCOL_EXAMPLES_PASS"
            if status == "PASS"
            else "DHMS_AGENTFUSE_PROTOCOL_EXAMPLES_FAIL"
        ),
    }


def run_example(name: str, path: Path, expected_verdict: str) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    failed_checks: list[str] = []
    parsed: dict[str, Any] = {}
    if completed.returncode != 0:
        failed_checks.append("example_exit_code_nonzero")
    if expected_verdict not in completed.stdout:
        failed_checks.append("expected_verdict_missing")
    try:
        parsed = json.loads(completed.stdout)
    except json.JSONDecodeError:
        failed_checks.append("example_output_not_json")

    executed = bool(parsed.get("executed", True))
    direct_execution_allowed = bool(parsed.get("direct_execution_allowed", True))
    execution_allowed = bool(parsed.get("execution_allowed", True))
    if executed:
        failed_checks.append("example_executed")
    if direct_execution_allowed:
        failed_checks.append("example_direct_execution_allowed")
    if execution_allowed:
        failed_checks.append("example_execution_allowed")

    return {
        "example_name": name,
        "passed": not failed_checks,
        "exit_code": completed.returncode,
        "expected_verdict": expected_verdict,
        "executed": executed,
        "direct_execution_allowed": direct_execution_allowed,
        "execution_allowed": execution_allowed,
        "failed_checks": failed_checks,
    }


def validate_trace_examples() -> dict[str, Any]:
    failed_checks: list[str] = []
    try:
        trace_doc = json.loads(TRACE_EXAMPLES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "trace_examples_total": 0,
            "executed_count": 0,
            "direct_execution_allowed_count": 0,
            "failed_checks": ["trace_examples_json_invalid"],
        }

    traces = trace_doc.get("trace_examples", [])
    if len(traces) != 3:
        failed_checks.append("trace_examples_total_not_three")

    executed_count = 0
    direct_execution_allowed_count = 0
    for trace in traces:
        example_id = trace.get("example_id", "unknown")
        agentfuse_trace = trace.get("agentfuse_trace", {})
        safety_decision = trace.get("safety_decision", {})
        gate_decision = trace.get("execution_gate_decision", {})
        if agentfuse_trace.get("executed") is not False:
            failed_checks.append(f"{example_id}.trace_executed_not_false")
            executed_count += 1
        if agentfuse_trace.get("execution_result") is not None:
            failed_checks.append(f"{example_id}.execution_result_not_null")
        if safety_decision.get("direct_execution_allowed") is not False:
            failed_checks.append(f"{example_id}.direct_execution_allowed_not_false")
            direct_execution_allowed_count += 1
        if gate_decision.get("execution_allowed") is not False:
            failed_checks.append(f"{example_id}.execution_allowed_not_false")
        if agentfuse_trace.get("tool_family") != "DHMS AgentFuse":
            failed_checks.append(f"{example_id}.tool_family_mismatch")
        if "production-ready" in json.dumps(trace).lower():
            failed_checks.append(f"{example_id}.production_ready_claim_detected")

    return {
        "trace_examples_total": len(traces),
        "executed_count": executed_count,
        "direct_execution_allowed_count": direct_execution_allowed_count,
        "failed_checks": failed_checks,
    }


if __name__ == "__main__":
    raise SystemExit(main())
