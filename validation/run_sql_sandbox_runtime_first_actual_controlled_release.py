#!/usr/bin/env python3
"""Run the v0.5.15 first actual controlled SQL sandbox release validation."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from sql_sandbox_runtime_first_actual_controlled_release import (
    run_sql_sandbox_runtime_first_actual_controlled_release,
)


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT_SCRIPTS = [
    "validation/run_execution_runtime_contract_stub.py",
    "validation/run_tool_call_interceptor_stub.py",
    "validation/run_sql_safety_runtime_mount_stub.py",
    "validation/run_runtime_dry_run_loop_stub.py",
    "validation/run_runtime_execution_gate_stub.py",
    "validation/run_sql_sandbox_runtime_bridge_stub.py",
    "validation/run_sql_sandbox_runtime_bridge_first_held_release_review.py",
    "validation/run_sql_sandbox_runtime_bridge_first_controlled_release_stub.py",
    "validation/run_sql_sandbox_runtime_bridge_actual_release_authorization_review.py",
    "validation/run_sql_sandbox_runtime_first_actual_release_boundary_stub.py",
    "validation/run_sql_safety_temp_sqlite_select_only_first_real_run.py",
    "validation/run_sql_safety_temp_sqlite_mutation_block_test.py",
]


def main() -> int:
    preflight_results = [run_preflight(script) for script in PREFLIGHT_SCRIPTS]
    result = run_sql_sandbox_runtime_first_actual_controlled_release()
    failed_preflights = [
        preflight["script"]
        for preflight in preflight_results
        if preflight.get("status") != "PASS"
    ]
    if failed_preflights:
        result["failed_checks"].extend(f"preflight_failed:{script}" for script in failed_preflights)
        result["status"] = "FAIL"
        result["final_verdict"] = "NEEDS_SQL_SANDBOX_RUNTIME_FIRST_ACTUAL_CONTROLLED_RELEASE_FIX"

    result["preflight_results"] = preflight_results
    result["all_preflights_passed"] = not failed_preflights
    result["preflight_scripts"] = PREFLIGHT_SCRIPTS
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


def run_preflight(script: str) -> dict[str, Any]:
    completed = subprocess.run(
        ["python3", script],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    parsed: dict[str, Any] = {}
    if completed.stdout.strip():
        try:
            parsed = json.loads(completed.stdout)
        except json.JSONDecodeError:
            parsed = {"status": "FAIL", "parse_error": "stdout was not valid JSON"}
    status = "PASS" if completed.returncode == 0 and parsed.get("status") == "PASS" else "FAIL"
    return {
        "script": script,
        "status": status,
        "returncode": completed.returncode,
        "validation": parsed.get("validation"),
        "final_verdict": parsed.get("final_verdict"),
        "failed_checks": parsed.get("failed_checks", []),
    }


if __name__ == "__main__":
    raise SystemExit(main())
