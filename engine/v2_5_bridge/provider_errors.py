"""Provider errors for DHMS V2.5 bridge."""

class ProviderError(Exception):
    pass

class ModelUnavailableError(ProviderError):
    pass
