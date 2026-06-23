#!/usr/bin/env python3
"""Smoke test for the v0.6.2 SQL Fuse demo CLI.

The smoke test invokes the local CLI demo and checks observable output markers.
It does not execute SQL directly, import sqlite3, create SQLite databases
itself, invoke OpenClaw, invoke DeepSeek, call provider SDKs, call agent SDKs,
use HTTP, or contact external services.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_JSON = ROOT / "reports" / "dhms_agentfuse_bench_sql_v0" / "summary.json"
SUMMARY_MD = ROOT / "reports" / "dhms_agentfuse_bench_sql_v0" / "summary.md"

EXPECTED_OUTPUT_MARKERS = [
    "DHMS SQL Fuse Demo",
    "benchmark_name=DHMS-AgentFuse-Bench SQL v0",
    "cases_total=7",
    "cases_passed=7",
    "release_eligible_count=1",
    "blocked_or_fail_closed_count=6",
    "direct_execution_allowed_count=0",
    "sql_executed_by_benchmark_count=0",
    "sqlite_database_created_by_benchmark_count=0",
    "sandbox_executed_by_benchmark_count=0",
    "mutation_sql_executed_count=0",
    "rejected_input_executed_count=0",
    "failed_checks=[]",
    "linked_actual_release_proof=v0.5.15 existing controlled release validation",
    "demo_executed_sql=false",
    "demo_created_sqlite_database=false",
    "final_verdict=SQL_FUSE_DEMO_PASS",
]


def main() -> int:
    result = run_smoke()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


def run_smoke() -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "cli.py", "demo-sql-fuse"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    stdout = completed.stdout
    missing_markers = [marker for marker in EXPECTED_OUTPUT_MARKERS if marker not in stdout]
    summary_json_exists = SUMMARY_JSON.exists()
    summary_md_exists = SUMMARY_MD.exists()

    summary: dict[str, Any] = {}
    if summary_json_exists:
        try:
            summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            summary = {"failed_parse": True}

    sql_executed_by_demo_count = int(summary.get("sql_executed_by_benchmark_count", -1))
    sqlite_database_created_by_demo_count = int(summary.get("sqlite_database_created_by_benchmark_count", -1))
    failed_checks: list[str] = []
    if completed.returncode != 0:
        failed_checks.append("cli_demo_exit_code_nonzero")
    if missing_markers:
        failed_checks.append("expected_output_markers_missing")
    if not summary_json_exists:
        failed_checks.append("summary_json_missing")
    if not summary_md_exists:
        failed_checks.append("summary_md_missing")
    if sql_executed_by_demo_count != 0:
        failed_checks.append("sql_executed_by_demo_count_not_zero")
    if sqlite_database_created_by_demo_count != 0:
        failed_checks.append("sqlite_database_created_by_demo_count_not_zero")

    status = "PASS" if not failed_checks else "FAIL"
    return {
        "validation": "sql_fuse_demo_cli_smoke_v0_6_2",
        "status": status,
        "cli_demo_invoked": True,
        "cli_demo_exit_code": completed.returncode,
        "expected_output_markers_present": not missing_markers,
        "missing_output_markers": missing_markers,
        "summary_json_exists": summary_json_exists,
        "summary_md_exists": summary_md_exists,
        "sql_executed_by_demo_count": sql_executed_by_demo_count,
        "sqlite_database_created_by_demo_count": sqlite_database_created_by_demo_count,
        "failed_checks": failed_checks,
        "benchmark_runner_executed_sql": False,
        "benchmark_runner_imported_sqlite3": False,
        "benchmark_runner_created_sqlite_database": False,
        "openclaw_invoked": False,
        "deepseek_invoked": False,
        "provider_sdk_invoked": False,
        "agent_sdk_invoked": False,
        "http_adapter_invoked": False,
        "final_verdict": (
            "READY_FOR_V0_6_3_MINIMAL_API_ADAPTER_SKELETON"
            if status == "PASS"
            else "NEEDS_SQL_FUSE_DEMO_CLI_FIX"
        ),
    }


if __name__ == "__main__":
    raise SystemExit(main())
