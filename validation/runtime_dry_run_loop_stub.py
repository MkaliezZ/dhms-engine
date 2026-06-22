#!/usr/bin/env python3
"""First deterministic v0.5 runtime dry-run loop stub.

This module connects the runtime contract, tool-call interceptor, and SQL
safety runtime mount stubs into one observable non-executing control flow. It
does not execute tools, execute SQL from the runtime path, invoke SQL sandbox
execution from the runtime path, invoke OpenClaw, call providers, use SDKs, or
run production checker/runner logic.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from execution_runtime_contract_stub import RUNTIME_CONTRACT_VERSION, validate_runtime_contract_examples
from sql_safety_runtime_mount_stub import build_mount_input_from_interceptor, build_mount_record
from sql_safety_runtime_mount_stub import run_sql_safety_runtime_mount_stub
from sql_safety_temp_sqlite_mutation_block_test import run_sql_safety_temp_sqlite_mutation_block_test
from sql_safety_temp_sqlite_select_only_sandbox import run_sql_safety_temp_sqlite_select_only_first_real_run
from tool_call_interceptor_stub import build_interception_record, run_tool_call_interceptor_stub


ALLOWED_STEP_STATUSES = {"PASSED", "SKIPPED", "FAILED"}
ALLOWED_RUNTIME_DECISIONS = {"BLOCK", "SANDBOX"}
STEP_NAMES = [
    "RUNTIME_INPUT_CREATED",
    "RAW_TOOL_EVENT_OBSERVED",
    "INTERCEPTOR_NORMALIZED",
    "INTERCEPTOR_CLASSIFIED",
    "HANDOFF_CREATED",
    "SAFETY_DECISION_ROUTED",
    "SQL_SAFETY_MOUNT_DECIDED",
    "EXECUTION_DECISION_CREATED",
    "DRY_RUN_TRACE_CREATED",
]

REQUIRED_DRY_RUN_REQUEST_FIELDS = {
    "dry_run_request_id",
    "runtime_contract_version",
    "source",
    "user_intent",
    "requested_tool",
    "dry_run_only",
    "black_box_mode",
}

REQUIRED_STEP_RECORD_FIELDS = {
    "step_id",
    "dry_run_request_id",
    "step_name",
    "step_status",
    "input_observed",
    "output_produced",
    "executed",
    "failed_checks",
}

REQUIRED_RUNTIME_DECISION_FIELDS = {
    "runtime_decision_id",
    "dry_run_request_id",
    "proposal_id",
    "tool_type",
    "decision",
    "reason_code",
    "dhms_final_decision",
    "sandbox_required",
    "sandbox_planned",
    "execution_allowed",
    "executed",
}

REQUIRED_FINAL_TRACE_FIELDS = {
    "runtime_trace_id",
    "dry_run_request_id",
    "request_id",
    "proposal_id",
    "tool_type",
    "decision",
    "dry_run_only",
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
    "dhms_final_decision",
}

NON_EXECUTION_TRACE_FLAGS = {
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


def run_runtime_dry_run_loop_stub() -> dict[str, Any]:
    contract_preflight = validate_runtime_contract_examples()
    interceptor_preflight = run_tool_call_interceptor_stub()
    sql_mount_preflight = run_sql_safety_runtime_mount_stub()
    select_only_preflight = run_sql_safety_temp_sqlite_select_only_first_real_run()
    mutation_block_preflight = run_sql_safety_temp_sqlite_mutation_block_test()

    scenarios = build_runtime_dry_run_scenarios()
    records = [build_runtime_dry_run_record(scenario) for scenario in scenarios]
    record_results = [validate_runtime_dry_run_record(record) for record in records]

    failed_checks = [
        f"{result['dry_run_request_id']}.{check}"
        for result in record_results
        for check in result["failed_checks"]
    ]
    for name, result in [
        ("contract_preflight_failed", contract_preflight),
        ("interceptor_preflight_failed", interceptor_preflight),
        ("sql_mount_preflight_failed", sql_mount_preflight),
        ("select_only_preflight_failed", select_only_preflight),
        ("mutation_block_preflight_failed", mutation_block_preflight),
    ]:
        if result.get("status") != "PASS":
            failed_checks.append(name)

    decisions_by_tool_type = dict(
        sorted(Counter(f"{result['tool_type']}:{result['decision']}" for result in record_results).items())
    )
    blocked_count = sum(1 for result in record_results if result["decision"] == "BLOCK")
    sandbox_count = sum(1 for result in record_results if result["decision"] == "SANDBOX")
    executed_count = sum(1 for record in records if record["final_trace"]["executed"])
    sql_executed_count = sum(1 for record in records if record["final_trace"]["sql_executed"])
    openclaw_invoked_count = sum(1 for record in records if record["final_trace"]["openclaw_invoked"])
    passed_runtime_requests = sum(1 for result in record_results if result["passed"])
    status = "PASS" if not failed_checks and passed_runtime_requests == len(records) else "FAIL"

    return {
        "validation": "runtime_dry_run_loop_stub_v0_5_5",
        "status": status,
        "contract_preflight_passed": contract_preflight.get("status") == "PASS",
        "interceptor_preflight_passed": interceptor_preflight.get("status") == "PASS",
        "sql_mount_preflight_passed": sql_mount_preflight.get("status") == "PASS",
        "select_only_preflight_passed": select_only_preflight.get("status") == "PASS",
        "mutation_block_preflight_passed": mutation_block_preflight.get("status") == "PASS",
        "total_runtime_requests": len(records),
        "passed_runtime_requests": passed_runtime_requests,
        "decisions_by_tool_type": decisions_by_tool_type,
        "blocked_count": blocked_count,
        "sandbox_count": sandbox_count,
        "executed_count": executed_count,
        "sql_executed_count": sql_executed_count,
        "openclaw_invoked_count": openclaw_invoked_count,
        "failed_checks": failed_checks,
        "runtime_records": records,
        "record_results": record_results,
        "runtime_wrapper_executed": False,
        "tool_execution_invoked": False,
        "sql_execution_invoked_from_runtime_path": False,
        "sqlite_database_created_from_runtime_path": False,
        "sql_sandbox_execution_invoked_from_runtime_path": False,
        "openclaw_invoked": False,
        "deepseek_invoked": False,
        "provider_sdk_invoked": False,
        "agent_sdk_invoked": False,
        "http_adapter_invoked": False,
        "production_checker_invoked": False,
        "production_runner_invoked": False,
        "full_suite_validation_invoked": False,
        "final_verdict": (
            "READY_FOR_V0_5_6_RUNTIME_EXECUTION_GATE_STUB"
            if status == "PASS"
            else "NEEDS_RUNTIME_DRY_RUN_LOOP_STUB_FIX"
        ),
    }


def build_runtime_dry_run_scenarios() -> list[dict[str, Any]]:
    return [
        build_scenario(
            dry_run_request_id="dry_run_sql_mutation",
            request_id="req_dry_run_sql_mutation",
            user_intent="Attempt a SQL UPDATE against toy account state.",
            requested_tool="sql",
            raw_event_id="raw_dry_run_sql_mutation",
            raw_tool_name="execute_sql",
            raw_tool_args={"sql": "UPDATE toy_accounts SET status = 'deleted' WHERE id = 1;"},
            raw_tool_text="Run UPDATE toy_accounts SET status = 'deleted' WHERE id = 1;",
        ),
        build_scenario(
            dry_run_request_id="dry_run_sql_select_only",
            request_id="req_dry_run_sql_select_only",
            user_intent="Inspect toy account rows with a SELECT-only query.",
            requested_tool="sql",
            raw_event_id="raw_dry_run_sql_select_only",
            raw_tool_name="sql_query",
            raw_tool_args={"sql": "SELECT id, label, status FROM toy_accounts ORDER BY id;"},
            raw_tool_text="Read toy account rows with SELECT id, label, status FROM toy_accounts ORDER BY id;",
        ),
        build_scenario(
            dry_run_request_id="dry_run_openclaw_runtime",
            request_id="req_dry_run_openclaw_runtime",
            user_intent="Attempt to invoke OpenClaw as a runtime backend.",
            requested_tool="openclaw",
            raw_event_id="raw_dry_run_openclaw_runtime",
            raw_tool_name="openclaw_agent",
            raw_tool_args={"mode": "runtime_candidate", "profile": "dhms-pilot"},
            raw_tool_text="Run OpenClaw through the future runtime backend.",
        ),
        build_scenario(
            dry_run_request_id="dry_run_future_api",
            request_id="req_dry_run_future_api",
            user_intent="Attempt to invoke a future account mutation API.",
            requested_tool="api",
            raw_event_id="raw_dry_run_future_api",
            raw_tool_name="api_call",
            raw_tool_args={"method": "POST", "path": "/accounts/account_abc/refund"},
            raw_tool_text="Call a future API endpoint that may mutate account state.",
        ),
        build_scenario(
            dry_run_request_id="dry_run_unknown_malformed",
            request_id="req_dry_run_unknown_malformed",
            user_intent="Submit malformed tool request.",
            requested_tool="unknown",
            raw_event_id="raw_dry_run_unknown_malformed",
            raw_tool_name="",
            raw_tool_args={},
            raw_tool_text="",
        ),
    ]


def build_scenario(
    *,
    dry_run_request_id: str,
    request_id: str,
    user_intent: str,
    requested_tool: str,
    raw_event_id: str,
    raw_tool_name: str,
    raw_tool_args: dict[str, Any],
    raw_tool_text: str,
) -> dict[str, Any]:
    return {
        "dry_run_request": {
            "dry_run_request_id": dry_run_request_id,
            "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
            "source": "runtime_dry_run_loop_stub",
            "user_intent": user_intent,
            "requested_tool": requested_tool,
            "dry_run_only": True,
            "black_box_mode": True,
        },
        "raw_event": {
            "raw_event_id": raw_event_id,
            "request_id": request_id,
            "source": "runtime_dry_run_loop_stub",
            "raw_tool_name": raw_tool_name,
            "raw_tool_args": raw_tool_args,
            "raw_tool_text": raw_tool_text,
            "observed": True,
        },
    }


def build_runtime_dry_run_record(scenario: dict[str, Any]) -> dict[str, Any]:
    dry_run_request = scenario["dry_run_request"]
    raw_event = scenario["raw_event"]
    interception_record = build_interception_record(raw_event)
    proposal = interception_record["normalized_proposal"]
    classification = interception_record["classification"]
    handoff = interception_record["handoff"]

    sql_mount_record = None
    if proposal["tool_type"] == "SQL" and handoff["handoff_target"] == "RUNTIME_CONTRACT_SAFETY_DECISION":
        sql_mount_record = build_mount_record(build_mount_input_from_interceptor(interception_record))

    runtime_decision = build_runtime_decision(dry_run_request, proposal, classification, handoff, sql_mount_record)
    final_trace = build_final_trace(dry_run_request, raw_event, proposal, runtime_decision)
    steps = build_step_records(dry_run_request, raw_event, interception_record, sql_mount_record, runtime_decision, final_trace)

    return {
        "dry_run_request": dry_run_request,
        "raw_event": raw_event,
        "interception_record": interception_record,
        "sql_mount_record": sql_mount_record,
        "runtime_decision": runtime_decision,
        "final_trace": final_trace,
        "step_records": steps,
    }


def build_runtime_decision(
    dry_run_request: dict[str, Any],
    proposal: dict[str, Any],
    classification: dict[str, Any],
    handoff: dict[str, Any],
    sql_mount_record: dict[str, Any] | None,
) -> dict[str, Any]:
    if handoff["handoff_status"] == "BLOCKED_BEFORE_SAFETY_DECISION":
        decision = "BLOCK"
        reason_code = "interceptor_blocked_malformed_or_unknown_tool"
        sandbox_required = False
        sandbox_planned = False
    elif sql_mount_record is not None:
        sql_decision = sql_mount_record["sql_decision"]
        decision = sql_decision["decision"]
        reason_code = sql_decision["reason_code"]
        sandbox_required = sql_decision["sandbox_required"]
        sandbox_planned = decision == "SANDBOX"
    elif proposal["tool_type"] == "OPENCLAW":
        decision = "BLOCK"
        reason_code = "openclaw_runtime_adapter_not_implemented"
        sandbox_required = False
        sandbox_planned = False
    elif proposal["tool_type"] in {"API", "FILE", "SYSTEM"}:
        decision = "BLOCK"
        reason_code = f"{proposal['tool_type'].lower()}_runtime_adapter_not_implemented"
        sandbox_required = False
        sandbox_planned = False
    else:
        decision = "BLOCK"
        reason_code = "unsupported_tool_type_blocked"
        sandbox_required = False
        sandbox_planned = False

    return {
        "runtime_decision_id": f"runtime_decision_{dry_run_request['dry_run_request_id']}",
        "dry_run_request_id": dry_run_request["dry_run_request_id"],
        "proposal_id": proposal["proposal_id"],
        "tool_type": proposal["tool_type"],
        "decision": decision,
        "reason_code": reason_code,
        "dhms_final_decision": True,
        "sandbox_required": sandbox_required,
        "sandbox_planned": sandbox_planned,
        "execution_allowed": False,
        "executed": False,
        "interceptor_risk_class": classification["risk_class"],
    }


def build_final_trace(
    dry_run_request: dict[str, Any],
    raw_event: dict[str, Any],
    proposal: dict[str, Any],
    runtime_decision: dict[str, Any],
) -> dict[str, Any]:
    return {
        "runtime_trace_id": f"runtime_trace_{dry_run_request['dry_run_request_id']}",
        "dry_run_request_id": dry_run_request["dry_run_request_id"],
        "request_id": raw_event["request_id"],
        "proposal_id": proposal["proposal_id"],
        "tool_type": proposal["tool_type"],
        "decision": runtime_decision["decision"],
        "dry_run_only": True,
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
        "dhms_final_decision": True,
    }


def build_step_records(
    dry_run_request: dict[str, Any],
    raw_event: dict[str, Any],
    interception_record: dict[str, Any],
    sql_mount_record: dict[str, Any] | None,
    runtime_decision: dict[str, Any],
    final_trace: dict[str, Any],
) -> list[dict[str, Any]]:
    proposal = interception_record["normalized_proposal"]
    classification = interception_record["classification"]
    handoff = interception_record["handoff"]
    values = {
        "RUNTIME_INPUT_CREATED": (True, True, "PASSED"),
        "RAW_TOOL_EVENT_OBSERVED": (raw_event.get("observed") is True, True, "PASSED"),
        "INTERCEPTOR_NORMALIZED": (proposal.get("proposal_observed") is True, True, "PASSED"),
        "INTERCEPTOR_CLASSIFIED": (bool(classification.get("risk_class")), True, "PASSED"),
        "HANDOFF_CREATED": (handoff.get("dhms_control_plane") is True, True, "PASSED"),
        "SAFETY_DECISION_ROUTED": (True, True, "PASSED"),
        "SQL_SAFETY_MOUNT_DECIDED": (
            proposal.get("tool_type") == "SQL",
            sql_mount_record is not None,
            "PASSED" if sql_mount_record is not None else "SKIPPED",
        ),
        "EXECUTION_DECISION_CREATED": (True, bool(runtime_decision), "PASSED"),
        "DRY_RUN_TRACE_CREATED": (True, bool(final_trace), "PASSED"),
    }
    return [
        {
            "step_id": f"{dry_run_request['dry_run_request_id']}.{step_name.lower()}",
            "dry_run_request_id": dry_run_request["dry_run_request_id"],
            "step_name": step_name,
            "step_status": status,
            "input_observed": input_observed,
            "output_produced": output_produced,
            "executed": False,
            "failed_checks": [],
        }
        for step_name, (input_observed, output_produced, status) in values.items()
    ]


def validate_runtime_dry_run_record(record: dict[str, Any]) -> dict[str, Any]:
    failed_checks: list[str] = []
    dry_run_request = record.get("dry_run_request", {})
    raw_event = record.get("raw_event", {})
    interception_record = record.get("interception_record", {})
    proposal = interception_record.get("normalized_proposal", {})
    classification = interception_record.get("classification", {})
    handoff = interception_record.get("handoff", {})
    sql_mount_record = record.get("sql_mount_record")
    runtime_decision = record.get("runtime_decision", {})
    final_trace = record.get("final_trace", {})
    step_records = record.get("step_records", [])

    require_fields("dry_run_request", dry_run_request, REQUIRED_DRY_RUN_REQUEST_FIELDS, failed_checks)
    require_fields("runtime_decision", runtime_decision, REQUIRED_RUNTIME_DECISION_FIELDS, failed_checks)
    require_fields("final_trace", final_trace, REQUIRED_FINAL_TRACE_FIELDS, failed_checks)
    for index, step_record in enumerate(step_records):
        require_fields(f"step_record[{index}]", step_record, REQUIRED_STEP_RECORD_FIELDS, failed_checks)
        if step_record.get("step_name") not in STEP_NAMES:
            failed_checks.append(f"step_record[{index}].unknown_step_name")
        if step_record.get("step_status") not in ALLOWED_STEP_STATUSES:
            failed_checks.append(f"step_record[{index}].unknown_step_status")
        if step_record.get("executed") is not False:
            failed_checks.append(f"step_record[{index}].executed_not_false")
        if step_record.get("failed_checks") != []:
            failed_checks.append(f"step_record[{index}].failed_checks_not_empty")

    observed_step_names = [step.get("step_name") for step in step_records]
    if observed_step_names != STEP_NAMES:
        failed_checks.append("step_names_not_exact_order")
    if dry_run_request.get("dry_run_only") is not True:
        failed_checks.append("dry_run_only_not_true")
    if dry_run_request.get("black_box_mode") is not True:
        failed_checks.append("black_box_mode_not_true")
    if runtime_decision.get("decision") not in ALLOWED_RUNTIME_DECISIONS:
        failed_checks.append("unknown_runtime_decision")
    if runtime_decision.get("decision") == "ALLOW":
        failed_checks.append("allow_decision_not_permitted_in_dry_run")
    if runtime_decision.get("dhms_final_decision") is not True:
        failed_checks.append("runtime_decision_not_dhms_final")
    if runtime_decision.get("execution_allowed") is not False:
        failed_checks.append("execution_allowed_not_false")
    if runtime_decision.get("executed") is not False:
        failed_checks.append("runtime_decision_executed")
    if final_trace.get("dhms_final_decision") is not True:
        failed_checks.append("trace_not_dhms_final")
    if final_trace.get("black_box_validated") is not True:
        failed_checks.append("black_box_validated_not_true")
    if final_trace.get("decision") != runtime_decision.get("decision"):
        failed_checks.append("trace_decision_mismatch")
    if final_trace.get("tool_type") != runtime_decision.get("tool_type"):
        failed_checks.append("trace_tool_type_mismatch")
    for flag in sorted(NON_EXECUTION_TRACE_FLAGS):
        if final_trace.get(flag) is not False:
            failed_checks.append(f"{flag}_not_false")

    tool_type = proposal.get("tool_type")
    risk_class = classification.get("risk_class")
    decision = runtime_decision.get("decision")
    if raw_event.get("observed") is not True:
        failed_checks.append("raw_event_not_observed")
    if proposal.get("tool_executed") is not False:
        failed_checks.append("proposal_tool_executed")
    if handoff.get("tool_executed") is not False:
        failed_checks.append("handoff_tool_executed")
    if handoff.get("dhms_control_plane") is not True:
        failed_checks.append("handoff_not_dhms_control_plane")
    if tool_type == "SQL":
        if sql_mount_record is None:
            failed_checks.append("sql_without_mount_record")
        elif sql_mount_record["runtime_trace"].get("sandbox_executed") is not False:
            failed_checks.append("sql_mount_sandbox_executed")
        sql_text = str(proposal.get("tool_args", {}).get("sql", "")).strip().lower()
        if sql_text.startswith(("update", "delete", "insert", "drop", "alter", "replace", "truncate", "create")):
            if risk_class != "CRITICAL":
                failed_checks.append("sql_mutation_risk_not_critical")
            if decision != "BLOCK":
                failed_checks.append("sql_mutation_not_blocked")
        elif sql_text.startswith("select"):
            if risk_class != "MEDIUM":
                failed_checks.append("sql_select_risk_not_medium")
            if decision != "SANDBOX":
                failed_checks.append("sql_select_not_sandbox")
            if runtime_decision.get("sandbox_required") is not True:
                failed_checks.append("sql_select_sandbox_required_not_true")
            if runtime_decision.get("sandbox_planned") is not True:
                failed_checks.append("sql_select_sandbox_planned_not_true")
    elif tool_type == "OPENCLAW":
        if risk_class != "HIGH":
            failed_checks.append("openclaw_risk_not_high")
        if decision != "BLOCK":
            failed_checks.append("openclaw_not_blocked")
        if runtime_decision.get("reason_code") != "openclaw_runtime_adapter_not_implemented":
            failed_checks.append("openclaw_reason_mismatch")
    elif tool_type in {"API", "FILE", "SYSTEM"}:
        if risk_class != "HIGH":
            failed_checks.append("external_tool_risk_not_high")
        if decision != "BLOCK":
            failed_checks.append("external_tool_not_blocked")
    elif tool_type == "UNKNOWN":
        if handoff.get("handoff_status") != "BLOCKED_BEFORE_SAFETY_DECISION":
            failed_checks.append("unknown_not_blocked_before_safety")
        if decision != "BLOCK":
            failed_checks.append("unknown_not_blocked")

    return {
        "dry_run_request_id": dry_run_request.get("dry_run_request_id"),
        "tool_type": tool_type,
        "risk_class": risk_class,
        "decision": decision,
        "sandbox_required": runtime_decision.get("sandbox_required"),
        "sandbox_planned": runtime_decision.get("sandbox_planned"),
        "executed": final_trace.get("executed"),
        "passed": not failed_checks,
        "failed_checks": failed_checks,
    }


def require_fields(prefix: str, payload: dict[str, Any], required_fields: set[str], failed_checks: list[str]) -> None:
    missing = sorted(required_fields.difference(payload))
    for field in missing:
        failed_checks.append(f"{prefix}.missing_{field}")
