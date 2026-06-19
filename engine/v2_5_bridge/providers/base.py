"""Base provider adapter."""

import hashlib
import json
import os
import urllib.request
from typing import Any, Mapping, Optional

from model_alias_registry import resolve_model
from provider_model_parser import parse_model_spec


class BaseAPIModel:
    name = "base"
    provider = "base"

    def __init__(self, requested_model_spec: Optional[str] = None) -> None:
        parsed = parse_model_spec(requested_model_spec or self.provider)
        self.requested_model_spec = parsed["requested_model_spec"] or self.provider
        self.provider = parsed["provider"] or self.provider
        self.requested_alias = parsed["requested_alias"]
        self.model_name, self.failure_mode = resolve_model(self.provider, self.requested_alias)
        self.enabled = False
        self.fallback_used = False
        self.real_api_used = False
        self.last_error_type = None

    def generate(self, input_text: str, regime: str, memory_condition: Mapping[str, Any]) -> str:
        raise NotImplementedError

    def unavailable_response(self, regime: str, reason: str) -> str:
        self.fallback_used = True
        self.real_api_used = False
        self.failure_mode = reason
        return f"{self.provider}_unavailable[{regime}:{reason}:{self.model_name or 'unresolved'}]"

    def fallback_response(self, input_text: str, regime: str, memory_condition: Mapping[str, Any], reason: str) -> str:
        self.fallback_used = True
        self.real_api_used = False
        self.failure_mode = reason
        label = str(memory_condition.get("state", "unspecified"))
        digest = hashlib.sha256(f"{self.provider}|{self.model_name}|{regime}|{input_text}|{label}".encode("utf-8")).hexdigest()[:12]
        return f"{self.provider}_fallback_response[{regime}:{label}:{digest}:{reason}]"

    def status(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "requested_model_spec": self.requested_model_spec,
            "requested_alias": self.requested_alias,
            "resolved_model_id": self.model_name,
            "enabled": self.enabled,
            "real_api_used": self.real_api_used,
            "fallback_used": self.fallback_used,
            "failure_mode": self.failure_mode,
            "last_error_type": self.last_error_type,
        }

    def post_json(self, endpoint: str, payload: Mapping[str, Any], headers: Mapping[str, str]) -> Mapping[str, Any]:
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=dict(headers),
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
