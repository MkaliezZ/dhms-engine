#!/usr/bin/env python3
"""Read-only validation for DHMS controlled proposal replay evidence records."""

import json
import sys
from pathlib import Path


REPLAY_RECORDS_PATH = Path("benchmarks/dhms_controlled_proposal_replay_evidence_v0/replay_records.json")
SOURCE_FIXTURES_PATH = Path("benchmarks/dhms_controlled_agent_proposal_gate_v0/proposals.json")

EXPECTED_TOP_LEVEL = {
    "benchmark_id": "dhms_controlled_proposal_replay_evidence_v0",
    "milestone": "v2.9.1",
    "contract": "docs/dhms_controlled_proposal_replay_evidence_contract_v2_9_1.md",
    "source_fixture_manifest": "benchmarks/dhms_controlled_agent_proposal_gate_v0/proposals.json",
    "source_validator": "validation/run_dhms_controlled_agent_proposal_gate_fixture_validation_v0.py",
    "source_freeze": "docs/dhms_controlled_agent_proposal_gate_result_review_and_freeze_v2_8_4.md",
    "record_count": 16,
}

EXPECTED_ASSERTIONS = {
    "static_record_only",
    "no_fixture_mutation",
    "no_validator_execution",
    "no_source_runtime_code",
    "no_cli",
    "no_schema",
    "no_sql_execution",
    "no_db_access",
    "no_model_api",
    "no_network",
    "no_subprocess",
    "no_env_access",
    "no_credentials",
    "no_user_data",
    "no_kerniq",
    "no_e2b",
    "no_production_runtime",
}


