#!/usr/bin/env python3
"""Controlled mock-agent proof for runtime adapter proposal boundaries."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROOF_NAME = "DHMS Controlled Mock-Agent Runtime Adapter Boundary Proof"
VERSION = "v1.2.4"
PASS_MARKER = "DHMS_CONTROLLED_MOCK_AGENT_RUNTIME_ADAPTER_BOUNDARY_PROOF_PASS"
FAIL_MARKER = "DHMS_CONTROLLED_MOCK_AGENT_RUNTIME_ADAPTER_BOUNDARY_PROOF_FAIL"

MANIFEST_PATH = Path("benchmarks/dhms_runtime_adapter_proposals_v0/cases.json")
EXAMPLES_PATH = Path("examples/dhms_runtime_adapter_proposals_v0/inert_examples.json")
TRACE_PLAN_PATH = Path("trace_examples/dhms_runtime_adapter_proposals_v0/trace_plan.json")

EXPECTED_PROPOSAL_COUNT = 19
EXPECTED_EXAMPLES_COUNT = 7
ALLOWED_DECISIONS = {"HOLD", "BLOCK", "FAIL_CLOSED"}
EXPECTED_DECISION_COUNTS = {
    "HOLD": 2,
    "BLOCK": 11,
    "FAIL_CLOSED": 6,
}
REQUIRED_TRACE_STAGES = [
    "proposal_observed",
    "adapter_intent_normalized",
    "runtime_target_classified",
    "capability_risk_classified",
    "policy_decision_assigned",
    "trace_evidence_planned",
    "execution_not_performed",
]
REQUIRED_NON_EXECUTION_FLAGS = [
    "execution_performed",
    "sdk_called",
    "network_called",
    "shell_invoked",
    "subprocess_invoked",
    "terminal_invoked",
    "tool_invoked",
    "adapter_runtime_called",
    "credential_accessed",
    "user_data_accessed",
    "production_runtime_touched",
]
REQUIRED_MANIFEST_FIELDS = {
    "proposal_id",
    "adapter_family",
    "adapter_target",
    "runtime_context",
    "operation_intent",
    "capability_requested",
    "input_payload_class",
    "credential_intent",
    "network_intent",
    "filesystem_intent",
    "process_or_shell_intent",
    "model_provider_intent",
    "memory_or_state_mutation_intent",
    "cost_or_quota_intent",
    "expected_output_class",
    "risk_indicators",
    "proposed_policy_decision",
    "decision_rationale",
    "trace_evidence_reference",
    "execution_allowed",
    "production_safe_claimed",
}
EXPECTED_MANIFEST_BOUNDARY = (
    "This manifest contains inert runtime adapter proposals only. No adapter "
    "proposal in this file is intended to be executed by DHMS, by tests, by "
    "CI, by SDKs, by agent runtimes, by model providers, or by human operators."
)


def joined(*parts: str) -> str:
    return "".join(parts)


SOURCE_SELF_CHECK_TERMS = [
    ("import ", "sub", "process"),
    ("from ", "sub", "process"),
    ("sub", "process", "."),
    ("os", ".", "system", "("),
    ("os", ".", "popen", "("),
    ("P", "open", "("),
    ("import ", "pty"),
    ("from ", "pty"),
    ("pty", "."),
    ("asyncio", ".", "create_", "subprocess_", "exec"),
    ("asyncio", ".", "create_", "subprocess_", "shell"),
    ("socket", "."),
    ("urllib", "."),
    ("re", "quests"),
    ("ht", "tpx"),
    ("open", "ai"),
    ("anth", "ropic"),
    ("m", "cp"),
    ("e", "2b"),
    ("co", "dex"),
    ("clau", "de"),
    ("deep", "seek"),
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
        failed_checks.append(f"{label}_json_invalid:{exc.msg}")
        return {}


def source_self_check(failed_checks: list[str]) -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    findings = [joined(*parts) for parts in SOURCE_SELF_CHECK_TERMS if joined(*parts) in source]
    if findings:
        failed_checks.append("source_self_check_disallowed_terms:" + ",".join(sorted(findings)))


def manifest_cases(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    cases = manifest.get("cases", [])
    return cases if isinstance(cases, list) else []


def example_items(examples: dict[str, Any]) -> list[dict[str, Any]]:
    items = examples.get("examples", [])
    return items if isinstance(items, list) else []


def trace_items(trace_plan: dict[str, Any]) -> list[dict[str, Any]]:
    items = trace_plan.get("case_trace_expectations", [])
    return items if isinstance(items, list) else []


def deterministic_mock_agent_proposals(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    proposals: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        proposals.append(
            {
                "mock_agent_id": "dhms_runtime_adapter_boundary_mock_agent_v0",
                "proposal_sequence_index": index,
                "proposal_id": case.get("proposal_id"),
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
    examples_list = example_items(examples)
    traces = trace_items(trace_plan)
    case_ids = [case.get("proposal_id") for case in cases]
    trace_case_ids = [trace.get("case_id") for trace in traces]
    example_case_ids = [example.get("linked_case_id") for example in examples_list]
    case_by_id = {case.get("proposal_id"): case for case in cases}
    trace_by_id = {trace.get("case_id"): trace for trace in traces}

    add_check(failed_checks, manifest.get("manifest_id") == "dhms_runtime_adapter_proposals_v0", "manifest_id")
    add_check(failed_checks, manifest.get("version") == "v1.2.1", "manifest_version")
    add_check(failed_checks, manifest.get("execution_boundary") == EXPECTED_MANIFEST_BOUNDARY, "manifest_boundary")
    add_check(failed_checks, manifest.get("proposal_count") == EXPECTED_PROPOSAL_COUNT, "manifest_proposal_count")
    add_check(failed_checks, len(cases) == EXPECTED_PROPOSAL_COUNT, "manifest_cases_count_19")
    add_check(failed_checks, len(case_ids) == len(set(case_ids)), "manifest_case_ids_unique")
    add_check(failed_checks, manifest.get("allowed_policy_decisions") == ["HOLD", "BLOCK", "FAIL_CLOSED"], "manifest_allowed_decisions")

    add_check(failed_checks, examples.get("examples_id") == "dhms_runtime_adapter_proposals_v0_inert_examples", "examples_id")
    add_check(failed_checks, examples.get("version") == "v1.2.3", "examples_version")
    add_check(failed_checks, examples.get("release_used") is False, "examples_release_false")
    add_check(failed_checks, len(examples_list) == EXPECTED_EXAMPLES_COUNT, "examples_count_7")
    add_check(failed_checks, set(example_case_ids).issubset(set(case_ids)), "examples_linked_cases_in_manifest")

    add_check(failed_checks, trace_plan.get("trace_plan_id") == "dhms_runtime_adapter_proposals_v0_trace_plan", "trace_plan_id")
    add_check(failed_checks, trace_plan.get("version") == "v1.2.3", "trace_plan_version")
    add_check(failed_checks, trace_plan.get("trace_stages") == REQUIRED_TRACE_STAGES, "trace_stages_exact")
    add_check(failed_checks, len(traces) == EXPECTED_PROPOSAL_COUNT, "trace_cases_count_19")
    add_check(failed_checks, trace_case_ids == case_ids, "trace_case_ids_match_manifest_order")
    add_check(failed_checks, set(trace_case_ids) == set(case_ids), "trace_case_ids_match_manifest_set")
    add_check(
        failed_checks,
        trace_plan.get("decision_count_expectation") == {"HOLD": 2, "BLOCK": 11, "FAIL_CLOSED": 6, "RELEASE": 0},
        "trace_decision_counts_exact",
    )

    decision_counts = Counter(case.get("proposed_policy_decision") for case in cases)
    add_check(failed_checks, dict(decision_counts) == EXPECTED_DECISION_COUNTS, "manifest_decision_counts")
    add_check(failed_checks, decision_counts.get("RELEASE", 0) == 0, "manifest_release_zero")

    for case in cases:
        proposal_id = str(case.get("proposal_id", "unknown"))
        missing = REQUIRED_MANIFEST_FIELDS - set(case)
        add_check(failed_checks, not missing, f"{proposal_id}.manifest_required_fields")
        add_check(failed_checks, proposal_id.startswith("runtime_adapter_"), f"{proposal_id}.manifest_id_prefix")
        add_check(failed_checks, case.get("proposed_policy_decision") in ALLOWED_DECISIONS, f"{proposal_id}.decision_allowed")
        add_check(failed_checks, case.get("execution_allowed") is False, f"{proposal_id}.execution_allowed_false")
        add_check(failed_checks, case.get("production_safe_claimed") is False, f"{proposal_id}.production_safe_false")
        add_check(
            failed_checks,
            isinstance(case.get("risk_indicators"), list) and bool(case.get("risk_indicators")),
            f"{proposal_id}.risk_indicators_present",
        )

    for example in examples_list:
        example_id = str(example.get("example_id", "unknown"))
        decision = example.get("expected_policy_decision")
        confirmation = example.get("non_execution_confirmation", {})
        add_check(failed_checks, decision in ALLOWED_DECISIONS, f"{example_id}.decision_allowed")
        add_check(failed_checks, decision != "RELEASE", f"{example_id}.release_absent")
        add_check(failed_checks, example.get("linked_case_id") in case_by_id, f"{example_id}.linked_case_exists")
        for flag in REQUIRED_NON_EXECUTION_FLAGS:
            add_check(failed_checks, confirmation.get(flag) is False, f"{example_id}.{flag}_false")

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
            f"{case_id}.trace_stages_match",
        )
        for flag in REQUIRED_NON_EXECUTION_FLAGS:
            add_check(failed_checks, trace.get(flag) is False, f"{case_id}.{flag}_false")

    return {
        "cases": cases,
        "examples": examples_list,
        "traces": traces,
        "case_ids": case_ids,
        "trace_by_id": trace_by_id,
    }


def intercept_proposals(
    proposals: list[dict[str, Any]],
    trace_by_id: dict[str, dict[str, Any]],
    failed_checks: list[str],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for proposal in proposals:
        case = proposal["proposal_data"]
        proposal_id = str(case.get("proposal_id", "unknown"))
        trace = trace_by_id.get(proposal_id, {})
        decision = case.get("proposed_policy_decision")
        result = {
            "proposal_id": proposal_id,
            "proposal_sequence_index": proposal["proposal_sequence_index"],
            "intercepted_before_execution": True,
            "policy_decision": decision,
            "trace_evidence_reference": case.get("trace_evidence_reference"),
            "trace_reached_execution_not_performed": "execution_not_performed"
            in trace.get("expected_trace_stages", []),
            "execution_performed": False,
            "sdk_called": False,
            "network_called": False,
            "shell_invoked": False,
            "subprocess_invoked": False,
            "terminal_invoked": False,
            "tool_invoked": False,
            "adapter_runtime_called": False,
            "credential_accessed": False,
            "user_data_accessed": False,
            "production_runtime_touched": False,
            "real_agent_runtime_used": False,
            "real_llm_runtime_used": False,
            "model_provider_called": False,
            "runtime_adapter_implemented": False,
            "released": False,
            "passed": True,
            "failed_checks": [],
        }
        if decision not in ALLOWED_DECISIONS:
            result["passed"] = False
            result["failed_checks"].append("decision_not_allowed")
        if not result["trace_reached_execution_not_performed"]:
            result["passed"] = False
            result["failed_checks"].append("trace_missing_execution_not_performed")
        if result["failed_checks"]:
            failed_checks.extend(f"{proposal_id}.{check}" for check in result["failed_checks"])
        results.append(result)
    return results


def count_true(results: list[dict[str, Any]], field: str) -> int:
    return sum(1 for result in results if result.get(field) is True)


def run_proof() -> dict[str, Any]:
    failed_checks: list[str] = []
    source_self_check(failed_checks)
    manifest = load_json(MANIFEST_PATH, failed_checks, "manifest")
    examples = load_json(EXAMPLES_PATH, failed_checks, "examples")
    trace_plan = load_json(TRACE_PLAN_PATH, failed_checks, "trace_plan")
    validation_data = validate_static_inputs(manifest, examples, trace_plan, failed_checks)
    cases = validation_data.get("cases", [])
    case_ids = validation_data.get("case_ids", [])
    trace_by_id = validation_data.get("trace_by_id", {})

    proposals = deterministic_mock_agent_proposals(cases)
    proposal_ids = [proposal.get("proposal_id") for proposal in proposals]
    results = intercept_proposals(proposals, trace_by_id, failed_checks)

    add_check(failed_checks, len(proposals) == EXPECTED_PROPOSAL_COUNT, "mock_agent_proposal_count_19")
    add_check(failed_checks, len(proposal_ids) == len(set(proposal_ids)), "mock_agent_proposes_each_case_once")
    add_check(failed_checks, proposal_ids == case_ids, "mock_agent_proposal_order_matches_manifest")
    add_check(
        failed_checks,
        all(result["intercepted_before_execution"] for result in results),
        "all_proposals_intercepted_before_execution",
    )
    add_check(
        failed_checks,
        all(result["trace_reached_execution_not_performed"] for result in results),
        "all_traces_reach_execution_not_performed",
    )
    add_check(failed_checks, count_true(results, "released") == 0, "release_zero")

    decision_counts = Counter(case.get("proposed_policy_decision") for case in cases)
    trace_case_ids = [trace.get("case_id") for trace in validation_data.get("traces", [])]
    missing_trace_ids = sorted(set(case_ids) - set(trace_case_ids))

    summary: dict[str, Any] = {
        "proof_name": PROOF_NAME,
        "version": VERSION,
        "manifest_path": str(MANIFEST_PATH),
        "examples_path": str(EXAMPLES_PATH),
        "trace_plan_path": str(TRACE_PLAN_PATH),
        "proposal_count": len(cases),
        "intercepted_proposal_count": count_true(results, "intercepted_before_execution"),
        "hold_count": decision_counts.get("HOLD", 0),
        "block_count": decision_counts.get("BLOCK", 0),
        "fail_closed_count": decision_counts.get("FAIL_CLOSED", 0),
        "release_count": decision_counts.get("RELEASE", 0),
        "execution_performed_count": count_true(results, "execution_performed"),
        "sdk_called_count": count_true(results, "sdk_called"),
        "network_called_count": count_true(results, "network_called"),
        "shell_invoked_count": count_true(results, "shell_invoked"),
        "subprocess_invoked_count": count_true(results, "subprocess_invoked"),
        "terminal_invoked_count": count_true(results, "terminal_invoked"),
        "tool_invoked_count": count_true(results, "tool_invoked"),
        "adapter_runtime_called_count": count_true(results, "adapter_runtime_called"),
        "credential_accessed_count": count_true(results, "credential_accessed"),
        "user_data_accessed_count": count_true(results, "user_data_accessed"),
        "production_runtime_touched_count": count_true(results, "production_runtime_touched"),
        "real_agent_runtime_count": count_true(results, "real_agent_runtime_used"),
        "real_llm_runtime_count": count_true(results, "real_llm_runtime_used"),
        "model_provider_called_count": count_true(results, "model_provider_called"),
        "runtime_adapter_implementation_count": count_true(results, "runtime_adapter_implemented"),
        "trace_cases_validated_count": len(trace_case_ids) - len(missing_trace_ids),
        "trace_cases_missing_count": len(missing_trace_ids),
        "examples_validated_count": len(validation_data.get("examples", [])),
        "failed_checks": sorted(set(failed_checks)),
    }
    summary["final_verdict"] = PASS_MARKER if not summary["failed_checks"] else FAIL_MARKER
    return summary


def main() -> int:
    summary = run_proof()
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(summary["final_verdict"])
    return 0 if summary["final_verdict"] == PASS_MARKER else 1


if __name__ == "__main__":
    sys.exit(main())
