#!/usr/bin/env python3
"""Deterministic SQL sandbox runtime bridge stub for v0.5.8.

This module evaluates planned bridge inputs and produces non-executing bridge
authorization records, planned sandbox request stubs, and bridge traces. It
does not execute SQL, create SQLite databases, call SQL sandbox execution,
open runtime gates, invoke OpenClaw, call providers, use SDKs, or run
production checker/runner logic.
"""

from __future__ import annotations

from collections import Counter
from typing import Any


ALLOWLISTED_SELECT = "SELECT id, label, status FROM toy_accounts ORDER BY id;"
SQL_MUTATION_KEYWORDS = ("update", "delete", "insert", "drop", "alter", "replace", "truncate", "create")

ALLOWED_BRIDGE_RESULTS = {
    "ELIGIBLE_HELD_FOR_FUTURE_SANDBOX_EXECUTION",
    "REJECTED_MUTATION_SQL",
    "REJECTED_BLOCK_DECISION",
    "REJECTED_NON_SQL_TOOL",
    "REJECTED_UNKNOWN_OR_MALFORMED_SQL",
    "REJECTED_MULTI_STATEMENT_SQL",
    "REJECTED_COMMENT_HIDDEN_MUTATION",
    "FAIL_CLOSED_INVALID_BRIDGE_INPUT",
}
ALLOWED_AUTHORIZATION_DECISIONS = {"STUB_ELIGIBLE_BUT_NOT_RELEASED", "REJECT_BRIDGE_INPUT", "FAIL_CLOSED"}

REQUIRED_BRIDGE_INPUT_FIELDS = {
    "bridge_input_id",
    "dry_run_request_id",
    "request_id",
    "proposal_id",
    "runtime_decision_id",
    "gate_id",
    "tool_type",
    "runtime_decision",
    "gate_result",
    "sql_text",
    "select_only_candidate",
    "mutation_risk",
    "sandbox_required",
    "sandbox_bridge_required",
    "dhms_final_decision",
    "dhms_gate_owner",
    "black_box_mode",
    "previous_execution_detected",
}
REQUIRED_ELIGIBILITY_FIELDS = {
    "bridge_eligibility_id",
    "bridge_input_id",
    "eligible_for_bridge",
    "bridge_result",
    "bridge_reason_code",
    "fail_closed",
    "required_allowlist_match",
    "allowlist_matched",
    "mutation_rejected",
    "multi_statement_rejected",
    "comment_hidden_mutation_rejected",
    "non_sql_rejected",
    "dhms_bridge_owner",
}
REQUIRED_AUTHORIZATION_FIELDS = {
    "bridge_authorization_id",
    "bridge_eligibility_id",
    "authorization_decision",
    "authorization_reason_code",
    "bridge_release_allowed",
    "sandbox_mode_required",
    "temporary_database_required",
    "synthetic_data_only",
    "mutation_detection_required",
    "teardown_required",
    "delete_verification_required",
    "execution_requested",
}
REQUIRED_SANDBOX_REQUEST_FIELDS = {
    "sandbox_request_id",
    "bridge_authorization_id",
    "sql_text",
    "allowlisted_select",
    "temporary_database",
    "real_database",
    "network_database",
    "credential_used",
    "production_data_used",
    "execution_requested",
    "sandbox_created",
    "sql_executed",
}
REQUIRED_BRIDGE_TRACE_FIELDS = {
    "bridge_trace_id",
    "bridge_input_id",
    "bridge_eligibility_id",
    "bridge_authorization_id",
    "sandbox_request_id",
    "dry_run_only",
    "bridge_implemented",
    "sandbox_execution_released",
    "execution_release_allowed",
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
    "dhms_bridge_owner",
}

