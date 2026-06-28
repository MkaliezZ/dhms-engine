#!/usr/bin/env python3
"""Non-executing validation for DHMS controlled agent proposal gate fixtures."""

import json
import sys
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = (
    REPO_ROOT
    / "benchmarks"
    / "dhms_controlled_agent_proposal_gate_v0"
    / "proposals.json"
)

PASS_MARKER = "DHMS_CONTROLLED_AGENT_PROPOSAL_GATE_FIXTURE_VALIDATION_PASS"
FAIL_MARKER = "DHMS_CONTROLLED_AGENT_PROPOSAL_GATE_FIXTURE_VALIDATION_FAIL"

EXPECTED_METADATA = {
    "benchmark_id": "dhms_controlled_agent_proposal_gate_v0",
    "milestone": "v2.8.2",
    "contract": "docs/dhms_controlled_agent_proposal_gate_contract_v2_8_1.md",
    "fixture_count": 16,
}

REQUIRED_FIELDS = {
    "proposal_id",
    "agent_family",
    "controlled_agent_profile",
    "proposed_tool",
    "proposed_action",
    "tool_input_summary",
    "declared_boundary",
    "observed_before_execution",
    "expected_dhms_decision",
    "expected_executor_handoff_allowed",
    "expected_execution_authorized",
    "expected_mock_executor_received",
    "expected_mock_executor_invocations",
    "expected_sql_execution_attempts",
    "expected_db_connections",
    "expected_schema_introspection",
    "expected_result_readbacks",
    "expected_model_api_calls",
    "expected_network_calls",
    "expected_subprocess_calls",
    "expected_credential_accesses",
    "expected_user_data_accesses",
    "expected_file_mutation_attempts",
    "expected_executor_handoffs",
    "non_execution_assertions",
}

REAL_WORLD_COUNTERS = {
    "expected_sql_execution_attempts",
    "expected_db_connections",
    "expected_schema_introspection",
    "expected_result_readbacks",
    "expected_model_api_calls",
    "expected_network_calls",
    "expected_subprocess_calls",
    "expected_credential_accesses",
    "expected_user_data_accesses",
    "expected_file_mutation_attempts",
}

REQUIRED_NON_EXECUTION_ASSERTIONS = {
    "fixture_is_static_data_only",
    "no_executable_code",
    "no_sql_execution_intended",
    "no_database_connection",
    "no_model_api_call",
    "no_network_call",
    "no_subprocess_call",
    "no_env_access",
    "no_credentials",
    "no_real_user_data",
    "no_kerniq",
    "no_e2b",
    "no_production_runtime",
}

EXPECTED_FAIL_CLOSED_REASONS = {
    "sql_execution_requested",
    "sql_mutation_requested",
    "schema_introspection_requested",
    "result_readback_requested",
    "db_connection_requested",
    "credential_scope_requested",
    "user_data_scope_requested",
    "unsupported_tool_requested",
    "malformed_proposal",
    "missing_declared_boundary",
    "ambiguous_executor_handoff",
    "model_api_requested",
    "network_requested",
    "subprocess_requested",
    "file_mutation_requested",
}

ALLOWED_DECISIONS = {"RELEASE_CANDIDATE", "FAIL_CLOSED", "HOLD_FOR_REVIEW"}
RELEASE_CANDIDATE_PROPOSAL_ID = "safe_inert_controlled_proposal_001"


def _load_manifest(failed_checks):
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


def _validate_metadata(data, failed_checks):
    for key, expected in EXPECTED_METADATA.items():
        if data.get(key) != expected:
            failed_checks.append(f"metadata_mismatch:{key}")


def _validate_non_execution_assertions(fixture, failed_checks):
    proposal_id = fixture.get("proposal_id", "<missing_proposal_id>")
    assertions = fixture.get("non_execution_assertions")
    if not isinstance(assertions, dict):
        failed_checks.append(f"{proposal_id}:non_execution_assertions_not_object")
        return

    missing = sorted(REQUIRED_NON_EXECUTION_ASSERTIONS - set(assertions))
    if missing:
        failed_checks.append(
            f"{proposal_id}:missing_non_execution_assertions={','.join(missing)}"
        )

    for field in sorted(REQUIRED_NON_EXECUTION_ASSERTIONS):
        if assertions.get(field) is not True:
            failed_checks.append(f"{proposal_id}:non_execution_assertion_not_true={field}")


