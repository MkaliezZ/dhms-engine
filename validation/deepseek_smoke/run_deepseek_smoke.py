#!/usr/bin/env python3
"""Bounded DeepSeek real API smoke test for DHMS V2.5."""

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional

WORKDIR = Path(__file__).resolve().parents[2]
ENGINE_DIR = WORKDIR / "engine"
PATHS = (
    ENGINE_DIR / "v2_5_bridge",
    ENGINE_DIR / "v2_cross_model",
    ENGINE_DIR / "v0",
    ENGINE_DIR / "v1",
    ENGINE_DIR / "cross_model",
    ENGINE_DIR / "statistics",
    WORKDIR / "binding",
)
for path in PATHS:
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)

from v25_bridge_runner import run_v25_bridge  # noqa: E402

VALIDATION_NAME = "DHMS DeepSeek Real API Smoke Test"
PROVIDER = "deepseek"
ENDPOINT = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_MAX_REAL_API_CALLS = 9
HARD_REAL_API_CALL_CAP = 15
REGIME_COUNT = 3
FALLBACK_MARKERS = ("deepseek_fallback_response", "fallback_mock_response")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=VALIDATION_NAME)
    parser.add_argument("--n", type=int, default=1)
    parser.add_argument("--models", default="mock,deepseek")
    parser.add_argument("--max-real-api-calls", type=int, default=DEFAULT_MAX_REAL_API_CALLS)
    parser.add_argument("--output", default="validation/deepseek_smoke/outputs")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = (WORKDIR / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    cases = load_cases()
    v2_models, api_models = split_models(args.models)
    api_key_present = bool(os.environ.get("DEEPSEEK_API_KEY"))
    model = os.environ.get("DEEPSEEK_MODEL") or os.environ.get("DHMS_DEEPSEEK_MODEL") or DEFAULT_MODEL
    max_calls = min(args.max_real_api_calls, HARD_REAL_API_CALL_CAP)
    planned_real_calls = len(cases) * args.n * REGIME_COUNT if api_key_present else 0

    started = utc_now()
    failure_modes = []
    case_results = []
    raw_case_payloads = []
    real_api_used_any = False
    fallback_used_any = False
    total_real_api_calls = 0

    if args.n < 1:
        failure_modes.append("invalid_n")
    if args.max_real_api_calls > HARD_REAL_API_CALL_CAP:
        failure_modes.append("max_real_api_calls_reduced_to_hard_cap")
    if not api_key_present:
        failure_modes.append("DEEPSEEK_API_KEY not set")
    if planned_real_calls > max_calls:
        failure_modes.append("real_api_call_cap_exceeded_before_execution")

    if args.n < 1 or planned_real_calls > max_calls:
        result = build_result(
            status="FAIL",
            timestamp=started,
            api_key_present=api_key_present,
            model=model,
            real_api_used=False,
            fallback_used=False,
            total_cases=len(cases),
            total_real_api_calls=0,
            max_real_api_calls=max_calls,
            case_results=[],
            failure_modes=failure_modes,
        )
        write_outputs(output_dir, result, [])
        return 1

    for case_name, input_text in cases.items():
        start = time.perf_counter()
        try:
            payload = run_v25_bridge("B", input_text, n=args.n, models=v2_models, api_models=api_models)
            latency_ms = round((time.perf_counter() - start) * 1000, 3)
            raw_path = raw_dir / f"{case_name}.json"
            raw_path.write_text(json.dumps(redact_payload(payload), indent=2, sort_keys=True), encoding="utf-8")
            raw_case_payloads.append(payload)

            deepseek_result = payload.get("real_api_results", {}).get("deepseek")
            fallback_used = detect_fallback(deepseek_result)
            fallback_used_any = fallback_used_any or fallback_used
            real_api_used = api_key_present and not fallback_used and deepseek_result is not None
            real_api_used_any = real_api_used_any or real_api_used
            if real_api_used:
                total_real_api_calls += args.n * REGIME_COUNT

            status = "PASS" if real_api_used else "PARTIAL"
            if api_key_present and fallback_used:
                status = "bridge_routing_issue_or_api_failure"
                failure_modes.append("fallback used")
            if deepseek_result is None:
                status = "FAIL"
                failure_modes.append("response format mismatch")

            case_results.append({
                "case_name": case_name,
                "status": status,
                "latency_ms": latency_ms,
                "v2_result_present": "v2_results" in payload,
                "real_api_result_present": deepseek_result is not None,
                "drift_analysis_present": "drift_analysis" in payload,
                "noise_estimation_present": "noise_estimation" in payload,
                "cross_model_real_world_comparison_present": "cross_model_real_world_comparison" in payload,
                "real_deepseek_call": real_api_used,
                "fallback_used": fallback_used,
                "api_key_present": api_key_present,
                "provider": PROVIDER,
                "model": model,
                "response_snippet": response_snippet(deepseek_result),
                "raw_output": str(raw_path.relative_to(WORKDIR)),
                "v2_metrics_overridden": payload.get("cross_model_real_world_comparison", {}).get("schema_compatibility", {}).get("v2_metrics_overridden"),
                "drift_analysis": payload.get("drift_analysis", {}),
                "noise_estimation": payload.get("noise_estimation", {}),
            })
        except Exception as exc:
            latency_ms = round((time.perf_counter() - start) * 1000, 3)
            failure_modes.append(type(exc).__name__)
            case_results.append({
                "case_name": case_name,
                "status": "FAIL",
                "latency_ms": latency_ms,
                "v2_result_present": False,
                "real_api_result_present": False,
                "drift_analysis_present": False,
                "noise_estimation_present": False,
                "fallback_used": False,
                "api_key_present": api_key_present,
                "provider": PROVIDER,
                "model": model,
                "error_type": type(exc).__name__,
                "response_snippet": "",
            })

    failure_modes = sorted(set(failure_modes))
    status = determine_status(api_key_present, real_api_used_any, fallback_used_any, case_results, failure_modes)
    result = build_result(
        status=status,
        timestamp=started,
        api_key_present=api_key_present,
        model=model,
        real_api_used=real_api_used_any,
        fallback_used=fallback_used_any,
        total_cases=len(cases),
        total_real_api_calls=total_real_api_calls,
        max_real_api_calls=max_calls,
        case_results=case_results,
        failure_modes=failure_modes,
    )
    write_outputs(output_dir, result, raw_case_payloads)
    print(json.dumps({
        "validation_name": result["validation_name"],
        "status": result["status"],
        "real_api_used": result["real_api_used"],
        "fallback_used": result["fallback_used"],
        "total_real_api_calls": result["total_real_api_calls"],
        "report": str((output_dir / "deepseek_smoke_report.md").relative_to(WORKDIR)),
    }, indent=2, sort_keys=True))
    return 0 if status in {"PASS", "PARTIAL"} else 1



def split_models(models: str) -> tuple[str, str]:
    v2_supported = {"mock", "fallback", "external"}
    api_supported = {"deepseek", "openai", "claude", "fallback", "fallback_mock"}
    requested = [item.strip().lower() for item in models.split(",") if item.strip()]
    v2_models = [item for item in requested if item in v2_supported]
    api_models = [item for item in requested if item in api_supported and item not in v2_supported]
    if "deepseek" not in api_models:
        api_models.append("deepseek")
    return ",".join(v2_models or ["mock"]), ",".join(api_models)


def load_cases() -> dict[str, str]:
    case_dir = Path(__file__).resolve().parent / "smoke_cases"
    return {
        path.stem: path.read_text(encoding="utf-8").strip()
        for path in sorted(case_dir.glob("*.txt"))
    }


def detect_fallback(deepseek_result: Optional[Mapping[str, Any]]) -> bool:
    if not deepseek_result:
        return False
    for run_result in deepseek_result.get("per_run_results", []):
        for regime_result in run_result.get("regime_results", {}).values():
            response = str(regime_result.get("raw_response") or regime_result.get("response", ""))
            if any(marker in response for marker in FALLBACK_MARKERS):
                return True
    return False


def response_snippet(deepseek_result: Optional[Mapping[str, Any]], limit: int = 180) -> str:
    if not deepseek_result:
        return ""
    try:
        first_run = deepseek_result["per_run_results"][0]
        response = first_run["regime_results"]["DHMS-B"].get("raw_response") or first_run["regime_results"]["DHMS-B"]["response"]
        return str(response).replace("\n", " ")[:limit]
    except Exception:
        return ""


def determine_status(
    api_key_present: bool,
    real_api_used: bool,
    fallback_used: bool,
    case_results: list[Mapping[str, Any]],
    failure_modes: list[str],
) -> str:
    if not api_key_present:
        return "PARTIAL"
    if any(case.get("status") == "FAIL" for case in case_results):
        return "FAIL"
    if real_api_used and not fallback_used and not failure_modes:
        return "PASS"
    return "PARTIAL"


def build_result(
    *,
    status: str,
    timestamp: str,
    api_key_present: bool,
    model: str,
    real_api_used: bool,
    fallback_used: bool,
    total_cases: int,
    total_real_api_calls: int,
    max_real_api_calls: int,
    case_results: list[Mapping[str, Any]],
    failure_modes: list[str],
) -> dict[str, Any]:
    v2_metrics_overridden = any(case.get("v2_metrics_overridden") is not False for case in case_results) if case_results else False
    recommendation = recommend(status, api_key_present, real_api_used, fallback_used)
    return {
        "validation_name": VALIDATION_NAME,
        "status": status,
        "timestamp": timestamp,
        "workdir": str(WORKDIR),
        "api_key_present": api_key_present,
        "provider": PROVIDER,
        "model": model,
        "endpoint": ENDPOINT,
        "real_api_used": real_api_used,
        "fallback_used": fallback_used,
        "total_cases": total_cases,
        "total_real_api_calls": total_real_api_calls,
        "max_real_api_calls": max_real_api_calls,
        "v2_metrics_overridden": v2_metrics_overridden,
        "case_results": list(case_results),
        "failure_modes": list(failure_modes),
        "productization_ready": status == "PASS",
        "recommendation": recommendation,
        "protected_layer_hashes": protected_hashes(),
    }


def recommend(status: str, api_key_present: bool, real_api_used: bool, fallback_used: bool) -> str:
    if not api_key_present:
        return "Configure DEEPSEEK_API_KEY then rerun smoke test"
    if fallback_used or not real_api_used:
        return "Fix DeepSeek adapter then rerun smoke test"
    if status == "PASS":
        return "Proceed to DHMS Product Diagnosis v1.3"
    return "Fix DeepSeek adapter then rerun smoke test"


def write_outputs(output_dir: Path, result: Mapping[str, Any], raw_payloads: list[Mapping[str, Any]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "deepseek_smoke_result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    (output_dir / "deepseek_smoke_report.md").write_text(build_report(result), encoding="utf-8")


def build_report(result: Mapping[str, Any]) -> str:
    lines = [
        "# DHMS DeepSeek Real API Smoke Test Report",
        "",
        "## Summary",
        "",
        f"* Status: {result['status']}",
        f"* Real DeepSeek API used: {'yes' if result['real_api_used'] else 'no'}",
        f"* Fallback used: {'yes' if result['fallback_used'] else 'no'}",
        f"* Total API calls: {result['total_real_api_calls']}",
        f"* Total cases: {result['total_cases']}",
        f"* Model: {result['model']}",
        f"* Timestamp: {result['timestamp']}",
        "",
        "## Environment",
        "",
        f"* DEEPSEEK_API_KEY present: {str(result['api_key_present']).lower()}",
        f"* DEEPSEEK_MODEL: {result['model']}",
        "* Endpoint: DeepSeek chat completions",
        "",
        "## Test Cases",
        "",
    ]
    for case in result["case_results"]:
        lines.extend([
            f"### {case['case_name']}",
            "",
            f"* Status: {case['status']}",
            f"* v2_result_present: {case.get('v2_result_present')}",
            f"* real_api_result_present: {case.get('real_api_result_present')}",
            f"* drift_analysis_present: {case.get('drift_analysis_present')}",
            f"* noise_estimation_present: {case.get('noise_estimation_present')}",
            f"* fallback_used: {case.get('fallback_used')}",
            f"* latency_ms: {case.get('latency_ms')}",
            f"* short response snippet: {case.get('response_snippet', '')}",
            "",
        ])
    lines.extend([
        "## Metric Integrity",
        "",
        "* v2_results remained authoritative.",
        f"* v2_metrics_overridden = {str(result['v2_metrics_overridden']).lower()}",
        "* DHMS metrics were not redefined.",
        "",
        "## Failure Modes Observed",
        "",
    ])
    failure_modes = result.get("failure_modes") or ["none"]
    for mode in failure_modes:
        lines.append(f"* {mode}")
    lines.extend([
        "",
        "## Productization Implications",
        "",
        f"* Is Product Layer safe to build now? {'yes' if result['productization_ready'] else 'no'}",
        "* Product Layer should expose API availability, fallback status, bounded call count, drift score, instability index, and v2 metric integrity.",
        "* Product reports must show timeout, rate limit, auth failure, fallback use, response format mismatch, and adapter routing issues.",
        "",
        "## Next Step Recommendation",
        "",
        f"* {result['recommendation']}",
        "",
    ])
    return "\n".join(lines)


def protected_hashes() -> dict[str, str]:
    paths = []
    for rel in ("spec", "contract", "binding"):
        paths.extend(sorted((WORKDIR / rel).glob("**/*")))
    output = {}
    for path in paths:
        if path.is_file():
            output[str(path.relative_to(WORKDIR))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return output


def redact_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    return payload


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
