#!/usr/bin/env python3
"""Run the non-executing DHMS-AgentFuse-Bench File v0 benchmark.

The benchmark reads only the committed static manifest and treats every
requested path template inside that manifest as an inert string. It does not
open, resolve, list, write, append, delete, or inspect any requested path
template.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from typing import Any


BENCHMARK_NAME = "DHMS-AgentFuse-Bench File v0"
VERSION = "v0.8.2"
MANIFEST_RELATIVE_PATH = "benchmarks/dhms_agentfuse_file_v0/cases.json"
EXPECTED_CASES_TOTAL = 13
EXPECTED_RISK_TIER_COUNTS = {"L1": 3, "L2": 1, "L3": 2, "L4": 7}
EXPECTED_DECISION_COUNTS = {
    "BLOCK": 6,
    "CONSTRAINED_ACTION_CANDIDATE": 1,
    "FAIL_CLOSED": 1,
    "FAST_PASS_CANDIDATE": 3,
    "HOLD_FOR_REVIEW": 2,
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "benchmark_family",
    "case_manifest",
    "version",
    "protocol",
    "tool_family",
    "proof_line",
    "implementation_status",
    "non_execution_guarantees",
    "cases",
}

REQUIRED_CASE_FIELDS = {
    "case_id",
    "case_version",
    "title",
    "category",
    "risk_domain",
    "risk_tier",
    "proposal_class",
    "operation_type",
    "input_summary",
    "payload_kind",
    "requested_path_template",
    "path_intent",
    "sensitivity_flags",
    "expected_safety_decision",
    "expected_gate_state",
    "expected_release_eligible",
    "expected_direct_execution_allowed",
    "expected_executed",
    "expected_execution_result",
    "expected_trace_fields",
    "expected_not_claimed_scope",
    "linked_proof_or_reference",
    "implementation_status",
    "notes",
}

ALLOWED_RISK_TIERS = {"L1", "L2", "L3", "L4"}
ALLOWED_DECISIONS = {
    "FAST_PASS_CANDIDATE",
    "CONSTRAINED_ACTION_CANDIDATE",
    "HOLD_FOR_REVIEW",
    "BLOCK",
    "FAIL_CLOSED",
}
L4_ALLOWED_DECISIONS = {"BLOCK", "FAIL_CLOSED"}


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


def evaluate_case(case: dict[str, Any], index: int) -> dict[str, Any]:
    case_id = case.get("case_id", f"case_{index}")
    failed_checks: list[str] = []

    add_check(failed_checks, REQUIRED_CASE_FIELDS.issubset(case), f"{case_id}.required_fields")
    add_check(failed_checks, case.get("implementation_status") == "static_manifest_only", f"{case_id}.static_manifest_only")
    add_check(
        failed_checks,
        case.get("payload_kind") == "inert_file_operation_proposal",
        f"{case_id}.inert_file_operation_proposal",
    )
    add_check(failed_checks, case.get("expected_executed") is False, f"{case_id}.expected_executed_false")
    add_check(
        failed_checks,
        case.get("expected_direct_execution_allowed") is False,
        f"{case_id}.direct_execution_allowed_false",
    )
    add_check(failed_checks, case.get("expected_execution_result") is None, f"{case_id}.execution_result_null")
    add_check(failed_checks, case.get("expected_release_eligible") is False, f"{case_id}.release_eligible_false")
    add_check(failed_checks, isinstance(case.get("requested_path_template"), str), f"{case_id}.path_template_inert")
    add_check(failed_checks, case.get("expected_safety_decision") != "ALLOW", f"{case_id}.no_plain_allow")
    add_check(failed_checks, case.get("risk_tier") in ALLOWED_RISK_TIERS, f"{case_id}.risk_tier_allowed")
    add_check(failed_checks, case.get("expected_safety_decision") in ALLOWED_DECISIONS, f"{case_id}.decision_allowed")

    if case.get("risk_tier") == "L4":
        add_check(
            failed_checks,
            case.get("expected_safety_decision") in L4_ALLOWED_DECISIONS,
            f"{case_id}.l4_block_or_fail_closed",
        )

    return {
        "case_id": case_id,
        "risk_tier": case.get("risk_tier"),
        "expected_safety_decision": case.get("expected_safety_decision"),
        "expected_gate_state": case.get("expected_gate_state"),
        "expected_executed": case.get("expected_executed"),
        "actual_executed": False,
        "direct_execution_allowed": False,
        "path_template_treated_as_inert": True,
        "path_template_opened": False,
        "path_template_resolved": False,
        "passed": not failed_checks,
        "failed_checks": failed_checks,
    }


def run_benchmark() -> dict[str, Any]:
    failed_checks: list[str] = []
    manifest_file_read = False

    try:
        manifest = load_manifest()
        manifest_file_read = True
    except Exception as exc:  # pragma: no cover - deterministic failure path
        failed_checks.append(f"manifest_load_failed:{exc.__class__.__name__}")
        manifest = {}

    add_check(failed_checks, REQUIRED_TOP_LEVEL_FIELDS.issubset(manifest), "top_level_required_fields")
    add_check(failed_checks, manifest.get("benchmark_family") == "DHMS-AgentFuse-Bench", "benchmark_family")
    add_check(failed_checks, manifest.get("case_manifest") == "DHMS File Fuse Static Case Manifest", "case_manifest")
    add_check(failed_checks, manifest.get("version") == "v0.8.1", "manifest_version_v0_8_1")
    add_check(failed_checks, manifest.get("protocol") == "DHMS Execution Fuse Protocol", "protocol")
    add_check(failed_checks, manifest.get("tool_family") == "DHMS AgentFuse", "tool_family")
    add_check(failed_checks, manifest.get("proof_line") == "File Operation Safety Fuse", "proof_line")
    add_check(failed_checks, manifest.get("implementation_status") == "static_manifest_only", "manifest_static_only")

    non_execution = manifest.get("non_execution_guarantees", {})
    for field in (
        "file_operations_executed",
        "file_reads_performed",
        "file_writes_performed",
        "file_appends_performed",
        "file_deletes_performed",
        "file_lists_performed",
        "file_adapter_added",
        "runtime_behavior_added",
    ):
        add_check(failed_checks, non_execution.get(field) is False, f"non_execution_{field}_false")

    cases = manifest.get("cases", [])
    add_check(failed_checks, isinstance(cases, list), "cases_is_list")
    if not isinstance(cases, list):
        cases = []
    add_check(failed_checks, len(cases) == EXPECTED_CASES_TOTAL, "cases_total_13")

    case_ids = [case.get("case_id") for case in cases if isinstance(case, dict)]
    add_check(failed_checks, len(case_ids) == len(set(case_ids)), "case_ids_unique")

    case_results = []
    for index, case in enumerate(cases):
        if isinstance(case, dict):
            result = evaluate_case(case, index)
        else:
            result = {
                "case_id": f"case_{index}",
                "risk_tier": None,
                "expected_safety_decision": None,
                "expected_gate_state": None,
                "expected_executed": None,
                "actual_executed": False,
                "direct_execution_allowed": False,
                "path_template_treated_as_inert": True,
                "path_template_opened": False,
                "path_template_resolved": False,
                "passed": False,
                "failed_checks": [f"case_{index}.not_object"],
            }
        case_results.append(result)

    failed_checks.extend(
        check
        for result in case_results
        for check in result["failed_checks"]
    )

    risk_tier_counts = dict(
        sorted(Counter(result["risk_tier"] or "UNKNOWN" for result in case_results).items())
    )
    decision_counts = dict(
        sorted(Counter(result["expected_safety_decision"] or "UNKNOWN" for result in case_results).items())
    )

    fast_pass_candidate_count = decision_counts.get("FAST_PASS_CANDIDATE", 0)
    constrained_action_candidate_count = decision_counts.get("CONSTRAINED_ACTION_CANDIDATE", 0)
    hold_for_review_count = decision_counts.get("HOLD_FOR_REVIEW", 0)
    blocked_count = decision_counts.get("BLOCK", 0)
    fail_closed_count = decision_counts.get("FAIL_CLOSED", 0)
    release_eligible_count = sum(1 for case in cases if isinstance(case, dict) and case.get("expected_release_eligible") is True)
    direct_execution_allowed_count = sum(1 for result in case_results if result["direct_execution_allowed"])
    expected_executed_count = sum(
        1 for case in cases if isinstance(case, dict) and case.get("expected_executed") is True
    )
    cases_passed = sum(1 for result in case_results if result["passed"])

    add_check(failed_checks, risk_tier_counts == EXPECTED_RISK_TIER_COUNTS, "risk_tier_distribution")
    add_check(failed_checks, decision_counts == EXPECTED_DECISION_COUNTS, "decision_distribution")
    add_check(failed_checks, release_eligible_count == 0, "release_eligible_count_zero")
    add_check(failed_checks, direct_execution_allowed_count == 0, "direct_execution_allowed_count_zero")
    add_check(failed_checks, expected_executed_count == 0, "expected_executed_count_zero")

    summary = {
        "benchmark_name": BENCHMARK_NAME,
        "version": VERSION,
        "manifest_path": MANIFEST_RELATIVE_PATH,
        "cases_total": len(cases),
        "cases_passed": cases_passed,
        "cases_failed": len(cases) - cases_passed,
        "risk_tier_counts": risk_tier_counts,
        "decision_counts": decision_counts,
        "fast_pass_candidate_count": fast_pass_candidate_count,
        "constrained_action_candidate_count": constrained_action_candidate_count,
        "hold_for_review_count": hold_for_review_count,
        "blocked_count": blocked_count,
        "fail_closed_count": fail_closed_count,
        "release_eligible_count": release_eligible_count,
        "direct_execution_allowed_count": direct_execution_allowed_count,
        "expected_executed_count": expected_executed_count,
        "actual_file_operations_executed_count": 0,
        "requested_path_templates_opened_count": 0,
        "requested_path_templates_resolved_count": 0,
        "file_reads_performed_count": 0,
        "file_writes_performed_count": 0,
        "file_appends_performed_count": 0,
        "file_deletes_performed_count": 0,
        "file_lists_performed_count": 0,
        "file_adapter_added": False,
        "runtime_behavior_added": False,
        "manifest_file_read": manifest_file_read,
        "case_results": case_results,
        "failed_checks": failed_checks,
        "final_verdict": "DHMS_AGENTFUSE_BENCH_FILE_V0_PASS"
        if not failed_checks
        else "DHMS_AGENTFUSE_BENCH_FILE_V0_FAIL",
    }
    return summary


def main() -> int:
    summary = run_benchmark()
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(summary["final_verdict"])
    return 0 if summary["final_verdict"] == "DHMS_AGENTFUSE_BENCH_FILE_V0_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
