"""Gemini generateContent adapter."""

import os
from typing import Any, Mapping, Optional

from provider_response_parsers import parse_gemini_generate_content
from providers.base import BaseAPIModel


class GeminiModel(BaseAPIModel):
    name = "gemini"
    provider = "gemini"

    def __init__(self, requested_model_spec: Optional[str] = None) -> None:
        super().__init__(requested_model_spec)
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.enabled = bool(self.api_key and self.model_name and not self.failure_mode)

    def generate(self, input_text: str, regime: str, memory_condition: Mapping[str, Any]) -> str:
        if not self.model_name:
            return self.unavailable_response(regime, self.failure_mode or "model_not_found_or_not_available")
        if not self.api_key:
            return self.unavailable_response(regime, "api_key_missing")
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {"contents": [{"parts": [{"text": input_text}]}], "generationConfig": {"temperature": 0}}
        try:
            data = self.post_json(endpoint, payload, {"Content-Type": "application/json"})
            self.real_api_used = True
            return parse_gemini_generate_content(data)
        except Exception as exc:
            self.last_error_type = type(exc).__name__
            return self.fallback_response(input_text, regime, memory_condition, "api_failure")
