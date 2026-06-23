#!/usr/bin/env python3
"""Run DHMS-AgentFuse-Bench SQL v0."""

from __future__ import annotations

import json

from dhms_agentfuse_bench_sql_v0 import run_dhms_agentfuse_bench_sql_v0


def main() -> int:
    result = run_dhms_agentfuse_bench_sql_v0()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
