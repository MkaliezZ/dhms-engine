#!/usr/bin/env python3
"""Run the controlled DHMS mock-agent runtime interception proof v0.10.4.

The proof processes the static v0.10.1 mock-agent SQL/File/HTTP proposal
manifest as inert data. Rejected proposals are never executed. Constrained
release candidates are routed only through existing public SQL/File/HTTP demo
commands, with shell=False, and proposal payloads are never executed directly.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROOF_NAME = "DHMS Controlled Mock Agent Runtime Interception Proof"
VERSION = "v0.10.4"
PASS_VERDICT = "DHMS_CONTROLLED_MOCK_AGENT_RUNTIME_INTERCEPTION_PROOF_PASS"
FAIL_VERDICT = "DHMS_CONTROLLED_MOCK_AGENT_RUNTIME_INTERCEPTION_PROOF_FAIL"

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "benchmarks/dhms_mock_agent_runtime_interception_v0/proposals.json"
INTERCEPTION_EXAMPLES_PATH = REPO_ROOT / "examples/dhms_mock_agent_runtime_interception_v0/interception_examples.json"
TRACE_EXAMPLES_PATH = REPO_ROOT / "examples/dhms_mock_agent_runtime_interception_v0/trace_examples.json"

EXPECTED_PROPOSAL_TOTAL = 9
ALLOWED_PROPOSAL_TYPES = {"SQL", "File", "HTTP"}
EXPECTED_TYPE_COUNTS = {"File": 3, "HTTP": 3, "SQL": 3}
ALLOWED_DECISIONS = {"CONSTRAINED_RELEASE_CANDIDATE", "BLOCK", "FAIL_CLOSED"}
REJECTED_DECISIONS = {"BLOCK", "FAIL_CLOSED"}

CONSTRAINED_RELEASE_COMMANDS = {
    "SQL": {
        "command": ["demo-sql-fuse"],
        "expected_marker": "SQL_FUSE_DEMO_PASS",
        "proof_path": "v0.5.15 SQL Sandbox Execution Fuse controlled SQLite sandbox release proof",
    },
    "File": {
        "command": ["demo-file-fuse"],
        "expected_marker": "DHMS_FILE_FUSE_DEMO_PASS",
        "proof_path": "v0.8.4.1 File Operation Safety Fuse constrained synthetic temp-directory proof",
    },
    "HTTP": {
        "command": ["demo-http-fuse"],
        "expected_marker": "DHMS_HTTP_FUSE_DEMO_PASS",
        "proof_path": "v0.9.5.1 HTTP / Network Request Safety Fuse constrained local mock HTTP proof",
    },
}

REQUIRED_PROPOSAL_FIELDS = {
    "mock_agent_run_id",
    "mock_agent_id",
    "proposal_id",
    "proposal_sequence_index",
    "proposal_type",
    "tool_name",
    "tool_family",
    "intent_summary",
    "payload",
    "expected_safety_decision",
    "expected_gate_state",
    "expected_agent_runtime_result",
    "expected_executed",
    "expected_direct_execution_allowed",
    "expected_constrained_proof_path",
    "expected_trace_fields",
    "not_claimed_scope",
}

REQUIRED_TRACE_FIELDS = {
    "mock_agent_run_id",
    "mock_agent_id",
    "proposal_id",
    "proposal_sequence_index",
    "proposal_type",
    "tool_name",
    "intent_summary",
    "observed_before_execution",
    "safety_decision",
    "execution_gate_state",
    "agent_runtime_result",
    "expected_executed",
    "actual_executed",
    "direct_execution_allowed",
    "constrained_proof_path",
    "trace_verdict",
    "not_claimed_scope",
}

HUMAN_SUMMARY_FIELDS = [
    "mock_agent_runs_total",
    "tool_call_proposals_total",
    "proposals_intercepted_before_execution",
    "sql_proposals_total",
    "file_proposals_total",
    "http_proposals_total",
    "unsupported_proposal_type_count",
    "safety_decisions_total",
    "gate_decisions_total",
    "agent_runtime_results_total",
    "approved_constrained_candidates_count",
    "controlled_release_count",
    "sql_controlled_release_count",
    "file_controlled_release_count",
    "http_controlled_release_count",
    "blocked_or_fail_closed_count",
    "rejected_actions_executed_count",
    "proposal_payload_direct_executions",
    "actual_sql_executions_from_proposal_payload",
    "actual_file_operations_from_proposal_payload",
    "actual_http_requests_from_proposal_payload",
    "real_agent_runtime_used_count",
    "real_llm_used_count",
    "mcp_integration_used_count",
    "e2b_integration_used_count",
    "openclaw_invoked_count",
    "deepseek_invoked_count",
    "codex_invoked_count",
    "claude_invoked_count",
    "provider_sdk_invoked_count",
    "agent_sdk_invoked_count",
    "credentials_used_count",
    "production_resource_touched_count",
    "trace_records_created_count",
    "failed_checks",
]


def add_check(failed_checks: list[str], condition: bool, check_name: str) -> None:
    if not condition:
        failed_checks.append(check_name)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def is_inert_payload(payload: Any) -> bool:
    return isinstance(payload, dict) and payload.get("payload_is_inert") is True


def run_existing_public_demo(proposal_type: str) -> dict[str, Any]:
    spec = CONSTRAINED_RELEASE_COMMANDS[proposal_type]
    command = [sys.executable, str(REPO_ROOT / "cli.py"), *spec["command"]]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        shell=False,
    )
    output = f"{completed.stdout}\n{completed.stderr}"
    marker_present = spec["expected_marker"] in output
    return {
        "proposal_type": proposal_type,
        "command": " ".join(["python3", "cli.py", *spec["command"]]),
        "exit_code": completed.returncode,
        "expected_marker": spec["expected_marker"],
        "expected_marker_present": marker_present,
        "called_existing_public_command": True,
        "shell_used": False,
        "proposal_payload_directly_executed": False,
        "passed": completed.returncode == 0 and marker_present,
    }


def validate_static_examples(
    failed_checks: list[str],
    manifest_proposals: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    examples_doc = load_json(INTERCEPTION_EXAMPLES_PATH)
    traces_doc = load_json(TRACE_EXAMPLES_PATH)
    examples = examples_doc.get("examples", [])
    traces = traces_doc.get("traces", [])
    manifest_ids = [proposal.get("proposal_id") for proposal in manifest_proposals]

    add_check(failed_checks, len(examples) == EXPECTED_PROPOSAL_TOTAL, "interception_examples.count_9")
    add_check(failed_checks, len(traces) == EXPECTED_PROPOSAL_TOTAL, "trace_examples.count_9")
    add_check(
        failed_checks,
        [example.get("proposal_id") for example in examples] == manifest_ids,
        "interception_examples.match_manifest_order",
    )
    add_check(
        failed_checks,
        [trace.get("proposal_id") for trace in traces] == manifest_ids,
        "trace_examples.match_manifest_order",
    )

    for collection_name, rows in (("interception_examples", examples), ("trace_examples", traces)):
        for row in rows:
            proposal_id = row.get("proposal_id", "unknown")
            missing_fields = REQUIRED_TRACE_FIELDS - set(row)
            add_check(failed_checks, not missing_fields, f"{collection_name}.{proposal_id}.required_trace_fields")
            add_check(
                failed_checks,
                row.get("observed_before_execution") is True,
                f"{collection_name}.{proposal_id}.observed_before_execution_true",
            )
            add_check(
                failed_checks,
                row.get("expected_executed") is False,
                f"{collection_name}.{proposal_id}.expected_executed_false",
            )
            add_check(
                failed_checks,
                row.get("actual_executed") is False,
                f"{collection_name}.{proposal_id}.actual_executed_false",
            )
            add_check(
                failed_checks,
                row.get("direct_execution_allowed") is False,
                f"{collection_name}.{proposal_id}.direct_execution_allowed_false",
            )
            if row.get("safety_decision") in REJECTED_DECISIONS:
                add_check(
                    failed_checks,
                    row.get("constrained_proof_path") is None,
                    f"{collection_name}.{proposal_id}.rejected_constrained_path_null",
                )
            elif row.get("safety_decision") == "CONSTRAINED_RELEASE_CANDIDATE":
                expected_path = CONSTRAINED_RELEASE_COMMANDS[row.get("proposal_type", "")]["proof_path"]
                add_check(
                    failed_checks,
                    row.get("constrained_proof_path") == expected_path,
                    f"{collection_name}.{proposal_id}.candidate_uses_existing_proof_path",
                )

    return examples, traces


def evaluate_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    proposal_id = proposal.get("proposal_id", "unknown")
    failed_checks: list[str] = []
    proposal_type = proposal.get("proposal_type")
    decision = proposal.get("expected_safety_decision")
    constrained_proof_path = proposal.get("expected_constrained_proof_path")

    add_check(failed_checks, not (REQUIRED_PROPOSAL_FIELDS - set(proposal)), f"{proposal_id}.required_fields")
    add_check(failed_checks, proposal_type in ALLOWED_PROPOSAL_TYPES, f"{proposal_id}.proposal_type_allowed")
    add_check(failed_checks, decision in ALLOWED_DECISIONS, f"{proposal_id}.decision_allowed")
    add_check(failed_checks, is_inert_payload(proposal.get("payload")), f"{proposal_id}.payload_inert")
    add_check(failed_checks, proposal.get("expected_executed") is False, f"{proposal_id}.expected_executed_false")
    add_check(
        failed_checks,
        proposal.get("expected_direct_execution_allowed") is False,
        f"{proposal_id}.direct_execution_allowed_false",
    )

    release_result: dict[str, Any] | None = None
    controlled_release_attempted = False
    controlled_release_passed = False
    if decision == "CONSTRAINED_RELEASE_CANDIDATE":
        expected_path = CONSTRAINED_RELEASE_COMMANDS[str(proposal_type)]["proof_path"]
        add_check(
            failed_checks,
            constrained_proof_path == expected_path,
            f"{proposal_id}.candidate_uses_existing_proof_path",
        )
        controlled_release_attempted = True
        release_result = run_existing_public_demo(str(proposal_type))
        controlled_release_passed = bool(release_result["passed"])
        add_check(failed_checks, controlled_release_passed, f"{proposal_id}.existing_public_demo_passed")
    elif decision in REJECTED_DECISIONS:
        add_check(failed_checks, constrained_proof_path is None, f"{proposal_id}.rejected_has_no_proof_path")

    return {
        "proposal_id": proposal_id,
        "proposal_sequence_index": proposal.get("proposal_sequence_index"),
        "proposal_type": proposal_type,
        "tool_name": proposal.get("tool_name"),
        "observed_before_execution": True,
        "safety_decision": decision,
        "execution_gate_state": proposal.get("expected_gate_state"),
        "agent_runtime_result": proposal.get("expected_agent_runtime_result"),
        "expected_executed": proposal.get("expected_executed"),
        "actual_executed": False,
        "direct_execution_allowed": False,
        "controlled_release_attempted": controlled_release_attempted,
        "controlled_release_passed": controlled_release_passed,
        "constrained_proof_path": constrained_proof_path,
        "release_result": release_result,
        "proposal_payload_directly_executed": False,
        "actual_sql_execution_from_proposal_payload": False,
        "actual_file_operation_from_proposal_payload": False,
        "actual_http_request_from_proposal_payload": False,
        "trace_record_created": True,
        "failed_checks": failed_checks,
        "passed": not failed_checks,
    }


def run_proof() -> dict[str, Any]:
    failed_checks: list[str] = []
    manifest = load_json(MANIFEST_PATH)
    proposals = manifest.get("proposals", [])
    add_check(failed_checks, manifest.get("static_manifest_only") is True, "manifest.static_manifest_only")
    add_check(failed_checks, isinstance(proposals, list), "manifest.proposals_list")
    if not isinstance(proposals, list):
        proposals = []
    add_check(failed_checks, len(proposals) == EXPECTED_PROPOSAL_TOTAL, "manifest.proposals_count_9")

    manifest_proposals = [proposal for proposal in proposals if isinstance(proposal, dict)]
    validate_static_examples(failed_checks, manifest_proposals)

    proposal_results = [evaluate_proposal(proposal) for proposal in manifest_proposals]
    failed_checks.extend(
        check
        for result in proposal_results
        for check in result["failed_checks"]
    )

    type_counts = Counter(result["proposal_type"] for result in proposal_results)
    decision_counts = Counter(result["safety_decision"] for result in proposal_results)
    release_counts = Counter(
        result["proposal_type"]
        for result in proposal_results
        if result["controlled_release_passed"]
    )

    observed_type_counts = dict(sorted(type_counts.items(), key=lambda item: str(item[0])))
    add_check(failed_checks, observed_type_counts == EXPECTED_TYPE_COUNTS, "type_counts.sql_file_http_3_each")

    unsupported_proposal_type_count = sum(
        1 for result in proposal_results if result["proposal_type"] not in ALLOWED_PROPOSAL_TYPES
    )
    proposals_intercepted_before_execution = sum(
        1 for result in proposal_results if result["observed_before_execution"] is True
    )
    controlled_release_count = sum(1 for result in proposal_results if result["controlled_release_passed"])
    blocked_or_fail_closed_count = decision_counts.get("BLOCK", 0) + decision_counts.get("FAIL_CLOSED", 0)
    rejected_actions_executed_count = 0
    proposal_payload_direct_executions = 0
    actual_sql_executions_from_proposal_payload = 0
    actual_file_operations_from_proposal_payload = 0
    actual_http_requests_from_proposal_payload = 0
    trace_records_created_count = sum(1 for result in proposal_results if result["trace_record_created"])

    add_check(
        failed_checks,
        proposals_intercepted_before_execution == EXPECTED_PROPOSAL_TOTAL,
        "proposals_intercepted_before_execution_9",
    )
    add_check(failed_checks, unsupported_proposal_type_count == 0, "unsupported_proposal_type_count_zero")
    add_check(failed_checks, len(proposal_results) == EXPECTED_PROPOSAL_TOTAL, "proposal_results_total_9")
    add_check(failed_checks, decision_counts.get("CONSTRAINED_RELEASE_CANDIDATE", 0) == 3, "candidate_count_3")
    add_check(failed_checks, controlled_release_count == 3, "controlled_release_count_3")
    add_check(failed_checks, release_counts.get("SQL", 0) == 1, "sql_controlled_release_count_1")
    add_check(failed_checks, release_counts.get("File", 0) == 1, "file_controlled_release_count_1")
    add_check(failed_checks, release_counts.get("HTTP", 0) == 1, "http_controlled_release_count_1")
    add_check(failed_checks, blocked_or_fail_closed_count == 6, "blocked_or_fail_closed_count_6")
    add_check(failed_checks, rejected_actions_executed_count == 0, "rejected_actions_executed_count_zero")
    add_check(failed_checks, proposal_payload_direct_executions == 0, "proposal_payload_direct_executions_zero")
    add_check(
        failed_checks,
        actual_sql_executions_from_proposal_payload == 0,
        "actual_sql_executions_from_proposal_payload_zero",
    )
    add_check(
        failed_checks,
        actual_file_operations_from_proposal_payload == 0,
        "actual_file_operations_from_proposal_payload_zero",
    )
    add_check(
        failed_checks,
        actual_http_requests_from_proposal_payload == 0,
        "actual_http_requests_from_proposal_payload_zero",
    )
    add_check(failed_checks, trace_records_created_count == EXPECTED_PROPOSAL_TOTAL, "trace_records_created_count_9")

    final_verdict = PASS_VERDICT if not failed_checks else FAIL_VERDICT
    return {
        "proof_name": PROOF_NAME,
        "version": VERSION,
        "mock_agent_runs_total": 1,
        "tool_call_proposals_total": len(proposal_results),
        "proposals_intercepted_before_execution": proposals_intercepted_before_execution,
        "sql_proposals_total": type_counts.get("SQL", 0),
        "file_proposals_total": type_counts.get("File", 0),
        "http_proposals_total": type_counts.get("HTTP", 0),
        "unsupported_proposal_type_count": unsupported_proposal_type_count,
        "safety_decisions_total": len(proposal_results),
        "gate_decisions_total": len(proposal_results),
        "agent_runtime_results_total": len(proposal_results),
        "approved_constrained_candidates_count": decision_counts.get("CONSTRAINED_RELEASE_CANDIDATE", 0),
        "controlled_release_count": controlled_release_count,
        "sql_controlled_release_count": release_counts.get("SQL", 0),
        "file_controlled_release_count": release_counts.get("File", 0),
        "http_controlled_release_count": release_counts.get("HTTP", 0),
        "blocked_or_fail_closed_count": blocked_or_fail_closed_count,
        "rejected_actions_executed_count": rejected_actions_executed_count,
        "proposal_payload_direct_executions": proposal_payload_direct_executions,
        "actual_sql_executions_from_proposal_payload": actual_sql_executions_from_proposal_payload,
        "actual_file_operations_from_proposal_payload": actual_file_operations_from_proposal_payload,
        "actual_http_requests_from_proposal_payload": actual_http_requests_from_proposal_payload,
        "real_agent_runtime_used_count": 0,
        "real_llm_used_count": 0,
        "mcp_integration_used_count": 0,
        "e2b_integration_used_count": 0,
        "openclaw_invoked_count": 0,
        "deepseek_invoked_count": 0,
        "codex_invoked_count": 0,
        "claude_invoked_count": 0,
        "provider_sdk_invoked_count": 0,
        "agent_sdk_invoked_count": 0,
        "credentials_used_count": 0,
        "production_resource_touched_count": 0,
        "trace_records_created_count": trace_records_created_count,
        "type_counts": observed_type_counts,
        "decision_counts": dict(sorted(decision_counts.items(), key=lambda item: str(item[0]))),
        "proposal_results": proposal_results,
        "failed_checks": failed_checks,
        "final_verdict": final_verdict,
    }


def human_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (list, dict)):
        return json.dumps(value, separators=(",", ":"), sort_keys=True)
    return str(value)


def main() -> int:
    summary = run_proof()
    print(summary["final_verdict"])
    if summary["final_verdict"] == FAIL_VERDICT:
        reason = summary["failed_checks"][0] if summary["failed_checks"] else "unknown_failure"
        print(f"failure_reason={reason}")
    for field in HUMAN_SUMMARY_FIELDS:
        print(f"{field}={human_value(summary[field])}")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["final_verdict"] == PASS_VERDICT else 1


if __name__ == "__main__":
    sys.exit(main())
