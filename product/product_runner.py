"""Product orchestration for DHMS Product Diagnosis v1.3."""

import json
import sys
from pathlib import Path
from typing import Any, Mapping, Optional

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
ENGINE_DIR = ROOT_DIR / "engine"
PATHS = (
    CURRENT_DIR,
    ENGINE_DIR / "v2_5_bridge",
    ENGINE_DIR / "v2_cross_model",
    ENGINE_DIR / "v0",
    ENGINE_DIR / "v1",
    ENGINE_DIR / "cross_model",
    ENGINE_DIR / "statistics",
    ROOT_DIR / "binding",
)
for path in PATHS:
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)

from example_cases import load_text  # noqa: E402
from diagnosis_engine import diagnose_product_result  # noqa: E402
from expected_property_checker import parse_case_fields  # noqa: E402
from product_summary import summarize_product_result  # noqa: E402
from report_generator import generate_reports  # noqa: E402


def run_product_test(
    *,
    input_text: Optional[str] = None,
    input_file: Optional[str] = None,
    models: str = "mock",
    n: int = 5,
    mode: str = "B",
    report: bool = False,
    output: str = "reports/latest",
    case_metadata: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    if n < 1:
        raise ValueError("n must be >= 1")
    text = load_text(input_text, input_file)
    dhms_result = run_dhms(text, mode=mode, models=models, n=n)
    attach_real_api_baseline(dhms_result)
    summary = summarize_product_result(dhms_result, text, models, n)
    metadata = build_case_metadata(text, input_file, models, n, output, case_metadata)
    product_result = {
        "product_name": "LLM Memory Stability Tester",
        "product_version": "DHMS Product Diagnosis v1.3.3",
        **metadata,
        **summary,
        "raw_dhms_result": dhms_result,
        "report_paths": {},
        "reproduction_command": reproduction_command(input_text, input_file, models, n, mode, report, output),
    }
    current = product_result.get("calibration", {}).get("current_run", {})
    product_result["real_api_used"] = bool(current.get("real_api_used"))
    product_result["provider_statuses"] = current.get("provider_statuses") or []
    product_result.update(diagnose_product_result(product_result, text))
    if report:
        product_result["report_paths"] = generate_reports(product_result, output)
    return product_result


def build_case_metadata(case_text: str, input_file: Optional[str], models: str, n: int, output: str, metadata: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    meta = dict(metadata or {})
    fields = parse_case_fields(case_text)
    case_path = meta.get("case_path") or input_file or "not_available"
    case_id = meta.get("case_id") or derive_case_id(case_path)
    case_category = meta.get("case_category") or derive_case_category(case_path)
    requested_models = [item.strip() for item in models.split(",") if item.strip()]
    return {
        "case_id": case_id,
        "case_path": case_path,
        "case_category": case_category,
        "suite_name": meta.get("suite_name"),
        "suite_run_id": meta.get("suite_run_id"),
        "suite_output_dir": meta.get("suite_output_dir") or output,
        "requested_models": requested_models,
        "trial_count": n,
        "real_api_used": "not_available",
        "provider_statuses": [],
        "expected_stability_property": fields.get("expected_stability_property"),
    }


def derive_case_id(case_path: Any) -> str:
    path = str(case_path or "")
    if not path or path == "not_available":
        return "not_available"
    return Path(path).stem


def derive_case_category(case_path: Any) -> str:
    path = Path(str(case_path or ""))
    parts = path.parts
    if "llm_core" in parts:
        index = parts.index("llm_core")
        if len(parts) > index + 1:
            return parts[index + 1]
    if len(parts) >= 2:
        return parts[-2]
    return "not_available"


def run_dhms(input_text: str, *, mode: str, models: str, n: int) -> dict[str, Any]:
    try:
        from v25_bridge_runner import run_v25_bridge
        api_models = api_models_from(models)
        v2_models = v2_models_from(models)
        return run_v25_bridge(mode, input_text, n=n, models=v2_models, api_models=api_models)
    except Exception as exc:
        from v2_orchestrator import run_v2_experiment
        result = run_v2_experiment(mode, input_text, n=n, models=v2_models_from(models))
        result["product_layer_fallback_reason"] = type(exc).__name__
        return result


def v2_models_from(models: str) -> str:
    supported = {"mock", "fallback", "external"}
    selected = []
    for item in models.split(","):
        token = item.strip().lower()
        provider = token.split(":", 1)[0]
        if provider in supported:
            selected.append(provider)
    return ",".join(selected or ["mock"])


def api_models_from(models: str) -> str:
    supported = {"openai", "deepseek", "claude", "anthropic", "qwen", "dashscope", "kimi", "moonshot", "gemini", "mistral"}
    selected = []
    for item in models.split(","):
        token = item.strip().lower()
        provider = token.split(":", 1)[0]
        if provider in supported:
            selected.append(token)
    return ",".join(selected)


def attach_real_api_baseline(dhms_result: dict[str, Any]) -> None:
    path = ROOT_DIR / "validation/deepseek_smoke/outputs/deepseek_smoke_result.json"
    if not path.exists():
        return
    baseline = json.loads(path.read_text(encoding="utf-8"))
    dhms_result["real_api_validation_baseline"] = {
        "status": baseline.get("status"),
        "provider": baseline.get("provider"),
        "model": baseline.get("model"),
        "real_api_used": baseline.get("real_api_used"),
        "fallback_used": baseline.get("fallback_used"),
        "total_real_api_calls": baseline.get("total_real_api_calls"),
        "v2_metrics_overridden": baseline.get("v2_metrics_overridden"),
        "recommendation": baseline.get("recommendation"),
    }


def reproduction_command(input_text: Optional[str], input_file: Optional[str], models: str, n: int, mode: str, report: bool, output: str) -> str:
    if input_text:
        source = f'--input "{input_text}"'
    else:
        source = f'--input-file {input_file}'
    report_flag = " --report" if report else ""
    output_flag = f" --output {output}" if report else ""
    return f"python3 cli.py test {source} --models {models} --n {n} --mode {mode}{report_flag}{output_flag}"
