"""Public metadata registry for reviewed AgentFuse integration mappings."""

from .model import IntegrationProfile
from .registry import get_integration, list_integrations

__all__ = ["IntegrationProfile", "get_integration", "list_integrations"]
