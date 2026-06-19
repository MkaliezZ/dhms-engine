"""Provider adapter contract checks."""

REQUIRED_ATTRS = ["name", "provider", "requested_model_spec", "requested_alias", "model_name", "enabled"]


def validate_adapter(adapter):
    missing = [name for name in REQUIRED_ATTRS if not hasattr(adapter, name)]
    if missing:
        return False, missing
    if not callable(getattr(adapter, "generate", None)):
        return False, ["generate"]
    return True, []
