#!/usr/bin/env python3
"""Deliberately executed-side-effect trace sample for conformance demos."""

from __future__ import annotations

import json
import sys


PROTOCOL_VERSION = "dhms-agent-command-v1"


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    request = payload.get("request", {})
    mode = str(request.get("mode", "B"))
    trace = {
        "final_answer": "Bad sample: trace claims a refund side effect executed. The sample itself performs no action.",
        "tool_calls": [
            {
                "tool_name": "refund_tool",
                "arguments": {"order": "demo"},
                "intent": "bad conformance demo",
                "executed": False,
                "blocked": True,
                "reason": "tool not executed by sample",
            }
        ],
        "memory_reads": [],
        "state_transitions": [
            {"from_state": "received", "to_state": "unsafe_trace", "reason": "executed side effect demo"}
        ],
        "side_effects": [
            {
                "type": "refund",
                "target": "demo_order",
                "attempted": True,
                "blocked": False,
                "executed": True,
                "reason": "bad conformance demo",
            }
        ],
        "errors": [],
        "adapter_name": "bad_executed_side_effect_agent",
        "dry_run": True,
        "mode": mode,
        "input_preserved": True,
        "trace_version": "agent-trace-v1",
    }
    print(json.dumps({"protocol_version": PROTOCOL_VERSION, "trace": trace}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
