#!/usr/bin/env python3
"""Deterministic execution runtime contract stub for v0.5.1.

This module defines mock runtime contract objects and validates that they remain
non-executing. It does not invoke runtime wrappers, tools, SQL sandboxes,
providers, agent SDKs, HTTP adapters, production checkers, or production
runners.
"""

from __future__ import annotations

from collections import Counter
from typing import Any


RUNTIME_CONTRACT_VERSION = "dhms-execution-runtime-contract-v0.5.1-stub"
ALLOWED_DECISIONS = {"ALLOW", "BLOCK", "SANDBOX", "REWRITE"}

REQUIRED_RUNTIME_INPUT_REQUEST_FIELDS = {
    "request_id",
    "runtime_contract_version",
    "source",
    "user_intent",
    "context_snapshot",
    "memory_snapshot",
    "tool_state_snapshot",
    "requested_tool",
    "black_box_mode",
}

REQUIRED_TOOL_CALL_PROPOSAL_FIELDS = {
    "proposal_id",
    "request_id",
    "tool_type",
    "tool_name",
    "tool_args",
    "proposed_by",
    "proposal_observed",
    "tool_executed",
}

REQUIRED_SAFETY_DECISION_FIELDS = {
    "decision_id",
    "request_id",
    "proposal_id",
    "decision",
    "allowed_actions",
    "blocked_actions",
    "sandbox_required",
    "rewrite_required",
    "reason_code",
    "dhms_final_decision",
}

REQUIRED_EXECUTION_DECISION_FIELDS = {
    "decision_id",
    "request_id",
    "proposal_id",
    "decision",
    "allow_execution",
    "block_execution",
    "sandbox_execution",
    "rewrite_execution",
    "dhms_final_decision",
}

REQUIRED_EXECUTION_TRACE_FIELDS = {
    "trace_id",
    "request_id",
    "proposal_id",
    "decision_id",
    "tool_type",
    "decision",
    "executed",
    "tool_executed",
    "provider_invoked",
    "agent_sdk_invoked",
    "external_service_sdk_invoked",
    "production_runner_invoked",
    "http_adapter_invoked",
    "external_mutation_detected",
    "black_box_validated",
}

NON_EXECUTION_TRACE_FLAGS = {
    "executed",
    "tool_executed",
    "provider_invoked",
    "agent_sdk_invoked",
    "external_service_sdk_invoked",
    "production_runner_invoked",
    "http_adapter_invoked",
    "external_mutation_detected",
}


def build_runtime_contract_examples() -> list[dict[str, Any]]:
    return [
        build_contract_example(
            example_id="sql_delete_blocked",
            request_id="req_sql_delete_blocked",
            proposal_id="prop_sql_delete_blocked",
            decision_id="dec_sql_delete_blocked",
            trace_id="trace_sql_delete_blocked",
            source="runtime_contract_stub",
            user_intent="Delete account row without explicit authorization.",
            requested_tool="sql",
            tool_type="SQL",
            tool_name="sqlite_temp_sandbox",
            tool_args={
                "proposed_sql": "DELETE FROM toy_accounts WHERE id = 1;",
                "database": "temporary_local_sqlite",
            },
            decision="BLOCK",
            allowed_actions=[],
            blocked_actions=["DELETE"],
            sandbox_required=False,
            rewrite_required=False,
            reason_code="mutation_sql_without_authorization",
        ),
        build_contract_example(
            example_id="sql_select_sandbox",
            request_id="req_sql_select_sandbox",
            proposal_id="prop_sql_select_sandbox",
            decision_id="dec_sql_select_sandbox",
            trace_id="trace_sql_select_sandbox",
            source="runtime_contract_stub",
            user_intent="Inspect synthetic toy account rows through a read-only SQL path.",
            requested_tool="sql",
            tool_type="SQL",
            tool_name="sqlite_temp_sandbox",
            tool_args={
                "proposed_sql": "SELECT id, label, status FROM toy_accounts ORDER BY id;",
                "database": "temporary_local_sqlite",
            },
            decision="SANDBOX",
            allowed_actions=["SELECT"],
            blocked_actions=["INSERT", "UPDATE", "DELETE", "DROP", "ALTER"],
            sandbox_required=True,
            rewrite_required=False,
            reason_code="select_only_requires_sandbox",
        ),
        build_contract_example(
            example_id="openclaw_runtime_blocked",
            request_id="req_openclaw_runtime_blocked",
            proposal_id="prop_openclaw_runtime_blocked",
            decision_id="dec_openclaw_runtime_blocked",
            trace_id="trace_openclaw_runtime_blocked",
            source="runtime_contract_stub",
            user_intent="Attempt to route through OpenClaw as a runtime backend.",
            requested_tool="openclaw",
            tool_type="OPENCLAW",
            tool_name="openclaw_runtime_candidate",
            tool_args={"mode": "runtime_candidate", "profile_required": True},
            decision="BLOCK",
            allowed_actions=[],
            blocked_actions=["OPENCLAW_RUNTIME_EXECUTION"],
            sandbox_required=False,
            rewrite_required=False,
            reason_code="openclaw_runtime_integration_not_implemented",
        ),
        build_contract_example(
            example_id="future_system_tool_blocked",
            request_id="req_future_system_tool_blocked",
            proposal_id="prop_future_system_tool_blocked",
            decision_id="dec_future_system_tool_blocked",
            trace_id="trace_future_system_tool_blocked",
            source="runtime_contract_stub",
            user_intent="Write a file through a future system tool path.",
            requested_tool="future_file_system",
            tool_type="FUTURE_API_FILE_SYSTEM",
            tool_name="future_file_system_tool",
            tool_args={"path": "/tmp/dhms-runtime-stub.txt", "operation": "write"},
            decision="BLOCK",
            allowed_actions=[],
            blocked_actions=["FILE_WRITE"],
            sandbox_required=False,
            rewrite_required=False,
            reason_code="future_tool_backend_not_implemented",
        ),
    ]


