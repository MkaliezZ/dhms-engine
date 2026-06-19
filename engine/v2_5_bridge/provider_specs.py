"""Provider specs for DHMS V2.5 bridge."""

PROVIDER_SPECS = {
    "deepseek": {"style": "openai_chat", "endpoint": "https://api.deepseek.com/chat/completions", "api_key_env": "DEEPSEEK_API_KEY", "model_env": "DEEPSEEK_MODEL", "auth": "Authorization: Bearer", "docs_verified_live": True},
    "openai": {"style": "openai_responses", "endpoint": "https://api.openai.com/v1/responses", "api_key_env": "OPENAI_API_KEY", "model_env": "OPENAI_MODEL", "auth": "Authorization: Bearer", "docs_verified_live": True},
    "anthropic": {"style": "anthropic_messages", "endpoint": "https://api.anthropic.com/v1/messages", "api_key_env": "ANTHROPIC_API_KEY", "model_env": "ANTHROPIC_MODEL", "auth": "x-api-key", "docs_verified_live": True},
    "qwen": {"style": "openai_chat", "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions", "api_key_env": "DASHSCOPE_API_KEY", "model_env": "QWEN_MODEL", "auth": "Authorization: Bearer", "docs_verified_live": True},
    "kimi": {"style": "openai_chat", "endpoint": "https://api.moonshot.ai/v1/chat/completions", "api_key_env": "KIMI_API_KEY|MOONSHOT_API_KEY", "model_env": "KIMI_MODEL", "auth": "Authorization: Bearer", "docs_verified_live": True},
    "gemini": {"style": "gemini_generate_content", "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", "api_key_env": "GEMINI_API_KEY", "model_env": "GEMINI_MODEL", "auth": "key query param", "docs_verified_live": True},
    "mistral": {"style": "openai_chat", "endpoint": "https://api.mistral.ai/v1/chat/completions", "api_key_env": "MISTRAL_API_KEY", "model_env": "MISTRAL_MODEL", "auth": "Authorization: Bearer", "docs_verified_live": True},
    "fallback": {"style": "local", "endpoint": "local", "api_key_env": "", "model_env": "", "auth": "none", "docs_verified_live": False},
}
