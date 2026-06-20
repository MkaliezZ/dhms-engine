#!/usr/bin/env python3
"""Deliberately unsafe dry_run=false sample for conformance demos."""

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
        "final_answer": "Bad sample: dry_run was set false. No real action was taken by this sample.",
        "tool_calls": [],
        "memory_reads": [],
        "state_transitions": [
            {"from_state": "received", "to_state": "invalid_trace", "reason": "dry_run=false conformance demo"}
        ],
        "side_effects": [],
        "errors": [],
        "adapter_name": "bad_dry_run_false_agent",
        "dry_run": False,
        "mode": mode,
        "input_preserved": True,
        "trace_version": "agent-trace-v1",
    }
    print(json.dumps({"protocol_version": PROTOCOL_VERSION, "trace": trace}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
