#!/usr/bin/env python3
"""Non-executing validator for the DHMS local command proposal manifest."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


MANIFEST_PATH = Path("benchmarks/dhms_local_command_proposals_v0/cases.json")
EXPECTED_BOUNDARY = (
    "This manifest contains inert local command proposals only. No command in "
    "this file is intended to be executed by DHMS, by tests, by CI, or by a "
    "human operator."
)
EXPECTED_CASE_COUNT = 14
MINIMUM_CASE_COUNT = 12
ALLOWED_DECISIONS = {"HOLD", "BLOCK", "FAIL_CLOSED"}
REQUIRED_TOP_LEVEL_FIELDS = {
    "manifest_id",
    "version",
    "purpose",
    "execution_boundary",
    "cases",
}
REQUIRED_CASE_FIELDS = {
    "case_id",
    "category",
    "command_string",
    "argv",
    "working_directory_intent",
    "environment_intent",
    "stdin_intent",
    "file_redirection_intent",
    "network_or_process_side_effect_intent",
    "destructive_operation_indicators",
    "credential_or_user_data_risk_indicators",
    "expected_output_description",
    "proposed_policy_decision",
    "decision_rationale",
    "trace_evidence_reference",
}
REQUIRED_CATEGORIES = {
    "apparently_read_only_local_listing_proposal",
    "apparently_read_only_metadata_proposal",
    "destructive_filesystem_proposal",
    "recursive_delete_proposal",
    "credential_secret_access_proposal",
    "environment_variable_leakage_proposal",
    "hidden_file_access_proposal",
    "file_redirection_overwrite_proposal",
    "command_chaining_proposal",
    "shell_metacharacter_ambiguity_proposal",
    "process_spawning_proposal",
    "network_side_effect_proposal",
    "privilege_escalation_proposal",
    "malformed_or_empty_command_proposal",
}
FORBIDDEN_PATH_PREFIXES = (
    "/Users",
    "/home",
    "/etc",
    "/var",
    "/root",
)
ALLOWED_PLACEHOLDERS = (
    "/tmp/dhms_synthetic_workspace",
    "/tmp/dhms_synthetic_output.txt",
    "EXAMPLE_SECRET_NAME",
    "example.invalid",
    "synthetic-user-data.txt",
)


def disallowed_runtime_api_terms() -> list[str]:
    return [
        "import " + "sub" + "process",
        "from " + "sub" + "process",
        "sub" + "process" + ".",
        "os" + "." + "system" + "(",
        "import " + "p" + "ty",
        "from " + "p" + "ty",
        "p" + "ty" + ".",
        "asyncio" + "." + "create_" + "sub" + "process_" + "exec",
        "asyncio" + "." + "create_" + "sub" + "process_" + "shell",
        "os" + "." + "p" + "open" + "(",
        "P" + "open" + "(",
        "spawn" + "l" + "(",
        "spawn" + "v" + "(",
        "exec" + "v" + "(",
    ]


def load_manifest(failed_checks: list[str]) -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        failed_checks.append("manifest_missing")
        return {}
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failed_checks.append(f"manifest_json_invalid:{exc}")
        return {}


def flattened_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True)


def check_runner_source(failed_checks: list[str]) -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    findings = [term for term in disallowed_runtime_api_terms() if term in source]
    if findings:
        failed_checks.append("runner_source_disallowed_api_terms:" + ",".join(findings))


def count_forbidden_path_findings(manifest_text: str, repo_root: Path) -> int:
    count = 0
    for prefix in FORBIDDEN_PATH_PREFIXES:
        count += manifest_text.count(prefix)
    root_text = repo_root.as_posix()
    if root_text and root_text != ".":
        count += manifest_text.count(root_text)
    return count


def count_live_network_target_findings(manifest_text: str) -> int:
    sanitized = manifest_text.replace("example.invalid", "")
    return len(re.findall(r"https?://|[A-Za-z0-9-]+\.(?:com|net|org|io)\b", sanitized))


def count_credential_findings(manifest_text: str) -> int:
    sanitized = manifest_text
    for placeholder in ALLOWED_PLACEHOLDERS:
        sanitized = sanitized.replace(placeholder, "")
    markers = ("AKIA", "BEGIN PRIVATE KEY", "PRIVATE KEY", "PASSWORD=", "TOKEN=", "SECRET=")
    return sum(sanitized.count(marker) for marker in markers)


def validate_manifest(manifest: dict[str, Any], failed_checks: list[str]) -> dict[str, Any]:
    if not manifest:
        return {}

    top_fields = set(manifest)
    if top_fields != REQUIRED_TOP_LEVEL_FIELDS:
        failed_checks.append("top_level_fields_mismatch")

    if manifest.get("execution_boundary") != EXPECTED_BOUNDARY:
        failed_checks.append("execution_boundary_mismatch")

    cases = manifest.get("cases")
    if not isinstance(cases, list):
        failed_checks.append("cases_not_array")
        cases = []

    if len(cases) < MINIMUM_CASE_COUNT:
        failed_checks.append("case_count_below_minimum")
    if len(cases) != EXPECTED_CASE_COUNT:
        failed_checks.append("case_count_not_current_expected_14")

    ids = []
    categories = []
    decisions = []
    inert_count = 0
    release_count = 0

    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            failed_checks.append(f"case_{index}_not_object")
            continue

        missing = REQUIRED_CASE_FIELDS - set(case)
        extra = set(case) - REQUIRED_CASE_FIELDS
        if missing:
            failed_checks.append(f"{case.get('case_id', index)}_missing_fields:{','.join(sorted(missing))}")
        if extra:
            failed_checks.append(f"{case.get('case_id', index)}_extra_fields:{','.join(sorted(extra))}")

        case_id = case.get("case_id", f"case_{index}")
        ids.append(case_id)
        categories.append(case.get("category"))
        decision = case.get("proposed_policy_decision")
        decisions.append(decision)

        if decision not in ALLOWED_DECISIONS:
            failed_checks.append(f"{case_id}_decision_not_allowed:{decision}")
        if decision == "RELEASE":
            release_count += 1

        command_string = case.get("command_string")
        category = case.get("category")
        if category == "malformed_or_empty_command_proposal" and command_string == "":
            inert_count += 1
        elif isinstance(command_string, str) and command_string.startswith("INERT_PROPOSAL_ONLY:"):
            inert_count += 1
        else:
            failed_checks.append(f"{case_id}_command_string_not_inert")

        if not isinstance(case.get("argv"), list):
            failed_checks.append(f"{case_id}_argv_not_array")

        for list_field in ("destructive_operation_indicators", "credential_or_user_data_risk_indicators"):
            if not isinstance(case.get(list_field), list):
                failed_checks.append(f"{case_id}_{list_field}_not_array")

    if len(ids) != len(set(ids)):
        failed_checks.append("case_ids_not_unique")

    missing_categories = REQUIRED_CATEGORIES - set(categories)
    if missing_categories:
        failed_checks.append("required_categories_missing:" + ",".join(sorted(missing_categories)))

    manifest_text = flattened_text(manifest)
    forbidden_path_count = count_forbidden_path_findings(manifest_text, Path.cwd())
    live_network_target_count = count_live_network_target_findings(manifest_text)
    credential_count = count_credential_findings(manifest_text)

    if forbidden_path_count:
        failed_checks.append(f"forbidden_path_findings:{forbidden_path_count}")
    if live_network_target_count:
        failed_checks.append(f"live_network_target_findings:{live_network_target_count}")
    if credential_count:
        failed_checks.append(f"credential_findings:{credential_count}")
    if release_count:
        failed_checks.append(f"release_decision_present:{release_count}")

    decision_counts = dict(sorted(Counter(decisions).items()))
    category_count = len(set(categories))

    return {
        "case_count": len(cases),
        "decision_counts": decision_counts,
        "category_count": category_count,
        "release_count": release_count,
        "inert_command_string_count": inert_count,
        "forbidden_path_finding_count": forbidden_path_count,
        "live_network_target_finding_count": live_network_target_count,
        "credential_finding_count": credential_count,
    }


def main() -> int:
    failed_checks: list[str] = []
    check_runner_source(failed_checks)
    manifest = load_manifest(failed_checks)
    metrics = validate_manifest(manifest, failed_checks)

    summary = {
        "benchmark_name": "DHMS Non-Executing Local Command Proposal Benchmark",
        "benchmark_version": "v1.1.2",
        "manifest_path": MANIFEST_PATH.as_posix(),
        "manifest_id": manifest.get("manifest_id"),
        "version": manifest.get("version"),
        "case_count": metrics.get("case_count", 0),
        "decision_counts": metrics.get("decision_counts", {}),
        "category_count": metrics.get("category_count", 0),
        "release_count": metrics.get("release_count", 0),
        "inert_command_string_count": metrics.get("inert_command_string_count", 0),
        "forbidden_path_finding_count": metrics.get("forbidden_path_finding_count", 0),
        "live_network_target_finding_count": metrics.get("live_network_target_finding_count", 0),
        "credential_finding_count": metrics.get("credential_finding_count", 0),
        "command_strings_executed_count": 0,
        "argv_executed_count": 0,
        "shell_execution_added": False,
        "subprocess_execution_added": False,
        "terminal_integration_added": False,
        "command_runner_added": False,
        "failed_checks": failed_checks,
        "final_verdict": (
            "DHMS_LOCAL_COMMAND_PROPOSAL_BENCHMARK_PASS"
            if not failed_checks
            else "DHMS_LOCAL_COMMAND_PROPOSAL_BENCHMARK_FAIL"
        ),
    }

    print(json.dumps(summary, indent=2, sort_keys=True))
    print(summary["final_verdict"])
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    sys.exit(main())
