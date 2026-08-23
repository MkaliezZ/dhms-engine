"""Focused HTTP contract tests for the AgentFuse policy service prototype."""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from examples.http_policy_service.client import evaluate
from examples.http_policy_service.server import create_server


@contextmanager
def _running_service() -> Iterator[str]:
    server = create_server(port=0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    try:
        yield f"http://{host}:{port}/evaluate"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def _post(url: str, payload: object) -> tuple[int, dict[str, object]]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read())
    except HTTPError as error:
        return error.code, json.loads(error.read())


def _request(tool_call_id: str, tool_name: str) -> dict[str, object]:
    return {
        "tool_call_id": tool_call_id,
        "tool_name": tool_name,
        "arguments_digest": "sha256-synthetic-example",
        "context": {"source": "focused-test"},
    }


def test_allow_request_preserves_identity() -> None:
    with _running_service() as url:
        status, response = _post(url, _request("call-allow-001", "read_profile"))

    assert status == 200
    assert response == {
        "decision": "allow",
        "tool_call_id": "call-allow-001",
    }


def test_block_request_returns_non_execution_status_and_identity() -> None:
    with _running_service() as url:
        status, response = _post(url, _request("call-block-001", "delete_file"))

    assert status == 200
    assert response == {
        "decision": "block",
        "execution_status": "not_executed",
        "tool_call_id": "call-block-001",
    }


def test_example_client_uses_the_http_contract() -> None:
    with _running_service() as url:
        response = evaluate(
            _request("call-client-001", "read_profile"), service_url=url
        )

    assert response == {
        "decision": "allow",
        "tool_call_id": "call-client-001",
    }


def test_response_does_not_copy_digest_or_context_payload() -> None:
    payload = _request("call-safe-001", "transfer_money")
    payload["arguments_digest"] = "sha256-RAW_SENSITIVE_DIGEST_SENTINEL"
    payload["context"] = {"source": "RAW_SENSITIVE_CONTEXT_SENTINEL"}

    with _running_service() as url:
        status, response = _post(url, payload)
    serialized = json.dumps(response, sort_keys=True)

    assert status == 200
    assert "arguments" not in response
    assert "arguments_digest" not in response
    assert "RAW_SENSITIVE_DIGEST_SENTINEL" not in serialized
    assert "RAW_SENSITIVE_CONTEXT_SENTINEL" not in serialized


def test_raw_arguments_are_rejected_without_echoing_payload() -> None:
    payload = _request("call-reject-001", "delete_file")
    payload["arguments"] = {"secret": "RAW_ARGUMENT_SENTINEL"}

    with _running_service() as url:
        status, response = _post(url, payload)
    serialized = json.dumps(response, sort_keys=True)

    assert status == 400
    assert response == {"error": "invalid_request"}
    assert "RAW_ARGUMENT_SENTINEL" not in serialized
