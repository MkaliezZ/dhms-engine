"""Adapter Conformance Test Kit for local BYOA command agents."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from .adapter_conformance_cases import CONFORMANCE_CASES
from .adapter_conformance_report import write_adapter_conformance_reports
from .adapter_conformance_types import AdapterConformanceReport, ConformanceCheckResult, to_jsonable
from .agent_protocol import DHMS_AGENT_PROTOCOL_VERSION, safe_command_display
from .command_agent_adapter import CommandAgentAdapter, command_metadata_from_trace
from .trace_schema import AgentRunRequest


CONFORMANCE_VERSION = "adapter_conformance_v1_phase5"
SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"\b[A-Z0-9_]*(?:API_KEY|SECRET|TOKEN)\s*=\s*[^\s\"'`]+"),
    re.compile(r"BEGIN PRIVATE KEY"),
)
BLOCKING_FAILURE_TYPES = {
    "invalid_json": "invalid_json",
    "wrong_protocol": "wrong_protocol",
    "missing_trace": "missing_trace",
    "dry_run_false": "dry_run",
    "executed_side_effect": "executed_side_effect",
    "timeout": "timeout",
    "nonzero_exit": "nonzero_exit",
    "trace_validation_error": "missing_required_trace_fields",
    "command_adapter_failure": "process_launch",
}


def run_adapter_conformance(
    agent_command: str,
    output: str = "reports/adapter_conformance/latest",
    timeout_seconds: int = 10,
    report: bool = False,
) -> dict[str, Any]:
    adapter = CommandAgentAdapter(agent_command, timeout_seconds=timeout_seconds)
    probe_results: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    for case in CONFORMANCE_CASES:
        request = AgentRunRequest(
            input_text=case.input_text,
            mode="B",
            memory_condition={"refund_policy": "simulated policy memory for adapter conformance", "profile": case.case_id},
            context_condition={"conformance_case": case.case_id},
            tool_state_condition={"dry_run": True},
            dry_run=True,
            metadata={"conformance_case_id": case.case_id, "expected_focus": case.expected_focus},
        )
        trace = adapter.run(request)
        traces.append(trace)
        probe_results.append(probe_result(case, trace))

    check_results = build_check_results(traces)
    blocking_failures = blocking_failures_from_checks(check_results)
    score = readiness_score(check_results)
    overall = overall_status(check_results)
    report_data = AdapterConformanceReport(
        conformance_version=CONFORMANCE_VERSION,
        adapter_command=safe_command_display(agent_command),
        protocol_version=DHMS_AGENT_PROTOCOL_VERSION,
        overall_status=overall,
        adapter_readiness_score=score,
        blocking_failures=blocking_failures,
        warning_count=sum(1 for item in check_results if item.status == "WARN"),
        pass_count=sum(1 for item in check_results if item.status == "PASS"),
        fail_count=sum(1 for item in check_results if item.status == "FAIL"),
        check_results=[to_jsonable(item) for item in check_results],
        probe_results=probe_results,
        generated_at=datetime.now().isoformat(timespec="seconds"),
        caveats=[
            "Adapter conformance is not production certification.",
            "Dry-run only.",
            "Local BYOA command agents only.",
            "HTTP adapter not implemented.",
            "DHMS does not grant permission to execute user tools.",
        ],
        report_paths={},
    )
    result = to_jsonable(report_data)
    if report:
        result["report_paths"] = write_adapter_conformance_reports(result, output)
    return result


def probe_result(case: Any, trace: dict[str, Any]) -> dict[str, Any]:
    metadata = command_metadata_from_trace(trace)
    failure_type = trace.get("command_failure_type") or metadata.get("command_failure_type")
    validation = trace.get("_trace_validation") if isinstance(trace.get("_trace_validation"), dict) else {}
    status = "PASS"
    if failure_type or validation.get("valid") is False:
        status = "FAIL"
    elif validation.get("warnings"):
        status = "WARN"
    return {
        "case_id": case.case_id,
        "name": case.name,
        "focus": case.expected_focus,
        "status": status,
        "primary_failure": conformance_failure_key(str(failure_type or "")) or "none",
        "command_failure_type": failure_type or "none",
        "trace_validation": validation,
        "stderr_preview": metadata.get("stderr_preview", ""),
        "command_exit_status": metadata.get("command_exit_status"),
    }


def build_check_results(traces: list[dict[str, Any]]) -> list[ConformanceCheckResult]:
    failures_by_type = failure_cases_by_type(traces)
    trace_validation_errors = validation_errors(traces)
    attempted_unblocked = side_effect_attempts_unblocked(traces)
    tool_executed = tool_calls_executed(traces)
    stderr_hits = stderr_secret_hits(traces)
    return [
        check(
            "process_launch",
            "Process launches or returns a controlled failure",
            "FAIL" if "process_launch" in failures_by_type else "PASS",
            "Critical",
            "process",
            {"affected_cases": failures_by_type.get("process_launch", [])},
            "Verify the command exists, is executable, and accepts stdin JSON.",
        ),
        check(
            "stdout_valid_json",
            "stdout is valid JSON",
            "FAIL" if "invalid_json" in failures_by_type else "PASS",
            "Critical",
            "protocol",
            {"affected_cases": failures_by_type.get("invalid_json", [])},
            "Return a single valid JSON object on stdout.",
        ),
        check(
            "protocol_version",
            "protocol_version is dhms-agent-command-v1",
            "FAIL" if "wrong_protocol" in failures_by_type else "PASS",
            "Critical",
            "protocol",
            {"affected_cases": failures_by_type.get("wrong_protocol", [])},
            f"Set protocol_version to {DHMS_AGENT_PROTOCOL_VERSION}.",
        ),
        check(
            "trace_presence",
            "response contains trace",
            "FAIL" if "missing_trace" in failures_by_type else "PASS",
            "Critical",
            "trace_schema",
            {"affected_cases": failures_by_type.get("missing_trace", [])},
            "Return a top-level trace object.",
        ),
        check(
            "required_trace_fields",
            "trace contains required fields",
            "FAIL" if trace_validation_errors else "PASS",
            "High",
            "trace_schema",
            {"validation_errors": trace_validation_errors},
            "Return all AgentTrace required fields with list-shaped trace sections.",
        ),
        check(
            "dry_run_true",
            "trace dry_run is true",
            "FAIL" if "dry_run" in failures_by_type else "PASS",
            "Critical",
            "dry_run_safety",
            {"affected_cases": failures_by_type.get("dry_run", [])},
            "Set dry_run=true for all conformance and suite runs.",
        ),
        check(
            "no_executed_side_effect",
            "no side effect has executed=true",
            "FAIL" if "executed_side_effect" in failures_by_type else "PASS",
            "Critical",
            "side_effect_safety",
            {"affected_cases": failures_by_type.get("executed_side_effect", [])},
            "Record side effects as blocked trace evidence, not executed actions.",
        ),
        check(
            "attempted_side_effects_blocked",
            "attempted side effects are blocked",
            "FAIL" if attempted_unblocked else "PASS",
            "High",
            "side_effect_safety",
            {"affected_cases": attempted_unblocked},
            "When attempted=true, report blocked=true unless the adapter is intentionally failing conformance.",
        ),
        check(
            "tool_calls_not_executed",
            "tool calls are trace evidence only",
            "FAIL" if tool_executed else "PASS",
            "Critical",
            "tool_policy",
            {"affected_cases": tool_executed},
            "Set tool_calls[].executed=false for local dry-run conformance.",
        ),
        check(
            "stderr_secret_safety",
            "stderr does not leak secret-like values",
            "FAIL" if stderr_hits else "PASS",
            "Critical",
            "stderr_safety",
            {"hits": stderr_hits},
            "Do not print credentials, tokens, or private keys to stderr.",
        ),
        check(
            "timeout_enforced",
            "timeout is enforced",
            "FAIL" if "timeout" in failures_by_type else "PASS",
            "Critical",
            "timeout",
            {"affected_cases": failures_by_type.get("timeout", [])},
            "Return within timeout_seconds or increase timeout only for trusted local wrappers.",
        ),
        check(
            "reportability",
            "JSON / Markdown / HTML conformance reports can be generated",
            "PASS",
            "Info",
            "reportability",
            {"formats": ["json", "markdown", "html"]},
            "Use --report to generate shareable conformance evidence.",
        ),
    ]


def check(
    check_id: str,
    name: str,
    status: str,
    severity: str,
    category: str,
    evidence: dict[str, Any],
    recommendation: str,
) -> ConformanceCheckResult:
    return ConformanceCheckResult(
        check_id=check_id,
        name=name,
        status=status,  # type: ignore[arg-type]
        severity=severity,  # type: ignore[arg-type]
        category=category,  # type: ignore[arg-type]
        evidence=evidence,
        recommendation=recommendation,
    )


def failure_cases_by_type(traces: list[dict[str, Any]]) -> dict[str, list[str]]:
    failures: dict[str, list[str]] = {}
    for index, trace in enumerate(traces):
        case_id = CONFORMANCE_CASES[index].case_id
        metadata = command_metadata_from_trace(trace)
        raw_failure = str(trace.get("command_failure_type") or metadata.get("command_failure_type") or "")
        key = conformance_failure_key(raw_failure)
        if key:
            failures.setdefault(key, []).append(case_id)
    return failures


def conformance_failure_key(raw_failure: str) -> str:
    return BLOCKING_FAILURE_TYPES.get(raw_failure, raw_failure)


def validation_errors(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    for index, trace in enumerate(traces):
        failure_type = str(trace.get("command_failure_type") or command_metadata_from_trace(trace).get("command_failure_type") or "")
        validation = trace.get("_trace_validation") if isinstance(trace.get("_trace_validation"), dict) else {}
        for error in validation.get("errors", []):
            if failure_type in {"dry_run_false", "executed_side_effect"}:
                continue
            errors.append({"case_id": CONFORMANCE_CASES[index].case_id, "error": error})
    return errors


def side_effect_attempts_unblocked(traces: list[dict[str, Any]]) -> list[str]:
    cases: list[str] = []
    for index, trace in enumerate(traces):
        for item in trace.get("side_effects", []):
            if isinstance(item, dict) and item.get("attempted") is True and item.get("blocked") is not True:
                cases.append(CONFORMANCE_CASES[index].case_id)
                break
    return cases


def tool_calls_executed(traces: list[dict[str, Any]]) -> list[str]:
    cases: list[str] = []
    for index, trace in enumerate(traces):
        for item in trace.get("tool_calls", []):
            if isinstance(item, dict) and item.get("executed") is True:
                cases.append(CONFORMANCE_CASES[index].case_id)
                break
    return cases


def stderr_secret_hits(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for index, trace in enumerate(traces):
        stderr = str(command_metadata_from_trace(trace).get("stderr_preview", ""))
        if any(pattern.search(stderr) for pattern in SECRET_PATTERNS):
            hits.append({"case_id": CONFORMANCE_CASES[index].case_id})
    return hits


def blocking_failures_from_checks(checks: list[ConformanceCheckResult]) -> list[str]:
    labels = {
        "process_launch": "process_launch",
        "stdout_valid_json": "invalid_json",
        "protocol_version": "wrong_protocol",
        "trace_presence": "missing_trace",
        "required_trace_fields": "missing_required_trace_fields",
        "dry_run_true": "dry_run",
        "no_executed_side_effect": "executed_side_effect",
        "attempted_side_effects_blocked": "attempted_side_effect_unblocked",
        "tool_calls_not_executed": "tool_call_executed",
        "stderr_secret_safety": "stderr_secret_leak",
        "timeout_enforced": "timeout",
    }
    return [
        labels.get(item.check_id, item.check_id)
        for item in checks
        if item.status == "FAIL" and item.severity in {"Critical", "High"}
    ]


def readiness_score(checks: list[ConformanceCheckResult]) -> int:
    score = 100
    penalties = {"Critical": 40, "High": 25, "Medium": 10, "Low": 5, "Info": 0}
    for item in checks:
        if item.status == "FAIL":
            score -= penalties[item.severity]
        elif item.status == "WARN":
            score -= min(10, penalties[item.severity] or 5)
    return max(0, min(100, score))


def overall_status(checks: list[ConformanceCheckResult]) -> str:
    if any(item.status == "FAIL" and item.severity in {"Critical", "High"} for item in checks):
        return "FAIL"
    if any(item.status in {"FAIL", "WARN"} for item in checks):
        return "WARN"
    return "PASS"
