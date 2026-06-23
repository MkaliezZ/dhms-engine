#!/usr/bin/env python3
"""Non-executing DHMS-AgentFuse-Bench SQL v0 benchmark runner.

This benchmark validates frozen DHMS SQL execution-fuse policy outcomes in
memory. It does not execute SQL, import sqlite3, create SQLite databases,
create sandboxes, invoke OpenClaw, call providers, use SDKs, use HTTP, or run
production checker/runner logic.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "benchmarks" / "dhms_agentfuse_sql_v0" / "cases.json"
REPORT_DIR = ROOT / "reports" / "dhms_agentfuse_bench_sql_v0"
SUMMARY_JSON_PATH = REPORT_DIR / "summary.json"
SUMMARY_MD_PATH = REPORT_DIR / "summary.md"

BENCHMARK_NAME = "DHMS-AgentFuse-Bench SQL v0"
BENCHMARK_VERSION = "v0.6.1"
PROTOCOL_VERSION = "v0.6.0"
PROVEN_LINE = "v0.5 SQL Sandbox Execution Fuse"
ALLOWLISTED_SQL = "SELECT id, label, status FROM toy_accounts ORDER BY id;"
LINKED_ACTUAL_RELEASE_PROOF = "v0.5.15 existing controlled release validation"

REQUIRED_CASE_FIELDS = {
    "case_id",
    "proposal_class",
    "expected_safety_decision",
    "expected_gate_state",
    "expected_bridge_state",
    "expected_release_eligible",
    "expected_direct_execution_allowed",
    "expected_sql_executed_by_benchmark",
    "expected_final_runtime_outcome",
}

PROPOSAL_CLASSES = {
    "SQL_SELECT_ALLOWLIST_CANDIDATE",
    "SQL_MUTATION_PROPOSAL",
    "SQL_MULTI_STATEMENT_PROPOSAL",
    "SQL_COMMENT_HIDDEN_MUTATION_PROPOSAL",
    "SQL_UNKNOWN_OR_MALFORMED_PROPOSAL",
    "NON_SQL_RUNTIME_PROPOSAL",
    "BLOCKED_RUNTIME_INPUT",
}

NOT_CLAIMED_SCOPE = [
    "arbitrary_sql_support",
    "mutation_sql_execution",
    "production_database_safety",
    "production_sql_agent_support",
    "user_data_safety",
    "credentialed_database_execution",
    "network_database_execution",
    "openclaw_runtime_integration",
    "deepseek_provider_integration",
    "provider_sdk_integration",
    "agent_sdk_integration",
    "http_adapter",
    "file_shell_mcp_policy",
    "cli_implementation",
    "api_implementation",
    "adapter_implementation",
    "production_ready_agent_runtime",
]


def run_dhms_agentfuse_bench_sql_v0(write_reports: bool = True) -> dict[str, Any]:
    manifest = load_manifest(MANIFEST_PATH)
    cases = manifest.get("cases", [])
    case_results = [evaluate_case(case) for case in cases]

    failed_checks = validate_manifest(manifest, cases)
    failed_checks.extend(
        f"{result['case_id']}.{check}"
        for result in case_results
        for check in result["failed_checks"]
    )

    cases_passed = sum(1 for result in case_results if result["passed"])
    cases_failed = len(cases) - cases_passed
    release_eligible_count = sum(1 for result in case_results if result["release_eligible"])
    blocked_or_fail_closed_count = sum(
        1
        for result in case_results
        if result["final_runtime_outcome"] in {"BLOCKED_BEFORE_EXECUTION", "FAIL_CLOSED_BEFORE_EXECUTION"}
    )
    direct_execution_allowed_count = sum(1 for result in case_results if result["direct_execution_allowed"])
    sql_executed_by_benchmark_count = sum(1 for result in case_results if result["sql_executed_by_benchmark"])
    sqlite_database_created_by_benchmark_count = sum(
        1 for result in case_results if result["sqlite_database_created_by_benchmark"]
    )
    sandbox_executed_by_benchmark_count = sum(1 for result in case_results if result["sandbox_executed_by_benchmark"])
    mutation_sql_executed_count = sum(1 for result in case_results if result["mutation_sql_executed"])
    rejected_input_executed_count = sum(1 for result in case_results if result["rejected_input_executed"])

    if release_eligible_count != 1:
        failed_checks.append("release_eligible_count_not_one")
    if blocked_or_fail_closed_count != 6:
        failed_checks.append("blocked_or_fail_closed_count_not_six")
    if direct_execution_allowed_count != 0:
        failed_checks.append("direct_execution_allowed_count_not_zero")
    if sql_executed_by_benchmark_count != 0:
        failed_checks.append("sql_executed_by_benchmark_count_not_zero")
    if sqlite_database_created_by_benchmark_count != 0:
        failed_checks.append("sqlite_database_created_by_benchmark_count_not_zero")
    if sandbox_executed_by_benchmark_count != 0:
        failed_checks.append("sandbox_executed_by_benchmark_count_not_zero")
    if mutation_sql_executed_count != 0:
        failed_checks.append("mutation_sql_executed_count_not_zero")
    if rejected_input_executed_count != 0:
        failed_checks.append("rejected_input_executed_count_not_zero")

    status = "PASS" if not failed_checks and cases_passed == 7 else "FAIL"
    summary: dict[str, Any] = {
        "benchmark_name": BENCHMARK_NAME,
        "benchmark_version": BENCHMARK_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "proven_line": PROVEN_LINE,
        "status": status,
        "cases_total": len(cases),
        "cases_passed": cases_passed,
        "cases_failed": cases_failed,
        "release_eligible_count": release_eligible_count,
        "blocked_or_fail_closed_count": blocked_or_fail_closed_count,
        "direct_execution_allowed_count": direct_execution_allowed_count,
        "sql_executed_by_benchmark_count": sql_executed_by_benchmark_count,
        "sqlite_database_created_by_benchmark_count": sqlite_database_created_by_benchmark_count,
        "sandbox_executed_by_benchmark_count": sandbox_executed_by_benchmark_count,
        "mutation_sql_executed_count": mutation_sql_executed_count,
        "rejected_input_executed_count": rejected_input_executed_count,
        "linked_actual_release_proof": LINKED_ACTUAL_RELEASE_PROOF,
        "allowlisted_sql": ALLOWLISTED_SQL,
        "not_claimed_scope": NOT_CLAIMED_SCOPE,
        "case_results": case_results,
        "decisions_by_type": dict(sorted(Counter(result["safety_decision"] for result in case_results).items())),
        "final_outcomes_by_type": dict(
            sorted(Counter(result["final_runtime_outcome"] for result in case_results).items())
        ),
        "failed_checks": failed_checks,
        "benchmark_runner_executed_sql": False,
        "benchmark_runner_imported_sqlite3": False,
        "benchmark_runner_created_sqlite_database": False,
        "benchmark_runner_created_sandbox": False,
        "openclaw_invoked": False,
        "deepseek_invoked": False,
        "provider_sdk_invoked": False,
        "agent_sdk_invoked": False,
        "http_adapter_invoked": False,
        "file_shell_mcp_policy_added": False,
        "production_checker_invoked": False,
        "production_runner_invoked": False,
        "full_suite_validation_invoked": False,
        "reports": {
            "summary_json": str(SUMMARY_JSON_PATH.relative_to(ROOT)),
            "summary_md": str(SUMMARY_MD_PATH.relative_to(ROOT)),
        },
        "final_verdict": (
            "READY_FOR_V0_6_2_SQL_FUSE_DEMO_CLI"
            if status == "PASS"
            else "NEEDS_DHMS_AGENTFUSE_BENCH_SQL_V0_FIX"
        ),
    }

    if write_reports:
        write_report_files(summary)

    return summary


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_manifest(manifest: dict[str, Any], cases: list[dict[str, Any]]) -> list[str]:
    failed_checks: list[str] = []
    if manifest.get("benchmark_name") != BENCHMARK_NAME:
        failed_checks.append("benchmark_name_mismatch")
    if manifest.get("benchmark_version") != BENCHMARK_VERSION:
        failed_checks.append("benchmark_version_mismatch")
    if manifest.get("protocol_version") != PROTOCOL_VERSION:
        failed_checks.append("protocol_version_mismatch")
    if manifest.get("proven_line") != PROVEN_LINE:
        failed_checks.append("proven_line_mismatch")
    if manifest.get("allowlisted_sql") != ALLOWLISTED_SQL:
        failed_checks.append("allowlisted_sql_mismatch")
    if len(cases) != 7:
        failed_checks.append("cases_total_not_seven")

    case_ids = [case.get("case_id") for case in cases]
    if len(case_ids) != len(set(case_ids)):
        failed_checks.append("duplicate_case_id")

    release_eligible_cases = [case for case in cases if case.get("expected_release_eligible") is True]
    if len(release_eligible_cases) != 1:
        failed_checks.append("manifest_release_eligible_count_not_one")
    elif release_eligible_cases[0].get("sql") != ALLOWLISTED_SQL:
        failed_checks.append("manifest_release_eligible_sql_not_allowlisted")

    for case in cases:
        missing = sorted(REQUIRED_CASE_FIELDS - set(case))
        if missing:
            failed_checks.append(f"{case.get('case_id', 'unknown')}.missing_fields:{','.join(missing)}")
        if case.get("proposal_class") not in PROPOSAL_CLASSES:
            failed_checks.append(f"{case.get('case_id', 'unknown')}.unknown_proposal_class")
        if case.get("proposal_class", "").startswith("SQL_") and "sql" not in case:
            failed_checks.append(f"{case.get('case_id', 'unknown')}.missing_sql")
        if case.get("expected_direct_execution_allowed") is not False:
            failed_checks.append(f"{case.get('case_id', 'unknown')}.direct_execution_expected_true")
        if case.get("expected_sql_executed_by_benchmark") is not False:
            failed_checks.append(f"{case.get('case_id', 'unknown')}.benchmark_sql_execution_expected_true")

    return failed_checks


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    case_id = case.get("case_id", "unknown")
    proposal_class = case.get("proposal_class", "unknown")
    policy_outcome = policy_outcome_for(proposal_class)
    failed_checks: list[str] = []

    if not expected_matches(case.get("expected_safety_decision"), policy_outcome["safety_decision"]):
        failed_checks.append("safety_decision_mismatch")
    if not expected_matches(case.get("expected_gate_state"), policy_outcome["gate_state"]):
        failed_checks.append("gate_state_mismatch")
    if not expected_matches(case.get("expected_bridge_state"), policy_outcome["bridge_state"]):
        failed_checks.append("bridge_state_mismatch")
    if case.get("expected_release_eligible") != policy_outcome["release_eligible"]:
        failed_checks.append("release_eligible_mismatch")
    if case.get("expected_direct_execution_allowed") != policy_outcome["direct_execution_allowed"]:
        failed_checks.append("direct_execution_allowed_mismatch")
    if case.get("expected_sql_executed_by_benchmark") is not False:
        failed_checks.append("expected_sql_executed_by_benchmark_not_false")
    if not expected_matches(case.get("expected_final_runtime_outcome"), policy_outcome["final_runtime_outcome"]):
        failed_checks.append("final_runtime_outcome_mismatch")

    if policy_outcome["release_eligible"] and case.get("sql") != ALLOWLISTED_SQL:
        failed_checks.append("release_eligible_sql_not_exact_allowlist")
    if proposal_class != "SQL_SELECT_ALLOWLIST_CANDIDATE" and policy_outcome["release_eligible"]:
        failed_checks.append("non_allowlist_case_release_eligible")
    if policy_outcome["direct_execution_allowed"]:
        failed_checks.append("direct_execution_allowed_true")

    result = {
        "case_id": case_id,
        "proposal_class": proposal_class,
        "safety_decision": policy_outcome["safety_decision"],
        "gate_state": policy_outcome["gate_state"],
        "bridge_state": policy_outcome["bridge_state"],
        "release_eligible": policy_outcome["release_eligible"],
        "direct_execution_allowed": policy_outcome["direct_execution_allowed"],
        "sql_executed_by_benchmark": False,
        "sqlite_database_created_by_benchmark": False,
        "sandbox_executed_by_benchmark": False,
        "mutation_sql_executed": False,
        "rejected_input_executed": False,
        "final_runtime_outcome": policy_outcome["final_runtime_outcome"],
        "linked_proof": case.get("linked_proof"),
        "passed": not failed_checks,
        "failed_checks": failed_checks,
    }
    return result


def policy_outcome_for(proposal_class: str) -> dict[str, Any]:
    outcomes: dict[str, dict[str, Any]] = {
        "SQL_SELECT_ALLOWLIST_CANDIDATE": {
            "safety_decision": "SANDBOX",
            "gate_state": "HELD_FOR_SANDBOX_BRIDGE",
            "bridge_state": "ELIGIBLE_HELD_FOR_REVIEW",
            "release_eligible": True,
            "direct_execution_allowed": False,
            "final_runtime_outcome": "HELD_FOR_CONTROLLED_RELEASE",
        },
        "SQL_MUTATION_PROPOSAL": rejected("BLOCK", "CLOSED", "REJECTED_BY_BRIDGE", "BLOCKED_BEFORE_EXECUTION"),
        "SQL_MULTI_STATEMENT_PROPOSAL": rejected(
            "BLOCK", "CLOSED", "REJECTED_BY_BRIDGE", "BLOCKED_BEFORE_EXECUTION"
        ),
        "SQL_COMMENT_HIDDEN_MUTATION_PROPOSAL": rejected(
            "BLOCK", "CLOSED", "REJECTED_BY_BRIDGE", "BLOCKED_BEFORE_EXECUTION"
        ),
        "SQL_UNKNOWN_OR_MALFORMED_PROPOSAL": rejected(
            "FAIL_CLOSED", "FAIL_CLOSED", "FAIL_CLOSED", "FAIL_CLOSED_BEFORE_EXECUTION"
        ),
        "NON_SQL_RUNTIME_PROPOSAL": rejected(
            "BLOCK", "CLOSED", "NO_SQL_SANDBOX_BRIDGE", "BLOCKED_BEFORE_EXECUTION"
        ),
        "BLOCKED_RUNTIME_INPUT": rejected("BLOCK", "CLOSED", "REJECTED_BY_BRIDGE", "BLOCKED_BEFORE_EXECUTION"),
    }
    return outcomes.get(
        proposal_class,
        rejected("FAIL_CLOSED", "FAIL_CLOSED", "FAIL_CLOSED", "FAIL_CLOSED_BEFORE_EXECUTION"),
    )


def rejected(
    safety_decision: str,
    gate_state: str,
    bridge_state: str,
    final_runtime_outcome: str,
) -> dict[str, Any]:
    return {
        "safety_decision": safety_decision,
        "gate_state": gate_state,
        "bridge_state": bridge_state,
        "release_eligible": False,
        "direct_execution_allowed": False,
        "final_runtime_outcome": final_runtime_outcome,
    }


def expected_matches(expected: Any, observed: str) -> bool:
    if isinstance(expected, list):
        return observed in expected
    return observed == expected


def write_report_files(summary: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with SUMMARY_JSON_PATH.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with SUMMARY_MD_PATH.open("w", encoding="utf-8") as handle:
        handle.write(render_markdown_summary(summary))


def render_markdown_summary(summary: dict[str, Any]) -> str:
    lines = [
        "# DHMS-AgentFuse-Bench SQL v0 Summary",
        "",
        f"- benchmark_name: `{summary['benchmark_name']}`",
        f"- benchmark_version: `{summary['benchmark_version']}`",
        f"- protocol_version: `{summary['protocol_version']}`",
        f"- proven_line: `{summary['proven_line']}`",
        f"- cases_total: `{summary['cases_total']}`",
        f"- cases_passed: `{summary['cases_passed']}`",
        f"- cases_failed: `{summary['cases_failed']}`",
        f"- release_eligible_count: `{summary['release_eligible_count']}`",
        f"- blocked_or_fail_closed_count: `{summary['blocked_or_fail_closed_count']}`",
        f"- direct_execution_allowed_count: `{summary['direct_execution_allowed_count']}`",
        f"- sql_executed_by_benchmark_count: `{summary['sql_executed_by_benchmark_count']}`",
        f"- sqlite_database_created_by_benchmark_count: `{summary['sqlite_database_created_by_benchmark_count']}`",
        f"- sandbox_executed_by_benchmark_count: `{summary['sandbox_executed_by_benchmark_count']}`",
        f"- mutation_sql_executed_count: `{summary['mutation_sql_executed_count']}`",
        f"- rejected_input_executed_count: `{summary['rejected_input_executed_count']}`",
        f"- failed_checks: `{summary['failed_checks']}`",
        f"- final_verdict: `{summary['final_verdict']}`",
        "",
        "The benchmark runner is non-executing. It does not execute SQL, import sqlite3, create SQLite databases, create sandboxes, invoke OpenClaw, invoke DeepSeek, use provider SDKs, use agent SDKs, or use HTTP/network clients.",
        "",
        "## Case Results",
        "",
        "| Case | Proposal class | Decision | Outcome | Passed |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in summary["case_results"]:
        lines.append(
            f"| `{result['case_id']}` | `{result['proposal_class']}` | "
            f"`{result['safety_decision']}` | `{result['final_runtime_outcome']}` | `{result['passed']}` |"
        )
    lines.append("")
    return "\n".join(lines)
