"""Experimental stdlib HTTP boundary for AgentFuse policy decisions."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from dhms_agentfuse import RuntimeGuard, ToolCallRequest

ALLOWED_TOOLS = frozenset({"read_profile"})
BLOCKED_TOOLS = frozenset({"delete_file", "transfer_money"})
MAX_REQUEST_BYTES = 64 * 1024

_REQUEST_FIELDS = frozenset(
    {"tool_call_id", "tool_name", "arguments_digest", "context"}
)
_GUARD = RuntimeGuard(
    allow_tools=ALLOWED_TOOLS,
    deny_tools=BLOCKED_TOOLS,
    default_action="block",
)


class InvalidPolicyRequest(ValueError):
    """Raised when a request does not match the bounded example contract."""


def _require_text(payload: Mapping[str, Any], field_name: str) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value:
        raise InvalidPolicyRequest(f"{field_name} must be a non-empty string")
    return value


def evaluate_payload(payload: object) -> dict[str, object]:
    """Evaluate one digest-only request without dispatching a tool handler."""

    if not isinstance(payload, Mapping):
        raise InvalidPolicyRequest("request body must be a JSON object")
    if "arguments" in payload:
        raise InvalidPolicyRequest("raw arguments are not accepted")
    if set(payload) - _REQUEST_FIELDS:
        raise InvalidPolicyRequest("request contains unsupported fields")

    tool_call_id = _require_text(payload, "tool_call_id")
    tool_name = _require_text(payload, "tool_name")
    arguments_digest = _require_text(payload, "arguments_digest")
    context = payload.get("context", {})
    if not isinstance(context, Mapping):
        raise InvalidPolicyRequest("context must be a JSON object")

    tool_call = ToolCallRequest(
        tool_call_id=tool_call_id,
        tool_name=tool_name,
        arguments={},
        safe_metadata={
            "arguments_digest": arguments_digest,
            "context_keys": tuple(sorted(str(key) for key in context)),
        },
    )
    decision = _GUARD.evaluate(tool_call)
    response: dict[str, object] = {
        "tool_call_id": decision.tool_call_id,
        "decision": decision.action,
    }
    if decision.action == "block":
        non_execution = decision.evidence.non_execution
        if non_execution is None:
            raise RuntimeError("blocked decision is missing non-execution evidence")
        response["execution_status"] = non_execution.status
    return response


class PolicyServiceHandler(BaseHTTPRequestHandler):
    """Handle the single experimental POST /evaluate endpoint."""

    server_version = "AgentFusePolicyServicePrototype/0"

    def do_POST(self) -> None:
        if self.path != "/evaluate":
            self._send_json(404, {"error": "not_found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "invalid_request"})
            return
        if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
            self._send_json(400, {"error": "invalid_request"})
            return

        try:
            payload = json.loads(self.rfile.read(content_length))
            response = evaluate_payload(payload)
        except (InvalidPolicyRequest, json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "invalid_request"})
            return
        except RuntimeError:
            self._send_json(500, {"error": "evaluation_failed"})
            return

        self._send_json(200, response)

    def _send_json(self, status: int, payload: Mapping[str, object]) -> None:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def create_server(host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    """Create the local demonstration server without starting its loop."""

    return ThreadingHTTPServer((host, port), PolicyServiceHandler)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    server = create_server(args.host, args.port)
    print(
        f"AgentFuse policy service prototype listening on http://{args.host}:{args.port}"
    )
    print("This is a local experimental example, not a production server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
