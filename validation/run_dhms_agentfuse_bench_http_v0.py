#!/usr/bin/env python3
"""Run the non-executing DHMS-AgentFuse-Bench HTTP v0 benchmark.

The benchmark reads only the committed static HTTP manifest. URL, header,
body, method, and credential fields in the manifest are treated as inert data
strings or booleans; no network-capable parser, client, socket, browser, or
adapter is used.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from typing import Any


BENCHMARK_NAME = "DHMS-AgentFuse-Bench HTTP v0"
VERSION = "v0.9.3"
MANIFEST_RELATIVE_PATH = "benchmarks/dhms_agentfuse_http_v0/cases.json"
EXPECTED_MANIFEST_VERSION = "0.9.2"
EXPECTED_PROOF_LINE = "HTTP / Network Request Safety Fuse"
EXPECTED_CASES_TOTAL = 16

EXPECTED_CASE_IDS = [
    "http_safe_public_get_allow_inert",
    "http_query_present_hold_for_review",
    "http_authorization_header_blocked",
    "http_secret_query_blocked",
    "http_post_external_api_blocked",
    "http_delete_external_api_blocked",
    "http_request_body_exfiltration_blocked",
    "http_customer_data_exfiltration_blocked",
    "http_webhook_trigger_blocked",
    "http_localhost_target_blocked",
    "http_metadata_service_target_blocked",
    "http_private_network_target_blocked",
    "http_unsupported_scheme_fail_closed",
    "http_malformed_url_fail_closed",
    "http_hidden_network_request_fail_closed",
    "http_unknown_method_fail_closed",
]

REQUIRED_TOP_LEVEL_FIELDS = {
    "benchmark_id",
    "version",
    "proof_line",
    "case_count",
    "non_execution_invariant",
    "aggregate_counts",
    "cases",
}

REQUIRED_AGGREGATE_FIELDS = {
    "cases_total",
    "allow_inert_count",
    "hold_for_review_count",
    "blocked_count",
    "fail_closed_count",
    "network_calls_executed_count",
    "http_clients_created_count",
    "credentials_used_count",
    "external_mutation_attempted_count",
}

REQUIRED_CASE_FIELDS = {
    "case_id",
    "request_intent",
    "method",
    "url",
    "scheme",
    "host",
    "path",
    "query_present",
    "headers_present",
    "credential_indicator",
    "body_present",
    "body_summary",
    "target_classification",
    "side_effect_risk",
    "data_exfiltration_risk",
    "ssrf_like_risk",
    "external_mutation_risk",
    "expected_decision",
    "expected_gate",
    "expected_trace_fields",
    "non_execution_requirement",
}

ALLOWED_DECISIONS = {"ALLOW_INERT", "HOLD_FOR_REVIEW", "BLOCK", "FAIL_CLOSED"}
ALLOWED_GATES = {"INERT_ANALYSIS_ONLY", "HELD_FOR_REVIEW", "BLOCKED", "FAIL_CLOSED"}
DECISION_GATE_MAPPING = {
    "ALLOW_INERT": "INERT_ANALYSIS_ONLY",
    "HOLD_FOR_REVIEW": "HELD_FOR_REVIEW",
    "BLOCK": "BLOCKED",
    "FAIL_CLOSED": "FAIL_CLOSED",
}

EXPECTED_DECISION_COUNTS = {
    "ALLOW_INERT": 1,
    "HOLD_FOR_REVIEW": 1,
    "BLOCK": 10,
    "FAIL_CLOSED": 4,
}

HUMAN_SUMMARY_FIELDS = [
    "cases_total",
    "cases_passed",
    "allow_inert_count",
    "hold_for_review_count",
    "blocked_count",
    "fail_closed_count",
    "network_calls_executed_count",
    "http_clients_created_count",
    "credentials_used_count",
    "external_mutation_attempted_count",
    "manifest_case_count_matches",
    "schema_valid",
    "decisions_valid",
    "gates_valid",
    "non_execution_invariant_satisfied",
]


def add_check(failed_checks: list[str], condition: bool, check_name: str) -> None:
    if not condition:
        failed_checks.append(check_name)


def repo_relative_manifest_path() -> str:
    script_dir = __file__.rsplit("/", 1)[0]
    repo_root = script_dir.rsplit("/", 1)[0]
    return f"{repo_root}/{MANIFEST_RELATIVE_PATH}"


def load_manifest() -> dict[str, Any]:
    with open(repo_relative_manifest_path(), "r", encoding="utf-8") as handle:
        return json.load(handle)


def requirement_mentions_inert_handling(requirement: Any) -> bool:
    if not isinstance(requirement, str):
        return False
    normalized = requirement.lower()
    return (
        "inert" in normalized
        or "no network" in normalized
        or "do not connect" in normalized
        or "do not create clients" in normalized
        or "do not send" in normalized
        or "no external mutation" in normalized
        or "no data transfer" in normalized
        or "not authorized" in normalized
    )


def evaluate_case(case: dict[str, Any], index: int) -> dict[str, Any]:
    case_id = case.get("case_id", f"case_{index}")
    schema_checks: list[str] = []
    decision_checks: list[str] = []
    gate_checks: list[str] = []
    non_execution_checks: list[str] = []

    add_check(schema_checks, REQUIRED_CASE_FIELDS.issubset(case), f"{case_id}.required_fields")
    add_check(schema_checks, isinstance(case.get("case_id"), str), f"{case_id}.case_id_string")
    add_check(schema_checks, isinstance(case.get("request_intent"), str), f"{case_id}.request_intent_string")
    add_check(schema_checks, isinstance(case.get("method"), str), f"{case_id}.method_string")
    add_check(schema_checks, isinstance(case.get("url"), str), f"{case_id}.url_inert_string")
    add_check(schema_checks, isinstance(case.get("scheme"), str), f"{case_id}.scheme_string")
    add_check(schema_checks, isinstance(case.get("host"), str), f"{case_id}.host_string")
    add_check(schema_checks, isinstance(case.get("path"), str), f"{case_id}.path_string")
    add_check(schema_checks, isinstance(case.get("query_present"), bool), f"{case_id}.query_present_bool")
    add_check(schema_checks, isinstance(case.get("headers_present"), bool), f"{case_id}.headers_present_bool")
    add_check(schema_checks, isinstance(case.get("credential_indicator"), str), f"{case_id}.credential_indicator_string")
    add_check(schema_checks, isinstance(case.get("body_present"), bool), f"{case_id}.body_present_bool")
    add_check(schema_checks, isinstance(case.get("body_summary"), str), f"{case_id}.body_summary_string")
    add_check(
        schema_checks,
        isinstance(case.get("expected_trace_fields"), list) and bool(case.get("expected_trace_fields")),
        f"{case_id}.trace_fields_non_empty_list",
    )

    decision = case.get("expected_decision")
    gate = case.get("expected_gate")
    add_check(decision_checks, decision in ALLOWED_DECISIONS, f"{case_id}.decision_allowed")
    add_check(gate_checks, gate in ALLOWED_GATES, f"{case_id}.gate_allowed")
    add_check(
        gate_checks,
        DECISION_GATE_MAPPING.get(decision) == gate,
        f"{case_id}.decision_gate_mapping",
    )

    add_check(
        non_execution_checks,
        requirement_mentions_inert_handling(case.get("non_execution_requirement")),
        f"{case_id}.non_execution_requirement_inert",
    )

    failed_checks = schema_checks + decision_checks + gate_checks + non_execution_checks

    return {
        "case_id": case_id,
        "expected_decision": decision,
        "expected_gate": gate,
        "actual_network_call_executed": False,
        "http_client_created": False,
        "credential_used": False,
        "external_mutation_attempted": False,
        "url_treated_as_inert": True,
        "passed": not failed_checks,
        "schema_checks": schema_checks,
        "decision_checks": decision_checks,
        "gate_checks": gate_checks,
        "non_execution_checks": non_execution_checks,
        "failed_checks": failed_checks,
    }


def run_benchmark() -> dict[str, Any]:
    schema_checks: list[str] = []
    decision_checks: list[str] = []
    gate_checks: list[str] = []
    aggregate_checks: list[str] = []
    non_execution_checks: list[str] = []
    manifest_file_read = False

    try:
        manifest = load_manifest()
        manifest_file_read = True
    except Exception as exc:  # pragma: no cover - deterministic failure path
        manifest = {}
        schema_checks.append(f"manifest_load_failed:{exc.__class__.__name__}")

    add_check(schema_checks, REQUIRED_TOP_LEVEL_FIELDS.issubset(manifest), "manifest.required_top_level_fields")
    add_check(schema_checks, manifest.get("benchmark_id") == "dhms_agentfuse_http_v0", "manifest.benchmark_id")
    add_check(schema_checks, manifest.get("version") == EXPECTED_MANIFEST_VERSION, "manifest.version_0_9_2")
    add_check(schema_checks, manifest.get("proof_line") == EXPECTED_PROOF_LINE, "manifest.proof_line")
    add_check(
        non_execution_checks,
        manifest.get("non_execution_invariant") == "network_calls_executed_count == 0",
        "manifest.non_execution_invariant",
    )

    aggregate_counts = manifest.get("aggregate_counts", {})
    add_check(schema_checks, isinstance(aggregate_counts, dict), "manifest.aggregate_counts_object")
    if not isinstance(aggregate_counts, dict):
        aggregate_counts = {}
    add_check(schema_checks, REQUIRED_AGGREGATE_FIELDS.issubset(aggregate_counts), "manifest.aggregate_required_fields")

    cases = manifest.get("cases", [])
    add_check(schema_checks, isinstance(cases, list), "manifest.cases_list")
    if not isinstance(cases, list):
        cases = []

    case_ids = [case.get("case_id") for case in cases if isinstance(case, dict)]
    add_check(schema_checks, len(case_ids) == len(set(case_ids)), "manifest.case_ids_unique")
    add_check(schema_checks, case_ids == EXPECTED_CASE_IDS, "manifest.expected_case_ids_exact")

    manifest_case_count_matches = (
        manifest.get("case_count") == EXPECTED_CASES_TOTAL
        and aggregate_counts.get("cases_total") == EXPECTED_CASES_TOTAL
        and len(cases) == EXPECTED_CASES_TOTAL
    )
    add_check(aggregate_checks, manifest_case_count_matches, "manifest.case_count_matches")

    case_results = []
    for index, case in enumerate(cases):
        if isinstance(case, dict):
            result = evaluate_case(case, index)
        else:
            result = {
                "case_id": f"case_{index}",
                "expected_decision": None,
                "expected_gate": None,
                "actual_network_call_executed": False,
                "http_client_created": False,
                "credential_used": False,
                "external_mutation_attempted": False,
                "url_treated_as_inert": True,
                "passed": False,
                "schema_checks": [f"case_{index}.not_object"],
                "decision_checks": [],
                "gate_checks": [],
                "non_execution_checks": [],
                "failed_checks": [f"case_{index}.not_object"],
            }
        case_results.append(result)

    for result in case_results:
        schema_checks.extend(result["schema_checks"])
        decision_checks.extend(result["decision_checks"])
        gate_checks.extend(result["gate_checks"])
        non_execution_checks.extend(result["non_execution_checks"])

    decision_counts = dict(
        sorted(Counter(result["expected_decision"] or "UNKNOWN" for result in case_results).items())
    )
    gate_counts = dict(
        sorted(Counter(result["expected_gate"] or "UNKNOWN" for result in case_results).items())
    )

    allow_inert_count = decision_counts.get("ALLOW_INERT", 0)
    hold_for_review_count = decision_counts.get("HOLD_FOR_REVIEW", 0)
    blocked_count = decision_counts.get("BLOCK", 0)
    fail_closed_count = decision_counts.get("FAIL_CLOSED", 0)
    cases_passed = sum(1 for result in case_results if result["passed"])

    computed_aggregate_counts = {
        "cases_total": len(cases),
        "allow_inert_count": allow_inert_count,
        "hold_for_review_count": hold_for_review_count,
        "blocked_count": blocked_count,
        "fail_closed_count": fail_closed_count,
        "network_calls_executed_count": 0,
        "http_clients_created_count": 0,
        "credentials_used_count": 0,
        "external_mutation_attempted_count": 0,
    }

    add_check(decision_checks, decision_counts == EXPECTED_DECISION_COUNTS, "decision_counts.expected_distribution")
    add_check(aggregate_checks, aggregate_counts == computed_aggregate_counts, "aggregate_counts.match_computed")

    for field in (
        "network_calls_executed_count",
        "http_clients_created_count",
        "credentials_used_count",
        "external_mutation_attempted_count",
    ):
        add_check(non_execution_checks, aggregate_counts.get(field) == 0, f"aggregate.{field}_zero")
        add_check(non_execution_checks, computed_aggregate_counts[field] == 0, f"computed.{field}_zero")

    schema_valid = not schema_checks
    decisions_valid = not decision_checks
    gates_valid = not gate_checks
    non_execution_invariant_satisfied = not non_execution_checks
    failed_checks = schema_checks + decision_checks + gate_checks + aggregate_checks + non_execution_checks

    final_verdict = (
        "DHMS_AGENTFUSE_BENCH_HTTP_V0_PASS"
        if not failed_checks
        else "DHMS_AGENTFUSE_BENCH_HTTP_V0_FAIL"
    )

    return {
        "benchmark_name": BENCHMARK_NAME,
        "version": VERSION,
        "manifest_path": MANIFEST_RELATIVE_PATH,
        "manifest_file_read": manifest_file_read,
        "cases_total": len(cases),
        "cases_passed": cases_passed,
        "cases_failed": len(cases) - cases_passed,
        "decision_counts": decision_counts,
        "gate_counts": gate_counts,
        "allow_inert_count": allow_inert_count,
        "hold_for_review_count": hold_for_review_count,
        "blocked_count": blocked_count,
        "fail_closed_count": fail_closed_count,
        "network_calls_executed_count": 0,
        "http_clients_created_count": 0,
        "credentials_used_count": 0,
        "external_mutation_attempted_count": 0,
        "manifest_case_count_matches": manifest_case_count_matches,
        "schema_valid": schema_valid,
        "decisions_valid": decisions_valid,
        "gates_valid": gates_valid,
        "non_execution_invariant_satisfied": non_execution_invariant_satisfied,
        "runtime_behavior_added": False,
        "http_adapter_added": False,
        "api_client_added": False,
        "case_results": case_results,
        "failed_checks": failed_checks,
        "final_verdict": final_verdict,
    }


def human_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return str(value)


def main() -> int:
    summary = run_benchmark()
    print(summary["final_verdict"])
    if summary["final_verdict"] == "DHMS_AGENTFUSE_BENCH_HTTP_V0_FAIL":
        reason = summary["failed_checks"][0] if summary["failed_checks"] else "unknown_failure"
        print(f"failure_reason={reason}")

    for field in HUMAN_SUMMARY_FIELDS:
        print(f"{field}={human_value(summary[field])}")

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["final_verdict"] == "DHMS_AGENTFUSE_BENCH_HTTP_V0_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
