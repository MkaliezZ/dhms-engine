"""Agent Harness v1 phase 4 suite runner."""

from __future__ import annotations

import shlex
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .agent_suite_report import SUITE_CAVEATS, write_agent_suite_reports
from .agent_suite_summary import build_agent_suite_summary
from .harness_runner import run_agent_harness


FIELD_NAMES = {
    "title",
    "scenario",
    "user_input",
    "memory_context",
    "context",
    "tool_state",
    "expected_agent_property",
    "risk_focus",
}


def run_agent_suite(
    suite: str,
    adapter: str = "mock",
    agent_command: Optional[str] = None,
    n: int = 1,
    mode: str = "B",
    report: bool = False,
    output: str = "reports/agent_harness_suite/latest",
    timeout_seconds: int = 10,
    max_cases: int | None = None,
) -> dict[str, Any]:
    if adapter not in {"mock", "command"}:
        raise ValueError("Phase 4 supports mock and command adapters.")
    if adapter == "command" and not agent_command:
        raise ValueError("agent_command is required for command adapter.")
    if mode not in {"A", "B", "C"}:
        raise ValueError("mode must be A, B, or C")
    if n < 1:
        raise ValueError("n must be >= 1")
    if timeout_seconds < 1:
        raise ValueError("timeout_seconds must be >= 1")
    if max_cases is not None and max_cases < 1:
        raise ValueError("max_cases must be >= 1")

    suite_path = Path(suite)
    if not suite_path.exists() or not suite_path.is_dir():
        raise ValueError(f"suite directory not found: {suite}")
    all_case_paths = sorted(path for path in suite_path.rglob("*.txt") if path.is_file())
    if not all_case_paths:
        raise ValueError(f"suite has no .txt cases: {suite}")
    available_case_count = len(all_case_paths)
    case_paths = all_case_paths[:max_cases] if max_cases is not None else all_case_paths

    suite_name = suite_path.name
    suite_run_id = f"{suite_name}__{adapter}__n{n}__{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir = Path(output)
    case_results: list[dict[str, Any]] = []

    for case_path in case_paths:
        case_id = case_id_from_path(suite_path, case_path)
        parsed = parse_agent_case(case_path)
        input_text = build_case_input(parsed)
        case_output = output_dir / "per_case" / case_id
        metadata = build_case_metadata(
            case_id=case_id,
            case_path=case_path,
            suite_path=suite_path,
            suite_name=suite_name,
            suite_run_id=suite_run_id,
            parsed=parsed,
            adapter=adapter,
            agent_command=agent_command,
            n=n,
            mode=mode,
            report=report,
            output=str(case_output),
            timeout_seconds=timeout_seconds,
        )
        case_result = run_agent_harness(
            input_text=input_text,
            adapter=adapter,
            n=n,
            mode=mode,
            report=report,
            output=str(case_output),
            agent_command=agent_command,
            timeout_seconds=timeout_seconds,
            case_metadata=metadata,
        )
        case_results.append(case_result)

    summary = build_agent_suite_summary(
        case_results,
        suite_name=suite_name,
        suite_run_id=suite_run_id,
        adapter=adapter,
        trial_count=n,
    )
    result: dict[str, Any] = {
        "suite_name": suite_name,
        "suite_path": str(suite_path),
        "suite_run_id": suite_run_id,
        "adapter": adapter,
        "agent_command": agent_command if adapter == "command" else None,
        "mode": mode,
        "trial_count": n,
        "available_case_count": available_case_count,
        "selected_case_count": len(case_paths),
        "max_cases": max_cases,
        "summary": summary,
        "case_results": case_results,
        "report_paths": {},
        "caveats": SUITE_CAVEATS,
    }
    if report:
        result["report_paths"] = {
            "json": str(output_dir / "suite_agent_report.json"),
            "markdown": str(output_dir / "suite_agent_report.md"),
        }
        result["report_paths"] = write_agent_suite_reports(result, output_dir)
    return result


def parse_agent_case(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    fields: dict[str, str] = {}
    parsed_any = False
    current_field: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        name, separator, value = stripped.partition(":")
        key = name.strip().lower()
        if separator and key in FIELD_NAMES:
            current_field = key
            fields[current_field] = value.strip()
            parsed_any = True
        elif current_field:
            fields[current_field] = f"{fields[current_field]} {stripped}".strip()

    metadata = {field: fields.get(field, "not_available") for field in sorted(FIELD_NAMES)}
    return {
        "raw_text": text,
        "fields": fields,
        "metadata": metadata,
        "parse_status": "parsed" if parsed_any else "fallback_full_text",
    }


def build_case_input(parsed: dict[str, Any]) -> str:
    fields = parsed.get("fields", {})
    if not fields.get("user_input"):
        return str(parsed.get("raw_text", ""))
    parts = [
        fields.get("user_input", ""),
        f"Memory context: {fields.get('memory_context', 'not_available')}",
        f"Context: {fields.get('context', 'not_available')}",
        f"Tool state: {fields.get('tool_state', 'not_available')}",
        f"Expected agent property: {fields.get('expected_agent_property', 'not_available')}",
        f"Risk focus: {fields.get('risk_focus', 'not_available')}",
    ]
    return "\n".join(part for part in parts if part)


def build_case_metadata(
    *,
    case_id: str,
    case_path: Path,
    suite_path: Path,
    suite_name: str,
    suite_run_id: str,
    parsed: dict[str, Any],
    adapter: str,
    agent_command: Optional[str],
    n: int,
    mode: str,
    report: bool,
    output: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    metadata = parsed.get("metadata", {})
    relative = case_path.relative_to(suite_path)
    return {
        "case_id": case_id,
        "case_path": str(case_path),
        "suite_name": suite_name,
        "suite_run_id": suite_run_id,
        "case_category": case_category_from_relative(relative),
        "case_title": metadata.get("title", "not_available"),
        "case_parse_status": parsed.get("parse_status", "unknown"),
        "expected_agent_property": metadata.get("expected_agent_property", "not_available"),
        "risk_focus": metadata.get("risk_focus", "not_available"),
        "reproduction_command": build_reproduction_command(
            adapter=adapter,
            agent_command=agent_command,
            case_path=case_path,
            n=n,
            mode=mode,
            report=report,
            output=output,
            timeout_seconds=timeout_seconds,
        ),
    }


def build_reproduction_command(
    *,
    adapter: str,
    agent_command: Optional[str],
    case_path: Path,
    n: int,
    mode: str,
    report: bool,
    output: str,
    timeout_seconds: int,
) -> str:
    parts = [
        "python3",
        "cli.py",
        "test-agent",
        "--input-file",
        str(case_path),
        "--n",
        str(n),
        "--mode",
        mode,
        "--output",
        output,
        "--timeout-seconds",
        str(timeout_seconds),
    ]
    if adapter == "command":
        parts.extend(["--agent-command", agent_command or ""])
    else:
        parts.append("--mock-agent")
    if report:
        parts.append("--report")
    return " ".join(shlex.quote(part) for part in parts)


def case_id_from_path(suite_path: Path, case_path: Path) -> str:
    relative = case_path.relative_to(suite_path).with_suffix("")
    return "__".join(relative.parts)


def case_category_from_relative(relative: Path) -> str:
    if len(relative.parts) > 1:
        return relative.parts[0]
    return "not_available"
