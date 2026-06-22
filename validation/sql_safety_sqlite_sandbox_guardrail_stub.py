#!/usr/bin/env python3
"""SQLite sandbox guardrail stub validation without SQLite execution."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = REPO_ROOT / "cases" / "sql_safety"
DISPOSABLE_STUB_VALIDATION = REPO_ROOT / "validation" / "run_sql_safety_local_disposable_sandbox_stub.py"

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
    "case_id",
    "taxonomy_group",
    "guardrail_stub",
    "sandbox_mode",
    "sqlite_sandbox_planned",
    "sqlite_imported",
    "sqlite_database_created",
    "database_connected",
    "sql_executed",
    "temp_directory_required",
    "randomized_filename_required",
    "user_path_allowed",
    "persistent_database_allowed",
    "network_database_allowed",
    "credential_used",
    "production_data_allowed",
    "select_only_first",
    "mutation_sql_allowed",
    "mutation_attempted",
    "mutation_detected",
    "rollback_performed",
    "sandbox_deleted",
    "sandbox_deletion_verified",
    "provider_invoked",
    "real_checker_invoked",
    "production_runner_invoked",
    "http_adapter_invoked",
    "external_mutation_detected",
    "passed",
    "failed_checks",
]

UNSAFE_TEXT_PATTERNS = [
    "sqlite_imported=true",
    "sqlite_database_created=true",
    "database_connected=true",
    "sql_executed=true",
    "user_path_allowed=true",
    "persistent_database_allowed=true",
    "network_database_allowed=true",
    "credential_used=true",
    "production_data_allowed=true",
    "mutation_sql_allowed=true",
    "mutation_detected=true",
    "provider_invoked=true",
    "real_checker_invoked=true",
    "production_runner_invoked=true",
    "http_adapter_invoked=true",
    "external_mutation_detected=true",
    "created sqlite database",
    "opened database connection",
    "sql executed successfully",
    "executed sql against",
    "used database credential",
    "provider was invoked",
    "production runner invoked",
    "http adapter executed",
    "external mutation occurred",
]


def run_sql_safety_sqlite_sandbox_guardrail_stub() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    disposable_stub_result = run_disposable_stub_preflight()
    add_check(
        checks,
        "disposable_sandbox_stub_preflight_passed",
        disposable_stub_result.get("status") == "PASS",
        {
            "status": disposable_stub_result.get("status"),
            "failed_checks": disposable_stub_result.get("failed_checks", []),
        },
    )

    observed_paths = sorted(CASE_DIR.glob("*.txt")) if CASE_DIR.exists() else []
    observed_case_ids = sorted(path.stem for path in observed_paths)
    stub_case_ids = sorted(str(case_id) for case_id in disposable_stub_result.get("case_ids", []))

    add_check(
        checks,
        "exact_sql_case_file_set",
        observed_case_ids == EXPECTED_CASE_IDS,
        {"expected": EXPECTED_CASE_IDS, "observed": observed_case_ids},
    )
    add_check(
        checks,
        "case_set_matches_disposable_sandbox_stub",
        observed_case_ids == stub_case_ids == EXPECTED_CASE_IDS,
        {
            "filesystem": observed_case_ids,
            "disposable_stub": stub_case_ids,
            "expected": EXPECTED_CASE_IDS,
        },
    )

    records = [build_guardrail_record(case_id) for case_id in EXPECTED_CASE_IDS]
    for record in records:
        validate_record(checks, record)

    add_check(checks, "no_unsafe_wording_in_guardrail_records", not unsafe_wording(records), {})

    failed_checks = [check["name"] for check in checks if not check["passed"]]
    passed_cases = sorted(str(record["case_id"]) for record in records if record.get("passed") is True)
    status = "PASS" if not failed_checks and passed_cases == EXPECTED_CASE_IDS else "FAIL"
    return {
        "validation": "sql_safety_sqlite_sandbox_guardrail_stub_v042e",
        "status": status,
        "total_cases": len(records),
        "passed_cases": len(passed_cases),
        "failed_checks": failed_checks,
        "case_ids": EXPECTED_CASE_IDS,
        "case_set_consistency": observed_case_ids == stub_case_ids == EXPECTED_CASE_IDS,
        "disposable_sandbox_stub_preflight_reused": True,
        "guardrail_stub": True,
        "sandbox_mode": True,
        "sqlite_sandbox_planned": True,
        "non_execution_confirmed": status == "PASS",
        "sqlite_imported": False,
        "sqlite_database_created": False,
        "database_connected": False,
        "sql_executed": False,
        "credential_used": False,
        "mutation_sql_allowed": False,
        "mutation_detected": False,
        "provider_invoked": False,
        "real_checker_invoked": False,
        "production_runner_invoked": False,
        "http_adapter_invoked": False,
        "external_mutation_detected": False,
        "records": records,
        "per_case_guardrail_summary": [
            {
                "case_id": record["case_id"],
                "taxonomy_group": record["taxonomy_group"],
                "guardrail_stub": record["guardrail_stub"],
                "sqlite_sandbox_planned": record["sqlite_sandbox_planned"],
                "sqlite_imported": record["sqlite_imported"],
                "sqlite_database_created": record["sqlite_database_created"],
                "database_connected": record["database_connected"],
                "sql_executed": record["sql_executed"],
                "select_only_first": record["select_only_first"],
                "mutation_sql_allowed": record["mutation_sql_allowed"],
                "passed": record["passed"],
            }
            for record in records
        ],
        "checks": checks,
        "final_verdict": (
            "READY_FOR_V0_4_2F_SQL_SAFETY_SELECT_ONLY_SQLITE_SANDBOX_DRY_RUN_PLAN"
            if status == "PASS"
            else "NEEDS_SQL_SAFETY_SQLITE_SANDBOX_GUARDRAIL_STUB_FIX"
        ),
    }


def build_guardrail_record(case_id: str) -> dict[str, Any]:
    record = {
        "case_id": case_id,
        "taxonomy_group": EXPECTED_CASES[case_id],
        "guardrail_stub": True,
        "sandbox_mode": True,
        "sqlite_sandbox_planned": True,
        "sqlite_imported": False,
        "sqlite_database_created": False,
        "database_connected": False,
        "sql_executed": False,
        "temp_directory_required": True,
        "randomized_filename_required": True,
        "user_path_allowed": False,
        "persistent_database_allowed": False,
        "network_database_allowed": False,
        "credential_used": False,
        "production_data_allowed": False,
        "select_only_first": True,
        "mutation_sql_allowed": False,
        "mutation_attempted": False,
        "mutation_detected": False,
        "rollback_performed": False,
        "sandbox_deleted": False,
        "sandbox_deletion_verified": False,
        "provider_invoked": False,
        "real_checker_invoked": False,
        "production_runner_invoked": False,
        "http_adapter_invoked": False,
        "external_mutation_detected": False,
        "guardrail_events": [
            "case_loaded",
            "disposable_sandbox_stub_preflight_reused",
            "guardrail_stub_record_created",
            "client_import_not_performed",
            "database_creation_not_performed",
            "database_connection_not_performed",
            "sql_execution_not_performed",
            "rollback_delete_not_performed",
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


def run_disposable_stub_preflight() -> dict[str, Any]:
    module = load_module(DISPOSABLE_STUB_VALIDATION, "sql_safety_local_disposable_sandbox_stub")
    if module is None or not hasattr(module, "main"):
        return {"status": "FAIL", "failed_checks": ["disposable_stub_validation_load_failed"]}
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exit_code = module.main()
    try:
        result = json.loads(buffer.getvalue())
    except json.JSONDecodeError:
        return {"status": "FAIL", "failed_checks": ["disposable_stub_validation_invalid_json"], "exit_code": exit_code}
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
    add_check(checks, f"{case_id}.guardrail_stub_true", record.get("guardrail_stub") is True, record)
    add_check(checks, f"{case_id}.sandbox_mode_true", record.get("sandbox_mode") is True, record)
    add_check(checks, f"{case_id}.sqlite_sandbox_planned_true", record.get("sqlite_sandbox_planned") is True, record)
    add_check(checks, f"{case_id}.sqlite_imported_false", record.get("sqlite_imported") is False, record)
    add_check(checks, f"{case_id}.sqlite_database_created_false", record.get("sqlite_database_created") is False, record)
    add_check(checks, f"{case_id}.database_connected_false", record.get("database_connected") is False, record)
    add_check(checks, f"{case_id}.sql_executed_false", record.get("sql_executed") is False, record)
    add_check(checks, f"{case_id}.temp_directory_required_true", record.get("temp_directory_required") is True, record)
    add_check(checks, f"{case_id}.randomized_filename_required_true", record.get("randomized_filename_required") is True, record)
    add_check(checks, f"{case_id}.user_path_allowed_false", record.get("user_path_allowed") is False, record)
    add_check(checks, f"{case_id}.persistent_database_allowed_false", record.get("persistent_database_allowed") is False, record)
    add_check(checks, f"{case_id}.network_database_allowed_false", record.get("network_database_allowed") is False, record)
    add_check(checks, f"{case_id}.credential_used_false", record.get("credential_used") is False, record)
    add_check(checks, f"{case_id}.production_data_allowed_false", record.get("production_data_allowed") is False, record)
    add_check(checks, f"{case_id}.select_only_first_true", record.get("select_only_first") is True, record)
    add_check(checks, f"{case_id}.mutation_sql_allowed_false", record.get("mutation_sql_allowed") is False, record)
    add_check(checks, f"{case_id}.mutation_attempted_false", record.get("mutation_attempted") is False, record)
    add_check(checks, f"{case_id}.mutation_detected_false", record.get("mutation_detected") is False, record)
    add_check(checks, f"{case_id}.rollback_performed_false", record.get("rollback_performed") is False, record)
    add_check(checks, f"{case_id}.sandbox_deleted_false", record.get("sandbox_deleted") is False, record)
    add_check(checks, f"{case_id}.sandbox_deletion_verified_false", record.get("sandbox_deletion_verified") is False, record)
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
        and record.get("guardrail_stub") is True
        and record.get("sandbox_mode") is True
        and record.get("sqlite_sandbox_planned") is True
        and record.get("sqlite_imported") is False
        and record.get("sqlite_database_created") is False
        and record.get("database_connected") is False
        and record.get("sql_executed") is False
        and record.get("temp_directory_required") is True
        and record.get("randomized_filename_required") is True
        and record.get("user_path_allowed") is False
        and record.get("persistent_database_allowed") is False
        and record.get("network_database_allowed") is False
        and record.get("credential_used") is False
        and record.get("production_data_allowed") is False
        and record.get("select_only_first") is True
        and record.get("mutation_sql_allowed") is False
        and record.get("mutation_attempted") is False
        and record.get("mutation_detected") is False
        and record.get("rollback_performed") is False
        and record.get("sandbox_deleted") is False
        and record.get("sandbox_deletion_verified") is False
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
