"""Identity-chain checks for the historical non-executing AgentFuse API."""

from __future__ import annotations

from dataclasses import replace

import pytest

from dhms_agentfuse import (
    apply_execution_gate,
    build_agentfuse_trace,
    create_runtime_request,
    create_tool_call_proposal,
    evaluate_proposal,
)


def _chain():
    request = create_runtime_request(
        request_id="request-a",
        source="identity-test",
        intent_summary="evaluate one inert SQL proposal",
        raw_event={"kind": "synthetic"},
    )
    proposal = create_tool_call_proposal(
        proposal_id="proposal-a",
        request_id=request.request_id,
        tool_name="sql_tool",
        tool_type="SQL",
        requested_effect="read synthetic rows",
        payload={"sql": "SELECT unsupported FROM synthetic;"},
    )
    decision = evaluate_proposal(proposal)
    gate = apply_execution_gate(proposal, decision)
    return request, proposal, decision, gate


def test_execution_gate_rejects_mismatched_decision_identity() -> None:
    _, proposal, decision, _ = _chain()

    with pytest.raises(ValueError, match="decision proposal_id"):
        apply_execution_gate(proposal, replace(decision, proposal_id="proposal-b"))


@pytest.mark.parametrize(
    "mismatch",
    ["request", "decision", "gate"],
)
def test_trace_rejects_mixed_identity_chain(mismatch: str) -> None:
    request, proposal, decision, gate = _chain()
    if mismatch == "request":
        proposal = replace(proposal, request_id="request-b")
    elif mismatch == "decision":
        decision = replace(decision, proposal_id="proposal-b")
    else:
        gate = replace(gate, proposal_id="proposal-b")

    with pytest.raises(ValueError, match="must match"):
        build_agentfuse_trace(request, proposal, decision, gate)


def test_matching_identity_chain_still_builds_non_executing_trace() -> None:
    request, proposal, decision, gate = _chain()

    trace = build_agentfuse_trace(request, proposal, decision, gate)

    assert trace.executed is False
    assert trace.proposal.proposal_id == trace.safety_decision.proposal_id
    assert trace.proposal.proposal_id == trace.gate_decision.proposal_id
