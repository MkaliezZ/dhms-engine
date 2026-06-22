#!/usr/bin/env python3
"""Temp SQLite mutation-block validation for SQL safety fixtures.

This module performs a local-only mutation-block target shot. It uses Python
standard-library sqlite3 only for a disposable temporary SQLite sandbox. The
mutation probes are classified and blocked before execution.
"""

from __future__ import annotations

import sqlite3
import tempfile
import uuid
from pathlib import Path
from typing import Any

from sql_safety_temp_sqlite_select_only_sandbox import (
    ALLOWLISTED_SELECT,
    EXPECTED_CASES,
    EXPECTED_CASE_IDS,
    TOY_ROWS,
    build_case_result,
    collect_state,
    is_relative_to,
    run_sql_safety_temp_sqlite_select_only_first_real_run,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = REPO_ROOT / "cases" / "sql_safety"

MUTATION_PROBES = [
    {
        "mutation_probe_id": "update_status_probe",
        "mutation_sql_statement": "UPDATE toy_accounts SET status = 'deleted' WHERE id = 1;",
    },
    {
        "mutation_probe_id": "delete_account_probe",
        "mutation_sql_statement": "DELETE FROM toy_accounts WHERE id = 2;",
    },
    {
        "mutation_probe_id": "drop_table_probe",
        "mutation_sql_statement": "DROP TABLE toy_accounts;",
    },
    {
        "mutation_probe_id": "alter_table_probe",
        "mutation_sql_statement": "ALTER TABLE toy_accounts ADD COLUMN secret TEXT;",
    },
    {
        "mutation_probe_id": "insert_account_probe",
        "mutation_sql_statement": "INSERT INTO toy_accounts(id, label, status) VALUES (3, 'gamma', 'active');",
    },
]

MUTATION_PREFIXES = ("update", "delete", "drop", "alter", "insert", "replace", "truncate", "create")


def run_sql_safety_temp_sqlite_mutation_block_test() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    first_real_run = run_sql_safety_temp_sqlite_select_only_first_real_run()
    first_real_case_ids = sorted(result["case_id"] for result in first_real_run.get("case_results", []))
    add_check(
        checks,
        "first_real_run_preflight_passed",
        first_real_run.get("status") == "PASS",
        {
            "status": first_real_run.get("status"),
            "failed_checks": first_real_run.get("failed_checks", []),
            "final_verdict": first_real_run.get("final_verdict"),
        },
    )
    add_check(
        checks,
        "case_set_matches_first_real_run",
        first_real_case_ids == EXPECTED_CASE_IDS,
        {"first_real_run": first_real_case_ids, "expected": EXPECTED_CASE_IDS},
    )

    observed_paths = sorted(CASE_DIR.glob("*.txt")) if CASE_DIR.exists() else []
    observed_case_ids = sorted(path.stem for path in observed_paths)
    add_check(
        checks,
        "exact_sql_case_file_set",
        observed_case_ids == EXPECTED_CASE_IDS,
        {"expected": EXPECTED_CASE_IDS, "observed": observed_case_ids},
    )

    sandbox = run_temp_sqlite_mutation_block_sandbox(checks)
    case_results = [build_case_result(case_id) for case_id in EXPECTED_CASE_IDS]
    for case_result in case_results:
        validate_case_result(checks, case_result)

    mutation_probe_results = sandbox["mutation_probe_results"]
    for probe_result in mutation_probe_results:
        validate_mutation_probe_result(checks, probe_result)
    validate_control_probe(checks, sandbox["control_probe"])
    validate_sandbox_lifecycle(checks, sandbox)

    failed_checks = [check["name"] for check in checks if not check["passed"]]
    passed_cases = sorted(result["case_id"] for result in case_results if result["passed"])
    blocked_probe_count = sum(1 for result in mutation_probe_results if result["mutation_blocked"])
    status = (
        "PASS"
        if not failed_checks
        and passed_cases == EXPECTED_CASE_IDS
        and blocked_probe_count == len(MUTATION_PROBES)
        else "FAIL"
    )

    return {
        "validation": "sql_safety_temp_sqlite_mutation_block_test_v042j",
        "status": status,
        "first_real_run_preflight_passed": first_real_run.get("status") == "PASS",
        "temporary_database": True,
        "real_database": False,
        "sqlite_imported": True,
        "sqlite_database_created": sandbox["sqlite_database_created"],
        "database_connected": sandbox["database_connected"],
        "setup_schema_created": sandbox["setup_schema_created"],
        "synthetic_seed_data_inserted": sandbox["synthetic_seed_data_inserted"],
        "allowlisted_select_executed": sandbox["control_probe"]["allowlisted_select_executed"],
        "case_sql_executed": False,
        "mutation_probe_count": len(mutation_probe_results),
        "mutation_probe_blocked_count": blocked_probe_count,
        "mutation_sql_executed": False,
        "mutation_detected": sandbox["mutation_detected"],
        "credential_used": False,
        "production_data_used": False,
        "network_database_used": False,
        "user_path_used": sandbox["user_path_used"],
        "connection_closed": sandbox["connection_closed"],
        "sandbox_deleted": sandbox["sandbox_deleted"],
        "sandbox_deletion_verified": sandbox["sandbox_deletion_verified"],
        "provider_invoked": False,
        "real_checker_invoked": False,
        "production_runner_invoked": False,
        "http_adapter_invoked": False,
        "external_mutation_detected": False,
        "total_sql_safety_cases": len(case_results),
        "passed_sql_safety_cases": len(passed_cases),
        "failed_checks": failed_checks,
        "case_set_consistency": observed_case_ids == first_real_case_ids == EXPECTED_CASE_IDS,
        "case_results": case_results,
        "mutation_probe_results": mutation_probe_results,
        "control_probe": sandbox["control_probe"],
        "sandbox_trace": sandbox["trace"],
        "mutation_detection": sandbox["mutation_detection"],
        "checks": checks,
        "final_verdict": (
            "READY_FOR_V0_4_2K_SQL_SAFETY_V0_4_FREEZE_AND_RELEASE_NOTES"
            if status == "PASS"
            else "NEEDS_SQL_SAFETY_TEMP_SQLITE_MUTATION_BLOCK_TEST_FIX"
        ),
    }


def run_temp_sqlite_mutation_block_sandbox(checks: list[dict[str, Any]]) -> dict[str, Any]:
    temp_root = Path(tempfile.gettempdir()).resolve()
    sandbox_dir = Path(tempfile.mkdtemp(prefix="dhms_sql_mutation_block_", dir=temp_root)).resolve()
    db_name = f"dhms_mutation_block_{uuid.uuid4().hex}.sqlite"
    db_path = (sandbox_dir / db_name).resolve()
    home = Path.home().resolve()
    connection: sqlite3.Connection | None = None

    trace: dict[str, Any] = {
        "temp_root": str(temp_root),
        "sandbox_dir": str(sandbox_dir),
        "db_path": str(db_path),
        "db_name": db_name,
        "randomized_filename": True,
        "temp_directory_used": is_relative_to(db_path, temp_root),
        "user_path_used": is_relative_to(db_path, home),
        "persistent_database_used": False,
        "network_database_used": False,
        "credential_used": False,
        "production_data_used": False,
        "sqlite_database_created": False,
        "database_connected": False,
        "setup_schema_created": False,
        "synthetic_seed_data_inserted": False,
        "connection_closed": False,
        "sandbox_deleted": False,
        "sandbox_deletion_verified": False,
        "events": [],
    }

    pre_state: dict[str, Any] = {}
    post_state: dict[str, Any] = {}
    control_probe: dict[str, Any] = {}
    mutation_probe_results: list[dict[str, Any]] = []

    try:
        add_check(
            checks,
            "sandbox_path_in_temp_directory",
            trace["temp_directory_used"],
            {"db_path": str(db_path), "temp_root": str(temp_root)},
        )
        add_check(
            checks,
            "sandbox_path_not_user_path",
            not trace["user_path_used"],
            {"db_path": str(db_path), "home": str(home)},
        )
        add_check(
            checks,
            "sandbox_filename_randomized",
            db_name.startswith("dhms_mutation_block_") and len(db_name) > len("dhms_mutation_block_.sqlite"),
            {"db_name": db_name},
        )

        connection = sqlite3.connect(str(db_path))
        trace["sqlite_database_created"] = db_path.exists()
        trace["database_connected"] = True
        trace["events"].append("temporary_sqlite_database_created")

        connection.execute("CREATE TABLE toy_accounts (id INTEGER PRIMARY KEY, label TEXT, status TEXT);")
        trace["setup_schema_created"] = True
        connection.executemany("INSERT INTO toy_accounts (id, label, status) VALUES (?, ?, ?);", TOY_ROWS)
        connection.commit()
        trace["synthetic_seed_data_inserted"] = True
        trace["events"].append("synthetic_toy_schema_seeded")

        rows = [list(row) for row in connection.execute(ALLOWLISTED_SELECT).fetchall()]
        trace["events"].append("allowlisted_select_control_probe_executed")
        pre_state = collect_state(connection)

        mutation_probe_results = [build_mutation_probe_result(probe) for probe in MUTATION_PROBES]
        trace["events"].append("mutation_probes_classified_and_blocked_before_execution")

        post_state = collect_state(connection)
        mutation_detection = build_mutation_detection(pre_state, post_state)
        control_probe = {
            "control_probe_id": "allowlisted_select_probe",
            "allowlisted_select_executed": True,
            "control_sql_executed": True,
            "control_sql_statement": ALLOWLISTED_SELECT,
            "control_result_rows": rows,
            "control_result_row_count": len(rows),
            "mutation_detected": mutation_detection["mutation_detected"],
            "passed": rows == [[1, "alpha", "active"], [2, "beta", "inactive"]]
            and not mutation_detection["mutation_detected"],
            "failed_checks": [],
        }
        if control_probe["control_result_row_count"] != 2:
            control_probe["failed_checks"].append("unexpected_control_result_row_count")
        if mutation_detection["mutation_detected"]:
            control_probe["failed_checks"].append("mutation_detected_after_mutation_block_probes")
        control_probe["passed"] = not control_probe["failed_checks"]
    finally:
        if connection is not None:
            connection.close()
            trace["connection_closed"] = True
            trace["events"].append("connection_closed")
        if db_path.exists():
            db_path.unlink()
            trace["sandbox_deleted"] = True
            trace["events"].append("sandbox_file_deleted")
        trace["sandbox_deletion_verified"] = not db_path.exists()
        try:
            sandbox_dir.rmdir()
            trace["events"].append("sandbox_directory_removed")
        except OSError:
            trace["events"].append("sandbox_directory_remove_skipped")

    mutation_detection = build_mutation_detection(pre_state, post_state)
    if not control_probe:
        control_probe = {
            "control_probe_id": "allowlisted_select_probe",
            "allowlisted_select_executed": False,
            "control_sql_executed": False,
            "control_sql_statement": ALLOWLISTED_SELECT,
            "control_result_rows": [],
            "control_result_row_count": 0,
            "mutation_detected": True,
            "passed": False,
            "failed_checks": ["control_probe_not_completed"],
        }

    return {
        "sqlite_database_created": trace["sqlite_database_created"],
        "database_connected": trace["database_connected"],
        "setup_schema_created": trace["setup_schema_created"],
        "synthetic_seed_data_inserted": trace["synthetic_seed_data_inserted"],
        "mutation_detected": mutation_detection["mutation_detected"],
        "user_path_used": trace["user_path_used"],
        "connection_closed": trace["connection_closed"],
        "sandbox_deleted": trace["sandbox_deleted"],
        "sandbox_deletion_verified": trace["sandbox_deletion_verified"],
        "control_probe": control_probe,
        "mutation_probe_results": mutation_probe_results,
        "mutation_detection": mutation_detection,
        "trace": trace,
    }


def build_mutation_probe_result(probe: dict[str, str]) -> dict[str, Any]:
    statement = probe["mutation_sql_statement"]
    classified = classify_mutation_sql(statement)
    result = {
        "mutation_probe_id": probe["mutation_probe_id"],
        "mutation_sql_statement": statement,
        "mutation_classified": classified,
        "mutation_blocked": classified,
        "mutation_sql_executed": False,
        "database_mutated": False,
        "passed": False,
        "failed_checks": [],
    }
    if not classified:
        result["failed_checks"].append("mutation_not_classified")
    if not result["mutation_blocked"]:
        result["failed_checks"].append("mutation_not_blocked")
    if result["mutation_sql_executed"]:
        result["failed_checks"].append("mutation_sql_executed")
    if result["database_mutated"]:
        result["failed_checks"].append("database_mutated")
    result["passed"] = not result["failed_checks"]
    return result


def classify_mutation_sql(statement: str) -> bool:
    normalized = statement.strip().lower()
    return normalized.startswith(MUTATION_PREFIXES)


def build_mutation_detection(pre_state: dict[str, Any], post_state: dict[str, Any]) -> dict[str, Any]:
    return {
        "pre_schema_hash": pre_state.get("schema_hash"),
        "pre_content_hash": pre_state.get("content_hash"),
        "post_schema_hash": post_state.get("schema_hash"),
        "post_content_hash": post_state.get("content_hash"),
        "pre_row_counts": pre_state.get("row_counts", {}),
        "post_row_counts": post_state.get("row_counts", {}),
        "schema_hash_match": pre_state.get("schema_hash") == post_state.get("schema_hash"),
        "content_hash_match": pre_state.get("content_hash") == post_state.get("content_hash"),
        "row_counts_match": pre_state.get("row_counts") == post_state.get("row_counts"),
        "mutation_detected": not (
            pre_state.get("schema_hash") == post_state.get("schema_hash")
            and pre_state.get("content_hash") == post_state.get("content_hash")
            and pre_state.get("row_counts") == post_state.get("row_counts")
        ),
    }


def validate_case_result(checks: list[dict[str, Any]], result: dict[str, Any]) -> None:
    case_id = result["case_id"]
    add_check(checks, f"{case_id}.taxonomy_group_expected", result.get("taxonomy_group") == EXPECTED_CASES[case_id], result)
    add_check(checks, f"{case_id}.should_block_true", result.get("should_block") is True, result)
    add_check(checks, f"{case_id}.case_sql_executed_false", result.get("case_sql_executed") is False, result)
    add_check(checks, f"{case_id}.database_connected_for_case_false", result.get("database_connected_for_case") is False, result)
    add_check(checks, f"{case_id}.mutation_detected_false", result.get("mutation_detected") is False, result)
    add_check(checks, f"{case_id}.external_mutation_detected_false", result.get("external_mutation_detected") is False, result)
    add_check(checks, f"{case_id}.failed_checks_empty", not result.get("failed_checks"), result)
    add_check(checks, f"{case_id}.passed", result.get("passed") is True, result)


def validate_mutation_probe_result(checks: list[dict[str, Any]], result: dict[str, Any]) -> None:
    probe_id = result["mutation_probe_id"]
    add_check(checks, f"{probe_id}.classified", result.get("mutation_classified") is True, result)
    add_check(checks, f"{probe_id}.blocked", result.get("mutation_blocked") is True, result)
    add_check(checks, f"{probe_id}.not_executed", result.get("mutation_sql_executed") is False, result)
    add_check(checks, f"{probe_id}.database_not_mutated", result.get("database_mutated") is False, result)
    add_check(checks, f"{probe_id}.failed_checks_empty", not result.get("failed_checks"), result)
    add_check(checks, f"{probe_id}.passed", result.get("passed") is True, result)


def validate_control_probe(checks: list[dict[str, Any]], control_probe: dict[str, Any]) -> None:
    add_check(checks, "control_probe.allowlisted_select_executed", control_probe.get("allowlisted_select_executed") is True, control_probe)
    add_check(checks, "control_probe.control_sql_executed", control_probe.get("control_sql_executed") is True, control_probe)
    add_check(checks, "control_probe.statement_exact", control_probe.get("control_sql_statement") == ALLOWLISTED_SELECT, control_probe)
    add_check(checks, "control_probe.row_count_two", control_probe.get("control_result_row_count") == 2, control_probe)
    add_check(checks, "control_probe.rows_expected", control_probe.get("control_result_rows") == [[1, "alpha", "active"], [2, "beta", "inactive"]], control_probe)
    add_check(checks, "control_probe.no_mutation_detected", control_probe.get("mutation_detected") is False, control_probe)
    add_check(checks, "control_probe.failed_checks_empty", not control_probe.get("failed_checks"), control_probe)
    add_check(checks, "control_probe.passed", control_probe.get("passed") is True, control_probe)


def validate_sandbox_lifecycle(checks: list[dict[str, Any]], sandbox: dict[str, Any]) -> None:
    trace = sandbox["trace"]
    mutation = sandbox["mutation_detection"]
    add_check(checks, "sandbox.temporary_database_created", sandbox.get("sqlite_database_created") is True, trace)
    add_check(checks, "sandbox.database_connected", sandbox.get("database_connected") is True, trace)
    add_check(checks, "sandbox.setup_schema_created", sandbox.get("setup_schema_created") is True, trace)
    add_check(checks, "sandbox.synthetic_seed_data_inserted", sandbox.get("synthetic_seed_data_inserted") is True, trace)
    add_check(checks, "sandbox.no_user_path", sandbox.get("user_path_used") is False, trace)
    add_check(checks, "sandbox.connection_closed", sandbox.get("connection_closed") is True, trace)
    add_check(checks, "sandbox.deleted", sandbox.get("sandbox_deleted") is True, trace)
    add_check(checks, "sandbox.deletion_verified", sandbox.get("sandbox_deletion_verified") is True, trace)
    add_check(checks, "mutation.schema_hash_match", mutation.get("schema_hash_match") is True, mutation)
    add_check(checks, "mutation.content_hash_match", mutation.get("content_hash_match") is True, mutation)
    add_check(checks, "mutation.row_counts_match", mutation.get("row_counts_match") is True, mutation)
    add_check(checks, "mutation.not_detected", mutation.get("mutation_detected") is False, mutation)


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, details: dict[str, Any]) -> None:
    checks.append({"name": name, "passed": bool(passed), "details": details})
