import json
import re
import sys
from collections import Counter
from pathlib import Path


MANIFEST_PATH = Path(
    "benchmarks/dhms_langchain_sql_agent_adapter_skeleton_shape_v0/shape_fixtures.json"
)

PASS_MARKER = "DHMS_LANGCHAIN_SQL_AGENT_ADAPTER_SKELETON_SHAPE_FIXTURE_VALIDATION_PASS"
FAIL_MARKER = "DHMS_LANGCHAIN_SQL_AGENT_ADAPTER_SKELETON_SHAPE_FIXTURE_VALIDATION_FAIL"

TOP_LEVEL_FIELDS = [
    "manifest_name",
    "manifest_version",
    "milestone",
    "contract_source",
    "fixture_count",
    "decision_counts",
    "fixtures_are_static_inert_shape_metadata_only",
    "non_execution_manifest_assertions",
    "fixtures",
]

FIXTURE_FIELDS = [
    "fixture_id",
    "contract_subject",
    "fixture_kind",
    "shape_subject",
    "shape_surface",
    "observation_boundary",
    "emit_boundary",
    "executable_surface_status",
    "langchain_surface_status",
    "sql_database_toolkit_surface_status",
    "sql_text_status",
    "db_scope_status",
    "schema_scope_status",
    "result_scope_status",
    "model_provider_scope_status",
    "credential_scope_status",
    "user_data_scope_status",
    "runtime_scope_status",
    "framework_loop_status",
    "retry_loop_status",
    "expected_dhms_decision",
    "expected_fail_closed_reason",
    "non_execution_assertions",
]

ASSERTION_KEYS = [
    "source_files_added",
    "adapter_implemented",
    "skeleton_implemented",
    "validator_added",
    "schema_added",
    "cli_added",
    "parser_added",
    "runner_added",
    "hook_added",
    "langchain_installed",
    "langchain_imported",
    "langchain_invoked",
    "langchain_integrated",
    "langchain_wrapped",
    "langchain_callback_defined",
    "langchain_tool_defined",
    "sql_database_toolkit_integrated",
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
    "execution_authorized",
]

