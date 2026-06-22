#!/usr/bin/env python3
"""Authorize next-phase temp SQLite SELECT-only readiness without execution."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = REPO_ROOT / "cases" / "sql_safety"
EXECUTION_STUB_VALIDATION = REPO_ROOT / "validation" / "run_sql_safety_select_only_sqlite_execution_stub.py"

AUTHORIZED_NEXT_PHASE = "v0.4.2I_SQL_SAFETY_TEMP_SQLITE_SELECT_ONLY_FIRST_REAL_RUN"
AUTHORIZATION_SCOPE = "temporary_local_sqlite_select_only"

EXPECTED_CASES = {
    "sql_delete_without_authorization": "A",
    "sql_dry_run_claim_completed": "A",
    "sql_injection_tool_call_guard": "A",
    "sql_update_from_stale_memory": "B",
    "sql_rag_identity_conflict": "B",
    "sql_select_sensitive_data_leakage": "B",
    "sql_conflicting_instruction_update": "C",
}
EXPECTED_CASE_IDS = sorted(EXPECTED_CASES)

REQUIRED_RECORD_FIELDS = [
    "authorization_gate",
    "case_id",
    "taxonomy_group",
    "next_phase_authorized",
    "authorized_next_phase",
    "authorization_scope",
    "sqlite_import_allowed_next_phase",
    "sqlite_imported_this_phase",
    "sqlite_database_created_this_phase",
    "database_connected_this_phase",
    "sql_executed_this_phase",
    "temp_directory_required",
    "randomized_filename_required",
    "user_path_allowed",
    "persistent_database_allowed",
    "network_database_allowed",
    "credential_allowed",
    "production_data_allowed",
    "select_only_required",
    "mutation_sql_allowed",
    "multiple_statements_allowed",
    "comments_hiding_mutation_allowed",
    "mutation_detection_required",
    "connection_close_required",
    "sandbox_delete_required",
    "sandbox_deletion_verification_required",
    "provider_invoked",
    "real_checker_invoked",
    "production_runner_invoked",
    "http_adapter_invoked",
    "external_mutation_detected",
    "passed",
    "failed_checks",
]

UNSAFE_TEXT_PATTERNS = [
    "sqlite_imported_this_phase=true",
    "sqlite_database_created_this_phase=true",
    "database_connected_this_phase=true",
    "sql_executed_this_phase=true",
    "user_path_allowed=true",
    "persistent_database_allowed=true",
    "network_database_allowed=true",
    "credential_allowed=true",
    "production_data_allowed=true",
    "mutation_sql_allowed=true",
    "multiple_statements_allowed=true",
    "comments_hiding_mutation_allowed=true",
    "provider_invoked=true",
    "real_checker_invoked=true",
    "production_runner_invoked=true",
    "http_adapter_invoked=true",
    "external_mutation_detected=true",
    "created sqlite database this phase",
    "opened database connection this phase",
    "sql executed this phase",
    "used database credential this phase",
    "provider was invoked",
    "production runner invoked",
    "http adapter executed",
    "external mutation occurred",
]


def run_sql_safety_temp_sqlite_select_only_authorization_gate() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    execution_stub_result = run_execution_stub_preflight()
    add_check(
        checks,
        "select_only_execution_stub_preflight_passed",
        execution_stub_result.get("status") == "PASS",
        {
            "status": execution_stub_result.get("status"),
            "failed_checks": execution_stub_result.get("failed_checks", []),
        },
    )

    observed_paths = sorted(CASE_DIR.glob("*.txt")) if CASE_DIR.exists() else []
    observed_case_ids = sorted(path.stem for path in observed_paths)
    execution_stub_case_ids = sorted(str(case_id) for case_id in execution_stub_result.get("case_ids", []))

    add_check(
        checks,
        "exact_sql_case_file_set",
        observed_case_ids == EXPECTED_CASE_IDS,
        {"expected": EXPECTED_CASE_IDS, "observed": observed_case_ids},
    )
    add_check(
        checks,
        "case_set_matches_select_only_execution_stub",
        observed_case_ids == execution_stub_case_ids == EXPECTED_CASE_IDS,
        {
            "filesystem": observed_case_ids,
            "execution_stub": execution_stub_case_ids,
            "expected": EXPECTED_CASE_IDS,
        },
    )

    records = [build_authorization_record(case_id) for case_id in EXPECTED_CASE_IDS]
    for record in records:
        validate_record(checks, record)

    add_check(checks, "no_unsafe_wording_in_authorization_records", not unsafe_wording(records), {})

    failed_checks = [check["name"] for check in checks if not check["passed"]]
    passed_cases = sorted(str(record["case_id"]) for record in records if record.get("passed") is True)
    status = "PASS" if not failed_checks and passed_cases == EXPECTED_CASE_IDS else "FAIL"
    return {
        "validation": "sql_safety_temp_sqlite_select_only_authorization_gate_v042h",
        "status": status,
        "total_cases": len(records),
        "passed_cases": len(passed_cases),
        "failed_checks": failed_checks,
        "case_ids": EXPECTED_CASE_IDS,
        "case_set_consistency": observed_case_ids == execution_stub_case_ids == EXPECTED_CASE_IDS,
        "select_only_execution_stub_preflight_reused": True,
        "authorization_gate": True,
        "authorized_next_phase": AUTHORIZED_NEXT_PHASE,
        "authorization_scope": AUTHORIZATION_SCOPE,
        "non_execution_confirmed": status == "PASS",
        "sqlite_import_allowed_next_phase": True,
        "sqlite_imported_this_phase": False,
        "sqlite_database_created_this_phase": False,
        "database_connected_this_phase": False,
        "sql_executed_this_phase": False,
        "credential_allowed": False,
        "production_data_allowed": False,
        "mutation_sql_allowed": False,
        "provider_invoked": False,
        "real_checker_invoked": False,
        "production_runner_invoked": False,
        "http_adapter_invoked": False,
        "external_mutation_detected": False,
        "records": records,
        "per_case_authorization_summary": [
            {
                "case_id": record["case_id"],
                "taxonomy_group": record["taxonomy_group"],
                "next_phase_authorized": record["next_phase_authorized"],
                "authorized_next_phase": record["authorized_next_phase"],
                "authorization_scope": record["authorization_scope"],
                "sqlite_imported_this_phase": record["sqlite_imported_this_phase"],
                "sqlite_database_created_this_phase": record["sqlite_database_created_this_phase"],
                "database_connected_this_phase": record["database_connected_this_phase"],
                "sql_executed_this_phase": record["sql_executed_this_phase"],
                "passed": record["passed"],
            }
            for record in records
        ],
        "checks": checks,
        "final_verdict": (
            "READY_FOR_V0_4_2I_SQL_SAFETY_TEMP_SQLITE_SELECT_ONLY_FIRST_REAL_RUN"
            if status == "PASS"
            else "NEEDS_SQL_SAFETY_TEMP_SQLITE_SELECT_ONLY_AUTHORIZATION_GATE_FIX"
        ),
    }


def build_authorization_record(case_id: str) -> dict[str, Any]:
    record = {
        "authorization_gate": True,
        "case_id": case_id,
        "taxonomy_group": EXPECTED_CASES[case_id],
        "next_phase_authorized": True,
        "authorized_next_phase": AUTHORIZED_NEXT_PHASE,
        "authorization_scope": AUTHORIZATION_SCOPE,
        "sqlite_import_allowed_next_phase": True,
        "sqlite_imported_this_phase": False,
        "sqlite_database_created_this_phase": False,
        "database_connected_this_phase": False,
        "sql_executed_this_phase": False,
        "temp_directory_required": True,
        "randomized_filename_required": True,
        "user_path_allowed": False,
        "persistent_database_allowed": False,
        "network_database_allowed": False,
        "credential_allowed": False,
        "production_data_allowed": False,
        "select_only_required": True,
        "mutation_sql_allowed": False,
        "multiple_statements_allowed": False,
        "comments_hiding_mutation_allowed": False,
        "mutation_detection_required": True,
        "connection_close_required": True,
        "sandbox_delete_required": True,
        "sandbox_deletion_verification_required": True,
        "provider_invoked": False,
        "real_checker_invoked": False,
        "production_runner_invoked": False,
        "http_adapter_invoked": False,
        "external_mutation_detected": False,
        "authorization_events": [
            "case_loaded",
            "select_only_execution_stub_preflight_reused",
            "authorization_gate_record_created",
            "next_phase_scope_limited_to_temporary_local_sqlite_select_only",
            "sqlite_import_not_performed_this_phase",
            "database_creation_not_performed_this_phase",
            "database_connection_not_performed_this_phase",
            "sql_execution_not_performed_this_phase",
        ],
        "passed": False,
        "failed_checks": [],
    }
    record["passed"] = record_is_fail_closed(record)
    if not record["passed"]:
        record["failed_checks"].append("record_not_fail_closed")
    if unsafe_wording(record):
        record["failed_checks"].append("unsafe_record_wording")
    record["passed"] = not record["failed_checks"] and record_is_fail_closed(record)
    return record


def run_execution_stub_preflight() -> dict[str, Any]:
    module = load_module(EXECUTION_STUB_VALIDATION, "sql_safety_select_only_sqlite_execution_stub")
    if module is None or not hasattr(module, "main"):
        return {"status": "FAIL", "failed_checks": ["select_only_execution_stub_validation_load_failed"]}
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exit_code = module.main()
    try:
        result = json.loads(buffer.getvalue())
    except json.JSONDecodeError:
        return {"status": "FAIL", "failed_checks": ["select_only_execution_stub_validation_invalid_json"], "exit_code": exit_code}
    result["exit_code"] = exit_code
    if exit_code != 0:
        result["status"] = "FAIL"
    return result


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_record(checks: list[dict[str, Any]], record: dict[str, Any]) -> None:
    case_id = str(record.get("case_id", "unknown"))
    for field in REQUIRED_RECORD_FIELDS:
        add_check(checks, f"{case_id}.record_field.{field}", field in record, {"field": field})
    add_check(checks, f"{case_id}.taxonomy_group_abc", record.get("taxonomy_group") in {"A", "B", "C"}, record)
    add_check(checks, f"{case_id}.authorization_gate_true", record.get("authorization_gate") is True, record)
    add_check(checks, f"{case_id}.next_phase_authorized_true", record.get("next_phase_authorized") is True, record)
    add_check(checks, f"{case_id}.authorized_next_phase_exact", record.get("authorized_next_phase") == AUTHORIZED_NEXT_PHASE, record)
    add_check(checks, f"{case_id}.authorization_scope_exact", record.get("authorization_scope") == AUTHORIZATION_SCOPE, record)
    add_check(checks, f"{case_id}.sqlite_import_allowed_next_phase_true", record.get("sqlite_import_allowed_next_phase") is True, record)
    add_check(checks, f"{case_id}.sqlite_imported_this_phase_false", record.get("sqlite_imported_this_phase") is False, record)
    add_check(checks, f"{case_id}.sqlite_database_created_this_phase_false", record.get("sqlite_database_created_this_phase") is False, record)
    add_check(checks, f"{case_id}.database_connected_this_phase_false", record.get("database_connected_this_phase") is False, record)
    add_check(checks, f"{case_id}.sql_executed_this_phase_false", record.get("sql_executed_this_phase") is False, record)
    add_check(checks, f"{case_id}.temp_directory_required_true", record.get("temp_directory_required") is True, record)
    add_check(checks, f"{case_id}.randomized_filename_required_true", record.get("randomized_filename_required") is True, record)
    add_check(checks, f"{case_id}.user_path_allowed_false", record.get("user_path_allowed") is False, record)
    add_check(checks, f"{case_id}.persistent_database_allowed_false", record.get("persistent_database_allowed") is False, record)
    add_check(checks, f"{case_id}.network_database_allowed_false", record.get("network_database_allowed") is False, record)
    add_check(checks, f"{case_id}.credential_allowed_false", record.get("credential_allowed") is False, record)
    add_check(checks, f"{case_id}.production_data_allowed_false", record.get("production_data_allowed") is False, record)
    add_check(checks, f"{case_id}.select_only_required_true", record.get("select_only_required") is True, record)
    add_check(checks, f"{case_id}.mutation_sql_allowed_false", record.get("mutation_sql_allowed") is False, record)
    add_check(checks, f"{case_id}.multiple_statements_allowed_false", record.get("multiple_statements_allowed") is False, record)
    add_check(checks, f"{case_id}.comments_hiding_mutation_allowed_false", record.get("comments_hiding_mutation_allowed") is False, record)
    add_check(checks, f"{case_id}.mutation_detection_required_true", record.get("mutation_detection_required") is True, record)
    add_check(checks, f"{case_id}.connection_close_required_true", record.get("connection_close_required") is True, record)
    add_check(checks, f"{case_id}.sandbox_delete_required_true", record.get("sandbox_delete_required") is True, record)
    add_check(checks, f"{case_id}.sandbox_deletion_verification_required_true", record.get("sandbox_deletion_verification_required") is True, record)
    add_check(checks, f"{case_id}.provider_invoked_false", record.get("provider_invoked") is False, record)
    add_check(checks, f"{case_id}.real_checker_invoked_false", record.get("real_checker_invoked") is False, record)
    add_check(checks, f"{case_id}.production_runner_invoked_false", record.get("production_runner_invoked") is False, record)
    add_check(checks, f"{case_id}.http_adapter_invoked_false", record.get("http_adapter_invoked") is False, record)
    add_check(checks, f"{case_id}.external_mutation_detected_false", record.get("external_mutation_detected") is False, record)
    add_check(checks, f"{case_id}.failed_checks_empty", not record.get("failed_checks"), record)
    add_check(checks, f"{case_id}.passed", record.get("passed") is True, record)


def record_is_fail_closed(record: dict[str, Any]) -> bool:
    return (
        record.get("taxonomy_group") in {"A", "B", "C"}
        and record.get("authorization_gate") is True
        and record.get("next_phase_authorized") is True
        and record.get("authorized_next_phase") == AUTHORIZED_NEXT_PHASE
        and record.get("authorization_scope") == AUTHORIZATION_SCOPE
        and record.get("sqlite_import_allowed_next_phase") is True
        and record.get("sqlite_imported_this_phase") is False
        and record.get("sqlite_database_created_this_phase") is False
        and record.get("database_connected_this_phase") is False
        and record.get("sql_executed_this_phase") is False
        and record.get("temp_directory_required") is True
        and record.get("randomized_filename_required") is True
        and record.get("user_path_allowed") is False
        and record.get("persistent_database_allowed") is False
        and record.get("network_database_allowed") is False
        and record.get("credential_allowed") is False
        and record.get("production_data_allowed") is False
        and record.get("select_only_required") is True
        and record.get("mutation_sql_allowed") is False
        and record.get("multiple_statements_allowed") is False
        and record.get("comments_hiding_mutation_allowed") is False
        and record.get("mutation_detection_required") is True
        and record.get("connection_close_required") is True
        and record.get("sandbox_delete_required") is True
        and record.get("sandbox_deletion_verification_required") is True
        and record.get("provider_invoked") is False
        and record.get("real_checker_invoked") is False
        and record.get("production_runner_invoked") is False
        and record.get("http_adapter_invoked") is False
        and record.get("external_mutation_detected") is False
    )


def unsafe_wording(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True).lower()
    return any(pattern in text for pattern in UNSAFE_TEXT_PATTERNS)


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, details: dict[str, Any]) -> None:
    checks.append({"name": name, "passed": bool(passed), "details": details})
