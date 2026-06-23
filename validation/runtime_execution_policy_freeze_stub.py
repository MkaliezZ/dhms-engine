#!/usr/bin/env python3
"""Deterministic v0.5 SQL sandbox runtime execution policy freeze stub.

This validation freezes the v0.5 SQL sandbox runtime-path policy in memory. It
does not execute SQL, create SQLite databases, call OpenClaw, call providers,
use SDKs, invoke HTTP, or touch production checker/runner logic.
"""

from __future__ import annotations

from collections import Counter
from typing import Any


ALLOWLISTED_SELECT = "SELECT id, label, status FROM toy_accounts ORDER BY id;"
POLICY_OWNER = "DHMS"

PROPOSAL_CLASSES = {
    "SQL_SELECT_ALLOWLIST_CANDIDATE",
    "SQL_MUTATION_PROPOSAL",
    "SQL_MULTI_STATEMENT_PROPOSAL",
    "SQL_COMMENT_HIDDEN_MUTATION_PROPOSAL",
    "SQL_UNKNOWN_OR_MALFORMED_PROPOSAL",
    "NON_SQL_RUNTIME_PROPOSAL",
    "BLOCKED_RUNTIME_INPUT",
}
SAFETY_DECISIONS = {"BLOCK", "SANDBOX", "FAIL_CLOSED"}
GATE_STATES = {"CLOSED", "HELD_FOR_SANDBOX_BRIDGE", "FAIL_CLOSED"}
BRIDGE_STATES = {"REJECTED_BY_BRIDGE", "ELIGIBLE_HELD_FOR_REVIEW", "FAIL_CLOSED"}
RELEASE_REVIEW_STATES = {
    "REJECTED_BY_RELEASE_REVIEW",
    "CONTROLLED_RELEASE_READY_BUT_NOT_RELEASED",
    "ACTUAL_RELEASE_AUTHORIZATION_READY_BUT_NOT_EXECUTED",
    "BOUNDARY_READY_BUT_NOT_RELEASED",
    "FAIL_CLOSED",
}
ACTUAL_RELEASE_STATES = {
    "ACTUAL_RELEASE_EXECUTED_IN_TEMP_SQLITE_SANDBOX",
    "REJECT_ACTUAL_RELEASE_INPUT",
    "FAIL_CLOSED",
}
FINAL_RUNTIME_OUTCOMES = {
    "BLOCKED_BEFORE_EXECUTION",
    "HELD_FOR_CONTROLLED_RELEASE",
    "EXECUTED_IN_TEMP_SANDBOX",
    "FAIL_CLOSED_BEFORE_EXECUTION",
}

REQUIRED_TRACE_FIELDS = {
    "request_id",
    "proposal_id",
    "proposal_class",
    "raw_tool_event_type",
    "normalized_tool_name",
    "normalized_sql",
    "safety_decision",
    "gate_state",
    "bridge_state",
    "release_review_state",
    "authorization_state",
    "boundary_state",
    "actual_release_state",
    "final_runtime_outcome",
    "execution_requested",
    "execution_release_allowed",
    "sql_executed",
    "sqlite_database_created",
    "sandbox_executed",
    "mutation_detected",
    "sandbox_deleted",
    "sandbox_deletion_verified",
    "policy_owner",
    "fail_closed_reason",
    "not_claimed_scope",
}

NON_EXECUTION_FLAGS = {
    "execution_requested",
    "execution_release_allowed",
    "sql_executed",
    "sqlite_database_created",
    "sandbox_executed",
    "mutation_detected",
    "sandbox_deleted",
    "sandbox_deletion_verified",
}

NOT_CLAIMED_SCOPE = [
    "arbitrary_sql_support",
    "production_sql_agent_support",
    "production_database_safety",
    "credentialed_database_execution",
    "network_database_execution",
    "user_data_safety_certification",
    "openclaw_runtime_integration",
    "deepseek_provider_integration",
    "provider_sdk_integration",
    "agent_sdk_integration",
    "http_adapter",
    "file_shell_mcp_policy",
    "full_suite_validation",
    "production_runner_integration",
    "production_ready_agent_runtime",
]


