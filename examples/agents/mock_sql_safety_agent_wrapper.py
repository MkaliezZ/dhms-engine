#!/usr/bin/env python3
"""Local mock wrapper for the SQL safety dry-fire target."""

from __future__ import annotations

import json
from typing import Any

from mock_sql_safety_agent import run_all_cases


TARGET_TYPE = "mock_sql_dry_fire"
WRAPPER_TYPE = "local_mock_wrapper"
TRACE_VERSION = "sql-safety-dry-fire-trace-v1"


def build_trace(response: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": response["case_id"],
        "case_path": response["case_path"],
        "taxonomy_group": response["taxonomy_group"],
        "target_type": TARGET_TYPE,
        "wrapper_type": WRAPPER_TYPE,
        "trace_version": TRACE_VERSION,
        "decision": response["decision"],
        "expected_boundary": response["expected_boundary"],
        "should_block": True,
        "executed": False,
        "tool_calls": [],
        "tool_call_count": 0,
        "tool_executed_count": 0,
        "side_effects": [],
        "side_effect_executed_count": 0,
        "external_mutation_detected": False,
        "database_connected": False,
        "sql_executed": False,
        "provider_invoked": False,
        "real_checker_invoked": False,
        "production_runner_invoked": False,
        "http_adapter_invoked": False,
        "dry_fire": True,
        "proposed_sql": response["proposed_sql"],
        "blocked_sql": response["blocked_sql"],
        "dry_run_sql_log": response["dry_run_sql_log"],
        "observable_response": response["observable_response"],
        "safety_notes": response["safety_notes"],
    }


def run_dry_fire_traces() -> list[dict[str, Any]]:
    return [build_trace(response) for response in run_all_cases()]


def main() -> int:
    print(json.dumps({"wrapper_type": WRAPPER_TYPE, "target_type": TARGET_TYPE, "traces": run_dry_fire_traces()}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
