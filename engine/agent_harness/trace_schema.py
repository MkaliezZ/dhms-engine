"""JSON-serializable trace schema for Agent Harness v1 phase 1."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Literal, Mapping


Mode = Literal["A", "B", "C"]
TRACE_VERSION = "agent_harness_trace_v1_phase1"


@dataclass
class AgentRunRequest:
    input_text: str
    mode: Mode
    memory_condition: Mapping[str, Any] = field(default_factory=dict)
    context_condition: Mapping[str, Any] = field(default_factory=dict)
    tool_state_condition: Mapping[str, Any] = field(default_factory=dict)
    dry_run: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class ToolCallTrace:
    tool_name: str
    arguments: Mapping[str, Any] = field(default_factory=dict)
    intent: str = ""
    executed: bool = False
    blocked: bool = True
    reason: str = "phase1_dry_run"


@dataclass
class MemoryTrace:
    key: str
    value_preview: str
    source: str
    confidence: str
    freshness: str
    used_in_answer: bool


@dataclass
class StateTransitionTrace:
    from_state: str
    to_state: str
    reason: str


@dataclass
class SideEffectRecord:
    type: str
    target: str
    attempted: bool
    blocked: bool
    reason: str


@dataclass
class AgentTrace:
    final_answer: str
    tool_calls: list[Mapping[str, Any]] = field(default_factory=list)
    memory_reads: list[Mapping[str, Any]] = field(default_factory=list)
    state_transitions: list[Mapping[str, Any]] = field(default_factory=list)
    side_effects: list[Mapping[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    adapter_name: str = "mock"
    dry_run: bool = True
    mode: Mode = "B"
    input_preserved: bool = True
    trace_version: str = TRACE_VERSION


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