NON_EXECUTION_TRACE_FLAGS = {
    "bridge_implemented",
    "sandbox_execution_released",
    "execution_release_allowed",
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


def run_sql_sandbox_runtime_bridge_stub() -> dict[str, Any]:
    bridge_inputs = build_bridge_inputs()
    records = [build_bridge_record(bridge_input) for bridge_input in bridge_inputs]
    record_results = [validate_bridge_record(record) for record in records]

    failed_checks = [
        f"{result['bridge_input_id']}.{check}"
        for result in record_results
        for check in result["failed_checks"]
    ]
    eligible_count = sum(1 for result in record_results if result["eligible_for_bridge"])
    rejected_count = sum(1 for result in record_results if not result["eligible_for_bridge"])
    bridge_results_by_type = dict(sorted(Counter(result["bridge_result"] for result in record_results).items()))
    authorization_decisions_by_type = dict(
        sorted(Counter(result["authorization_decision"] for result in record_results).items())
    )
    bridge_release_allowed_count = sum(
        1 for record in records if record["authorization_stub"]["bridge_release_allowed"]
    )
    sandbox_execution_released_count = sum(
        1 for record in records if record["bridge_trace"]["sandbox_execution_released"]
    )
    sql_executed_count = sum(1 for record in records if record["bridge_trace"]["sql_executed"])
    sqlite_database_created_count = sum(1 for record in records if record["bridge_trace"]["sqlite_database_created"])
    passed_bridge_inputs = sum(1 for result in record_results if result["passed"])
    status = "PASS" if not failed_checks and passed_bridge_inputs == len(records) else "FAIL"

    return {
        "validation": "sql_sandbox_runtime_bridge_stub_v0_5_8",
        "status": status,
        "total_bridge_inputs": len(records),
        "passed_bridge_inputs": passed_bridge_inputs,
        "eligible_count": eligible_count,
        "rejected_count": rejected_count,
        "bridge_results_by_type": bridge_results_by_type,
        "authorization_decisions_by_type": authorization_decisions_by_type,
        "bridge_release_allowed_count": bridge_release_allowed_count,
        "sandbox_execution_released_count": sandbox_execution_released_count,
        "sql_executed_count": sql_executed_count,
        "sqlite_database_created_count": sqlite_database_created_count,
        "failed_checks": failed_checks,
        "bridge_records": records,
        "record_results": record_results,
        "runtime_wrapper_executed": False,
        "tool_execution_invoked": False,
        "sql_execution_invoked_from_runtime_path": False,
        "sqlite_database_created_from_runtime_path": False,
        "sql_sandbox_execution_invoked_from_runtime_path": False,
        "execution_gate_opened": False,
        "execution_release_allowed": False,
        "bridge_release_allowed": False,
        "sandbox_execution_released": False,
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
            "READY_FOR_V0_5_9_SQL_SANDBOX_RUNTIME_BRIDGE_FIRST_HELD_RELEASE_REVIEW"
            if status == "PASS"
            else "NEEDS_SQL_SANDBOX_RUNTIME_BRIDGE_STUB_FIX"
        ),
    }


def build_bridge_inputs() -> list[dict[str, Any]]:
    return [
        bridge_input(
            bridge_input_id="bridge_sql_select_only_eligible",
            tool_type="SQL",
            runtime_decision="SANDBOX",
            gate_result="HELD_FOR_SANDBOX_BRIDGE",
            sql_text=ALLOWLISTED_SELECT,
            select_only_candidate=True,
            mutation_risk=False,
            sandbox_required=True,
            sandbox_bridge_required=True,
        ),
        bridge_input(
            bridge_input_id="bridge_sql_mutation_rejected",
            tool_type="SQL",
            runtime_decision="SANDBOX",
            gate_result="HELD_FOR_SANDBOX_BRIDGE",
            sql_text="UPDATE toy_accounts SET status = 'deleted' WHERE id = 1;",
            select_only_candidate=False,
            mutation_risk=True,
            sandbox_required=True,
            sandbox_bridge_required=True,
        ),
        bridge_input(
            bridge_input_id="bridge_sql_block_decision_rejected",
            tool_type="SQL",
            runtime_decision="BLOCK",
            gate_result="CLOSED",
            sql_text="DELETE FROM toy_accounts WHERE id = 1;",
            select_only_candidate=False,
            mutation_risk=True,
            sandbox_required=False,
            sandbox_bridge_required=False,
        ),
        bridge_input(
            bridge_input_id="bridge_openclaw_rejected",
            tool_type="OPENCLAW",
            runtime_decision="BLOCK",
            gate_result="CLOSED",
            sql_text="",
            select_only_candidate=False,
            mutation_risk=False,
            sandbox_required=False,
            sandbox_bridge_required=False,
        ),
        bridge_input(
            bridge_input_id="bridge_sql_unknown_rejected",
            tool_type="SQL",
            runtime_decision="SANDBOX",
            gate_result="HELD_FOR_SANDBOX_BRIDGE",
            sql_text="",
            select_only_candidate=False,
            mutation_risk=False,
            sandbox_required=True,
            sandbox_bridge_required=True,
        ),
        bridge_input(
            bridge_input_id="bridge_sql_multi_statement_rejected",
            tool_type="SQL",
            runtime_decision="SANDBOX",
            gate_result="HELD_FOR_SANDBOX_BRIDGE",
            sql_text="SELECT id FROM toy_accounts; SELECT status FROM toy_accounts;",
            select_only_candidate=True,
            mutation_risk=False,
            sandbox_required=True,
            sandbox_bridge_required=True,
        ),
        bridge_input(
            bridge_input_id="bridge_sql_comment_hidden_mutation_rejected",
            tool_type="SQL",
            runtime_decision="SANDBOX",
            gate_result="HELD_FOR_SANDBOX_BRIDGE",
            sql_text="SELECT id, label, status FROM toy_accounts ORDER BY id; -- then DROP TABLE toy_accounts",
            select_only_candidate=True,
            mutation_risk=False,
            sandbox_required=True,
            sandbox_bridge_required=True,
        ),
    ]


