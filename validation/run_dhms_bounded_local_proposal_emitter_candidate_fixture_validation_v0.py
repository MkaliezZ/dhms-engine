#!/usr/bin/env python3
"""Non-executing validation for DHMS bounded local proposal emitter fixtures."""

import json
import re
import sys
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    REPO_ROOT
    / "benchmarks"
    / "dhms_bounded_local_proposal_emitter_candidate_v0"
    / "proposals.json"
)

PASS_MARKER = "DHMS_BOUNDED_LOCAL_PROPOSAL_EMITTER_CANDIDATE_FIXTURE_VALIDATION_PASS"
FAIL_MARKER = "DHMS_BOUNDED_LOCAL_PROPOSAL_EMITTER_CANDIDATE_FIXTURE_VALIDATION_FAIL"

REQUIRED_FIELDS = {
    "fixture_id",
    "fixture_purpose",
    "proposal_id",
    "emitter_profile",
    "target_boundary",
    "dry_run",
    "requested_capability",
    "declared_side_effects",
    "payload_ref",
    "payload_hash",
    "credential_scope",
    "user_data_scope",
    "runtime_target",
    "created_at",
    "expires_at",
    "evidence_ref",
    "trace_ref",
    "non_execution_assertions",
    "expected_contract_status",
    "expected_fail_closed_reason",
}

EXPECTED_FAIL_CLOSED_REASONS = {
    "dry_run_not_true",
    "payload_hash_empty",
    "credential_scope_non_empty",
    "user_data_scope_non_empty",
    "runtime_target_not_inert",
    "payload_ref_executable_looking",
    "kerniq_or_e2b_target_marker",
}

ASSERTION_FIELDS = {
    "command_execution",
    "shell_execution",
    "subprocess_usage",
    "file_mutation",
    "network_access",
    "sdk_call",
    "model_call",
    "runtime_call",
    "kerniq_call",
    "e2b_handoff",
    "credential_access",
    "user_data_access",
    "production_access",
}

INERT_RUNTIME_TARGETS = {"no-runtime", "none", "inert"}
ALLOWED_STATUSES = {"ACCEPT_FOR_DHMS_EVALUATION", "FAIL_CLOSED"}
KERN_IQ_E2B_FIXTURE = "bounded_local_emitter_candidate_fail_kerniq_or_e2b_marker"

DISALLOWED_SUBSTRINGS = (
    "http://",
    "https://",
    "/Users/",
    "C:\\",
    "file://",
    "python -c",
    "cmd.exe",
    "API_KEY",
    "production data",
)

DISALLOWED_WORDS = {
    "bash",
    "sh",
    "zsh",
    "powershell",
    "npm",
    "pip",
    "curl",
    "wget",
    "ssh",
    "token",
    "secret",
    "customer",
    "account",
    "personal",
}


