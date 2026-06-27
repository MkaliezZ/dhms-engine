#!/usr/bin/env python3
"""Read-only validation for LangChain SQL Agent emit-only adapter fixtures."""

import json
import sys
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = (
    REPO_ROOT
    / "benchmarks"
    / "dhms_langchain_sql_agent_emit_only_adapter_v0"
    / "adapter_boundary_fixtures.json"
)

PASS_MARKER = "DHMS_LANGCHAIN_SQL_AGENT_EMIT_ONLY_ADAPTER_FIXTURE_VALIDATION_PASS"
FAIL_MARKER = "DHMS_LANGCHAIN_SQL_AGENT_EMIT_ONLY_ADAPTER_FIXTURE_VALIDATION_FAIL"

REQUIRED_FIXTURE_FIELDS = [
    "fixture_id",
    "adapter_subject",
    "framework_subject",
    "model_provider_subject",
    "observed_action_stage",
    "proposal_source",
    "proposal_shape",
    "tool_input_status",
    "sql_text_status",
    "db_connection_scope",
    "schema_introspection_scope",
    "sql_execution_scope",
    "result_readback_scope",
    "credential_scope",
    "user_data_scope",
    "mutation_intent",
    "framework_loop_status",
    "retry_loop_status",
    "expected_dhms_decision",
    "expected_fail_closed_reason",
    "non_execution_assertions",
]

REQUIRED_ASSERTION_FIELDS = [
    "langchain_installed",
    "langchain_imported",
    "langchain_invoked",
    "langchain_integrated",
    "sql_database_toolkit_used",
    "executable_tool_input_generated",
    "sql_executed",
    "db_connected",
    "schema_introspected",
    "result_readback_performed",
    "model_api_called",
    "credential_accessed",
    "user_data_accessed",
    "kerniq_runtime_called",
    "e2b_handoff_performed",
    "runtime_behavior_added",
]

REQUIRED_FAIL_CLOSED_REASONS = [
    "langchain_runtime_unobserved",
    "executable_tool_input_detected",
    "sql_database_toolkit_detected",
    "db_connection_requested",
    "schema_introspection_requested",
    "sql_execution_requested",
    "result_readback_requested",
    "credential_scope_non_empty",
    "user_data_scope_non_empty",
    "mutation_or_write_intent",
    "framework_tool_loop_unbounded",
    "retry_loop_unbounded",
    "adapter_boundary_missing",
    "evidence_capture_missing",
    "unsupported_model_behavior",
    "unsupported_langchain_tool_format",
]

EXPECTED_ACCEPTED_VALUES = {
    "fixture_id": "langchain_emit_only_accept_inert_adapter_metadata",
    "adapter_subject": "synthetic_langchain_sql_agent_emit_only_adapter_candidate",
    "framework_subject": "synthetic_langchain_sql_agent_framework_subject",
    "model_provider_subject": "synthetic_model_provider_subject",
    "observed_action_stage": "pre_execution_observed",
    "proposal_source": "synthetic_langchain_sql_agent_proposal_surface",
    "proposal_shape": "inert_adapter_metadata",
    "tool_input_status": "none",
    "sql_text_status": "inert_metadata_only",
    "db_connection_scope": [],
    "schema_introspection_scope": [],
    "sql_execution_scope": [],
    "result_readback_scope": [],
    "credential_scope": [],
    "user_data_scope": [],
    "mutation_intent": "none",
    "framework_loop_status": "none",
    "retry_loop_status": "none",
    "expected_dhms_decision": "ACCEPT_FOR_DHMS_EVALUATION",
    "expected_fail_closed_reason": None,
}

EXPECTED_DECISION_COUNTS = {
    "ACCEPT_FOR_DHMS_EVALUATION": 1,
    "FAIL_CLOSED": 16,
}

SQL_STATEMENT_FORMS = [
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
]

DISALLOWED_RUNTIME_PATTERNS = [
    "import langchain",
    "from langchain",
    "pip install langchain",
    "poetry add langchain",
    "langchain.invoke",
    "langchain.run",
    "sqldatabasetoolkit(",
    "sqldatabase.from_uri",
    "create_sql_agent",
    "agentexecutor",
    "sqlite3.connect",
    "create_engine",
    "psycopg",
    "mysql.connector",
    "openai.",
    "anthropic.",
    "deepseek.",
    "qwen.",
    "glm.",
    "kimi.",
    "requests.",
    "httpx.",
    "subprocess",
    "os.environ",
    "dotenv",
    "e2b",
    "kerniq runtime",
]