def bridge_input(
    *,
    bridge_input_id: str,
    tool_type: str,
    runtime_decision: str,
    gate_result: str,
    sql_text: str,
    select_only_candidate: bool,
    mutation_risk: bool,
    sandbox_required: bool,
    sandbox_bridge_required: bool,
) -> dict[str, Any]:
    suffix = bridge_input_id.removeprefix("bridge_")
    return {
        "bridge_input_id": bridge_input_id,
        "dry_run_request_id": f"dry_run_{suffix}",
        "request_id": f"req_{suffix}",
        "proposal_id": f"proposal_{suffix}",
        "runtime_decision_id": f"runtime_decision_{suffix}",
        "gate_id": f"gate_{suffix}",
        "tool_type": tool_type,
        "runtime_decision": runtime_decision,
        "gate_result": gate_result,
        "sql_text": sql_text,
        "select_only_candidate": select_only_candidate,
        "mutation_risk": mutation_risk,
        "sandbox_required": sandbox_required,
        "sandbox_bridge_required": sandbox_bridge_required,
        "dhms_final_decision": True,
        "dhms_gate_owner": True,
        "black_box_mode": True,
        "previous_execution_detected": False,
    }


def build_bridge_record(bridge_input_payload: dict[str, Any]) -> dict[str, Any]:
    eligibility = evaluate_bridge_eligibility(bridge_input_payload)
    authorization = build_authorization_stub(eligibility)
    sandbox_request = build_sandbox_request_stub(bridge_input_payload, authorization)
    trace = build_bridge_trace(bridge_input_payload, eligibility, authorization, sandbox_request)
    return {
        "bridge_input": bridge_input_payload,
        "eligibility_result": eligibility,
        "authorization_stub": authorization,
        "sandbox_request_stub": sandbox_request,
        "bridge_trace": trace,
    }


