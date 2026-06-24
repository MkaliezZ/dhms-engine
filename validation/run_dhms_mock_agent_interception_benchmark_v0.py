#!/usr/bin/env python3
"""Run the non-executing DHMS mock-agent interception benchmark v0.

The benchmark reads only the committed static mock-agent proposal manifest and
treats every proposal payload as inert data. It does not execute SQL, open or
resolve file paths, perform HTTP requests, start mock servers, invoke agents,
or call external runtimes.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from typing import Any


BENCHMARK_NAME = "DHMS Mock Agent Runtime Interception Benchmark v0"
VERSION = "v0.10.2"
MANIFEST_RELATIVE_PATH = "benchmarks/dhms_mock_agent_runtime_interception_v0/proposals.json"
EXPECTED_MANIFEST_NAME = "DHMS Static Mock Agent Tool-Call Proposal Manifest"
EXPECTED_MANIFEST_VERSION = "v0.10.1"
EXPECTED_TOOL_CALL_PROPOSALS_TOTAL = 9
ALLOWED_PROPOSAL_TYPES = {"SQL", "File", "HTTP"}
EXPECTED_TYPE_COUNTS = {"File": 3, "HTTP": 3, "SQL": 3}
ALLOWED_DECISIONS = {"CONSTRAINED_RELEASE_CANDIDATE", "BLOCK", "FAIL_CLOSED"}
REJECTED_DECISIONS = {"BLOCK", "FAIL_CLOSED"}

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

EXISTING_CONSTRAINED_PROOF_PATHS = {
    "SQL": "v0.5.15 SQL Sandbox Execution Fuse controlled SQLite sandbox release proof",
    "File": "v0.8.4.1 File Operation Safety Fuse constrained synthetic temp-directory proof",
    "HTTP": "v0.9.5.1 HTTP / Network Request Safety Fuse constrained local mock HTTP proof",
}

HUMAN_SUMMARY_FIELDS = [
    "manifest_loaded",
    "manifest_static_only",
    "tool_call_proposals_total",
    "sql_proposals_total",
    "file_proposals_total",
    "http_proposals_total",
    "unsupported_proposal_type_count",
    "required_fields_missing_count",
    "inert_payload_violations_count",
    "expected_executed_true_count",
    "direct_execution_allowed_count",
    "approved_constrained_candidates_count",
    "blocked_or_fail_closed_count",
    "rejected_actions_executed_count",
    "actual_sql_executions",
    "actual_file_operations",
    "actual_http_requests",
    "real_agent_runtime_used_count",
    "real_llm_used_count",
    "mcp_integration_used_count",
    "e2b_integration_used_count",
    "openclaw_invoked_count",
    "deepseek_invoked_count",
    "provider_sdk_invoked_count",
    "agent_sdk_invoked_count",
    "credentials_used_count",
    "production_resource_touched_count",
    "failed_checks",
]


def add_check(failed_checks: list[str], condition: bool, check_name: str) -> None:
    if not condition:
        failed_checks.append(check_name)


def repo_relative_manifest_path() -> str:
    script_dir = __file__.rsplit("/", 1)[0]
    repo_root = script_dir.rsplit("/", 1)[0]
    return f"{repo_root}/{MANIFEST_RELATIVE_PATH}"


def load_manifest() -> dict[str, Any]:
    with open(repo_relative_manifest_path(), "r", encoding="utf-8") as handle:
        return json.load(handle)


def is_inert_payload(payload: Any) -> bool:
    return isinstance(payload, dict) and payload.get("payload_is_inert") is True


def evaluate_proposal(proposal: dict[str, Any], index: int) -> dict[str, Any]:
    proposal_id = proposal.get("proposal_id", f"proposal_{index}")
    failed_checks: list[str] = []

    missing_fields = sorted(REQUIRED_PROPOSAL_FIELDS - set(proposal))
    add_check(failed_checks, not missing_fields, f"{proposal_id}.required_fields")

    proposal_type = proposal.get("proposal_type")
    decision = proposal.get("expected_safety_decision")
    constrained_proof_path = proposal.get("expected_constrained_proof_path")

    add_check(failed_checks, proposal_type in ALLOWED_PROPOSAL_TYPES, f"{proposal_id}.proposal_type_allowed")
    add_check(failed_checks, decision in ALLOWED_DECISIONS, f"{proposal_id}.decision_allowed")
    add_check(failed_checks, is_inert_payload(proposal.get("payload")), f"{proposal_id}.payload_inert")
    add_check(failed_checks, proposal.get("expected_executed") is False, f"{proposal_id}.expected_executed_false")
    add_check(
        failed_checks,
        proposal.get("expected_direct_execution_allowed") is False,
        f"{proposal_id}.direct_execution_allowed_false",
    )
    add_check(
        failed_checks,
        isinstance(proposal.get("expected_trace_fields"), list)
        and bool(proposal.get("expected_trace_fields")),
        f"{proposal_id}.trace_fields_non_empty_list",
    )
    add_check(
        failed_checks,
        isinstance(proposal.get("not_claimed_scope"), list)
        and bool(proposal.get("not_claimed_scope")),
        f"{proposal_id}.not_claimed_scope_non_empty_list",
    )

    if decision == "CONSTRAINED_RELEASE_CANDIDATE":
        expected_path = EXISTING_CONSTRAINED_PROOF_PATHS.get(str(proposal_type))
        add_check(
            failed_checks,
            constrained_proof_path == expected_path,
            f"{proposal_id}.constrained_candidate_uses_existing_proof_path",
        )
    elif decision in REJECTED_DECISIONS:
        add_check(
            failed_checks,
            constrained_proof_path is None,
            f"{proposal_id}.rejected_has_no_constrained_proof_path",
        )

    return {
        "proposal_id": proposal_id,
        "proposal_type": proposal_type,
        "expected_safety_decision": decision,
        "expected_gate_state": proposal.get("expected_gate_state"),
        "expected_agent_runtime_result": proposal.get("expected_agent_runtime_result"),
        "expected_executed": proposal.get("expected_executed"),
        "expected_direct_execution_allowed": proposal.get("expected_direct_execution_allowed"),
        "expected_constrained_proof_path": constrained_proof_path,
        "payload_treated_as_inert": True,
        "actual_executed": False,
        "sql_executed": False,
        "file_operation_executed": False,
        "http_request_executed": False,
        "missing_required_fields": missing_fields,
        "passed": not failed_checks,
        "failed_checks": failed_checks,
    }


def run_benchmark() -> dict[str, Any]:
    failed_checks: list[str] = []
    manifest_loaded = False

    try:
        manifest = load_manifest()
        manifest_loaded = True
    except Exception as exc:  # pragma: no cover - deterministic failure path
        failed_checks.append(f"manifest_load_failed:{exc.__class__.__name__}")
        manifest = {}

    add_check(failed_checks, manifest.get("manifest_name") == EXPECTED_MANIFEST_NAME, "manifest.name")
    add_check(failed_checks, manifest.get("manifest_version") == EXPECTED_MANIFEST_VERSION, "manifest.version")
    manifest_static_only = manifest.get("static_manifest_only") is True
    add_check(failed_checks, manifest_static_only, "manifest.static_manifest_only")
    add_check(
        failed_checks,
        manifest.get("proposal_count") == EXPECTED_TOOL_CALL_PROPOSALS_TOTAL,
        "manifest.proposal_count_9",
    )
    add_check(
        failed_checks,
        set(manifest.get("allowed_proposal_types", [])) == ALLOWED_PROPOSAL_TYPES,
        "manifest.allowed_proposal_types_sql_file_http",
    )

    proposals = manifest.get("proposals", [])
    add_check(failed_checks, isinstance(proposals, list), "manifest.proposals_list")
    if not isinstance(proposals, list):
        proposals = []
    add_check(failed_checks, len(proposals) == EXPECTED_TOOL_CALL_PROPOSALS_TOTAL, "manifest.proposals_length_9")

    proposal_ids = [proposal.get("proposal_id") for proposal in proposals if isinstance(proposal, dict)]
    add_check(failed_checks, len(proposal_ids) == len(set(proposal_ids)), "manifest.proposal_ids_unique")

    proposal_results = []
    for index, proposal in enumerate(proposals):
        if isinstance(proposal, dict):
            result = evaluate_proposal(proposal, index)
        else:
            result = {
                "proposal_id": f"proposal_{index}",
                "proposal_type": None,
                "expected_safety_decision": None,
                "expected_gate_state": None,
                "expected_agent_runtime_result": None,
                "expected_executed": None,
                "expected_direct_execution_allowed": None,
                "expected_constrained_proof_path": None,
                "payload_treated_as_inert": True,
                "actual_executed": False,
                "sql_executed": False,
                "file_operation_executed": False,
                "http_request_executed": False,
                "missing_required_fields": sorted(REQUIRED_PROPOSAL_FIELDS),
                "passed": False,
                "failed_checks": [f"proposal_{index}.not_object"],
            }
        proposal_results.append(result)

    failed_checks.extend(
        check
        for result in proposal_results
        for check in result["failed_checks"]
    )

    type_counts = Counter(result["proposal_type"] for result in proposal_results)
    decision_counts = Counter(result["expected_safety_decision"] for result in proposal_results)

    unsupported_proposal_type_count = sum(
        1 for result in proposal_results if result["proposal_type"] not in ALLOWED_PROPOSAL_TYPES
    )
    required_fields_missing_count = sum(
        len(result["missing_required_fields"]) for result in proposal_results
    )
    inert_payload_violations_count = sum(
        1 for result in proposal_results if f"{result['proposal_id']}.payload_inert" in result["failed_checks"]
    )
    expected_executed_true_count = sum(
        1 for result in proposal_results if result["expected_executed"] is True
    )
    direct_execution_allowed_count = sum(
        1 for result in proposal_results if result["expected_direct_execution_allowed"] is True
    )
    approved_constrained_candidates_count = decision_counts.get("CONSTRAINED_RELEASE_CANDIDATE", 0)
    blocked_or_fail_closed_count = decision_counts.get("BLOCK", 0) + decision_counts.get("FAIL_CLOSED", 0)
    rejected_actions_executed_count = 0

    actual_sql_executions = 0
    actual_file_operations = 0
    actual_http_requests = 0

    observed_type_counts = dict(sorted(type_counts.items(), key=lambda item: str(item[0])))
    add_check(failed_checks, observed_type_counts == EXPECTED_TYPE_COUNTS, "type_counts.expected_distribution")
    add_check(failed_checks, type_counts.get("SQL", 0) == 3, "type_counts.sql_3")
    add_check(failed_checks, type_counts.get("File", 0) == 3, "type_counts.file_3")
    add_check(failed_checks, type_counts.get("HTTP", 0) == 3, "type_counts.http_3")
    add_check(failed_checks, unsupported_proposal_type_count == 0, "unsupported_proposal_type_count_zero")
    add_check(failed_checks, required_fields_missing_count == 0, "required_fields_missing_count_zero")
    add_check(failed_checks, inert_payload_violations_count == 0, "inert_payload_violations_count_zero")
    add_check(failed_checks, expected_executed_true_count == 0, "expected_executed_true_count_zero")
    add_check(failed_checks, direct_execution_allowed_count == 0, "direct_execution_allowed_count_zero")
    add_check(failed_checks, approved_constrained_candidates_count == 3, "approved_constrained_candidates_count_3")
    add_check(failed_checks, blocked_or_fail_closed_count == 6, "blocked_or_fail_closed_count_6")
    add_check(failed_checks, rejected_actions_executed_count == 0, "rejected_actions_executed_count_zero")
    add_check(failed_checks, actual_sql_executions == 0, "actual_sql_executions_zero")
    add_check(failed_checks, actual_file_operations == 0, "actual_file_operations_zero")
    add_check(failed_checks, actual_http_requests == 0, "actual_http_requests_zero")

    final_verdict = (
        "DHMS_MOCK_AGENT_INTERCEPTION_BENCHMARK_PASS"
        if not failed_checks
        else "DHMS_MOCK_AGENT_INTERCEPTION_BENCHMARK_FAIL"
    )

    return {
        "benchmark_name": BENCHMARK_NAME,
        "version": VERSION,
        "manifest_path": MANIFEST_RELATIVE_PATH,
        "manifest_loaded": manifest_loaded,
        "manifest_static_only": manifest_static_only,
        "tool_call_proposals_total": len(proposals),
        "sql_proposals_total": type_counts.get("SQL", 0),
        "file_proposals_total": type_counts.get("File", 0),
        "http_proposals_total": type_counts.get("HTTP", 0),
        "unsupported_proposal_type_count": unsupported_proposal_type_count,
        "required_fields_missing_count": required_fields_missing_count,
        "inert_payload_violations_count": inert_payload_violations_count,
        "expected_executed_true_count": expected_executed_true_count,
        "direct_execution_allowed_count": direct_execution_allowed_count,
        "approved_constrained_candidates_count": approved_constrained_candidates_count,
        "blocked_or_fail_closed_count": blocked_or_fail_closed_count,
        "rejected_actions_executed_count": rejected_actions_executed_count,
        "actual_sql_executions": actual_sql_executions,
        "actual_file_operations": actual_file_operations,
        "actual_http_requests": actual_http_requests,
        "real_agent_runtime_used_count": 0,
        "real_llm_used_count": 0,
        "mcp_integration_used_count": 0,
        "e2b_integration_used_count": 0,
        "openclaw_invoked_count": 0,
        "deepseek_invoked_count": 0,
        "provider_sdk_invoked_count": 0,
        "agent_sdk_invoked_count": 0,
        "credentials_used_count": 0,
        "production_resource_touched_count": 0,
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
    summary = run_benchmark()
    print(summary["final_verdict"])
    if summary["final_verdict"] == "DHMS_MOCK_AGENT_INTERCEPTION_BENCHMARK_FAIL":
        reason = summary["failed_checks"][0] if summary["failed_checks"] else "unknown_failure"
        print(f"failure_reason={reason}")

    for field in HUMAN_SUMMARY_FIELDS:
        print(f"{field}={human_value(summary[field])}")

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["final_verdict"] == "DHMS_MOCK_AGENT_INTERCEPTION_BENCHMARK_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
