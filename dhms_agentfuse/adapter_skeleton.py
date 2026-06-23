"""DHMS AgentFuse Adapter Skeleton.

This is a non-executing adapter skeleton. It demonstrates integration shape
only. It does not execute tools or connect to real agent runtimes.
"""

from __future__ import annotations

from typing import Any

from .api import (
    apply_execution_gate,
    build_agentfuse_trace,
    create_runtime_request,
    create_tool_call_proposal,
    evaluate_proposal,
)
from .models import AgentFuseTrace, ExecutionGateDecision, RuntimeRequest, SafetyDecision, ToolCallProposal


class AgentFuseAdapterSkeleton:
    """Non-executing reference adapter shape for DHMS AgentFuse.

    This skeleton captures an event, builds a proposal, evaluates policy,
    applies a closed or held gate, and builds a trace. It performs no network,
    file, shell, SQL, provider, OpenClaw, DeepSeek, MCP, or agent-runtime work.
    """

    def capture_event(self, raw_event: Any) -> RuntimeRequest:
        return create_runtime_request(
            source="dhms_agentfuse_adapter_skeleton",
            intent_summary="captured_runtime_event_for_non_executing_review",
            raw_event=raw_event,
            metadata={"adapter_skeleton": True},
        )

    def build_proposal(
        self,
        runtime_request: RuntimeRequest,
        tool_name: str,
        tool_type: str,
        requested_effect: str,
        payload: Any,
    ) -> ToolCallProposal:
        return create_tool_call_proposal(
            request_id=runtime_request.request_id,
            tool_name=tool_name,
            tool_type=tool_type,
            requested_effect=requested_effect,
            payload=payload,
            metadata={"adapter_skeleton": True},
        )

    def evaluate(self, proposal: ToolCallProposal) -> SafetyDecision:
        return evaluate_proposal(proposal)

    def gate(self, proposal: ToolCallProposal, decision: SafetyDecision) -> ExecutionGateDecision:
        return apply_execution_gate(proposal, decision)

    def trace(
        self,
        request: RuntimeRequest,
        proposal: ToolCallProposal,
        decision: SafetyDecision,
        gate_decision: ExecutionGateDecision,
    ) -> AgentFuseTrace:
        return build_agentfuse_trace(request, proposal, decision, gate_decision)
