"""Provider/model selection parsing."""

PROVIDER_ALIASES = {
    "claude": "anthropic",
    "anthropic": "anthropic",
    "dashscope": "qwen",
    "qwen": "qwen",
    "moonshot": "kimi",
    "kimi": "kimi",
    "fallback_mock": "fallback",
}


def parse_model_spec(spec):
    raw = (spec or "").strip().lower()
    if not raw:
        return {"requested_model_spec": "", "provider": "", "requested_alias": None, "requested_model": None}
    if ":" in raw:
        provider, requested = raw.split(":", 1)
        requested = requested.strip() or None
    else:
        provider, requested = raw, None
    provider = PROVIDER_ALIASES.get(provider.strip(), provider.strip())
    return {
        "requested_model_spec": raw,
        "provider": provider,
        "requested_alias": requested,
        "requested_model": requested,
    }


def parse_api_names(api_models):
    return [item.strip() for item in (api_models or "").split(",") if item.strip()]
