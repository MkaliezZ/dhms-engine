#!/usr/bin/env python3
"""Run SQL safety temp SQLite SELECT-only authorization gate."""

from __future__ import annotations

import json

from sql_safety_temp_sqlite_select_only_authorization_gate import (
    run_sql_safety_temp_sqlite_select_only_authorization_gate,
)


def main() -> int:
    result = run_sql_safety_temp_sqlite_select_only_authorization_gate()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
