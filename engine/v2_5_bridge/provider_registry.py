"""Provider registry for DHMS V2.5 bridge."""

from provider_model_parser import parse_api_names, parse_model_spec
from providers.anthropic_adapter import AnthropicModel
from providers.deepseek_adapter import DeepSeekModel
from providers.fallback_adapter import FallbackMockModel
from providers.gemini_adapter import GeminiModel
from providers.kimi_adapter import KimiModel
from providers.mistral_adapter import MistralModel
from providers.openai_adapter import OpenAIModel
from providers.qwen_adapter import QwenModel

PROVIDER_CLASSES = {
    "deepseek": DeepSeekModel,
    "openai": OpenAIModel,
    "anthropic": AnthropicModel,
    "qwen": QwenModel,
    "kimi": KimiModel,
    "gemini": GeminiModel,
    "mistral": MistralModel,
    "fallback": FallbackMockModel,
}


def create_provider_model(spec):
    parsed = parse_model_spec(spec)
    provider = parsed["provider"]
    if provider not in PROVIDER_CLASSES:
        raise ValueError(f"unknown provider: {provider}")
    return PROVIDER_CLASSES[provider](spec)


def create_api_model(spec):
    return create_provider_model(spec)


def provider_names():
    return sorted(PROVIDER_CLASSES.keys())


def parse_api_model_specs(api_models):
    return parse_api_names(api_models)
