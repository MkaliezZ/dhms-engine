#!/usr/bin/env python3
"""Deliberately wrong protocol sample for command adapter conformance demos."""

from __future__ import annotations

import json
import sys


def main() -> int:
    _ = sys.stdin.read()
    print(json.dumps({"protocol_version": "wrong-protocol", "trace": {}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
