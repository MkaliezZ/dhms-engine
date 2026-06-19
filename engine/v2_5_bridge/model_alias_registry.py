"""Provider model alias resolution."""

import os

_ALIAS = {
    "deepseek": {
        None: ("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        "default": ("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        "flash": ("DEEPSEEK_FLASH_MODEL", "deepseek-v4-flash"),
        "pro": ("DEEPSEEK_PRO_MODEL", "deepseek-v4-pro"),
    },
    "openai": {
        None: ("OPENAI_MODEL", "gpt-5.5"),
        "latest": ("OPENAI_MODEL", "gpt-5.5"),
        "mini": ("OPENAI_MINI_MODEL", None),
    },
    "anthropic": {
        None: ("ANTHROPIC_MODEL", "claude-sonnet-4-5"),
        "sonnet": ("ANTHROPIC_SONNET_MODEL", "claude-sonnet-4-5"),
        "opus": ("ANTHROPIC_OPUS_MODEL", None),
        "haiku": ("ANTHROPIC_HAIKU_MODEL", "claude-3-5-haiku-latest"),
    },
    "qwen": {
        None: ("QWEN_MODEL", "qwen-plus"),
        "plus": ("QWEN_PLUS_MODEL", "qwen-plus"),
        "turbo": ("QWEN_TURBO_MODEL", None),
    },
    "kimi": {
        None: ("KIMI_MODEL", "kimi-k2.7-code"),
        "k2": ("KIMI_K2_MODEL", "kimi-k2.7-code"),
    },
    "gemini": {
        None: ("GEMINI_MODEL", "gemini-2.5-flash"),
        "flash": ("GEMINI_FLASH_MODEL", "gemini-2.5-flash"),
        "pro": ("GEMINI_PRO_MODEL", None),
    },
    "mistral": {
        None: ("MISTRAL_MODEL", "mistral-small-latest"),
        "small": ("MISTRAL_SMALL_MODEL", "mistral-small-latest"),
        "medium": ("MISTRAL_MEDIUM_MODEL", None),
        "large": ("MISTRAL_LARGE_MODEL", None),
    },
    "fallback": {None: (None, "fallback_mock")},
}


def resolve_model(provider, requested_alias):
    aliases = _ALIAS.get(provider, {})
    key = requested_alias if requested_alias in aliases else None
    if requested_alias and requested_alias not in aliases:
        return requested_alias, None
    env_name, default = aliases.get(key, (None, None))
    if env_name and os.environ.get(env_name):
        return os.environ[env_name], None
    if default:
        return default, None
    return None, "model_not_found_or_not_available"


def alias_table():
    return _ALIAS
