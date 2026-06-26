#!/usr/bin/env python3
"""Read-only validation for DHMS SQL Agent local emit-only fixtures.

This validator reads only the committed static fixture manifest and treats all
SQL-agent proposal fields as inert metadata. It does not execute SQL, connect to
databases, inspect schemas, call runtimes, or dereference any declared metadata.
"""

from __future__ import annotations

from collections import Counter
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = (
    REPO_ROOT
    / "benchmarks"
    / "dhms_sql_agent_local_emit_only_v0"
    / "proposals.json"
)

PASS_MARKER = "DHMS_SQL_AGENT_LOCAL_EMIT_ONLY_FIXTURE_VALIDATION_PASS"
FAIL_MARKER = "DHMS_SQL_AGENT_LOCAL_EMIT_ONLY_FIXTURE_VALIDATION_FAIL"

REQUIRED_FIELDS = {
    "fixture_id",
    "fixture_purpose",
    "proposal_id",
    "agent_profile",
    "natural_language_request",
    "sql_dialect",
    "sql_candidate",
    "sql_operation_type",
    "declared_tables",
    "declared_columns",
    "declared_side_effects",
    "read_write_class",
    "risk_markers",
    "where_clause_present",
    "limit_clause_present",
    "credential_scope",
    "user_data_scope",
    "db_connection_scope",
    "schema_source",
    "runtime_target",
    "dry_run",
    "expected_dhms_decision",
    "expected_fail_closed_reason",
    "non_execution_assertions",
}

ASSERTION_FIELDS = {
    "sql_execution",
    "db_connection",
    "schema_introspection",
    "real_schema_access",
    "real_data_access",
    "database_mutation",
    "sqlite_postgres_mysql_client",
    "orm_usage",
    "langchain_usage",
    "llamaindex_usage",
    "sqldatabasetoolkit_usage",
    "subprocess_usage",
    "shell_execution",
    "command_execution",
    "file_mutation",
    "network_access",
    "env_access",
    "credential_access",
    "user_data_access",
    "sdk_model_runtime_access",
    "kerniq_runtime_call",
    "e2b_handoff",
}

EXPECTED_FAIL_CLOSED_REASONS = {
    "dry_run_not_true",
    "db_connection_scope_non_empty",
    "credential_scope_non_empty",
    "user_data_scope_non_empty",
    "runtime_target_not_no_runtime",
    "schema_source_real_schema_claim",
    "sql_execution_requested",
    "database_mutation_without_safe_boundary",
    "third_party_or_external_runtime_marker",
}

ALLOWED_DECISIONS = {"ACCEPT_FOR_DHMS_EVALUATION", "FAIL_CLOSED"}
ACCEPT_DECISION = "ACCEPT_FOR_DHMS_EVALUATION"
FAIL_DECISION = "FAIL_CLOSED"
THIRD_PARTY_MARKER_FIXTURE_ID = "sql_agent_fail_third_party_or_external_runtime_marker"

SQL_STATEMENT_FORMS = {
    "SELECT",
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "MERGE",
    "EXEC",
    "CALL",
}

REAL_WORLD_MARKERS = (
    "http://",
    "https://",
    "file://",
    "/Users/",
    "C:\\",
    "token",
    "secret",
    "API_KEY",
    "password",
    "customer",
    "account",
    "personal",
    "production data",
)

THIRD_PARTY_MARKERS = (
    "langchain",
    "llamaindex",
    "sqldatabasetoolkit",
    "kerniq",
    "e2b",
)


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def add(failed_checks: list[str], message: str) -> None:
    failed_checks.append(message)


def iter_string_values(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        found: list[str] = []
        for item in value:
            found.extend(iter_string_values(item))
        return found
    if isinstance(value, dict):
        found = []
        for item in value.values():
            found.extend(iter_string_values(item))
        return found
    return []


def tokenize_statement_words(value: str) -> set[str]:
    normalized = []
    for char in value:
        if char.isalnum() or char == "_":
            normalized.append(char)
        else:
            normalized.append(" ")
    return {part.upper() for part in "".join(normalized).split()}


def has_sql_statement_form(value: str) -> bool:
    return bool(SQL_STATEMENT_FORMS & tokenize_statement_words(value))


def has_real_world_marker(value: str) -> str | None:
    lowered = value.lower()
    for marker in REAL_WORLD_MARKERS:
        if marker.lower() in lowered:
            return marker
    return None


def is_inert_sql_candidate(value: object) -> bool:
    return isinstance(value, str) and value.startswith("inert_sql_intent_")


def is_synthetic_list(value: object, prefix: str) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, str) and item.startswith(prefix) for item in value
    )


