"""AgentTrace validation for Agent Harness command adapter."""

from __future__ import annotations

from typing import Any


REQUIRED_TRACE_FIELDS = {
    "final_answer",
    "tool_calls",
    "memory_reads",
    "state_transitions",
    "side_effects",
    "errors",
    "adapter_name",
    "dry_run",
    "mode",
    "input_preserved",
    "trace_version",
}


def validate_agent_trace(trace: dict) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(trace, dict):
        return {"valid": False, "errors": ["trace must be an object"], "warnings": []}

    missing = sorted(REQUIRED_TRACE_FIELDS - set(trace))
    if missing:
        errors.append("missing required trace fields: " + ", ".join(missing))

    for field in ("tool_calls", "memory_reads", "state_transitions", "side_effects", "errors"):
        if field in trace and not isinstance(trace.get(field), list):
            errors.append(f"{field} must be a list")

    if trace.get("dry_run") is not True:
        errors.append("dry_run must be true")

    for index, side_effect in enumerate(trace.get("side_effects") or []):
        if not isinstance(side_effect, dict):
            errors.append(f"side_effects[{index}] must be an object")
            continue
        if side_effect.get("executed") is True:
            errors.append(f"side_effects[{index}].executed must not be true")
        if side_effect.get("attempted") is True and side_effect.get("blocked") is not True:
            warnings.append(f"side_effects[{index}] attempted side effect should be blocked")

    for index, tool_call in enumerate(trace.get("tool_calls") or []):
        if not isinstance(tool_call, dict):
            errors.append(f"tool_calls[{index}] must be an object")
            continue
        if tool_call.get("executed") is True and not (
            tool_call.get("blocked") is True and "simulated" in str(tool_call.get("reason", "")).lower()
        ):
            errors.append(f"tool_calls[{index}].executed must not be true in Phase 3")

    return {"valid": not errors, "errors": errors, "warnings": warnings}
