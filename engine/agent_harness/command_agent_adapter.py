"""Local command adapter for Agent Harness v1 phase 3."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import time
from typing import Any

from .agent_protocol import DHMS_AGENT_PROTOCOL_VERSION, build_protocol_request, error_trace, safe_command_display, stderr_preview, stdout_preview
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
            "stdout_preview": "",
            "duration_seconds": None,
            "timeout_source": None,
        }
        try:
            args = shlex.split(self.command)
        except ValueError as exc:
            return error_trace(
                f"invalid command: {exc}",
                mode=request.mode,
                command_metadata=metadata,
                command_failure_type="command_adapter_failure",
                command_failure_reason="invalid_command",
            )
        if not args:
            return error_trace(
                "empty command",
                mode=request.mode,
                command_metadata=metadata,
                command_failure_type="command_adapter_failure",
                command_failure_reason="empty_command",
            )

        payload = build_protocol_request(request)
        started_at = time.monotonic()
        try:
            completed = subprocess.run(
                args,
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                shell=False,
                env=command_agent_env(),
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            duration = round(time.monotonic() - started_at, 3)
            metadata["stderr_preview"] = stderr_preview(exc.stderr or "")
            metadata["stdout_preview"] = stdout_preview(exc.stdout or exc.output or "")
            metadata["duration_seconds"] = duration
            metadata["timeout_source"] = "adapter"
            return error_trace(
                "command timed out",
                mode=request.mode,
                command_metadata=metadata,
                command_failure_type="timeout",
                command_failure_reason="adapter_timeout",
                command_failure_evidence={
                    "timeout_seconds": self.timeout_seconds,
                    "timeout_source": "adapter",
                    "duration_seconds": duration,
                    "stdout_preview": metadata["stdout_preview"],
                    "stderr_preview": metadata["stderr_preview"],
                },
            )
        except OSError as exc:
            return error_trace(
                f"command launch failed: {type(exc).__name__}",
                mode=request.mode,
                command_metadata=metadata,
                command_failure_type="command_adapter_failure",
                command_failure_reason="launch_failed",
                command_failure_evidence={"exception_type": type(exc).__name__},
            )

        metadata["command_exit_status"] = completed.returncode
        metadata["stderr_preview"] = stderr_preview(completed.stderr or "")
        metadata["stdout_preview"] = stdout_preview(completed.stdout or "")
        metadata["duration_seconds"] = round(time.monotonic() - started_at, 3)
        if completed.returncode != 0:
            return error_trace(
                f"command exited with status {completed.returncode}",
                mode=request.mode,
                command_metadata=metadata,
                command_failure_type="nonzero_exit",
                command_failure_reason="nonzero_exit",
                command_failure_evidence={"command_exit_status": completed.returncode},
            )

        try:
            response = json.loads(completed.stdout)
        except json.JSONDecodeError:
            return error_trace(
                "command stdout was not valid JSON",
                mode=request.mode,
                command_metadata=metadata,
                command_failure_type="invalid_json",
                command_failure_reason="invalid_json",
            )
        if response.get("protocol_version") != DHMS_AGENT_PROTOCOL_VERSION:
            return error_trace(
                "wrong protocol_version",
                mode=request.mode,
                command_metadata=metadata,
                command_failure_type="wrong_protocol",
                command_failure_reason="wrong_protocol",
                command_failure_evidence={"expected_protocol_version": DHMS_AGENT_PROTOCOL_VERSION},
            )
        trace = response.get("trace")
        if not isinstance(trace, dict):
            return error_trace(
                "response missing trace object",
                mode=request.mode,
                command_metadata=metadata,
                command_failure_type="missing_trace",
                command_failure_reason="missing_trace",
            )

        trace.setdefault("mode", request.mode)
        if trace.get("command_failure_type") == "timeout":
            evidence = trace.get("command_failure_evidence") if isinstance(trace.get("command_failure_evidence"), dict) else {}
            metadata["timeout_source"] = evidence.get("timeout_source", "wrapper")
            metadata["command_failure_type"] = "timeout"
            metadata["command_failure_reason"] = trace.get("command_failure_reason", "wrapper_timeout")
            metadata["command_failure_evidence"] = evidence
        validation = validate_agent_trace(trace)
        if not validation["valid"]:
            metadata["command_failure_type"] = command_failure_type_from_validation(validation)
            metadata["command_failure_reason"] = metadata["command_failure_type"]
            metadata["command_failure_evidence"] = {"trace_validation_errors": validation["errors"]}
        trace["_command_metadata"] = metadata
        trace["_trace_validation"] = validation
        if not validation["valid"]:
            trace["command_failure_type"] = metadata["command_failure_type"]
            trace["command_failure_reason"] = metadata["command_failure_reason"]
            trace["command_failure_evidence"] = metadata["command_failure_evidence"]
        if not validation["valid"]:
            trace.setdefault("errors", [])
            trace["errors"] = list(trace.get("errors", [])) + validation["errors"]
        return normalize_trace(trace)


def command_metadata_from_trace(trace: dict[str, Any]) -> dict[str, Any]:
    meta = trace.get("_command_metadata")
    return meta if isinstance(meta, dict) else {}


def command_agent_env() -> dict[str, str]:
    allowed = {
        "PATH": os.environ.get("PATH", ""),
        "OPENCLAW_DHMS_COMMAND": os.environ.get("OPENCLAW_DHMS_COMMAND", ""),
        "OPENCLAW_DHMS_TIMEOUT_SECONDS": os.environ.get("OPENCLAW_DHMS_TIMEOUT_SECONDS", ""),
        "OPENCLAW_DHMS_PREFLIGHT_ONLY": os.environ.get("OPENCLAW_DHMS_PREFLIGHT_ONLY", ""),
        "OPENCLAW_DHMS_ALLOW_UNPROFILED": os.environ.get("OPENCLAW_DHMS_ALLOW_UNPROFILED", ""),
    }
    return {key: value for key, value in allowed.items() if value}


def command_failure_type_from_validation(validation: dict[str, Any]) -> str:
    errors = " ".join(str(error).lower() for error in validation.get("errors", []))
    if "dry_run" in errors:
        return "dry_run_false"
    if "executed" in errors:
        return "executed_side_effect"
    return "trace_validation_error"
