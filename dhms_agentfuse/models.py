"""Minimal in-memory models for the DHMS AgentFuse API skeleton.

These objects describe integration shape only. They do not execute tools,
perform IO, create sandboxes, or connect to agent runtimes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


PROTOCOL_VERSION = "v0.6.0"
TOOL_FAMILY = "DHMS AgentFuse"
POLICY_FAMILY = "DHMS AgentFuse Minimal API"

DECISIONS = {
    "BLOCK",
    "FAIL_CLOSED",
    "SANDBOX_HELD",
    "ALLOWLIST_CANDIDATE_HELD",
}

GATE_STATES = {
    "CLOSED",
    "FAIL_CLOSED",
    "HELD_FOR_REVIEW",
    "HELD_FOR_SANDBOX_BRIDGE",
}


@dataclass(frozen=True)
class RuntimeRequest:
    request_id: str
    source: str
    intent_summary: str
    raw_event: Any
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ToolCallProposal:
    proposal_id: str
    request_id: str
    tool_name: str
    tool_type: str
    requested_effect: str
    payload: Any
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SafetyDecision:
    decision_id: str
    proposal_id: str
    decision: str
    reason: str
    release_eligible: bool
    direct_execution_allowed: bool
    policy_family: str = POLICY_FAMILY
    protocol_version: str = PROTOCOL_VERSION

    def __post_init__(self) -> None:
        if self.decision not in DECISIONS:
            raise ValueError(f"unknown safety decision: {self.decision}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExecutionGateDecision:
    gate_id: str
    proposal_id: str
    gate_state: str
    reason: str
    execution_allowed: bool
    requires_review: bool

    def __post_init__(self) -> None:
        if self.gate_state not in GATE_STATES:
            raise ValueError(f"unknown gate state: {self.gate_state}")
        if self.execution_allowed:
            raise ValueError("v0.6.3 skeleton cannot allow execution")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentFuseTrace:
    trace_id: str
    request: RuntimeRequest
    proposal: ToolCallProposal
    safety_decision: SafetyDecision
    gate_decision: ExecutionGateDecision
    executed: bool
    execution_result: None
    protocol_version: str = PROTOCOL_VERSION
    tool_family: str = TOOL_FAMILY

    def __post_init__(self) -> None:
        if self.executed:
            raise ValueError("v0.6.3 skeleton traces must remain non-executing")
        if self.execution_result is not None:
            raise ValueError("v0.6.3 skeleton traces cannot contain execution results")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
