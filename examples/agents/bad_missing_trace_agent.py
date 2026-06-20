#!/usr/bin/env python3
"""Deliberately missing trace sample for command adapter conformance demos."""

from __future__ import annotations

import json
import sys


PROTOCOL_VERSION = "dhms-agent-command-v1"


def main() -> int:
    _ = sys.stdin.read()
    print(json.dumps({"protocol_version": PROTOCOL_VERSION, "message": "trace intentionally omitted"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