def build_contract_example(
    *,
    example_id: str,
    request_id: str,
    proposal_id: str,
    decision_id: str,
    trace_id: str,
    source: str,
    user_intent: str,
    requested_tool: str,
    tool_type: str,
    tool_name: str,
    tool_args: dict[str, Any],
    decision: str,
    allowed_actions: list[str],
    blocked_actions: list[str],
    sandbox_required: bool,
    rewrite_required: bool,
    reason_code: str,
) -> dict[str, Any]:
    runtime_input_request = {
        "request_id": request_id,
        "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
        "source": source,
        "user_intent": user_intent,
        "context_snapshot": {"mode": "contract_stub", "observable_context_only": True},
        "memory_snapshot": {"memory_used": False, "stale_memory_authorization": False},
        "tool_state_snapshot": {"tool_available": False, "tool_already_executed": False},
        "requested_tool": requested_tool,
        "black_box_mode": True,
    }
    tool_call_proposal = {
        "proposal_id": proposal_id,
        "request_id": request_id,
        "tool_type": tool_type,
        "tool_name": tool_name,
        "tool_args": tool_args,
        "proposed_by": "contract_stub",
        "proposal_observed": True,
        "tool_executed": False,
    }
    safety_decision = {
        "decision_id": decision_id,
        "request_id": request_id,
        "proposal_id": proposal_id,
        "decision": decision,
        "allowed_actions": allowed_actions,
        "blocked_actions": blocked_actions,
        "sandbox_required": sandbox_required,
        "rewrite_required": rewrite_required,
        "reason_code": reason_code,
        "dhms_final_decision": True,
    }
    execution_decision = {
        "decision_id": decision_id,
        "request_id": request_id,
        "proposal_id": proposal_id,
        "decision": decision,
        "allow_execution": decision == "ALLOW",
        "block_execution": decision == "BLOCK",
        "sandbox_execution": decision == "SANDBOX",
        "rewrite_execution": decision == "REWRITE",
        "dhms_final_decision": True,
    }
    execution_trace = {
        "trace_id": trace_id,
        "request_id": request_id,
        "proposal_id": proposal_id,
        "decision_id": decision_id,
        "tool_type": tool_type,
        "decision": decision,
        "executed": False,
        "tool_executed": False,
        "provider_invoked": False,
        "agent_sdk_invoked": False,
        "external_service_sdk_invoked": False,
        "production_runner_invoked": False,
        "http_adapter_invoked": False,
        "external_mutation_detected": False,
        "black_box_validated": True,
    }
    return {
        "example_id": example_id,
        "runtime_input_request": runtime_input_request,
        "tool_call_proposal": tool_call_proposal,
        "safety_decision": safety_decision,
        "execution_decision": execution_decision,
        "execution_trace": execution_trace,
    }


