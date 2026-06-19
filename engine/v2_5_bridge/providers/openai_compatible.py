"""OpenAI-compatible Chat Completions provider family."""

import os
from typing import Any, Mapping, Optional

from provider_response_parsers import parse_chat_completions, parse_mistral_content
from providers.base import BaseAPIModel


class OpenAICompatibleChatModel(BaseAPIModel):
    provider = "compatible"
    endpoint = ""
    api_key_env = ""
    base_url_env = None
    parser = staticmethod(parse_chat_completions)

    def __init__(self, requested_model_spec: Optional[str] = None) -> None:
        super().__init__(requested_model_spec)
        self.api_key = self._api_key()
        if self.base_url_env and os.environ.get(self.base_url_env):
            self.endpoint = os.environ[self.base_url_env].rstrip("/")
            if not self.endpoint.endswith("/chat/completions"):
                self.endpoint += "/chat/completions"
        self.enabled = bool(self.api_key and self.model_name and not self.failure_mode)

    def _api_key(self) -> str:
        return os.environ.get(self.api_key_env, "")

    def build_payload(self, input_text: str, regime: str, memory_condition: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "DHMS black-box response. Keep the evaluated input fixed; do not infer hidden state."},
                {"role": "user", "content": input_text},
            ],
            "temperature": 0,
        }

    def generate(self, input_text: str, regime: str, memory_condition: Mapping[str, Any]) -> str:
        if not self.model_name:
            return self.unavailable_response(regime, self.failure_mode or "model_not_found_or_not_available")
        if not self.api_key:
            return self.unavailable_response(regime, "api_key_missing")
        payload = self.build_payload(input_text, regime, memory_condition)
        try:
            data = self.post_json(self.endpoint, payload, {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"})
            self.real_api_used = True
            return str(self.parser(data))
        except Exception as exc:
            self.last_error_type = type(exc).__name__
            return self.fallback_response(input_text, regime, memory_condition, "api_failure")


class MistralChatModel(OpenAICompatibleChatModel):
    provider = "mistral"
    endpoint = "https://api.mistral.ai/v1/chat/completions"
    api_key_env = "MISTRAL_API_KEY"
    parser = staticmethod(parse_mistral_content)
