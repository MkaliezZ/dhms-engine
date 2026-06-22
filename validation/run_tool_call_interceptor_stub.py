#!/usr/bin/env python3
"""Run the v0.5.2 tool-call interceptor stub validation."""

from __future__ import annotations

import json

from tool_call_interceptor_stub import run_tool_call_interceptor_stub


def main() -> int:
    result = run_tool_call_interceptor_stub()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