def validate_assertions(fixture: dict, failed_checks: list[str]) -> None:
    fixture_id = fixture.get("fixture_id", "<missing-fixture-id>")
    assertions = fixture.get("non_execution_assertions")
    if not isinstance(assertions, dict):
        add(failed_checks, f"{fixture_id}: non_execution_assertions_not_object")
        return

    missing = sorted(ASSERTION_FIELDS - set(assertions))
    extra = sorted(set(assertions) - ASSERTION_FIELDS)
    if missing:
        add(failed_checks, f"{fixture_id}: missing_non_execution_assertions={','.join(missing)}")
    if extra:
        add(failed_checks, f"{fixture_id}: extra_non_execution_assertions={','.join(extra)}")

    for field in sorted(ASSERTION_FIELDS):
        if assertions.get(field) is not False:
            add(failed_checks, f"{fixture_id}: non_execution_assertion_not_false={field}")


def validate_marker_boundary(fixture: dict, failed_checks: list[str]) -> None:
    fixture_id = fixture.get("fixture_id", "<missing-fixture-id>")
    for value in iter_string_values(fixture):
        if has_sql_statement_form(value):
            add(failed_checks, f"{fixture_id}: executable_sql_statement_form_found")
        marker = has_real_world_marker(value)
        if marker is not None:
            add(failed_checks, f"{fixture_id}: real_world_marker_found={marker}")
        lowered = value.lower()
        if any(marker in lowered for marker in THIRD_PARTY_MARKERS):
            if fixture_id != THIRD_PARTY_MARKER_FIXTURE_ID:
                add(failed_checks, f"{fixture_id}: third_party_marker_outside_expected_fixture")
            elif not (
                value.startswith("inert_marker_")
                or value == "third_party_or_external_runtime_marker"
                or value == fixture_id
                or value.startswith("inert_sql_intent_")
            ):
                add(failed_checks, f"{fixture_id}: third_party_marker_not_inert")


def validate_accepted_fixture(fixture: dict, failed_checks: list[str]) -> None:
    fixture_id = fixture.get("fixture_id", "<missing-fixture-id>")
    if fixture.get("dry_run") is not True:
        add(failed_checks, f"{fixture_id}: accepted_dry_run_not_true")
    if fixture.get("db_connection_scope") != []:
        add(failed_checks, f"{fixture_id}: accepted_db_connection_scope_not_empty")
    if fixture.get("credential_scope") != []:
        add(failed_checks, f"{fixture_id}: accepted_credential_scope_not_empty")
    if fixture.get("user_data_scope") != []:
        add(failed_checks, f"{fixture_id}: accepted_user_data_scope_not_empty")
    if fixture.get("schema_source") not in {"synthetic", "declared-only"}:
        add(failed_checks, f"{fixture_id}: accepted_schema_source_not_synthetic_or_declared_only")
    if fixture.get("runtime_target") != "no-runtime":
        add(failed_checks, f"{fixture_id}: accepted_runtime_target_not_no_runtime")
    if not is_inert_sql_candidate(fixture.get("sql_candidate")):
        add(failed_checks, f"{fixture_id}: accepted_sql_candidate_not_inert_marker")
    if not is_synthetic_list(fixture.get("declared_tables"), "synthetic_table_"):
        add(failed_checks, f"{fixture_id}: accepted_declared_tables_not_synthetic")
    if not is_synthetic_list(fixture.get("declared_columns"), "synthetic_column_"):
        add(failed_checks, f"{fixture_id}: accepted_declared_columns_not_synthetic")
    if fixture.get("expected_dhms_decision") != ACCEPT_DECISION:
        add(failed_checks, f"{fixture_id}: accepted_decision_not_accept")
    if fixture.get("expected_fail_closed_reason") is not None:
        add(failed_checks, f"{fixture_id}: accepted_fail_closed_reason_not_null")


