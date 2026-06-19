"""Backward-compatible API adapter exports for DHMS V2.5 bridge."""

from provider_model_parser import parse_api_names
from provider_registry import create_api_model
from providers.anthropic_adapter import AnthropicModel as ClaudeModel
from providers.deepseek_adapter import DeepSeekModel
from providers.fallback_adapter import FallbackMockModel
from providers.gemini_adapter import GeminiModel
from providers.kimi_adapter import KimiModel
from providers.mistral_adapter import MistralModel
from providers.openai_adapter import OpenAIModel
from providers.qwen_adapter import QwenModel
from providers.base import BaseAPIModel

API_MODELS = {
    "deepseek": DeepSeekModel,
    "openai": OpenAIModel,
    "anthropic": ClaudeModel,
    "claude": ClaudeModel,
    "qwen": QwenModel,
    "dashscope": QwenModel,
    "kimi": KimiModel,
    "moonshot": KimiModel,
    "gemini": GeminiModel,
    "mistral": MistralModel,
    "fallback": FallbackMockModel,
    "fallback_mock": FallbackMockModel,
}
