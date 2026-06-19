"""Agent Harness v1 phase 1 runner."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .mock_agent_adapter import MockAgentAdapter
from .perturbation_profile import build_context_condition, build_memory_condition, build_tool_state_condition
from .trace_normalizer import normalize_trace
from .trace_schema import AgentRunRequest


HARNESS_VERSION = "agent_harness_v1_phase1"


def run_agent_harness(
    input_text: str,
    adapter: str = "mock",
    n: int = 1,
    mode: str = "B",
    report: bool = False,
    output: str = "reports/agent_harness/latest",
) -> dict[str, Any]:
    if adapter != "mock":
        raise ValueError("Phase 1 supports only the mock adapter.")
    if mode not in {"A", "B", "C"}:
        raise ValueError("mode must be A, B, or C")
    if n < 1:
        raise ValueError("n must be >= 1")

    adapter_instance = MockAgentAdapter()
    traces = []
    errors = []
    for trial_index in range(n):
        request = AgentRunRequest(
            input_text=input_text,
            mode=mode,  # type: ignore[arg-type]
            memory_condition=build_memory_condition(mode),
            context_condition=build_context_condition(mode),
            tool_state_condition=build_tool_state_condition(),
            dry_run=True,
            metadata={"trial_index": trial_index, "agent_harness_phase": "phase1_mock_dry_run"},
        )
        try:
            traces.append(normalize_trace(adapter_instance.run(request)))
        except Exception as exc:  # pragma: no cover - defensive aggregation
            errors.append(f"{type(exc).__name__}: {exc}")

    result = {
        "harness_version": HARNESS_VERSION,
        "adapter": adapter,
        "mode": mode,
        "trial_count": n,
        "traces": traces,
        "side_effects_blocked_count": sum(
            1 for trace in traces for item in trace.get("side_effects", []) if item.get("blocked")
        ),
        "tool_call_count": sum(len(trace.get("tool_calls", [])) for trace in traces),
        "memory_read_count": sum(len(trace.get("memory_reads", [])) for trace in traces),
        "errors": errors,
        "dry_run": True,
        "agent_harness_phase": "phase1_mock_dry_run",
    }
    if report:
        result["report_paths"] = write_reports(result, Path(output))
    return result


def write_reports(result: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "agent_harness_report.json"
    md_path = output_dir / "agent_harness_report.md"
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(build_markdown_report(result), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def build_markdown_report(result: dict[str, Any]) -> str:
    lines = [
        "# DHMS Agent Harness Phase 1 Report",
        "",
        f"* adapter: {result['adapter']}",
        f"* dry_run: {str(result['dry_run']).lower()}",
        f"* mode: {result['mode']}",
        f"* trial_count: {result['trial_count']}",
        f"* side_effects_blocked_count: {result['side_effects_blocked_count']}",
        f"* tool_call_count: {result['tool_call_count']}",
        f"* memory_read_count: {result['memory_read_count']}",
        "",
        "## Traces",
        "",
    ]
    for index, trace in enumerate(result.get("traces", []), start=1):
        lines.extend(
            [
                f"### Trial {index}",
                "",
                f"* final_answer: {trace.get('final_answer')}",
                f"* adapter_name: {trace.get('adapter_name')}",
                f"* mode: {trace.get('mode')}",
                "",
                "Tool calls:",
            ]
        )
        for tool_call in trace.get("tool_calls", []):
            lines.append(
                f"* {tool_call.get('tool_name')} executed={tool_call.get('executed')} blocked={tool_call.get('blocked')} reason={tool_call.get('reason')}"
            )
        if not trace.get("tool_calls"):
            lines.append("* none")
        lines.append("")
        lines.append("Memory reads:")
        for memory_read in trace.get("memory_reads", []):
            lines.append(
                f"* {memory_read.get('key')} source={memory_read.get('source')} freshness={memory_read.get('freshness')} used={memory_read.get('used_in_answer')}"
            )
        lines.append("")
        lines.append("Side effects blocked:")
        for side_effect in trace.get("side_effects", []):
            lines.append(
                f"* {side_effect.get('type')} target={side_effect.get('target')} blocked={side_effect.get('blocked')} reason={side_effect.get('reason')}"
            )
        if not trace.get("side_effects"):
            lines.append("* none")
        lines.append("")
        lines.append("Errors:")
        if trace.get("errors"):
            lines.extend(f"* {error}" for error in trace.get("errors", []))
        else:
            lines.append("* none")
        lines.append("")
    lines.extend(
        [
            "## Caveat",
            "",
            "Phase 1 mock dry-run only; no real agent, real tools, real provider APIs, or external side effects executed.",
            "",
        ]
    )
    return "\n".join(lines)
