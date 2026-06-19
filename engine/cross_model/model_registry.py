"""Model registry for DHMS v2 cross-model execution."""

import hashlib
import json
import os
import urllib.request
from typing import Any, Mapping


class BaseModel:
    name = "base"

    def generate(self, input_text: str, regime: str, memory_condition: Mapping[str, Any]) -> str:
        raise NotImplementedError


class MockModel(BaseModel):
    name = "mock"

    def generate(self, input_text: str, regime: str, memory_condition: Mapping[str, Any]) -> str:
        memory_label = str(memory_condition.get("state", "unspecified"))
        digest = hashlib.sha256(f"mock|{regime}|{input_text}|{memory_label}".encode("utf-8")).hexdigest()[:12]
        return f"mock_response[{regime}:{memory_label}:{digest}]"


class DeterministicFallbackModel(BaseModel):
    name = "fallback"

    def generate(self, input_text: str, regime: str, memory_condition: Mapping[str, Any]) -> str:
        memory_label = str(memory_condition.get("state", "unspecified"))
        digest = hashlib.sha256(f"fallback|{regime}|{input_text}|{memory_label}".encode("utf-8")).hexdigest()[:12]
        return f"fallback_response[{regime}:{memory_label}:{digest}]"


class ExternalAPIModel(BaseModel):
    name = "external"

    def __init__(self) -> None:
        self.api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
        self.endpoint = os.environ.get("DHMS_EXTERNAL_API_URL", "https://api.openai.com/v1/chat/completions")
        self.model_name = os.environ.get("DHMS_EXTERNAL_MODEL", "gpt-4o-mini")
        self.enabled = os.environ.get("DHMS_ENABLE_EXTERNAL_API") == "1" and bool(self.api_key)
        self.fallback = DeterministicFallbackModel()

    def generate(self, input_text: str, regime: str, memory_condition: Mapping[str, Any]) -> str:
        if not self.enabled:
            return self._fallback_response(input_text, regime, memory_condition)
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "Return a concise response to the fixed input."},
                {"role": "user", "content": input_text},
            ],
            "temperature": 0,
        }
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
            return str(data["choices"][0]["message"]["content"])
        except Exception:
            return self._fallback_response(input_text, regime, memory_condition)

    def _fallback_response(self, input_text: str, regime: str, memory_condition: Mapping[str, Any]) -> str:
        base = self.fallback.generate(input_text, regime, memory_condition)
        return base.replace("fallback_response", "external_fallback_response", 1)


MODEL_TYPES = {
    "mock": MockModel,
    "external": ExternalAPIModel,
    "fallback": DeterministicFallbackModel,
}


def create_model(name: str) -> BaseModel:
    key = name.strip().lower()
    if key not in MODEL_TYPES:
        raise ValueError(f"unknown model: {name}")
    return MODEL_TYPES[key]()

