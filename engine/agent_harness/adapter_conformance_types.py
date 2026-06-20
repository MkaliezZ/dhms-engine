"""JSON-serializable result types for Agent Harness adapter conformance."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Literal, Mapping


CheckStatus = Literal["PASS", "WARN", "FAIL"]
Severity = Literal["Critical", "High", "Medium", "Low", "Info"]
CheckCategory = Literal[
    "process",
    "protocol",
    "trace_schema",
    "dry_run_safety",
    "side_effect_safety",
    "tool_policy",
    "stderr_safety",
    "timeout",
    "reportability",
]


@dataclass
class ConformanceCheckResult:
    check_id: str
    name: str
    status: CheckStatus
    severity: Severity
    category: CheckCategory
    evidence: Mapping[str, Any] = field(default_factory=dict)
    recommendation: str = ""


@dataclass
class AdapterConformanceReport:
    conformance_version: str
    adapter_command: str
    protocol_version: str
    overall_status: CheckStatus
    adapter_readiness_score: int
    blocking_failures: list[str]
    warning_count: int
    pass_count: int
    fail_count: int
    check_results: list[Mapping[str, Any]]
    probe_results: list[Mapping[str, Any]]
    generated_at: str
    caveats: list[str]
    report_paths: Mapping[str, str] = field(default_factory=dict)


def to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return to_jsonable(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [to_jsonable(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)
