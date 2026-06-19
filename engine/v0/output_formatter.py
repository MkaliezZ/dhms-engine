"""JSON-only output formatting for DHMS Minimal Engine v0."""

import json
from typing import Mapping, Any


def format_output(result: Mapping[str, Any]) -> str:
    return json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)

