#!/usr/bin/env python3
"""Non-executing fixture validation for DHMS bounded local mock-to-real v0.

This validator reads only the committed static fixture manifest and treats every
fixture payload as inert metadata. It does not execute, dereference, parse for
runtime use, or hand off any proposal.
"""

from __future__ import annotations

from collections import Counter
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "benchmarks" / "dhms_bounded_local_mock_to_real_v0" / "proposals.json"

EXPECTED_TOP_LEVEL = {
    "fixture_set": "DHMS Bounded Local Mock-to-Real Inert Proposal Fixtures",
    "version": "v2.1.2",
    "contract_reference": "docs/dhms_bounded_local_mock_to_real_preview_proof_contract_v2_1_1.md",
    "fixture_count": 8,
    "fixtures_are_static_inert_data_only": True,
}

EXPECTED_CASE_IDS = [
    "valid_release_candidate_inert_read_only",
    "valid_hold_candidate_needs_review",
    "valid_block_candidate_unsupported_capability",
    "valid_fail_closed_missing_payload_hash",
    "valid_fail_closed_non_empty_credential_scope",
    "valid_fail_closed_non_empty_user_data_scope",
    "valid_fail_closed_runtime_target_not_none",
    "valid_fail_closed_executable_looking_payload_ref",
]

REQUIRED_FIXTURE_FIELDS = {
    "case_id",
    "contract_version",
    "proposal_id",
    "source_profile",
    "target_boundary",
    "dry_run",
    "requested_capability",
    "expected_side_effects",
    "payload_ref",
    "payload_hash",
    "credential_scope",
    "user_data_scope",
    "runtime_target",
    "execution_allowed",
    "created_at",
    "expires_at",
    "evidence_ref",
    "trace_ref",
    "expected_dhms_decision",
    "expected_gate_state",
    "expected_fail_closed_reason",
    "non_execution_assertions",
    "notes",
}

NON_EXECUTION_ASSERTION_KEYS = {
    "command_execution",
    "shell_execution",
    "file_mutation",
    "network_access",
    "sdk_call",
    "model_call",
    "runtime_call",
    "adapter_call",
    "kerniQ_runtime_call",
    "e2b_handoff",
    "credential_access",
    "user_data_access",
    "production_resource_access",
}

EXPECTED_DECISION_COUNTS = {
    "RELEASE": 1,
    "HOLD": 1,
    "BLOCK": 1,
    "FAIL_CLOSED": 5,
}

FAIL_CLOSED_REASONS = {
    "valid_fail_closed_missing_payload_hash": "payload_hash_missing",
    "valid_fail_closed_non_empty_credential_scope": "credential_scope_non_empty",
    "valid_fail_closed_non_empty_user_data_scope": "user_data_scope_non_empty",
    "valid_fail_closed_runtime_target_not_none": "runtime_target_not_none_inert_or_no_runtime",
    "valid_fail_closed_executable_looking_payload_ref": "payload_ref_executable_looking",
}

SAFE_MARKER_ALLOWLIST = {
    "valid_fail_closed_non_empty_credential_scope": {
        "synthetic_non_empty_credential_scope_marker",
    },
    "valid_fail_closed_non_empty_user_data_scope": {
        "synthetic_non_empty_user_data_scope_marker",
    },
    "valid_fail_closed_runtime_target_not_none": {
        "synthetic_runtime_target_not_none",
    },
    "valid_fail_closed_executable_looking_payload_ref": {
        "executable-looking://bounded-local-mock-to-real/synthetic-trigger-label",
    },
}

DANGEROUS_SUBSTRINGS = [
    "http://",
    "https://",
    "file://",
    "&&",
    ";",
    "|",
    "`",
    "$(",
    "api_key",
    "token",
    "secret",
    "password",
    "bearer",
    "production_db",
    "prod_database",
    "customer_data",
    "sdk.invoke",
    "invoke_sdk",
    "call_sdk",
    "model.invoke",
    "invoke_model",
    "call_model",
    "kerniq://",
    "kerniq runtime call",
    "call_kerniq",
    "e2b://",
    "e2b handoff",
    "call_e2b",
]


