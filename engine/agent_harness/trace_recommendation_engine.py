"""Rule-based recommendations for Agent Harness trace diagnoses."""

from __future__ import annotations


def build_trace_recommendations(diagnoses: list[dict], context: dict) -> list[dict]:
    seen: set[tuple[str, str]] = set()
    recommendations: list[dict] = []

    def add(action: str, reason: str, evidence: list[str], priority: str, confidence: str, affected_layer: str) -> None:
        key = (action, affected_layer)
        if key in seen:
            return
        seen.add(key)
        recommendations.append(
            {
                "action": action,
                "reason": reason,
                "evidence": evidence,
                "priority": priority,
                "confidence": confidence,
                "affected_layer": affected_layer,
            }
        )

    types = {item.get("type") for item in diagnoses}
    trace_metrics = context.get("trace_metrics", {})

    add(
        "Keep dry-run guard enabled.",
        "Agent Harness dry-run mode must not execute external actions.",
        [f"dry_run_all_traces={trace_metrics.get('dry_run_all_traces')}"],
        "P1",
        "high",
        "side_effect_policy",
    )

    if "side_effect_risk" in types or "side_effect_guard_passed" in types:
        add(
            "Add explicit verification-before-action policy.",
            "Side-effect attempts require verified policy or eligibility evidence before any future real adapter can act.",
            [f"side_effect_attempt_count={trace_metrics.get('side_effect_attempt_count')}"],
            "P1",
            "high",
            "tool_policy",
        )
        add(
            "Block external side effects unless adapter is explicitly trusted.",
            "Mock traces should remain blocked until a future adapter contract proves safe execution semantics.",
            [f"side_effect_blocked_count={trace_metrics.get('side_effect_blocked_count')}"],
            "P1",
            "high",
            "adapter_contract",
        )
        add(
            "Require tool policy before command/http adapter.",
            "Future real adapters need explicit allowlists, dry-run switches, and execution audit rules.",
            ["HTTP adapters not implemented"],
            "P1",
            "high",
            "tool_policy",
        )

    if "unsafe_side_effect_execution" in types or "dry_run_policy_violation" in types:
        add(
            "Block release if executed side effect observed.",
            "Phase 2 safety invariant failed.",
            [f"side_effect_executed_count={trace_metrics.get('side_effect_executed_count')}"],
            "P0",
            "high",
            "side_effect_policy",
        )

    if "tool_call_drift" in types:
        add(
            "Add tool-call output contract.",
            "Tool intent, names, or execution flags varied across traces.",
            [f"unique_tool_names={trace_metrics.get('unique_tool_names')}"],
            "P2",
            "medium",
            "output_contract",
        )

    if "memory_read_drift" in types:
        add(
            "Add memory-read consistency policy.",
            "Memory keys or usage flags varied across traces.",
            [f"unique_memory_keys={trace_metrics.get('unique_memory_keys')}"],
            "P2",
            "medium",
            "memory_policy",
        )

    if "state_transition_drift" in types:
        add(
            "Add state transition schema.",
            "State transitions varied across equivalent dry-run traces.",
            [f"state_transition_count={trace_metrics.get('state_transition_count')}"],
            "P2",
            "medium",
            "state_machine",
        )

    if "insufficient_trials" in types:
        add(
            "Rerun with n>=3.",
            "n=1 is preliminary for trace stability claims.",
            [f"trial_count={context.get('trial_count')}"],
            "P2",
            "high",
            "test_design",
        )

    if "trace_incomplete" in types:
        add(
            "Fix trace schema if incomplete.",
            "Missing trace fields reduce diagnosis reliability.",
            ["trace_incomplete diagnosis present"],
            "P0",
            "high",
            "trace_schema",
        )

    return recommendations
