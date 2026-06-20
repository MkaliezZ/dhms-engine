"""Trace diagnosis taxonomy for Agent Harness v1 phase 2."""

from __future__ import annotations


DIAGNOSIS_VERSION = "Agent Harness Trace Diagnosis v1 phase2"


TRACE_DIAGNOSIS_TYPES = {
    "final_answer_drift": "Final answers differ meaningfully across trials or regimes.",
    "tool_call_drift": "Tool intent, tool name, arguments, or verification behavior changes unexpectedly.",
    "memory_read_drift": "Memory keys, freshness, confidence, or used-in-answer flags vary unexpectedly.",
    "state_transition_drift": "Agent state transitions differ across equivalent runs or perturbation modes.",
    "side_effect_risk": "Agent attempted an external side effect.",
    "side_effect_guard_passed": "Side effects were attempted but correctly blocked by dry-run guard.",
    "unsafe_side_effect_execution": "A side effect was marked executed=true in Phase 2.",
    "trace_incomplete": "Required trace fields are missing or malformed.",
    "dry_run_policy_violation": "dry_run is false or trace records real execution in Phase 2.",
    "insufficient_trials": "n is too low for strong trace stability claims.",
    "expected_agent_property_violation": "Agent trace violates the case expected behavior.",
    "mock_agent_only_caveat": "Phase 2 uses deterministic mock agent only; no real agent reliability claim.",
    "command_adapter_failure": "Command adapter failed at the local process or protocol boundary.",
    "command_adapter_invalid_json": "Command adapter stdout was not valid JSON.",
    "command_adapter_wrong_protocol": "Command adapter returned the wrong protocol version.",
    "command_adapter_timeout": "Command adapter process timed out.",
    "command_adapter_nonzero_exit": "Command adapter process exited with a nonzero status.",
    "command_adapter_trace_validation_error": "Command adapter returned an invalid AgentTrace.",
}


SEVERITY_RANK = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}


def make_diagnosis(
    diagnosis_type: str,
    severity: str,
    confidence: str,
    interpretation: str,
    evidence: dict,
    recommended_actions: list[str],
) -> dict:
    return {
        "type": diagnosis_type,
        "meaning": TRACE_DIAGNOSIS_TYPES[diagnosis_type],
        "severity": severity,
        "confidence": confidence,
        "interpretation": interpretation,
        "evidence": evidence,
        "recommended_actions": recommended_actions,
    }
