"""Phase 1 side-effect guard for Agent Harness dry runs."""

from __future__ import annotations

from .trace_schema import SideEffectRecord, to_jsonable


DESTRUCTIVE_ACTIONS = {
    "api_mutation",
    "booking",
    "delete",
    "deletion",
    "email_send",
    "external_action",
    "file_write",
    "network_call",
    "purchase",
    "refund",
    "shell_command",
}


def guard_side_effect(action_type: str, target: str, dry_run: bool = True) -> dict:
    normalized = action_type.strip().lower().replace(" ", "_")
    blocked = dry_run or normalized in DESTRUCTIVE_ACTIONS
    if blocked:
        reason = "phase1_dry_run_blocks_external_side_effects"
    else:
        reason = "phase1_allows_no_real_external_execution"
        blocked = True
    record = SideEffectRecord(
        type=normalized,
        target=target,
        attempted=True,
        blocked=blocked,
        reason=reason,
    )
    return to_jsonable(record)
