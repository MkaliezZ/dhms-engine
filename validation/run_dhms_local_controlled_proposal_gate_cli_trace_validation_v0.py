#!/usr/bin/env python3
"""Validate DHMS local controlled proposal gate CLI traces.

This validator exercises the gate-proposal CLI path through cli.main with
in-memory stdout capture. It does not execute proposals or call external tools.
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from cli import main as cli_main  # noqa: E402


EXAMPLES: Tuple[Tuple[str, str, str, List[str]], ...] = (
    (
        "examples/proposals/safe_read_only_summary.json",
        "safe_read_only_summary_001",
        "RELEASE_CANDIDATE",
        [],
    ),
    (
        "examples/proposals/drop_table.json",
        "drop_table_001",
        "FAIL_CLOSED",
        ["sql_mutation"],
    ),
    (
        "examples/proposals/model_api_request.json",
        "model_api_request_001",
        "FAIL_CLOSED",
        ["model_api"],
    ),
)

REQUIRED_TOP_LEVEL_KEYS = (
    "dhms_gate_version",
    "proposal_id",
    "decision",
    "reason",
    "blocked_capabilities",
    "execution_authorized",
    "runtime_behaviors_added",
    "evidence_trace",
)

REQUIRED_TRACE_TRUE_KEYS = (
    "observed_before_execution",
    "deterministic",
    "stdlib_only",
    "no_sql_execution",
    "no_db_access",
    "no_model_api",
    "no_network",
    "no_subprocess",
    "no_env_access",
    "no_credentials",
    "no_user_data",
    "no_file_mutation",
    "no_langchain",
    "no_kerniq",
    "no_e2b",
    "no_production_runtime",
)


def _run_gate_cli(example_path: str) -> Dict[str, Any]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exit_code = cli_main(["gate-proposal", example_path])
    if exit_code != 0:
        raise AssertionError(f"{example_path}: gate-proposal returned {exit_code}: {stderr.getvalue().strip()}")
    try:
        result = json.loads(stdout.getvalue())
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{example_path}: CLI output is not valid JSON: {exc}") from exc
    if not isinstance(result, dict):
        raise AssertionError(f"{example_path}: CLI output JSON must be an object")
    return result


def _validate_result(
    result: Dict[str, Any],
    example_path: str,
    expected_proposal_id: str,
    expected_decision: str,
    expected_blocked_capabilities: List[str],
) -> None:
    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in result:
            raise AssertionError(f"{example_path}: missing top-level key {key}")

    if result["proposal_id"] != expected_proposal_id:
        raise AssertionError(f"{example_path}: unexpected proposal_id {result['proposal_id']!r}")
    if result["decision"] != expected_decision:
        raise AssertionError(f"{example_path}: unexpected decision {result['decision']!r}")
    if result["execution_authorized"] is not False:
        raise AssertionError(f"{example_path}: execution_authorized must be false")
    if result["runtime_behaviors_added"] != 0:
        raise AssertionError(f"{example_path}: runtime_behaviors_added must be 0")

    blocked_capabilities = result["blocked_capabilities"]
    if not isinstance(blocked_capabilities, list):
        raise AssertionError(f"{example_path}: blocked_capabilities must be a list")
    for expected_blocked in expected_blocked_capabilities:
        if expected_blocked not in blocked_capabilities:
            raise AssertionError(f"{example_path}: missing blocked capability {expected_blocked}")
    if not expected_blocked_capabilities and blocked_capabilities != []:
        raise AssertionError(f"{example_path}: expected no blocked capabilities")

    trace = result["evidence_trace"]
    if not isinstance(trace, dict):
        raise AssertionError(f"{example_path}: evidence_trace must be an object")
    if trace.get("input_file") != example_path:
        raise AssertionError(f"{example_path}: evidence_trace input_file mismatch")
    if trace.get("evaluator") != "local_controlled_proposal_gate":
        raise AssertionError(f"{example_path}: evidence_trace evaluator mismatch")
    for key in REQUIRED_TRACE_TRUE_KEYS:
        if key not in trace:
            raise AssertionError(f"{example_path}: missing evidence_trace key {key}")
        if trace[key] is not True:
            raise AssertionError(f"{example_path}: evidence_trace {key} must be true")


def run_validation() -> None:
    results = []
    for example_path, proposal_id, decision, blocked_capabilities in EXAMPLES:
        result = _run_gate_cli(example_path)
        _validate_result(result, example_path, proposal_id, decision, blocked_capabilities)
        results.append(result)

    release_candidate_count = sum(1 for result in results if result["decision"] == "RELEASE_CANDIDATE")
    fail_closed_count = sum(1 for result in results if result["decision"] == "FAIL_CLOSED")
    hold_for_review_count = sum(1 for result in results if result["decision"] == "HOLD_FOR_REVIEW")
    runtime_behaviors_added = sum(result["runtime_behaviors_added"] for result in results)

    if len(results) != 3:
        raise AssertionError("expected exactly 3 validated CLI examples")
    if release_candidate_count != 1 or fail_closed_count != 2 or hold_for_review_count != 0:
        raise AssertionError("unexpected decision distribution")
    if any(result["execution_authorized"] is not False for result in results):
        raise AssertionError("gate-proposal must not authorize execution")
    if runtime_behaviors_added != 0:
        raise AssertionError("runtime_behaviors_added must remain 0")

    print("DHMS_LOCAL_CONTROLLED_PROPOSAL_GATE_CLI_TRACE_VALIDATION_PASS")
    print("validated_cli_examples=3")
    print("release_candidate=1")
    print("fail_closed=2")
    print("hold_for_review=0")
    print("all_outputs_valid_json=true")
    print("all_execution_authorized_false=true")
    print("all_runtime_behaviors_added_zero=true")
    print("all_observed_before_execution=true")
    print("all_evidence_trace_keys_present=true")
    print("all_evidence_trace_assertions_true=true")
    print("gate_proposal_execution_authorized=false")
    print("runtime_behaviors_added=0")


def main() -> int:
    try:
        run_validation()
    except AssertionError as exc:
        print(f"DHMS local controlled proposal gate CLI trace validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
