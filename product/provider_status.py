"""Provider status and doctor output."""

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BRIDGE = ROOT / "engine" / "v2_5_bridge"
if str(BRIDGE) not in sys.path:
    sys.path.insert(0, str(BRIDGE))
from model_alias_registry import alias_table, resolve_model  # noqa: E402
from provider_model_parser import PROVIDER_ALIASES  # noqa: E402
from provider_specs import PROVIDER_SPECS  # noqa: E402

PROVIDERS = ["deepseek", "openai", "anthropic", "qwen", "kimi", "gemini", "mistral", "fallback"]


def provider_statuses() -> list[dict[str, Any]]:
    return [provider_status(provider) for provider in PROVIDERS]


def provider_status(provider: str) -> dict[str, Any]:
    spec = PROVIDER_SPECS[provider]
    aliases = sorted([alias for alias, target in PROVIDER_ALIASES.items() if target == provider and alias != provider])
    alias_keys = sorted([str(k) for k in alias_table().get(provider, {}).keys() if k is not None])
    key = key_present(spec.get("api_key_env", ""))
    live = live_verified(provider)
    if provider == "fallback":
        status = "fallback_only"
    elif live:
        status = "live_verified"
    elif key:
        status = "adapter_ready_byok"
    else:
        status = "key_missing"
    default_model, _ = resolve_model(provider, None)
    return {
        "provider": provider,
        "aliases": aliases,
        "key_present": key,
        "default_model": default_model,
        "available_model_aliases": alias_keys,
        "live_verified": live,
        "static_conformance_covered": conformance_passed(),
        "status": status,
    }


def key_present(env_decl: str) -> bool:
    if not env_decl:
        return False
    for name in env_decl.split("|"):
        if name and os.environ.get(name):
            return True
    return False


def live_verified(provider: str) -> bool:
    base = ROOT / "validation/provider_smoke/outputs"
    if not base.exists():
        return False
    for report in base.glob(f"{provider}_*/provider_smoke_report.json"):
        try:
            data = json.loads(report.read_text())
        except Exception:
            continue
        if data.get("status") == "PASS" and data.get("real_api_used") is True:
            return True
    return False


def conformance_passed() -> bool:
    path = ROOT / "validation/provider_conformance/outputs/provider_conformance_report.json"
    if not path.exists():
        return False
    try:
        return json.loads(path.read_text()).get("status") == "PASS"
    except Exception:
        return False


def models_for(provider=None) -> dict[str, Any]:
    table = alias_table()
    if provider:
        return {provider: sorted([str(k) for k in table.get(provider, {}) if k is not None])}
    return {name: sorted([str(k) for k in aliases if k is not None]) for name, aliases in table.items()}


def format_status_table(statuses: list[dict[str, Any]]) -> str:
    lines = ["provider | status | key_present | live_verified | default_model | aliases", "---|---|---|---|---|---"]
    for item in statuses:
        lines.append(f"{item['provider']} | {item['status']} | {item['key_present']} | {item['live_verified']} | {item['default_model']} | {', '.join(item['available_model_aliases'])}")
    return "\n".join(lines)
