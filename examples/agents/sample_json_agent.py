#!/usr/bin/env python3
"""Sample local BYOA agent for DHMS command protocol v1.

This sample reads one JSON request from stdin and writes one JSON response to
stdout. It never calls APIs, writes files, or executes tools.
"""

from __future__ import annotations

import json
import sys


PROTOCOL_VERSION = "dhms-agent-command-v1"


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return write_response(error_trace("invalid request JSON"))
    request = payload.get("request", {})
    input_text = str(request.get("input_text", ""))
    mode = str(request.get("mode", "B"))
    memory = request.get("memory_condition", {})
    trace = {
        "final_answer": (
            "Dry-run only: I would check refund policy and eligibility before any refund. "
            "No refund was issued."
        ),
        "tool_calls": [
            {
                "tool_name": "policy_lookup",
                "arguments": {"query": "refund eligibility", "mode": mode},
                "intent": "check refund policy before action",
                "executed": False,
                "blocked": True,
                "reason": "simulated_dry_run_tool_intent",
            }
        ],
        "memory_reads": [
            {
                "key": "refund_policy",
                "value_preview": str(memory.get("refund_policy", ""))[:120],
                "source": str(memory.get("profile", "command_agent_memory")),
                "confidence": "medium",
                "freshness": "simulated",
                "used_in_answer": True,
            }
        ],
        "state_transitions": [
            {"from_state": "received", "to_state": "checking_policy", "reason": "refund request requires policy check"},
            {"from_state": "checking_policy", "to_state": "dry_run_blocked", "reason": "dry-run blocks refund action"},
        ],
        "side_effects": [
            {
                "type": "refund",
                "target": "customer_refund",
                "attempted": "refund" in input_text.lower(),
                "blocked": True,
                "executed": False,
                "reason": "dry_run_blocks_refund",
            }
        ],
        "errors": [],
        "adapter_name": "sample_json_agent",
        "dry_run": True,
        "mode": mode,
        "input_preserved": True,
        "trace_version": "agent-trace-v1",
    }
    return write_response(trace)


def error_trace(message: str) -> dict:
    return {
        "final_answer": "Sample agent could not process request.",
        "tool_calls": [],
        "memory_reads": [],
        "state_transitions": [],
        "side_effects": [],
        "errors": [message],
        "adapter_name": "sample_json_agent",
        "dry_run": True,
        "mode": "B",
        "input_preserved": False,
        "trace_version": "agent-trace-v1-error",
    }


def write_response(trace: dict) -> int:
    print(json.dumps({"protocol_version": PROTOCOL_VERSION, "trace": trace}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
