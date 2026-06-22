#!/usr/bin/env python3
"""Mount SQL Safety v0.4 into the v0.5 runtime stub path.

This module routes intercepted SQL proposals into deterministic SQL safety
runtime decisions. It does not execute SQL, create SQLite databases from the
runtime path, invoke SQL sandbox execution, call providers, or run production
checker/runner logic.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from execution_runtime_contract_stub import validate_runtime_contract_examples
from sql_safety_temp_sqlite_mutation_block_test import run_sql_safety_temp_sqlite_mutation_block_test
from sql_safety_temp_sqlite_select_only_sandbox import run_sql_safety_temp_sqlite_select_only_first_real_run
from tool_call_interceptor_stub import run_tool_call_interceptor_stub


ALLOWED_SQL_RISK_TYPES = {"MUTATION_SQL", "SELECT_ONLY_SQL", "UNKNOWN_SQL", "MALFORMED_SQL"}
ALLOWED_SQL_DECISIONS = {"BLOCK", "SANDBOX"}
SQL_MUTATION_PREFIXES = ("update", "delete", "insert", "drop", "alter", "replace", "truncate", "create")

REQUIRED_MOUNT_INPUT_FIELDS = {
    "mount_input_id",
    "request_id",
    "proposal_id",
    "classification_id",
    "tool_type",
    "tool_name",
    "tool_args",
    "sql_text",
    "interceptor_handoff_status",
    "received_by_sql_safety_mount",
    "tool_executed",
}

REQUIRED_SQL_DECISION_FIELDS = {
    "sql_decision_id",
    "mount_input_id",
    "request_id",
    "proposal_id",
    "sql_risk_type",
    "decision",
    "reason_code",
    "sandbox_required",
    "mutation_risk",
    "select_only_candidate",
    "dhms_final_decision",
    "sql_executed",
}

REQUIRED_SQL_TRACE_FIELDS = {
    "trace_id",
    "request_id",
    "proposal_id",
    "sql_decision_id",
    "tool_type",
    "decision",
    "executed",
    "sql_executed",
    "sandbox_executed",
    "provider_invoked",
    "agent_sdk_invoked",
    "external_service_sdk_invoked",
    "production_runner_invoked",
    "http_adapter_invoked",
    "external_mutation_detected",
    "black_box_validated",
}

NON_EXECUTION_TRACE_FLAGS = {
    "executed",
    "sql_executed",
    "sandbox_executed",
    "provider_invoked",
    "agent_sdk_invoked",
    "external_service_sdk_invoked",
    "production_runner_invoked",
    "http_adapter_invoked",
    "external_mutation_detected",
}


def run_sql_safety_runtime_mount_stub() -> dict[str, Any]:
    contract_preflight = validate_runtime_contract_examples()
    interceptor_preflight = run_tool_call_interceptor_stub()
    select_preflight = run_sql_safety_temp_sqlite_select_only_first_real_run()
    mutation_preflight = run_sql_safety_temp_sqlite_mutation_block_test()

    mount_inputs = build_sql_mount_inputs(interceptor_preflight)
    records = [build_mount_record(mount_input) for mount_input in mount_inputs]
    record_results = [validate_mount_record(record) for record in records]

    failed_checks = [
        f"{result['mount_input_id']}.{check}"
        for result in record_results
        for check in result["failed_checks"]
    ]
    for name, result in [
        ("contract_preflight_failed", contract_preflight),
        ("interceptor_preflight_failed", interceptor_preflight),
        ("select_only_preflight_failed", select_preflight),
        ("mutation_block_preflight_failed", mutation_preflight),
    ]:
        if result.get("status") != "PASS":
            failed_checks.append(name)

    decisions_by_type = dict(sorted(Counter(result["decision"] for result in record_results).items()))
    sql_risk_types = dict(sorted(Counter(result["sql_risk_type"] for result in record_results).items()))
    blocked_count = sum(1 for result in record_results if result["decision"] == "BLOCK")
    sandbox_required_count = sum(1 for result in record_results if result["sandbox_required"])
    executed_count = sum(1 for record in records if record["runtime_trace"]["executed"])
    passed_mount_inputs = sum(1 for result in record_results if result["passed"])
    status = "PASS" if not failed_checks and passed_mount_inputs == len(records) else "FAIL"

    return {
        "validation": "sql_safety_runtime_mount_stub_v0_5_3",
        "status": status,
        "contract_preflight_passed": contract_preflight.get("status") == "PASS",
        "interceptor_preflight_passed": interceptor_preflight.get("status") == "PASS",
        "select_only_preflight_passed": select_preflight.get("status") == "PASS",
        "mutation_block_preflight_passed": mutation_preflight.get("status") == "PASS",
        "total_mount_inputs": len(mount_inputs),
        "passed_mount_inputs": passed_mount_inputs,
        "decisions_by_type": decisions_by_type,
        "sql_risk_types": sql_risk_types,
        "blocked_count": blocked_count,
        "sandbox_required_count": sandbox_required_count,
        "executed_count": executed_count,
        "failed_checks": failed_checks,
        "mount_inputs": mount_inputs,
        "mount_records": records,
        "record_results": record_results,
        "runtime_wrapper_executed": False,
        "tool_execution_invoked": False,
        "sql_execution_invoked_from_runtime_path": False,
        "sqlite_database_created_from_runtime_path": False,
        "sql_sandbox_execution_invoked_from_runtime_path": False,
        "openclaw_invoked": False,
        "deepseek_invoked": False,
        "provider_sdk_invoked": False,
        "agent_sdk_invoked": False,
        "http_adapter_invoked": False,
        "production_checker_invoked": False,
        "production_runner_invoked": False,
        "full_suite_validation_invoked": False,
        "final_verdict": (
            "READY_FOR_V0_5_4_OPENCLAW_EVALUATION_WRAPPER_REVIEW_FOR_RUNTIME_ADAPTATION"
            if status == "PASS"
            else "NEEDS_SQL_SAFETY_RUNTIME_MOUNT_STUB_FIX"
        ),
    }


def build_sql_mount_inputs(interceptor_result: dict[str, Any]) -> list[dict[str, Any]]:
    records = interceptor_result.get("interception_records", [])
    sql_records = [
        record
        for record in records
        if record.get("normalized_proposal", {}).get("tool_type") == "SQL"
        and record.get("handoff", {}).get("handoff_target") == "RUNTIME_CONTRACT_SAFETY_DECISION"
    ]
    mount_inputs = [build_mount_input_from_interceptor(record) for record in sql_records]
    mount_inputs.append(
        {
            "mount_input_id": "mount_sql_unknown_missing_text",
            "request_id": "req_sql_unknown_missing_text",
            "proposal_id": "proposal_sql_unknown_missing_text",
            "classification_id": "classification_sql_unknown_missing_text",
            "tool_type": "SQL",
            "tool_name": "sql_query",
            "tool_args": {},
            "sql_text": "",
            "interceptor_handoff_status": "HANDED_OFF",
            "received_by_sql_safety_mount": True,
            "tool_executed": False,
        }
    )
    return mount_inputs


def build_mount_input_from_interceptor(record: dict[str, Any]) -> dict[str, Any]:
    proposal = record["normalized_proposal"]
    classification = record["classification"]
    return {
        "mount_input_id": f"mount_{proposal['proposal_id']}",
        "request_id": proposal["request_id"],
        "proposal_id": proposal["proposal_id"],
        "classification_id": classification["classification_id"],
        "tool_type": "SQL",
        "tool_name": proposal["tool_name"],
        "tool_args": proposal["tool_args"],
        "sql_text": str(proposal.get("tool_args", {}).get("sql", "")),
        "interceptor_handoff_status": record["handoff"]["handoff_status"],
        "received_by_sql_safety_mount": True,
        "tool_executed": False,
    }


def build_mount_record(mount_input: dict[str, Any]) -> dict[str, Any]:
    decision = build_sql_decision(mount_input)
    trace = build_runtime_trace(mount_input, decision)
    return {
        "mount_input": mount_input,
        "sql_decision": decision,
        "runtime_trace": trace,
    }


def build_sql_decision(mount_input: dict[str, Any]) -> dict[str, Any]:
    sql_text = str(mount_input.get("sql_text", "")).strip()
    normalized = sql_text.lower()
    mutation_risk = normalized.startswith(SQL_MUTATION_PREFIXES)
    select_only_candidate = normalized.startswith("select") and not any(
        keyword in normalized for keyword in SQL_MUTATION_PREFIXES
    )
    malformed = not sql_text
    if mutation_risk:
        sql_risk_type = "MUTATION_SQL"
        decision = "BLOCK"
        reason_code = "mutation_sql_blocked_before_execution"
        sandbox_required = False
    elif select_only_candidate:
        sql_risk_type = "SELECT_ONLY_SQL"
        decision = "SANDBOX"
        reason_code = "select_only_requires_sql_safety_sandbox"
        sandbox_required = True
    elif malformed:
        sql_risk_type = "MALFORMED_SQL"
        decision = "BLOCK"
        reason_code = "malformed_sql_blocked"
        sandbox_required = False
    else:
        sql_risk_type = "UNKNOWN_SQL"
        decision = "BLOCK"
        reason_code = "unknown_sql_blocked"
        sandbox_required = False
    return {
        "sql_decision_id": f"sql_decision_{mount_input['mount_input_id']}",
        "mount_input_id": mount_input["mount_input_id"],
        "request_id": mount_input["request_id"],
        "proposal_id": mount_input["proposal_id"],
        "sql_risk_type": sql_risk_type,
        "decision": decision,
        "reason_code": reason_code,
        "sandbox_required": sandbox_required,
        "mutation_risk": mutation_risk,
        "select_only_candidate": select_only_candidate,
        "dhms_final_decision": True,
        "sql_executed": False,
    }


def build_runtime_trace(mount_input: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "trace_id": f"trace_{decision['sql_decision_id']}",
        "request_id": mount_input["request_id"],
        "proposal_id": mount_input["proposal_id"],
        "sql_decision_id": decision["sql_decision_id"],
        "tool_type": "SQL",
        "decision": decision["decision"],
        "executed": False,
        "sql_executed": False,
        "sandbox_executed": False,
        "provider_invoked": False,
        "agent_sdk_invoked": False,
        "external_service_sdk_invoked": False,
        "production_runner_invoked": False,
        "http_adapter_invoked": False,
        "external_mutation_detected": False,
        "black_box_validated": True,
    }


def validate_mount_record(record: dict[str, Any]) -> dict[str, Any]:
    failed_checks: list[str] = []
    mount_input = record.get("mount_input", {})
    decision = record.get("sql_decision", {})
    trace = record.get("runtime_trace", {})

    require_fields("mount_input", mount_input, REQUIRED_MOUNT_INPUT_FIELDS, failed_checks)
    require_fields("sql_decision", decision, REQUIRED_SQL_DECISION_FIELDS, failed_checks)
    require_fields("runtime_trace", trace, REQUIRED_SQL_TRACE_FIELDS, failed_checks)

    if mount_input.get("tool_type") != "SQL":
        failed_checks.append("mount_input_tool_type_not_sql")
    if mount_input.get("received_by_sql_safety_mount") is not True:
        failed_checks.append("mount_input_not_received")
    if mount_input.get("tool_executed") is not False:
        failed_checks.append("mount_input_tool_executed")
    if decision.get("sql_risk_type") not in ALLOWED_SQL_RISK_TYPES:
        failed_checks.append("unknown_sql_risk_type")
    if decision.get("decision") not in ALLOWED_SQL_DECISIONS:
        failed_checks.append("unknown_sql_decision")
    if decision.get("dhms_final_decision") is not True:
        failed_checks.append("dhms_final_decision_not_true")
    if decision.get("sql_executed") is not False:
        failed_checks.append("decision_sql_executed")

    risk_type = decision.get("sql_risk_type")
    sql_decision = decision.get("decision")
    if risk_type == "MUTATION_SQL" and sql_decision != "BLOCK":
        failed_checks.append("mutation_sql_not_blocked")
    if risk_type == "SELECT_ONLY_SQL" and sql_decision != "SANDBOX":
        failed_checks.append("select_only_not_sandboxed")
    if risk_type in {"UNKNOWN_SQL", "MALFORMED_SQL"} and sql_decision != "BLOCK":
        failed_checks.append("unknown_or_malformed_not_blocked")
    if risk_type == "SELECT_ONLY_SQL" and decision.get("sandbox_required") is not True:
        failed_checks.append("select_only_sandbox_required_not_true")
    if risk_type != "SELECT_ONLY_SQL" and decision.get("sandbox_required") is not False:
        failed_checks.append("non_select_sandbox_required_not_false")
    if trace.get("decision") != sql_decision:
        failed_checks.append("trace_decision_mismatch")
    if trace.get("tool_type") != "SQL":
        failed_checks.append("trace_tool_type_not_sql")
    for flag in sorted(NON_EXECUTION_TRACE_FLAGS):
        if trace.get(flag) is not False:
            failed_checks.append(f"{flag}_not_false")
    if trace.get("black_box_validated") is not True:
        failed_checks.append("black_box_validated_not_true")

    return {
        "mount_input_id": mount_input.get("mount_input_id"),
        "proposal_id": mount_input.get("proposal_id"),
        "sql_risk_type": decision.get("sql_risk_type"),
        "decision": decision.get("decision"),
        "sandbox_required": decision.get("sandbox_required"),
        "executed": trace.get("executed"),
        "passed": not failed_checks,
        "failed_checks": failed_checks,
    }


def require_fields(prefix: str, payload: dict[str, Any], required_fields: set[str], failed_checks: list[str]) -> None:
    missing = sorted(required_fields.difference(payload))
    for field in missing:
        failed_checks.append(f"{prefix}.missing_{field}")
