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

    if "command_adapter_invalid_json" in types:
        add(
            "Ensure the local agent writes exactly one valid JSON object to stdout.",
            "The command adapter could not parse stdout as JSON.",
            ["command_adapter_invalid_json diagnosis present"],
            "P1",
            "high",
            "adapter_contract",
        )

    if "command_adapter_wrong_protocol" in types:
        add(
            'Use protocol_version="dhms-agent-command-v1".',
            "The local agent returned the wrong command protocol version.",
            ["command_adapter_wrong_protocol diagnosis present"],
            "P1",
            "high",
            "adapter_contract",
        )

    if "command_adapter_timeout" in types:
        add(
            "Increase timeout only after confirming the agent is not hanging; keep timeout enforced.",
            "The command adapter process timed out.",
            ["command_adapter_timeout diagnosis present"],
            "P1",
            "high",
            "adapter_contract",
        )

    if "command_adapter_trace_validation_error" in types:
        add(
            "Return a complete AgentTrace with required fields.",
            "The command adapter returned a trace that failed validation.",
            ["command_adapter_trace_validation_error diagnosis present"],
            "P1",
            "high",
            "trace_schema",
        )

    if "command_adapter_nonzero_exit" in types:
        add(
            "Fix local agent process errors before using it in suite runs.",
            "The command adapter process exited with a nonzero status.",
            ["command_adapter_nonzero_exit diagnosis present"],
            "P1",
            "high",
            "adapter_contract",
        )

    if "command_adapter_failure" in types:
        add(
            "Fix the local command adapter failure before suite runs.",
            "The command adapter failed at the local process or protocol boundary.",
            ["command_adapter_failure diagnosis present"],
            "P1",
            "high",
            "adapter_contract",
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
