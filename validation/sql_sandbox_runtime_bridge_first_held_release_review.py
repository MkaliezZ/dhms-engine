#!/usr/bin/env python3
"""Deterministic held-release review for the SQL sandbox runtime bridge.

This module reviews the single eligible-but-held SELECT-only bridge candidate
from v0.5.8. It does not release execution, execute SQL, create SQLite
databases, call SQL sandbox execution, invoke OpenClaw, call providers, use
SDKs, or run production checker/runner logic.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from sql_sandbox_runtime_bridge_stub import (
    ALLOWLISTED_SELECT,
    build_bridge_inputs,
    build_bridge_record,
    run_sql_sandbox_runtime_bridge_stub,
)


ALLOWED_REVIEW_DECISIONS = {
    "REVIEW_READY_BUT_NOT_RELEASED",
    "REVIEW_REJECTED_INPUT",
    "REVIEW_FAIL_CLOSED",
}
ALLOWED_REVIEW_REASON_CODES = {
    "ALLOWLISTED_SELECT_HELD_FOR_FUTURE_RELEASE_PLAN",
    "REJECTED_MUTATION_SQL",
    "REJECTED_BLOCK_DECISION",
    "REJECTED_NON_SQL_TOOL",
    "REJECTED_UNKNOWN_OR_MALFORMED_SQL",
    "REJECTED_MULTI_STATEMENT_SQL",
    "REJECTED_COMMENT_HIDDEN_MUTATION",
    "FAIL_CLOSED_INVALID_REVIEW_INPUT",
}
BRIDGE_RESULT_TO_REVIEW_REASON = {
    "REJECTED_MUTATION_SQL": "REJECTED_MUTATION_SQL",
    "REJECTED_BLOCK_DECISION": "REJECTED_BLOCK_DECISION",
    "REJECTED_NON_SQL_TOOL": "REJECTED_NON_SQL_TOOL",
    "REJECTED_UNKNOWN_OR_MALFORMED_SQL": "REJECTED_UNKNOWN_OR_MALFORMED_SQL",
    "REJECTED_MULTI_STATEMENT_SQL": "REJECTED_MULTI_STATEMENT_SQL",
    "REJECTED_COMMENT_HIDDEN_MUTATION": "REJECTED_COMMENT_HIDDEN_MUTATION",
}

REQUIRED_REVIEW_INPUT_FIELDS = {
    "review_input_id",
    "bridge_input_id",
    "bridge_eligibility_id",
    "bridge_authorization_id",
    "sandbox_request_id",
    "tool_type",
    "runtime_decision",
    "gate_result",
    "bridge_result",
    "authorization_decision",
    "sql_text",
    "allowlist_matched",
    "select_only_candidate",
    "mutation_risk",
    "bridge_release_allowed",
    "sandbox_execution_released",
    "execution_requested",
    "sql_executed",
    "sqlite_database_created",
}
REQUIRED_REVIEW_DECISION_FIELDS = {
    "review_decision_id",
    "review_input_id",
    "review_decision",
    "review_reason_code",
    "future_release_candidate",
    "future_release_plan_required",
    "release_now",
    "bridge_release_allowed",
    "sandbox_execution_released",
    "dhms_release_owner",
}
REQUIRED_REVIEW_TRACE_FIELDS = {
    "review_trace_id",
    "review_input_id",
    "review_decision_id",
    "bridge_input_id",
    "tool_type",
    "runtime_decision",
    "gate_result",
    "bridge_result",
    "review_decision",
    "dry_run_only",
    "release_now",
    "future_release_candidate",
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

NON_EXECUTION_REVIEW_FLAGS = {
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


def run_sql_sandbox_runtime_bridge_first_held_release_review() -> dict[str, Any]:
    bridge_stub_result = run_sql_sandbox_runtime_bridge_stub()
    bridge_records = build_review_source_bridge_records(bridge_stub_result)
    review_records = [build_review_record(record) for record in bridge_records]
    record_results = [validate_review_record(record) for record in review_records]

    failed_checks = [
        f"{result['review_input_id']}.{check}"
        for result in record_results
        for check in result["failed_checks"]
    ]
    eligible_held_candidate_count = sum(1 for result in record_results if result["future_release_candidate"])
    ready_but_not_released_count = sum(
        1 for result in record_results if result["review_decision"] == "REVIEW_READY_BUT_NOT_RELEASED"
    )
    rejected_review_count = sum(
        1 for result in record_results if result["review_decision"] == "REVIEW_REJECTED_INPUT"
    )
    release_now_count = sum(1 for record in review_records if record["review_decision"]["release_now"])
    bridge_release_allowed_count = sum(
        1 for record in review_records if record["review_trace"]["bridge_release_allowed"]
    )
    sandbox_execution_released_count = sum(
        1 for record in review_records if record["review_trace"]["sandbox_execution_released"]
    )
    sql_executed_count = sum(1 for record in review_records if record["review_trace"]["sql_executed"])
    sqlite_database_created_count = sum(
        1 for record in review_records if record["review_trace"]["sqlite_database_created"]
    )
    passed_review_inputs = sum(1 for result in record_results if result["passed"])
    review_decisions_by_type = dict(
        sorted(Counter(result["review_decision"] for result in record_results).items())
    )
    review_reason_codes_by_type = dict(
        sorted(Counter(result["review_reason_code"] for result in record_results).items())
    )

    if bridge_stub_result.get("status") != "PASS":
        failed_checks.append("bridge_stub_precondition_not_pass")
    if eligible_held_candidate_count != 1:
        failed_checks.append("eligible_held_candidate_count_not_one")
    if ready_but_not_released_count != 1:
        failed_checks.append("ready_but_not_released_count_not_one")
    if rejected_review_count != 6:
        failed_checks.append("rejected_review_count_not_six")

    status = "PASS" if not failed_checks and passed_review_inputs == len(review_records) else "FAIL"

    return {
        "validation": "sql_sandbox_runtime_bridge_first_held_release_review_v0_5_9",
        "status": status,
        "total_review_inputs": len(review_records),
        "passed_review_inputs": passed_review_inputs,
        "eligible_held_candidate_count": eligible_held_candidate_count,
        "ready_but_not_released_count": ready_but_not_released_count,
        "rejected_review_count": rejected_review_count,
        "review_decisions_by_type": review_decisions_by_type,
        "review_reason_codes_by_type": review_reason_codes_by_type,
        "release_now_count": release_now_count,
        "bridge_release_allowed_count": bridge_release_allowed_count,
        "sandbox_execution_released_count": sandbox_execution_released_count,
        "sql_executed_count": sql_executed_count,
        "sqlite_database_created_count": sqlite_database_created_count,
        "failed_checks": failed_checks,
        "review_records": review_records,
        "record_results": record_results,
        "bridge_stub_status": bridge_stub_result.get("status"),
        "bridge_stub_final_verdict": bridge_stub_result.get("final_verdict"),
        "real_bridge_execution_implemented": False,
        "execution_gate_opened": False,
        "release_now": False,
        "bridge_release_allowed": False,
        "sandbox_execution_released": False,
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
            "READY_FOR_V0_5_10_SQL_SANDBOX_RUNTIME_BRIDGE_FIRST_CONTROLLED_RELEASE_PLAN"
            if status == "PASS"
            else "NEEDS_SQL_SANDBOX_RUNTIME_BRIDGE_HELD_RELEASE_REVIEW_FIX"
        ),
    }


def build_review_source_bridge_records(bridge_stub_result: dict[str, Any]) -> list[dict[str, Any]]:
    records = bridge_stub_result.get("bridge_records")
    if isinstance(records, list) and records:
        return records
    return [build_bridge_record(bridge_input) for bridge_input in build_bridge_inputs()]


def build_review_record(bridge_record: dict[str, Any]) -> dict[str, Any]:
    review_input = build_review_input(bridge_record)
    review_decision = build_review_decision(review_input)
    review_trace = build_review_trace(review_input, review_decision)
    return {
        "review_input": review_input,
        "review_decision": review_decision,
        "review_trace": review_trace,
    }


def build_review_input(bridge_record: dict[str, Any]) -> dict[str, Any]:
    bridge_input = bridge_record["bridge_input"]
    eligibility = bridge_record["eligibility_result"]
    authorization = bridge_record["authorization_stub"]
    sandbox_request = bridge_record["sandbox_request_stub"]
    bridge_trace = bridge_record["bridge_trace"]
    bridge_input_id = bridge_input["bridge_input_id"]
    return {
        "review_input_id": f"review_input_{bridge_input_id}",
        "bridge_input_id": bridge_input_id,
        "bridge_eligibility_id": eligibility["bridge_eligibility_id"],
        "bridge_authorization_id": authorization["bridge_authorization_id"],
        "sandbox_request_id": sandbox_request["sandbox_request_id"],
        "tool_type": bridge_input["tool_type"],
        "runtime_decision": bridge_input["runtime_decision"],
        "gate_result": bridge_input["gate_result"],
        "bridge_result": eligibility["bridge_result"],
        "authorization_decision": authorization["authorization_decision"],
        "sql_text": bridge_input.get("sql_text", ""),
        "allowlist_matched": eligibility["allowlist_matched"],
        "select_only_candidate": bridge_input["select_only_candidate"],
        "mutation_risk": bridge_input["mutation_risk"],
        "bridge_release_allowed": authorization["bridge_release_allowed"],
        "sandbox_execution_released": bridge_trace["sandbox_execution_released"],
        "execution_requested": sandbox_request["execution_requested"],
        "sql_executed": bridge_trace["sql_executed"],
        "sqlite_database_created": bridge_trace["sqlite_database_created"],
    }


def build_review_decision(review_input: dict[str, Any]) -> dict[str, Any]:
    eligible = is_ready_but_not_released_candidate(review_input)
    if eligible:
        review_decision = "REVIEW_READY_BUT_NOT_RELEASED"
        review_reason_code = "ALLOWLISTED_SELECT_HELD_FOR_FUTURE_RELEASE_PLAN"
        future_release_candidate = True
    elif review_input.get("bridge_result") in BRIDGE_RESULT_TO_REVIEW_REASON:
        review_decision = "REVIEW_REJECTED_INPUT"
        review_reason_code = BRIDGE_RESULT_TO_REVIEW_REASON[review_input["bridge_result"]]
        future_release_candidate = False
    else:
        review_decision = "REVIEW_FAIL_CLOSED"
        review_reason_code = "FAIL_CLOSED_INVALID_REVIEW_INPUT"
        future_release_candidate = False

    return {
        "review_decision_id": f"review_decision_{review_input['review_input_id']}",
        "review_input_id": review_input["review_input_id"],
        "review_decision": review_decision,
        "review_reason_code": review_reason_code,
        "future_release_candidate": future_release_candidate,
        "future_release_plan_required": True,
        "release_now": False,
        "bridge_release_allowed": False,
        "sandbox_execution_released": False,
        "dhms_release_owner": True,
    }


def is_ready_but_not_released_candidate(review_input: dict[str, Any]) -> bool:
    return (
        review_input.get("tool_type") == "SQL"
        and review_input.get("runtime_decision") == "SANDBOX"
        and review_input.get("gate_result") == "HELD_FOR_SANDBOX_BRIDGE"
        and review_input.get("bridge_result") == "ELIGIBLE_HELD_FOR_FUTURE_SANDBOX_EXECUTION"
        and review_input.get("authorization_decision") == "STUB_ELIGIBLE_BUT_NOT_RELEASED"
        and review_input.get("sql_text") == ALLOWLISTED_SELECT
        and review_input.get("allowlist_matched") is True
        and review_input.get("select_only_candidate") is True
        and review_input.get("mutation_risk") is False
        and review_input.get("bridge_release_allowed") is False
        and review_input.get("sandbox_execution_released") is False
        and review_input.get("execution_requested") is False
        and review_input.get("sql_executed") is False
        and review_input.get("sqlite_database_created") is False
    )


def build_review_trace(
    review_input: dict[str, Any],
    review_decision: dict[str, Any],
) -> dict[str, Any]:
    return {
        "review_trace_id": f"review_trace_{review_input['review_input_id']}",
        "review_input_id": review_input["review_input_id"],
        "review_decision_id": review_decision["review_decision_id"],
        "bridge_input_id": review_input["bridge_input_id"],
        "tool_type": review_input["tool_type"],
        "runtime_decision": review_input["runtime_decision"],
        "gate_result": review_input["gate_result"],
        "bridge_result": review_input["bridge_result"],
        "review_decision": review_decision["review_decision"],
        "dry_run_only": True,
        "release_now": False,
        "future_release_candidate": review_decision["future_release_candidate"],
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


def validate_review_record(record: dict[str, Any]) -> dict[str, Any]:
    failed_checks: list[str] = []
    review_input = record.get("review_input", {})
    review_decision = record.get("review_decision", {})
    review_trace = record.get("review_trace", {})

    require_fields("review_input", review_input, REQUIRED_REVIEW_INPUT_FIELDS, failed_checks)
    require_fields("review_decision", review_decision, REQUIRED_REVIEW_DECISION_FIELDS, failed_checks)
    require_fields("review_trace", review_trace, REQUIRED_REVIEW_TRACE_FIELDS, failed_checks)

    decision = review_decision.get("review_decision")
    reason_code = review_decision.get("review_reason_code")
    if decision not in ALLOWED_REVIEW_DECISIONS:
        failed_checks.append("unknown_review_decision")
    if reason_code not in ALLOWED_REVIEW_REASON_CODES:
        failed_checks.append("unknown_review_reason_code")
    if review_decision.get("future_release_plan_required") is not True:
        failed_checks.append("future_release_plan_required_not_true")
    if review_decision.get("dhms_release_owner") is not True:
        failed_checks.append("decision_not_dhms_release_owner")
    if review_trace.get("dhms_release_owner") is not True:
        failed_checks.append("trace_not_dhms_release_owner")
    if review_trace.get("black_box_validated") is not True:
        failed_checks.append("trace_black_box_not_true")
    if review_trace.get("dry_run_only") is not True:
        failed_checks.append("trace_dry_run_only_not_true")

    for flag in sorted(NON_EXECUTION_REVIEW_FLAGS):
        if review_trace.get(flag) is not False:
            failed_checks.append(f"trace_{flag}_not_false")
    for field in (
        "bridge_release_allowed",
        "sandbox_execution_released",
        "execution_requested",
        "sql_executed",
        "sqlite_database_created",
    ):
        if review_input.get(field) is not False:
            failed_checks.append(f"review_input_{field}_not_false")
    for field in ("release_now", "bridge_release_allowed", "sandbox_execution_released"):
        if review_decision.get(field) is not False:
            failed_checks.append(f"review_decision_{field}_not_false")

    ready_candidate = is_ready_but_not_released_candidate(review_input)
    if ready_candidate:
        if decision != "REVIEW_READY_BUT_NOT_RELEASED":
            failed_checks.append("eligible_candidate_not_ready_but_not_released")
        if reason_code != "ALLOWLISTED_SELECT_HELD_FOR_FUTURE_RELEASE_PLAN":
            failed_checks.append("eligible_candidate_reason_mismatch")
        if review_decision.get("future_release_candidate") is not True:
            failed_checks.append("eligible_candidate_not_future_release_candidate")
    else:
        if review_input.get("bridge_result") in BRIDGE_RESULT_TO_REVIEW_REASON:
            if decision != "REVIEW_REJECTED_INPUT":
                failed_checks.append("rejected_input_review_decision_mismatch")
            expected_reason = BRIDGE_RESULT_TO_REVIEW_REASON[review_input["bridge_result"]]
            if reason_code != expected_reason:
                failed_checks.append(f"rejected_input_reason_expected_{expected_reason}")
        else:
            if decision != "REVIEW_FAIL_CLOSED":
                failed_checks.append("invalid_input_not_fail_closed")
        if review_decision.get("future_release_candidate") is not False:
            failed_checks.append("rejected_or_invalid_input_future_release_candidate")

    return {
        "review_input_id": review_input.get("review_input_id"),
        "bridge_input_id": review_input.get("bridge_input_id"),
        "bridge_result": review_input.get("bridge_result"),
        "review_decision": decision,
        "review_reason_code": reason_code,
        "future_release_candidate": review_decision.get("future_release_candidate"),
        "release_now": review_trace.get("release_now"),
        "bridge_release_allowed": review_trace.get("bridge_release_allowed"),
        "sandbox_execution_released": review_trace.get("sandbox_execution_released"),
        "sql_executed": review_trace.get("sql_executed"),
        "sqlite_database_created": review_trace.get("sqlite_database_created"),
        "passed": not failed_checks,
        "failed_checks": failed_checks,
    }


def require_fields(prefix: str, payload: dict[str, Any], required_fields: set[str], failed_checks: list[str]) -> None:
    missing = sorted(required_fields.difference(payload))
    for field in missing:
        failed_checks.append(f"{prefix}.missing_{field}")
