#!/usr/bin/env python3
"""Controlled agent that returns a structured wrapper-style timeout trace."""

from __future__ import annotations

import json
import sys


PROTOCOL_VERSION = "dhms-agent-command-v1"


def main() -> int:
    payload = json.loads(sys.stdin.read() or "{}")
    request = payload.get("request", {}) if isinstance(payload, dict) else {}
    mode = str(request.get("mode", "B"))
    trace = {
        "final_answer": "Controlled structured timeout; no external side effects were executed by DHMS.",
        "tool_calls": [],
        "memory_reads": [],
        "state_transitions": [
            {"from_state": "intake", "to_state": "wrapper_timeout", "reason": "controlled local timeout fixture"}
        ],
        "side_effects": [],
        "errors": [{"type": "openclaw_timeout", "message": "Controlled timeout fixture returned structured DHMS JSON."}],
        "adapter_name": "structured_timeout_agent",
        "dry_run": True,
        "mode": mode,
        "input_preserved": True,
        "trace_version": "agent-trace-v1",
        "command_failure_type": "timeout",
        "command_failure_reason": "openclaw_timeout",
        "command_failure_evidence": {
            "timeout_source": "wrapper",
            "timeout_seconds": 1,
            "duration_seconds": 1,
            "stdout_preview": "",
            "stderr_preview": "",
        },
    }
    print(json.dumps({"protocol_version": PROTOCOL_VERSION, "trace": trace}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
