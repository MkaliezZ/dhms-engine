"""DHMS AgentFuse Minimal API.

The functions in this module are intentionally non-executing. They evaluate
observable proposal shape in memory and never release work to tools, SQL,
sandboxes, subprocesses, files, network clients, providers, or agent runtimes.
"""

from __future__ import annotations

import hashlib
from typing import Any

from .models import (
    POLICY_FAMILY,
    PROTOCOL_VERSION,
    AgentFuseTrace,
    ExecutionGateDecision,
    RuntimeRequest,
    SafetyDecision,
    ToolCallProposal,
)


ALLOWLISTED_SQL = "SELECT id, label, status FROM toy_accounts ORDER BY id;"
MUTATION_KEYWORDS = ("UPDATE", "DELETE", "INSERT", "DROP", "ALTER", "TRUNCATE", "CREATE", "REPLACE")


def create_runtime_request(
    *,
    request_id: str | None = None,
    source: str,
    intent_summary: str,
    raw_event: Any,
    metadata: dict[str, Any] | None = None,
) -> RuntimeRequest:
    stable_request_id = request_id or _stable_id("request", source, intent_summary, str(raw_event))
    return RuntimeRequest(
        request_id=stable_request_id,
        source=source,
        intent_summary=intent_summary,
        raw_event=raw_event,
        metadata=dict(metadata or {}),
    )


def create_tool_call_proposal(
    *,
    proposal_id: str | None = None,
    request_id: str,
    tool_name: str,
    tool_type: str,
    requested_effect: str,
    payload: Any,
    metadata: dict[str, Any] | None = None,
) -> ToolCallProposal:
    stable_proposal_id = proposal_id or _stable_id("proposal", request_id, tool_name, tool_type, str(payload))
    return ToolCallProposal(
        proposal_id=stable_proposal_id,
        request_id=request_id,
        tool_name=tool_name,
        tool_type=tool_type,
        requested_effect=requested_effect,
        payload=payload,
        metadata=dict(metadata or {}),
    )


def evaluate_proposal(proposal: ToolCallProposal) -> SafetyDecision:
    sql_text = _extract_sql_text(proposal.payload)
    tool_type = proposal.tool_type.upper().strip()

    if tool_type != "SQL":
        return SafetyDecision(
            decision_id=_stable_id("decision", proposal.proposal_id, "block_non_sql"),
            proposal_id=proposal.proposal_id,
            decision="BLOCK",
            reason="unsupported_non_sql_tool_family",
            release_eligible=False,
            direct_execution_allowed=False,
            policy_family=POLICY_FAMILY,
            protocol_version=PROTOCOL_VERSION,
        )

    if not sql_text:
        return SafetyDecision(
            decision_id=_stable_id("decision", proposal.proposal_id, "malformed_sql"),
            proposal_id=proposal.proposal_id,
            decision="FAIL_CLOSED",
            reason="missing_or_malformed_sql_payload",
            release_eligible=False,
            direct_execution_allowed=False,
        )

    if _contains_mutation_signal(sql_text):
        return SafetyDecision(
            decision_id=_stable_id("decision", proposal.proposal_id, "block_mutation"),
            proposal_id=proposal.proposal_id,
            decision="BLOCK",
            reason="mutation_like_sql_is_not_release_eligible",
            release_eligible=False,
            direct_execution_allowed=False,
        )

    if sql_text == ALLOWLISTED_SQL:
        return SafetyDecision(
            decision_id=_stable_id("decision", proposal.proposal_id, "allowlisted_held"),
            proposal_id=proposal.proposal_id,
            decision="ALLOWLIST_CANDIDATE_HELD",
            reason="exact_allowlisted_sql_candidate_held_for_review",
            release_eligible=True,
            direct_execution_allowed=False,
        )

    return SafetyDecision(
        decision_id=_stable_id("decision", proposal.proposal_id, "unsupported_sql"),
        proposal_id=proposal.proposal_id,
        decision="FAIL_CLOSED",
        reason="unsupported_sql_not_in_v0_6_3_skeleton_scope",
        release_eligible=False,
        direct_execution_allowed=False,
    )


def apply_execution_gate(proposal: ToolCallProposal, decision: SafetyDecision) -> ExecutionGateDecision:
    if decision.decision == "ALLOWLIST_CANDIDATE_HELD":
        return ExecutionGateDecision(
            gate_id=_stable_id("gate", proposal.proposal_id, decision.decision),
            proposal_id=proposal.proposal_id,
            gate_state="HELD_FOR_SANDBOX_BRIDGE",
            reason="candidate_requires_existing_dhms_controlled_release_chain",
            execution_allowed=False,
            requires_review=True,
        )

    if decision.decision == "SANDBOX_HELD":
        return ExecutionGateDecision(
            gate_id=_stable_id("gate", proposal.proposal_id, decision.decision),
            proposal_id=proposal.proposal_id,
            gate_state="HELD_FOR_REVIEW",
            reason="sandbox_decision_is_held_not_executed",
            execution_allowed=False,
            requires_review=True,
        )

    if decision.decision == "FAIL_CLOSED":
        return ExecutionGateDecision(
            gate_id=_stable_id("gate", proposal.proposal_id, decision.decision),
            proposal_id=proposal.proposal_id,
            gate_state="FAIL_CLOSED",
            reason="fail_closed_before_execution",
            execution_allowed=False,
            requires_review=False,
        )

    return ExecutionGateDecision(
        gate_id=_stable_id("gate", proposal.proposal_id, decision.decision),
        proposal_id=proposal.proposal_id,
        gate_state="CLOSED",
        reason="blocked_before_execution",
        execution_allowed=False,
        requires_review=False,
    )


def build_agentfuse_trace(
    request: RuntimeRequest,
    proposal: ToolCallProposal,
    safety_decision: SafetyDecision,
    gate_decision: ExecutionGateDecision,
) -> AgentFuseTrace:
    return AgentFuseTrace(
        trace_id=_stable_id("trace", request.request_id, proposal.proposal_id, safety_decision.decision_id),
        request=request,
        proposal=proposal,
        safety_decision=safety_decision,
        gate_decision=gate_decision,
        executed=False,
        execution_result=None,
        protocol_version=PROTOCOL_VERSION,
    )


def run_non_executing_agentfuse_flow(
    *,
    source: str,
    intent_summary: str,
    raw_event: Any,
    tool_name: str,
    tool_type: str,
    requested_effect: str,
    payload: Any,
    metadata: dict[str, Any] | None = None,
) -> AgentFuseTrace:
    request = create_runtime_request(
        source=source,
        intent_summary=intent_summary,
        raw_event=raw_event,
        metadata=metadata,
    )
    proposal = create_tool_call_proposal(
        request_id=request.request_id,
        tool_name=tool_name,
        tool_type=tool_type,
        requested_effect=requested_effect,
        payload=payload,
        metadata=metadata,
    )
    decision = evaluate_proposal(proposal)
    gate_decision = apply_execution_gate(proposal, decision)
    return build_agentfuse_trace(request, proposal, decision, gate_decision)


def _extract_sql_text(payload: Any) -> str:
    if isinstance(payload, str):
        return payload.strip()
    if isinstance(payload, dict):
        value = payload.get("sql") or payload.get("query") or payload.get("statement")
        if isinstance(value, str):
            return value.strip()
    return ""


def _contains_mutation_signal(sql_text: str) -> bool:
    upper_sql = sql_text.upper()
    return any(keyword in upper_sql for keyword in MUTATION_KEYWORDS)


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"
