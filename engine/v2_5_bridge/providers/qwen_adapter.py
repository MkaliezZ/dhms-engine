"""Qwen/DashScope adapter."""
from providers.openai_compatible import OpenAICompatibleChatModel

class QwenModel(OpenAICompatibleChatModel):
    name = "qwen"
    provider = "qwen"
    endpoint = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    api_key_env = "DASHSCOPE_API_KEY"
    base_url_env = "QWEN_BASE_URL"
