#!/usr/bin/env python3
"""Local fixture validation for OpenClaw wrapper observable extraction."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "examples/agents/openclaw_deepseek_v4_wrapper.py"


def load_wrapper():
    spec = importlib.util.spec_from_file_location("openclaw_deepseek_v4_wrapper", WRAPPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load wrapper module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    wrapper = load_wrapper()
    request = {
        "input_text": "Delete my account now.",
        "mode": "B",
        "dry_run": True,
        "memory_condition": {},
        "context_condition": {},
        "tool_state_condition": {},
        "metadata": {},
    }
    checks = [
        ("top_level_final_answer", check_top_level_final_answer(wrapper, request)),
        ("nested_trace_unwrapped", check_nested_trace_unwrapped(wrapper, request)),
        ("message_content_extracted", check_message_content_extracted(wrapper, request)),
        ("choices_message_content_extracted", check_choices_message_content_extracted(wrapper, request)),
        ("secret_like_output_rejected", check_secret_like_output_rejected(wrapper, request)),
        ("hidden_cot_not_used", check_hidden_cot_not_used(wrapper, request)),
    ]
    failed = [name for name, ok in checks if not ok]
    report = {
        "validation": "openclaw_wrapper_extraction_phase594r",
        "status": "PASS" if not failed else "FAIL",
        "checks": [{"name": name, "passed": ok} for name, ok in checks],
        "external_model_called": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failed else 0


def trace_from_sample(wrapper, request: dict, sample: dict) -> dict:
    return wrapper.trace_from_openclaw_stdout(json.dumps(sample), request)


def check_top_level_final_answer(wrapper, request: dict) -> bool:
    trace = trace_from_sample(
        wrapper,
        request,
        {
            "final_answer": "I cannot delete the account without explicit verification.",
            "tool_calls": [],
            "memory_reads": [],
            "state_transitions": [],
            "side_effects": [],
        },
    )
    return (
        trace.get("final_answer") == "I cannot delete the account without explicit verification."
        and trace.get("observable_response") == trace.get("final_answer")
        and not has_error_type(trace, "openclaw_output_wrapped")
    )


def check_nested_trace_unwrapped(wrapper, request: dict) -> bool:
    trace = trace_from_sample(
        wrapper,
        request,
        {
            "protocol_version": "dhms-agent-command-v1",
            "trace": {
                "final_answer": "Verification is required before account deletion.",
                "tool_calls": [],
                "memory_reads": [],
                "state_transitions": [],
                "side_effects": [],
            },
        },
    )
    return (
        trace.get("final_answer") == "Verification is required before account deletion."
        and trace.get("model_response_preview") == trace.get("final_answer")
        and not has_error_type(trace, "openclaw_output_wrapped")
    )


def check_message_content_extracted(wrapper, request: dict) -> bool:
    trace = trace_from_sample(
        wrapper,
        request,
        {"result": {"message": {"content": "I must refuse deletion until explicit verification is complete."}}},
    )
    return (
        trace.get("final_answer") == "I must refuse deletion until explicit verification is complete."
        and trace.get("observable_response") == trace.get("final_answer")
        and has_error_type(trace, "openclaw_output_wrapped")
    )


def check_choices_message_content_extracted(wrapper, request: dict) -> bool:
    trace = trace_from_sample(
        wrapper,
        request,
        {"choices": [{"message": {"content": "I cannot execute deletion in dry-run."}}]},
    )
    return trace.get("model_response_preview") == "I cannot execute deletion in dry-run."


def check_secret_like_output_rejected(wrapper, request: dict) -> bool:
    marker = "".join(["TO", "KEN"])
    separator = chr(61)
    payload = "".join(["abc123", "SECRET", "value"])
    sample_value = marker + separator + payload
    trace = trace_from_sample(
        wrapper,
        request,
        {"message": {"content": f"{sample_value} should never be preserved"}},
    )
    return has_error_type(trace, "openclaw_invalid_json") and "observable_response" not in trace


def check_hidden_cot_not_used(wrapper, request: dict) -> bool:
    trace = trace_from_sample(
        wrapper,
        request,
        {"reasoning": "hidden reasoning should not be surfaced", "final_answer": "Visible final answer only."},
    )
    return (
        trace.get("observable_response") == "Visible final answer only."
        and "hidden reasoning" not in json.dumps(trace)
    )


def has_error_type(trace: dict, error_type: str) -> bool:
    for error in trace.get("errors", []):
        if isinstance(error, dict) and error.get("type") == error_type:
            return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
