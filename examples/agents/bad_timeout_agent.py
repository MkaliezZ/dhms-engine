#!/usr/bin/env python3
"""Deliberately slow sample for command adapter timeout conformance demos."""

from __future__ import annotations

import sys
import time


def main() -> int:
    _ = sys.stdin.read()
    time.sleep(5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
