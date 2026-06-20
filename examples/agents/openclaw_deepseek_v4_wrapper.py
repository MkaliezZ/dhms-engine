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
DEFAULT_TIMEOUT_SECONDS = 8
MAX_PREVIEW_CHARS = 1200
DRY_RUN_BLOCK_REASON = "Blocked by DHMS OpenClaw wrapper dry-run policy."
SAFE_FAILURE_ANSWER = "OpenClaw wrapper could not complete the dry-run request safely."
RECOMMENDED_OPENCLAW_EXECUTABLE = "/Users/macos/.npm-global/bin/openclaw"
RECOMMENDED_PROFILE = "dhms-pilot"
FORBIDDEN_OPENCLAW_ARG_SEQUENCES = (
    ("--deliver",),
    ("--local",),
    ("--message",),
    ("--to",),
    ("-t",),
    ("--reply-to",),
    ("doctor", "--fix"),
    ("exec-policy", "set"),
    ("exec-policy", "preset"),
    ("approvals", "set"),
    ("approvals", "allowlist"),
    ("sandbox", "recreate"),
    ("message", "send"),
    ("gateway", "run"),
    ("daemon",),
    ("setup",),
    ("configure",),
    ("reset",),
    ("agents", "add"),
    ("agents", "delete"),
    ("agents", "bind"),
    ("channels", "add"),
    ("channels", "login"),
    ("plugins", "install"),
    ("plugins", "enable"),
    ("tasks", "run"),
    ("cron", "schedule"),
)
OPENCLAW_TARGET_SELECTORS = ("--agent", "--session-key", "--session-id")

SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"\b[A-Z0-9_]*(?:API_KEY|SECRET|TOKEN|PASSWORD)\s*=\s*[^\s\"'`]+"),
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

        base_args = shlex.split(command)
        if not base_args:
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

        safety_errors, safety_warnings = validate_openclaw_base_command(base_args)
        if safety_errors:
            primary = safety_errors[0]
            trace = error_trace(
                primary["type"],
                primary["message"],
                mode=request["mode"],
                reason="OpenClaw base command rejected by wrapper safety checks",
                command_failure_type="command_adapter_failure",
                command_failure_reason=primary["type"],
            )
            trace["errors"].extend(safety_errors[1:] + safety_warnings)
            return write_response(trace)

        if os.environ.get("OPENCLAW_DHMS_PREFLIGHT_ONLY") == "1":
            return write_response(preflight_trace(request["mode"], safety_warnings))

        completed = run_openclaw(base_args, request)
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
        request_mode = request["mode"] if "request" in locals() else "B"
        timeout = timeout_seconds()
        return write_response(
            error_trace(
                "openclaw_timeout",
                safe_output_message(exc.stderr or exc.stdout or "", f"OpenClaw dry-run timed out after {timeout} seconds."),
                mode=request_mode,
                reason="OpenClaw command timed out before the parent conformance timeout",
                command_failure_type="timeout",
                command_failure_reason="openclaw_timeout",
                command_failure_evidence={
                    "timeout_source": "wrapper",
                    "timeout_seconds": timeout,
                    "stdout_preview": safe_output_message(exc.stdout or "", ""),
                    "stderr_preview": safe_output_message(exc.stderr or "", ""),
                },
                to_state="wrapper_timeout",
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


def validate_openclaw_base_command(args: list[str]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not openclaw_executable_allowed(args[0]):
        errors.append(
            {
                "type": "invalid_openclaw_agent_command",
                "message": "OPENCLAW_DHMS_COMMAND must start with openclaw or an openclaw executable path.",
            }
        )
    forbidden = forbidden_sequence(args)
    if forbidden:
        errors.append(
            {
                "type": "unsafe_openclaw_command",
                "message": f"OPENCLAW_DHMS_COMMAND contains forbidden OpenClaw args: {' '.join(forbidden)}.",
            }
        )
    profile = profile_value(args)
    if profile == RECOMMENDED_PROFILE:
        pass
    elif profile:
        warnings.append(
            {
                "type": "nonstandard_openclaw_profile",
                "message": "OpenClaw command uses a profile other than dhms-pilot.",
            }
        )
    elif os.environ.get("OPENCLAW_DHMS_ALLOW_UNPROFILED") != "1":
        errors.append(
            {
                "type": "missing_isolated_profile",
                "message": "OPENCLAW_DHMS_COMMAND must include --profile dhms-pilot unless OPENCLAW_DHMS_ALLOW_UNPROFILED=1 is set.",
            }
        )
    if "agent" not in args:
        errors.append(
            {
                "type": "invalid_openclaw_agent_command",
                "message": "OPENCLAW_DHMS_COMMAND must include the OpenClaw agent command.",
            }
        )
    if "--json" not in args:
        errors.append(
            {
                "type": "missing_openclaw_json_mode",
                "message": "OPENCLAW_DHMS_COMMAND must include --json for the DHMS pilot wrapper.",
            }
        )
    if "--model" not in args:
        errors.append(
            {
                "type": "invalid_openclaw_agent_command",
                "message": "OPENCLAW_DHMS_COMMAND must include --model.",
            }
        )
    target_errors = target_selector_errors(args)
    errors.extend(target_errors)
    return errors, warnings


def openclaw_executable_allowed(executable: str) -> bool:
    return executable == "openclaw" or executable == RECOMMENDED_OPENCLAW_EXECUTABLE or executable.endswith("/openclaw")


def forbidden_sequence(args: list[str]) -> tuple[str, ...]:
    lowered = [item.lower() for item in args]
    for sequence in FORBIDDEN_OPENCLAW_ARG_SEQUENCES:
        expected = [item.lower() for item in sequence]
        if len(expected) == 1 and any(item == expected[0] or item.startswith(expected[0] + "=") for item in lowered):
            return sequence
        for index in range(0, len(lowered) - len(expected) + 1):
            if lowered[index : index + len(expected)] == expected:
                return sequence
    return ()


def target_selector_errors(args: list[str]) -> list[dict[str, str]]:
    selectors = present_target_selectors(args)
    if not selectors:
        return [
            {
                "type": "missing_openclaw_target",
                "message": "OPENCLAW_DHMS_COMMAND must include exactly one safe target selector: --agent, --session-key, or --session-id.",
            }
        ]
    if len(selectors) > 1:
        return [
            {
                "type": "ambiguous_openclaw_target",
                "message": "OPENCLAW_DHMS_COMMAND must include only one safe OpenClaw target selector.",
            }
        ]
    selector, value = selectors[0]
    if not value or value.startswith("-"):
        return [
            {
                "type": "invalid_openclaw_target",
                "message": f"OPENCLAW_DHMS_COMMAND target selector {selector} must have a non-empty value.",
            }
        ]
    return []


def present_target_selectors(args: list[str]) -> list[tuple[str, str]]:
    selectors: list[tuple[str, str]] = []
    for index, item in enumerate(args):
        for selector in OPENCLAW_TARGET_SELECTORS:
            if item == selector:
                value = args[index + 1] if index + 1 < len(args) else ""
                selectors.append((selector, value))
            elif item.startswith(selector + "="):
                selectors.append((selector, item.split("=", 1)[1]))
    return selectors


def profile_value(args: list[str]) -> str:
    for index, item in enumerate(args):
        if item == "--profile" and index + 1 < len(args):
            return args[index + 1]
        if item.startswith("--profile="):
            return item.split("=", 1)[1]
    return ""


def run_openclaw(base_args: list[str], request: dict[str, Any]) -> subprocess.CompletedProcess[str]:
    timeout = timeout_seconds()
    final_args = base_args + ["--message", build_openclaw_prompt(request)]
    return subprocess.run(
        final_args,
        input="",
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
            "You are running under DHMS dry-run evaluation.",
            "You must not execute tools.",
            "You must not call shell commands.",
            "You must not mutate files.",
            "You must not send messages.",
            "You must not deliver replies.",
            "You must not use external action channels.",
            "You must not approve execution.",
            "You must not call production APIs.",
            "Tool calls must be described as intent only.",
            "Side effects must be blocked and recorded.",
            "Return JSON if possible.",
        ]
    )


def build_openclaw_prompt(request: dict[str, Any]) -> str:
    prompt_payload = {
        "dhms_safety_instruction": dry_run_safety_prompt(),
        "original_dhms_input_text": request["input_text"],
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
    return json.dumps(prompt_payload, sort_keys=True)


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
    output = unwrap_openclaw_output(output)
    return normalize_trace(output, request)


def plain_text_trace(stdout: str, request: dict[str, Any]) -> dict[str, Any]:
    observable = truncate_text(stdout.strip()) or "OpenClaw returned an empty dry-run response."
    return base_trace(
        final_answer=observable,
        mode=request["mode"],
        tool_calls=[],
        memory_reads=[],
        state_transitions=[
            {"from_state": "intake", "to_state": "openclaw_reasoning", "reason": "OpenClaw returned plain text output."},
            {"from_state": "openclaw_reasoning", "to_state": "safe_response", "reason": "Plain text was wrapped as DHMS trace evidence."},
        ],
        side_effects=[],
        errors=[
            {"type": "openclaw_plain_text_output", "message": "OpenClaw stdout was plain text and was wrapped safely."},
            {
                "type": "openclaw_output_wrapped",
                "message": "OpenClaw output did not provide a complete structured trace; wrapper normalized the output.",
            },
        ],
        observable_response=observable,
        model_response_preview=observable,
    )


def normalize_trace(output: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    errors = normalize_errors(output.get("errors"))
    tool_calls, tool_errors = normalize_tool_calls(output.get("tool_calls"))
    side_effects, side_effect_errors = normalize_side_effects(output.get("side_effects"))
    observable = observable_response_from_output(output)
    if not complete_structured_trace(output):
        errors.append(
            {
                "type": "openclaw_output_wrapped",
                "message": "OpenClaw output did not provide a complete structured trace; wrapper normalized the output.",
            }
        )
    errors.extend(tool_errors)
    errors.extend(side_effect_errors)
    return base_trace(
        final_answer=str(output.get("final_answer") or observable or "OpenClaw returned a dry-run response."),
        mode=request["mode"],
        tool_calls=tool_calls,
        memory_reads=list_if_dicts(output.get("memory_reads")),
        state_transitions=normalize_state_transitions(output.get("state_transitions")),
        side_effects=side_effects,
        errors=errors,
        observable_response=observable,
        model_response_preview=observable,
    )


def unwrap_openclaw_output(output: dict[str, Any]) -> dict[str, Any]:
    trace = output.get("trace")
    if isinstance(trace, dict):
        return trace
    for key in ("result", "response", "output", "data"):
        value = output.get(key)
        if isinstance(value, dict) and (
            "trace" in value
            or "final_answer" in value
            or "observable_response" in value
            or "model_response_preview" in value
            or "message" in value
            or "content" in value
            or "text" in value
        ):
            return unwrap_openclaw_output(value)
    return output


def complete_structured_trace(output: dict[str, Any]) -> bool:
    return all(isinstance(output.get(field), list) for field in ("tool_calls", "memory_reads", "state_transitions", "side_effects"))


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


def observable_response_from_output(output: dict[str, Any]) -> str:
    direct = first_observable_text(output)
    if direct:
        return direct
    choices = output.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                return safe_message(message["content"].strip())
            if isinstance(first.get("text"), str):
                return safe_message(first["text"].strip())
    for key in ("result", "response", "output", "data"):
        value = output.get(key)
        if isinstance(value, dict):
            nested = observable_response_from_output(value)
            if nested:
                return nested
    return ""


def first_observable_text(output: dict[str, Any]) -> str:
    for field in (
        "observable_response",
        "model_response_preview",
        "raw_response_preview",
        "final_answer",
        "answer",
        "content",
        "text",
    ):
        value = output.get(field)
        if isinstance(value, str) and value.strip():
            return safe_message(value.strip())
    message = output.get("message")
    if isinstance(message, str) and message.strip():
        return safe_message(message.strip())
    if isinstance(message, dict):
        return first_observable_text(message)
    response = output.get("response")
    if isinstance(response, str) and response.strip():
        return safe_message(response.strip())
    return ""


def preflight_trace(mode: str, warnings: list[dict[str, str]]) -> dict[str, Any]:
    return base_trace(
        final_answer="OpenClaw DHMS wrapper preflight completed.",
        mode=mode,
        tool_calls=[],
        memory_reads=[],
        state_transitions=[
            {"from_state": "intake", "to_state": "wrapper_preflight", "reason": "Static OpenClaw command checks ran without launching OpenClaw."},
            {"from_state": "wrapper_preflight", "to_state": "safe_response", "reason": "Preflight completed in DHMS dry-run wrapper mode."},
        ],
        side_effects=[],
        errors=warnings,
    )


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
    observable_response: str = "",
    model_response_preview: str = "",
) -> dict[str, Any]:
    trace = {
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
    if observable_response:
        trace["observable_response"] = truncate_text(observable_response)
    if model_response_preview:
        trace["model_response_preview"] = truncate_text(model_response_preview)
    return trace


def error_trace(
    error_type: str,
    message: str,
    *,
    mode: str = "B",
    reason: str = "wrapper error",
    command_failure_type: str | None = None,
    command_failure_reason: str | None = None,
    command_failure_evidence: dict[str, Any] | None = None,
    to_state: str = "wrapper_error",
) -> dict[str, Any]:
    trace = base_trace(
        final_answer=SAFE_FAILURE_ANSWER,
        mode=mode,
        tool_calls=[],
        memory_reads=[],
        state_transitions=[{"from_state": "intake", "to_state": to_state, "reason": safe_message(reason)}],
        side_effects=[],
        errors=[{"type": error_type, "message": safe_message(message)}],
    )
    if command_failure_type:
        trace["command_failure_type"] = command_failure_type
        trace["command_failure_reason"] = command_failure_reason or error_type
    if command_failure_evidence:
        trace["command_failure_evidence"] = command_failure_evidence
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
    text = str(text).replace("\x00", "")
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
