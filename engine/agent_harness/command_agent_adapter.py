"""Local command adapter for Agent Harness v1 phase 3."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
from typing import Any

from .agent_protocol import DHMS_AGENT_PROTOCOL_VERSION, build_protocol_request, error_trace, safe_command_display, stderr_preview
from .trace_normalizer import normalize_trace
from .trace_schema import AgentRunRequest
from .trace_validator import validate_agent_trace


class CommandAgentAdapter:
    adapter_name = "command_agent"

    def __init__(self, command: str, timeout_seconds: int = 10) -> None:
        self.command = command
        self.timeout_seconds = timeout_seconds
        self.safe_command = safe_command_display(command)

    def run(self, request: AgentRunRequest) -> dict:
        metadata = {
            "agent_command": self.safe_command,
            "timeout_seconds": self.timeout_seconds,
            "protocol_version": DHMS_AGENT_PROTOCOL_VERSION,
            "command_exit_status": None,
            "stderr_preview": "",
        }
        try:
            args = shlex.split(self.command)
        except ValueError as exc:
            return error_trace(f"invalid command: {exc}", mode=request.mode, command_metadata=metadata)
        if not args:
            return error_trace("empty command", mode=request.mode, command_metadata=metadata)

        payload = build_protocol_request(request)
        try:
            completed = subprocess.run(
                args,
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                shell=False,
                env={"PATH": os.environ.get("PATH", "")},
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            metadata["stderr_preview"] = stderr_preview(exc.stderr or "")
            return error_trace("command timed out", mode=request.mode, command_metadata=metadata)
        except OSError as exc:
            return error_trace(f"command launch failed: {type(exc).__name__}", mode=request.mode, command_metadata=metadata)

        metadata["command_exit_status"] = completed.returncode
        metadata["stderr_preview"] = stderr_preview(completed.stderr or "")
        if completed.returncode != 0:
            return error_trace(
                f"command exited with status {completed.returncode}",
                mode=request.mode,
                command_metadata=metadata,
            )

        try:
            response = json.loads(completed.stdout)
        except json.JSONDecodeError:
            return error_trace("command stdout was not valid JSON", mode=request.mode, command_metadata=metadata)
        if response.get("protocol_version") != DHMS_AGENT_PROTOCOL_VERSION:
            return error_trace("wrong protocol_version", mode=request.mode, command_metadata=metadata)
        trace = response.get("trace")
        if not isinstance(trace, dict):
            return error_trace("response missing trace object", mode=request.mode, command_metadata=metadata)

        trace.setdefault("mode", request.mode)
        validation = validate_agent_trace(trace)
        trace["_command_metadata"] = metadata
        trace["_trace_validation"] = validation
        if not validation["valid"]:
            trace.setdefault("errors", [])
            trace["errors"] = list(trace.get("errors", [])) + validation["errors"]
        return normalize_trace(trace)


def command_metadata_from_trace(trace: dict[str, Any]) -> dict[str, Any]:
    meta = trace.get("_command_metadata")
    return meta if isinstance(meta, dict) else {}
