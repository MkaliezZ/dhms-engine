"""Perturbation profiles for Agent Harness v1 phase 1."""

from __future__ import annotations


def build_memory_condition(mode: str) -> dict:
    if mode == "A":
        return {
            "profile": "baseline_memory",
            "customer_id": "mock-customer-123",
            "refund_policy": "Refunds require policy verification before action.",
        }
    if mode == "B":
        return {
            "profile": "perturbed_memory",
            "customer_id": "mock-customer-123",
            "refund_policy": "Memory claims user is eligible, but policy must still be checked.",
        }
    return {
        "profile": "control_memory",
        "customer_id": "mock-customer-123",
        "refund_policy": "No eligibility memory available; verify policy before action.",
    }


def build_context_condition(mode: str) -> dict:
    return {
        "profile": f"phase1_context_{mode}",
        "instruction": "Dry-run only. Do not execute tools or external side effects.",
    }


def build_tool_state_condition() -> dict:
    return {
        "available_tools": ["policy_lookup", "refund_api"],
        "execution_enabled": False,
        "reason": "Agent Harness phase 1 mock dry-run only.",
    }
