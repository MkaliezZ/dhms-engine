"""Agent command protocol helpers for DHMS Agent Harness v1 phase 3."""

from __future__ import annotations

import re
from typing import Any

from .trace_schema import AgentRunRequest, to_jsonable


DHMS_AGENT_PROTOCOL_VERSION = "dhms-agent-command-v1"
STDERR_PREVIEW_LIMIT = 1200
SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"\b[A-Z0-9_]*(?:API_KEY|SECRET|TOKEN|PASSWORD)\s*=\s*[^\s\"'`]+", re.IGNORECASE),
    re.compile(r"BEGIN PRIVATE KEY"),
)


def build_protocol_request(request: AgentRunRequest) -> dict[str, Any]:
    return {
        "protocol_version": DHMS_AGENT_PROTOCOL_VERSION,
        "request": to_jsonable(request),
    }


def safe_command_display(command: str) -> str:
    redacted_markers = ("api_key", "token", "secret", "password")
    parts = []
    for part in command.split():
        lower = part.lower()
        if any(marker in lower for marker in redacted_markers):
            parts.append("[REDACTED]")
        else:
            parts.append(part)
    return " ".join(parts)


def stderr_preview(stderr: str) -> str:
    return output_preview(stderr)


def stdout_preview(stdout: str) -> str:
    return output_preview(stdout)


def output_preview(text: str) -> str:
    preview = redact_sensitive(str(text).strip())
    if len(preview) <= STDERR_PREVIEW_LIMIT:
        return preview
    return preview[:STDERR_PREVIEW_LIMIT] + "...[truncated]"


def redact_sensitive(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("<REDACTED>", redacted)
    return redacted


def error_trace(
    message: str,
    *,
    adapter_name: str = "command_agent",
    mode: str = "B",
    command_metadata: dict[str, Any] | None = None,
    command_failure_type: str | None = None,
    command_failure_reason: str | None = None,
    command_failure_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    failure_reason = command_failure_reason or message
    failure_evidence = command_failure_evidence or {"error": message}
    trace = {
        "final_answer": "Command adapter returned an error trace; no external side effects were executed by DHMS.",
        "tool_calls": [],
        "memory_reads": [],
        "state_transitions": [
            {
                "from_state": "command_adapter_started",
                "to_state": "error_trace",
                "reason": message,
            }
        ],
        "side_effects": [],
        "errors": [message],
        "adapter_name": adapter_name,
        "dry_run": True,
        "mode": mode,
        "input_preserved": True,
        "trace_version": "agent-trace-v1-error",
    }
    if command_failure_type:
        trace["command_failure_type"] = command_failure_type
        trace["command_failure_reason"] = failure_reason
        trace["command_failure_evidence"] = failure_evidence
    if command_metadata:
        if command_failure_type:
            command_metadata = dict(command_metadata)
            command_metadata["command_failure_type"] = command_failure_type
            command_metadata["command_failure_reason"] = failure_reason
            command_metadata["command_failure_evidence"] = failure_evidence
        trace["_command_metadata"] = command_metadata
    return trace
