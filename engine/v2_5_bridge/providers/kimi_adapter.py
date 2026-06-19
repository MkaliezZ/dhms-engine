"""Kimi/Moonshot adapter."""
import os
from providers.openai_compatible import OpenAICompatibleChatModel

class KimiModel(OpenAICompatibleChatModel):
    name = "kimi"
    provider = "kimi"
    endpoint = "https://api.moonshot.ai/v1/chat/completions"
    api_key_env = "KIMI_API_KEY"
    base_url_env = "KIMI_BASE_URL"

    def _api_key(self):
        return os.environ.get("KIMI_API_KEY") or os.environ.get("MOONSHOT_API_KEY", "")
