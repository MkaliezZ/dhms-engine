"""Adapter interface for Agent Harness v1."""

from __future__ import annotations

from typing import Protocol

from .trace_schema import AgentRunRequest


class AgentAdapter(Protocol):
    adapter_name: str

    def run(self, request: AgentRunRequest) -> dict:
        """Return an AgentTrace-compatible JSON-serializable dictionary."""