def evaluate_bridge_eligibility(bridge_input_payload: dict[str, Any]) -> dict[str, Any]:
    sql_text = str(bridge_input_payload.get("sql_text", ""))
    normalized_sql = sql_text.strip().lower()
    tool_type = bridge_input_payload.get("tool_type")
    runtime_decision = bridge_input_payload.get("runtime_decision")
    gate_result = bridge_input_payload.get("gate_result")

    allowlist_matched = sql_text.strip() == ALLOWLISTED_SELECT
    required_allowlist_match = True
    mutation_detected = contains_mutation_sql(normalized_sql) or bridge_input_payload.get("mutation_risk") is True
    multi_statement = has_multiple_statements(sql_text)
    comment_hidden_mutation = has_comment_hidden_mutation(sql_text)
    non_sql = tool_type != "SQL"
    unknown_or_malformed = tool_type == "SQL" and not normalized_sql

    if non_sql:
        bridge_result = "REJECTED_NON_SQL_TOOL"
        bridge_reason_code = "non_sql_tool_rejected_before_bridge"
    elif runtime_decision == "BLOCK" or gate_result == "CLOSED":
        bridge_result = "REJECTED_BLOCK_DECISION"
        bridge_reason_code = "block_decision_or_closed_gate_rejected"
    elif comment_hidden_mutation:
        bridge_result = "REJECTED_COMMENT_HIDDEN_MUTATION"
        bridge_reason_code = "comment_hidden_mutation_rejected"
    elif mutation_detected:
        bridge_result = "REJECTED_MUTATION_SQL"
        bridge_reason_code = "mutation_sql_rejected_before_bridge"
    elif unknown_or_malformed:
        bridge_result = "REJECTED_UNKNOWN_OR_MALFORMED_SQL"
        bridge_reason_code = "unknown_or_malformed_sql_rejected"
    elif multi_statement:
        bridge_result = "REJECTED_MULTI_STATEMENT_SQL"
        bridge_reason_code = "multi_statement_sql_rejected"
    elif not base_eligibility_fields_ok(bridge_input_payload) or not allowlist_matched:
        bridge_result = "FAIL_CLOSED_INVALID_BRIDGE_INPUT"
        bridge_reason_code = "bridge_input_failed_eligibility_or_allowlist"
    else:
        bridge_result = "ELIGIBLE_HELD_FOR_FUTURE_SANDBOX_EXECUTION"
        bridge_reason_code = "allowlisted_select_eligible_but_not_released"

    eligible = bridge_result == "ELIGIBLE_HELD_FOR_FUTURE_SANDBOX_EXECUTION"
    return {
        "bridge_eligibility_id": f"eligibility_{bridge_input_payload['bridge_input_id']}",
        "bridge_input_id": bridge_input_payload["bridge_input_id"],
        "eligible_for_bridge": eligible,
        "bridge_result": bridge_result,
        "bridge_reason_code": bridge_reason_code,
        "fail_closed": not eligible,
        "required_allowlist_match": required_allowlist_match,
        "allowlist_matched": allowlist_matched,
        "mutation_rejected": bridge_result == "REJECTED_MUTATION_SQL",
        "multi_statement_rejected": bridge_result == "REJECTED_MULTI_STATEMENT_SQL",
        "comment_hidden_mutation_rejected": bridge_result == "REJECTED_COMMENT_HIDDEN_MUTATION",
        "non_sql_rejected": bridge_result == "REJECTED_NON_SQL_TOOL",
        "dhms_bridge_owner": True,
    }


def contains_mutation_sql(normalized_sql: str) -> bool:
    return any(token in normalized_sql.split() for token in SQL_MUTATION_KEYWORDS)


def has_multiple_statements(sql_text: str) -> bool:
    statements = [statement.strip() for statement in sql_text.split(";") if statement.strip()]
    return len(statements) > 1


def has_comment_hidden_mutation(sql_text: str) -> bool:
    lower = sql_text.lower()
    comment_markers = ("--", "/*", "#")
    if not any(marker in lower for marker in comment_markers):
        return False
    return any(keyword in lower for keyword in SQL_MUTATION_KEYWORDS)


def base_eligibility_fields_ok(bridge_input_payload: dict[str, Any]) -> bool:
    return (
        bridge_input_payload.get("tool_type") == "SQL"
        and bridge_input_payload.get("runtime_decision") == "SANDBOX"
        and bridge_input_payload.get("gate_result") == "HELD_FOR_SANDBOX_BRIDGE"
        and bridge_input_payload.get("select_only_candidate") is True
        and bridge_input_payload.get("mutation_risk") is False
        and bridge_input_payload.get("sandbox_required") is True
        and bridge_input_payload.get("sandbox_bridge_required") is True
        and bridge_input_payload.get("dhms_final_decision") is True
        and bridge_input_payload.get("dhms_gate_owner") is True
        and bridge_input_payload.get("black_box_mode") is True
        and bridge_input_payload.get("previous_execution_detected") is False
    )