def add(errors: list[str], message: str) -> None:
    errors.append(message)


def is_sha256_ref(value: object) -> bool:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        return False
    digest = value.removeprefix("sha256:")
    return len(digest) == 64 and all(ch in "0123456789abcdef" for ch in digest)


def iter_string_values(value: object, path: str = "") -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(path, value)]
    if isinstance(value, list):
        found: list[tuple[str, str]] = []
        for index, item in enumerate(value):
            found.extend(iter_string_values(item, f"{path}[{index}]"))
        return found
    if isinstance(value, dict):
        found = []
        for key, item in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            found.extend(iter_string_values(item, child_path))
        return found
    return []


def has_absolute_path_marker(value: str) -> bool:
    if value.startswith("/"):
        return True
    for marker in (" /", "\"/", "'/"):
        if marker in value:
            return True
    if len(value) >= 3 and value[1] == ":" and value[0].isalpha() and value[2] in ("\\", "/"):
        return True
    return False


def validate_dangerous_content(case_id: str, fixture: dict[str, object], errors: list[str]) -> None:
    allowed_values = SAFE_MARKER_ALLOWLIST.get(case_id, set())
    for path, value in iter_string_values(fixture):
        lowered = value.lower()
        if value in allowed_values:
            continue
        for marker in DANGEROUS_SUBSTRINGS:
            if marker == ";" and path == "notes":
                continue
            if marker in lowered:
                add(errors, f"{case_id}: dangerous marker found in inert fixture value: {marker}")
        if has_absolute_path_marker(value):
            add(errors, f"{case_id}: absolute path marker found in inert fixture value")


