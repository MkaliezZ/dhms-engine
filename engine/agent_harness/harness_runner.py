"""Agent Harness v1 runner with phase 2 trace diagnosis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from .agent_protocol import DHMS_AGENT_PROTOCOL_VERSION
from .command_agent_adapter import CommandAgentAdapter, command_metadata_from_trace
from .mock_agent_adapter import MockAgentAdapter
from .perturbation_profile import build_context_condition, build_memory_condition, build_tool_state_condition
from .trace_normalizer import normalize_trace
from .trace_report_enricher import enrich_agent_harness_result
from .trace_schema import AgentRunRequest


HARNESS_VERSION = "agent_harness_v1_phase3_command_adapter"


def run_agent_harness(
    input_text: str,
    adapter: str = "mock",
    n: int = 1,
    mode: str = "B",
    report: bool = False,
    output: str = "reports/agent_harness/latest",
    agent_command: Optional[str] = None,
    timeout_seconds: int = 10,
) -> dict[str, Any]:
    if adapter not in {"mock", "command"}:
        raise ValueError("Phase 3 supports mock and command adapters.")
    if adapter == "command" and not agent_command:
        raise ValueError("agent_command is required for command adapter.")
    if mode not in {"A", "B", "C"}:
        raise ValueError("mode must be A, B, or C")
    if n < 1:
        raise ValueError("n must be >= 1")

    if adapter == "command":
        adapter_instance = CommandAgentAdapter(agent_command or "", timeout_seconds=timeout_seconds)
    else:
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
            metadata={"trial_index": trial_index, "agent_harness_phase": "phase3_command_adapter_dry_run"},
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
        "agent_harness_phase": "phase3_command_adapter_dry_run",
    }
    if adapter == "command":
        result.update(command_report_metadata(traces, agent_command or "", timeout_seconds))
    result = enrich_agent_harness_result(result, input_text)
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
    summary = result.get("diagnosis_summary", {})
    metrics = result.get("trace_metrics", {})
    expected = result.get("expected_property_check", {})
    lines = [
        "# DHMS Agent Harness Trace Diagnosis Report",
        "",
        "## Executive Summary",
        "",
        f"* adapter: {result['adapter']}",
        f"* command: {result.get('agent_command', 'not_applicable')}",
        f"* protocol_version: {result.get('protocol_version', 'not_applicable')}",
        f"* timeout_seconds: {result.get('timeout_seconds', 'not_applicable')}",
        f"* trace_validation: {result.get('trace_validation', 'not_applicable')}",
        f"* command_exit_status: {result.get('command_exit_status', 'not_available')}",
        f"* dry_run: {str(result['dry_run']).lower()}",
        f"* mode: {result['mode']}",
        f"* trial_count: {result['trial_count']}",
        f"* diagnosis_version: {result.get('diagnosis_version')}",
        f"* primary_issue: {summary.get('primary_issue', 'not_available')}",
        f"* severity: {summary.get('severity', 'not_available')}",
        f"* recommendation_confidence: {result.get('recommendation_confidence', 'not_available')}",
        "",
        "## Dry-Run Status",
        "",
        f"* dry_run_all_traces: {metrics.get('dry_run_all_traces')}",
        f"* side_effects_blocked_count: {result['side_effects_blocked_count']}",
        f"* side_effect_executed_count: {metrics.get('side_effect_executed_count')}",
        f"* side-effect safety result: {'pass' if metrics.get('side_effect_executed_count') == 0 else 'fail'}",
        f"* stderr_preview: {result.get('stderr_preview') or 'none'}",
        "",
        "## Trace Metrics",
        "",
        f"* final_answer_unique_count: {metrics.get('final_answer_unique_count')}",
        f"* tool_call_count: {result['tool_call_count']}",
        f"* unique_tool_names: {', '.join(metrics.get('unique_tool_names', [])) or 'none'}",
        f"* memory_read_count: {result['memory_read_count']}",
        f"* unique_memory_keys: {', '.join(metrics.get('unique_memory_keys', [])) or 'none'}",
        f"* state_transition_count: {metrics.get('state_transition_count')}",
        f"* side_effect_attempt_count: {metrics.get('side_effect_attempt_count')}",
        f"* error_count: {metrics.get('error_count')}",
        f"* trace_count: {metrics.get('trace_count')}",
        "",
        "## Expected Agent Property Check",
        "",
        f"* passed: {expected.get('passed', 'unknown')}",
        f"* confidence: {expected.get('confidence', 'low')}",
        f"* notes: {expected.get('notes', 'not_available')}",
        "",
        "Evidence:",
    ]
    lines.extend(f"* {item}" for item in expected.get("evidence", []))
    lines.extend(
        [
            "",
            "## Diagnosis Summary",
            "",
            f"* primary_issue: {summary.get('primary_issue', 'not_available')}",
            f"* severity: {summary.get('severity', 'not_available')}",
            f"* confidence: {summary.get('confidence', 'not_available')}",
            f"* is_actionable: {summary.get('is_actionable', 'not_available')}",
            f"* short_explanation: {summary.get('short_explanation', 'not_available')}",
            "",
            "## Diagnoses",
            "",
        ]
    )
    for diagnosis in result.get("diagnoses", []):
        lines.extend(
            [
                f"### {diagnosis.get('type')}",
                "",
                f"* severity: {diagnosis.get('severity')}",
                f"* confidence: {diagnosis.get('confidence')}",
                f"* meaning: {diagnosis.get('meaning')}",
                f"* interpretation: {diagnosis.get('interpretation')}",
                f"* evidence: {diagnosis.get('evidence')}",
                "",
            ]
        )
    lines.extend(["## Recommendations", ""])
    for rec in result.get("recommendation_evidence", []):
        lines.extend(
            [
                f"* {rec.get('priority')} {rec.get('action')}",
                f"  * affected_layer: {rec.get('affected_layer')}",
                f"  * confidence: {rec.get('confidence')}",
                f"  * reason: {rec.get('reason')}",
                f"  * evidence: {', '.join(rec.get('evidence', []))}",
            ]
        )
    lines.extend(["", "## Traces", ""])
    for index, trace in enumerate(result.get("traces", []), start=1):
        lines.extend(
            [
                f"### Trial {index}",
                "",
                f"* final_answer: {trace.get('final_answer')}",
                f"* adapter_name: {trace.get('adapter_name')}",
                f"* mode: {trace.get('mode')}",
                "",
                "## Tool Calls" if index == 1 else "Tool calls:",
            ]
        )
        for tool_call in trace.get("tool_calls", []):
            lines.append(
                f"* {tool_call.get('tool_name')} executed={tool_call.get('executed')} blocked={tool_call.get('blocked')} reason={tool_call.get('reason')}"
            )
        if not trace.get("tool_calls"):
            lines.append("* none")
        lines.append("")
        lines.append("## Memory Reads" if index == 1 else "Memory reads:")
        for memory_read in trace.get("memory_reads", []):
            lines.append(
                f"* {memory_read.get('key')} source={memory_read.get('source')} freshness={memory_read.get('freshness')} used={memory_read.get('used_in_answer')}"
            )
        lines.append("")
        lines.append("## Side Effects" if index == 1 else "Side effects:")
        for side_effect in trace.get("side_effects", []):
            lines.append(
                f"* {side_effect.get('type')} target={side_effect.get('target')} blocked={side_effect.get('blocked')} reason={side_effect.get('reason')}"
            )
        if not trace.get("side_effects"):
            lines.append("* none")
        lines.append("")
        lines.append("## State Transitions" if index == 1 else "State transitions:")
        for transition in trace.get("state_transitions", []):
            lines.append(
                f"* {transition.get('from_state')} -> {transition.get('to_state')} reason={transition.get('reason')}"
            )
        if not trace.get("state_transitions"):
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
            "## Caveats",
            "",
            "* Phase 2 uses deterministic mock agent only.",
            "* No real agent tested.",
            "* No real tools executed.",
            "* No real APIs called.",
            "* n=1 is preliminary.",
            "* Local command adapter is BYOA dry-run only; DHMS does not certify external tool safety.",
            "",
        ]
    )
    return "\n".join(lines)


def command_report_metadata(traces: list[dict], command: str, timeout_seconds: int) -> dict[str, Any]:
    metadata_items = [command_metadata_from_trace(trace) for trace in traces]
    metadata_items = [item for item in metadata_items if item]
    first = metadata_items[0] if metadata_items else {}
    validation_items = [
        trace.get("_trace_validation")
        for trace in traces
        if isinstance(trace.get("_trace_validation"), dict)
    ]
    return {
        "agent_command": first.get("agent_command", command),
        "timeout_seconds": first.get("timeout_seconds", timeout_seconds),
        "protocol_version": first.get("protocol_version", DHMS_AGENT_PROTOCOL_VERSION),
        "trace_validation": validation_items or [{"valid": False, "errors": ["trace validation unavailable"], "warnings": []}],
        "command_exit_status": first.get("command_exit_status"),
        "stderr_preview": first.get("stderr_preview", ""),
    }