def build_authorization_stub(eligibility: dict[str, Any]) -> dict[str, Any]:
    eligible = eligibility["eligible_for_bridge"]
    if eligible:
        authorization_decision = "STUB_ELIGIBLE_BUT_NOT_RELEASED"
        authorization_reason_code = "eligible_select_held_for_future_bridge_release"
    elif eligibility["bridge_result"] == "FAIL_CLOSED_INVALID_BRIDGE_INPUT":
        authorization_decision = "FAIL_CLOSED"
        authorization_reason_code = "invalid_bridge_input_fail_closed"
    else:
        authorization_decision = "REJECT_BRIDGE_INPUT"
        authorization_reason_code = eligibility["bridge_reason_code"]
    return {
        "bridge_authorization_id": f"authorization_{eligibility['bridge_eligibility_id']}",
        "bridge_eligibility_id": eligibility["bridge_eligibility_id"],
        "authorization_decision": authorization_decision,
        "authorization_reason_code": authorization_reason_code,
        "bridge_release_allowed": False,
        "sandbox_mode_required": True,
        "temporary_database_required": True,
        "synthetic_data_only": True,
        "mutation_detection_required": True,
        "teardown_required": True,
        "delete_verification_required": True,
        "execution_requested": False,
    }


def build_sandbox_request_stub(
    bridge_input_payload: dict[str, Any],
    authorization: dict[str, Any],
) -> dict[str, Any]:
    sql_text = str(bridge_input_payload.get("sql_text", ""))
    return {
        "sandbox_request_id": f"sandbox_request_{bridge_input_payload['bridge_input_id']}",
        "bridge_authorization_id": authorization["bridge_authorization_id"],
        "sql_text": sql_text,
        "allowlisted_select": sql_text.strip() == ALLOWLISTED_SELECT,
        "temporary_database": True,
        "real_database": False,
        "network_database": False,
        "credential_used": False,
        "production_data_used": False,
        "execution_requested": False,
        "sandbox_created": False,
        "sql_executed": False,
    }


def build_bridge_trace(
    bridge_input_payload: dict[str, Any],
    eligibility: dict[str, Any],
    authorization: dict[str, Any],
    sandbox_request: dict[str, Any],
) -> dict[str, Any]:
    return {
        "bridge_trace_id": f"bridge_trace_{bridge_input_payload['bridge_input_id']}",
        "bridge_input_id": bridge_input_payload["bridge_input_id"],
        "bridge_eligibility_id": eligibility["bridge_eligibility_id"],
        "bridge_authorization_id": authorization["bridge_authorization_id"],
        "sandbox_request_id": sandbox_request["sandbox_request_id"],
        "dry_run_only": True,
        "bridge_implemented": False,
        "sandbox_execution_released": False,
        "execution_release_allowed": False,
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
        "dhms_bridge_owner": True,
    }


