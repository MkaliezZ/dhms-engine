#!/usr/bin/env python3
"""Run the v0.5.17 SQL sandbox runtime execution policy freeze stub."""

from __future__ import annotations

import json

from runtime_execution_policy_freeze_stub import run_runtime_execution_policy_freeze_stub


def main() -> int:
    result = run_runtime_execution_policy_freeze_stub()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
