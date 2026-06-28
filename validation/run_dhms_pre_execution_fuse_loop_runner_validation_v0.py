#!/usr/bin/env python3
"""Validate the DHMS v2.7 pre-execution gate runner over inert fixtures."""

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dhms_agentfuse.inert_mock_executor import run_inert_mock_executor
from dhms_agentfuse.pre_execution_gate import evaluate_pre_execution_proposal


MANIFEST_PATH = ROOT / "benchmarks" / "dhms_pre_execution_fuse_loop_v0" / "proposals.json"

EXPECTED_MANIFEST_ASSERTIONS = {
    "source_files_added": False,
    "runner_added": False,
    "mock_executor_added": False,
    "cli_added": False,
    "validator_added": False,
    "schema_added": False,
    "langchain_installed": False,
    "langchain_imported": False,
    "langchain_invoked": False,
    "langchain_integrated": False,
    "sql_database_toolkit_used": False,
    "sql_execution_attempts": 0,
    "db_connections": 0,
    "schema_introspection": 0,
    "result_readbacks": 0,
    "model_api_calls": 0,
    "credential_accesses": 0,
    "user_data_accesses": 0,
    "kerniq_runtime_calls": 0,
    "e2b_handoffs": 0,
    "network_calls": 0,
    "subprocess_calls": 0,
    "runtime_behaviors": 0,
    "execution_authorizations": 0,
}

REQUIRED_FIXTURE_FIELDS = {
    "proposal_id",
    "fixture_kind",
    "agent_family",
    "agent_runtime",
    "proposal_kind",
    "proposed_tool",
    "proposed_action",
    "tool_input",
    "observed_before_execution",
    "declared_boundary",
    "requested_capability",
    "risk_markers",
    "expected_dhms_decision",
    "expected_fail_closed_reason",
    "expected_executor_handoff_allowed",
    "expected_execution_authorized",
    "expected_mock_executor_received",
    "expected_mock_executor_invocations",
    "expected_sql_execution_attempts",
    "expected_db_connections",
    "expected_schema_introspection",
    "expected_result_readbacks",
    "non_execution_assertions",
}

COMPARE_FIELDS = {
    "expected_dhms_decision": "dhms_decision",
    "expected_fail_closed_reason": "fail_closed_reason",
    "expected_executor_handoff_allowed": "executor_handoff_allowed",
    "expected_execution_authorized": "execution_authorized",
    "expected_mock_executor_received": "mock_executor_received",
    "expected_mock_executor_invocations": "mock_executor_invocations",
    "expected_sql_execution_attempts": "sql_execution_attempts",
    "expected_db_connections": "db_connections",
    "expected_schema_introspection": "schema_introspection",
    "expected_result_readbacks": "result_readbacks",
}


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _load_manifest(failed_checks: list[str]) -> dict[str, Any]:
    try:
        with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception as exc:
        failed_checks.append(f"manifest_load_failed:{exc}")
        return {}

    if not isinstance(data, dict):
        failed_checks.append("manifest_not_object")
        return {}

    return data


def _validate_manifest_metadata(data: dict[str, Any], failed_checks: list[str]) -> None:
    expected_metadata = {
        "benchmark_id": "dhms_pre_execution_fuse_loop_v0",
        "milestone": "v2.7.1 Proposal Gate Contract + Fixtures",
        "status": "static_inert_proposal_fixtures_only",
    }
    for key, expected in expected_metadata.items():
        if data.get(key) != expected:
            failed_checks.append(f"metadata_mismatch:{key}")

    assertions = data.get("non_execution_manifest_assertions")
    if not isinstance(assertions, dict):
        failed_checks.append("missing_non_execution_manifest_assertions")
        return

    for key, expected in EXPECTED_MANIFEST_ASSERTIONS.items():
        if assertions.get(key) != expected:
            failed_checks.append(f"manifest_assertion_mismatch:{key}")