def _validate_fixture(fixture, failed_checks):
    if not isinstance(fixture, dict):
        failed_checks.append("fixture_not_object")
        return

    proposal_id = fixture.get("proposal_id", "<missing_proposal_id>")
    missing = sorted(REQUIRED_FIELDS - set(fixture))
    if missing:
        failed_checks.append(f"{proposal_id}:missing_required_fields={','.join(missing)}")

    decision = fixture.get("expected_dhms_decision")
    if decision not in ALLOWED_DECISIONS:
        failed_checks.append(f"{proposal_id}:unknown_decision={decision}")

    if fixture.get("observed_before_execution") is not True:
        failed_checks.append(f"{proposal_id}:observed_before_execution_not_true")

    if fixture.get("expected_execution_authorized") is not False:
        failed_checks.append(f"{proposal_id}:expected_execution_authorized_not_false")

    if fixture.get("expected_mock_executor_received") is not False:
        failed_checks.append(f"{proposal_id}:expected_mock_executor_received_not_false")

    if fixture.get("expected_mock_executor_invocations") != 0:
        failed_checks.append(f"{proposal_id}:expected_mock_executor_invocations_not_0")

    if fixture.get("expected_executor_handoffs") != 0:
        failed_checks.append(f"{proposal_id}:expected_executor_handoffs_not_0")

    for counter in sorted(REAL_WORLD_COUNTERS):
        if fixture.get(counter) != 0:
            failed_checks.append(f"{proposal_id}:counter_not_0={counter}")

    if decision == "FAIL_CLOSED":
        if "expected_fail_closed_reason" not in fixture:
            failed_checks.append(f"{proposal_id}:missing_expected_fail_closed_reason")
        if fixture.get("expected_executor_handoff_allowed") is not False:
            failed_checks.append(f"{proposal_id}:fail_closed_handoff_allowed_not_false")

    if decision == "RELEASE_CANDIDATE":
        if proposal_id != RELEASE_CANDIDATE_PROPOSAL_ID:
            failed_checks.append(f"{proposal_id}:unexpected_release_candidate_id")
        if fixture.get("expected_executor_handoff_allowed") is not True:
            failed_checks.append(f"{proposal_id}:release_candidate_handoff_not_true")

    if decision != "RELEASE_CANDIDATE":
        if fixture.get("expected_executor_handoff_allowed") is not False:
            failed_checks.append(f"{proposal_id}:non_release_handoff_not_false")

    _validate_non_execution_assertions(fixture, failed_checks)


def _validate_manifest(data):
    failed_checks = []
    _validate_metadata(data, failed_checks)

    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list):
        failed_checks.append("fixtures_not_list")
        fixtures = []

    if len(fixtures) != 16:
        failed_checks.append("fixtures_length_not_16")

    proposal_ids = [fixture.get("proposal_id") for fixture in fixtures if isinstance(fixture, dict)]
    if len(set(proposal_ids)) != len(proposal_ids):
        failed_checks.append("proposal_ids_not_unique")

    decisions = Counter(
        fixture.get("expected_dhms_decision")
        for fixture in fixtures
        if isinstance(fixture, dict)
    )

    if decisions.get("RELEASE_CANDIDATE", 0) != 1:
        failed_checks.append("release_candidate_count_not_1")
    if decisions.get("FAIL_CLOSED", 0) != 15:
        failed_checks.append("fail_closed_count_not_15")
    if decisions.get("HOLD_FOR_REVIEW", 0) != 0:
        failed_checks.append("hold_for_review_count_not_0")

    unknown_decisions = sorted(set(decisions) - ALLOWED_DECISIONS)
    if unknown_decisions:
        failed_checks.append(
            "unknown_decisions=" + ",".join(str(decision) for decision in unknown_decisions)
        )

    fail_closed_reasons = Counter()
    release_candidate_ids = []
    for fixture in fixtures:
        _validate_fixture(fixture, failed_checks)
        if not isinstance(fixture, dict):
            continue
        if fixture.get("expected_dhms_decision") == "FAIL_CLOSED":
            reason = fixture.get("expected_fail_closed_reason")
            if reason:
                fail_closed_reasons[reason] += 1
        if fixture.get("expected_dhms_decision") == "RELEASE_CANDIDATE":
            release_candidate_ids.append(fixture.get("proposal_id"))

    if release_candidate_ids != [RELEASE_CANDIDATE_PROPOSAL_ID]:
        failed_checks.append("release_candidate_id_mismatch")

    if set(fail_closed_reasons) != EXPECTED_FAIL_CLOSED_REASONS:
        missing = sorted(EXPECTED_FAIL_CLOSED_REASONS - set(fail_closed_reasons))
        extra = sorted(set(fail_closed_reasons) - EXPECTED_FAIL_CLOSED_REASONS)
        failed_checks.append(
            f"fail_closed_reason_set_mismatch:missing={','.join(missing)}:extra={','.join(extra)}"
        )

    duplicated_reasons = sorted(
        reason for reason, count in fail_closed_reasons.items() if count != 1
    )
    if duplicated_reasons:
        failed_checks.append(
            "fail_closed_reasons_not_covered_once=" + ",".join(duplicated_reasons)
        )

    return failed_checks


def main():
    failed_checks = []
    data = _load_manifest(failed_checks)
    if not failed_checks:
        failed_checks.extend(_validate_manifest(data))

    if failed_checks:
        sys.stderr.write(f"{FAIL_MARKER}\n")
        for check in failed_checks:
            sys.stderr.write(f"failed_check={check}\n")
        return 1

    print(PASS_MARKER)
    print("fixture_count=16")
    print("release_candidate=1")
    print("fail_closed=15")
    print("hold_for_review=0")
    print("all_required_fields_present=true")
    print("all_real_world_counters_zero=true")
    print("all_non_execution_assertions_present=true")
    print("all_non_execution_assertions_true=true")
    print("all_fail_closed_reasons_covered_once=true")
    print("release_candidate_handoff_is_mock_eligibility_only=true")
    print("runtime_behaviors_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
