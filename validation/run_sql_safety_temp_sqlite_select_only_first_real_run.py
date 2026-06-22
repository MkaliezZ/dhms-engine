#!/usr/bin/env python3
"""Run the SQL safety temp SQLite SELECT-only first real target shot."""

from __future__ import annotations

import json

from sql_safety_temp_sqlite_select_only_sandbox import run_sql_safety_temp_sqlite_select_only_first_real_run


def main() -> int:
    result = run_sql_safety_temp_sqlite_select_only_first_real_run()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
