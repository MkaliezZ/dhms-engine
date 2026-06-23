#!/usr/bin/env python3
"""Deterministic runtime execution gate stub for v0.5.6.

The execution gate sits between a DHMS runtime decision and any future backend
or tool execution. It never releases execution in v0.5.6. It does not execute
tools, execute SQL from the runtime path, invoke SQL sandbox execution from the
runtime path, implement OpenClaw runtime integration, call providers, use SDKs,
or run production checker/runner logic.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from execution_runtime_contract_stub import validate_runtime_contract_examples
from runtime_dry_run_loop_stub import run_runtime_dry_run_loop_stub
from sql_safety_runtime_mount_stub import run_sql_safety_runtime_mount_stub
from sql_safety_temp_sqlite_mutation_block_test import run_sql_safety_temp_sqlite_mutation_block_test
from sql_safety_temp_sqlite_select_only_sandbox import run_sql_safety_temp_sqlite_select_only_first_real_run
from tool_call_interceptor_stub import run_tool_call_interceptor_stub


ALLOWED_RUNTIME_DECISIONS = {"BLOCK", "SANDBOX"}
ALLOWED_GATE_RESULTS = {"CLOSED", "HELD_FOR_SANDBOX_BRIDGE", "HELD_FOR_BACKEND_ADAPTER"}
ALLOWED_GATE_REASON_CODES = {
    "BLOCKED_BY_SQL_SAFETY_MUTATION",
    "HELD_SQL_SELECT_REQUIRES_SANDBOX_BRIDGE",
    "BLOCKED_OPENCLAW_RUNTIME_ADAPTER_NOT_IMPLEMENTED",
    "BLOCKED_API_RUNTIME_BACKEND_NOT_IMPLEMENTED",
    "BLOCKED_UNKNOWN_OR_MALFORMED_TOOL",
    "FAIL_CLOSED_INVALID_GATE_INPUT",
}

REQUIRED_GATE_INPUT_FIELDS = {
    "gate_input_id",
    "dry_run_request_id",
    "request_id",
    "proposal_id",
    "runtime_decision_id",
    "tool_type",
    "runtime_decision",
    "dhms_final_decision",
    "sandbox_required",
    "sandbox_planned",
    "requested_backend",
    "backend_adapter_available",
    "black_box_mode",
    "executed",
}

REQUIRED_GATE_VERDICT_FIELDS = {
    "gate_id",
    "gate_input_id",
    "tool_type",
    "runtime_decision",
    "gate_result",
    "gate_reason_code",
    "execution_release_allowed",
    "sandbox_bridge_required",
    "backend_adapter_required",
    "dhms_gate_owner",
    "executed",
}

REQUIRED_GATE_TRACE_FIELDS = {
    "gate_trace_id",
    "gate_input_id",
    "gate_id",
    "dry_run_request_id",
    "request_id",
    "proposal_id",
    "tool_type",
    "runtime_decision",
    "gate_result",
    "dry_run_only",
    "execution_release_allowed",
    "executed",
    "tool_executed",
    "sql_executed",
    "sandbox_executed",
    "openclaw_invoked",
    "provider_invoked",
    "agent_sdk_invoked",
    "external_service_sdk_invoked",
    "production_runner_invoked",
    "http_adapter_invoked",
    "external_mutation_detected",
    "black_box_validated",
    "dhms_gate_owner",
}

NON_EXECUTION_TRACE_FLAGS = {
    "execution_release_allowed",
    "executed",
    "tool_executed",
    "sql_executed",
    "sandbox_executed",
    "openclaw_invoked",
    "provider_invoked",
    "agent_sdk_invoked",
    "external_service_sdk_invoked",
    "production_runner_invoked",
    "http_adapter_invoked",
    "external_mutation_detected",
}


def run_runtime_execution_gate_stub() -> dict[str, Any]:
    contract_preflight = validate_runtime_contract_examples()
    interceptor_preflight = run_tool_call_interceptor_stub()
    sql_mount_preflight = run_sql_safety_runtime_mount_stub()
    dry_run_loop_preflight = run_runtime_dry_run_loop_stub()
    select_only_preflight = run_sql_safety_temp_sqlite_select_only_first_real_run()
    mutation_block_preflight = run_sql_safety_temp_sqlite_mutation_block_test()

    gate_inputs = build_gate_inputs_from_dry_run_loop(dry_run_loop_preflight)
    records = [build_gate_record(gate_input) for gate_input in gate_inputs]
    record_results = [validate_gate_record(record) for record in records]

    failed_checks = [
        f"{result['gate_input_id']}.{check}"
        for result in record_results
        for check in result["failed_checks"]
    ]
    for name, result in [
        ("contract_preflight_failed", contract_preflight),
        ("interceptor_preflight_failed", interceptor_preflight),
        ("sql_mount_preflight_failed", sql_mount_preflight),
        ("dry_run_loop_preflight_failed", dry_run_loop_preflight),
        ("select_only_preflight_failed", select_only_preflight),
        ("mutation_block_preflight_failed", mutation_block_preflight),
    ]:
        if result.get("status") != "PASS":
            failed_checks.append(name)

    gate_results_by_type = dict(
        sorted(Counter(f"{result['tool_type']}:{result['gate_result']}" for result in record_results).items())
    )
    closed_count = sum(1 for result in record_results if result["gate_result"] == "CLOSED")
    held_for_sandbox_bridge_count = sum(
        1 for result in record_results if result["gate_result"] == "HELD_FOR_SANDBOX_BRIDGE"
    )
    held_for_backend_adapter_count = sum(
        1 for result in record_results if result["gate_result"] == "HELD_FOR_BACKEND_ADAPTER"
    )
    execution_release_allowed_count = sum(
        1 for record in records if record["gate_trace"]["execution_release_allowed"]
    )
    executed_count = sum(1 for record in records if record["gate_trace"]["executed"])
    passed_gate_inputs = sum(1 for result in record_results if result["passed"])
    status = "PASS" if not failed_checks and passed_gate_inputs == len(records) else "FAIL"

    return {
        "validation": "runtime_execution_gate_stub_v0_5_6",
        "status": status,
        "contract_preflight_passed": contract_preflight.get("status") == "PASS",
        "interceptor_preflight_passed": interceptor_preflight.get("status") == "PASS",
        "sql_mount_preflight_passed": sql_mount_preflight.get("status") == "PASS",
        "dry_run_loop_preflight_passed": dry_run_loop_preflight.get("status") == "PASS",
        "select_only_preflight_passed": select_only_preflight.get("status") == "PASS",
        "mutation_block_preflight_passed": mutation_block_preflight.get("status") == "PASS",
        "total_gate_inputs": len(records),
        "passed_gate_inputs": passed_gate_inputs,
        "gate_results_by_type": gate_results_by_type,
        "closed_count": closed_count,
        "held_for_sandbox_bridge_count": held_for_sandbox_bridge_count,
        "held_for_backend_adapter_count": held_for_backend_adapter_count,
        "execution_release_allowed_count": execution_release_allowed_count,
        "executed_count": executed_count,
        "failed_checks": failed_checks,
        "gate_records": records,
        "record_results": record_results,
        "runtime_wrapper_executed": False,
        "tool_execution_invoked": False,
        "sql_execution_invoked_from_runtime_path": False,
        "sqlite_database_created_from_runtime_path": False,
        "sql_sandbox_execution_invoked_from_runtime_path": False,
        "sql_sandbox_bridge_implemented": False,
        "openclaw_runtime_integration_implemented": False,
        "openclaw_invoked": False,
        "deepseek_invoked": False,
        "provider_sdk_invoked": False,
        "agent_sdk_invoked": False,
        "http_adapter_invoked": False,
        "production_checker_invoked": False,
        "production_runner_invoked": False,
        "full_suite_validation_invoked": False,
        "final_verdict": (
            "READY_FOR_V0_5_7_SQL_SANDBOX_RUNTIME_BRIDGE_PLAN"
            if status == "PASS"
            else "NEEDS_RUNTIME_EXECUTION_GATE_STUB_FIX"
        ),
    }


def build_gate_inputs_from_dry_run_loop(dry_run_loop_result: dict[str, Any]) -> list[dict[str, Any]]:
    records = dry_run_loop_result.get("runtime_records", [])
    return [build_gate_input(record) for record in records]


def build_gate_input(runtime_record: dict[str, Any]) -> dict[str, Any]:
    dry_run_request = runtime_record["dry_run_request"]
    raw_event = runtime_record["raw_event"]
    runtime_decision = runtime_record["runtime_decision"]
    tool_type = runtime_decision["tool_type"]
    return {
        "gate_input_id": f"gate_input_{dry_run_request['dry_run_request_id']}",
        "dry_run_request_id": dry_run_request["dry_run_request_id"],
        "request_id": raw_event["request_id"],
        "proposal_id": runtime_decision["proposal_id"],
        "runtime_decision_id": runtime_decision["runtime_decision_id"],
        "tool_type": tool_type,
        "runtime_decision": runtime_decision["decision"],
        "dhms_final_decision": runtime_decision["dhms_final_decision"],
        "sandbox_required": runtime_decision["sandbox_required"],
        "sandbox_planned": runtime_decision["sandbox_planned"],
        "requested_backend": requested_backend_for_tool(tool_type),
        "backend_adapter_available": False,
        "black_box_mode": True,
        "executed": False,
    }


def requested_backend_for_tool(tool_type: str) -> str:
    return {
        "SQL": "sql_safety_runtime_backend_candidate",
        "OPENCLAW": "openclaw_runtime_backend_candidate",
        "API": "future_api_runtime_backend_candidate",
        "FILE": "future_file_runtime_backend_candidate",
        "SYSTEM": "future_system_runtime_backend_candidate",
        "UNKNOWN": "unknown_backend",
    }.get(tool_type, "unknown_backend")


def build_gate_record(gate_input: dict[str, Any]) -> dict[str, Any]:
    verdict = build_gate_verdict(gate_input)
    trace = build_gate_trace(gate_input, verdict)
    return {
        "gate_input": gate_input,
        "gate_verdict": verdict,
        "gate_trace": trace,
    }


def build_gate_verdict(gate_input: dict[str, Any]) -> dict[str, Any]:
    tool_type = gate_input.get("tool_type")
    runtime_decision = gate_input.get("runtime_decision")
    sandbox_required = gate_input.get("sandbox_required") is True
    sandbox_planned = gate_input.get("sandbox_planned") is True

    gate_result = "CLOSED"
    gate_reason_code = "FAIL_CLOSED_INVALID_GATE_INPUT"
    sandbox_bridge_required = False
    backend_adapter_required = False

    if runtime_decision == "SANDBOX" and tool_type == "SQL" and sandbox_required and sandbox_planned:
        gate_result = "HELD_FOR_SANDBOX_BRIDGE"
        gate_reason_code = "HELD_SQL_SELECT_REQUIRES_SANDBOX_BRIDGE"
        sandbox_bridge_required = True
    elif runtime_decision == "BLOCK" and tool_type == "SQL":
        gate_result = "CLOSED"
        gate_reason_code = "BLOCKED_BY_SQL_SAFETY_MUTATION"
    elif runtime_decision == "BLOCK" and tool_type == "OPENCLAW":
        gate_result = "CLOSED"
        gate_reason_code = "BLOCKED_OPENCLAW_RUNTIME_ADAPTER_NOT_IMPLEMENTED"
        backend_adapter_required = True
    elif runtime_decision == "BLOCK" and tool_type == "API":
        gate_result = "CLOSED"
        gate_reason_code = "BLOCKED_API_RUNTIME_BACKEND_NOT_IMPLEMENTED"
        backend_adapter_required = True
    elif runtime_decision == "BLOCK" and tool_type == "UNKNOWN":
        gate_result = "CLOSED"
        gate_reason_code = "BLOCKED_UNKNOWN_OR_MALFORMED_TOOL"
    elif runtime_decision == "BLOCK":
        gate_result = "CLOSED"
        gate_reason_code = "FAIL_CLOSED_INVALID_GATE_INPUT"

    return {
        "gate_id": f"gate_{gate_input['gate_input_id']}",
        "gate_input_id": gate_input["gate_input_id"],
        "tool_type": tool_type,
        "runtime_decision": runtime_decision,
        "gate_result": gate_result,
        "gate_reason_code": gate_reason_code,
        "execution_release_allowed": False,
        "sandbox_bridge_required": sandbox_bridge_required,
        "backend_adapter_required": backend_adapter_required,
        "dhms_gate_owner": True,
        "executed": False,
    }


def build_gate_trace(gate_input: dict[str, Any], verdict: dict[str, Any]) -> dict[str, Any]:
    return {
        "gate_trace_id": f"gate_trace_{gate_input['gate_input_id']}",
        "gate_input_id": gate_input["gate_input_id"],
        "gate_id": verdict["gate_id"],
        "dry_run_request_id": gate_input["dry_run_request_id"],
        "request_id": gate_input["request_id"],
        "proposal_id": gate_input["proposal_id"],
        "tool_type": gate_input["tool_type"],
        "runtime_decision": gate_input["runtime_decision"],
        "gate_result": verdict["gate_result"],
        "dry_run_only": True,
        "execution_release_allowed": False,
        "executed": False,
        "tool_executed": False,
        "sql_executed": False,
        "sandbox_executed": False,
        "openclaw_invoked": False,
        "provider_invoked": False,
        "agent_sdk_invoked": False,
        "external_service_sdk_invoked": False,
        "production_runner_invoked": False,
        "http_adapter_invoked": False,
        "external_mutation_detected": False,
        "black_box_validated": True,
        "dhms_gate_owner": True,
    }


def validate_gate_record(record: dict[str, Any]) -> dict[str, Any]:
    failed_checks: list[str] = []
    gate_input = record.get("gate_input", {})
    verdict = record.get("gate_verdict", {})
    trace = record.get("gate_trace", {})

    require_fields("gate_input", gate_input, REQUIRED_GATE_INPUT_FIELDS, failed_checks)
    require_fields("gate_verdict", verdict, REQUIRED_GATE_VERDICT_FIELDS, failed_checks)
    require_fields("gate_trace", trace, REQUIRED_GATE_TRACE_FIELDS, failed_checks)

    runtime_decision = gate_input.get("runtime_decision")
    tool_type = gate_input.get("tool_type")
    gate_result = verdict.get("gate_result")
    gate_reason_code = verdict.get("gate_reason_code")

    if runtime_decision not in ALLOWED_RUNTIME_DECISIONS:
        failed_checks.append("unknown_runtime_decision")
    if gate_result not in ALLOWED_GATE_RESULTS:
        failed_checks.append("unknown_gate_result")
    if gate_result == "OPEN":
        failed_checks.append("gate_open_not_allowed")
    if gate_reason_code not in ALLOWED_GATE_REASON_CODES:
        failed_checks.append("unknown_gate_reason_code")
    if gate_input.get("dhms_final_decision") is not True:
        failed_checks.append("gate_input_not_dhms_final")
    if gate_input.get("black_box_mode") is not True:
        failed_checks.append("gate_input_black_box_not_true")
    if gate_input.get("executed") is not False:
        failed_checks.append("gate_input_executed")
    if verdict.get("execution_release_allowed") is not False:
        failed_checks.append("execution_release_allowed_not_false")
    if verdict.get("dhms_gate_owner") is not True:
        failed_checks.append("dhms_gate_owner_not_true")
    if verdict.get("executed") is not False:
        failed_checks.append("gate_verdict_executed")
    if trace.get("black_box_validated") is not True:
        failed_checks.append("trace_black_box_not_true")
    if trace.get("dhms_gate_owner") is not True:
        failed_checks.append("trace_dhms_gate_owner_not_true")
    if trace.get("gate_result") != gate_result:
        failed_checks.append("trace_gate_result_mismatch")
    if trace.get("runtime_decision") != runtime_decision:
        failed_checks.append("trace_runtime_decision_mismatch")
    if trace.get("tool_type") != tool_type:
        failed_checks.append("trace_tool_type_mismatch")
    for flag in sorted(NON_EXECUTION_TRACE_FLAGS):
        if trace.get(flag) is not False:
            failed_checks.append(f"{flag}_not_false")

    if runtime_decision == "BLOCK" and gate_result != "CLOSED":
        failed_checks.append("block_decision_not_closed")
    if runtime_decision == "SANDBOX":
        if tool_type == "SQL" and gate_result != "HELD_FOR_SANDBOX_BRIDGE":
            failed_checks.append("sql_sandbox_not_held_for_bridge")
        if verdict.get("sandbox_bridge_required") is not True:
            failed_checks.append("sandbox_bridge_required_not_true")
    if tool_type == "SQL" and runtime_decision == "BLOCK":
        if gate_reason_code != "BLOCKED_BY_SQL_SAFETY_MUTATION":
            failed_checks.append("sql_mutation_reason_mismatch")
    if tool_type == "SQL" and runtime_decision == "SANDBOX":
        if gate_reason_code != "HELD_SQL_SELECT_REQUIRES_SANDBOX_BRIDGE":
            failed_checks.append("sql_select_reason_mismatch")
    if tool_type == "OPENCLAW":
        if gate_reason_code != "BLOCKED_OPENCLAW_RUNTIME_ADAPTER_NOT_IMPLEMENTED":
            failed_checks.append("openclaw_reason_mismatch")
        if verdict.get("backend_adapter_required") is not True:
            failed_checks.append("openclaw_backend_adapter_required_not_true")
    if tool_type == "API":
        if gate_reason_code != "BLOCKED_API_RUNTIME_BACKEND_NOT_IMPLEMENTED":
            failed_checks.append("api_reason_mismatch")
        if verdict.get("backend_adapter_required") is not True:
            failed_checks.append("api_backend_adapter_required_not_true")
    if tool_type == "UNKNOWN":
        if gate_reason_code != "BLOCKED_UNKNOWN_OR_MALFORMED_TOOL":
            failed_checks.append("unknown_reason_mismatch")

    return {
        "gate_input_id": gate_input.get("gate_input_id"),
        "tool_type": tool_type,
        "runtime_decision": runtime_decision,
        "gate_result": gate_result,
        "gate_reason_code": gate_reason_code,
        "execution_release_allowed": verdict.get("execution_release_allowed"),
        "executed": trace.get("executed"),
        "passed": not failed_checks,
        "failed_checks": failed_checks,
    }


def require_fields(prefix: str, payload: dict[str, Any], required_fields: set[str], failed_checks: list[str]) -> None:
    missing = sorted(required_fields.difference(payload))
    for field in missing:
        failed_checks.append(f"{prefix}.missing_{field}")
