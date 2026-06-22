#!/usr/bin/env python3
"""Run the v0.4.1H SQL safety minimal checker adapter."""

from __future__ import annotations

import json

from sql_safety_minimal_checker_adapter import run_sql_safety_minimal_checker_adapter


def main() -> int:
    result = run_sql_safety_minimal_checker_adapter()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
