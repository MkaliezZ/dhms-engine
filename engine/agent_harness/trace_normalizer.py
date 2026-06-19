"""Trace normalization helpers."""

from __future__ import annotations

import json
from typing import Any

from .trace_schema import to_jsonable


def normalize_trace(trace: Any) -> dict:
    data = to_jsonable(trace)
    json.dumps(data, sort_keys=True)
    if not isinstance(data, dict):
        raise TypeError("normalized trace must be a dictionary")
    return data
