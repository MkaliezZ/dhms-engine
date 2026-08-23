"""Standard-library client for the AgentFuse HTTP policy service example."""

from __future__ import annotations

import json
from collections.abc import Mapping
from urllib.request import Request, urlopen


def evaluate(
    payload: Mapping[str, object],
    *,
    service_url: str = "http://127.0.0.1:8000/evaluate",
) -> dict[str, object]:
    """Send one digest-only policy request to the local example service."""

    request = Request(
        service_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read())


def main() -> None:
    requests = [
        {
            "tool_call_id": "call-read-001",
            "tool_name": "read_profile",
            "arguments_digest": "sha256-read-example",
            "context": {"source": "example-client"},
        },
        {
            "tool_call_id": "call-delete-001",
            "tool_name": "delete_file",
            "arguments_digest": "sha256-delete-example",
            "context": {"source": "example-client"},
        },
    ]
    for payload in requests:
        print(json.dumps(evaluate(payload), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
