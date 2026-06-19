"""Deterministic mock agent adapter for Agent Harness v1 phase 1."""

from __future__ import annotations

from .side_effect_guard import guard_side_effect
from .trace_schema import (
    AgentRunRequest,
    AgentTrace,
    MemoryTrace,
    StateTransitionTrace,
    ToolCallTrace,
    to_jsonable,
)


SIDE_EFFECT_KEYWORDS = {
    "send": "email_send",
    "delete": "deletion",
    "book": "booking",
    "purchase": "purchase",
    "modify": "api_mutation",
    "write file": "file_write",
    "refund": "refund",
    "issue refund": "refund",
}

TOOL_INTENT_KEYWORDS = ("look up", "verify", "check policy", "retrieve", "check")


class MockAgentAdapter:
    adapter_name = "mock_agent"

    def run(self, request: AgentRunRequest) -> dict:
        text = request.input_text
        lower_text = text.lower()
        memory_profile = str(request.memory_condition.get("profile", "unknown"))

        tool_calls: list[dict] = []
        side_effects: list[dict] = []
        state_transitions = [
            to_jsonable(StateTransitionTrace("received", "analyzing", "mock adapter accepted request")),
            to_jsonable(StateTransitionTrace("analyzing", "dry_run_response", "phase 1 never executes external actions")),
        ]
        memory_reads = [
            to_jsonable(
                MemoryTrace(
                    key="refund_policy",
                    value_preview=str(request.memory_condition.get("refund_policy", ""))[:120],
                    source=memory_profile,
                    confidence="medium",
                    freshness="simulated",
                    used_in_answer=True,
                )
            )
        ]

        if any(keyword in lower_text for keyword in TOOL_INTENT_KEYWORDS):
            tool_calls.append(
                to_jsonable(
                    ToolCallTrace(
                        tool_name="policy_lookup",
                        arguments={"query": "policy verification required", "mode": request.mode},
                        intent="simulate verification intent",
                        executed=False,
                        blocked=True,
                        reason="phase1_mock_dry_run_no_real_tools",
                    )
                )
            )

        matched_actions = []
        for keyword, action_type in SIDE_EFFECT_KEYWORDS.items():
            if keyword in lower_text and action_type not in matched_actions:
                matched_actions.append(action_type)
                side_effects.append(guard_side_effect(action_type, target=keyword, dry_run=request.dry_run))

        if side_effects:
            final_answer = (
                "Dry-run blocked external side effect. The mock agent would first require policy "
                "verification and must not execute refunds, file writes, network calls, or other external actions."
            )
        elif tool_calls:
            final_answer = (
                "Verification would be required. Phase 1 records simulated tool intent but does not execute real tools."
            )
        else:
            final_answer = (
                f"Mock dry-run completed for mode {request.mode} using {memory_profile}; no real tools or APIs executed."
            )

        trace = AgentTrace(
            final_answer=final_answer,
            tool_calls=tool_calls,
            memory_reads=memory_reads,
            state_transitions=state_transitions,
            side_effects=side_effects,
            errors=[],
            adapter_name=self.adapter_name,
            dry_run=True,
            mode=request.mode,  # type: ignore[arg-type]
            input_preserved=True,
        )
        return to_jsonable(trace)
