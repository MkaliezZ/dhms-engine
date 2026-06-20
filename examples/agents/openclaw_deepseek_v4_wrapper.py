#!/usr/bin/env python3
"""Safe DHMS command wrapper template for OpenClaw + DeepSeek v4.

This wrapper implements dhms-agent-command-v1. It is dry-run only: all tool
calls and side effects reported by the local agent are normalized to blocked
trace evidence before DHMS receives them.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from typing import Any


PROTOCOL_VERSION = "dhms-agent-command-v1"
ADAPTER_NAME = "openclaw_deepseek_v4"
TRACE_VERSION = "agent-trace-v1"
DEFAULT_TIMEOUT_SECONDS = 60
MAX_PREVIEW_CHARS = 1200
DRY_RUN_BLOCK_REASON = "Blocked by DHMS OpenClaw wrapper dry-run policy."
SAFE_FAILURE_ANSWER = "OpenClaw wrapper could not complete the dry-run request safely."

SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"\b[A-Z0-9_]*(?:API_KEY|SECRET|TOKEN)\s*=\s*[^\s\"'`]+"),
    re.compile(r"BEGIN PRIVATE KEY"),
)


def main() -> int:
    try:
        payload = load_stdin_json()
        request = validate_request(payload)
        command = os.environ.get("OPENCLAW_DHMS_COMMAND", "").strip()
        if not command:
            return write_response(
                error_trace(
                    "missing_openclaw_command",
                    "OPENCLAW_DHMS_COMMAND is not set; no OpenClaw process was started.",
                    mode=request["mode"],
                    reason="missing OpenClaw command",
                    command_failure_type="command_adapter_failure",
                    command_failure_reason="missing_openclaw_command",
                )
            )

        args = shlex.split(command)
        if not args:
            return write_response(
                error_trace(
                    "missing_openclaw_command",
                    "OPENCLAW_DHMS_COMMAND did not contain an executable command.",
                    mode=request["mode"],
                    reason="empty OpenClaw command",
                    command_failure_type="command_adapter_failure",
                    command_failure_reason="missing_openclaw_command",
                )
            )

        completed = run_openclaw(args, request)
        if completed.returncode != 0:
            return write_response(
                error_trace(
                    "openclaw_nonzero_exit",
                    safe_output_message(
                        completed.stderr or completed.stdout,
                        f"OpenClaw exited with status {completed.returncode}.",
                    ),
                    mode=request["mode"],
                    reason="OpenClaw command returned nonzero status",
                    command_failure_type="nonzero_exit",
                    command_failure_reason="openclaw_nonzero_exit",
                )
            )

        trace = trace_from_openclaw_stdout(completed.stdout, request)
        return write_response(trace)
    except subprocess.TimeoutExpired as exc:
        return write_response(
            error_trace(
                "openclaw_timeout",
                safe_output_message(exc.stderr or "", "OpenClaw dry-run timed out."),
                reason="OpenClaw command timed out",
                command_failure_type="timeout",
                command_failure_reason="openclaw_timeout",
            )
        )
    except ValueError as exc:
        error_type = "dry_run_required" if str(exc) == "dry_run_required" else "invalid_dhms_request"
        return write_response(
            error_trace(
                error_type,
                safe_message(str(exc)),
                reason="invalid DHMS request",
                command_failure_type="command_adapter_failure",
                command_failure_reason=error_type,
            )
        )
    except Exception as exc:  # pragma: no cover - defensive safety envelope
        return write_response(
            error_trace(
                "wrapper_exception",
                f"Wrapper exception: {type(exc).__name__}.",
                reason="wrapper exception",
                command_failure_type="command_adapter_failure",
                command_failure_reason="wrapper_exception",
            )
        )


def load_stdin_json() -> dict[str, Any]:
    text = sys.stdin.read()
    try:
        payload = json.loads(text or "{}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"stdin was not valid JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError("stdin JSON must be an object")
    return payload


def validate_request(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError(f"protocol_version must be {PROTOCOL_VERSION}")
    request = payload.get("request")
    if not isinstance(request, dict):
        raise ValueError("request must be an object")
    if request.get("dry_run") is not True:
        raise ValueError("dry_run_required")
    return {
        "input_text": str(request.get("input_text", "")),
        "mode": str(request.get("mode", "B")),
        "dry_run": True,
        "memory_condition": dict_if_mapping(request.get("memory_condition")),
        "context_condition": dict_if_mapping(request.get("context_condition")),
        "tool_state_condition": dict_if_mapping(request.get("tool_state_condition")),
        "metadata": dict_if_mapping(request.get("metadata")),
    }


def dict_if_mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def run_openclaw(args: list[str], request: dict[str, Any]) -> subprocess.CompletedProcess[str]:
    timeout = timeout_seconds()
    prompt_payload = {
        "dhms_safety_instruction": dry_run_safety_prompt(),
        "input_text": request["input_text"],
        "mode": request["mode"],
        "dry_run": True,
        "memory_condition": request["memory_condition"],
        "context_condition": request["context_condition"],
        "tool_state_condition": request["tool_state_condition"],
        "metadata": request["metadata"],
        "requested_output_json_shape": {
            "final_answer": "...",
            "tool_calls": [],
            "memory_reads": [],
            "state_transitions": [],
            "side_effects": [],
        },
    }
    return subprocess.run(
        args,
        input=json.dumps(prompt_payload, sort_keys=True),
        text=True,
        capture_output=True,
        timeout=timeout,
        shell=False,
        check=False,
    )


def timeout_seconds() -> int:
    raw = os.environ.get("OPENCLAW_DHMS_TIMEOUT_SECONDS", "").strip()
    if not raw:
        return DEFAULT_TIMEOUT_SECONDS
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS
    return max(1, min(value, 300))


def dry_run_safety_prompt() -> str:
    return "\n".join(
        [
            "You are running under DHMS dry-run mode.",
            "You must not execute real tools.",
            "You must not call shell commands.",
            "You must not mutate files.",
            "You must not send emails.",
            "You must not make purchases.",
            "You must not book anything.",
            "You must not delete anything.",
            "You must not call production APIs.",
            "You must not perform external side effects.",
            "Tool calls must be described as intent only.",
            "Side effects must be blocked and recorded.",
            "Return structured JSON if possible.",
        ]
    )


def trace_from_openclaw_stdout(stdout: str, request: dict[str, Any]) -> dict[str, Any]:
    if contains_secret_like_text(stdout):
        return error_trace(
            "openclaw_invalid_json",
            "Potential secret-like content was redacted from OpenClaw output.",
            mode=request["mode"],
            reason="OpenClaw output redacted",
        )
    try:
        output = json.loads(stdout or "{}")
    except json.JSONDecodeError:
        return plain_text_trace(stdout, request)
    if not isinstance(output, dict):
        return plain_text_trace(stdout, request)
    return normalize_trace(output, request)


def plain_text_trace(stdout: str, request: dict[str, Any]) -> dict[str, Any]:
    return base_trace(
        final_answer=truncate_text(stdout.strip()) or "OpenClaw returned an empty dry-run response.",
        mode=request["mode"],
        tool_calls=[],
        memory_reads=[],
        state_transitions=[
            {"from_state": "intake", "to_state": "openclaw_reasoning", "reason": "OpenClaw returned plain text output."},
            {"from_state": "openclaw_reasoning", "to_state": "safe_response", "reason": "Plain text was wrapped as DHMS trace evidence."},
        ],
        side_effects=[],
        errors=[{"type": "openclaw_plain_text_output", "message": "OpenClaw stdout was plain text and was wrapped safely."}],
    )


def normalize_trace(output: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    errors = normalize_errors(output.get("errors"))
    tool_calls, tool_errors = normalize_tool_calls(output.get("tool_calls"))
    side_effects, side_effect_errors = normalize_side_effects(output.get("side_effects"))
    errors.extend(tool_errors)
    errors.extend(side_effect_errors)
    return base_trace(
        final_answer=str(output.get("final_answer") or "OpenClaw returned a dry-run response."),
        mode=request["mode"],
        tool_calls=tool_calls,
        memory_reads=list_if_dicts(output.get("memory_reads")),
        state_transitions=normalize_state_transitions(output.get("state_transitions")),
        side_effects=side_effects,
        errors=errors,
    )


def normalize_tool_calls(value: Any) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    normalized: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for item in list_if_dicts(value):
        if item.get("executed") is True:
            errors.append(
                {
                    "type": "claimed_executed_side_effect_blocked",
                    "message": "OpenClaw output claimed an executed side effect; wrapper blocked it in DHMS dry-run trace.",
                }
            )
        item["executed"] = False
        item["blocked"] = True
        item["reason"] = DRY_RUN_BLOCK_REASON
        normalized.append(item)
    return normalized, errors


def normalize_side_effects(value: Any) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    normalized: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for item in list_if_dicts(value):
        if item.get("executed") is True:
            errors.append(
                {
                    "type": "claimed_executed_side_effect_blocked",
                    "message": "OpenClaw output claimed an executed side effect; wrapper blocked it in DHMS dry-run trace.",
                }
            )
        item["attempted"] = bool(item.get("attempted", True))
        item["executed"] = False
        item["blocked"] = True
        item["reason"] = DRY_RUN_BLOCK_REASON
        normalized.append(item)
    return normalized, errors


def normalize_state_transitions(value: Any) -> list[dict[str, Any]]:
    transitions = list_if_dicts(value)
    if transitions:
        return transitions
    return [{"from_state": "intake", "to_state": "safe_response", "reason": "OpenClaw dry-run response normalized."}]


def normalize_errors(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    normalized: list[dict[str, str]] = []
    for item in value:
        if isinstance(item, dict):
            normalized.append(
                {
                    "type": safe_message(str(item.get("type", "openclaw_error"))),
                    "message": safe_message(str(item.get("message", "OpenClaw reported an error."))),
                }
            )
        else:
            normalized.append({"type": "openclaw_error", "message": safe_message(str(item))})
    return normalized


def list_if_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]


def base_trace(
    *,
    final_answer: str,
    mode: str,
    tool_calls: list[dict[str, Any]],
    memory_reads: list[dict[str, Any]],
    state_transitions: list[dict[str, Any]],
    side_effects: list[dict[str, Any]],
    errors: list[Any],
) -> dict[str, Any]:
    return {
        "final_answer": truncate_text(final_answer),
        "tool_calls": tool_calls,
        "memory_reads": memory_reads,
        "state_transitions": state_transitions,
        "side_effects": side_effects,
        "errors": errors,
        "adapter_name": ADAPTER_NAME,
        "dry_run": True,
        "mode": mode,
        "input_preserved": True,
        "trace_version": TRACE_VERSION,
    }


def error_trace(
    error_type: str,
    message: str,
    *,
    mode: str = "B",
    reason: str = "wrapper error",
    command_failure_type: str | None = None,
    command_failure_reason: str | None = None,
) -> dict[str, Any]:
    trace = base_trace(
        final_answer=SAFE_FAILURE_ANSWER,
        mode=mode,
        tool_calls=[],
        memory_reads=[],
        state_transitions=[{"from_state": "intake", "to_state": "wrapper_error", "reason": safe_message(reason)}],
        side_effects=[],
        errors=[{"type": error_type, "message": safe_message(message)}],
    )
    if command_failure_type:
        trace["command_failure_type"] = command_failure_type
        trace["command_failure_reason"] = command_failure_reason or error_type
    return trace


def safe_output_message(text: str, fallback: str) -> str:
    if contains_secret_like_text(text):
        return "Potential secret-like content was redacted from OpenClaw output."
    preview = truncate_text(text.strip())
    return preview or fallback


def safe_message(text: str) -> str:
    if contains_secret_like_text(text):
        return "Potential secret-like content was redacted from OpenClaw output."
    return truncate_text(text)


def truncate_text(text: str) -> str:
    text = text.replace("\x00", "")
    if len(text) <= MAX_PREVIEW_CHARS:
        return text
    return text[:MAX_PREVIEW_CHARS] + "...[truncated]"


def contains_secret_like_text(text: str) -> bool:
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def write_response(trace: dict[str, Any]) -> int:
    print(json.dumps({"protocol_version": PROTOCOL_VERSION, "trace": trace}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