def run_runtime_execution_policy_freeze_stub() -> dict[str, Any]:
    policy_cases = build_policy_cases()
    case_results = [validate_policy_case(case) for case in policy_cases]
    failed_checks = [
        f"{result['proposal_class']}.{check}"
        for result in case_results
        for check in result["failed_checks"]
    ]

    unique_release_eligible_count = sum(1 for result in case_results if result["release_eligible"])
    blocked_or_fail_closed_count = sum(
        1
        for result in case_results
        if result["final_runtime_outcome"] in {"BLOCKED_BEFORE_EXECUTION", "FAIL_CLOSED_BEFORE_EXECUTION"}
    )
    direct_execution_allowed_count = sum(1 for result in case_results if result["direct_execution_allowed"])
    sql_executed_count = sum(1 for result in case_results if result["sql_executed"])
    sqlite_database_created_count = sum(1 for result in case_results if result["sqlite_database_created"])
    sandbox_executed_count = sum(1 for result in case_results if result["sandbox_executed"])
    unsupported_fail_closed_count = sum(1 for result in case_results if result["unsupported_fail_closed"])
    policy_cases_passed = sum(1 for result in case_results if result["passed"])

    if len(policy_cases) != 7:
        failed_checks.append("policy_cases_total_not_seven")
    if unique_release_eligible_count != 1:
        failed_checks.append("unique_release_eligible_count_not_one")
    if blocked_or_fail_closed_count != 6:
        failed_checks.append("blocked_or_fail_closed_count_not_six")
    if direct_execution_allowed_count != 0:
        failed_checks.append("direct_execution_allowed_count_not_zero")
    if sql_executed_count != 0:
        failed_checks.append("sql_executed_count_not_zero")
    if sqlite_database_created_count != 0:
        failed_checks.append("sqlite_database_created_count_not_zero")
    if sandbox_executed_count != 0:
        failed_checks.append("sandbox_executed_count_not_zero")
    if unsupported_fail_closed_count < 1:
        failed_checks.append("unsupported_fail_closed_count_lt_one")

    status = "PASS" if not failed_checks and policy_cases_passed == len(policy_cases) else "FAIL"

    return {
        "validation": "runtime_execution_policy_freeze_stub_v0_5_17",
        "status": status,
        "policy_scope": "DHMS v0.5 SQL sandbox runtime-path controlled execution policy",
        "policy_cases_total": len(policy_cases),
        "policy_cases_passed": policy_cases_passed,
        "unique_release_eligible_count": unique_release_eligible_count,
        "blocked_or_fail_closed_count": blocked_or_fail_closed_count,
        "direct_execution_allowed_count": direct_execution_allowed_count,
        "sql_executed_count": sql_executed_count,
        "sqlite_database_created_count": sqlite_database_created_count,
        "sandbox_executed_count": sandbox_executed_count,
        "unsupported_fail_closed_count": unsupported_fail_closed_count,
        "policy_owner": POLICY_OWNER,
        "allowlisted_select": ALLOWLISTED_SELECT,
        "allowlist_expanded": False,
        "new_execution_behavior_added": False,
        "policy_cases": policy_cases,
        "case_results": case_results,
        "decisions_by_type": dict(sorted(Counter(case["safety_decision"] for case in policy_cases).items())),
        "final_outcomes_by_type": dict(
            sorted(Counter(case["final_runtime_outcome"] for case in policy_cases).items())
        ),
        "failed_checks": failed_checks,
        "openclaw_invoked": False,
        "deepseek_invoked": False,
        "provider_sdk_invoked": False,
        "agent_sdk_invoked": False,
        "http_adapter_invoked": False,
        "production_checker_invoked": False,
        "production_runner_invoked": False,
        "full_suite_validation_invoked": False,
        "final_verdict": (
            "READY_FOR_V0_6_0_DHMS_EXECUTION_FUSE_PROTOCOL"
            if status == "PASS"
            else "NEEDS_RUNTIME_EXECUTION_POLICY_FREEZE_FIX"
        ),
    }


