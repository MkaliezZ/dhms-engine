"""Mistral adapter."""
from providers.openai_compatible import MistralChatModel

class MistralModel(MistralChatModel):
    name = "mistral"
