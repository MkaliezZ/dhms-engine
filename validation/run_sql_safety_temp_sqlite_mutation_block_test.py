#!/usr/bin/env python3
"""Run the SQL safety temp SQLite mutation-block target test."""

from __future__ import annotations

import json

from sql_safety_temp_sqlite_mutation_block_test import run_sql_safety_temp_sqlite_mutation_block_test


def main() -> int:
    result = run_sql_safety_temp_sqlite_mutation_block_test()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
