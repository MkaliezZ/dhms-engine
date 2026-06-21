"""Agent Harness v1 phase 4 suite runner."""

from __future__ import annotations

import shlex
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .agent_expected_property_checker import parse_expected_constraints
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
    "expected_constraints",
    "risk_focus",
}

EXECUTION_SUMMARY_SCHEMA_VERSION = "agent-harness-execution-summary-v1"

TAXONOMY_LABELS = {
    "A": "Action Risk Domain",
    "B": "Memory / Context Risk Domain",
    "C": "Reserved Context Coordination Domain",
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
    case_id: str | None = None,
    run_all_cases: bool = False,
    judge_mode: str = "deterministic",
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
    if run_all_cases and max_cases is not None:
        raise ValueError("run_all_cases cannot be combined with max_cases")

    suite_path = Path(suite)
    if not suite_path.exists() or not suite_path.is_dir():
        raise ValueError(f"suite directory not found: {suite}")
    all_case_paths = sorted(path for path in suite_path.rglob("*.txt") if path.is_file())
    if not all_case_paths:
        raise ValueError(f"suite has no .txt cases: {suite}")
    available_case_count = len(all_case_paths)
    case_paths = select_case_paths(all_case_paths, suite_path=suite_path, case_id=case_id, max_cases=max_cases)

    suite_name = suite_path.name
    suite_run_id = f"{suite_name}__{adapter}__n{n}__{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir = Path(output)
    case_results: list[dict[str, Any]] = []

    for case_path in case_paths:
        current_case_id = case_id_from_path(suite_path, case_path)
        parsed = parse_agent_case(case_path)
        input_text = build_case_input(parsed)
        case_output = output_dir / "per_case" / current_case_id
        metadata = build_case_metadata(
            case_id=current_case_id,
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
            judge_mode=judge_mode,
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
            judge_mode=judge_mode,
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
        "case_selector": case_id,
        "run_all_cases": bool(run_all_cases and not case_id),
        "judge_mode": judge_mode,
        "summary": summary,
        "case_results": case_results,
        "execution_summary": build_execution_summary(
            case_results,
            suite_name=suite_name,
            suite_run_id=suite_run_id,
            adapter=adapter,
            trial_count=n,
            judge_mode=judge_mode,
            run_all_cases=bool(run_all_cases and not case_id),
            case_selector=case_id,
            max_cases=max_cases,
        ),
        "report_paths": {},
        "caveats": SUITE_CAVEATS,
    }
    result["execution_summary_path"] = write_execution_summary(result["execution_summary"], output_dir)
    if report:
        result["report_paths"] = {
            "json": str(output_dir / "suite_agent_report.json"),
            "markdown": str(output_dir / "suite_agent_report.md"),
            "execution_summary": result["execution_summary_path"],
        }
        result["report_paths"] = write_agent_suite_reports(result, output_dir)
    return result


def select_case_paths(
    all_case_paths: list[Path],
    *,
    suite_path: Path,
    case_id: str | None,
    max_cases: int | None,
) -> list[Path]:
    if case_id:
        wanted = case_id.strip()
        if not wanted:
            raise ValueError("--case/--case-id must not be empty")
        matches = [
            path
            for path in all_case_paths
            if case_id_from_path(suite_path, path) == wanted or path.stem == wanted
        ]
        if not matches:
            available = ", ".join(case_id_from_path(suite_path, path) for path in all_case_paths)
            raise ValueError(f"case id not found: {wanted}. Available cases: {available}")
        if len(matches) > 1:
            matched = ", ".join(str(path) for path in matches)
            raise ValueError(f"case id matched multiple cases: {wanted}. Matches: {matched}")
        return matches
    return all_case_paths[:max_cases] if max_cases is not None else all_case_paths


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
            if current_field == "expected_constraints":
                fields[current_field] = f"{fields[current_field]}\n{stripped}".strip()
            else:
                fields[current_field] = f"{fields[current_field]} {stripped}".strip()

    metadata = {field: fields.get(field, "not_available") for field in sorted(FIELD_NAMES)}
    metadata["expected_constraints"] = parse_expected_constraints(fields.get("expected_constraints", ""))
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
        f"Expected constraints: {fields.get('expected_constraints', 'not_available')}",
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
    judge_mode: str,
) -> dict[str, Any]:
    metadata = parsed.get("metadata", {})
    relative = case_path.relative_to(suite_path)
    perturbation_mode = infer_perturbation_mode(case_id, metadata)
    return {
        "case_id": case_id,
        "case_path": str(case_path),
        "suite_name": suite_name,
        "suite_run_id": suite_run_id,
        "case_category": case_category_from_relative(relative),
        "perturbation_mode": perturbation_mode,
        "abc_tag": perturbation_mode,
        "case_title": metadata.get("title", "not_available"),
        "case_parse_status": parsed.get("parse_status", "unknown"),
        "expected_agent_property": metadata.get("expected_agent_property", "not_available"),
        "expected_constraints": metadata.get("expected_constraints", []),
        "judge_mode": judge_mode,
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


def infer_perturbation_mode(case_id: str, metadata: dict[str, Any]) -> str:
    if case_id == "memory_sensitive_agent_action":
        return "B"
    text = " ".join(
        [
            case_id,
            str(metadata.get("title", "")),
            str(metadata.get("scenario", "")),
            str(metadata.get("user_input", "")),
            str(metadata.get("memory_context", "")),
            str(metadata.get("context", "")),
            str(metadata.get("tool_state", "")),
            str(metadata.get("expected_agent_property", "")),
            str(metadata.get("risk_focus", "")),
        ]
    ).lower()
    if "memory_sensitive" in case_id or "stale_authorization" in case_id:
        return "B"
    if any(word in text for word in ("delete", "refund", "tool", "side effect", "state", "transition", "subscription", "action", "modify")):
        return "A"
    return "A"


def build_execution_summary(
    case_results: list[dict[str, Any]],
    *,
    suite_name: str,
    suite_run_id: str,
    adapter: str,
    trial_count: int,
    judge_mode: str,
    run_all_cases: bool,
    case_selector: str | None,
    max_cases: int | None,
) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    passed_cases: list[str] = []
    failed_cases: list[str] = []
    unknown_cases: list[str] = []
    safety_values: list[str] = []
    semantic_values: list[str] = []
    taxonomy_distribution: dict[str, int] = {domain: 0 for domain in TAXONOMY_LABELS}

    for result in case_results:
        case_id = str(result.get("case_id", "unknown"))
        execution_safety = result.get("execution_safety_result", {}) if isinstance(result.get("execution_safety_result"), dict) else {}
        semantic = result.get("semantic_property_result", {}) if isinstance(result.get("semantic_property_result"), dict) else {}
        safety_overall = str(execution_safety.get("overall", "unknown"))
        semantic_overall = str(semantic.get("overall", "unknown"))
        taxonomy_domain = normalize_taxonomy_domain(result.get("perturbation_mode") or result.get("abc_tag"))
        taxonomy_distribution[taxonomy_domain] = taxonomy_distribution.get(taxonomy_domain, 0) + 1
        safety_values.append(safety_overall)
        semantic_values.append(semantic_overall)

        if safety_overall == "failed" or semantic_overall == "failed":
            failed_cases.append(case_id)
            final_status = "failed"
        elif safety_overall == "passed" and semantic_overall == "passed":
            passed_cases.append(case_id)
            final_status = "passed"
        else:
            unknown_cases.append(case_id)
            final_status = "unknown"

        cases.append(
            {
                "case_id": case_id,
                "case_path": result.get("case_path", "not_available"),
                "taxonomy_domain": taxonomy_domain,
                "taxonomy_label": TAXONOMY_LABELS[taxonomy_domain],
                "execution_safety_result": {
                    "overall": safety_overall,
                    "safety_veto": execution_safety.get("safety_veto", False),
                    "violations": execution_safety.get("violations", []),
                },
                "semantic_property_result": {
                    "overall": semantic_overall,
                    "passed": semantic.get("passed", "unknown"),
                    "safety_veto": semantic.get("safety_veto", False),
                    "unknown_reason": semantic.get("unknown_reason", ""),
                },
                "final_status": final_status,
            }
        )

    return {
        "schema_version": EXECUTION_SUMMARY_SCHEMA_VERSION,
        "run_metadata": {
            "suite_name": suite_name,
            "suite_run_id": suite_run_id,
            "adapter": adapter,
            "trial_count": trial_count,
            "judge_mode": judge_mode,
            "run_all_cases": run_all_cases,
            "case_selector": case_selector,
            "max_cases": max_cases,
        },
        "suite_summary": {
            "total_cases": len(case_results),
            "passed_cases": passed_cases,
            "failed_cases": failed_cases,
            "unknown_cases": unknown_cases,
        },
        "taxonomy_summary": {
            "taxonomy_model": "A/B perturbation model",
            "domains": build_taxonomy_summary(taxonomy_distribution),
        },
        "consistency_summary": {
            "execution_safety_result": consistency_summary(safety_values),
            "semantic_property_result": consistency_summary(semantic_values),
        },
        "cases": cases,
    }


def normalize_taxonomy_domain(value: Any) -> str:
    domain = str(value or "A").strip().upper()
    if domain in TAXONOMY_LABELS:
        return domain
    return "A"


def build_taxonomy_summary(distribution: dict[str, int]) -> dict[str, dict[str, Any]]:
    return {
        domain: {
            "label": label,
            "count": int(distribution.get(domain, 0)),
        }
        for domain, label in TAXONOMY_LABELS.items()
    }


def consistency_summary(values: list[str]) -> dict[str, Any]:
    unique_values = sorted(set(values))
    return {
        "consistent": len(unique_values) <= 1,
        "values": unique_values,
    }


def write_execution_summary(execution_summary: dict[str, Any], output_dir: Path) -> str:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "execution_summary.json"
    path.write_text(json.dumps(execution_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(path)
