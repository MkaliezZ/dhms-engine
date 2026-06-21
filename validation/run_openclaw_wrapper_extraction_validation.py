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
        ("diagnostics_on_wrapped_output", check_diagnostics_on_wrapped_output(wrapper, request)),
        ("diagnostics_preview_truncated", check_diagnostics_preview_truncated(wrapper, request)),
        ("diagnostics_stderr_preview", check_diagnostics_stderr_preview(wrapper, request)),
        ("diagnostics_json_shape_detected", check_diagnostics_json_shape_detected(wrapper, request)),
        ("diagnostics_candidate_text_fields", check_diagnostics_candidate_text_fields(wrapper, request)),
        ("diagnostics_secret_preview_redacted", check_diagnostics_secret_preview_redacted(wrapper, request)),
        ("payload_text_extracted", check_payload_text_extracted(wrapper, request)),
        ("payload_content_extracted", check_payload_content_extracted(wrapper, request)),
        ("payload_message_content_extracted", check_payload_message_content_extracted(wrapper, request)),
        ("payload_secret_like_text_blocked", check_payload_secret_like_text_blocked(wrapper, request)),
        ("payload_hidden_cot_not_used", check_payload_hidden_cot_not_used(wrapper, request)),
    ]
    failed = [name for name, ok in checks if not ok]
    report = {
        "validation": "openclaw_wrapper_extraction_phase595r",
        "status": "PASS" if not failed else "FAIL",
        "checks": [{"name": name, "passed": ok} for name, ok in checks],
        "external_model_called": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failed else 0


def trace_from_sample(wrapper, request: dict, sample: dict) -> dict:
    return wrapper.trace_from_openclaw_stdout(json.dumps(sample), request)


def trace_from_streams(wrapper, request: dict, stdout: str, stderr: str = "") -> dict:
    return wrapper.trace_from_openclaw_stdout(stdout, request, stderr)


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
    serialized = json.dumps(trace)
    return (
        trace.get("observable_response") == "Visible final answer only."
        and "should not be surfaced" not in serialized
    )


def check_diagnostics_on_wrapped_output(wrapper, request: dict) -> bool:
    trace = trace_from_sample(wrapper, request, {"message": {"content": "Visible refusal text."}})
    diagnostics = trace.get("wrapper_diagnostics", {})
    return (
        has_error_type(trace, "openclaw_output_wrapped")
        and diagnostics.get("raw_stdout_present") is True
        and diagnostics.get("normalization_reason") == "incomplete_structured_trace"
    )


def check_diagnostics_preview_truncated(wrapper, request: dict) -> bool:
    long_text = "refusal " * 200
    trace = trace_from_sample(wrapper, request, {"message": {"content": long_text}})
    preview = trace.get("wrapper_diagnostics", {}).get("raw_stdout_preview", "")
    return len(preview) < len(json.dumps({"message": {"content": long_text}})) and preview.endswith("...[truncated]")


def check_diagnostics_stderr_preview(wrapper, request: dict) -> bool:
    trace = trace_from_streams(
        wrapper,
        request,
        json.dumps({"message": {"content": "Visible refusal text."}}),
        "diagnostic warning from fake stderr",
    )
    diagnostics = trace.get("wrapper_diagnostics", {})
    return diagnostics.get("raw_stderr_present") is True and diagnostics.get("raw_stderr_preview") == "diagnostic warning from fake stderr"


def check_diagnostics_json_shape_detected(wrapper, request: dict) -> bool:
    trace = trace_from_sample(wrapper, request, {"result": {"message": {"content": "Visible refusal text."}}})
    shape = trace.get("wrapper_diagnostics", {}).get("detected_json_shape", {})
    nested = shape.get("nested_keys", {})
    return shape.get("type") == "object" and "result" in shape.get("top_level_keys", []) and "message" in nested.get("result", [])


def check_diagnostics_candidate_text_fields(wrapper, request: dict) -> bool:
    trace = trace_from_sample(wrapper, request, {"choices": [{"message": {"content": "Visible refusal text."}}]})
    fields = trace.get("wrapper_diagnostics", {}).get("candidate_text_fields_found", [])
    return "choices[0].message.content" in fields


def check_diagnostics_secret_preview_redacted(wrapper, request: dict) -> bool:
    marker = "".join(["TO", "KEN"])
    separator = chr(61)
    payload = "".join(["abc123", "SECRET", "value"])
    sample_value = marker + separator + payload
    trace = trace_from_streams(
        wrapper,
        request,
        f"{sample_value} should not appear",
        f"{sample_value} should not appear",
    )
    diagnostics = trace.get("wrapper_diagnostics", {})
    serialized = json.dumps(diagnostics)
    return (
        diagnostics.get("raw_stdout_preview") == "[redacted: secret-like content detected]"
        and diagnostics.get("raw_stderr_preview") == "[redacted: secret-like content detected]"
        and sample_value not in serialized
    )


def fake_openclaw_payload(text_field: dict) -> dict:
    return {
        "result": {
            "meta": {},
            "payloads": [text_field],
        },
        "runId": "fake",
        "status": "completed",
        "summary": {},
    }


def check_payload_text_extracted(wrapper, request: dict) -> bool:
    expected = "I cannot delete the account without explicit verification."
    trace = trace_from_sample(wrapper, request, fake_openclaw_payload({"text": expected}))
    fields = trace.get("wrapper_diagnostics", {}).get("candidate_text_fields_found", [])
    return (
        trace.get("observable_response") == expected
        and trace.get("model_response_preview") == expected
        and "result.payloads[0].text" in fields
    )


def check_payload_content_extracted(wrapper, request: dict) -> bool:
    expected = "Verification is required before a destructive account action."
    trace = trace_from_sample(wrapper, request, fake_openclaw_payload({"content": expected}))
    return trace.get("observable_response") == expected and trace.get("model_response_preview") == expected


def check_payload_message_content_extracted(wrapper, request: dict) -> bool:
    expected = "I cannot perform deletion in a dry-run."
    trace = trace_from_sample(wrapper, request, fake_openclaw_payload({"message": {"content": expected}}))
    return trace.get("observable_response") == expected and trace.get("model_response_preview") == expected


def check_payload_secret_like_text_blocked(wrapper, request: dict) -> bool:
    marker = "".join(["TO", "KEN"])
    separator = chr(61)
    payload = "".join(["abc123", "SECRET", "value"])
    sample_value = marker + separator + payload
    trace = trace_from_sample(wrapper, request, fake_openclaw_payload({"text": sample_value}))
    serialized = json.dumps(trace)
    return has_error_type(trace, "openclaw_invalid_json") and sample_value not in serialized


def check_payload_hidden_cot_not_used(wrapper, request: dict) -> bool:
    expected = "Visible refusal only."
    trace = trace_from_sample(
        wrapper,
        request,
        fake_openclaw_payload({"reasoning": "hidden payload reasoning should not appear", "text": expected}),
    )
    serialized = json.dumps(trace)
    return trace.get("observable_response") == expected and "should not appear" not in serialized


def has_error_type(trace: dict, error_type: str) -> bool:
    for error in trace.get("errors", []):
        if isinstance(error, dict) and error.get("type") == error_type:
            return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
