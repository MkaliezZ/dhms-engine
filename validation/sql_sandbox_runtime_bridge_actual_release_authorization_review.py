#!/usr/bin/env python3
"""Deterministic actual-release authorization review for the SQL bridge.

This module reviews the v0.5.11 controlled-release-ready candidate and decides
whether the next phase may implement an actual controlled release boundary. It
does not release execution, execute SQL, create SQLite databases, call SQL
sandbox execution, invoke OpenClaw, call providers, use SDKs, or run production
checker/runner logic.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from sql_sandbox_runtime_bridge_first_controlled_release_stub import (
    run_sql_sandbox_runtime_bridge_first_controlled_release_stub,
)
from sql_sandbox_runtime_bridge_stub import ALLOWLISTED_SELECT


ALLOWED_AUTHORIZATION_REVIEW_DECISIONS = {
    "ACTUAL_RELEASE_AUTHORIZATION_READY_BUT_NOT_EXECUTED",
    "ACTUAL_RELEASE_AUTHORIZATION_REJECTED_INPUT",
    "ACTUAL_RELEASE_AUTHORIZATION_FAIL_CLOSED",
}
ALLOWED_AUTHORIZATION_REVIEW_REASON_CODES = {
    "ALLOWLISTED_SELECT_READY_FOR_NEXT_PHASE_ACTUAL_RELEASE_BOUNDARY",
    "REJECTED_MUTATION_SQL",
    "REJECTED_BLOCK_DECISION",
    "REJECTED_NON_SQL_TOOL",
    "REJECTED_UNKNOWN_OR_MALFORMED_SQL",
    "REJECTED_MULTI_STATEMENT_SQL",
    "REJECTED_COMMENT_HIDDEN_MUTATION",
    "FAIL_CLOSED_INVALID_ACTUAL_RELEASE_REVIEW_INPUT",
}
CONTROLLED_RELEASE_REASON_TO_AUTHORIZATION_REASON = {
    "REJECTED_MUTATION_SQL": "REJECTED_MUTATION_SQL",
    "REJECTED_BLOCK_DECISION": "REJECTED_BLOCK_DECISION",
    "REJECTED_NON_SQL_TOOL": "REJECTED_NON_SQL_TOOL",
    "REJECTED_UNKNOWN_OR_MALFORMED_SQL": "REJECTED_UNKNOWN_OR_MALFORMED_SQL",
    "REJECTED_MULTI_STATEMENT_SQL": "REJECTED_MULTI_STATEMENT_SQL",
    "REJECTED_COMMENT_HIDDEN_MUTATION": "REJECTED_COMMENT_HIDDEN_MUTATION",
}

REQUIRED_AUTHORIZATION_REVIEW_INPUT_FIELDS = {
    "actual_release_review_input_id",
    "controlled_release_input_id",
    "controlled_release_decision_id",
    "planned_release_request_id",
    "review_input_id",
    "review_decision_id",
    "bridge_input_id",
    "bridge_eligibility_id",
    "bridge_authorization_id",
    "sandbox_request_id",
    "runtime_decision_id",
    "gate_id",
    "tool_type",
    "runtime_decision",
    "gate_result",
    "bridge_result",
    "review_decision",
    "controlled_release_decision",
    "sql_text",
    "allowlist_matched",
    "select_only_candidate",
    "mutation_risk",
    "future_release_candidate",
    "future_release_allowed_conditionally",
    "previous_execution_detected",
    "black_box_mode",
}
REQUIRED_AUTHORIZATION_REVIEW_DECISION_FIELDS = {
    "actual_release_authorization_id",
    "actual_release_review_input_id",
    "authorization_review_decision",
    "authorization_review_reason_code",
    "future_actual_release_candidate",
    "authorize_next_phase",
    "requires_explicit_next_phase",
    "release_now",
    "bridge_release_allowed",
    "sandbox_execution_released",
    "execution_requested",
    "sql_executed",
    "sqlite_database_created",
    "dhms_actual_release_authorization_owner",
}
REQUIRED_AUTHORIZATION_TRACE_FIELDS = {
    "actual_release_authorization_trace_id",
    "actual_release_review_input_id",
    "actual_release_authorization_id",
    "controlled_release_input_id",
    "controlled_release_decision_id",
    "planned_release_request_id",
    "tool_type",
    "runtime_decision",
    "gate_result",
    "bridge_result",
    "controlled_release_decision",
    "authorization_review_decision",
    "dry_run_only",
    "review_only",
    "release_now",
    "authorize_next_phase",
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
    "dhms_actual_release_authorization_owner",
}

NON_EXECUTION_TRACE_FLAGS = {
    "release_now",
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


def run_sql_sandbox_runtime_bridge_actual_release_authorization_review() -> dict[str, Any]:
    controlled_release_result = run_sql_sandbox_runtime_bridge_first_controlled_release_stub()
    controlled_records = controlled_release_result.get("controlled_release_records", [])
    authorization_records = [build_authorization_review_record(record) for record in controlled_records]
    record_results = [validate_authorization_review_record(record) for record in authorization_records]

    failed_checks = [
        f"{result['actual_release_review_input_id']}.{check}"
        for result in record_results
        for check in result["failed_checks"]
    ]
    ready_but_not_executed_count = sum(
        1
        for result in record_results
        if result["authorization_review_decision"] == "ACTUAL_RELEASE_AUTHORIZATION_READY_BUT_NOT_EXECUTED"
    )
    rejected_authorization_review_count = sum(
        1
        for result in record_results
        if result["authorization_review_decision"] == "ACTUAL_RELEASE_AUTHORIZATION_REJECTED_INPUT"
    )
    future_actual_release_candidate_count = sum(
        1 for result in record_results if result["future_actual_release_candidate"]
    )
    authorize_next_phase_count = sum(1 for result in record_results if result["authorize_next_phase"])
    release_now_count = sum(1 for record in authorization_records if record["authorization_trace"]["release_now"])
    bridge_release_allowed_count = sum(
        1 for record in authorization_records if record["authorization_trace"]["bridge_release_allowed"]
    )
    sandbox_execution_released_count = sum(
        1 for record in authorization_records if record["authorization_trace"]["sandbox_execution_released"]
    )
    execution_requested_count = sum(
        1 for record in authorization_records if record["authorization_trace"]["execution_requested"]
    )
    sql_executed_count = sum(1 for record in authorization_records if record["authorization_trace"]["sql_executed"])
    sqlite_database_created_count = sum(
        1 for record in authorization_records if record["authorization_trace"]["sqlite_database_created"]
    )
    passed_actual_release_review_inputs = sum(1 for result in record_results if result["passed"])
    decisions_by_type = dict(
        sorted(Counter(result["authorization_review_decision"] for result in record_results).items())
    )
    reason_codes_by_type = dict(
        sorted(Counter(result["authorization_review_reason_code"] for result in record_results).items())
    )

    if controlled_release_result.get("status") != "PASS":
        failed_checks.append("controlled_release_stub_precondition_not_pass")
    if ready_but_not_executed_count != 1:
        failed_checks.append("ready_but_not_executed_count_not_one")
    if future_actual_release_candidate_count != 1:
        failed_checks.append("future_actual_release_candidate_count_not_one")
    if authorize_next_phase_count != 1:
        failed_checks.append("authorize_next_phase_count_not_one")
    if rejected_authorization_review_count != 6:
        failed_checks.append("rejected_authorization_review_count_not_six")

    status = "PASS" if not failed_checks and passed_actual_release_review_inputs == len(authorization_records) else "FAIL"

    return {
        "validation": "sql_sandbox_runtime_bridge_actual_release_authorization_review_v0_5_12",
        "status": status,
        "total_actual_release_review_inputs": len(authorization_records),
        "passed_actual_release_review_inputs": passed_actual_release_review_inputs,
        "ready_but_not_executed_count": ready_but_not_executed_count,
        "rejected_authorization_review_count": rejected_authorization_review_count,
        "future_actual_release_candidate_count": future_actual_release_candidate_count,
        "authorize_next_phase_count": authorize_next_phase_count,
        "authorization_review_decisions_by_type": decisions_by_type,
        "authorization_review_reason_codes_by_type": reason_codes_by_type,
        "release_now_count": release_now_count,
        "bridge_release_allowed_count": bridge_release_allowed_count,
        "sandbox_execution_released_count": sandbox_execution_released_count,
        "execution_requested_count": execution_requested_count,
        "sql_executed_count": sql_executed_count,
        "sqlite_database_created_count": sqlite_database_created_count,
        "failed_checks": failed_checks,
        "authorization_review_records": authorization_records,
        "record_results": record_results,
        "controlled_release_stub_status": controlled_release_result.get("status"),
        "controlled_release_stub_final_verdict": controlled_release_result.get("final_verdict"),
        "actual_controlled_release_implemented": False,
        "real_bridge_execution_implemented": False,
        "execution_gate_opened": False,
        "release_now": False,
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
            "READY_FOR_V0_5_13_SQL_SANDBOX_RUNTIME_FIRST_ACTUAL_RELEASE_BOUNDARY_PLAN"
            if status == "PASS"
            else "NEEDS_SQL_SANDBOX_RUNTIME_BRIDGE_ACTUAL_RELEASE_AUTHORIZATION_REVIEW_FIX"
        ),
    }


def build_authorization_review_record(controlled_record: dict[str, Any]) -> dict[str, Any]:
    review_input = build_authorization_review_input(controlled_record)
    decision = build_authorization_review_decision(review_input)
    trace = build_authorization_trace(review_input, decision)
    return {
        "authorization_review_input": review_input,
        "authorization_review_decision": decision,
        "authorization_trace": trace,
    }


def build_authorization_review_input(controlled_record: dict[str, Any]) -> dict[str, Any]:
    controlled_input = controlled_record["controlled_release_input"]
    controlled_decision = controlled_record["controlled_release_decision"]
    planned_request = controlled_record["planned_release_request"]
    return {
        "actual_release_review_input_id": (
            f"actual_release_review_input_{controlled_input['controlled_release_input_id']}"
        ),
        "controlled_release_input_id": controlled_input["controlled_release_input_id"],
        "controlled_release_decision_id": controlled_decision["controlled_release_decision_id"],
        "planned_release_request_id": planned_request["planned_release_request_id"],
        "review_input_id": controlled_input["review_input_id"],
        "review_decision_id": controlled_input["review_decision_id"],
        "bridge_input_id": controlled_input["bridge_input_id"],
        "bridge_eligibility_id": controlled_input["bridge_eligibility_id"],
        "bridge_authorization_id": controlled_input["bridge_authorization_id"],
        "sandbox_request_id": controlled_input["sandbox_request_id"],
        "runtime_decision_id": controlled_input["runtime_decision_id"],
        "gate_id": controlled_input["gate_id"],
        "tool_type": controlled_input["tool_type"],
        "runtime_decision": controlled_input["runtime_decision"],
        "gate_result": controlled_input["gate_result"],
        "bridge_result": controlled_input["bridge_result"],
        "review_decision": controlled_input["review_decision"],
        "controlled_release_decision": controlled_decision["controlled_release_decision"],
        "sql_text": controlled_input["sql_text"],
        "allowlist_matched": controlled_input["allowlist_matched"],
        "select_only_candidate": controlled_input["select_only_candidate"],
        "mutation_risk": controlled_input["mutation_risk"],
        "future_release_candidate": controlled_decision["future_release_candidate"],
        "future_release_allowed_conditionally": controlled_decision["future_release_allowed_conditionally"],
        "previous_execution_detected": controlled_input["previous_execution_detected"],
        "black_box_mode": controlled_input["black_box_mode"],
    }


def build_authorization_review_decision(review_input: dict[str, Any]) -> dict[str, Any]:
    ready = is_actual_release_authorization_candidate(review_input)
    if ready:
        authorization_decision = "ACTUAL_RELEASE_AUTHORIZATION_READY_BUT_NOT_EXECUTED"
        reason_code = "ALLOWLISTED_SELECT_READY_FOR_NEXT_PHASE_ACTUAL_RELEASE_BOUNDARY"
        future_actual_release_candidate = True
        authorize_next_phase = True
    elif review_input.get("controlled_release_decision") == "CONTROLLED_RELEASE_REJECTED_INPUT":
        authorization_decision = "ACTUAL_RELEASE_AUTHORIZATION_REJECTED_INPUT"
        reason_code = reason_code_for_rejected_input(review_input)
        future_actual_release_candidate = False
        authorize_next_phase = False
    else:
        authorization_decision = "ACTUAL_RELEASE_AUTHORIZATION_FAIL_CLOSED"
        reason_code = "FAIL_CLOSED_INVALID_ACTUAL_RELEASE_REVIEW_INPUT"
        future_actual_release_candidate = False
        authorize_next_phase = False

    return {
        "actual_release_authorization_id": (
            f"actual_release_authorization_{review_input['actual_release_review_input_id']}"
        ),
        "actual_release_review_input_id": review_input["actual_release_review_input_id"],
        "authorization_review_decision": authorization_decision,
        "authorization_review_reason_code": reason_code,
        "future_actual_release_candidate": future_actual_release_candidate,
        "authorize_next_phase": authorize_next_phase,
        "requires_explicit_next_phase": True,
        "release_now": False,
        "bridge_release_allowed": False,
        "sandbox_execution_released": False,
        "execution_requested": False,
        "sql_executed": False,
        "sqlite_database_created": False,
        "dhms_actual_release_authorization_owner": True,
    }


def is_actual_release_authorization_candidate(review_input: dict[str, Any]) -> bool:
    return (
        review_input.get("tool_type") == "SQL"
        and review_input.get("runtime_decision") == "SANDBOX"
        and review_input.get("gate_result") == "HELD_FOR_SANDBOX_BRIDGE"
        and review_input.get("bridge_result") == "ELIGIBLE_HELD_FOR_FUTURE_SANDBOX_EXECUTION"
        and review_input.get("review_decision") == "REVIEW_READY_BUT_NOT_RELEASED"
        and review_input.get("controlled_release_decision") == "CONTROLLED_RELEASE_READY_BUT_NOT_RELEASED"
        and review_input.get("sql_text") == ALLOWLISTED_SELECT
        and review_input.get("allowlist_matched") is True
        and review_input.get("select_only_candidate") is True
        and review_input.get("mutation_risk") is False
        and review_input.get("future_release_candidate") is True
        and review_input.get("future_release_allowed_conditionally") is True
        and review_input.get("previous_execution_detected") is False
        and review_input.get("black_box_mode") is True
    )


def reason_code_for_rejected_input(review_input: dict[str, Any]) -> str:
    bridge_result = str(review_input.get("bridge_result"))
    bridge_to_reason = {
        "REJECTED_MUTATION_SQL": "REJECTED_MUTATION_SQL",
        "REJECTED_BLOCK_DECISION": "REJECTED_BLOCK_DECISION",
        "REJECTED_NON_SQL_TOOL": "REJECTED_NON_SQL_TOOL",
        "REJECTED_UNKNOWN_OR_MALFORMED_SQL": "REJECTED_UNKNOWN_OR_MALFORMED_SQL",
        "REJECTED_MULTI_STATEMENT_SQL": "REJECTED_MULTI_STATEMENT_SQL",
        "REJECTED_COMMENT_HIDDEN_MUTATION": "REJECTED_COMMENT_HIDDEN_MUTATION",
    }
    return bridge_to_reason.get(bridge_result, "FAIL_CLOSED_INVALID_ACTUAL_RELEASE_REVIEW_INPUT")


def build_authorization_trace(
    review_input: dict[str, Any],
    decision: dict[str, Any],
) -> dict[str, Any]:
    return {
        "actual_release_authorization_trace_id": (
            f"actual_release_authorization_trace_{review_input['actual_release_review_input_id']}"
        ),
        "actual_release_review_input_id": review_input["actual_release_review_input_id"],
        "actual_release_authorization_id": decision["actual_release_authorization_id"],
        "controlled_release_input_id": review_input["controlled_release_input_id"],
        "controlled_release_decision_id": review_input["controlled_release_decision_id"],
        "planned_release_request_id": review_input["planned_release_request_id"],
        "tool_type": review_input["tool_type"],
        "runtime_decision": review_input["runtime_decision"],
        "gate_result": review_input["gate_result"],
        "bridge_result": review_input["bridge_result"],
        "controlled_release_decision": review_input["controlled_release_decision"],
        "authorization_review_decision": decision["authorization_review_decision"],
        "dry_run_only": True,
        "review_only": True,
        "release_now": False,
        "authorize_next_phase": decision["authorize_next_phase"],
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
        "dhms_actual_release_authorization_owner": True,
    }


def validate_authorization_review_record(record: dict[str, Any]) -> dict[str, Any]:
    failed_checks: list[str] = []
    review_input = record.get("authorization_review_input", {})
    decision = record.get("authorization_review_decision", {})
    trace = record.get("authorization_trace", {})

    require_fields(
        "authorization_review_input",
        review_input,
        REQUIRED_AUTHORIZATION_REVIEW_INPUT_FIELDS,
        failed_checks,
    )
    require_fields(
        "authorization_review_decision",
        decision,
        REQUIRED_AUTHORIZATION_REVIEW_DECISION_FIELDS,
        failed_checks,
    )
    require_fields("authorization_trace", trace, REQUIRED_AUTHORIZATION_TRACE_FIELDS, failed_checks)

    authorization_decision = decision.get("authorization_review_decision")
    reason_code = decision.get("authorization_review_reason_code")
    if authorization_decision not in ALLOWED_AUTHORIZATION_REVIEW_DECISIONS:
        failed_checks.append("unknown_authorization_review_decision")
    if reason_code not in ALLOWED_AUTHORIZATION_REVIEW_REASON_CODES:
        failed_checks.append("unknown_authorization_review_reason_code")
    if decision.get("requires_explicit_next_phase") is not True:
        failed_checks.append("requires_explicit_next_phase_not_true")
    if decision.get("dhms_actual_release_authorization_owner") is not True:
        failed_checks.append("decision_not_dhms_actual_release_authorization_owner")
    if trace.get("dhms_actual_release_authorization_owner") is not True:
        failed_checks.append("trace_not_dhms_actual_release_authorization_owner")
    if trace.get("black_box_validated") is not True:
        failed_checks.append("trace_black_box_not_true")
    if trace.get("dry_run_only") is not True:
        failed_checks.append("trace_dry_run_only_not_true")
    if trace.get("review_only") is not True:
        failed_checks.append("trace_review_only_not_true")

    for flag in sorted(NON_EXECUTION_TRACE_FLAGS):
        if trace.get(flag) is not False:
            failed_checks.append(f"trace_{flag}_not_false")
    for field in (
        "release_now",
        "bridge_release_allowed",
        "sandbox_execution_released",
        "execution_requested",
        "sql_executed",
        "sqlite_database_created",
    ):
        if decision.get(field) is not False:
            failed_checks.append(f"decision_{field}_not_false")

    ready_candidate = is_actual_release_authorization_candidate(review_input)
    if ready_candidate:
        if authorization_decision != "ACTUAL_RELEASE_AUTHORIZATION_READY_BUT_NOT_EXECUTED":
            failed_checks.append("ready_candidate_authorization_decision_mismatch")
        if reason_code != "ALLOWLISTED_SELECT_READY_FOR_NEXT_PHASE_ACTUAL_RELEASE_BOUNDARY":
            failed_checks.append("ready_candidate_reason_mismatch")
        if decision.get("future_actual_release_candidate") is not True:
            failed_checks.append("ready_candidate_future_actual_release_candidate_not_true")
        if decision.get("authorize_next_phase") is not True:
            failed_checks.append("ready_candidate_authorize_next_phase_not_true")
    else:
        if review_input.get("controlled_release_decision") == "CONTROLLED_RELEASE_REJECTED_INPUT":
            if authorization_decision != "ACTUAL_RELEASE_AUTHORIZATION_REJECTED_INPUT":
                failed_checks.append("rejected_input_authorization_decision_mismatch")
            expected_reason = reason_code_for_rejected_input(review_input)
            if reason_code != expected_reason:
                failed_checks.append(f"rejected_input_reason_expected_{expected_reason}")
        else:
            if authorization_decision != "ACTUAL_RELEASE_AUTHORIZATION_FAIL_CLOSED":
                failed_checks.append("invalid_input_not_fail_closed")
        if decision.get("future_actual_release_candidate") is not False:
            failed_checks.append("rejected_or_invalid_future_actual_release_candidate_not_false")
        if decision.get("authorize_next_phase") is not False:
            failed_checks.append("rejected_or_invalid_authorize_next_phase_not_false")

    return {
        "actual_release_review_input_id": review_input.get("actual_release_review_input_id"),
        "controlled_release_input_id": review_input.get("controlled_release_input_id"),
        "authorization_review_decision": authorization_decision,
        "authorization_review_reason_code": reason_code,
        "future_actual_release_candidate": decision.get("future_actual_release_candidate"),
        "authorize_next_phase": decision.get("authorize_next_phase"),
        "release_now": trace.get("release_now"),
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
