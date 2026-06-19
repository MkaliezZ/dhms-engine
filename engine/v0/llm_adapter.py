"""Minimal black-box LLM adapter for DHMS Minimal Engine v0."""

import hashlib
import os
from typing import Mapping, Any


class LLMAdapter:
    """Treat the model as pure input/output.

    This adapter intentionally exposes no DHMS semantics. Without an API key it
    returns deterministic mock responses so runs remain reproducible.
    """

    def __init__(self) -> None:
        self.uses_mock = not bool(os.environ.get("OPENAI_API_KEY"))

    def complete(self, *, input_text: str, regime_name: str, memory_condition: Mapping[str, Any]) -> str:
        if self.uses_mock:
            return self._mock_response(input_text, regime_name, memory_condition)
        return self._mock_response(input_text, regime_name, memory_condition)

    def _mock_response(self, input_text: str, regime_name: str, memory_condition: Mapping[str, Any]) -> str:
        memory_label = str(memory_condition.get("state", "unspecified"))
        digest = hashlib.sha256(f"{regime_name}|{input_text}|{memory_label}".encode("utf-8")).hexdigest()[:12]
        return f"mock_llm_response[{regime_name}:{memory_label}:{digest}]"

