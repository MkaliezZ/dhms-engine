#!/usr/bin/env python3
"""Deterministic first actual release boundary stub for the SQL sandbox runtime.

This module converts the v0.5.12 actual-release authorization review into
non-executing boundary data structures. It does not release execution, execute
SQL, create SQLite databases, call SQL sandbox execution, invoke OpenClaw, call
providers, use SDKs, or run production checker/runner logic.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from sql_sandbox_runtime_bridge_actual_release_authorization_review import (
    run_sql_sandbox_runtime_bridge_actual_release_authorization_review,
)
from sql_sandbox_runtime_bridge_stub import ALLOWLISTED_SELECT


ALLOWED_BOUNDARY_DECISIONS = {
    "BOUNDARY_READY_FOR_FUTURE_ACTUAL_RELEASE",
    "BOUNDARY_REJECTED",
    "BOUNDARY_FAIL_CLOSED",
}
ALLOWED_BOUNDARY_REASON_CODES = {
    "ALLOWLISTED_SELECT_AUTHORIZED_FOR_FUTURE_ACTUAL_RELEASE",
    "REJECTED_NO_AUTHORIZED_CANDIDATE",
    "REJECTED_MULTIPLE_AUTHORIZED_CANDIDATES",
    "REJECTED_ALLOWLIST_MISMATCH",
    "REJECTED_MUTATION_OR_UNSAFE_SQL",
    "REJECTED_MISSING_TRACE_CHAIN",
    "REJECTED_PREVIOUS_EXECUTION_DETECTED",
    "REJECTED_MISSING_DHMS_OWNERSHIP",
    "REJECTED_AUTHORIZATION_NOT_READY",
    "FAIL_CLOSED_INVALID_BOUNDARY_INPUT",
}
UNSAFE_OR_REJECTED_REASON_CODES = {
    "REJECTED_MUTATION_SQL",
    "REJECTED_BLOCK_DECISION",
    "REJECTED_NON_SQL_TOOL",
    "REJECTED_UNKNOWN_OR_MALFORMED_SQL",
    "REJECTED_MULTI_STATEMENT_SQL",
    "REJECTED_COMMENT_HIDDEN_MUTATION",
}

REQUIRED_BOUNDARY_INPUT_FIELDS = {
    "actual_release_boundary_input_id",
    "actual_release_authorization_id",
    "actual_release_review_input_id",
    "controlled_release_decision_id",
    "controlled_release_input_id",
    "review_decision_id",
    "bridge_input_id",
    "runtime_decision_id",
    "gate_id",
    "tool_type",
    "sql_text",
    "allowlist_matched",
    "select_only_candidate",
    "mutation_risk",
    "runtime_decision",
    "gate_result",
    "authorization_review_decision",
    "authorize_next_phase",
    "previous_execution_detected",
    "black_box_mode",
}
REQUIRED_BOUNDARY_DECISION_FIELDS = {
    "actual_release_boundary_decision_id",
    "actual_release_boundary_input_id",
    "boundary_decision",
    "boundary_reason_code",
    "boundary_ready_for_future_actual_release",
    "requires_explicit_next_phase",
    "release_now",
    "execution_release_allowed",
    "bridge_release_allowed",
    "sandbox_execution_released",
    "execution_requested",
    "requires_temp_sqlite_sandbox",
    "requires_mutation_detection",
    "requires_teardown_verification",
    "requires_delete_verification",
    "dhms_boundary_owner",
}
REQUIRED_BOUNDARY_TRACE_FIELDS = {
    "actual_release_boundary_trace_id",
    "actual_release_boundary_input_id",
    "actual_release_boundary_decision_id",
    "dry_run_only",
    "stub_only",
    "release_now",
    "execution_release_allowed",
    "bridge_release_allowed",
    "sandbox_execution_released",
    "execution_requested",
    "executed",
    "tool_executed",
    "sql_executed",
    "sandbox_executed",
    "sqlite_database_created",
    "openclaw_invoked",
    "provider_invoked",
    "agent_sdk_invoked",
    "external_service_sdk_invoked",
    "production_runner_invoked",
    "http_adapter_invoked",
    "external_mutation_detected",
    "black_box_validated",
    "dhms_boundary_owner",
}

NON_EXECUTION_TRACE_FLAGS = {
    "release_now",
    "execution_release_allowed",
    "bridge_release_allowed",
    "sandbox_execution_released",
    "execution_requested",
    "executed",
    "tool_executed",
    "sql_executed",
    "sandbox_executed",
    "sqlite_database_created",
    "openclaw_invoked",
    "provider_invoked",
    "agent_sdk_invoked",
    "external_service_sdk_invoked",
    "production_runner_invoked",
    "http_adapter_invoked",
    "external_mutation_detected",
}


def run_sql_sandbox_runtime_first_actual_release_boundary_stub() -> dict[str, Any]:
    authorization_result = run_sql_sandbox_runtime_bridge_actual_release_authorization_review()
    authorization_records = authorization_result.get("authorization_review_records", [])
    boundary_records = [build_boundary_record(record) for record in authorization_records]
    record_results = [validate_boundary_record(record) for record in boundary_records]

    failed_checks = [
        f"{result['actual_release_boundary_input_id']}.{check}"
        for result in record_results
        for check in result["failed_checks"]
    ]
    boundary_ready_count = sum(
        1 for result in record_results if result["boundary_decision"] == "BOUNDARY_READY_FOR_FUTURE_ACTUAL_RELEASE"
    )
    boundary_rejected_count = sum(
        1 for result in record_results if result["boundary_decision"] == "BOUNDARY_REJECTED"
    )
    release_now_count = sum(1 for record in boundary_records if record["boundary_trace"]["release_now"])
    execution_release_allowed_count = sum(
        1 for record in boundary_records if record["boundary_trace"]["execution_release_allowed"]
    )
    bridge_release_allowed_count = sum(
        1 for record in boundary_records if record["boundary_trace"]["bridge_release_allowed"]
    )
    sandbox_execution_released_count = sum(
        1 for record in boundary_records if record["boundary_trace"]["sandbox_execution_released"]
    )
    execution_requested_count = sum(
        1 for record in boundary_records if record["boundary_trace"]["execution_requested"]
    )
    sql_executed_count = sum(1 for record in boundary_records if record["boundary_trace"]["sql_executed"])
    sqlite_database_created_count = sum(
        1 for record in boundary_records if record["boundary_trace"]["sqlite_database_created"]
    )
    passed_actual_release_boundary_inputs = sum(1 for result in record_results if result["passed"])
    decisions_by_type = dict(sorted(Counter(result["boundary_decision"] for result in record_results).items()))
    reason_codes_by_type = dict(sorted(Counter(result["boundary_reason_code"] for result in record_results).items()))

    if authorization_result.get("status") != "PASS":
        failed_checks.append("actual_release_authorization_review_precondition_not_pass")
    if boundary_ready_count != 1:
        failed_checks.append("boundary_ready_count_not_one")
    if boundary_rejected_count != 6:
        failed_checks.append("boundary_rejected_count_not_six")

    status = "PASS" if not failed_checks and passed_actual_release_boundary_inputs == len(boundary_records) else "FAIL"

    return {
        "validation": "sql_sandbox_runtime_first_actual_release_boundary_stub_v0_5_14",
        "status": status,
        "total_actual_release_boundary_inputs": len(boundary_records),
        "passed_actual_release_boundary_inputs": passed_actual_release_boundary_inputs,
        "boundary_ready_count": boundary_ready_count,
        "boundary_rejected_count": boundary_rejected_count,
        "boundary_decisions_by_type": decisions_by_type,
        "boundary_reason_codes_by_type": reason_codes_by_type,
        "release_now_count": release_now_count,
        "execution_release_allowed_count": execution_release_allowed_count,
        "bridge_release_allowed_count": bridge_release_allowed_count,
        "sandbox_execution_released_count": sandbox_execution_released_count,
        "execution_requested_count": execution_requested_count,
        "sql_executed_count": sql_executed_count,
        "sqlite_database_created_count": sqlite_database_created_count,
        "failed_checks": failed_checks,
        "boundary_records": boundary_records,
        "record_results": record_results,
        "actual_release_authorization_review_status": authorization_result.get("status"),
        "actual_release_authorization_review_final_verdict": authorization_result.get("final_verdict"),
        "actual_controlled_release_implemented": False,
        "real_bridge_execution_implemented": False,
        "execution_gate_opened": False,
        "release_now": False,
        "execution_release_allowed": False,
        "bridge_release_allowed": False,
        "sandbox_execution_released": False,
        "execution_requested": False,
        "sql_execution_invoked_from_runtime_path": False,
        "sqlite_database_created_from_runtime_path": False,
        "sql_sandbox_execution_invoked_from_runtime_path": False,
        "openclaw_runtime_integration_implemented": False,
        "openclaw_invoked": False,
        "deepseek_invoked": False,
        "provider_sdk_invoked": False,
        "agent_sdk_invoked": False,
        "http_adapter_invoked": False,
        "production_checker_invoked": False,
        "production_runner_invoked": False,
        "full_suite_validation_invoked": False,
        "final_verdict": (
            "READY_FOR_V0_5_15_SQL_SANDBOX_RUNTIME_FIRST_ACTUAL_CONTROLLED_RELEASE"
            if status == "PASS"
            else "NEEDS_SQL_SANDBOX_RUNTIME_FIRST_ACTUAL_RELEASE_BOUNDARY_STUB_FIX"
        ),
    }


def build_boundary_record(authorization_record: dict[str, Any]) -> dict[str, Any]:
    boundary_input = build_boundary_input(authorization_record)
    decision = build_boundary_decision(boundary_input)
    trace = build_boundary_trace(boundary_input, decision)
    return {
        "boundary_input": boundary_input,
        "boundary_decision": decision,
        "boundary_trace": trace,
    }


def build_boundary_input(authorization_record: dict[str, Any]) -> dict[str, Any]:
    review_input = authorization_record["authorization_review_input"]
    decision = authorization_record["authorization_review_decision"]
    return {
        "actual_release_boundary_input_id": (
            f"actual_release_boundary_input_{review_input['actual_release_review_input_id']}"
        ),
        "actual_release_authorization_id": decision["actual_release_authorization_id"],
        "actual_release_review_input_id": review_input["actual_release_review_input_id"],
        "controlled_release_decision_id": review_input["controlled_release_decision_id"],
        "controlled_release_input_id": review_input["controlled_release_input_id"],
        "review_decision_id": review_input["review_decision_id"],
        "bridge_input_id": review_input["bridge_input_id"],
        "runtime_decision_id": review_input["runtime_decision_id"],
        "gate_id": review_input["gate_id"],
        "tool_type": review_input["tool_type"],
        "sql_text": review_input["sql_text"],
        "allowlist_matched": review_input["allowlist_matched"],
        "select_only_candidate": review_input["select_only_candidate"],
        "mutation_risk": review_input["mutation_risk"],
        "runtime_decision": review_input["runtime_decision"],
        "gate_result": review_input["gate_result"],
        "authorization_review_decision": decision["authorization_review_decision"],
        "authorization_review_reason_code": decision["authorization_review_reason_code"],
        "authorize_next_phase": decision["authorize_next_phase"],
        "previous_execution_detected": review_input["previous_execution_detected"],
        "black_box_mode": review_input["black_box_mode"],
    }


def build_boundary_decision(boundary_input: dict[str, Any]) -> dict[str, Any]:
    ready = is_boundary_ready_candidate(boundary_input)
    if ready:
        boundary_decision = "BOUNDARY_READY_FOR_FUTURE_ACTUAL_RELEASE"
        reason_code = "ALLOWLISTED_SELECT_AUTHORIZED_FOR_FUTURE_ACTUAL_RELEASE"
        boundary_ready = True
    elif boundary_input.get("authorization_review_decision") == "ACTUAL_RELEASE_AUTHORIZATION_REJECTED_INPUT":
        boundary_decision = "BOUNDARY_REJECTED"
        reason_code = reason_code_for_rejected_input(boundary_input)
        boundary_ready = False
    else:
        boundary_decision = "BOUNDARY_FAIL_CLOSED"
        reason_code = "FAIL_CLOSED_INVALID_BOUNDARY_INPUT"
        boundary_ready = False

    return {
        "actual_release_boundary_decision_id": (
            f"actual_release_boundary_decision_{boundary_input['actual_release_boundary_input_id']}"
        ),
        "actual_release_boundary_input_id": boundary_input["actual_release_boundary_input_id"],
        "boundary_decision": boundary_decision,
        "boundary_reason_code": reason_code,
        "boundary_ready_for_future_actual_release": boundary_ready,
        "requires_explicit_next_phase": True,
        "release_now": False,
        "execution_release_allowed": False,
        "bridge_release_allowed": False,
        "sandbox_execution_released": False,
        "execution_requested": False,
        "requires_temp_sqlite_sandbox": True,
        "requires_mutation_detection": True,
        "requires_teardown_verification": True,
        "requires_delete_verification": True,
        "dhms_boundary_owner": True,
    }


def is_boundary_ready_candidate(boundary_input: dict[str, Any]) -> bool:
    return (
        boundary_input.get("tool_type") == "SQL"
        and boundary_input.get("sql_text") == ALLOWLISTED_SELECT
        and boundary_input.get("allowlist_matched") is True
        and boundary_input.get("select_only_candidate") is True
        and boundary_input.get("mutation_risk") is False
        and boundary_input.get("runtime_decision") == "SANDBOX"
        and boundary_input.get("gate_result") == "HELD_FOR_SANDBOX_BRIDGE"
        and boundary_input.get("authorization_review_decision")
        == "ACTUAL_RELEASE_AUTHORIZATION_READY_BUT_NOT_EXECUTED"
        and boundary_input.get("authorize_next_phase") is True
        and boundary_input.get("previous_execution_detected") is False
        and boundary_input.get("black_box_mode") is True
    )


def reason_code_for_rejected_input(boundary_input: dict[str, Any]) -> str:
    reason = str(boundary_input.get("authorization_review_reason_code"))
    if reason == "REJECTED_BLOCK_DECISION":
        return "REJECTED_AUTHORIZATION_NOT_READY"
    if reason == "REJECTED_NON_SQL_TOOL":
        return "REJECTED_AUTHORIZATION_NOT_READY"
    if reason in {
        "REJECTED_MUTATION_SQL",
        "REJECTED_UNKNOWN_OR_MALFORMED_SQL",
        "REJECTED_MULTI_STATEMENT_SQL",
        "REJECTED_COMMENT_HIDDEN_MUTATION",
    }:
        return "REJECTED_MUTATION_OR_UNSAFE_SQL"
    return "FAIL_CLOSED_INVALID_BOUNDARY_INPUT"


def build_boundary_trace(
    boundary_input: dict[str, Any],
    decision: dict[str, Any],
) -> dict[str, Any]:
    return {
        "actual_release_boundary_trace_id": (
            f"actual_release_boundary_trace_{boundary_input['actual_release_boundary_input_id']}"
        ),
        "actual_release_boundary_input_id": boundary_input["actual_release_boundary_input_id"],
        "actual_release_boundary_decision_id": decision["actual_release_boundary_decision_id"],
        "dry_run_only": True,
        "stub_only": True,
        "release_now": False,
        "execution_release_allowed": False,
        "bridge_release_allowed": False,
        "sandbox_execution_released": False,
        "execution_requested": False,
        "executed": False,
        "tool_executed": False,
        "sql_executed": False,
        "sandbox_executed": False,
        "sqlite_database_created": False,
        "openclaw_invoked": False,
        "provider_invoked": False,
        "agent_sdk_invoked": False,
        "external_service_sdk_invoked": False,
        "production_runner_invoked": False,
        "http_adapter_invoked": False,
        "external_mutation_detected": False,
        "black_box_validated": True,
        "dhms_boundary_owner": True,
    }


def validate_boundary_record(record: dict[str, Any]) -> dict[str, Any]:
    failed_checks: list[str] = []
    boundary_input = record.get("boundary_input", {})
    decision = record.get("boundary_decision", {})
    trace = record.get("boundary_trace", {})

    require_fields("boundary_input", boundary_input, REQUIRED_BOUNDARY_INPUT_FIELDS, failed_checks)
    require_fields("boundary_decision", decision, REQUIRED_BOUNDARY_DECISION_FIELDS, failed_checks)
    require_fields("boundary_trace", trace, REQUIRED_BOUNDARY_TRACE_FIELDS, failed_checks)

    boundary_decision = decision.get("boundary_decision")
    reason_code = decision.get("boundary_reason_code")
    if boundary_decision not in ALLOWED_BOUNDARY_DECISIONS:
        failed_checks.append("unknown_boundary_decision")
    if reason_code not in ALLOWED_BOUNDARY_REASON_CODES:
        failed_checks.append("unknown_boundary_reason_code")
    if decision.get("requires_explicit_next_phase") is not True:
        failed_checks.append("requires_explicit_next_phase_not_true")
    if decision.get("dhms_boundary_owner") is not True:
        failed_checks.append("decision_not_dhms_boundary_owner")
    if trace.get("dhms_boundary_owner") is not True:
        failed_checks.append("trace_not_dhms_boundary_owner")
    if trace.get("black_box_validated") is not True:
        failed_checks.append("trace_black_box_not_true")
    if trace.get("dry_run_only") is not True:
        failed_checks.append("trace_dry_run_only_not_true")
    if trace.get("stub_only") is not True:
        failed_checks.append("trace_stub_only_not_true")

    for flag in sorted(NON_EXECUTION_TRACE_FLAGS):
        if trace.get(flag) is not False:
            failed_checks.append(f"trace_{flag}_not_false")
    for field in (
        "release_now",
        "execution_release_allowed",
        "bridge_release_allowed",
        "sandbox_execution_released",
        "execution_requested",
    ):
        if decision.get(field) is not False:
            failed_checks.append(f"decision_{field}_not_false")
    for field in (
        "requires_temp_sqlite_sandbox",
        "requires_mutation_detection",
        "requires_teardown_verification",
        "requires_delete_verification",
    ):
        if decision.get(field) is not True:
            failed_checks.append(f"decision_{field}_not_true")

    ready_candidate = is_boundary_ready_candidate(boundary_input)
    if ready_candidate:
        if boundary_decision != "BOUNDARY_READY_FOR_FUTURE_ACTUAL_RELEASE":
            failed_checks.append("ready_candidate_boundary_decision_mismatch")
        if reason_code != "ALLOWLISTED_SELECT_AUTHORIZED_FOR_FUTURE_ACTUAL_RELEASE":
            failed_checks.append("ready_candidate_reason_mismatch")
        if decision.get("boundary_ready_for_future_actual_release") is not True:
            failed_checks.append("ready_candidate_boundary_ready_not_true")
    else:
        if boundary_input.get("authorization_review_decision") == "ACTUAL_RELEASE_AUTHORIZATION_REJECTED_INPUT":
            if boundary_decision != "BOUNDARY_REJECTED":
                failed_checks.append("rejected_input_boundary_decision_mismatch")
            expected_reason = reason_code_for_rejected_input(boundary_input)
            if reason_code != expected_reason:
                failed_checks.append(f"rejected_input_reason_expected_{expected_reason}")
        else:
            if boundary_decision != "BOUNDARY_FAIL_CLOSED":
                failed_checks.append("invalid_input_not_fail_closed")
        if decision.get("boundary_ready_for_future_actual_release") is not False:
            failed_checks.append("rejected_or_invalid_boundary_ready_not_false")

    return {
        "actual_release_boundary_input_id": boundary_input.get("actual_release_boundary_input_id"),
        "actual_release_authorization_id": boundary_input.get("actual_release_authorization_id"),
        "boundary_decision": boundary_decision,
        "boundary_reason_code": reason_code,
        "boundary_ready_for_future_actual_release": decision.get("boundary_ready_for_future_actual_release"),
        "release_now": trace.get("release_now"),
        "execution_release_allowed": trace.get("execution_release_allowed"),
        "bridge_release_allowed": trace.get("bridge_release_allowed"),
        "sandbox_execution_released": trace.get("sandbox_execution_released"),
        "execution_requested": trace.get("execution_requested"),
        "sql_executed": trace.get("sql_executed"),
        "sqlite_database_created": trace.get("sqlite_database_created"),
        "passed": not failed_checks,
        "failed_checks": failed_checks,
    }


def require_fields(prefix: str, payload: dict[str, Any], required_fields: set[str], failed_checks: list[str]) -> None:
    missing = sorted(required_fields.difference(payload))
    for field in missing:
        failed_checks.append(f"{prefix}.missing_{field}")
