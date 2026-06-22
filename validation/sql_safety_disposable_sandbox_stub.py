#!/usr/bin/env python3
"""Disposable SQL sandbox stub validation without database execution."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = REPO_ROOT / "cases" / "sql_safety"
DRY_FIRE_VALIDATION = REPO_ROOT / "validation" / "run_sql_safety_dry_fire_target_validation.py"

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
    "sandbox_mode",
    "sandbox_stub",
    "disposable_database",
    "real_database",
    "sqlite_database_created",
    "database_connected",
    "sql_executed",
    "mutation_attempted",
    "mutation_allowed",
    "mutation_detected",
    "rollback_performed",
    "sandbox_destroyed",
    "credential_used",
    "provider_invoked",
    "real_checker_invoked",
    "production_runner_invoked",
    "http_adapter_invoked",
    "agent_wrapper_invoked",
    "external_mutation_detected",
    "passed",
    "failed_checks",
]

UNSAFE_TEXT_PATTERNS = [
    "sqlite_database_created=true",
    "database_connected=true",
    "sql_executed=true",
    "mutation_detected=true",
    "credential_used=true",
    "provider_invoked=true",
    "real_checker_invoked=true",
    "production_runner_invoked=true",
    "http_adapter_invoked=true",
    "agent_wrapper_invoked=true",
    "external_mutation_detected=true",
    "created sqlite database",
    "opened database connection",
    "sql executed successfully",
    "executed sql against",
    "connected to database",
    "provider was invoked",
    "production runner invoked",
    "http adapter executed",
    "external mutation occurred",
]


def run_sql_safety_disposable_sandbox_stub() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    dry_fire_result = run_dry_fire_preflight()
    add_check(
        checks,
        "dry_fire_preflight_passed",
        dry_fire_result.get("status") == "PASS",
        {
            "status": dry_fire_result.get("status"),
            "failed_checks": dry_fire_result.get("failed_checks", []),
        },
    )

    observed_paths = sorted(CASE_DIR.glob("*.txt")) if CASE_DIR.exists() else []
    observed_case_ids = sorted(path.stem for path in observed_paths)
    dry_fire_case_ids = sorted(str(case_id) for case_id in dry_fire_result.get("case_ids", []))

    add_check(
        checks,
        "exact_sql_case_file_set",
        observed_case_ids == EXPECTED_CASE_IDS,
        {"expected": EXPECTED_CASE_IDS, "observed": observed_case_ids},
    )
    add_check(
        checks,
        "case_set_matches_dry_fire_validation",
        observed_case_ids == dry_fire_case_ids == EXPECTED_CASE_IDS,
        {
            "filesystem": observed_case_ids,
            "dry_fire": dry_fire_case_ids,
            "expected": EXPECTED_CASE_IDS,
        },
    )

    records = [build_stub_record(case_id) for case_id in EXPECTED_CASE_IDS]
    for record in records:
        validate_record(checks, record)

    add_check(checks, "no_unsafe_wording_in_sandbox_stub_records", not unsafe_wording(records), {})

    failed_checks = [check["name"] for check in checks if not check["passed"]]
    passed_cases = sorted(str(record["case_id"]) for record in records if record.get("passed") is True)
    status = "PASS" if not failed_checks and passed_cases == EXPECTED_CASE_IDS else "FAIL"
    return {
        "validation": "sql_safety_local_disposable_sandbox_stub_v042c",
        "status": status,
        "total_cases": len(records),
        "passed_cases": len(passed_cases),
        "failed_checks": failed_checks,
        "case_ids": EXPECTED_CASE_IDS,
        "case_set_consistency": observed_case_ids == dry_fire_case_ids == EXPECTED_CASE_IDS,
        "dry_fire_preflight_reused": True,
        "sandbox_stub": True,
        "sandbox_mode": True,
        "non_execution_confirmed": status == "PASS",
        "sqlite_database_created": False,
        "database_connected": False,
        "sql_executed": False,
        "mutation_detected": False,
        "credential_used": False,
        "provider_invoked": False,
        "real_checker_invoked": False,
        "production_runner_invoked": False,
        "http_adapter_invoked": False,
        "agent_wrapper_invoked": False,
        "external_mutation_detected": False,
        "records": records,
        "per_case_sandbox_stub_summary": [
            {
                "case_id": record["case_id"],
                "taxonomy_group": record["taxonomy_group"],
                "sandbox_mode": record["sandbox_mode"],
                "sandbox_stub": record["sandbox_stub"],
                "sqlite_database_created": record["sqlite_database_created"],
                "database_connected": record["database_connected"],
                "sql_executed": record["sql_executed"],
                "mutation_detected": record["mutation_detected"],
                "credential_used": record["credential_used"],
                "passed": record["passed"],
            }
            for record in records
        ],
        "checks": checks,
        "final_verdict": (
            "READY_FOR_V0_4_2D_SQL_SAFETY_LOCAL_SQLITE_SANDBOX_PLAN"
            if status == "PASS"
            else "NEEDS_SQL_SAFETY_LOCAL_DISPOSABLE_SANDBOX_STUB_FIX"
        ),
    }


def build_stub_record(case_id: str) -> dict[str, Any]:
    record = {
        "case_id": case_id,
        "taxonomy_group": EXPECTED_CASES[case_id],
        "sandbox_mode": True,
        "sandbox_stub": True,
        "disposable_database": True,
        "real_database": False,
        "sqlite_database_created": False,
        "database_connected": False,
        "sql_executed": False,
        "mutation_attempted": False,
        "mutation_allowed": False,
        "mutation_detected": False,
        "rollback_performed": False,
        "sandbox_destroyed": False,
        "credential_used": False,
        "provider_invoked": False,
        "real_checker_invoked": False,
        "production_runner_invoked": False,
        "http_adapter_invoked": False,
        "agent_wrapper_invoked": False,
        "external_mutation_detected": False,
        "lifecycle_events": [
            "case_loaded",
            "dry_fire_preflight_reused",
            "sandbox_stub_record_created",
            "sqlite_creation_skipped",
            "database_connection_skipped",
            "sql_execution_skipped",
            "rollback_skipped_because_no_sandbox_exists",
            "destroy_skipped_because_no_sandbox_exists",
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


def run_dry_fire_preflight() -> dict[str, Any]:
    module = load_module(DRY_FIRE_VALIDATION, "sql_safety_dry_fire_target_validation")
    if module is None or not hasattr(module, "main"):
        return {"status": "FAIL", "failed_checks": ["dry_fire_validation_load_failed"]}
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exit_code = module.main()
    try:
        result = json.loads(buffer.getvalue())
    except json.JSONDecodeError:
        return {"status": "FAIL", "failed_checks": ["dry_fire_validation_invalid_json"], "exit_code": exit_code}
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
    add_check(checks, f"{case_id}.sandbox_mode_true", record.get("sandbox_mode") is True, record)
    add_check(checks, f"{case_id}.sandbox_stub_true", record.get("sandbox_stub") is True, record)
    add_check(checks, f"{case_id}.disposable_database_true", record.get("disposable_database") is True, record)
    add_check(checks, f"{case_id}.real_database_false", record.get("real_database") is False, record)
    add_check(checks, f"{case_id}.sqlite_database_created_false", record.get("sqlite_database_created") is False, record)
    add_check(checks, f"{case_id}.database_connected_false", record.get("database_connected") is False, record)
    add_check(checks, f"{case_id}.sql_executed_false", record.get("sql_executed") is False, record)
    add_check(checks, f"{case_id}.mutation_attempted_false", record.get("mutation_attempted") is False, record)
    add_check(checks, f"{case_id}.mutation_allowed_false", record.get("mutation_allowed") is False, record)
    add_check(checks, f"{case_id}.mutation_detected_false", record.get("mutation_detected") is False, record)
    add_check(checks, f"{case_id}.rollback_performed_false", record.get("rollback_performed") is False, record)
    add_check(checks, f"{case_id}.sandbox_destroyed_false", record.get("sandbox_destroyed") is False, record)
    add_check(checks, f"{case_id}.credential_used_false", record.get("credential_used") is False, record)
    add_check(checks, f"{case_id}.provider_invoked_false", record.get("provider_invoked") is False, record)
    add_check(checks, f"{case_id}.real_checker_invoked_false", record.get("real_checker_invoked") is False, record)
    add_check(checks, f"{case_id}.production_runner_invoked_false", record.get("production_runner_invoked") is False, record)
    add_check(checks, f"{case_id}.http_adapter_invoked_false", record.get("http_adapter_invoked") is False, record)
    add_check(checks, f"{case_id}.agent_wrapper_invoked_false", record.get("agent_wrapper_invoked") is False, record)
    add_check(checks, f"{case_id}.external_mutation_detected_false", record.get("external_mutation_detected") is False, record)
    add_check(checks, f"{case_id}.failed_checks_empty", not record.get("failed_checks"), record)
    add_check(checks, f"{case_id}.passed", record.get("passed") is True, record)


def record_is_fail_closed(record: dict[str, Any]) -> bool:
    return (
        record.get("taxonomy_group") in {"A", "B", "C"}
        and record.get("sandbox_mode") is True
        and record.get("sandbox_stub") is True
        and record.get("disposable_database") is True
        and record.get("real_database") is False
        and record.get("sqlite_database_created") is False
        and record.get("database_connected") is False
        and record.get("sql_executed") is False
        and record.get("mutation_attempted") is False
        and record.get("mutation_allowed") is False
        and record.get("mutation_detected") is False
        and record.get("rollback_performed") is False
        and record.get("sandbox_destroyed") is False
        and record.get("credential_used") is False
        and record.get("provider_invoked") is False
        and record.get("real_checker_invoked") is False
        and record.get("production_runner_invoked") is False
        and record.get("http_adapter_invoked") is False
        and record.get("agent_wrapper_invoked") is False
        and record.get("external_mutation_detected") is False
    )


def unsafe_wording(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True).lower()
    return any(pattern in text for pattern in UNSAFE_TEXT_PATTERNS)


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, details: dict[str, Any]) -> None:
    checks.append({"name": name, "passed": bool(passed), "details": details})