def validate_runtime_contract_examples() -> dict[str, Any]:
    examples = build_runtime_contract_examples()
    example_results = [validate_example(example) for example in examples]
    failed_checks = [
        f"{result['example_id']}.{check}"
        for result in example_results
        for check in result["failed_checks"]
    ]
    decisions_by_type = dict(sorted(Counter(result["decision"] for result in example_results).items()))
    passed_examples = sum(1 for result in example_results if result["passed"])
    status = "PASS" if not failed_checks and passed_examples == len(examples) else "FAIL"
    return {
        "validation": "execution_runtime_contract_stub_v0_5_1",
        "status": status,
        "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
        "total_contract_examples": len(examples),
        "passed_examples": passed_examples,
        "failed_checks": failed_checks,
        "decisions_by_type": decisions_by_type,
        "allowed_decision_values": sorted(ALLOWED_DECISIONS),
        "examples": examples,
        "example_results": example_results,
        "runtime_wrapper_executed": False,
        "tool_execution_invoked": False,
        "sql_sandbox_execution_invoked": False,
        "openclaw_invoked": False,
        "deepseek_invoked": False,
        "provider_sdk_invoked": False,
        "agent_sdk_invoked": False,
        "http_adapter_invoked": False,
        "production_checker_invoked": False,
        "production_runner_invoked": False,
        "full_suite_validation_invoked": False,
        "final_verdict": (
            "READY_FOR_V0_5_2_TOOL_CALL_INTERCEPTOR_STUB"
            if status == "PASS"
            else "NEEDS_EXECUTION_RUNTIME_CONTRACT_STUB_FIX"
        ),
    }


def validate_example(example: dict[str, Any]) -> dict[str, Any]:
    failed_checks: list[str] = []
    runtime_input = example.get("runtime_input_request", {})
    proposal = example.get("tool_call_proposal", {})
    safety_decision = example.get("safety_decision", {})
    execution_decision = example.get("execution_decision", {})
    trace = example.get("execution_trace", {})

    require_fields("runtime_input_request", runtime_input, REQUIRED_RUNTIME_INPUT_REQUEST_FIELDS, failed_checks)
    require_fields("tool_call_proposal", proposal, REQUIRED_TOOL_CALL_PROPOSAL_FIELDS, failed_checks)
    require_fields("safety_decision", safety_decision, REQUIRED_SAFETY_DECISION_FIELDS, failed_checks)
    require_fields("execution_decision", execution_decision, REQUIRED_EXECUTION_DECISION_FIELDS, failed_checks)
    require_fields("execution_trace", trace, REQUIRED_EXECUTION_TRACE_FIELDS, failed_checks)

    decision = safety_decision.get("decision")
    if decision not in ALLOWED_DECISIONS:
        failed_checks.append("unknown_decision")
    if trace.get("decision") != decision or execution_decision.get("decision") != decision:
        failed_checks.append("decision_mismatch")
    if safety_decision.get("dhms_final_decision") is not True:
        failed_checks.append("dhms_final_decision_missing")
    if execution_decision.get("dhms_final_decision") is not True:
        failed_checks.append("execution_decision_dhms_final_missing")
    if runtime_input.get("black_box_mode") is not True:
        failed_checks.append("black_box_mode_not_true")
    if trace.get("black_box_validated") is not True:
        failed_checks.append("black_box_validated_not_true")
    if proposal.get("proposal_observed") is not True:
        failed_checks.append("proposal_not_observed")
    if proposal.get("tool_executed") is not False:
        failed_checks.append("proposal_tool_executed")
    for flag in sorted(NON_EXECUTION_TRACE_FLAGS):
        if trace.get(flag) is not False:
            failed_checks.append(f"{flag}_not_false")
    if execution_decision.get("allow_execution") is True:
        failed_checks.append("allow_execution_not_allowed_in_stub")
    if decision == "BLOCK" and execution_decision.get("block_execution") is not True:
        failed_checks.append("block_decision_not_reflected")
    if decision == "SANDBOX" and execution_decision.get("sandbox_execution") is not True:
        failed_checks.append("sandbox_decision_not_reflected")

    return {
        "example_id": example.get("example_id"),
        "tool_type": proposal.get("tool_type"),
        "decision": decision,
        "passed": not failed_checks,
        "failed_checks": failed_checks,
    }


def require_fields(prefix: str, payload: dict[str, Any], required_fields: set[str], failed_checks: list[str]) -> None:
    missing = sorted(required_fields.difference(payload))
    for field in missing:
        failed_checks.append(f"{prefix}.missing_{field}")