def validate_fixture(fixture: dict, failed_checks: list[str]) -> None:
    fixture_id = fixture.get("fixture_id", "<missing-fixture-id>")
    missing = sorted(REQUIRED_FIELDS - set(fixture))
    extra = sorted(set(fixture) - REQUIRED_FIELDS)
    if missing:
        add(failed_checks, f"{fixture_id}: missing_required_fields={','.join(missing)}")
    if extra:
        add(failed_checks, f"{fixture_id}: extra_fields={','.join(extra)}")

    validate_assertions(fixture, failed_checks)
    validate_marker_boundary(fixture, failed_checks)

    decision = fixture.get("expected_dhms_decision")
    if decision not in ALLOWED_DECISIONS:
        add(failed_checks, f"{fixture_id}: unexpected_decision={decision}")
    if decision == ACCEPT_DECISION:
        validate_accepted_fixture(fixture, failed_checks)
    if decision == FAIL_DECISION and not fixture.get("expected_fail_closed_reason"):
        add(failed_checks, f"{fixture_id}: fail_closed_reason_missing")


def validate_manifest(data: dict) -> tuple[list[str], list[dict]]:
    failed_checks: list[str] = []
    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list):
        return ["manifest: fixtures_not_list"], []

    if data.get("manifest_version") != "v2.3.2":
        add(failed_checks, "manifest: manifest_version_not_v2_3_2")
    if data.get("fixture_count") != 10:
        add(failed_checks, "manifest: fixture_count_not_10")
    if len(fixtures) != 10:
        add(failed_checks, "manifest: fixture_list_length_not_10")
    if data.get("fixtures_are_inert_metadata_only") is not True:
        add(failed_checks, "manifest: fixtures_are_inert_metadata_only_not_true")

    manifest_status_counts = data.get("status_counts")
    if manifest_status_counts != {ACCEPT_DECISION: 1, FAIL_DECISION: 9}:
        add(failed_checks, "manifest: status_counts_not_expected")

    fixture_ids = [fixture.get("fixture_id") for fixture in fixtures]
    proposal_ids = [fixture.get("proposal_id") for fixture in fixtures]
    if len(set(fixture_ids)) != len(fixture_ids):
        add(failed_checks, "manifest: duplicate_fixture_ids")
    if len(set(proposal_ids)) != len(proposal_ids):
        add(failed_checks, "manifest: duplicate_proposal_ids")

    decisions = Counter(fixture.get("expected_dhms_decision") for fixture in fixtures)
    if decisions.get(ACCEPT_DECISION, 0) != 1:
        add(failed_checks, "manifest: accepted_count_not_1")
    if decisions.get(FAIL_DECISION, 0) != 9:
        add(failed_checks, "manifest: fail_closed_count_not_9")

    fail_closed_reasons = set()
    for fixture in fixtures:
        validate_fixture(fixture, failed_checks)
        if fixture.get("expected_dhms_decision") == FAIL_DECISION:
            reason = fixture.get("expected_fail_closed_reason")
            if reason:
                fail_closed_reasons.add(reason)

    missing_reasons = sorted(EXPECTED_FAIL_CLOSED_REASONS - fail_closed_reasons)
    extra_reasons = sorted(fail_closed_reasons - EXPECTED_FAIL_CLOSED_REASONS)
    if missing_reasons:
        add(failed_checks, f"manifest: missing_fail_closed_reasons={','.join(missing_reasons)}")
    if extra_reasons:
        add(failed_checks, f"manifest: extra_fail_closed_reasons={','.join(extra_reasons)}")

    return failed_checks, fixtures


def main() -> int:
    try:
        data = load_manifest()
        failed_checks, fixtures = validate_manifest(data)
    except Exception as exc:  # pragma: no cover - deterministic failure path.
        print(FAIL_MARKER)
        print(f"failed_check=exception:{type(exc).__name__}:{exc}")
        return 1

    decisions = Counter(fixture.get("expected_dhms_decision") for fixture in fixtures)

    if failed_checks:
        print(FAIL_MARKER)
        for failed_check in sorted(failed_checks):
            print(f"failed_check={failed_check}")
        return 1

    print(PASS_MARKER)
    print("fixture_count=10")
    print(f"accepted_for_dhms_evaluation={decisions.get(ACCEPT_DECISION, 0)}")
    print(f"fail_closed={decisions.get(FAIL_DECISION, 0)}")
    print("all_required_fields_present=true")
    print("all_non_execution_assertions_present=true")
    print("all_sql_candidates_inert=true")
    print("sql_execution_attempts=0")
    print("db_connections=0")
    print("schema_introspection=0")
    print("langchain_runtime_calls=0")
    print("llamaindex_runtime_calls=0")
    print("kerniq_runtime_calls=0")
    print("e2b_handoffs=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
