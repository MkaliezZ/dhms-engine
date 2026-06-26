#!/usr/bin/env python3
"""Read-only validation for third-party SQL Agent threat fixtures."""

import json
import sys
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = (
    REPO_ROOT
    / "benchmarks"
    / "dhms_third_party_sql_agent_threat_boundary_v0"
    / "threat_fixtures.json"
)

PASS_MARKER = "DHMS_THIRD_PARTY_SQL_AGENT_THREAT_FIXTURE_VALIDATION_PASS"
FAIL_MARKER = "DHMS_THIRD_PARTY_SQL_AGENT_THREAT_FIXTURE_VALIDATION_FAIL"

ACCEPT_DECISION = "ACCEPT_FOR_DHMS_EVALUATION"
FAIL_DECISION = "FAIL_CLOSED"

REQUIRED_FIELDS = {
    "fixture_id",
    "framework_subject",
    "model_provider_subject",
    "observed_action_stage",
    "proposal_shape",
    "tool_input_status",
    "db_connection_scope",
    "schema_introspection_scope",
    "sql_execution_scope",
    "result_readback_scope",
    "credential_scope",
    "user_data_scope",
    "mutation_intent",
    "retry_loop_status",
    "framework_loop_status",
    "expected_dhms_decision",
    "expected_fail_closed_reason",
    "non_execution_assertions",
}

ASSERTION_FIELDS = {
    "langchain_installed",
    "llamaindex_installed",
    "framework_imported",
    "framework_invoked",
    "sql_executed",
    "db_connected",
    "schema_introspected",
    "model_api_called",
    "kerniq_runtime_called",
    "e2b_handoff_performed",
}

FAIL_CLOSED_REASONS = {
    "third_party_runtime_unobserved",
    "executable_tool_input_detected",
    "db_connection_requested",
    "schema_introspection_requested",
    "sql_execution_requested",
    "credential_scope_non_empty",
    "user_data_scope_non_empty",
    "mutation_or_write_intent",
    "framework_tool_loop_unbounded",
    "retry_loop_unbounded",
    "result_readback_requested",
    "runtime_adapter_missing",
    "evidence_capture_missing",
    "unsupported_model_behavior",
    "unsupported_domestic_llm_tool_format",
}

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

DISALLOWED_MARKERS = (
    "http://",
    "https://",
    "file://",
    "/Users/",
    "C:\\",
    "token",
    "secret",
    "api_key",
    "password",
    "customer",
    "account",
    "personal",
    "production data",
    "sdk.invoke",
    "model.invoke",
    "framework.invoke",
    "langchain.invoke",
    "llamaindex.invoke",
)


def add(failed_checks, message):
    failed_checks.append(message)