DISALLOWED_VALUE_MARKERS = [
    "http://",
    "https://",
    "file://",
    "/users/",
    "/home/",
    "c:\\",
    ".env",
    "api_key",
    "password",
    "secret",
    "token",
    "bearer",
    "customer",
    "account",
    "personal data",
    "production data",
]


def add_failed(failed_checks, check_name):
    failed_checks.append(check_name)


def load_manifest(failed_checks):
    if len(sys.argv) != 1:
        add_failed(failed_checks, "cli_arguments_not_allowed")
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except Exception:
        add_failed(failed_checks, "manifest_read_or_parse_failed")
        return {}


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


def tokenize(value):
    chars = []
    for char in value:
        if char.isalnum() or char == "_":
            chars.append(char)
        else:
            chars.append(" ")
    return [part.upper() for part in "".join(chars).split()]


def contains_executable_sql(value):
    tokens = tokenize(value)
    for token in tokens:
        if token in SQL_STATEMENT_FORMS:
            return True
    return False


def contains_disallowed_runtime_pattern(value):
    lowered = value.lower()
    for pattern in DISALLOWED_RUNTIME_PATTERNS:
        if pattern in lowered:
            return True
    return False


def contains_disallowed_secret_path_or_url(value):
    lowered = value.lower()
    for marker in DISALLOWED_VALUE_MARKERS:
        if marker in lowered:
            return True
    return False


def validate_manifest_metadata(manifest, failed_checks):
    if manifest.get("manifest_name") != "DHMS LangChain SQL Agent Emit-Only Adapter Static Boundary Fixtures":
        add_failed(failed_checks, "manifest_name_mismatch")
    if manifest.get("manifest_version") != "v2.5.2":
        add_failed(failed_checks, "manifest_version_mismatch")
    if manifest.get("milestone") != "v2.5.2 LangChain SQL Agent Static Adapter Boundary Fixtures":
        add_failed(failed_checks, "milestone_mismatch")
    if manifest.get("contract_source") != "docs/dhms_langchain_sql_agent_emit_only_adapter_contract_v2_5_1.md":
        add_failed(failed_checks, "contract_source_mismatch")
    if manifest.get("fixture_count") != 17:
        add_failed(failed_checks, "fixture_count_declared_mismatch")
    if manifest.get("decision_counts") != EXPECTED_DECISION_COUNTS:
        add_failed(failed_checks, "decision_counts_mismatch")
    if manifest.get("fixtures_are_static_inert_metadata_only") is not True:
        add_failed(failed_checks, "fixtures_not_static_inert_metadata_only")

    assertions = manifest.get("non_execution_manifest_assertions")
    if not isinstance(assertions, dict):
        add_failed(failed_checks, "non_execution_manifest_assertions_missing")
    elif any(value is not False for value in assertions.values()):
        add_failed(failed_checks, "non_execution_manifest_assertions_not_false")


def validate_fixture_shape(fixture, failed_checks):
    fixture_id = fixture.get("fixture_id", "missing_fixture_id")
    if list(fixture.keys()) != REQUIRED_FIXTURE_FIELDS:
        add_failed(failed_checks, "fixture_fields_not_exact:" + fixture_id)

    assertions = fixture.get("non_execution_assertions")
    if not isinstance(assertions, dict):
        add_failed(failed_checks, "non_execution_assertions_missing:" + fixture_id)
        return
    if list(assertions.keys()) != REQUIRED_ASSERTION_FIELDS:
        add_failed(failed_checks, "non_execution_assertion_fields_not_exact:" + fixture_id)
    if any(value is not False for value in assertions.values()):
        add_failed(failed_checks, "non_execution_assertion_not_false:" + fixture_id)


def validate_accepted_fixture(fixtures, failed_checks):
    accepted = [
        fixture
        for fixture in fixtures
        if fixture.get("expected_dhms_decision") == "ACCEPT_FOR_DHMS_EVALUATION"
    ]
    if len(accepted) != 1:
        add_failed(failed_checks, "accepted_fixture_count_mismatch")
        return

    fixture = accepted[0]
    if fixture.get("fixture_id") != "langchain_emit_only_accept_inert_adapter_metadata":
        add_failed(failed_checks, "accepted_fixture_id_mismatch")
    for field, expected_value in EXPECTED_ACCEPTED_VALUES.items():
        if fixture.get(field) != expected_value:
            add_failed(failed_checks, "accepted_fixture_value_mismatch:" + field)

    assertions = fixture.get("non_execution_assertions", {})
    if any(value is not False for value in assertions.values()):
        add_failed(failed_checks, "accepted_fixture_assertions_not_false")