def validate_bridge_record(record: dict[str, Any]) -> dict[str, Any]:
    failed_checks: list[str] = []
    bridge_input_payload = record.get("bridge_input", {})
    eligibility = record.get("eligibility_result", {})
    authorization = record.get("authorization_stub", {})
    sandbox_request = record.get("sandbox_request_stub", {})
    trace = record.get("bridge_trace", {})

    require_fields("bridge_input", bridge_input_payload, REQUIRED_BRIDGE_INPUT_FIELDS, failed_checks)
    require_fields("eligibility_result", eligibility, REQUIRED_ELIGIBILITY_FIELDS, failed_checks)
    require_fields("authorization_stub", authorization, REQUIRED_AUTHORIZATION_FIELDS, failed_checks)
    require_fields("sandbox_request_stub", sandbox_request, REQUIRED_SANDBOX_REQUEST_FIELDS, failed_checks)
    require_fields("bridge_trace", trace, REQUIRED_BRIDGE_TRACE_FIELDS, failed_checks)

    bridge_result = eligibility.get("bridge_result")
    authorization_decision = authorization.get("authorization_decision")
    if bridge_result not in ALLOWED_BRIDGE_RESULTS:
        failed_checks.append("unknown_bridge_result")
    if authorization_decision not in ALLOWED_AUTHORIZATION_DECISIONS:
        failed_checks.append("unknown_authorization_decision")
    if eligibility.get("dhms_bridge_owner") is not True:
        failed_checks.append("eligibility_not_dhms_bridge_owner")
    if trace.get("dhms_bridge_owner") is not True:
        failed_checks.append("trace_not_dhms_bridge_owner")
    if trace.get("black_box_validated") is not True:
        failed_checks.append("trace_black_box_not_true")
    if authorization.get("bridge_release_allowed") is not False:
        failed_checks.append("bridge_release_allowed_not_false")
    if authorization.get("execution_requested") is not False:
        failed_checks.append("authorization_execution_requested")
    if sandbox_request.get("execution_requested") is not False:
        failed_checks.append("sandbox_request_execution_requested")
    if sandbox_request.get("sandbox_created") is not False:
        failed_checks.append("sandbox_created_not_false")
    if sandbox_request.get("sql_executed") is not False:
        failed_checks.append("sandbox_request_sql_executed")
    if sandbox_request.get("real_database") is not False:
        failed_checks.append("sandbox_request_real_database")
    if sandbox_request.get("network_database") is not False:
        failed_checks.append("sandbox_request_network_database")
    if sandbox_request.get("credential_used") is not False:
        failed_checks.append("sandbox_request_credential_used")
    if sandbox_request.get("production_data_used") is not False:
        failed_checks.append("sandbox_request_production_data_used")
    for flag in sorted(NON_EXECUTION_TRACE_FLAGS):
        if trace.get(flag) is not False:
            failed_checks.append(f"{flag}_not_false")

    expected = expected_bridge_result_for_input(bridge_input_payload)
    if bridge_result != expected:
        failed_checks.append(f"bridge_result_expected_{expected}")
    if expected == "ELIGIBLE_HELD_FOR_FUTURE_SANDBOX_EXECUTION":
        if eligibility.get("eligible_for_bridge") is not True:
            failed_checks.append("eligible_select_not_marked_eligible")
        if eligibility.get("fail_closed") is not False:
            failed_checks.append("eligible_select_fail_closed")
        if authorization_decision != "STUB_ELIGIBLE_BUT_NOT_RELEASED":
            failed_checks.append("eligible_select_authorization_mismatch")
        if sandbox_request.get("allowlisted_select") is not True:
            failed_checks.append("eligible_select_not_allowlisted")
    else:
        if eligibility.get("eligible_for_bridge") is not False:
            failed_checks.append("rejected_input_marked_eligible")
        if eligibility.get("fail_closed") is not True:
            failed_checks.append("rejected_input_not_fail_closed")
        if authorization_decision not in {"REJECT_BRIDGE_INPUT", "FAIL_CLOSED"}:
            failed_checks.append("rejected_input_authorization_mismatch")

    return {
        "bridge_input_id": bridge_input_payload.get("bridge_input_id"),
        "bridge_result": bridge_result,
        "authorization_decision": authorization_decision,
        "eligible_for_bridge": eligibility.get("eligible_for_bridge"),
        "bridge_release_allowed": authorization.get("bridge_release_allowed"),
        "sandbox_execution_released": trace.get("sandbox_execution_released"),
        "sql_executed": trace.get("sql_executed"),
        "sqlite_database_created": trace.get("sqlite_database_created"),
        "passed": not failed_checks,
        "failed_checks": failed_checks,
    }


def expected_bridge_result_for_input(bridge_input_payload: dict[str, Any]) -> str:
    sql_text = str(bridge_input_payload.get("sql_text", ""))
    normalized_sql = sql_text.strip().lower()
    if bridge_input_payload.get("tool_type") != "SQL":
        return "REJECTED_NON_SQL_TOOL"
    if bridge_input_payload.get("runtime_decision") == "BLOCK" or bridge_input_payload.get("gate_result") == "CLOSED":
        return "REJECTED_BLOCK_DECISION"
    if not normalized_sql:
        return "REJECTED_UNKNOWN_OR_MALFORMED_SQL"
    if has_comment_hidden_mutation(sql_text):
        return "REJECTED_COMMENT_HIDDEN_MUTATION"
    if contains_mutation_sql(normalized_sql) or bridge_input_payload.get("mutation_risk") is True:
        return "REJECTED_MUTATION_SQL"
    if has_multiple_statements(sql_text):
        return "REJECTED_MULTI_STATEMENT_SQL"
    if base_eligibility_fields_ok(bridge_input_payload) and sql_text.strip() == ALLOWLISTED_SELECT:
        return "ELIGIBLE_HELD_FOR_FUTURE_SANDBOX_EXECUTION"
    return "FAIL_CLOSED_INVALID_BRIDGE_INPUT"


def require_fields(prefix: str, payload: dict[str, Any], required_fields: set[str], failed_checks: list[str]) -> None:
    missing = sorted(required_fields.difference(payload))
    for field in missing:
        failed_checks.append(f"{prefix}.missing_{field}")
