#!/usr/bin/env python3
"""Deliberately invalid JSON sample for command adapter conformance demos."""

from __future__ import annotations

import sys


def main() -> int:
    _ = sys.stdin.read()
    print("this is not json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
