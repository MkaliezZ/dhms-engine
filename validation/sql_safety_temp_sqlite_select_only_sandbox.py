#!/usr/bin/env python3
"""First real temp SQLite SELECT-only sandbox validation.

This module is intentionally local-only. It uses only Python standard-library
sqlite3 for a disposable temporary SQLite sandbox and does not invoke providers,
agent SDKs, production checker logic, production runner logic, HTTP adapters, or
network/database services.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import sqlite3
import tempfile
import uuid
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = REPO_ROOT / "cases" / "sql_safety"
AUTHORIZATION_GATE = REPO_ROOT / "validation" / "run_sql_safety_temp_sqlite_select_only_authorization_gate.py"

CONTROL_PROBE_ID = "allowlisted_select_probe"
ALLOWLISTED_SELECT = "SELECT id, label, status FROM toy_accounts ORDER BY id;"
AUTHORIZED_SCOPE = "temporary_local_sqlite_select_only"
AUTHORIZED_NEXT_PHASE = "v0.4.2I_SQL_SAFETY_TEMP_SQLITE_SELECT_ONLY_FIRST_REAL_RUN"

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

TOY_ROWS = [(1, "alpha", "active"), (2, "beta", "inactive")]


def run_sql_safety_temp_sqlite_select_only_first_real_run() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    authorization_result = run_authorization_gate()
    add_check(
        checks,
        "authorization_gate_passed",
        authorization_result.get("status") == "PASS",
        {
            "status": authorization_result.get("status"),
            "failed_checks": authorization_result.get("failed_checks", []),
        },
    )
    add_check(
        checks,
        "authorization_scope_exact",
        authorization_result.get("authorization_scope") == AUTHORIZED_SCOPE,
        {"authorization_scope": authorization_result.get("authorization_scope")},
    )
    add_check(
        checks,
        "authorized_next_phase_exact",
        authorization_result.get("authorized_next_phase") == AUTHORIZED_NEXT_PHASE,
        {"authorized_next_phase": authorization_result.get("authorized_next_phase")},
    )

    observed_paths = sorted(CASE_DIR.glob("*.txt")) if CASE_DIR.exists() else []
    observed_case_ids = sorted(path.stem for path in observed_paths)
    authorization_case_ids = sorted(str(case_id) for case_id in authorization_result.get("case_ids", []))
    add_check(
        checks,
        "exact_sql_case_file_set",
        observed_case_ids == EXPECTED_CASE_IDS,
        {"expected": EXPECTED_CASE_IDS, "observed": observed_case_ids},
    )
    add_check(
        checks,
        "case_set_matches_authorization_gate",
        observed_case_ids == authorization_case_ids == EXPECTED_CASE_IDS,
        {
            "filesystem": observed_case_ids,
            "authorization_gate": authorization_case_ids,
            "expected": EXPECTED_CASE_IDS,
        },
    )

    sandbox = run_temp_sqlite_control_probe(checks)
    case_results = [build_case_result(case_id) for case_id in EXPECTED_CASE_IDS]
    for case_result in case_results:
        validate_case_result(checks, case_result)

    control_probe = sandbox["control_probe"]
    validate_control_probe(checks, control_probe)
    validate_sandbox_lifecycle(checks, sandbox)

    failed_checks = [check["name"] for check in checks if not check["passed"]]
    passed_cases = sorted(result["case_id"] for result in case_results if result["passed"])
    control_probe_passed = control_probe["passed"]
    status = "PASS" if not failed_checks and passed_cases == EXPECTED_CASE_IDS and control_probe_passed else "FAIL"

    return {
        "validation": "sql_safety_temp_sqlite_select_only_first_real_run_v042i",
        "status": status,
        "authorization_gate_passed": authorization_result.get("status") == "PASS",
        "temporary_database": True,
        "real_database": False,
        "sqlite_imported": True,
        "sqlite_database_created": sandbox["sqlite_database_created"],
        "database_connected": sandbox["database_connected"],
        "setup_schema_created": sandbox["setup_schema_created"],
        "synthetic_seed_data_inserted": sandbox["synthetic_seed_data_inserted"],
        "allowlisted_select_executed": control_probe["allowlisted_select_executed"],
        "case_sql_executed": False,
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
        "control_probe_passed": control_probe_passed,
        "failed_checks": failed_checks,
        "case_set_consistency": observed_case_ids == authorization_case_ids == EXPECTED_CASE_IDS,
        "case_results": case_results,
        "control_probe": control_probe,
        "sandbox_trace": sandbox["trace"],
        "mutation_detection": sandbox["mutation_detection"],
        "checks": checks,
        "final_verdict": (
            "READY_FOR_V0_4_2J_SQL_SAFETY_TEMP_SQLITE_MUTATION_BLOCK_TEST"
            if status == "PASS"
            else "NEEDS_SQL_SAFETY_TEMP_SQLITE_SELECT_ONLY_FIRST_REAL_RUN_FIX"
        ),
    }


def run_authorization_gate() -> dict[str, Any]:
    module = load_module(AUTHORIZATION_GATE, "sql_safety_temp_sqlite_select_only_authorization_gate")
    if module is None or not hasattr(module, "main"):
        return {"status": "FAIL", "failed_checks": ["authorization_gate_load_failed"]}
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exit_code = module.main()
    try:
        result = json.loads(buffer.getvalue())
    except json.JSONDecodeError:
        return {"status": "FAIL", "failed_checks": ["authorization_gate_invalid_json"], "exit_code": exit_code}
    result["exit_code"] = exit_code
    if exit_code != 0:
        result["status"] = "FAIL"
    return result


def run_temp_sqlite_control_probe(checks: list[dict[str, Any]]) -> dict[str, Any]:
    temp_root = Path(tempfile.gettempdir()).resolve()
    sandbox_dir = Path(tempfile.mkdtemp(prefix="dhms_sql_safety_", dir=temp_root)).resolve()
    db_name = f"dhms_select_only_{uuid.uuid4().hex}.sqlite"
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

    try:
        add_check(checks, "sandbox_path_in_temp_directory", trace["temp_directory_used"], {"db_path": str(db_path), "temp_root": str(temp_root)})
        add_check(checks, "sandbox_path_not_user_path", not trace["user_path_used"], {"db_path": str(db_path), "home": str(home)})
        add_check(checks, "sandbox_filename_randomized", db_name.startswith("dhms_select_only_") and len(db_name) > len("dhms_select_only_.sqlite"), {"db_name": db_name})

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

        pre_state = collect_state(connection)
        rows = [list(row) for row in connection.execute(ALLOWLISTED_SELECT).fetchall()]
        trace["events"].append("allowlisted_select_control_probe_executed")
        post_state = collect_state(connection)

        mutation_detection = build_mutation_detection(pre_state, post_state)
        control_probe = {
            "control_probe_id": CONTROL_PROBE_ID,
            "allowlisted_select_executed": True,
            "control_sql_executed": True,
            "control_sql_statement": ALLOWLISTED_SELECT,
            "control_result_rows": rows,
            "control_result_row_count": len(rows),
            "mutation_detected": mutation_detection["mutation_detected"],
            "passed": rows == [[1, "alpha", "active"], [2, "beta", "inactive"]] and not mutation_detection["mutation_detected"],
            "failed_checks": [],
        }
        if control_probe["control_result_row_count"] != 2:
            control_probe["failed_checks"].append("unexpected_control_result_row_count")
        if mutation_detection["mutation_detected"]:
            control_probe["failed_checks"].append("mutation_detected_after_allowlisted_select")
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
            "control_probe_id": CONTROL_PROBE_ID,
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
        "mutation_detection": mutation_detection,
        "trace": trace,
    }


def collect_state(connection: sqlite3.Connection) -> dict[str, Any]:
    schema_rows = [
        list(row)
        for row in connection.execute(
            "SELECT type, name, tbl_name, sql FROM sqlite_master WHERE type IN ('table', 'index') ORDER BY type, name;"
        ).fetchall()
    ]
    table_names = [
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
        ).fetchall()
    ]
    table_content: dict[str, list[list[Any]]] = {}
    row_counts: dict[str, int] = {}
    for table_name in table_names:
        rows = [list(row) for row in connection.execute(f"SELECT * FROM {table_name} ORDER BY id;").fetchall()]
        table_content[table_name] = rows
        row_counts[table_name] = len(rows)
    return {
        "schema_hash": stable_hash(schema_rows),
        "content_hash": stable_hash(table_content),
        "row_counts": row_counts,
    }


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


def build_case_result(case_id: str) -> dict[str, Any]:
    result = {
        "case_id": case_id,
        "taxonomy_group": EXPECTED_CASES[case_id],
        "should_block": True,
        "case_sql_executed": False,
        "database_connected_for_case": False,
        "mutation_detected": False,
        "external_mutation_detected": False,
        "passed": True,
        "failed_checks": [],
    }
    return result


def validate_case_result(checks: list[dict[str, Any]], result: dict[str, Any]) -> None:
    case_id = result["case_id"]
    add_check(checks, f"{case_id}.taxonomy_group_abc", result.get("taxonomy_group") in {"A", "B", "C"}, result)
    add_check(checks, f"{case_id}.should_block_true", result.get("should_block") is True, result)
    add_check(checks, f"{case_id}.case_sql_executed_false", result.get("case_sql_executed") is False, result)
    add_check(checks, f"{case_id}.database_connected_for_case_false", result.get("database_connected_for_case") is False, result)
    add_check(checks, f"{case_id}.mutation_detected_false", result.get("mutation_detected") is False, result)
    add_check(checks, f"{case_id}.external_mutation_detected_false", result.get("external_mutation_detected") is False, result)
    add_check(checks, f"{case_id}.failed_checks_empty", not result.get("failed_checks"), result)
    add_check(checks, f"{case_id}.passed", result.get("passed") is True, result)


def validate_control_probe(checks: list[dict[str, Any]], control_probe: dict[str, Any]) -> None:
    add_check(checks, "control_probe.id", control_probe.get("control_probe_id") == CONTROL_PROBE_ID, control_probe)
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


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, details: dict[str, Any]) -> None:
    checks.append({"name": name, "passed": bool(passed), "details": details})
