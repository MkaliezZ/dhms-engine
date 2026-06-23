#!/usr/bin/env python3
"""Validate the DHMS File Fuse static case manifest without file operations."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


MANIFEST_RELATIVE_PATH = "benchmarks/dhms_agentfuse_file_v0/cases.json"

REQUIRED_TOP_LEVEL_FIELDS = {
    "benchmark_family",
    "case_manifest",
    "version",
    "protocol",
    "tool_family",
    "proof_line",
    "implementation_status",
    "non_execution_guarantees",
    "cases"
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
    "notes"
}

REQUIRED_TRACE_FIELDS = {
    "proposal_id",
    "operation_type",
    "requested_path_template",
    "path_intent",
    "risk_tier",
    "sensitivity_flags",
    "expected_safety_decision",
    "expected_gate_state",
    "expected_executed",
    "expected_execution_result",
    "not_claimed_scope"
}

REQUIRED_NOT_CLAIMED_SCOPE = {
    "not_direct_file_read_support",
    "not_direct_file_write_support",
    "not_file_adapter",
    "not_file_policy_implementation",
    "not_production_filesystem_safety"
}

ALLOWED_OPERATION_TYPES = {
    "file_read_proposal",
    "file_write_proposal",
    "file_append_proposal",
    "file_delete_proposal",
    "file_list_proposal",
    "file_metadata_proposal",
    "unsupported_file_operation_proposal"
}

ALLOWED_RISK_TIERS = {"L1", "L2", "L3", "L4"}
ALLOWED_DECISIONS = {
    "FAST_PASS_CANDIDATE",
    "CONSTRAINED_ACTION_CANDIDATE",
    "HOLD_FOR_REVIEW",
    "BLOCK",
    "FAIL_CLOSED"
}
ALLOWED_GATE_STATES = {
    "OBSERVED_OR_FAST_PASS_CANDIDATE",
    "HELD_FOR_CONSTRAINT_CHECK",
    "HELD_FOR_REVIEW",
    "CLOSED",
    "FAIL_CLOSED"
}


def add_check(failed_checks: list[str], condition: bool, name: str) -> None:
    if not condition:
        failed_checks.append(name)


def main() -> int:
    repo_root = Path(__file__).parent.parent
    manifest_path = repo_root / MANIFEST_RELATIVE_PATH

    failed_checks: list[str] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - deterministic failure path
        summary = {
            "smoke_name": "DHMS File Fuse Static Case Manifest Smoke",
            "version": "v0.8.1",
            "cases_total": 0,
            "cases_passed": 0,
            "expected_executed_count": 0,
            "direct_execution_allowed_count": 0,
            "file_operation_capability_added": False,
            "file_paths_opened_count": 0,
            "file_paths_resolved_count": 0,
            "failed_checks": [f"manifest_load_failed:{exc.__class__.__name__}"],
            "final_verdict": "DHMS_FILE_FUSE_STATIC_CASE_MANIFEST_FAIL"
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 1

    add_check(failed_checks, REQUIRED_TOP_LEVEL_FIELDS.issubset(manifest), "top_level_required_fields")
    add_check(failed_checks, manifest.get("version") == "v0.8.1", "version_v0_8_1")
    add_check(failed_checks, manifest.get("proof_line") == "File Operation Safety Fuse", "proof_line_file_operation_safety_fuse")
    add_check(failed_checks, manifest.get("implementation_status") == "static_manifest_only", "implementation_status_static_manifest_only")

    non_execution = manifest.get("non_execution_guarantees", {})
    for field in (
        "file_operations_executed",
        "file_reads_performed",
        "file_writes_performed",
        "file_appends_performed",
        "file_deletes_performed",
        "file_lists_performed",
        "file_adapter_added",
        "runtime_behavior_added"
    ):
        add_check(failed_checks, non_execution.get(field) is False, f"non_execution_guarantee_{field}_false")

    cases = manifest.get("cases", [])
    add_check(failed_checks, isinstance(cases, list), "cases_is_list")
    add_check(failed_checks, len(cases) == 13, "cases_total_13")

    case_ids = [case.get("case_id") for case in cases if isinstance(case, dict)]
    add_check(failed_checks, len(case_ids) == len(set(case_ids)), "case_ids_unique")

    expected_executed_count = 0
    direct_execution_allowed_count = 0
    file_operation_capability_added = False
    cases_passed = 0
    risk_tier_counts: Counter[str] = Counter()
    decision_counts: Counter[str] = Counter()

    for index, case in enumerate(cases):
        case_failed_before = len(failed_checks)
        prefix = case.get("case_id", f"case_{index}") if isinstance(case, dict) else f"case_{index}"
        add_check(failed_checks, isinstance(case, dict), f"{prefix}.is_object")
        if not isinstance(case, dict):
            continue

        add_check(failed_checks, REQUIRED_CASE_FIELDS.issubset(case), f"{prefix}.required_fields")
        add_check(failed_checks, case.get("category") == "file_fuse_static_case", f"{prefix}.category")
        add_check(failed_checks, case.get("risk_domain") == "file_operation_boundary", f"{prefix}.risk_domain")
        add_check(failed_checks, case.get("payload_kind") == "inert_file_operation_proposal", f"{prefix}.payload_kind")
        add_check(failed_checks, case.get("implementation_status") == "static_manifest_only", f"{prefix}.implementation_status")
        add_check(failed_checks, case.get("operation_type") in ALLOWED_OPERATION_TYPES, f"{prefix}.operation_type_allowed")
        add_check(failed_checks, case.get("risk_tier") in ALLOWED_RISK_TIERS, f"{prefix}.risk_tier_allowed")
        add_check(failed_checks, case.get("expected_safety_decision") in ALLOWED_DECISIONS, f"{prefix}.decision_allowed")
        add_check(failed_checks, case.get("expected_safety_decision") != "ALLOW", f"{prefix}.decision_not_plain_allow")
        add_check(failed_checks, case.get("expected_gate_state") in ALLOWED_GATE_STATES, f"{prefix}.gate_state_allowed")
        add_check(failed_checks, case.get("expected_release_eligible") is False, f"{prefix}.release_eligible_false")
        add_check(failed_checks, case.get("expected_direct_execution_allowed") is False, f"{prefix}.direct_execution_allowed_false")
        add_check(failed_checks, case.get("expected_executed") is False, f"{prefix}.expected_executed_false")
        add_check(failed_checks, case.get("expected_execution_result") is None, f"{prefix}.expected_execution_result_null")
        add_check(failed_checks, isinstance(case.get("requested_path_template"), str), f"{prefix}.requested_path_template_inert_string")
        add_check(failed_checks, isinstance(case.get("sensitivity_flags"), list), f"{prefix}.sensitivity_flags_list")
        add_check(failed_checks, REQUIRED_TRACE_FIELDS.issubset(set(case.get("expected_trace_fields", []))), f"{prefix}.trace_fields")
        add_check(failed_checks, REQUIRED_NOT_CLAIMED_SCOPE.issubset(set(case.get("expected_not_claimed_scope", []))), f"{prefix}.not_claimed_scope")

        if case.get("risk_tier") == "L4":
            add_check(
                failed_checks,
                case.get("expected_safety_decision") in {"BLOCK", "FAIL_CLOSED"},
                f"{prefix}.l4_block_or_fail_closed"
            )

        if case.get("expected_executed") is True:
            expected_executed_count += 1
            file_operation_capability_added = True
        if case.get("expected_direct_execution_allowed") is True:
            direct_execution_allowed_count += 1
            file_operation_capability_added = True
        if case.get("implementation_status") != "static_manifest_only":
            file_operation_capability_added = True

        risk_tier_counts[case.get("risk_tier", "UNKNOWN")] += 1
        decision_counts[case.get("expected_safety_decision", "UNKNOWN")] += 1
        if len(failed_checks) == case_failed_before:
            cases_passed += 1

    add_check(failed_checks, expected_executed_count == 0, "expected_executed_count_zero")
    add_check(failed_checks, direct_execution_allowed_count == 0, "direct_execution_allowed_count_zero")
    add_check(failed_checks, not file_operation_capability_added, "file_operation_capability_not_added")
    add_check(failed_checks, risk_tier_counts == Counter({"L1": 3, "L2": 1, "L3": 2, "L4": 7}), "risk_tier_distribution")

    summary = {
        "smoke_name": "DHMS File Fuse Static Case Manifest Smoke",
        "version": "v0.8.1",
        "manifest_path": MANIFEST_RELATIVE_PATH,
        "manifest_file_read": True,
        "cases_total": len(cases),
        "cases_passed": cases_passed if not failed_checks else cases_passed,
        "risk_tier_counts": dict(sorted(risk_tier_counts.items())),
        "decision_counts": dict(sorted(decision_counts.items())),
        "expected_executed_count": expected_executed_count,
        "direct_execution_allowed_count": direct_execution_allowed_count,
        "file_operation_capability_added": file_operation_capability_added,
        "file_paths_opened_count": 0,
        "file_paths_resolved_count": 0,
        "sqlite_database_created": False,
        "sandbox_files_created": False,
        "openclaw_invoked": False,
        "deepseek_invoked": False,
        "provider_sdk_invoked": False,
        "agent_sdk_invoked": False,
        "http_network_invoked": False,
        "shell_commands_invoked": False,
        "mcp_invoked": False,
        "failed_checks": failed_checks,
        "final_verdict": "DHMS_FILE_FUSE_STATIC_CASE_MANIFEST_PASS" if not failed_checks else "DHMS_FILE_FUSE_STATIC_CASE_MANIFEST_FAIL"
    }

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    sys.exit(main())
