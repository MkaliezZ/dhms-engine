#!/usr/bin/env python3
"""Static provider conformance checks. No real API calls."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKDIR = Path(__file__).resolve().parents[2]
BRIDGE = WORKDIR / "engine" / "v2_5_bridge"
for rel in (BRIDGE, WORKDIR / "binding", WORKDIR / "engine" / "v0"):
    sys.path.insert(0, str(rel))

from api_adapters import DeepSeekModel, create_api_model, parse_api_names  # noqa: E402
from model_alias_registry import resolve_model  # noqa: E402
from provider_contracts import validate_adapter  # noqa: E402
from provider_model_parser import parse_model_spec  # noqa: E402
from provider_registry import provider_names  # noqa: E402
from provider_response_parsers import (  # noqa: E402
    parse_anthropic_messages,
    parse_chat_completions,
    parse_gemini_generate_content,
    parse_mistral_content,
    parse_openai_responses,
)
from providers.deepseek_adapter import DeepSeekModel as RegistryDeepSeekModel  # noqa: E402

PROVIDERS = ["deepseek", "openai", "anthropic", "qwen", "kimi", "gemini", "mistral", "fallback"]


def main():
    checks = []
    checks.append(check("registry loads all providers", set(PROVIDERS).issubset(set(provider_names()))))
    checks.append(check("provider:model parsing", parse_model_spec("anthropic:sonnet")["provider"] == "anthropic" and parse_model_spec("claude:opus")["provider"] == "anthropic"))
    checks.append(check("provider aliases", parse_model_spec("dashscope:plus")["provider"] == "qwen" and parse_model_spec("moonshot:k2")["provider"] == "kimi"))
    checks.append(check("model aliases", resolve_model("deepseek", "flash")[0] is not None and resolve_model("mistral", "small")[0] == "mistral-small-latest"))
    checks.append(check("direct model passthrough", resolve_model("openai", "gpt-5.5")[0] == "gpt-5.5"))
    checks.append(check("parse_api_names", parse_api_names("mock,deepseek:flash") == ["mock", "deepseek:flash"]))
    for provider in PROVIDERS:
        adapter = create_api_model(provider)
        ok, missing = validate_adapter(adapter)
        checks.append(check(f"{provider} adapter contract", ok, {"missing": missing}))
    checks.append(check("DeepSeek import backward compatibility", DeepSeekModel is RegistryDeepSeekModel))
    checks.append(check("chat parser", parse_chat_completions({"choices":[{"message":{"content":"ok"}}]}) == "ok"))
    checks.append(check("OpenAI responses parser", parse_openai_responses({"output_text":"ok"}) == "ok"))
    checks.append(check("Anthropic parser", parse_anthropic_messages({"content":[{"type":"text","text":"ok"}]}) == "ok"))
    checks.append(check("Gemini parser", parse_gemini_generate_content({"candidates":[{"content":{"parts":[{"text":"ok"}]}}]}) == "ok"))
    checks.append(check("Mistral string parser", parse_mistral_content({"choices":[{"message":{"content":"ok"}}]}) == "ok"))
    checks.append(check("Mistral list parser", parse_mistral_content({"choices":[{"message":{"content":[{"text":"o"},{"text":"k"}]}}]}) == "ok"))
    unavailable = create_api_model("openai:mini")
    checks.append(check("unavailable alias explicit", unavailable.model_name is None and unavailable.failure_mode == "model_not_found_or_not_available"))
    status = "PASS" if all(item["passed"] for item in checks) else "FAIL"
    result = {"validation_name":"DHMS Provider Static Conformance", "status":status, "timestamp":datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "checks":checks}
    out = WORKDIR / "validation/provider_conformance/outputs/provider_conformance_report.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    md = WORKDIR / "validation/provider_conformance/outputs/provider_conformance_report.md"
    md.write_text(to_markdown(result), encoding="utf-8")
    print(json.dumps({"status": status, "checks": len(checks), "report": str(out.relative_to(WORKDIR))}, indent=2))
    return 0 if status == "PASS" else 1


def check(name, passed, extra=None):
    return {"name": name, "passed": bool(passed), "extra": extra or {}}


def to_markdown(result):
    lines = ["# DHMS Provider Static Conformance", "", f"Status: {result['status']}", ""]
    for item in result["checks"]:
        mark = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- {mark}: {item['name']}")
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    raise SystemExit(main())
