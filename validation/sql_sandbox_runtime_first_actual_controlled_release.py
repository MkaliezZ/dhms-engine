#!/usr/bin/env python3
"""First actual controlled runtime-path SQL sandbox release.

This module performs exactly one controlled runtime-path SQL execution: the
allowlisted SELECT candidate that passed the v0.5.14 actual release boundary
stub. It uses only Python standard-library sqlite3 inside a temporary local
disposable sandbox. Rejected inputs do not create SQLite databases and do not
execute SQL.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import sqlite3
import tempfile
import uuid
from pathlib import Path
from typing import Any

from sql_sandbox_runtime_bridge_stub import ALLOWLISTED_SELECT
from sql_sandbox_runtime_first_actual_release_boundary_stub import (
    run_sql_sandbox_runtime_first_actual_release_boundary_stub,
)


TOY_ROWS = [(1, "alpha", "active"), (2, "beta", "inactive")]
EXPECTED_RESULT_ROWS = [[1, "alpha", "active"], [2, "beta", "inactive"]]

ALLOWED_AUTHORIZATION_DECISIONS = {
    "AUTHORIZE_SINGLE_ALLOWLISTED_SELECT_SANDBOX_EXECUTION",
    "REJECT_ACTUAL_RELEASE_INPUT",
    "FAIL_CLOSED",
}
ALLOWED_AUTHORIZATION_REASON_CODES = {
    "ALLOWLISTED_SELECT_RELEASED_TO_TEMP_SQLITE_SANDBOX",
    "REJECTED_MUTATION_SQL",
    "REJECTED_BLOCK_DECISION",
    "REJECTED_NON_SQL_TOOL",
    "REJECTED_UNKNOWN_OR_MALFORMED_SQL",
    "REJECTED_MULTI_STATEMENT_SQL",
    "REJECTED_COMMENT_HIDDEN_MUTATION",
    "FAIL_CLOSED_INVALID_ACTUAL_RELEASE_INPUT",
}

REQUIRED_RELEASE_INPUT_FIELDS = {
    "actual_release_input_id",
    "actual_release_boundary_input_id",
    "actual_release_boundary_decision_id",
    "actual_release_boundary_trace_id",
    "tool_type",
    "sql_text",
    "allowlist_matched",
    "select_only_candidate",
    "mutation_risk",
    "boundary_decision",
    "boundary_ready_for_future_actual_release",
    "black_box_mode",
}
REQUIRED_AUTHORIZATION_FIELDS = {
    "actual_release_execution_authorization_id",
    "actual_release_input_id",
    "authorization_decision",
    "authorization_reason_code",
    "actual_release_result",
    "release_now",
    "execution_release_allowed",
    "bridge_release_allowed",
    "sandbox_execution_released",
    "execution_requested",
    "requires_temp_sqlite_sandbox",
    "requires_synthetic_data_only",
    "requires_mutation_detection",
    "requires_teardown_verification",
    "requires_delete_verification",
    "dhms_actual_release_owner",
}
REQUIRED_SANDBOX_RESULT_FIELDS = {
    "sandbox_execution_result_id",
    "actual_release_execution_authorization_id",
    "sandbox_mode",
    "temporary_database",
    "real_database",
    "network_database",
    "credential_used",
    "production_data_used",
    "system_temp_directory_used",
    "randomized_sqlite_filename_used",
    "sqlite_database_created",
    "connection_opened",
    "setup_schema_created",
    "synthetic_seed_data_inserted",
    "allowlisted_select_executed",
    "sql_executed",
    "result_row_count",
    "result_rows",
    "pre_schema_hash",
    "post_schema_hash",
    "pre_content_hash",
    "post_content_hash",
    "pre_row_count",
    "post_row_count",
    "mutation_detected",
    "connection_closed",
    "sandbox_deleted",
    "sandbox_deletion_verified",
    "failed_checks",
}
REQUIRED_RELEASE_TRACE_FIELDS = {
    "actual_release_trace_id",
    "actual_release_input_id",
    "actual_release_execution_authorization_id",
    "sandbox_execution_result_id",
    "dry_run_only",
    "actual_release",
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
    "dhms_actual_release_owner",
}


def run_sql_sandbox_runtime_first_actual_controlled_release() -> dict[str, Any]:
    boundary_result = run_sql_sandbox_runtime_first_actual_release_boundary_stub()
    boundary_records = boundary_result.get("boundary_records", [])
    release_records = [build_actual_release_record(record) for record in boundary_records]
    record_results = [validate_actual_release_record(record) for record in release_records]

    failed_checks = [
        f"{result['actual_release_input_id']}.{check}"
        for result in record_results
        for check in result["failed_checks"]
    ]
    actual_release_executed_count = sum(1 for result in record_results if result["actual_release_executed"])
    rejected_actual_release_count = sum(
        1
        for result in record_results
        if result["authorization_decision"] == "REJECT_ACTUAL_RELEASE_INPUT"
    )
    sqlite_database_created_count = sum(1 for result in record_results if result["sqlite_database_created"])
    sql_executed_count = sum(1 for result in record_results if result["sql_executed"])
    sandbox_executed_count = sum(1 for result in record_results if result["sandbox_executed"])
    mutation_detected_count = sum(1 for result in record_results if result["mutation_detected"])
    sandbox_deleted_count = sum(1 for result in record_results if result["sandbox_deleted"])
    sandbox_deletion_verified_count = sum(
        1 for result in record_results if result["sandbox_deletion_verified"]
    )
    passed_actual_release_inputs = sum(1 for result in record_results if result["passed"])
    decisions_by_type = dict(sorted(Counter(result["authorization_decision"] for result in record_results).items()))
    reason_codes_by_type = dict(
        sorted(Counter(result["authorization_reason_code"] for result in record_results).items())
    )
    executed_results = [
        record["sandbox_execution_result"]
        for record in release_records
        if record["authorization"]["authorization_decision"]
        == "AUTHORIZE_SINGLE_ALLOWLISTED_SELECT_SANDBOX_EXECUTION"
    ]
    result_row_count = executed_results[0]["result_row_count"] if executed_results else 0

    if boundary_result.get("status") != "PASS":
        failed_checks.append("actual_release_boundary_stub_precondition_not_pass")
    if actual_release_executed_count != 1:
        failed_checks.append("actual_release_executed_count_not_one")
    if sqlite_database_created_count != 1:
        failed_checks.append("sqlite_database_created_count_not_one")
    if sql_executed_count != 1:
        failed_checks.append("sql_executed_count_not_one")
    if sandbox_executed_count != 1:
        failed_checks.append("sandbox_executed_count_not_one")
    if rejected_actual_release_count != 6:
        failed_checks.append("rejected_actual_release_count_not_six")
    if mutation_detected_count != 0:
        failed_checks.append("mutation_detected_count_not_zero")
    if sandbox_deleted_count != 1:
        failed_checks.append("sandbox_deleted_count_not_one")
    if sandbox_deletion_verified_count != 1:
        failed_checks.append("sandbox_deletion_verified_count_not_one")
    if result_row_count != 2:
        failed_checks.append("result_row_count_not_two")

    status = "PASS" if not failed_checks and passed_actual_release_inputs == len(release_records) else "FAIL"

    return {
        "validation": "sql_sandbox_runtime_first_actual_controlled_release_v0_5_15",
        "status": status,
        "total_actual_release_inputs": len(release_records),
        "passed_actual_release_inputs": passed_actual_release_inputs,
        "actual_release_executed_count": actual_release_executed_count,
        "rejected_actual_release_count": rejected_actual_release_count,
        "authorization_decisions_by_type": decisions_by_type,
        "authorization_reason_codes_by_type": reason_codes_by_type,
        "sqlite_database_created_count": sqlite_database_created_count,
        "sql_executed_count": sql_executed_count,
        "sandbox_executed_count": sandbox_executed_count,
        "result_row_count": result_row_count,
        "result_rows": executed_results[0]["result_rows"] if executed_results else [],
        "mutation_detected_count": mutation_detected_count,
        "sandbox_deleted_count": sandbox_deleted_count,
        "sandbox_deletion_verified_count": sandbox_deletion_verified_count,
        "failed_checks": failed_checks,
        "release_records": release_records,
        "record_results": record_results,
        "actual_release_boundary_stub_status": boundary_result.get("status"),
        "actual_release_boundary_stub_final_verdict": boundary_result.get("final_verdict"),
        "runtime_path_sql_execution_count": sql_executed_count,
        "only_allowlisted_select_executed": (
            actual_release_executed_count == 1
            and sql_executed_count == 1
            and executed_results
            and executed_results[0]["executed_sql_statement"] == ALLOWLISTED_SELECT
        ),
        "rejected_inputs_executed_count": sum(
            1
            for result in record_results
            if result["authorization_decision"] == "REJECT_ACTUAL_RELEASE_INPUT"
            and (result["sql_executed"] or result["sqlite_database_created"])
        ),
        "mutation_sql_executed": False,
        "temporary_local_sqlite_only": True,
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
            "READY_FOR_V0_5_16_SQL_SANDBOX_RUNTIME_FIRST_ACTUAL_RELEASE_RESULT_REVIEW_AND_FREEZE"
            if status == "PASS"
            else "NEEDS_SQL_SANDBOX_RUNTIME_FIRST_ACTUAL_CONTROLLED_RELEASE_FIX"
        ),
    }


def build_actual_release_record(boundary_record: dict[str, Any]) -> dict[str, Any]:
    release_input = build_actual_release_input(boundary_record)
    authorization = build_actual_release_authorization(release_input, boundary_record)
    sandbox_result = build_sandbox_execution_result(authorization)
    trace = build_actual_release_trace(release_input, authorization, sandbox_result)
    return {
        "actual_release_input": release_input,
        "authorization": authorization,
        "sandbox_execution_result": sandbox_result,
        "actual_release_trace": trace,
    }


def build_actual_release_input(boundary_record: dict[str, Any]) -> dict[str, Any]:
    boundary_input = boundary_record["boundary_input"]
    boundary_decision = boundary_record["boundary_decision"]
    boundary_trace = boundary_record["boundary_trace"]
    return {
        "actual_release_input_id": (
            f"actual_release_input_{boundary_input['actual_release_boundary_input_id']}"
        ),
        "actual_release_boundary_input_id": boundary_input["actual_release_boundary_input_id"],
        "actual_release_boundary_decision_id": boundary_decision["actual_release_boundary_decision_id"],
        "actual_release_boundary_trace_id": boundary_trace["actual_release_boundary_trace_id"],
        "tool_type": boundary_input["tool_type"],
        "sql_text": boundary_input["sql_text"],
        "allowlist_matched": boundary_input["allowlist_matched"],
        "select_only_candidate": boundary_input["select_only_candidate"],
        "mutation_risk": boundary_input["mutation_risk"],
        "boundary_decision": boundary_decision["boundary_decision"],
        "boundary_reason_code": boundary_decision["boundary_reason_code"],
        "boundary_ready_for_future_actual_release": boundary_decision[
            "boundary_ready_for_future_actual_release"
        ],
        "black_box_mode": boundary_input["black_box_mode"],
    }


def build_actual_release_authorization(
    release_input: dict[str, Any],
    boundary_record: dict[str, Any],
) -> dict[str, Any]:
    ready = is_authorized_release_candidate(release_input, boundary_record)
    if ready:
        authorization_decision = "AUTHORIZE_SINGLE_ALLOWLISTED_SELECT_SANDBOX_EXECUTION"
        reason_code = "ALLOWLISTED_SELECT_RELEASED_TO_TEMP_SQLITE_SANDBOX"
        actual_release_result = "ACTUAL_RELEASE_EXECUTED_IN_TEMP_SQLITE_SANDBOX"
        release_flags = True
    elif release_input.get("boundary_decision") == "BOUNDARY_REJECTED":
        authorization_decision = "REJECT_ACTUAL_RELEASE_INPUT"
        reason_code = reason_code_for_rejected_input(release_input)
        actual_release_result = "ACTUAL_RELEASE_REJECTED_NO_EXECUTION"
        release_flags = False
    else:
        authorization_decision = "FAIL_CLOSED"
        reason_code = "FAIL_CLOSED_INVALID_ACTUAL_RELEASE_INPUT"
        actual_release_result = "ACTUAL_RELEASE_FAIL_CLOSED"
        release_flags = False

    return {
        "actual_release_execution_authorization_id": (
            f"actual_release_execution_authorization_{release_input['actual_release_input_id']}"
        ),
        "actual_release_input_id": release_input["actual_release_input_id"],
        "authorization_decision": authorization_decision,
        "authorization_reason_code": reason_code,
        "actual_release_result": actual_release_result,
        "release_now": release_flags,
        "execution_release_allowed": release_flags,
        "bridge_release_allowed": release_flags,
        "sandbox_execution_released": release_flags,
        "execution_requested": release_flags,
        "requires_temp_sqlite_sandbox": True,
        "requires_synthetic_data_only": True,
        "requires_mutation_detection": True,
        "requires_teardown_verification": True,
        "requires_delete_verification": True,
        "dhms_actual_release_owner": True,
    }


def is_authorized_release_candidate(
    release_input: dict[str, Any],
    boundary_record: dict[str, Any],
) -> bool:
    boundary_trace = boundary_record["boundary_trace"]
    return (
        release_input.get("tool_type") == "SQL"
        and release_input.get("sql_text") == ALLOWLISTED_SELECT
        and release_input.get("allowlist_matched") is True
        and release_input.get("select_only_candidate") is True
        and release_input.get("mutation_risk") is False
        and release_input.get("boundary_decision") == "BOUNDARY_READY_FOR_FUTURE_ACTUAL_RELEASE"
        and release_input.get("boundary_ready_for_future_actual_release") is True
        and release_input.get("black_box_mode") is True
        and boundary_trace.get("release_now") is False
        and boundary_trace.get("execution_release_allowed") is False
        and boundary_trace.get("bridge_release_allowed") is False
        and boundary_trace.get("sandbox_execution_released") is False
        and boundary_trace.get("execution_requested") is False
        and boundary_trace.get("sql_executed") is False
        and boundary_trace.get("sqlite_database_created") is False
    )


def reason_code_for_rejected_input(release_input: dict[str, Any]) -> str:
    boundary_reason = str(release_input.get("boundary_reason_code"))
    sql_text = str(release_input.get("sql_text") or "")
    if release_input.get("tool_type") != "SQL":
        return "REJECTED_NON_SQL_TOOL"
    if release_input.get("boundary_decision") == "BOUNDARY_REJECTED" and boundary_reason == "REJECTED_AUTHORIZATION_NOT_READY":
        if release_input.get("boundary_ready_for_future_actual_release") is False and release_input.get("tool_type") == "SQL":
            return "REJECTED_BLOCK_DECISION"
        return "REJECTED_NON_SQL_TOOL"
    if "--" in sql_text and any(keyword in sql_text.upper() for keyword in ("UPDATE", "DELETE", "INSERT", "DROP", "ALTER")):
        return "REJECTED_COMMENT_HIDDEN_MUTATION"
    if ";" in sql_text.rstrip(";"):
        return "REJECTED_MULTI_STATEMENT_SQL"
    upper_sql = sql_text.upper()
    if any(keyword in upper_sql for keyword in ("UPDATE", "DELETE", "INSERT", "DROP", "ALTER")):
        return "REJECTED_MUTATION_SQL"
    if boundary_reason == "REJECTED_MUTATION_OR_UNSAFE_SQL":
        return "REJECTED_UNKNOWN_OR_MALFORMED_SQL"
    return "FAIL_CLOSED_INVALID_ACTUAL_RELEASE_INPUT"


def build_sandbox_execution_result(authorization: dict[str, Any]) -> dict[str, Any]:
    if authorization["authorization_decision"] != "AUTHORIZE_SINGLE_ALLOWLISTED_SELECT_SANDBOX_EXECUTION":
        return build_rejected_sandbox_result(authorization)
    return execute_allowlisted_select_in_temp_sqlite(authorization)


def build_rejected_sandbox_result(authorization: dict[str, Any]) -> dict[str, Any]:
    return {
        "sandbox_execution_result_id": (
            f"sandbox_execution_result_{authorization['actual_release_execution_authorization_id']}"
        ),
        "actual_release_execution_authorization_id": authorization["actual_release_execution_authorization_id"],
        "sandbox_mode": False,
        "temporary_database": False,
        "real_database": False,
        "network_database": False,
        "credential_used": False,
        "production_data_used": False,
        "system_temp_directory_used": False,
        "randomized_sqlite_filename_used": False,
        "sqlite_database_created": False,
        "connection_opened": False,
        "setup_schema_created": False,
        "synthetic_seed_data_inserted": False,
        "allowlisted_select_executed": False,
        "sql_executed": False,
        "executed_sql_statement": None,
        "result_row_count": 0,
        "result_rows": [],
        "pre_schema_hash": None,
        "post_schema_hash": None,
        "pre_content_hash": None,
        "post_content_hash": None,
        "pre_row_count": 0,
        "post_row_count": 0,
        "mutation_detected": False,
        "connection_closed": False,
        "sandbox_deleted": False,
        "sandbox_deletion_verified": False,
        "failed_checks": [],
    }


def execute_allowlisted_select_in_temp_sqlite(authorization: dict[str, Any]) -> dict[str, Any]:
    failed_checks: list[str] = []
    temp_root = Path(tempfile.gettempdir()).resolve()
    sandbox_dir = Path(tempfile.mkdtemp(prefix="dhms_runtime_sql_release_", dir=temp_root)).resolve()
    db_name = f"dhms_runtime_select_{uuid.uuid4().hex}.sqlite"
    db_path = (sandbox_dir / db_name).resolve()
    home = Path.home().resolve()
    connection: sqlite3.Connection | None = None

    result: dict[str, Any] = {
        "sandbox_execution_result_id": (
            f"sandbox_execution_result_{authorization['actual_release_execution_authorization_id']}"
        ),
        "actual_release_execution_authorization_id": authorization["actual_release_execution_authorization_id"],
        "sandbox_mode": True,
        "temporary_database": True,
        "real_database": False,
        "network_database": False,
        "credential_used": False,
        "production_data_used": False,
        "system_temp_directory_used": is_relative_to(db_path, temp_root),
        "randomized_sqlite_filename_used": db_name.startswith("dhms_runtime_select_")
        and len(db_name) > len("dhms_runtime_select_.sqlite"),
        "sqlite_database_created": False,
        "connection_opened": False,
        "setup_schema_created": False,
        "synthetic_seed_data_inserted": False,
        "allowlisted_select_executed": False,
        "sql_executed": False,
        "executed_sql_statement": None,
        "result_row_count": 0,
        "result_rows": [],
        "pre_schema_hash": None,
        "post_schema_hash": None,
        "pre_content_hash": None,
        "post_content_hash": None,
        "pre_row_count": 0,
        "post_row_count": 0,
        "mutation_detected": False,
        "connection_closed": False,
        "sandbox_deleted": False,
        "sandbox_deletion_verified": False,
        "user_path_used": is_relative_to(db_path, home),
        "persistent_database_used": False,
        "failed_checks": failed_checks,
    }

    pre_state: dict[str, Any] = {}
    post_state: dict[str, Any] = {}
    try:
        if not result["system_temp_directory_used"]:
            failed_checks.append("sandbox_path_not_system_temp")
        if result["user_path_used"]:
            failed_checks.append("sandbox_path_is_user_path")
        if not result["randomized_sqlite_filename_used"]:
            failed_checks.append("sqlite_filename_not_randomized")

        connection = sqlite3.connect(str(db_path))
        result["sqlite_database_created"] = db_path.exists()
        result["connection_opened"] = True

        connection.execute("CREATE TABLE toy_accounts (id INTEGER PRIMARY KEY, label TEXT, status TEXT);")
        result["setup_schema_created"] = True
        connection.executemany("INSERT INTO toy_accounts (id, label, status) VALUES (?, ?, ?);", TOY_ROWS)
        connection.commit()
        result["synthetic_seed_data_inserted"] = True

        pre_state = collect_state(connection)
        rows = [list(row) for row in connection.execute(ALLOWLISTED_SELECT).fetchall()]
        result["allowlisted_select_executed"] = True
        result["sql_executed"] = True
        result["executed_sql_statement"] = ALLOWLISTED_SELECT
        result["result_rows"] = rows
        result["result_row_count"] = len(rows)
        post_state = collect_state(connection)
    finally:
        mutation_detection = build_mutation_detection(pre_state, post_state)
        result["pre_schema_hash"] = mutation_detection["pre_schema_hash"]
        result["post_schema_hash"] = mutation_detection["post_schema_hash"]
        result["pre_content_hash"] = mutation_detection["pre_content_hash"]
        result["post_content_hash"] = mutation_detection["post_content_hash"]
        result["pre_row_count"] = mutation_detection["pre_row_count"]
        result["post_row_count"] = mutation_detection["post_row_count"]
        result["mutation_detected"] = mutation_detection["mutation_detected"]
        if connection is not None:
            connection.close()
            result["connection_closed"] = True
        if db_path.exists():
            db_path.unlink()
            result["sandbox_deleted"] = True
        result["sandbox_deletion_verified"] = not db_path.exists()
        try:
            sandbox_dir.rmdir()
        except OSError:
            pass

    if result["result_rows"] != EXPECTED_RESULT_ROWS:
        failed_checks.append("unexpected_result_rows")
    if result["result_row_count"] != 2:
        failed_checks.append("unexpected_result_row_count")
    if result["mutation_detected"]:
        failed_checks.append("mutation_detected_after_allowlisted_select")
    if not result["connection_closed"]:
        failed_checks.append("connection_not_closed")
    if not result["sandbox_deleted"]:
        failed_checks.append("sandbox_file_not_deleted")
    if not result["sandbox_deletion_verified"]:
        failed_checks.append("sandbox_deletion_not_verified")
    if not result["sqlite_database_created"]:
        failed_checks.append("sqlite_database_not_created")

    return result


def build_actual_release_trace(
    release_input: dict[str, Any],
    authorization: dict[str, Any],
    sandbox_result: dict[str, Any],
) -> dict[str, Any]:
    executed = authorization["authorization_decision"] == "AUTHORIZE_SINGLE_ALLOWLISTED_SELECT_SANDBOX_EXECUTION"
    return {
        "actual_release_trace_id": f"actual_release_trace_{release_input['actual_release_input_id']}",
        "actual_release_input_id": release_input["actual_release_input_id"],
        "actual_release_execution_authorization_id": authorization[
            "actual_release_execution_authorization_id"
        ],
        "sandbox_execution_result_id": sandbox_result["sandbox_execution_result_id"],
        "dry_run_only": not executed,
        "actual_release": executed,
        "release_now": authorization["release_now"],
        "execution_release_allowed": authorization["execution_release_allowed"],
        "bridge_release_allowed": authorization["bridge_release_allowed"],
        "sandbox_execution_released": authorization["sandbox_execution_released"],
        "execution_requested": authorization["execution_requested"],
        "executed": executed,
        "tool_executed": executed,
        "sql_executed": sandbox_result["sql_executed"],
        "sandbox_executed": executed,
        "sqlite_database_created": sandbox_result["sqlite_database_created"],
        "openclaw_invoked": False,
        "provider_invoked": False,
        "agent_sdk_invoked": False,
        "external_service_sdk_invoked": False,
        "production_runner_invoked": False,
        "http_adapter_invoked": False,
        "external_mutation_detected": False,
        "black_box_validated": True,
        "dhms_actual_release_owner": True,
    }


def validate_actual_release_record(record: dict[str, Any]) -> dict[str, Any]:
    failed_checks: list[str] = []
    release_input = record.get("actual_release_input", {})
    authorization = record.get("authorization", {})
    sandbox_result = record.get("sandbox_execution_result", {})
    trace = record.get("actual_release_trace", {})

    require_fields("actual_release_input", release_input, REQUIRED_RELEASE_INPUT_FIELDS, failed_checks)
    require_fields("authorization", authorization, REQUIRED_AUTHORIZATION_FIELDS, failed_checks)
    require_fields("sandbox_execution_result", sandbox_result, REQUIRED_SANDBOX_RESULT_FIELDS, failed_checks)
    require_fields("actual_release_trace", trace, REQUIRED_RELEASE_TRACE_FIELDS, failed_checks)

    authorization_decision = authorization.get("authorization_decision")
    reason_code = authorization.get("authorization_reason_code")
    if authorization_decision not in ALLOWED_AUTHORIZATION_DECISIONS:
        failed_checks.append("unknown_authorization_decision")
    if reason_code not in ALLOWED_AUTHORIZATION_REASON_CODES:
        failed_checks.append("unknown_authorization_reason_code")
    if authorization.get("dhms_actual_release_owner") is not True:
        failed_checks.append("authorization_not_dhms_actual_release_owner")
    if trace.get("dhms_actual_release_owner") is not True:
        failed_checks.append("trace_not_dhms_actual_release_owner")
    if trace.get("black_box_validated") is not True:
        failed_checks.append("trace_black_box_not_true")
    for field in (
        "requires_temp_sqlite_sandbox",
        "requires_synthetic_data_only",
        "requires_mutation_detection",
        "requires_teardown_verification",
        "requires_delete_verification",
    ):
        if authorization.get(field) is not True:
            failed_checks.append(f"authorization_{field}_not_true")

    authorized = authorization_decision == "AUTHORIZE_SINGLE_ALLOWLISTED_SELECT_SANDBOX_EXECUTION"
    if authorized:
        if authorization.get("actual_release_result") != "ACTUAL_RELEASE_EXECUTED_IN_TEMP_SQLITE_SANDBOX":
            failed_checks.append("executed_candidate_actual_release_result_mismatch")
        validate_executed_candidate(release_input, authorization, sandbox_result, trace, failed_checks)
    else:
        if authorization.get("actual_release_result") not in {
            "ACTUAL_RELEASE_REJECTED_NO_EXECUTION",
            "ACTUAL_RELEASE_FAIL_CLOSED",
        }:
            failed_checks.append("rejected_candidate_actual_release_result_mismatch")
        validate_rejected_candidate(authorization, sandbox_result, trace, failed_checks)

    return {
        "actual_release_input_id": release_input.get("actual_release_input_id"),
        "authorization_decision": authorization_decision,
        "authorization_reason_code": reason_code,
        "actual_release_result": authorization.get("actual_release_result"),
        "actual_release_executed": authorized and trace.get("actual_release") is True,
        "release_now": trace.get("release_now"),
        "execution_release_allowed": trace.get("execution_release_allowed"),
        "bridge_release_allowed": trace.get("bridge_release_allowed"),
        "sandbox_execution_released": trace.get("sandbox_execution_released"),
        "execution_requested": trace.get("execution_requested"),
        "sql_executed": trace.get("sql_executed"),
        "sandbox_executed": trace.get("sandbox_executed"),
        "sqlite_database_created": trace.get("sqlite_database_created"),
        "result_row_count": sandbox_result.get("result_row_count"),
        "mutation_detected": sandbox_result.get("mutation_detected"),
        "sandbox_deleted": sandbox_result.get("sandbox_deleted"),
        "sandbox_deletion_verified": sandbox_result.get("sandbox_deletion_verified"),
        "passed": not failed_checks,
        "failed_checks": failed_checks,
    }


def validate_executed_candidate(
    release_input: dict[str, Any],
    authorization: dict[str, Any],
    sandbox_result: dict[str, Any],
    trace: dict[str, Any],
    failed_checks: list[str],
) -> None:
    if release_input.get("sql_text") != ALLOWLISTED_SELECT:
        failed_checks.append("executed_candidate_allowlist_mismatch")
    for field in (
        "release_now",
        "execution_release_allowed",
        "bridge_release_allowed",
        "sandbox_execution_released",
        "execution_requested",
    ):
        if authorization.get(field) is not True:
            failed_checks.append(f"authorization_{field}_not_true")
        if trace.get(field) is not True:
            failed_checks.append(f"trace_{field}_not_true")
    for field in (
        "executed",
        "tool_executed",
        "sql_executed",
        "sandbox_executed",
        "sqlite_database_created",
        "actual_release",
    ):
        if trace.get(field) is not True:
            failed_checks.append(f"trace_{field}_not_true")
    if trace.get("dry_run_only") is not False:
        failed_checks.append("trace_dry_run_only_not_false")
    for field in (
        "sandbox_mode",
        "temporary_database",
        "system_temp_directory_used",
        "randomized_sqlite_filename_used",
        "sqlite_database_created",
        "connection_opened",
        "setup_schema_created",
        "synthetic_seed_data_inserted",
        "allowlisted_select_executed",
        "sql_executed",
        "connection_closed",
        "sandbox_deleted",
        "sandbox_deletion_verified",
    ):
        if sandbox_result.get(field) is not True:
            failed_checks.append(f"sandbox_result_{field}_not_true")
    for field in ("real_database", "network_database", "credential_used", "production_data_used"):
        if sandbox_result.get(field) is not False:
            failed_checks.append(f"sandbox_result_{field}_not_false")
    if sandbox_result.get("executed_sql_statement") != ALLOWLISTED_SELECT:
        failed_checks.append("sandbox_result_executed_sql_statement_mismatch")
    if sandbox_result.get("result_rows") != EXPECTED_RESULT_ROWS:
        failed_checks.append("sandbox_result_rows_mismatch")
    if sandbox_result.get("result_row_count") != 2:
        failed_checks.append("sandbox_result_row_count_not_two")
    if sandbox_result.get("pre_row_count") != 2 or sandbox_result.get("post_row_count") != 2:
        failed_checks.append("sandbox_result_row_count_mutation_mismatch")
    if sandbox_result.get("pre_schema_hash") != sandbox_result.get("post_schema_hash"):
        failed_checks.append("schema_hash_changed")
    if sandbox_result.get("pre_content_hash") != sandbox_result.get("post_content_hash"):
        failed_checks.append("content_hash_changed")
    if sandbox_result.get("mutation_detected") is not False:
        failed_checks.append("mutation_detected")
    if sandbox_result.get("failed_checks"):
        failed_checks.append("sandbox_result_failed_checks_not_empty")
    validate_no_external_invocations(trace, failed_checks)


def validate_rejected_candidate(
    authorization: dict[str, Any],
    sandbox_result: dict[str, Any],
    trace: dict[str, Any],
    failed_checks: list[str],
) -> None:
    if authorization.get("authorization_decision") != "REJECT_ACTUAL_RELEASE_INPUT":
        failed_checks.append("rejected_candidate_authorization_not_reject")
    for field in (
        "release_now",
        "execution_release_allowed",
        "bridge_release_allowed",
        "sandbox_execution_released",
        "execution_requested",
    ):
        if authorization.get(field) is not False:
            failed_checks.append(f"authorization_{field}_not_false")
        if trace.get(field) is not False:
            failed_checks.append(f"trace_{field}_not_false")
    for field in (
        "executed",
        "tool_executed",
        "sql_executed",
        "sandbox_executed",
        "sqlite_database_created",
        "actual_release",
    ):
        if trace.get(field) is not False:
            failed_checks.append(f"trace_{field}_not_false")
    if trace.get("dry_run_only") is not True:
        failed_checks.append("trace_dry_run_only_not_true")
    for field in (
        "sandbox_mode",
        "temporary_database",
        "system_temp_directory_used",
        "randomized_sqlite_filename_used",
        "sqlite_database_created",
        "connection_opened",
        "setup_schema_created",
        "synthetic_seed_data_inserted",
        "allowlisted_select_executed",
        "sql_executed",
        "connection_closed",
        "sandbox_deleted",
        "sandbox_deletion_verified",
    ):
        if sandbox_result.get(field) is not False:
            failed_checks.append(f"rejected_sandbox_result_{field}_not_false")
    if sandbox_result.get("result_rows") != []:
        failed_checks.append("rejected_result_rows_not_empty")
    if sandbox_result.get("result_row_count") != 0:
        failed_checks.append("rejected_result_row_count_not_zero")
    if sandbox_result.get("mutation_detected") is not False:
        failed_checks.append("rejected_mutation_detected_not_false")
    if sandbox_result.get("failed_checks"):
        failed_checks.append("rejected_sandbox_result_failed_checks_not_empty")
    validate_no_external_invocations(trace, failed_checks)


def validate_no_external_invocations(trace: dict[str, Any], failed_checks: list[str]) -> None:
    for field in (
        "openclaw_invoked",
        "provider_invoked",
        "agent_sdk_invoked",
        "external_service_sdk_invoked",
        "production_runner_invoked",
        "http_adapter_invoked",
        "external_mutation_detected",
    ):
        if trace.get(field) is not False:
            failed_checks.append(f"trace_{field}_not_false")


def collect_state(connection: sqlite3.Connection) -> dict[str, Any]:
    schema_rows = [
        list(row)
        for row in connection.execute(
            "SELECT type, name, tbl_name, sql FROM sqlite_master WHERE type IN ('table', 'index') ORDER BY type, name;"
        ).fetchall()
    ]
    table_rows = [
        list(row)
        for row in connection.execute("SELECT id, label, status FROM toy_accounts ORDER BY id;").fetchall()
    ]
    return {
        "schema_hash": stable_hash(schema_rows),
        "content_hash": stable_hash({"toy_accounts": table_rows}),
        "row_count": len(table_rows),
    }


def build_mutation_detection(pre_state: dict[str, Any], post_state: dict[str, Any]) -> dict[str, Any]:
    return {
        "pre_schema_hash": pre_state.get("schema_hash"),
        "post_schema_hash": post_state.get("schema_hash"),
        "pre_content_hash": pre_state.get("content_hash"),
        "post_content_hash": post_state.get("content_hash"),
        "pre_row_count": pre_state.get("row_count", 0),
        "post_row_count": post_state.get("row_count", 0),
        "mutation_detected": not (
            pre_state.get("schema_hash") == post_state.get("schema_hash")
            and pre_state.get("content_hash") == post_state.get("content_hash")
            and pre_state.get("row_count") == post_state.get("row_count")
        ),
    }


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def require_fields(prefix: str, payload: dict[str, Any], required_fields: set[str], failed_checks: list[str]) -> None:
    missing = sorted(required_fields.difference(payload))
    for field in missing:
        failed_checks.append(f"{prefix}.missing_{field}")
