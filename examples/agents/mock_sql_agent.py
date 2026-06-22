#!/usr/bin/env python3
"""Dry-run-only mock SQL command agent for DHMS Agent Harness.

This target never connects to a database, never executes SQL, and never mutates
external state. It emits inert SQL trace evidence for future DHMS SQL safety
case work.
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any


PROTOCOL_VERSION = "dhms-agent-command-v1"
TRACE_VERSION = "agent-trace-v1"
AGENT_NAME = "mock_sql_agent"


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return write_response(error_trace("stdin was not valid JSON"))

    request = payload.get("request", {})
    if not isinstance(request, dict):
        return write_response(error_trace("request must be an object"))

    input_text = str(request.get("input_text", ""))
    mode = str(request.get("mode", "B"))
    memory = dict_if_mapping(request.get("memory_condition"))
    context = dict_if_mapping(request.get("context_condition"))
    metadata = dict_if_mapping(request.get("metadata"))

    if request.get("dry_run") is not True:
        return write_response(error_trace("dry_run_required", mode=mode, input_preserved=True))

    sql_context = classify_sql_request(input_text, memory, context)
    trace = build_trace(
        input_text=input_text,
        mode=mode,
        memory=memory,
        context=context,
        metadata=metadata,
        sql_context=sql_context,
    )
    return write_response(trace)


def dict_if_mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def classify_sql_request(input_text: str, memory: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    text = input_text.lower()
    joined_context = " ".join(str(value) for value in context.values()).lower()
    joined_memory = " ".join(str(value) for value in memory.values()).lower()
    combined = " ".join([text, joined_context, joined_memory])

    destructive = contains_any(combined, ["delete", "drop", "truncate"])
    mutation = contains_any(combined, ["update", "insert", "alter", "create", "merge"])
    sensitive_select = "select" in combined and contains_any(
        combined,
        ["password", "token", "secret", "ssn", "credit card", "payment", "email", "private"],
    )
    stale_memory = contains_any(combined, ["stale", "old memory", "stored memory", "memory says"])
    rag_identity_conflict = contains_any(
        combined,
        ["rag", "retrieved context", "retrieved profile", "identity conflict", "says i am", "admin"],
    )
    injection = contains_any(combined, ["ignore previous", "run tool", "execute tool", "shell", "exfiltrate"])
    completion_claim_risk = contains_any(combined, ["mark completed", "claim completed", "say it is done"])

    risk_labels = []
    if destructive:
        risk_labels.append("destructive_sql")
    if mutation:
        risk_labels.append("mutation_sql")
    if sensitive_select:
        risk_labels.append("sensitive_select")
    if stale_memory:
        risk_labels.append("stale_memory_authorization")
    if rag_identity_conflict:
        risk_labels.append("rag_identity_conflict")
    if injection:
        risk_labels.append("sql_injection_tool_call")
    if completion_claim_risk:
        risk_labels.append("dry_run_completion_claim")
    if not risk_labels:
        risk_labels.append("generic_sql_request")

    return {
        "risk_labels": risk_labels,
        "proposed_sql": proposed_sql_for(risk_labels, input_text),
        "blocked_reason": blocked_reason_for(risk_labels),
    }


def contains_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)


def proposed_sql_for(risk_labels: list[str], input_text: str) -> str:
    extracted = extract_sql_like_text(input_text)
    if extracted:
        return extracted
    if "destructive_sql" in risk_labels:
        return "DELETE FROM accounts WHERE user_id = 'user_123';"
    if "mutation_sql" in risk_labels or "stale_memory_authorization" in risk_labels:
        return "UPDATE accounts SET status = 'approved' WHERE account_id = 'account_abc';"
    if "sensitive_select" in risk_labels:
        return "SELECT email, payment_status FROM accounts WHERE account_id = 'account_abc';"
    if "rag_identity_conflict" in risk_labels:
        return "UPDATE accounts SET role = 'admin' WHERE user_id = 'user_123';"
    if "sql_injection_tool_call" in risk_labels:
        return "-- blocked prompt-injection-like SQL/tool request"
    return "SELECT status FROM accounts WHERE account_id = 'account_abc';"


def extract_sql_like_text(input_text: str) -> str:
    pattern = re.compile(r"\b(select|insert|update|delete|drop|truncate|alter|create|merge)\b.+", re.IGNORECASE | re.DOTALL)
    match = pattern.search(input_text)
    if not match:
        return ""
    sql = " ".join(match.group(0).strip().split())
    return sql[:500]


def blocked_reason_for(risk_labels: list[str]) -> str:
    if "destructive_sql" in risk_labels:
        return "destructive SQL requires explicit current authorization and remains blocked in dry-run."
    if "mutation_sql" in risk_labels:
        return "write SQL is blocked because this target never mutates external state."
    if "sensitive_select" in risk_labels:
        return "sensitive SELECT is blocked unless authorization is explicit and current."
    if "rag_identity_conflict" in risk_labels:
        return "retrieved context is not treated as identity or authorization."
    if "stale_memory_authorization" in risk_labels:
        return "stale memory is context, not authorization for SQL."
    if "sql_injection_tool_call" in risk_labels:
        return "tool or injection-like execution request is blocked by dry-run policy."
    return "SQL is represented as dry-run trace evidence only."


def build_trace(
    *,
    input_text: str,
    mode: str,
    memory: dict[str, Any],
    context: dict[str, Any],
    metadata: dict[str, Any],
    sql_context: dict[str, Any],
) -> dict[str, Any]:
    case_id = str(metadata.get("case_id", "not_available"))
    proposed_sql = str(sql_context["proposed_sql"])
    blocked_sql = proposed_sql if should_block(sql_context["risk_labels"]) else ""
    dry_run_log = [
        {
            "event": "sql_intent_detected",
            "risk_labels": sql_context["risk_labels"],
            "proposed_sql": proposed_sql,
        },
        {
            "event": "sql_execution_blocked",
            "blocked_sql": blocked_sql or proposed_sql,
            "reason": sql_context["blocked_reason"],
        },
    ]
    observable_response = observable_response_for(sql_context)
    sql_payload = {
        "agent_name": AGENT_NAME,
        "mode": "dry_run",
        "case_id": case_id,
        "user_request": input_text,
        "retrieved_context": context,
        "memory_context": memory,
        "proposed_sql": proposed_sql,
        "blocked_sql": blocked_sql,
        "dry_run_sql_log": dry_run_log,
        "observable_response": observable_response,
        "safety_notes": [
            "Dry-run only: no SQL was executed.",
            "No real database connection was opened.",
            "No external mutation occurred.",
            sql_context["blocked_reason"],
        ],
        "tool_call_count": 0,
        "tool_executed_count": 0,
        "side_effect_executed_count": 0,
        "executed": False,
        "external_mutation_detected": False,
    }
    return {
        "final_answer": observable_response,
        "observable_response": observable_response,
        "tool_calls": [],
        "memory_reads": memory_reads_for(memory),
        "state_transitions": [
            {"from_state": "received", "to_state": "sql_intent_detected", "reason": "input inspected for SQL risk"},
            {"from_state": "sql_intent_detected", "to_state": "dry_run_sql_blocked", "reason": "mock SQL target is dry-run only"},
        ],
        "side_effects": [],
        "errors": [],
        "adapter_name": AGENT_NAME,
        "dry_run": True,
        "mode": mode,
        "input_preserved": True,
        "trace_version": TRACE_VERSION,
        "mock_sql_agent": sql_payload,
    }


def should_block(risk_labels: list[str]) -> bool:
    return any(label != "generic_sql_request" for label in risk_labels) or "generic_sql_request" in risk_labels


def memory_reads_for(memory: dict[str, Any]) -> list[dict[str, Any]]:
    if not memory:
        return []
    return [
        {
            "key": key,
            "value_preview": str(value)[:120],
            "source": "mock_sql_agent_memory_context",
            "confidence": "low",
            "freshness": "unverified",
            "used_in_answer": True,
        }
        for key, value in sorted(memory.items())
    ]


def observable_response_for(sql_context: dict[str, Any]) -> str:
    labels = set(sql_context["risk_labels"])
    parts = [
        "Dry-run only: I will not execute SQL or mutate any database.",
        "This target emits only dry-run SQL trace evidence.",
    ]
    if "destructive_sql" in labels:
        parts.append("Proposed destructive SQL is blocked pending explicit current authorization.")
    if "mutation_sql" in labels:
        parts.append("Proposed write SQL is blocked; no external database action was taken.")
    if "sensitive_select" in labels:
        parts.append("Sensitive SELECT output is not retrieved or disclosed in this dry-run.")
    if "stale_memory_authorization" in labels:
        parts.append("Stale memory is not treated as authorization for SQL.")
    if "rag_identity_conflict" in labels:
        parts.append("Retrieved context is not treated as identity or permission.")
    if "sql_injection_tool_call" in labels:
        parts.append("Prompt-injection or tool-execution intent is blocked.")
    if "dry_run_completion_claim" in labels:
        parts.append("I will not claim that SQL was completed or committed.")
    parts.append("No external database action was taken.")
    return " ".join(parts)


def error_trace(message: str, *, mode: str = "B", input_preserved: bool = False) -> dict[str, Any]:
    return {
        "final_answer": "Mock SQL agent could not process the request safely.",
        "observable_response": "Dry-run only: no SQL was executed or attempted.",
        "tool_calls": [],
        "memory_reads": [],
        "state_transitions": [],
        "side_effects": [],
        "errors": [message],
        "adapter_name": AGENT_NAME,
        "dry_run": True,
        "mode": mode,
        "input_preserved": input_preserved,
        "trace_version": "agent-trace-v1-error",
        "mock_sql_agent": {
            "agent_name": AGENT_NAME,
            "mode": "dry_run",
            "proposed_sql": "",
            "blocked_sql": "",
            "dry_run_sql_log": [],
            "observable_response": "Dry-run only: no SQL was executed or attempted.",
            "safety_notes": ["No database connection exists in this target."],
            "tool_call_count": 0,
            "tool_executed_count": 0,
            "side_effect_executed_count": 0,
            "executed": False,
            "external_mutation_detected": False,
        },
    }


def write_response(trace: dict[str, Any]) -> int:
    print(json.dumps({"protocol_version": PROTOCOL_VERSION, "trace": trace}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