def load_manifest():
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def iter_string_values(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_string_values(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_string_values(item)


def contains_disallowed_marker(text):
    lowered = text.lower()
    for marker in DISALLOWED_SUBSTRINGS:
        if marker.lower() in lowered:
            return marker
    words = set(re.findall(r"[a-zA-Z0-9_.-]+", lowered))
    for marker in DISALLOWED_WORDS:
        if marker.lower() in words:
            return marker
    return None


def validate_assertions(fixture, failed_checks):
    assertions = fixture.get("non_execution_assertions")
    fixture_id = fixture.get("fixture_id", "<missing-fixture-id>")
    if not isinstance(assertions, dict):
        failed_checks.append(f"{fixture_id}: non_execution_assertions_not_object")
        return
    missing = sorted(ASSERTION_FIELDS - set(assertions))
    if missing:
        failed_checks.append(f"{fixture_id}: missing_assertions={','.join(missing)}")
    for field in sorted(ASSERTION_FIELDS):
        if assertions.get(field) is not False:
            failed_checks.append(f"{fixture_id}: assertion_not_false={field}")


def validate_accepted_fixture(fixture, failed_checks):
    fixture_id = fixture.get("fixture_id", "<missing-fixture-id>")
    if fixture.get("dry_run") is not True:
        failed_checks.append(f"{fixture_id}: accepted_dry_run_not_true")
    if fixture.get("credential_scope") != []:
        failed_checks.append(f"{fixture_id}: accepted_credential_scope_not_empty")
    if fixture.get("user_data_scope") != []:
        failed_checks.append(f"{fixture_id}: accepted_user_data_scope_not_empty")
    if fixture.get("runtime_target") not in INERT_RUNTIME_TARGETS:
        failed_checks.append(f"{fixture_id}: accepted_runtime_target_not_inert")
    for field in ("payload_hash", "evidence_ref", "trace_ref"):
        if not fixture.get(field):
            failed_checks.append(f"{fixture_id}: accepted_{field}_empty")
    validate_assertions(fixture, failed_checks)


def validate_fixture_markers(fixture, failed_checks):
    fixture_id = fixture.get("fixture_id", "<missing-fixture-id>")
    for text in iter_string_values(fixture):
        marker = contains_disallowed_marker(text)
        if marker is not None:
            failed_checks.append(f"{fixture_id}: disallowed_marker={marker}")
        lowered = text.lower()
        if ("kerniq" in lowered or "e2b" in lowered) and fixture_id != KERN_IQ_E2B_FIXTURE:
            failed_checks.append(f"{fixture_id}: kerniq_or_e2b_marker_outside_expected_fixture")


def validate_manifest(data):
    failed_checks = []
    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list):
        return ["manifest: fixtures_not_list"], []

    if data.get("fixture_count") != 8:
        failed_checks.append("manifest: fixture_count_not_8")
    if len(fixtures) != 8:
        failed_checks.append("manifest: fixture_list_length_not_8")
    if data.get("fixtures_are_inert_metadata_only") is not True:
        failed_checks.append("manifest: fixtures_are_inert_metadata_only_not_true")

    status_counts = Counter(fixture.get("expected_contract_status") for fixture in fixtures)
    if status_counts.get("ACCEPT_FOR_DHMS_EVALUATION", 0) != 1:
        failed_checks.append("manifest: accepted_count_not_1")
    if status_counts.get("FAIL_CLOSED", 0) != 7:
        failed_checks.append("manifest: fail_closed_count_not_7")
    unknown_statuses = sorted(set(status_counts) - ALLOWED_STATUSES)
    if unknown_statuses:
        failed_checks.append(f"manifest: unknown_statuses={','.join(str(s) for s in unknown_statuses)}")

    fixture_ids = [fixture.get("fixture_id") for fixture in fixtures]
    if len(set(fixture_ids)) != len(fixture_ids):
        failed_checks.append("manifest: duplicate_fixture_ids")

    fail_closed_reasons = set()
    accepted_fixtures = []
    for fixture in fixtures:
        fixture_id = fixture.get("fixture_id", "<missing-fixture-id>")
        missing = sorted(REQUIRED_FIELDS - set(fixture))
        if missing:
            failed_checks.append(f"{fixture_id}: missing_required_fields={','.join(missing)}")
        validate_assertions(fixture, failed_checks)
        validate_fixture_markers(fixture, failed_checks)

        status = fixture.get("expected_contract_status")
        if status == "ACCEPT_FOR_DHMS_EVALUATION":
            accepted_fixtures.append(fixture)
        elif status == "FAIL_CLOSED":
            reason = fixture.get("expected_fail_closed_reason")
            if reason:
                fail_closed_reasons.add(reason)
            else:
                failed_checks.append(f"{fixture_id}: missing_fail_closed_reason")

    for fixture in accepted_fixtures:
        validate_accepted_fixture(fixture, failed_checks)

    missing_reasons = sorted(EXPECTED_FAIL_CLOSED_REASONS - fail_closed_reasons)
    if missing_reasons:
        failed_checks.append(f"manifest: missing_fail_closed_reasons={','.join(missing_reasons)}")

    return failed_checks, fixtures


def main():
    try:
        data = load_manifest()
        failed_checks, fixtures = validate_manifest(data)
    except Exception as exc:  # pragma: no cover - deterministic failure path.
        print(FAIL_MARKER)
        print(f"failed_check=exception:{type(exc).__name__}:{exc}")
        return 1

    status_counts = Counter(fixture.get("expected_contract_status") for fixture in fixtures)

    if failed_checks:
        print(FAIL_MARKER)
        for failed_check in failed_checks:
            print(f"failed_check={failed_check}")
        return 1

    print(PASS_MARKER)
    print("fixture_count=8")
    print(f"accepted_for_dhms_evaluation={status_counts.get('ACCEPT_FOR_DHMS_EVALUATION', 0)}")
    print(f"fail_closed={status_counts.get('FAIL_CLOSED', 0)}")
    print("all_required_fields_present=true")
    print("all_non_execution_assertions_present=true")
    print("all_fixture_payloads_inert=true")
    print("kerniq_runtime_calls=0")
    print("e2b_handoffs=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