FAIL_CLOSED_REASONS = [
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

EXPECTED_TOP_LEVEL_VALUES = {
    "manifest_name": "DHMS LangChain SQL Agent Adapter Skeleton Static Shape Fixtures",
    "manifest_version": "v2.6.2",
    "milestone": "v2.6.2 LangChain SQL Agent Adapter Skeleton Static Shape Fixtures",
    "contract_source": "docs/dhms_langchain_sql_agent_emit_only_adapter_skeleton_contract_v2_6_1.md",
    "fixture_count": 17,
    "fixtures_are_static_inert_shape_metadata_only": True,
}

EXPECTED_DECISION_COUNTS = {
    "ACCEPT_FOR_SHAPE_REVIEW": 1,
    "FAIL_CLOSED": 16,
}

PASS_LINES = [
    PASS_MARKER,
    "fixture_count=17",
    "accepted_for_shape_review=1",
    "fail_closed=16",
    "all_required_fields_present=true",
    "all_non_execution_manifest_assertions_present=true",
    "all_non_execution_manifest_assertions_false=true",
    "all_non_execution_fixture_assertions_present=true",
    "all_non_execution_fixture_assertions_false=true",
    "all_shape_fixtures_inert=true",
    "all_fail_closed_reasons_covered_once=true",
    "source_files_added=0",
    "adapter_implementations=0",
    "skeleton_implementations=0",
    "validators_added_in_fixture_manifest=0",
    "schemas_added=0",
    "cli_surfaces=0",
    "parsers_added=0",
    "runners_added=0",
    "hooks_added=0",
    "langchain_installs=0",
    "langchain_imports=0",
    "langchain_invocations=0",
    "langchain_integrations=0",
    "langchain_wrappers=0",
    "langchain_callbacks=0",
    "langchain_tools=0",
    "sql_database_toolkit_integrations=0",
    "sql_execution_attempts=0",
    "db_connections=0",
    "schema_introspection=0",
    "result_readbacks=0",
    "model_api_calls=0",
    "credential_accesses=0",
    "user_data_accesses=0",
    "kerniq_runtime_calls=0",
    "e2b_handoffs=0",
    "runtime_behaviors=0",
    "execution_authorizations=0",
]

PROHIBITED_PATTERNS = [
    ("executable_sql_pattern", r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|MERGE)\b"),
    ("db_connection_string", r"\b(postgres|postgresql|mysql|sqlite|mongodb)://"),
    ("url_pattern", r"https?://"),
    ("file_path_pattern", r"(^|[\s\"'])(/Users/|/home/|/etc/|/var/|/tmp/|/private/|~/|\.env\b)"),
    ("import_statement", r"\b(from|import)\s+[A-Za-z_]"),
    ("python_class_function_module_example", r"\b(class|def|module)\s+[A-Za-z_]"),
    ("shell_command_pattern", r"\b(bash|zsh|sh|curl|wget|python3|pip|poetry|npm)\b"),
    ("model_provider_api_pattern", r"\b(OpenAI|Claude|DeepSeek|Qwen|GLM|Kimi|anthropic|chat.completions)\b"),
    ("langchain_executable_api_pattern", r"\b(LangChain|AgentExecutor|Tool|Callback|invoke|run|chain)\s*\("),
    ("sql_database_toolkit_api_pattern", r"\bSQLDatabaseToolkit\s*\("),
    ("secret_or_token_pattern", r"(sk-[A-Za-z0-9]|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY|token=|password=|secret=)"),
]


def add_check(failed_checks, condition, name):
    if not condition:
        failed_checks.append(name)


def assertion_block_valid(block):
    return isinstance(block, dict) and list(block.keys()) == ASSERTION_KEYS and all(
        value is False for value in block.values()
    )


def inert_text_from_manifest(data):
    safe_top_level = {
        key: value
        for key, value in data.items()
        if key not in {"contract_source", "non_execution_manifest_assertions", "fixtures"}
    }
    return json.dumps(
        {"top_level": safe_top_level, "fixtures": data.get("fixtures")},
        sort_keys=True,
    )


def validate_manifest(data):
    failed_checks = []

    add_check(failed_checks, isinstance(data, dict), "top_level_not_object")
    if not isinstance(data, dict):
        return failed_checks

    add_check(failed_checks, list(data.keys()) == TOP_LEVEL_FIELDS, "top_level_fields_or_order_invalid")

    for key, expected in EXPECTED_TOP_LEVEL_VALUES.items():
        add_check(failed_checks, data.get(key) == expected, f"top_level_value_invalid:{key}")

    add_check(
        failed_checks,
        data.get("decision_counts") == EXPECTED_DECISION_COUNTS,
        "decision_counts_invalid",
    )

    manifest_assertions = data.get("non_execution_manifest_assertions")
    add_check(
        failed_checks,
        assertion_block_valid(manifest_assertions),
        "non_execution_manifest_assertions_invalid",
    )

    fixtures = data.get("fixtures")
    add_check(failed_checks, isinstance(fixtures, list), "fixtures_not_list")
    if not isinstance(fixtures, list):
        return failed_checks

    add_check(failed_checks, len(fixtures) == 17, "fixture_count_invalid")

    decision_counts = Counter()
    fail_closed_reasons = Counter()
    accepted_fixtures = []

    for index, fixture in enumerate(fixtures):
        prefix = f"fixture_{index}"
        add_check(failed_checks, isinstance(fixture, dict), f"{prefix}_not_object")
        if not isinstance(fixture, dict):
            continue

        add_check(
            failed_checks,
            list(fixture.keys()) == FIXTURE_FIELDS,
            f"{prefix}_fields_or_order_invalid",
        )
        add_check(
            failed_checks,
            fixture.get("contract_subject")
            == "LangChain SQL Agent Emit-Only Adapter Skeleton Candidate",
            f"{prefix}_contract_subject_invalid",
        )
        add_check(
            failed_checks,
            fixture.get("fixture_kind") == "static_shape_fixture",
            f"{prefix}_fixture_kind_invalid",
        )
        add_check(
            failed_checks,
            assertion_block_valid(fixture.get("non_execution_assertions")),
            f"{prefix}_non_execution_assertions_invalid",
        )

        decision = fixture.get("expected_dhms_decision")
        decision_counts[decision] += 1
        if decision == "ACCEPT_FOR_SHAPE_REVIEW":
            accepted_fixtures.append(fixture)
        elif decision == "FAIL_CLOSED":
            reason = fixture.get("expected_fail_closed_reason")
            fail_closed_reasons[reason] += 1
            add_check(
                failed_checks,
                reason in FAIL_CLOSED_REASONS,
                f"{prefix}_fail_closed_reason_unknown",
            )
        else:
            failed_checks.append(f"{prefix}_decision_invalid")

    add_check(
        failed_checks,
        decision_counts == Counter(EXPECTED_DECISION_COUNTS),
        "actual_decision_counts_invalid",
    )

    add_check(failed_checks, len(accepted_fixtures) == 1, "accepted_fixture_count_invalid")
    if len(accepted_fixtures) == 1:
        accepted = accepted_fixtures[0]
        accepted_expectations = {
            "fixture_id": "skeleton_shape_accept_inert_documentation_boundary",
            "expected_fail_closed_reason": None,
            "executable_surface_status": "none",
            "sql_text_status": "none",
            "db_scope_status": "none",
            "schema_scope_status": "none",
            "result_scope_status": "none",
            "credential_scope_status": "none",
            "user_data_scope_status": "none",
            "runtime_scope_status": "none",
        }
        for key, expected in accepted_expectations.items():
            add_check(
                failed_checks,
                accepted.get(key) == expected,
                f"accepted_fixture_value_invalid:{key}",
            )

    expected_reason_counts = Counter({reason: 1 for reason in FAIL_CLOSED_REASONS})
    add_check(
        failed_checks,
        fail_closed_reasons == expected_reason_counts,
        "fail_closed_reason_coverage_invalid",
    )

    inert_text = inert_text_from_manifest(data)
    for name, pattern in PROHIBITED_PATTERNS:
        add_check(
            failed_checks,
            re.search(pattern, inert_text, re.IGNORECASE) is None,
            f"non_inert_content_detected:{name}",
        )

    return failed_checks


def load_manifest():
    if len(sys.argv) != 1:
        return None, ["cli_args_not_allowed"]
    if not MANIFEST_PATH.is_file():
        return None, ["manifest_file_missing"]
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8")), []
    except json.JSONDecodeError:
        return None, ["manifest_json_invalid"]


def main():
    data, failed_checks = load_manifest()
    if data is not None:
        failed_checks.extend(validate_manifest(data))

    if failed_checks:
        print(FAIL_MARKER)
        for failed_check in sorted(failed_checks):
            print(f"failed_check={failed_check}")
        return 1

    for line in PASS_LINES:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
