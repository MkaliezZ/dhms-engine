"""Response normalization for deterministic DHMS V2.5 comparability."""

import re
from typing import Any, Mapping


_WHITESPACE = re.compile(r"\s+")
_CODE_FENCE = re.compile(r"^```[a-zA-Z0-9_-]*\s*|\s*```$", re.MULTILINE)


def normalize_response(response: str) -> str:
    text = str(response)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _CODE_FENCE.sub("", text.strip())
    text = _WHITESPACE.sub(" ", text)
    return text.strip().lower()


def normalize_run_result(run_result: Mapping[str, Any]) -> dict[str, Any]:
    normalized = dict(run_result)
    regime_results = {}
    for regime, result in run_result["regime_results"].items():
        item = dict(result)
        item["raw_response"] = result["response"]
        item["response"] = normalize_response(result["response"])
        regime_results[regime] = item
    normalized["regime_results"] = regime_results
    return normalized


def normalize_model_results(model_results: Mapping[str, Any]) -> dict[str, Any]:
    output = {}
    for model_name, model_result in model_results.items():
        item = dict(model_result)
        item["per_run_results"] = [normalize_run_result(result) for result in model_result["per_run_results"]]
        output[model_name] = item
    return output