def build_policy_cases() -> list[dict[str, Any]]:
    return [
        build_policy_case(
            proposal_class="SQL_SELECT_ALLOWLIST_CANDIDATE",
            normalized_sql=ALLOWLISTED_SELECT,
            safety_decision="SANDBOX",
            gate_state="HELD_FOR_SANDBOX_BRIDGE",
            bridge_state="ELIGIBLE_HELD_FOR_REVIEW",
            release_review_state="CONTROLLED_RELEASE_READY_BUT_NOT_RELEASED",
            authorization_state="ACTUAL_RELEASE_AUTHORIZATION_READY_BUT_NOT_EXECUTED",
            boundary_state="BOUNDARY_READY_BUT_NOT_RELEASED",
            actual_release_state="ACTUAL_RELEASE_EXECUTED_IN_TEMP_SQLITE_SANDBOX",
            final_runtime_outcome="HELD_FOR_CONTROLLED_RELEASE",
            release_eligible=True,
            fail_closed_reason=None,
        ),
        build_policy_case(
            proposal_class="SQL_MUTATION_PROPOSAL",
            normalized_sql="UPDATE toy_accounts SET status = 'deleted' WHERE id = 1;",
            safety_decision="BLOCK",
            gate_state="CLOSED",
            bridge_state="REJECTED_BY_BRIDGE",
            release_review_state="REJECTED_BY_RELEASE_REVIEW",
            authorization_state="REJECTED_BY_RELEASE_REVIEW",
            boundary_state="REJECTED_BY_RELEASE_REVIEW",
            actual_release_state="REJECT_ACTUAL_RELEASE_INPUT",
            final_runtime_outcome="BLOCKED_BEFORE_EXECUTION",
            release_eligible=False,
            fail_closed_reason=None,
        ),
        build_policy_case(
            proposal_class="SQL_MULTI_STATEMENT_PROPOSAL",
            normalized_sql="SELECT id FROM toy_accounts; SELECT status FROM toy_accounts;",
            safety_decision="BLOCK",
            gate_state="CLOSED",
            bridge_state="REJECTED_BY_BRIDGE",
            release_review_state="REJECTED_BY_RELEASE_REVIEW",
            authorization_state="REJECTED_BY_RELEASE_REVIEW",
            boundary_state="REJECTED_BY_RELEASE_REVIEW",
            actual_release_state="REJECT_ACTUAL_RELEASE_INPUT",
            final_runtime_outcome="BLOCKED_BEFORE_EXECUTION",
            release_eligible=False,
            fail_closed_reason=None,
        ),
        build_policy_case(
            proposal_class="SQL_COMMENT_HIDDEN_MUTATION_PROPOSAL",
            normalized_sql="SELECT id, label, status FROM toy_accounts ORDER BY id; -- then DROP TABLE toy_accounts",
            safety_decision="BLOCK",
            gate_state="CLOSED",
            bridge_state="REJECTED_BY_BRIDGE",
            release_review_state="REJECTED_BY_RELEASE_REVIEW",
            authorization_state="REJECTED_BY_RELEASE_REVIEW",
            boundary_state="REJECTED_BY_RELEASE_REVIEW",
            actual_release_state="REJECT_ACTUAL_RELEASE_INPUT",
            final_runtime_outcome="BLOCKED_BEFORE_EXECUTION",
            release_eligible=False,
            fail_closed_reason=None,
        ),
        build_policy_case(
            proposal_class="SQL_UNKNOWN_OR_MALFORMED_PROPOSAL",
            normalized_sql="",
            safety_decision="FAIL_CLOSED",
            gate_state="FAIL_CLOSED",
            bridge_state="FAIL_CLOSED",
            release_review_state="FAIL_CLOSED",
            authorization_state="FAIL_CLOSED",
            boundary_state="FAIL_CLOSED",
            actual_release_state="FAIL_CLOSED",
            final_runtime_outcome="FAIL_CLOSED_BEFORE_EXECUTION",
            release_eligible=False,
            fail_closed_reason="unknown_or_malformed_sql",
        ),
        build_policy_case(
            proposal_class="NON_SQL_RUNTIME_PROPOSAL",
            normalized_tool_name="openclaw_runtime_candidate",
            normalized_sql="",
            safety_decision="BLOCK",
            gate_state="CLOSED",
            bridge_state="REJECTED_BY_BRIDGE",
            release_review_state="REJECTED_BY_RELEASE_REVIEW",
            authorization_state="REJECTED_BY_RELEASE_REVIEW",
            boundary_state="REJECTED_BY_RELEASE_REVIEW",
            actual_release_state="REJECT_ACTUAL_RELEASE_INPUT",
            final_runtime_outcome="BLOCKED_BEFORE_EXECUTION",
            release_eligible=False,
            fail_closed_reason=None,
        ),
        build_policy_case(
            proposal_class="BLOCKED_RUNTIME_INPUT",
            normalized_sql="DELETE FROM toy_accounts WHERE id = 1;",
            safety_decision="BLOCK",
            gate_state="CLOSED",
            bridge_state="REJECTED_BY_BRIDGE",
            release_review_state="REJECTED_BY_RELEASE_REVIEW",
            authorization_state="REJECTED_BY_RELEASE_REVIEW",
            boundary_state="REJECTED_BY_RELEASE_REVIEW",
            actual_release_state="REJECT_ACTUAL_RELEASE_INPUT",
            final_runtime_outcome="BLOCKED_BEFORE_EXECUTION",
            release_eligible=False,
            fail_closed_reason=None,
        ),
    ]