def validate_fixture(case_id: str, fixture: dict[str, object], errors: list[str]) -> None:
    fields = set(fixture)
    if fields != REQUIRED_FIXTURE_FIELDS:
        missing = sorted(REQUIRED_FIXTURE_FIELDS - fields)
        extra = sorted(fields - REQUIRED_FIXTURE_FIELDS)
        add(errors, f"{case_id}: fixture fields mismatch missing={missing} extra={extra}")

    if fixture.get("contract_version") != "bounded-local-mock-to-real-preview-proof-contract-v0":
        add(errors, f"{case_id}: unexpected contract_version")
    if fixture.get("source_profile") != "local_mock_to_real_proposal_emitter_candidate":
        add(errors, f"{case_id}: unexpected source_profile")
    if fixture.get("target_boundary") != "local_mock_to_real_agent_boundary":
        add(errors, f"{case_id}: unexpected target_boundary")

    if fixture.get("dry_run") is not True:
        add(errors, f"{case_id}: dry_run must be true")
    if fixture.get("execution_allowed") is not False:
        add(errors, f"{case_id}: execution_allowed must be false")

    for key in ("requested_capability", "expected_side_effects", "notes"):
        if not isinstance(fixture.get(key), str) or not fixture.get(key):
            add(errors, f"{case_id}: {key} must be a non-empty declarative string")

    payload_ref = fixture.get("payload_ref")
    if case_id == "valid_fail_closed_executable_looking_payload_ref":
        if payload_ref != "executable-looking://bounded-local-mock-to-real/synthetic-trigger-label":
            add(errors, f"{case_id}: executable-looking payload_ref must use the approved synthetic label")
    elif not isinstance(payload_ref, str) or not payload_ref.startswith("inert://bounded-local-mock-to-real/proposals/"):
        add(errors, f"{case_id}: payload_ref must be an inert proposal string")

    payload_hash = fixture.get("payload_hash")
    if case_id == "valid_fail_closed_missing_payload_hash":
        if payload_hash is not None:
            add(errors, f"{case_id}: payload_hash must be null")
    elif not is_sha256_ref(payload_hash):
        add(errors, f"{case_id}: payload_hash must be a sha256 ref")

    for key, prefix in (
        ("evidence_ref", "inert://bounded-local-mock-to-real/evidence/"),
        ("trace_ref", "inert://bounded-local-mock-to-real/traces/"),
    ):
        if not isinstance(fixture.get(key), str) or not fixture[key].startswith(prefix):
            add(errors, f"{case_id}: {key} must use prefix {prefix}")

    credential_scope = fixture.get("credential_scope")
    user_data_scope = fixture.get("user_data_scope")
    if not isinstance(credential_scope, list):
        add(errors, f"{case_id}: credential_scope must be a list")
        credential_scope = []
    if not isinstance(user_data_scope, list):
        add(errors, f"{case_id}: user_data_scope must be a list")
        user_data_scope = []

    if case_id == "valid_fail_closed_non_empty_credential_scope":
        if credential_scope != ["synthetic_non_empty_credential_scope_marker"]:
            add(errors, f"{case_id}: credential_scope must contain only the synthetic marker")
    elif credential_scope != []:
        add(errors, f"{case_id}: credential_scope must be empty")

    if case_id == "valid_fail_closed_non_empty_user_data_scope":
        if user_data_scope != ["synthetic_non_empty_user_data_scope_marker"]:
            add(errors, f"{case_id}: user_data_scope must contain only the synthetic marker")
    elif user_data_scope != []:
        add(errors, f"{case_id}: user_data_scope must be empty")

    runtime_target = fixture.get("runtime_target")
    if case_id == "valid_fail_closed_runtime_target_not_none":
        if runtime_target != "synthetic_runtime_target_not_none":
            add(errors, f"{case_id}: runtime_target must be the approved synthetic invalid marker")
    elif runtime_target not in {"none", "inert", "no-runtime"}:
        add(errors, f"{case_id}: runtime_target must remain none/inert/no-runtime")

    decision = fixture.get("expected_dhms_decision")
    if case_id in FAIL_CLOSED_REASONS:
        if decision != "FAIL_CLOSED":
            add(errors, f"{case_id}: expected_dhms_decision must be FAIL_CLOSED")
        if fixture.get("expected_fail_closed_reason") != FAIL_CLOSED_REASONS[case_id]:
            add(errors, f"{case_id}: expected_fail_closed_reason mismatch")
        if fixture.get("expected_gate_state") != "NON_EXECUTING_FAIL_CLOSED":
            add(errors, f"{case_id}: expected_gate_state must fail closed")
    else:
        if fixture.get("expected_fail_closed_reason") is not None:
            add(errors, f"{case_id}: expected_fail_closed_reason must be null")

    if decision == "RELEASE":
        if fixture.get("expected_gate_state") != "NON_EXECUTING_ELIGIBLE_FOR_FUTURE_BOUNDED_DECISION_EVALUATION":
            add(errors, f"{case_id}: RELEASE fixture must remain non-executing eligible only")
    elif decision == "HOLD":
        if fixture.get("expected_gate_state") != "NON_EXECUTING_HELD_FOR_REVIEW":
            add(errors, f"{case_id}: HOLD fixture must remain held for review")
    elif decision == "BLOCK":
        if fixture.get("expected_gate_state") != "NON_EXECUTING_CLOSED":
            add(errors, f"{case_id}: BLOCK fixture must remain closed")
    elif decision != "FAIL_CLOSED":
        add(errors, f"{case_id}: unexpected decision {decision!r}")

    assertions = fixture.get("non_execution_assertions")
    if not isinstance(assertions, dict):
        add(errors, f"{case_id}: non_execution_assertions must be an object")
        assertions = {}
    if set(assertions) != NON_EXECUTION_ASSERTION_KEYS:
        missing = sorted(NON_EXECUTION_ASSERTION_KEYS - set(assertions))
        extra = sorted(set(assertions) - NON_EXECUTION_ASSERTION_KEYS)
        add(errors, f"{case_id}: non_execution_assertions keys mismatch missing={missing} extra={extra}")
    for key, value in assertions.items():
        if value is not False:
            add(errors, f"{case_id}: non_execution_assertions.{key} must be false")

    validate_dangerous_content(case_id, fixture, errors)