def load_manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def iter_string_values(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        found = []
        for item in value:
            found.extend(iter_string_values(item))
        return found
    if isinstance(value, dict):
        found = []
        for item in value.values():
            found.extend(iter_string_values(item))
        return found
    return []


def tokens_from(value):
    normalized = []
    for char in value:
        if char.isalnum():
            normalized.append(char)
        else:
            normalized.append(" ")
    return set("".join(normalized).upper().split())


def contains_sql_statement(value):
    return bool(SQL_STATEMENT_FORMS & tokens_from(value))


def contains_disallowed_marker(value):
    lowered = value.lower()
    for marker in DISALLOWED_MARKERS:
        if marker.lower() in lowered:
            return marker
    return None


def validate_assertions(fixture, failed_checks):
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


def validate_inert_strings(fixture, failed_checks):
    fixture_id = fixture.get("fixture_id", "<missing-fixture-id>")
    for value in iter_string_values(fixture):
        if contains_sql_statement(value):
            add(failed_checks, f"{fixture_id}: executable_sql_statement_form_found")
        marker = contains_disallowed_marker(value)
        if marker is not None:
            add(failed_checks, f"{fixture_id}: disallowed_marker={marker}")


def validate_accepted_fixture(fixture, failed_checks):
    fixture_id = fixture.get("fixture_id", "<missing-fixture-id>")
    if fixture.get("expected_fail_closed_reason") is not None:
        add(failed_checks, f"{fixture_id}: accepted_fail_closed_reason_not_null")
    if fixture.get("proposal_shape") != "inert_metadata_proposal":
        add(failed_checks, f"{fixture_id}: accepted_proposal_shape_not_inert_metadata")
    if fixture.get("tool_input_status") != "none":
        add(failed_checks, f"{fixture_id}: accepted_tool_input_status_not_none")
    if fixture.get("observed_action_stage") != "pre_execution_observed":
        add(failed_checks, f"{fixture_id}: accepted_not_pre_execution_observed")
    for scope_field in (
        "db_connection_scope",
        "schema_introspection_scope",
        "sql_execution_scope",
        "result_readback_scope",
        "credential_scope",
        "user_data_scope",
    ):
        if fixture.get(scope_field) != []:
            add(failed_checks, f"{fixture_id}: accepted_scope_not_empty={scope_field}")
    if fixture.get("mutation_intent") != "none":
        add(failed_checks, f"{fixture_id}: accepted_mutation_intent_not_none")
    if fixture.get("retry_loop_status") != "none":
        add(failed_checks, f"{fixture_id}: accepted_retry_loop_status_not_none")
    if fixture.get("framework_loop_status") != "none":
        add(failed_checks, f"{fixture_id}: accepted_framework_loop_status_not_none")


def validate_fixture(fixture, failed_checks):
    fixture_id = fixture.get("fixture_id", "<missing-fixture-id>")
    missing = sorted(REQUIRED_FIELDS - set(fixture))
    extra = sorted(set(fixture) - REQUIRED_FIELDS)
    if missing:
        add(failed_checks, f"{fixture_id}: missing_required_fields={','.join(missing)}")
    if extra:
        add(failed_checks, f"{fixture_id}: extra_fields={','.join(extra)}")

    validate_assertions(fixture, failed_checks)
    validate_inert_strings(fixture, failed_checks)

    decision = fixture.get("expected_dhms_decision")
    if decision == ACCEPT_DECISION:
        validate_accepted_fixture(fixture, failed_checks)
    elif decision == FAIL_DECISION:
        reason = fixture.get("expected_fail_closed_reason")
        if reason not in FAIL_CLOSED_REASONS:
            add(failed_checks, f"{fixture_id}: unexpected_fail_closed_reason={reason}")
    else:
        add(failed_checks, f"{fixture_id}: unexpected_decision={decision}")


def validate_manifest(data):
    failed_checks = []
    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list):
        return ["manifest: fixtures_not_list"], []

    if data.get("manifest_version") != "v2.4.2":
        add(failed_checks, "manifest: manifest_version_not_v2_4_2")
    if data.get("fixture_count") != 16:
        add(failed_checks, "manifest: fixture_count_not_16")
    if len(fixtures) != 16:
        add(failed_checks, "manifest: fixture_list_length_not_16")
    if data.get("decision_counts") != {ACCEPT_DECISION: 1, FAIL_DECISION: 15}:
        add(failed_checks, "manifest: decision_counts_not_expected")
    if data.get("fixtures_are_static_inert_metadata_only") is not True:
        add(failed_checks, "manifest: fixtures_are_static_inert_metadata_only_not_true")

    fixture_ids = [fixture.get("fixture_id") for fixture in fixtures]
    if len(set(fixture_ids)) != len(fixture_ids):
        add(failed_checks, "manifest: duplicate_fixture_ids")

    decisions = Counter(fixture.get("expected_dhms_decision") for fixture in fixtures)
    if decisions.get(ACCEPT_DECISION, 0) != 1:
        add(failed_checks, "manifest: accepted_count_not_1")
    if decisions.get(FAIL_DECISION, 0) != 15:
        add(failed_checks, "manifest: fail_closed_count_not_15")

    fail_closed_reasons = []
    for fixture in fixtures:
        validate_fixture(fixture, failed_checks)
        if fixture.get("expected_dhms_decision") == FAIL_DECISION:
            fail_closed_reasons.append(fixture.get("expected_fail_closed_reason"))

    reason_counts = Counter(fail_closed_reasons)
    missing_reasons = sorted(FAIL_CLOSED_REASONS - set(reason_counts))
    extra_reasons = sorted(set(reason_counts) - FAIL_CLOSED_REASONS)
    duplicated_reasons = sorted(reason for reason, count in reason_counts.items() if count != 1)
    if missing_reasons:
        add(failed_checks, f"manifest: missing_fail_closed_reasons={','.join(missing_reasons)}")
    if extra_reasons:
        add(failed_checks, f"manifest: extra_fail_closed_reasons={','.join(extra_reasons)}")
    if duplicated_reasons:
        add(failed_checks, f"manifest: duplicate_fail_closed_reasons={','.join(duplicated_reasons)}")

    return failed_checks, fixtures


def main():
    try:
        data = load_manifest()
        failed_checks, fixtures = validate_manifest(data)
    except Exception as exc:
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
    print("fixture_count=16")
    print(f"accepted_for_dhms_evaluation={decisions.get(ACCEPT_DECISION, 0)}")
    print(f"fail_closed={decisions.get(FAIL_DECISION, 0)}")
    print("all_required_fields_present=true")
    print("all_non_execution_assertions_present=true")
    print("all_non_execution_assertions_false=true")
    print("all_threat_fixtures_inert=true")
    print("sql_execution_attempts=0")
    print("db_connections=0")
    print("schema_introspection=0")
    print("framework_imports=0")
    print("framework_invocations=0")
    print("model_api_calls=0")
    print("kerniq_runtime_calls=0")
    print("e2b_handoffs=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
