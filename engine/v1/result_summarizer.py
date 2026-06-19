"""Structured summaries for DHMS v1 measurement results."""

from typing import Any, Mapping, Sequence


def build_summary(
    *,
    mode: str,
    input_text: str,
    n: int,
    measurement: Mapping[str, Any],
    per_run_results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    metrics = measurement["aggregated_metrics"]
    comparison = measurement["regime_comparison"]
    return {
        "requested_mode": mode,
        "input_length": len(input_text),
        "trial_count": n,
        "metrics": metrics,
        "input_identity_preserved": comparison["input_identity_preserved"],
        "binding_validated_runs": sum(1 for result in per_run_results if result["execution_permitted"]),
        "readable_summary": (
            "DHMS v1 completed "
            f"{n} trial(s) with stability={metrics['stability']}, "
            f"sensitivity={metrics['sensitivity']}, "
            f"specificity={metrics['specificity']}, "
            f"isolation_strength={metrics['isolation_strength']}."
        ),
    }