def main() -> int:
    errors: list[str] = []

    try:
        manifest = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    except Exception as exc:  # deterministic failure text without traceback
        print("DHMS_BOUNDED_LOCAL_MOCK_TO_REAL_FIXTURE_VALIDATION_FAIL")
        print(f"failed_check=manifest_read_or_parse_failed:{exc.__class__.__name__}")
        return 1

    for key, expected in EXPECTED_TOP_LEVEL.items():
        if manifest.get(key) != expected:
            add(errors, f"top_level:{key} expected={expected!r} actual={manifest.get(key)!r}")

    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list):
        add(errors, "top_level:fixtures must be a list")
        fixtures = []
    if len(fixtures) != 8:
        add(errors, f"top_level:fixtures length expected=8 actual={len(fixtures)}")

    case_ids = [fixture.get("case_id") for fixture in fixtures if isinstance(fixture, dict)]
    if case_ids != EXPECTED_CASE_IDS:
        add(errors, f"case_order mismatch expected={EXPECTED_CASE_IDS} actual={case_ids}")
    if len(set(case_ids)) != len(case_ids):
        add(errors, "case_ids must be unique")

    for fixture in fixtures:
        if not isinstance(fixture, dict):
            add(errors, "fixture entry must be an object")
            continue
        case_id = fixture.get("case_id")
        if not isinstance(case_id, str):
            add(errors, "fixture case_id must be a string")
            continue
        validate_fixture(case_id, fixture, errors)

    decision_counts = Counter(
        fixture.get("expected_dhms_decision")
        for fixture in fixtures
        if isinstance(fixture, dict)
    )
    if dict(decision_counts) != EXPECTED_DECISION_COUNTS:
        add(errors, f"decision_counts mismatch expected={EXPECTED_DECISION_COUNTS} actual={dict(decision_counts)}")

    all_dry_run_true = all(isinstance(fixture, dict) and fixture.get("dry_run") is True for fixture in fixtures)
    all_execution_allowed_false = all(
        isinstance(fixture, dict) and fixture.get("execution_allowed") is False for fixture in fixtures
    )
    all_non_execution_assertions_present = all(
        isinstance(fixture, dict)
        and isinstance(fixture.get("non_execution_assertions"), dict)
        and set(fixture["non_execution_assertions"]) == NON_EXECUTION_ASSERTION_KEYS
        and all(value is False for value in fixture["non_execution_assertions"].values())
        for fixture in fixtures
    )
    kerniq_runtime_calls = sum(
        1
        for fixture in fixtures
        if isinstance(fixture, dict)
        and isinstance(fixture.get("non_execution_assertions"), dict)
        and fixture["non_execution_assertions"].get("kerniQ_runtime_call") is not False
    )
    e2b_handoffs = sum(
        1
        for fixture in fixtures
        if isinstance(fixture, dict)
        and isinstance(fixture.get("non_execution_assertions"), dict)
        and fixture["non_execution_assertions"].get("e2b_handoff") is not False
    )

    if errors:
        print("DHMS_BOUNDED_LOCAL_MOCK_TO_REAL_FIXTURE_VALIDATION_FAIL")
        for message in errors:
            print(f"failed_check={message}")
        return 1

    print("DHMS_BOUNDED_LOCAL_MOCK_TO_REAL_FIXTURE_VALIDATION_PASS")
    print(f"fixture_count={len(fixtures)}")
    print(f"decision_RELEASE={decision_counts.get('RELEASE', 0)}")
    print(f"decision_HOLD={decision_counts.get('HOLD', 0)}")
    print(f"decision_BLOCK={decision_counts.get('BLOCK', 0)}")
    print(f"decision_FAIL_CLOSED={decision_counts.get('FAIL_CLOSED', 0)}")
    print(f"all_dry_run_true={str(all_dry_run_true).lower()}")
    print(f"all_execution_allowed_false={str(all_execution_allowed_false).lower()}")
    print(f"all_non_execution_assertions_present={str(all_non_execution_assertions_present).lower()}")
    print(f"kerniq_runtime_calls={kerniq_runtime_calls}")
    print(f"e2b_handoffs={e2b_handoffs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
