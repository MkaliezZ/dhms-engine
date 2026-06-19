"""DeepSeek adapter."""
from providers.openai_compatible import OpenAICompatibleChatModel

class DeepSeekModel(OpenAICompatibleChatModel):
    name = "deepseek"
    provider = "deepseek"
    endpoint = "https://api.deepseek.com/chat/completions"
    api_key_env = "DEEPSEEK_API_KEY"