def validate_fail_closed_fixtures(fixtures, failed_checks):
    fail_closed = [
        fixture
        for fixture in fixtures
        if fixture.get("expected_dhms_decision") == "FAIL_CLOSED"
    ]
    if len(fail_closed) != 16:
        add_failed(failed_checks, "fail_closed_fixture_count_mismatch")

    reasons = [fixture.get("expected_fail_closed_reason") for fixture in fail_closed]
    if Counter(reasons) != Counter(REQUIRED_FAIL_CLOSED_REASONS):
        add_failed(failed_checks, "fail_closed_reasons_not_covered_once")

    allowed_reasons = set(REQUIRED_FAIL_CLOSED_REASONS)
    for fixture in fail_closed:
        fixture_id = fixture.get("fixture_id", "missing_fixture_id")
        if fixture.get("expected_fail_closed_reason") not in allowed_reasons:
            add_failed(failed_checks, "fail_closed_reason_not_allowed:" + fixture_id)
        assertions = fixture.get("non_execution_assertions", {})
        if any(value is not False for value in assertions.values()):
            add_failed(failed_checks, "fail_closed_assertions_not_false:" + fixture_id)


def validate_inert_content(manifest, failed_checks):
    for value in iter_string_values(manifest):
        if contains_executable_sql(value):
            add_failed(failed_checks, "executable_sql_pattern_found")
        if contains_disallowed_runtime_pattern(value):
            add_failed(failed_checks, "runtime_or_integration_pattern_found")
        if contains_disallowed_secret_path_or_url(value):
            add_failed(failed_checks, "secret_path_url_or_user_data_marker_found")


def validate_manifest(manifest):
    failed_checks = []
    validate_manifest_metadata(manifest, failed_checks)

    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list):
        add_failed(failed_checks, "fixtures_not_list")
        fixtures = []

    if len(fixtures) != 17:
        add_failed(failed_checks, "fixture_count_actual_mismatch")

    fixture_ids = [fixture.get("fixture_id") for fixture in fixtures if isinstance(fixture, dict)]
    if len(fixture_ids) != len(set(fixture_ids)):
        add_failed(failed_checks, "fixture_ids_not_unique")

    decisions = Counter(
        fixture.get("expected_dhms_decision")
        for fixture in fixtures
        if isinstance(fixture, dict)
    )
    if decisions != Counter(EXPECTED_DECISION_COUNTS):
        add_failed(failed_checks, "actual_decision_counts_mismatch")

    for fixture in fixtures:
        if not isinstance(fixture, dict):
            add_failed(failed_checks, "fixture_not_object")
            continue
        validate_fixture_shape(fixture, failed_checks)

    validate_accepted_fixture(fixtures, failed_checks)
    validate_fail_closed_fixtures(fixtures, failed_checks)
    validate_inert_content(manifest, failed_checks)
    return failed_checks


def print_pass():
    print(PASS_MARKER)
    print("fixture_count=17")
    print("accepted_for_dhms_evaluation=1")
    print("fail_closed=16")
    print("all_required_fields_present=true")
    print("all_non_execution_assertions_present=true")
    print("all_non_execution_assertions_false=true")
    print("all_adapter_fixtures_inert=true")
    print("all_fail_closed_reasons_covered_once=true")
    print("sql_execution_attempts=0")
    print("db_connections=0")
    print("schema_introspection=0")
    print("result_readbacks=0")
    print("langchain_installs=0")
    print("langchain_imports=0")
    print("langchain_invocations=0")
    print("langchain_integrations=0")
    print("sql_database_toolkit_integrations=0")
    print("model_api_calls=0")
    print("credential_accesses=0")
    print("user_data_accesses=0")
    print("kerniq_runtime_calls=0")
    print("e2b_handoffs=0")
    print("runtime_behaviors=0")


def print_fail(failed_checks):
    print(FAIL_MARKER)
    for check_name in sorted(set(failed_checks)):
        print("failed_check=" + check_name)


def main():
    initial_failed_checks = []
    manifest = load_manifest(initial_failed_checks)
    failed_checks = initial_failed_checks + validate_manifest(manifest)
    if failed_checks:
        print_fail(failed_checks)
        return 1
    print_pass()
    return 0


if __name__ == "__main__":
    sys.exit(main())