def fail(message: str) -> None:
    print(f"DHMS_CONTROLLED_PROPOSAL_REPLAY_EVIDENCE_VALIDATION_FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:
        fail(f"could not read JSON from {path}: {exc}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> int:
    replay_manifest = load_json(REPLAY_RECORDS_PATH)
    source_manifest = load_json(SOURCE_FIXTURES_PATH)

    for key, expected_value in EXPECTED_TOP_LEVEL.items():
        require(
            replay_manifest.get(key) == expected_value,
            f"top-level field {key!r} expected {expected_value!r}, got {replay_manifest.get(key)!r}",
        )

    records = replay_manifest.get("records")
    fixtures = source_manifest.get("fixtures")

    require(isinstance(records, list), "records must be a list")
    require(isinstance(fixtures, list), "source fixtures must be a list")
    require(len(records) == 16, f"expected exactly 16 replay records, got {len(records)}")
    require(len(fixtures) == 16, f"expected exactly 16 source fixtures, got {len(fixtures)}")

    replay_record_ids = [record.get("replay_record_id") for record in records]
    source_proposal_ids = [record.get("source_proposal_id") for record in records]
    fixture_ids = [fixture.get("proposal_id") for fixture in fixtures]

    require(len(set(replay_record_ids)) == 16, "replay_record_id values must be unique")
    require(len(set(source_proposal_ids)) == 16, "source_proposal_id values must be unique")
    require(set(source_proposal_ids) == set(fixture_ids), "source_proposal_id set must match v2.8.2 fixture ids")
    require(source_proposal_ids == fixture_ids, "source_proposal_id order must match v2.8.2 fixture order")

    fixtures_by_id = {fixture["proposal_id"]: fixture for fixture in fixtures}
    release_candidate_count = 0
    fail_closed_count = 0
    hold_for_review_count = 0
    all_replay_records_static_only = True
    all_runtime_behaviors_added_zero = True
    all_execution_authorized_false = True
    all_real_world_counters_zero_preserved = True
    all_non_execution_assertions_preserved = True
    all_replay_assertions_present = True
    all_replay_assertions_true = True

    for record in records:
        proposal_id = record.get("source_proposal_id")
        fixture = fixtures_by_id[proposal_id]
        source_decision = record.get("source_decision")

        require(
            source_decision == fixture.get("expected_dhms_decision"),
            f"{proposal_id}: source_decision does not match source fixture",
        )

        if source_decision == "RELEASE_CANDIDATE":
            release_candidate_count += 1
            require(
                proposal_id == "safe_inert_controlled_proposal_001",
                "release candidate must be safe_inert_controlled_proposal_001",
            )
            require("source_fail_closed_reason" not in record, f"{proposal_id}: release candidate must not include fail-closed reason")
        elif source_decision == "FAIL_CLOSED":
            fail_closed_count += 1
            require(
                record.get("source_fail_closed_reason") == fixture.get("expected_fail_closed_reason"),
                f"{proposal_id}: source_fail_closed_reason does not match source fixture",
            )
        elif source_decision == "HOLD_FOR_REVIEW":
            hold_for_review_count += 1
        else:
            fail(f"{proposal_id}: unexpected source_decision {source_decision!r}")

        all_replay_records_static_only = all_replay_records_static_only and (
            record.get("replay_scope") == "repository_local_read_only_replay_evidence"
            and record.get("replay_mode") == "static_evidence_record_only"
            and record.get("frozen_validation_marker") == "DHMS_CONTROLLED_AGENT_PROPOSAL_GATE_FIXTURE_VALIDATION_PASS"
            and record.get("expected_replay_status") == "REPLAY_EVIDENCE_STATIC_ONLY"
        )
        all_execution_authorized_false = all_execution_authorized_false and record.get("expected_execution_authorized") is False
        all_runtime_behaviors_added_zero = all_runtime_behaviors_added_zero and record.get("expected_runtime_behaviors_added") == 0
        all_real_world_counters_zero_preserved = (
            all_real_world_counters_zero_preserved and record.get("expected_real_world_counters_zero") is True
        )
        all_non_execution_assertions_preserved = (
            all_non_execution_assertions_preserved and record.get("expected_non_execution_assertions_preserved") is True
        )

        replay_assertions = record.get("replay_assertions")
        all_replay_assertions_present = (
            all_replay_assertions_present
            and isinstance(replay_assertions, dict)
            and set(replay_assertions) == EXPECTED_ASSERTIONS
        )
        all_replay_assertions_true = (
            all_replay_assertions_true
            and isinstance(replay_assertions, dict)
            and all(value is True for value in replay_assertions.values())
        )

    require(release_candidate_count == 1, f"expected RELEASE_CANDIDATE count 1, got {release_candidate_count}")
    require(fail_closed_count == 15, f"expected FAIL_CLOSED count 15, got {fail_closed_count}")
    require(hold_for_review_count == 0, f"expected HOLD_FOR_REVIEW count 0, got {hold_for_review_count}")
    require(all_replay_records_static_only, "all replay records must be static only")
    require(all_runtime_behaviors_added_zero, "all runtime behavior counters must be 0")
    require(all_execution_authorized_false, "all execution authorization values must be false")
    require(all_real_world_counters_zero_preserved, "all real-world counter invariants must be preserved")
    require(all_non_execution_assertions_preserved, "all non-execution assertions must be preserved")
    require(all_replay_assertions_present, "all replay assertions must be present")
    require(all_replay_assertions_true, "all replay assertions must be true")

    print("DHMS_CONTROLLED_PROPOSAL_REPLAY_EVIDENCE_VALIDATION_PASS")
    print("record_count=16")
    print("source_fixture_alignment=true")
    print("release_candidate=1")
    print("fail_closed=15")
    print("hold_for_review=0")
    print("all_replay_records_static_only=true")
    print("all_runtime_behaviors_added_zero=true")
    print("all_execution_authorized_false=true")
    print("all_real_world_counters_zero_preserved=true")
    print("all_non_execution_assertions_preserved=true")
    print("all_replay_assertions_present=true")
    print("all_replay_assertions_true=true")
    print("runtime_behaviors_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