def build_policy_case(
    *,
    proposal_class: str,
    normalized_sql: str,
    safety_decision: str,
    gate_state: str,
    bridge_state: str,
    release_review_state: str,
    authorization_state: str,
    boundary_state: str,
    actual_release_state: str,
    final_runtime_outcome: str,
    release_eligible: bool,
    fail_closed_reason: str | None,
    normalized_tool_name: str = "sql_runtime_candidate",
) -> dict[str, Any]:
    slug = proposal_class.lower()
    return {
        "request_id": f"policy_request_{slug}",
        "proposal_id": f"policy_proposal_{slug}",
        "proposal_class": proposal_class,
        "raw_tool_event_type": "runtime_tool_proposal",
        "normalized_tool_name": normalized_tool_name,
        "normalized_sql": normalized_sql,
        "safety_decision": safety_decision,
        "gate_state": gate_state,
        "bridge_state": bridge_state,
        "release_review_state": release_review_state,
        "authorization_state": authorization_state,
        "boundary_state": boundary_state,
        "actual_release_state": actual_release_state,
        "final_runtime_outcome": final_runtime_outcome,
        "release_eligible": release_eligible,
        "direct_execution_allowed": False,
        "execution_requested": False,
        "execution_release_allowed": False,
        "sql_executed": False,
        "sqlite_database_created": False,
        "sandbox_executed": False,
        "mutation_detected": False,
        "sandbox_deleted": False,
        "sandbox_deletion_verified": False,
        "policy_owner": POLICY_OWNER,
        "fail_closed_reason": fail_closed_reason,
        "not_claimed_scope": list(NOT_CLAIMED_SCOPE),
    }


