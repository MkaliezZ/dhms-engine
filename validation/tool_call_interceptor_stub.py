#!/usr/bin/env python3
"""Deterministic tool-call interceptor stub for v0.5.2.

The interceptor observes raw tool-call proposals, normalizes them, classifies
tool type and risk signals, and hands normalized proposals to the runtime
contract safety-decision layer. It never executes tools.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from execution_runtime_contract_stub import validate_runtime_contract_examples


ALLOWED_TOOL_TYPES = {"SQL", "OPENCLAW", "API", "FILE", "SYSTEM", "UNKNOWN"}
ALLOWED_NORMALIZATION_STATUSES = {"NORMALIZED", "MALFORMED_BLOCKED", "UNKNOWN_TOOL_BLOCKED"}
ALLOWED_RISK_CLASSES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
ALLOWED_HANDOFF_TARGETS = {
    "RUNTIME_CONTRACT_SAFETY_DECISION",
    "INTERCEPTOR_BLOCKED_MALFORMED",
    "INTERCEPTOR_BLOCKED_UNKNOWN_TOOL",
}
ALLOWED_HANDOFF_STATUSES = {"HANDED_OFF", "BLOCKED_BEFORE_SAFETY_DECISION"}

REQUIRED_RAW_EVENT_FIELDS = {
    "raw_event_id",
    "request_id",
    "source",
    "raw_tool_name",
    "raw_tool_args",
    "raw_tool_text",
    "observed",
}

REQUIRED_NORMALIZED_PROPOSAL_FIELDS = {
    "proposal_id",
    "request_id",
    "raw_event_id",
    "tool_type",
    "tool_name",
    "tool_args",
    "normalization_status",
    "proposal_observed",
    "tool_executed",
}

REQUIRED_CLASSIFICATION_FIELDS = {
    "classification_id",
    "proposal_id",
    "tool_type",
    "risk_class",
    "risk_signals",
    "requires_safety_decision",
    "requires_sandbox_review",
    "mutation_risk",
    "external_effect_risk",
    "malformed_request",
}

REQUIRED_HANDOFF_FIELDS = {
    "handoff_id",
    "proposal_id",
    "classification_id",
    "handoff_target",
    "handoff_status",
    "dhms_control_plane",
    "final_decision_made",
    "tool_executed",
}

REQUIRED_TRACE_FIELDS = {
    "interception_trace_id",
    "request_id",
    "raw_event_id",
    "proposal_id",
    "classification_id",
    "handoff_id",
    "tool_type",
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
    "tool_executed",
    "provider_invoked",
    "agent_sdk_invoked",
    "external_service_sdk_invoked",
    "production_runner_invoked",
    "http_adapter_invoked",
    "external_mutation_detected",
}

SQL_MUTATION_KEYWORDS = ("update", "delete", "insert", "drop", "alter", "replace", "truncate")


def run_tool_call_interceptor_stub() -> dict[str, Any]:
    contract_preflight = validate_runtime_contract_examples()
    raw_events = build_raw_tool_call_events()
    records = [build_interception_record(raw_event) for raw_event in raw_events]
    record_results = [validate_interception_record(record) for record in records]

    failed_checks = [
        f"{result['raw_event_id']}.{check}"
        for result in record_results
        for check in result["failed_checks"]
    ]
    if contract_preflight.get("status") != "PASS":
        failed_checks.append("contract_preflight_failed")

    classifications_by_tool_type = dict(sorted(Counter(result["tool_type"] for result in record_results).items()))
    classifications_by_risk_class = dict(sorted(Counter(result["risk_class"] for result in record_results).items()))
    handoffs_to_safety_decision = sum(
        1
        for record in records
        if record["handoff"]["handoff_target"] == "RUNTIME_CONTRACT_SAFETY_DECISION"
    )
    interceptor_blocked_count = sum(
        1
        for record in records
        if record["handoff"]["handoff_status"] == "BLOCKED_BEFORE_SAFETY_DECISION"
    )
    executed_count = sum(1 for record in records if record["interception_trace"]["tool_executed"])
    passed_records = sum(1 for result in record_results if result["passed"])
    status = "PASS" if not failed_checks and passed_records == len(records) else "FAIL"

    return {
        "validation": "tool_call_interceptor_stub_v0_5_2",
        "status": status,
        "contract_preflight_passed": contract_preflight.get("status") == "PASS",
        "total_raw_events": len(raw_events),
        "normalized_proposals": len(records),
        "passed_records": passed_records,
        "classifications_by_tool_type": classifications_by_tool_type,
        "classifications_by_risk_class": classifications_by_risk_class,
        "handoffs_to_safety_decision": handoffs_to_safety_decision,
        "interceptor_blocked_count": interceptor_blocked_count,
        "executed_count": executed_count,
        "failed_checks": failed_checks,
        "raw_events": raw_events,
        "interception_records": records,
        "record_results": record_results,
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
            "READY_FOR_V0_5_3_SQL_SAFETY_MODULE_MOUNTED_INTO_RUNTIME_STUB"
            if status == "PASS"
            else "NEEDS_TOOL_CALL_INTERCEPTOR_STUB_FIX"
        ),
    }


def build_raw_tool_call_events() -> list[dict[str, Any]]:
    return [
        {
            "raw_event_id": "raw_sql_mutation_update",
            "request_id": "req_sql_mutation_update",
            "source": "interceptor_stub",
            "raw_tool_name": "execute_sql",
            "raw_tool_args": {"sql": "UPDATE toy_accounts SET status = 'deleted' WHERE id = 1;"},
            "raw_tool_text": "Please run UPDATE toy_accounts SET status = 'deleted' WHERE id = 1;",
            "observed": True,
        },
        {
            "raw_event_id": "raw_sql_select_only",
            "request_id": "req_sql_select_only",
            "source": "interceptor_stub",
            "raw_tool_name": "sql_query",
            "raw_tool_args": {"sql": "SELECT id, label, status FROM toy_accounts ORDER BY id;"},
            "raw_tool_text": "Read toy account rows with a SELECT-only query.",
            "observed": True,
        },
        {
            "raw_event_id": "raw_openclaw_runtime",
            "request_id": "req_openclaw_runtime",
            "source": "interceptor_stub",
            "raw_tool_name": "openclaw_agent",
            "raw_tool_args": {"mode": "runtime_candidate", "profile": "dhms-pilot"},
            "raw_tool_text": "Run OpenClaw as a runtime tool backend.",
            "observed": True,
        },
        {
            "raw_event_id": "raw_future_api",
            "request_id": "req_future_api",
            "source": "interceptor_stub",
            "raw_tool_name": "api_call",
            "raw_tool_args": {"method": "POST", "path": "/accounts/account_abc/refund"},
            "raw_tool_text": "Call a future API endpoint that may mutate account state.",
            "observed": True,
        },
        {
            "raw_event_id": "raw_file_write",
            "request_id": "req_file_write",
            "source": "interceptor_stub",
            "raw_tool_name": "file_write",
            "raw_tool_args": {"path": "/tmp/dhms-interceptor-stub.txt", "content": "stub"},
            "raw_tool_text": "Write a local file through a future FILE tool.",
            "observed": True,
        },
        {
            "raw_event_id": "raw_unknown_malformed",
            "request_id": "req_unknown_malformed",
            "source": "interceptor_stub",
            "raw_tool_name": "",
            "raw_tool_args": {},
            "raw_tool_text": "",
            "observed": True,
        },
    ]


def build_interception_record(raw_event: dict[str, Any]) -> dict[str, Any]:
    proposal = normalize_raw_event(raw_event)
    classification = classify_proposal(proposal)
    handoff = build_handoff(proposal, classification)
    trace = build_trace(raw_event, proposal, classification, handoff)
    return {
        "raw_event": raw_event,
        "normalized_proposal": proposal,
        "classification": classification,
        "handoff": handoff,
        "interception_trace": trace,
    }


def normalize_raw_event(raw_event: dict[str, Any]) -> dict[str, Any]:
    raw_tool_name = str(raw_event.get("raw_tool_name", "")).strip()
    raw_tool_text = str(raw_event.get("raw_tool_text", "")).strip()
    raw_tool_args = raw_event.get("raw_tool_args", {})
    tool_type = infer_tool_type(raw_tool_name, raw_tool_text, raw_tool_args)
    malformed = not raw_tool_name or not raw_tool_text
    if malformed:
        normalization_status = "MALFORMED_BLOCKED"
    elif tool_type == "UNKNOWN":
        normalization_status = "UNKNOWN_TOOL_BLOCKED"
    else:
        normalization_status = "NORMALIZED"
    return {
        "proposal_id": f"proposal_{raw_event['raw_event_id']}",
        "request_id": raw_event["request_id"],
        "raw_event_id": raw_event["raw_event_id"],
        "tool_type": tool_type,
        "tool_name": raw_tool_name or "unknown_tool",
        "tool_args": raw_tool_args,
        "normalization_status": normalization_status,
        "proposal_observed": True,
        "tool_executed": False,
    }


def infer_tool_type(raw_tool_name: str, raw_tool_text: str, raw_tool_args: dict[str, Any]) -> str:
    combined = " ".join([raw_tool_name, raw_tool_text, " ".join(str(value) for value in raw_tool_args.values())]).lower()
    if "sql" in combined or "select " in combined or any(keyword in combined for keyword in SQL_MUTATION_KEYWORDS):
        return "SQL"
    if "openclaw" in combined:
        return "OPENCLAW"
    if "api" in combined or "endpoint" in combined or "post" in combined:
        return "API"
    if "file" in combined or "write" in combined or "delete file" in combined:
        return "FILE"
    if "system" in combined or "shell" in combined:
        return "SYSTEM"
    return "UNKNOWN"


def classify_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    tool_type = proposal["tool_type"]
    sql_text = str(proposal.get("tool_args", {}).get("sql", "")).strip().lower()
    malformed = proposal["normalization_status"] == "MALFORMED_BLOCKED"
    unknown = proposal["normalization_status"] == "UNKNOWN_TOOL_BLOCKED"
    mutation_risk = tool_type == "SQL" and any(sql_text.startswith(keyword) for keyword in SQL_MUTATION_KEYWORDS)
    select_only = tool_type == "SQL" and sql_text.startswith("select") and not mutation_risk
    external_effect_risk = tool_type in {"OPENCLAW", "API", "FILE", "SYSTEM"} or mutation_risk

    if malformed or unknown:
        risk_class = "HIGH"
        risk_signals = ["malformed_or_unknown_tool"]
    elif mutation_risk:
        risk_class = "CRITICAL"
        risk_signals = ["sql_mutation_intent", "external_mutation_risk"]
    elif select_only:
        risk_class = "MEDIUM"
        risk_signals = ["sql_select_only", "sandbox_review_required"]
    elif tool_type == "OPENCLAW":
        risk_class = "HIGH"
        risk_signals = ["openclaw_runtime_candidate", "external_effect_risk"]
    elif tool_type in {"API", "FILE", "SYSTEM"}:
        risk_class = "HIGH"
        risk_signals = [f"{tool_type.lower()}_tool_candidate", "external_effect_risk"]
    else:
        risk_class = "LOW"
        risk_signals = ["no_mutation_signal_detected"]

    return {
        "classification_id": f"classification_{proposal['proposal_id']}",
        "proposal_id": proposal["proposal_id"],
        "tool_type": tool_type,
        "risk_class": risk_class,
        "risk_signals": risk_signals,
        "requires_safety_decision": not (malformed or unknown),
        "requires_sandbox_review": select_only,
        "mutation_risk": mutation_risk,
        "external_effect_risk": external_effect_risk,
        "malformed_request": malformed,
    }


def build_handoff(proposal: dict[str, Any], classification: dict[str, Any]) -> dict[str, Any]:
    if proposal["normalization_status"] == "MALFORMED_BLOCKED":
        handoff_target = "INTERCEPTOR_BLOCKED_MALFORMED"
        handoff_status = "BLOCKED_BEFORE_SAFETY_DECISION"
    elif proposal["normalization_status"] == "UNKNOWN_TOOL_BLOCKED":
        handoff_target = "INTERCEPTOR_BLOCKED_UNKNOWN_TOOL"
        handoff_status = "BLOCKED_BEFORE_SAFETY_DECISION"
    else:
        handoff_target = "RUNTIME_CONTRACT_SAFETY_DECISION"
        handoff_status = "HANDED_OFF"
    return {
        "handoff_id": f"handoff_{proposal['proposal_id']}",
        "proposal_id": proposal["proposal_id"],
        "classification_id": classification["classification_id"],
        "handoff_target": handoff_target,
        "handoff_status": handoff_status,
        "dhms_control_plane": True,
        "final_decision_made": False,
        "tool_executed": False,
    }


def build_trace(
    raw_event: dict[str, Any],
    proposal: dict[str, Any],
    classification: dict[str, Any],
    handoff: dict[str, Any],
) -> dict[str, Any]:
    return {
        "interception_trace_id": f"trace_{raw_event['raw_event_id']}",
        "request_id": raw_event["request_id"],
        "raw_event_id": raw_event["raw_event_id"],
        "proposal_id": proposal["proposal_id"],
        "classification_id": classification["classification_id"],
        "handoff_id": handoff["handoff_id"],
        "tool_type": proposal["tool_type"],
        "tool_executed": False,
        "provider_invoked": False,
        "agent_sdk_invoked": False,
        "external_service_sdk_invoked": False,
        "production_runner_invoked": False,
        "http_adapter_invoked": False,
        "external_mutation_detected": False,
        "black_box_validated": True,
    }


def validate_interception_record(record: dict[str, Any]) -> dict[str, Any]:
    failed_checks: list[str] = []
    raw_event = record.get("raw_event", {})
    proposal = record.get("normalized_proposal", {})
    classification = record.get("classification", {})
    handoff = record.get("handoff", {})
    trace = record.get("interception_trace", {})

    require_fields("raw_event", raw_event, REQUIRED_RAW_EVENT_FIELDS, failed_checks)
    require_fields("normalized_proposal", proposal, REQUIRED_NORMALIZED_PROPOSAL_FIELDS, failed_checks)
    require_fields("classification", classification, REQUIRED_CLASSIFICATION_FIELDS, failed_checks)
    require_fields("handoff", handoff, REQUIRED_HANDOFF_FIELDS, failed_checks)
    require_fields("interception_trace", trace, REQUIRED_TRACE_FIELDS, failed_checks)

    if raw_event.get("observed") is not True:
        failed_checks.append("raw_event_not_observed")
    if proposal.get("proposal_observed") is not True:
        failed_checks.append("proposal_not_observed")
    if proposal.get("tool_executed") is not False:
        failed_checks.append("proposal_tool_executed")
    if proposal.get("tool_type") not in ALLOWED_TOOL_TYPES:
        failed_checks.append("unknown_tool_type_enum")
    if proposal.get("normalization_status") not in ALLOWED_NORMALIZATION_STATUSES:
        failed_checks.append("unknown_normalization_status")
    if classification.get("tool_type") not in ALLOWED_TOOL_TYPES:
        failed_checks.append("classification_unknown_tool_type")
    if classification.get("risk_class") not in ALLOWED_RISK_CLASSES:
        failed_checks.append("unknown_risk_class")
    if classification.get("requires_safety_decision") is not True and handoff.get("handoff_status") == "HANDED_OFF":
        failed_checks.append("handoff_without_safety_decision_requirement")
    if handoff.get("handoff_target") not in ALLOWED_HANDOFF_TARGETS:
        failed_checks.append("unknown_handoff_target")
    if handoff.get("handoff_status") not in ALLOWED_HANDOFF_STATUSES:
        failed_checks.append("unknown_handoff_status")
    if handoff.get("dhms_control_plane") is not True:
        failed_checks.append("dhms_control_plane_not_true")
    if handoff.get("final_decision_made") is not False:
        failed_checks.append("final_decision_made_in_interceptor")
    if handoff.get("tool_executed") is not False:
        failed_checks.append("handoff_tool_executed")
    for flag in sorted(NON_EXECUTION_TRACE_FLAGS):
        if trace.get(flag) is not False:
            failed_checks.append(f"{flag}_not_false")
    if trace.get("black_box_validated") is not True:
        failed_checks.append("black_box_validated_not_true")
    if trace.get("tool_type") != proposal.get("tool_type"):
        failed_checks.append("trace_tool_type_mismatch")

    malformed_or_unknown = proposal.get("normalization_status") in {"MALFORMED_BLOCKED", "UNKNOWN_TOOL_BLOCKED"}
    if malformed_or_unknown:
        if handoff.get("handoff_status") != "BLOCKED_BEFORE_SAFETY_DECISION":
            failed_checks.append("malformed_unknown_not_blocked_before_safety_decision")
        if handoff.get("handoff_target") == "RUNTIME_CONTRACT_SAFETY_DECISION":
            failed_checks.append("malformed_unknown_handed_to_safety_decision")
    else:
        if handoff.get("handoff_target") != "RUNTIME_CONTRACT_SAFETY_DECISION":
            failed_checks.append("normal_proposal_not_handed_to_safety_decision")
        if handoff.get("handoff_status") != "HANDED_OFF":
            failed_checks.append("normal_proposal_not_handed_off")

    return {
        "raw_event_id": raw_event.get("raw_event_id"),
        "proposal_id": proposal.get("proposal_id"),
        "tool_type": proposal.get("tool_type"),
        "risk_class": classification.get("risk_class"),
        "handoff_target": handoff.get("handoff_target"),
        "handoff_status": handoff.get("handoff_status"),
        "passed": not failed_checks,
        "failed_checks": failed_checks,
    }


def require_fields(prefix: str, payload: dict[str, Any], required_fields: set[str], failed_checks: list[str]) -> None:
    missing = sorted(required_fields.difference(payload))
    for field in missing:
        failed_checks.append(f"{prefix}.missing_{field}")
