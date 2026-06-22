#!/usr/bin/env python3
"""Run SQL safety SELECT-only SQLite execution stub validation."""

from __future__ import annotations

import json

from sql_safety_select_only_sqlite_execution_stub import run_sql_safety_select_only_sqlite_execution_stub


def main() -> int:
    result = run_sql_safety_select_only_sqlite_execution_stub()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