def validate_policy_case(case: dict[str, Any]) -> dict[str, Any]:
    failed_checks: list[str] = []
    missing = sorted(REQUIRED_TRACE_FIELDS.difference(case))
    failed_checks.extend(f"missing_{field}" for field in missing)

    proposal_class = case.get("proposal_class")
    safety_decision = case.get("safety_decision")
    gate_state = case.get("gate_state")
    bridge_state = case.get("bridge_state")
    release_review_state = case.get("release_review_state")
    actual_release_state = case.get("actual_release_state")
    final_runtime_outcome = case.get("final_runtime_outcome")

    if proposal_class not in PROPOSAL_CLASSES:
        failed_checks.append("unknown_proposal_class")
    if safety_decision not in SAFETY_DECISIONS:
        failed_checks.append("unknown_safety_decision")
    if gate_state not in GATE_STATES:
        failed_checks.append("unknown_gate_state")
    if bridge_state not in BRIDGE_STATES:
        failed_checks.append("unknown_bridge_state")
    if release_review_state not in RELEASE_REVIEW_STATES:
        failed_checks.append("unknown_release_review_state")
    if case.get("authorization_state") not in RELEASE_REVIEW_STATES:
        failed_checks.append("unknown_authorization_state")
    if case.get("boundary_state") not in RELEASE_REVIEW_STATES:
        failed_checks.append("unknown_boundary_state")
    if actual_release_state not in ACTUAL_RELEASE_STATES:
        failed_checks.append("unknown_actual_release_state")
    if final_runtime_outcome not in FINAL_RUNTIME_OUTCOMES:
        failed_checks.append("unknown_final_runtime_outcome")
    if case.get("policy_owner") != POLICY_OWNER:
        failed_checks.append("policy_owner_not_dhms")
    if not case.get("not_claimed_scope"):
        failed_checks.append("not_claimed_scope_missing")

    for flag in sorted(NON_EXECUTION_FLAGS):
        if case.get(flag) is not False:
            failed_checks.append(f"{flag}_not_false")
    if case.get("direct_execution_allowed") is not False:
        failed_checks.append("direct_execution_allowed_not_false")

    release_eligible = is_unique_release_eligible_case(case)
    if release_eligible:
        if case.get("release_eligible") is not True:
            failed_checks.append("unique_candidate_release_eligible_not_true")
        if final_runtime_outcome != "HELD_FOR_CONTROLLED_RELEASE":
            failed_checks.append("unique_candidate_not_held_for_controlled_release")
    else:
        if case.get("release_eligible") is not False:
            failed_checks.append("rejected_case_release_eligible_not_false")
        if final_runtime_outcome not in {"BLOCKED_BEFORE_EXECUTION", "FAIL_CLOSED_BEFORE_EXECUTION"}:
            failed_checks.append("rejected_case_final_outcome_not_block_or_fail_closed")

    if safety_decision == "SANDBOX":
        if gate_state != "HELD_FOR_SANDBOX_BRIDGE":
            failed_checks.append("sandbox_not_held_for_bridge")
        if case.get("direct_execution_allowed") is not False:
            failed_checks.append("sandbox_direct_execution_allowed")
    if safety_decision == "BLOCK":
        if final_runtime_outcome != "BLOCKED_BEFORE_EXECUTION":
            failed_checks.append("block_final_outcome_not_blocked")
        if gate_state != "CLOSED":
            failed_checks.append("block_gate_not_closed")
    if safety_decision == "FAIL_CLOSED":
        if final_runtime_outcome != "FAIL_CLOSED_BEFORE_EXECUTION":
            failed_checks.append("fail_closed_final_outcome_mismatch")
        if gate_state != "FAIL_CLOSED":
            failed_checks.append("fail_closed_gate_mismatch")
        if not case.get("fail_closed_reason"):
            failed_checks.append("fail_closed_reason_missing")

    return {
        "proposal_class": proposal_class,
        "safety_decision": safety_decision,
        "gate_state": gate_state,
        "bridge_state": bridge_state,
        "final_runtime_outcome": final_runtime_outcome,
        "release_eligible": case.get("release_eligible"),
        "direct_execution_allowed": case.get("direct_execution_allowed"),
        "sql_executed": case.get("sql_executed"),
        "sqlite_database_created": case.get("sqlite_database_created"),
        "sandbox_executed": case.get("sandbox_executed"),
        "unsupported_fail_closed": safety_decision == "FAIL_CLOSED",
        "passed": not failed_checks,
        "failed_checks": failed_checks,
    }


def is_unique_release_eligible_case(case: dict[str, Any]) -> bool:
    return (
        case.get("proposal_class") == "SQL_SELECT_ALLOWLIST_CANDIDATE"
        and case.get("normalized_sql") == ALLOWLISTED_SELECT
        and case.get("safety_decision") == "SANDBOX"
        and case.get("gate_state") == "HELD_FOR_SANDBOX_BRIDGE"
        and case.get("bridge_state") == "ELIGIBLE_HELD_FOR_REVIEW"
        and case.get("release_review_state") == "CONTROLLED_RELEASE_READY_BUT_NOT_RELEASED"
        and case.get("authorization_state") == "ACTUAL_RELEASE_AUTHORIZATION_READY_BUT_NOT_EXECUTED"
        and case.get("boundary_state") == "BOUNDARY_READY_BUT_NOT_RELEASED"
    )
