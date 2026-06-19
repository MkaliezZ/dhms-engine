"""Local fallback adapter."""
from typing import Any, Mapping, Optional
from providers.base import BaseAPIModel

class FallbackMockModel(BaseAPIModel):
    name = "fallback"
    provider = "fallback"
    def __init__(self, requested_model_spec: Optional[str] = None) -> None:
        super().__init__(requested_model_spec or "fallback")
        self.enabled = True
    def generate(self, input_text: str, regime: str, memory_condition: Mapping[str, Any]) -> str:
        return self.fallback_response(input_text, regime, memory_condition, "local_fallback")
