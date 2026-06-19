#!/usr/bin/env python3
"""Bounded live provider smoke runner."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKDIR = Path(__file__).resolve().parents[2]
ENGINE = WORKDIR / "engine"
for rel in (ENGINE / "v2_5_bridge", ENGINE / "v2_cross_model", ENGINE / "v0", ENGINE / "v1", ENGINE / "cross_model", ENGINE / "statistics", WORKDIR / "binding"):
    sys.path.insert(0, str(rel))

from provider_model_parser import parse_model_spec  # noqa: E402
from provider_specs import PROVIDER_SPECS  # noqa: E402
from v25_bridge_runner import run_v25_bridge  # noqa: E402

HARD_CAP = 9
REGIME_CALLS = 3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model")
    parser.add_argument("--n", type=int, default=1)
    parser.add_argument("--max-real-api-calls", type=int, default=3)
    args = parser.parse_args()
    provider = parse_model_spec(args.provider)["provider"]
    model_spec = f"{provider}:{args.model}" if args.model else provider
    parsed = parse_model_spec(model_spec)
    max_calls = min(args.max_real_api_calls, HARD_CAP)
    planned = args.n * REGIME_CALLS
    out_dir = WORKDIR / "validation/provider_smoke/outputs" / f"{provider}_{args.model or 'default'}"
    out_dir.mkdir(parents=True, exist_ok=True)
    spec = PROVIDER_SPECS.get(provider, {})
    api_key_present = key_present(spec.get("api_key_env", ""))
    if not api_key_present:
        result = base_result(provider, args.model, None, "SKIPPED", False, False, 0, max_calls, ["api_key_missing"])
        write(out_dir, result)
        print_summary(result, out_dir)
        return 0
    if planned > max_calls:
        result = base_result(provider, args.model, None, "FAIL", True, False, 0, max_calls, ["real_api_call_cap_exceeded_before_execution"])
        write(out_dir, result)
        print_summary(result, out_dir)
        return 1
    try:
        payload = run_v25_bridge("B", "Provider smoke test: answer in one concise sentence.", n=args.n, models="mock", api_models=model_spec)
        real = payload.get("real_api_results", {})
        model_result = next(iter(real.values())) if real else {}
        status_obj = model_result.get("provider_status", {})
        fallback = bool(status_obj.get("fallback_used"))
        real_used = bool(status_obj.get("real_api_used"))
        failure_modes = []
        if status_obj.get("failure_mode"):
            failure_modes.append(status_obj["failure_mode"])
        status = "PASS" if real_used and not fallback else "PARTIAL" if fallback else "FAIL"
        result = base_result(provider, args.model, status_obj.get("resolved_model_id"), status, True, real_used, planned if real_used else 0, max_calls, failure_modes)
        result.update({
            "fallback_used": fallback,
            "requested_model_spec": status_obj.get("requested_model_spec", model_spec),
            "requested_alias": status_obj.get("requested_alias"),
            "v2_metrics_overridden": payload.get("cross_model_real_world_comparison", {}).get("schema_compatibility", {}).get("v2_metrics_overridden", False),
            "drift_analysis_present": "drift_analysis" in payload,
            "noise_estimation_present": "noise_estimation" in payload,
            "response_snippet": response_snippet(model_result),
        })
    except Exception as exc:
        result = base_result(provider, args.model, None, "FAIL", True, False, 0, max_calls, [type(exc).__name__])
    write(out_dir, result)
    print_summary(result, out_dir)
    return 0 if result["status"] in {"PASS", "SKIPPED", "PARTIAL"} else 1


def key_present(env_decl):
    if not env_decl:
        return True
    for name in env_decl.split("|"):
        if name and os.environ.get(name):
            return True
    return False


def base_result(provider, requested_model, resolved, status, key, real, calls, max_calls, failures):
    return {
        "provider": provider,
        "requested_model": requested_model,
        "resolved_model_id": resolved,
        "status": status,
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "api_key_present": key,
        "real_api_used": real,
        "fallback_used": False,
        "total_real_api_calls": calls,
        "max_real_api_calls": max_calls,
        "v2_metrics_overridden": False,
        "drift_analysis_present": False,
        "noise_estimation_present": False,
        "failure_modes": failures,
        "recommendation": recommend(status, failures),
    }


def recommend(status, failures):
    if status == "PASS":
        return "Provider live smoke passed."
    if "api_key_missing" in failures:
        return "Configure provider API key then rerun smoke test."
    return "Inspect provider adapter/model availability then rerun smoke test."


def response_snippet(model_result):
    try:
        response = model_result["per_run_results"][0]["regime_results"]["DHMS-B"].get("raw_response") or model_result["per_run_results"][0]["regime_results"]["DHMS-B"].get("response")
        return str(response).replace("\n", " ")[:180]
    except Exception:
        return ""


def write(out_dir, result):
    (out_dir / "provider_smoke_report.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    lines = ["# DHMS Provider Smoke Report", "", f"Status: {result['status']}", f"Provider: {result['provider']}", f"Requested model: {result.get('requested_model')}", f"Resolved model: {result.get('resolved_model_id')}", f"Real API used: {result['real_api_used']}", f"Fallback used: {result['fallback_used']}", f"Failure modes: {', '.join(result['failure_modes']) or 'none'}", ""]
    (out_dir / "provider_smoke_report.md").write_text("\n".join(lines), encoding="utf-8")


def print_summary(result, out_dir):
    print(json.dumps({"status": result["status"], "provider": result["provider"], "real_api_used": result["real_api_used"], "fallback_used": result["fallback_used"], "report": str(out_dir.relative_to(WORKDIR))}, indent=2, sort_keys=True))

if __name__ == "__main__":
    raise SystemExit(main())
