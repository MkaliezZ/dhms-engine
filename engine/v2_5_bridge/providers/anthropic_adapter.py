"""Anthropic Messages API adapter."""

import os
from typing import Any, Mapping, Optional

from provider_response_parsers import parse_anthropic_messages
from providers.base import BaseAPIModel


class AnthropicModel(BaseAPIModel):
    name = "anthropic"
    provider = "anthropic"
    endpoint = "https://api.anthropic.com/v1/messages"

    def __init__(self, requested_model_spec: Optional[str] = None) -> None:
        super().__init__(requested_model_spec)
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.version = os.environ.get("ANTHROPIC_VERSION", "2023-06-01")
        self.enabled = bool(self.api_key and self.model_name and not self.failure_mode)

    def generate(self, input_text: str, regime: str, memory_condition: Mapping[str, Any]) -> str:
        if not self.model_name:
            return self.unavailable_response(regime, self.failure_mode or "model_not_found_or_not_available")
        if not self.api_key:
            return self.unavailable_response(regime, "api_key_missing")
        payload = {"model": self.model_name, "max_tokens": 512, "temperature": 0, "messages": [{"role": "user", "content": input_text}]}
        headers = {"x-api-key": self.api_key, "anthropic-version": self.version, "Content-Type": "application/json"}
        try:
            data = self.post_json(self.endpoint, payload, headers)
            self.real_api_used = True
            return parse_anthropic_messages(data)
        except Exception as exc:
            self.last_error_type = type(exc).__name__
            return self.fallback_response(input_text, regime, memory_condition, "api_failure")