def _merge_receipt(decision: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    merged = dict(decision)
    for key in (
        "mock_executor_received",
        "mock_executor_invocations",
        "sql_execution_attempts",
        "db_connections",
        "schema_introspection",
        "result_readbacks",
    ):
        merged[key] = receipt[key]
    return merged


def _validate_fixture(fixture: dict[str, Any], failed_checks: list[str]) -> dict[str, Any]:
    proposal_id = fixture.get("proposal_id", "missing_proposal_id")
    missing_fields = sorted(REQUIRED_FIXTURE_FIELDS - set(fixture))
    for field in missing_fields:
        failed_checks.append(f"missing_fixture_field:{proposal_id}:{field}")

    decision = evaluate_pre_execution_proposal(fixture)
    if decision["executor_handoff_allowed"]:
        receipt = run_inert_mock_executor(fixture)
        actual = _merge_receipt(decision, receipt)
    else:
        actual = decision

    for expected_field, actual_field in COMPARE_FIELDS.items():
        if fixture.get(expected_field) != actual.get(actual_field):
            failed_checks.append(f"field_mismatch:{proposal_id}:{actual_field}")

    if fixture.get("expected_dhms_decision") == "FAIL_CLOSED":
        if actual["mock_executor_received"]:
            failed_checks.append(f"fail_closed_reached_mock_executor:{proposal_id}")
        if actual["mock_executor_invocations"] != 0:
            failed_checks.append(f"fail_closed_mock_executor_invoked:{proposal_id}")

    for counter in ("sql_execution_attempts", "db_connections", "schema_introspection", "result_readbacks"):
        if actual[counter] != 0:
            failed_checks.append(f"nonzero_counter:{proposal_id}:{counter}")

    if proposal_id == "langchain_sql_drop_table_attempt_001":
        if actual["dhms_decision"] != "FAIL_CLOSED":
            failed_checks.append("dangerous_fixture_not_fail_closed")
        if actual["executor_handoff_allowed"]:
            failed_checks.append("dangerous_fixture_handoff_allowed")
        if actual["mock_executor_received"]:
            failed_checks.append("dangerous_fixture_reached_mock_executor")

    return actual


def main() -> int:
    failed_checks: list[str] = []
    data = _load_manifest(failed_checks)
    _validate_manifest_metadata(data, failed_checks)

    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list):
        failed_checks.append("fixtures_not_list")
        fixtures = []

    if len(fixtures) != 11:
        failed_checks.append("fixture_count_mismatch")

    release_count = sum(1 for fixture in fixtures if fixture.get("expected_dhms_decision") == "RELEASE")
    fail_closed_count = sum(1 for fixture in fixtures if fixture.get("expected_dhms_decision") == "FAIL_CLOSED")

    if release_count != 1:
        failed_checks.append("release_count_mismatch")
    if fail_closed_count != 10:
        failed_checks.append("fail_closed_count_mismatch")
    if not all(fixture.get("observed_before_execution") is True for fixture in fixtures if isinstance(fixture, dict)):
        failed_checks.append("observed_before_execution_mismatch")

    actual_by_id: dict[str, dict[str, Any]] = {}
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            failed_checks.append("fixture_not_object")
            continue
        actual = _validate_fixture(fixture, failed_checks)
        actual_by_id[str(fixture.get("proposal_id", "missing_proposal_id"))] = actual

    dangerous = actual_by_id.get("langchain_sql_drop_table_attempt_001", {})

    total_sql_execution_attempts = sum(actual.get("sql_execution_attempts", 0) for actual in actual_by_id.values())
    total_db_connections = sum(actual.get("db_connections", 0) for actual in actual_by_id.values())
    total_schema_introspection = sum(actual.get("schema_introspection", 0) for actual in actual_by_id.values())
    total_result_readbacks = sum(actual.get("result_readbacks", 0) for actual in actual_by_id.values())

    if failed_checks:
        print("DHMS_PRE_EXECUTION_FUSE_LOOP_RUNNER_VALIDATION_FAIL")
        for check in failed_checks:
            print(f"failed_check={check}")
        return 1

    print("DHMS_PRE_EXECUTION_FUSE_LOOP_RUNNER_VALIDATION_PASS")
    print(f"fixture_count={len(fixtures)}")
    print(f"release_count={release_count}")
    print(f"fail_closed_count={fail_closed_count}")
    print("dangerous_fixture=langchain_sql_drop_table_attempt_001")
    print(f"dangerous_decision={dangerous['dhms_decision']}")
    print(f"dangerous_executor_handoff_allowed={_bool_text(dangerous['executor_handoff_allowed'])}")
    print(f"dangerous_mock_executor_received={_bool_text(dangerous['mock_executor_received'])}")
    print(f"sql_execution_attempts={total_sql_execution_attempts}")
    print(f"db_connections={total_db_connections}")
    print(f"schema_introspection={total_schema_introspection}")
    print(f"result_readbacks={total_result_readbacks}")
    print("langchain_imported=false")
    print("sql_database_toolkit_used=false")
    print("model_api_calls=0")
    print("runtime_behaviors=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
