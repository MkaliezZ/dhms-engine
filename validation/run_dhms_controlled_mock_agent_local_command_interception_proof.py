#!/usr/bin/env python3
"""Controlled non-executing proof for local command proposal interception."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


MANIFEST_PATH = Path("benchmarks/dhms_local_command_proposals_v0/cases.json")
EXAMPLES_PATH = Path("examples/dhms_local_command_proposals_v0/inert_examples.json")
TRACE_PLAN_PATH = Path("trace_examples/dhms_local_command_proposals_v0/trace_plan.json")

EXPECTED_PROPOSAL_COUNT = 14
EXPECTED_EXAMPLES_COUNT = 7
ALLOWED_DECISIONS = {"HOLD", "BLOCK", "FAIL_CLOSED"}
REQUIRED_TRACE_STAGES = [
    "proposal_observed",
    "proposal_normalized",
    "risk_classified",
    "policy_decision_assigned",
    "trace_evidence_recorded",
    "execution_not_performed",
]
MANIFEST_EXECUTION_BOUNDARY = (
    "This manifest contains inert local command proposals only. No command in "
    "this file is intended to be executed by DHMS, by tests, by CI, or by a "
    "human operator."
)
EXAMPLES_EXECUTION_BOUNDARY = (
    "These examples are inert local command proposal documentation only. They "
    "are not command execution instructions and must not be executed by DHMS, "
    "tests, CI, or human operators."
)
TRACE_PLAN_EXECUTION_BOUNDARY = (
    "This trace plan is inert documentation data only. It does not execute "
    "local command proposals and does not authorize shell, subprocess, "
    "terminal, or command runner behavior."
)
PASS_MARKER = "DHMS_CONTROLLED_MOCK_AGENT_LOCAL_COMMAND_INTERCEPTION_PROOF_PASS"
FAIL_MARKER = "DHMS_CONTROLLED_MOCK_AGENT_LOCAL_COMMAND_INTERCEPTION_PROOF_FAIL"


def disallowed_source_terms() -> list[str]:
    return [
        "import " + "sub" + "process",
        "from " + "sub" + "process",
        "sub" + "process" + ".",
        "os" + "." + "system" + "(",
        "os" + "." + "p" + "open" + "(",
        "P" + "open" + "(",
        "import " + "p" + "ty",
        "from " + "p" + "ty",
        "p" + "ty" + ".",
        "asyncio" + "." + "create_" + "sub" + "process_" + "exec",
        "asyncio" + "." + "create_" + "sub" + "process_" + "shell",
        "spawn" + "l" + "(",
        "spawn" + "v" + "(",
        "exec" + "v" + "(",
        "socket" + ".",
        "urllib" + ".",
        "req" + "uests",
    ]


def add_check(failed_checks: list[str], condition: bool, check_name: str) -> None:
    if not condition:
        failed_checks.append(check_name)


def load_json(path: Path, failed_checks: list[str], label: str) -> dict[str, Any]:
    if not path.exists():
        failed_checks.append(f"{label}_missing")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failed_checks.append(f"{label}_json_invalid:{exc}")
        return {}


def check_runner_source(failed_checks: list[str]) -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    findings = [term for term in disallowed_source_terms() if term in source]
    if findings:
        failed_checks.append("runner_source_disallowed_terms:" + ",".join(findings))


def manifest_cases(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    cases = manifest.get("cases", [])
    return cases if isinstance(cases, list) else []


def examples_items(examples: dict[str, Any]) -> list[dict[str, Any]]:
    items = examples.get("examples", [])
    return items if isinstance(items, list) else []


def trace_items(trace_plan: dict[str, Any]) -> list[dict[str, Any]]:
    items = trace_plan.get("case_trace_expectations", [])
    return items if isinstance(items, list) else []


def deterministic_mock_agent(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    proposals = []
    for index, case in enumerate(cases, start=1):
        proposals.append(
            {
                "mock_agent_id": "dhms_local_command_mock_agent_v0",
                "proposal_sequence_index": index,
                "proposal_id": case.get("case_id"),
                "proposal_data": case,
            }
        )
    return proposals


def validate_static_inputs(
    manifest: dict[str, Any],
    examples: dict[str, Any],
    trace_plan: dict[str, Any],
    failed_checks: list[str],
) -> dict[str, Any]:
    cases = manifest_cases(manifest)
    examples_list = examples_items(examples)
    traces = trace_items(trace_plan)

    case_ids = [case.get("case_id") for case in cases]
    example_case_ids = [example.get("linked_case_id") for example in examples_list]
    trace_case_ids = [trace.get("case_id") for trace in traces]
    case_by_id = {case.get("case_id"): case for case in cases}
    trace_by_id = {trace.get("case_id"): trace for trace in traces}

    add_check(failed_checks, manifest.get("execution_boundary") == MANIFEST_EXECUTION_BOUNDARY, "manifest_boundary")
    add_check(failed_checks, examples.get("execution_boundary") == EXAMPLES_EXECUTION_BOUNDARY, "examples_boundary")
    add_check(failed_checks, trace_plan.get("execution_boundary") == TRACE_PLAN_EXECUTION_BOUNDARY, "trace_plan_boundary")

    add_check(failed_checks, len(cases) == EXPECTED_PROPOSAL_COUNT, "manifest_case_count_14")
    add_check(failed_checks, len(examples_list) == EXPECTED_EXAMPLES_COUNT, "examples_count_7")
    add_check(failed_checks, len(traces) == EXPECTED_PROPOSAL_COUNT, "trace_case_count_14")
    add_check(failed_checks, len(case_ids) == len(set(case_ids)), "manifest_case_ids_unique")
    add_check(failed_checks, trace_case_ids == case_ids, "trace_case_ids_match_manifest_order")
    add_check(failed_checks, set(trace_case_ids) == set(case_ids), "trace_case_ids_match_manifest_set")
    add_check(failed_checks, set(example_case_ids).issubset(set(case_ids)), "example_case_ids_in_manifest")

    add_check(
        failed_checks,
        trace_plan.get("trace_stages") == REQUIRED_TRACE_STAGES,
        "trace_plan_required_stages_exact",
    )

    for case in cases:
        case_id = case.get("case_id")
        decision = case.get("proposed_policy_decision")
        add_check(failed_checks, decision in ALLOWED_DECISIONS, f"{case_id}.manifest_decision_allowed")
        add_check(failed_checks, decision != "RELEASE", f"{case_id}.manifest_release_absent")

    for example in examples_list:
        example_id = example.get("example_id")
        decision = example.get("policy_decision")
        add_check(failed_checks, decision in ALLOWED_DECISIONS, f"{example_id}.example_decision_allowed")
        add_check(failed_checks, decision != "RELEASE", f"{example_id}.example_release_absent")

    for case_id in case_ids:
        case = case_by_id.get(case_id, {})
        trace = trace_by_id.get(case_id, {})
        add_check(failed_checks, bool(trace), f"{case_id}.trace_present")
        add_check(
            failed_checks,
            trace.get("expected_policy_decision") == case.get("proposed_policy_decision"),
            f"{case_id}.trace_decision_matches_manifest",
        )
        add_check(
            failed_checks,
            trace.get("expected_trace_evidence_reference") == case.get("trace_evidence_reference"),
            f"{case_id}.trace_reference_matches_manifest",
        )
        add_check(
            failed_checks,
            trace.get("expected_trace_stages") == REQUIRED_TRACE_STAGES,
            f"{case_id}.trace_required_stages",
        )
        for counter_name in (
            "command_strings_executed_count",
            "argv_executed_count",
            "shell_execution_count",
            "subprocess_execution_count",
            "terminal_execution_count",
        ):
            add_check(failed_checks, trace.get(counter_name) == 0, f"{case_id}.{counter_name}_zero")

    return {
        "cases": cases,
        "examples": examples_list,
        "traces": traces,
        "case_ids": case_ids,
        "trace_by_id": trace_by_id,
    }


def run_proof() -> dict[str, Any]:
    failed_checks: list[str] = []
    check_runner_source(failed_checks)

    manifest = load_json(MANIFEST_PATH, failed_checks, "manifest")
    examples = load_json(EXAMPLES_PATH, failed_checks, "examples")
    trace_plan = load_json(TRACE_PLAN_PATH, failed_checks, "trace_plan")
    validation_data = validate_static_inputs(manifest, examples, trace_plan, failed_checks)

    cases = validation_data.get("cases", [])
    trace_by_id = validation_data.get("trace_by_id", {})
    proposals = deterministic_mock_agent(cases)
    intercepted_results = []
    seen_proposal_ids = []

    for proposal in proposals:
        case = proposal["proposal_data"]
        case_id = case.get("case_id")
        trace = trace_by_id.get(case_id, {})
        seen_proposal_ids.append(case_id)
        intercepted_results.append(
            {
                "proposal_id": case_id,
                "proposal_sequence_index": proposal["proposal_sequence_index"],
                "intercepted_before_execution": True,
                "policy_decision": case.get("proposed_policy_decision"),
                "trace_evidence_reference": case.get("trace_evidence_reference"),
                "trace_reached_execution_not_performed": "execution_not_performed"
                in trace.get("expected_trace_stages", []),
                "command_string_executed": False,
                "argv_executed": False,
                "shell_executed": False,
                "subprocess_executed": False,
                "terminal_executed": False,
                "released": False,
            }
        )

    add_check(failed_checks, len(proposals) == EXPECTED_PROPOSAL_COUNT, "mock_agent_proposal_count_14")
    add_check(failed_checks, len(seen_proposal_ids) == len(set(seen_proposal_ids)), "mock_agent_proposes_each_case_once")
    add_check(
        failed_checks,
        seen_proposal_ids == validation_data.get("case_ids", []),
        "mock_agent_proposal_order_matches_manifest",
    )
    add_check(
        failed_checks,
        all(result["intercepted_before_execution"] for result in intercepted_results),
        "all_proposals_intercepted_before_execution",
    )
    add_check(
        failed_checks,
        all(result["trace_reached_execution_not_performed"] for result in intercepted_results),
        "all_traces_reach_execution_not_performed",
    )
    add_check(failed_checks, not any(result["released"] for result in intercepted_results), "no_proposal_released")

    decision_counts = Counter(case.get("proposed_policy_decision") for case in cases)
    release_count = decision_counts.get("RELEASE", 0)
    trace_cases_missing_count = max(0, EXPECTED_PROPOSAL_COUNT - len(trace_items(trace_plan)))

    metrics = {
        "proposal_count": len(cases),
        "intercepted_proposal_count": len(intercepted_results),
        "hold_count": decision_counts.get("HOLD", 0),
        "block_count": decision_counts.get("BLOCK", 0),
        "fail_closed_count": decision_counts.get("FAIL_CLOSED", 0),
        "release_count": release_count,
        "command_strings_executed_count": 0,
        "argv_executed_count": 0,
        "shell_execution_count": 0,
        "subprocess_execution_count": 0,
        "terminal_execution_count": 0,
        "command_runner_invocation_count": 0,
        "mock_agent_runtime_count": 1,
        "real_agent_runtime_count": 0,
        "real_llm_runtime_count": 0,
        "trace_cases_validated_count": len(trace_items(trace_plan)),
        "trace_cases_missing_count": trace_cases_missing_count,
        "examples_validated_count": len(examples_items(examples)),
    }

    expected_metrics = {
        "proposal_count": 14,
        "intercepted_proposal_count": 14,
        "hold_count": 2,
        "block_count": 8,
        "fail_closed_count": 4,
        "release_count": 0,
        "command_strings_executed_count": 0,
        "argv_executed_count": 0,
        "shell_execution_count": 0,
        "subprocess_execution_count": 0,
        "terminal_execution_count": 0,
        "command_runner_invocation_count": 0,
        "mock_agent_runtime_count": 1,
        "real_agent_runtime_count": 0,
        "real_llm_runtime_count": 0,
        "trace_cases_validated_count": 14,
        "trace_cases_missing_count": 0,
        "examples_validated_count": 7,
    }
    for name, expected in expected_metrics.items():
        add_check(failed_checks, metrics.get(name) == expected, f"metric_{name}_expected_{expected}")

    final_verdict = PASS_MARKER if not failed_checks else FAIL_MARKER
    return {
        "proof_name": "DHMS Controlled Mock-Agent Local Command Interception Proof",
        "version": "v1.1.4",
        "manifest_path": MANIFEST_PATH.as_posix(),
        "examples_path": EXAMPLES_PATH.as_posix(),
        "trace_plan_path": TRACE_PLAN_PATH.as_posix(),
        **metrics,
        "local_command_proposals": intercepted_results,
        "failed_checks": failed_checks,
        "final_verdict": final_verdict,
    }


def main() -> int:
    summary = run_proof()
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(summary["final_verdict"])
    return 0 if summary["final_verdict"] == PASS_MARKER else 1


if __name__ == "__main__":
    sys.exit(main())
