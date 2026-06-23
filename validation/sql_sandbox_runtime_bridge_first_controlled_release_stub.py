#!/usr/bin/env python3
"""Deterministic controlled-release stub for the SQL sandbox bridge.

This module converts the v0.5.9 held-release review result into non-executing
controlled-release data structures. It does not release execution, execute SQL,
create SQLite databases, call SQL sandbox execution, invoke OpenClaw, call
providers, use SDKs, or run production checker/runner logic.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from sql_sandbox_runtime_bridge_first_held_release_review import (
    run_sql_sandbox_runtime_bridge_first_held_release_review,
)
from sql_sandbox_runtime_bridge_stub import ALLOWLISTED_SELECT


ALLOWED_CONTROLLED_RELEASE_DECISIONS = {
    "CONTROLLED_RELEASE_READY_BUT_NOT_RELEASED",
    "CONTROLLED_RELEASE_REJECTED_INPUT",
    "CONTROLLED_RELEASE_FAIL_CLOSED",
}
ALLOWED_CONTROLLED_RELEASE_REASON_CODES = {
    "ALLOWLISTED_SELECT_READY_FOR_FUTURE_CONTROLLED_SANDBOX_RELEASE",
    "REJECTED_MUTATION_SQL",
    "REJECTED_BLOCK_DECISION",
    "REJECTED_NON_SQL_TOOL",
    "REJECTED_UNKNOWN_OR_MALFORMED_SQL",
    "REJECTED_MULTI_STATEMENT_SQL",
    "REJECTED_COMMENT_HIDDEN_MUTATION",
    "FAIL_CLOSED_INVALID_CONTROLLED_RELEASE_INPUT",
}
REVIEW_REASON_TO_CONTROLLED_RELEASE_REASON = {
    "REJECTED_MUTATION_SQL": "REJECTED_MUTATION_SQL",
    "REJECTED_BLOCK_DECISION": "REJECTED_BLOCK_DECISION",
    "REJECTED_NON_SQL_TOOL": "REJECTED_NON_SQL_TOOL",
    "REJECTED_UNKNOWN_OR_MALFORMED_SQL": "REJECTED_UNKNOWN_OR_MALFORMED_SQL",
    "REJECTED_MULTI_STATEMENT_SQL": "REJECTED_MULTI_STATEMENT_SQL",
    "REJECTED_COMMENT_HIDDEN_MUTATION": "REJECTED_COMMENT_HIDDEN_MUTATION",
}

REQUIRED_CONTROLLED_RELEASE_INPUT_FIELDS = {
    "controlled_release_input_id",
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
    "sql_text",
    "allowlist_matched",
    "select_only_candidate",
    "mutation_risk",
    "previous_execution_detected",
    "black_box_mode",
}
REQUIRED_CONTROLLED_RELEASE_DECISION_FIELDS = {
    "controlled_release_decision_id",
    "controlled_release_input_id",
    "controlled_release_decision",
    "controlled_release_reason_code",
    "future_release_candidate",
    "future_release_allowed_conditionally",
    "requires_explicit_next_phase",
    "release_now",
    "bridge_release_allowed",
    "sandbox_execution_released",
    "execution_requested",
    "dhms_release_owner",
}
REQUIRED_PLANNED_RELEASE_REQUEST_FIELDS = {
    "planned_release_request_id",
    "controlled_release_decision_id",
    "sql_text",
    "allowlisted_select",
    "temporary_database_required",
    "synthetic_data_only",
    "mutation_detection_required",
    "teardown_required",
    "delete_verification_required",
    "real_database",
    "network_database",
    "credential_used",
    "production_data_used",
    "sandbox_execution_requested",
    "release_now",
    "sql_executed",
    "sqlite_database_created",
}
REQUIRED_CONTROLLED_RELEASE_TRACE_FIELDS = {
    "controlled_release_trace_id",
    "controlled_release_input_id",
    "controlled_release_decision_id",
    "planned_release_request_id",
    "dry_run_only",
    "stub_only",
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
    "black_box_validated",
    "dhms_release_owner",
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


def run_sql_sandbox_runtime_bridge_first_controlled_release_stub() -> dict[str, Any]:
    review_result = run_sql_sandbox_runtime_bridge_first_held_release_review()
    review_records = review_result.get("review_records", [])
    controlled_records = [build_controlled_release_record(record) for record in review_records]
    record_results = [validate_controlled_release_record(record) for record in controlled_records]

    failed_checks = [
        f"{result['controlled_release_input_id']}.{check}"
        for result in record_results
        for check in result["failed_checks"]
    ]
    ready_but_not_released_count = sum(
        1
        for result in record_results
        if result["controlled_release_decision"] == "CONTROLLED_RELEASE_READY_BUT_NOT_RELEASED"
    )
    rejected_controlled_release_count = sum(
        1
        for result in record_results
        if result["controlled_release_decision"] == "CONTROLLED_RELEASE_REJECTED_INPUT"
    )
    future_release_candidate_count = sum(1 for result in record_results if result["future_release_candidate"])
    release_now_count = sum(1 for record in controlled_records if record["controlled_release_trace"]["release_now"])
    bridge_release_allowed_count = sum(
        1 for record in controlled_records if record["controlled_release_trace"]["bridge_release_allowed"]
    )
    sandbox_execution_released_count = sum(
        1 for record in controlled_records if record["controlled_release_trace"]["sandbox_execution_released"]
    )
    execution_requested_count = sum(
        1 for record in controlled_records if record["controlled_release_trace"]["execution_requested"]
    )
    sql_executed_count = sum(1 for record in controlled_records if record["controlled_release_trace"]["sql_executed"])
    sqlite_database_created_count = sum(
        1 for record in controlled_records if record["controlled_release_trace"]["sqlite_database_created"]
    )
    passed_controlled_release_inputs = sum(1 for result in record_results if result["passed"])
    decisions_by_type = dict(
        sorted(Counter(result["controlled_release_decision"] for result in record_results).items())
    )
    reason_codes_by_type = dict(
        sorted(Counter(result["controlled_release_reason_code"] for result in record_results).items())
    )

    if review_result.get("status") != "PASS":
        failed_checks.append("held_release_review_precondition_not_pass")
    if ready_but_not_released_count != 1:
        failed_checks.append("ready_but_not_released_count_not_one")
    if future_release_candidate_count != 1:
        failed_checks.append("future_release_candidate_count_not_one")
    if rejected_controlled_release_count != 6:
        failed_checks.append("rejected_controlled_release_count_not_six")

    status = "PASS" if not failed_checks and passed_controlled_release_inputs == len(controlled_records) else "FAIL"

    return {
        "validation": "sql_sandbox_runtime_bridge_first_controlled_release_stub_v0_5_11",
        "status": status,
        "total_controlled_release_inputs": len(controlled_records),
        "passed_controlled_release_inputs": passed_controlled_release_inputs,
        "ready_but_not_released_count": ready_but_not_released_count,
        "rejected_controlled_release_count": rejected_controlled_release_count,
        "future_release_candidate_count": future_release_candidate_count,
        "controlled_release_decisions_by_type": decisions_by_type,
        "controlled_release_reason_codes_by_type": reason_codes_by_type,
        "release_now_count": release_now_count,
        "bridge_release_allowed_count": bridge_release_allowed_count,
        "sandbox_execution_released_count": sandbox_execution_released_count,
        "execution_requested_count": execution_requested_count,
        "sql_executed_count": sql_executed_count,
        "sqlite_database_created_count": sqlite_database_created_count,
        "failed_checks": failed_checks,
        "controlled_release_records": controlled_records,
        "record_results": record_results,
        "held_release_review_status": review_result.get("status"),
        "held_release_review_final_verdict": review_result.get("final_verdict"),
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
            "READY_FOR_V0_5_12_SQL_SANDBOX_RUNTIME_BRIDGE_ACTUAL_RELEASE_AUTHORIZATION_REVIEW"
            if status == "PASS"
            else "NEEDS_SQL_SANDBOX_RUNTIME_BRIDGE_CONTROLLED_RELEASE_STUB_FIX"
        ),
    }


def build_controlled_release_record(review_record: dict[str, Any]) -> dict[str, Any]:
    controlled_input = build_controlled_release_input(review_record)
    decision = build_controlled_release_decision(controlled_input)
    planned_request = build_planned_release_request(controlled_input, decision)
    trace = build_controlled_release_trace(controlled_input, decision, planned_request)
    return {
        "controlled_release_input": controlled_input,
        "controlled_release_decision": decision,
        "planned_release_request": planned_request,
        "controlled_release_trace": trace,
    }


def build_controlled_release_input(review_record: dict[str, Any]) -> dict[str, Any]:
    review_input = review_record["review_input"]
    review_decision = review_record["review_decision"]
    bridge_input_id = review_input["bridge_input_id"]
    suffix = bridge_input_id.removeprefix("bridge_")
    return {
        "controlled_release_input_id": f"controlled_release_input_{bridge_input_id}",
        "review_input_id": review_input["review_input_id"],
        "review_decision_id": review_decision["review_decision_id"],
        "bridge_input_id": bridge_input_id,
        "bridge_eligibility_id": review_input["bridge_eligibility_id"],
        "bridge_authorization_id": review_input["bridge_authorization_id"],
        "sandbox_request_id": review_input["sandbox_request_id"],
        "runtime_decision_id": f"runtime_decision_{suffix}",
        "gate_id": f"gate_{suffix}",
        "tool_type": review_input["tool_type"],
        "runtime_decision": review_input["runtime_decision"],
        "gate_result": review_input["gate_result"],
        "bridge_result": review_input["bridge_result"],
        "review_decision": review_decision["review_decision"],
        "sql_text": review_input["sql_text"],
        "allowlist_matched": review_input["allowlist_matched"],
        "select_only_candidate": review_input["select_only_candidate"],
        "mutation_risk": review_input["mutation_risk"],
        "previous_execution_detected": False,
        "black_box_mode": True,
    }


def build_controlled_release_decision(controlled_input: dict[str, Any]) -> dict[str, Any]:
    ready = is_controlled_release_candidate(controlled_input)
    if ready:
        controlled_decision = "CONTROLLED_RELEASE_READY_BUT_NOT_RELEASED"
        reason_code = "ALLOWLISTED_SELECT_READY_FOR_FUTURE_CONTROLLED_SANDBOX_RELEASE"
        future_release_candidate = True
        future_release_allowed_conditionally = True
    elif controlled_input.get("review_decision") == "REVIEW_REJECTED_INPUT":
        controlled_decision = "CONTROLLED_RELEASE_REJECTED_INPUT"
        reason_code = reason_code_for_rejected_input(controlled_input)
        future_release_candidate = False
        future_release_allowed_conditionally = False
    else:
        controlled_decision = "CONTROLLED_RELEASE_FAIL_CLOSED"
        reason_code = "FAIL_CLOSED_INVALID_CONTROLLED_RELEASE_INPUT"
        future_release_candidate = False
        future_release_allowed_conditionally = False

    return {
        "controlled_release_decision_id": (
            f"controlled_release_decision_{controlled_input['controlled_release_input_id']}"
        ),
        "controlled_release_input_id": controlled_input["controlled_release_input_id"],
        "controlled_release_decision": controlled_decision,
        "controlled_release_reason_code": reason_code,
        "future_release_candidate": future_release_candidate,
        "future_release_allowed_conditionally": future_release_allowed_conditionally,
        "requires_explicit_next_phase": True,
        "release_now": False,
        "bridge_release_allowed": False,
        "sandbox_execution_released": False,
        "execution_requested": False,
        "dhms_release_owner": True,
    }


def is_controlled_release_candidate(controlled_input: dict[str, Any]) -> bool:
    return (
        controlled_input.get("tool_type") == "SQL"
        and controlled_input.get("runtime_decision") == "SANDBOX"
        and controlled_input.get("gate_result") == "HELD_FOR_SANDBOX_BRIDGE"
        and controlled_input.get("bridge_result") == "ELIGIBLE_HELD_FOR_FUTURE_SANDBOX_EXECUTION"
        and controlled_input.get("review_decision") == "REVIEW_READY_BUT_NOT_RELEASED"
        and controlled_input.get("sql_text") == ALLOWLISTED_SELECT
        and controlled_input.get("allowlist_matched") is True
        and controlled_input.get("select_only_candidate") is True
        and controlled_input.get("mutation_risk") is False
        and controlled_input.get("previous_execution_detected") is False
        and controlled_input.get("black_box_mode") is True
    )


def reason_code_for_rejected_input(controlled_input: dict[str, Any]) -> str:
    bridge_result = controlled_input.get("bridge_result")
    bridge_to_reason = {
        "REJECTED_MUTATION_SQL": "REJECTED_MUTATION_SQL",
        "REJECTED_BLOCK_DECISION": "REJECTED_BLOCK_DECISION",
        "REJECTED_NON_SQL_TOOL": "REJECTED_NON_SQL_TOOL",
        "REJECTED_UNKNOWN_OR_MALFORMED_SQL": "REJECTED_UNKNOWN_OR_MALFORMED_SQL",
        "REJECTED_MULTI_STATEMENT_SQL": "REJECTED_MULTI_STATEMENT_SQL",
        "REJECTED_COMMENT_HIDDEN_MUTATION": "REJECTED_COMMENT_HIDDEN_MUTATION",
    }
    return bridge_to_reason.get(str(bridge_result), "FAIL_CLOSED_INVALID_CONTROLLED_RELEASE_INPUT")


def build_planned_release_request(
    controlled_input: dict[str, Any],
    decision: dict[str, Any],
) -> dict[str, Any]:
    return {
        "planned_release_request_id": f"planned_release_request_{controlled_input['controlled_release_input_id']}",
        "controlled_release_decision_id": decision["controlled_release_decision_id"],
        "sql_text": controlled_input["sql_text"],
        "allowlisted_select": controlled_input["sql_text"] == ALLOWLISTED_SELECT,
        "temporary_database_required": True,
        "synthetic_data_only": True,
        "mutation_detection_required": True,
        "teardown_required": True,
        "delete_verification_required": True,
        "real_database": False,
        "network_database": False,
        "credential_used": False,
        "production_data_used": False,
        "sandbox_execution_requested": False,
        "release_now": False,
        "sql_executed": False,
        "sqlite_database_created": False,
    }


def build_controlled_release_trace(
    controlled_input: dict[str, Any],
    decision: dict[str, Any],
    planned_request: dict[str, Any],
) -> dict[str, Any]:
    return {
        "controlled_release_trace_id": f"controlled_release_trace_{controlled_input['controlled_release_input_id']}",
        "controlled_release_input_id": controlled_input["controlled_release_input_id"],
        "controlled_release_decision_id": decision["controlled_release_decision_id"],
        "planned_release_request_id": planned_request["planned_release_request_id"],
        "dry_run_only": True,
        "stub_only": True,
        "release_now": False,
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
        "dhms_release_owner": True,
    }


def validate_controlled_release_record(record: dict[str, Any]) -> dict[str, Any]:
    failed_checks: list[str] = []
    controlled_input = record.get("controlled_release_input", {})
    decision = record.get("controlled_release_decision", {})
    planned_request = record.get("planned_release_request", {})
    trace = record.get("controlled_release_trace", {})

    require_fields(
        "controlled_release_input",
        controlled_input,
        REQUIRED_CONTROLLED_RELEASE_INPUT_FIELDS,
        failed_checks,
    )
    require_fields(
        "controlled_release_decision",
        decision,
        REQUIRED_CONTROLLED_RELEASE_DECISION_FIELDS,
        failed_checks,
    )
    require_fields(
        "planned_release_request",
        planned_request,
        REQUIRED_PLANNED_RELEASE_REQUEST_FIELDS,
        failed_checks,
    )
    require_fields(
        "controlled_release_trace",
        trace,
        REQUIRED_CONTROLLED_RELEASE_TRACE_FIELDS,
        failed_checks,
    )

    controlled_decision = decision.get("controlled_release_decision")
    reason_code = decision.get("controlled_release_reason_code")
    if controlled_decision not in ALLOWED_CONTROLLED_RELEASE_DECISIONS:
        failed_checks.append("unknown_controlled_release_decision")
    if reason_code not in ALLOWED_CONTROLLED_RELEASE_REASON_CODES:
        failed_checks.append("unknown_controlled_release_reason_code")
    if decision.get("requires_explicit_next_phase") is not True:
        failed_checks.append("requires_explicit_next_phase_not_true")
    if decision.get("dhms_release_owner") is not True:
        failed_checks.append("decision_not_dhms_release_owner")
    if trace.get("dhms_release_owner") is not True:
        failed_checks.append("trace_not_dhms_release_owner")
    if trace.get("black_box_validated") is not True:
        failed_checks.append("trace_black_box_not_true")
    if trace.get("dry_run_only") is not True:
        failed_checks.append("trace_dry_run_only_not_true")
    if trace.get("stub_only") is not True:
        failed_checks.append("trace_stub_only_not_true")

    for flag in sorted(NON_EXECUTION_TRACE_FLAGS):
        if trace.get(flag) is not False:
            failed_checks.append(f"trace_{flag}_not_false")
    for field in ("release_now", "bridge_release_allowed", "sandbox_execution_released", "execution_requested"):
        if decision.get(field) is not False:
            failed_checks.append(f"decision_{field}_not_false")
    for field in (
        "sandbox_execution_requested",
        "release_now",
        "sql_executed",
        "sqlite_database_created",
        "real_database",
        "network_database",
        "credential_used",
        "production_data_used",
    ):
        if planned_request.get(field) is not False:
            failed_checks.append(f"planned_request_{field}_not_false")
    for field in (
        "temporary_database_required",
        "synthetic_data_only",
        "mutation_detection_required",
        "teardown_required",
        "delete_verification_required",
    ):
        if planned_request.get(field) is not True:
            failed_checks.append(f"planned_request_{field}_not_true")

    ready_candidate = is_controlled_release_candidate(controlled_input)
    if ready_candidate:
        if controlled_decision != "CONTROLLED_RELEASE_READY_BUT_NOT_RELEASED":
            failed_checks.append("ready_candidate_decision_mismatch")
        if reason_code != "ALLOWLISTED_SELECT_READY_FOR_FUTURE_CONTROLLED_SANDBOX_RELEASE":
            failed_checks.append("ready_candidate_reason_mismatch")
        if decision.get("future_release_candidate") is not True:
            failed_checks.append("ready_candidate_future_release_candidate_not_true")
        if decision.get("future_release_allowed_conditionally") is not True:
            failed_checks.append("ready_candidate_conditionally_allowed_not_true")
        if planned_request.get("allowlisted_select") is not True:
            failed_checks.append("ready_candidate_not_allowlisted")
    else:
        if controlled_input.get("review_decision") == "REVIEW_REJECTED_INPUT":
            if controlled_decision != "CONTROLLED_RELEASE_REJECTED_INPUT":
                failed_checks.append("rejected_input_decision_mismatch")
            expected_reason = reason_code_for_rejected_input(controlled_input)
            if reason_code != expected_reason:
                failed_checks.append(f"rejected_input_reason_expected_{expected_reason}")
        else:
            if controlled_decision != "CONTROLLED_RELEASE_FAIL_CLOSED":
                failed_checks.append("invalid_input_not_fail_closed")
        if decision.get("future_release_candidate") is not False:
            failed_checks.append("rejected_or_invalid_future_release_candidate_not_false")
        if decision.get("future_release_allowed_conditionally") is not False:
            failed_checks.append("rejected_or_invalid_conditionally_allowed_not_false")

    return {
        "controlled_release_input_id": controlled_input.get("controlled_release_input_id"),
        "bridge_input_id": controlled_input.get("bridge_input_id"),
        "controlled_release_decision": controlled_decision,
        "controlled_release_reason_code": reason_code,
        "future_release_candidate": decision.get("future_release_candidate"),
        "future_release_allowed_conditionally": decision.get("future_release_allowed_conditionally"),
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
