#!/usr/bin/env python3
"""Validation for Agent Harness v1 phase 4 suite runner."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.agent_harness.agent_suite_runner import parse_agent_case

OUTPUT_DIR = ROOT / "validation" / "outputs"
REPORT_JSON = OUTPUT_DIR / "agent_harness_phase4_report.json"
REPORT_MD = OUTPUT_DIR / "agent_harness_phase4_report.md"
PROTECTED_PATHS = [
    "spec",
    "contract",
    "binding",
    "engine/v1",
    "engine/v2_cross_model",
    "engine/cross_model",
    "engine/statistics",
]
SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"\b[A-Z0-9_]*(?:API_KEY|SECRET|TOKEN)\s*=\s*[^\s\"'`]+"),
    re.compile(r"BEGIN PRIVATE KEY"),
)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "branch_name": git_output(["branch", "--show-current"]),
        "checks": {},
        "commands": [],
        "notes": [
            "Validation uses mock adapter and local sample JSON command adapter only.",
            "DHMS does not execute real tools or call real provider APIs in this validation.",
        ],
    }

    case_paths = sorted((ROOT / "cases" / "agent_core").rglob("*.txt"))
    parse_errors: list[str] = []
    for path in case_paths:
        parsed = parse_agent_case(path)
        if parsed.get("parse_status") not in {"parsed", "fallback_full_text"}:
            parse_errors.append(str(path))
    report["checks"]["parse_check_status"] = "PASS" if not parse_errors else "FAIL"
    report["parse_errors"] = parse_errors
    report["total_case_count"] = len(case_paths)

    commands = {
        "py_compile_status": [
            "python3",
            "-X",
            "pycache_prefix=/tmp/dhms_engine_agent_pycache",
            "-m",
            "compileall",
            "-q",
            str(ROOT),
        ],
        "product_command_status": [
            "python3",
            "cli.py",
            "test",
            "--input",
            "Does this agent stay consistent?",
            "--models",
            "mock",
            "--n",
            "1",
            "--report",
            "--output",
            "reports/agent_phase4_existing_product_check",
        ],
        "single_mock_compatibility_status": [
            "python3",
            "cli.py",
            "test-agent",
            "--mock-agent",
            "--input",
            "Check the refund policy and issue a refund if eligible.",
            "--n",
            "1",
            "--report",
            "--output",
            "reports/agent_harness_phase4/mock_single_compat",
        ],
        "single_command_compatibility_status": [
            "python3",
            "cli.py",
            "test-agent",
            "--agent-command",
            "python3 examples/agents/sample_json_agent.py",
            "--input",
            "Check the refund policy and issue a refund if eligible.",
            "--n",
            "1",
            "--report",
            "--output",
            "reports/agent_harness_phase4/command_single_compat",
        ],
        "mock_suite_status": [
            "python3",
            "cli.py",
            "test-agent-suite",
            "--suite",
            "cases/agent_core",
            "--mock-agent",
            "--n",
            "1",
            "--report",
            "--output",
            "reports/agent_harness_phase4/mock_suite",
        ],
        "command_suite_status": [
            "python3",
            "cli.py",
            "test-agent-suite",
            "--suite",
            "cases/agent_core",
            "--agent-command",
            "python3 examples/agents/sample_json_agent.py",
            "--n",
            "1",
            "--report",
            "--output",
            "reports/agent_harness_phase4/command_suite",
        ],
        "n3_mock_suite_status": [
            "python3",
            "cli.py",
            "test-agent-suite",
            "--suite",
            "cases/agent_core",
            "--mock-agent",
            "--n",
            "3",
            "--report",
            "--output",
            "reports/agent_harness_phase4/mock_suite_n3",
        ],
    }
    for check_name, command in commands.items():
        completed = run_command(command)
        report["commands"].append(completed)
        report["checks"][check_name] = "PASS" if completed["returncode"] == 0 else "FAIL"

    suite_reports = [
        ROOT / "reports" / "agent_harness_phase4" / "mock_suite" / "suite_agent_report.json",
        ROOT / "reports" / "agent_harness_phase4" / "command_suite" / "suite_agent_report.json",
        ROOT / "reports" / "agent_harness_phase4" / "mock_suite_n3" / "suite_agent_report.json",
    ]
    aggregate_present = all(path.exists() for path in suite_reports)
    per_case_present = all(per_case_reports_present(path, len(case_paths)) for path in suite_reports if path.exists())
    report["checks"]["aggregate_report_presence"] = "PASS" if aggregate_present else "FAIL"
    report["checks"]["per_case_report_presence"] = "PASS" if per_case_present else "FAIL"

    loaded_suites = [load_json(path) for path in suite_reports if path.exists()]
    total_executed = sum(int(item.get("summary", {}).get("total_side_effects_executed") or 0) for item in loaded_suites)
    total_attempts = sum(int(item.get("summary", {}).get("total_side_effect_attempts") or 0) for item in loaded_suites)
    total_blocked = sum(int(item.get("summary", {}).get("total_side_effects_blocked") or 0) for item in loaded_suites)
    dry_run_confirmed = all(item.get("summary", {}).get("dry_run_all_cases") is True for item in loaded_suites)
    report["checks"]["side_effects_blocked_confirmed"] = "PASS" if total_attempts > 0 and total_blocked >= total_attempts else "FAIL"
    report["checks"]["no_side_effects_executed"] = "PASS" if total_executed == 0 else "FAIL"
    report["checks"]["dry_run_confirmed"] = "PASS" if dry_run_confirmed else "FAIL"

    report["checks"]["http_adapter_not_implemented"] = "PASS" if http_adapter_not_implemented() else "FAIL"
    report["checks"]["no_real_tools_or_real_apis_called_by_dhms"] = "PASS" if phase4_static_safety_scan() else "FAIL"

    protected_changes = git_output(["diff", "--name-only", "main", "--", *PROTECTED_PATHS]).splitlines()
    report["protected_core_layer_hash_result"] = {
        "status": "PASS" if not protected_changes else "FAIL",
        "changed_paths": protected_changes,
    }
    report["checks"]["protected_core_layer_hash_result"] = report["protected_core_layer_hash_result"]["status"]

    secret_hits = secret_scan()
    report["key_leakage_scan_result"] = {
        "status": "PASS" if not secret_hits else "FAIL",
        "hits": secret_hits,
    }
    report["checks"]["key_leakage_scan_result"] = report["key_leakage_scan_result"]["status"]

    report["status"] = "PASS" if all(value == "PASS" for value in report["checks"].values()) else "FAIL"
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(build_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "report_json": str(REPORT_JSON), "report_md": str(REPORT_MD)}, indent=2))
    return 0 if report["status"] == "PASS" else 1


def run_command(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout_preview": completed.stdout[-1200:],
        "stderr_preview": completed.stderr[-1200:],
    }


def git_output(args: list[str]) -> str:
    completed = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)
    return completed.stdout.strip()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def per_case_reports_present(suite_report_path: Path, expected_count: int) -> bool:
    suite = load_json(suite_report_path)
    case_results = suite.get("case_results", [])
    if len(case_results) != expected_count:
        return False
    for result in case_results:
        paths = result.get("report_paths", {})
        if not paths.get("json") or not paths.get("markdown"):
            return False
        if not Path(paths["json"]).exists() or not Path(paths["markdown"]).exists():
            return False
    return True


def http_adapter_not_implemented() -> bool:
    cli_text = (ROOT / "cli.py").read_text(encoding="utf-8")
    return "--agent-url" not in cli_text and "test-agent-http" not in cli_text


def phase4_static_safety_scan() -> bool:
    paths = [
        ROOT / "engine" / "agent_harness" / "agent_suite_runner.py",
        ROOT / "engine" / "agent_harness" / "agent_suite_summary.py",
        ROOT / "engine" / "agent_harness" / "agent_suite_report.py",
        ROOT / "cli.py",
    ]
    forbidden = ("httpx", "requests.", "urllib", "socket.", "os.system", "shell=True")
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if any(item in text for item in forbidden):
            return False
    return True


def secret_scan() -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    ignored_parts = {".git", ".venv", "__pycache__", "reports"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or ignored_parts.intersection(path.parts):
            continue
        if path.suffix in {".pyc", ".png", ".jpg", ".jpeg", ".gif"}:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            if is_scanner_rule_reference(line):
                continue
            if any(pattern.search(line) for pattern in SECRET_PATTERNS):
                hits.append({"path": str(path.relative_to(ROOT)), "line": line_number})
    return hits


def is_scanner_rule_reference(line: str) -> bool:
    return any(
        marker in line
        for marker in (
            "SECRET_PATTERNS",
            "re.compile",
            "rg -q",
            "pattern =",
            "patterns =",
            "BEGIN PRIVATE KEY",
        )
    ) and not line.lstrip().startswith("-----BEGIN PRIVATE KEY")


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Agent Harness Phase 4 Validation Report",
        "",
        f"* status: {report['status']}",
        f"* branch_name: {report['branch_name']}",
        f"* total_case_count: {report['total_case_count']}",
        "",
        "## Checks",
        "",
    ]
    for key, value in sorted(report["checks"].items()):
        lines.append(f"* {key}: {value}")
    lines.extend(
        [
            "",
            "## Protected Core Layers",
            "",
            f"* status: {report['protected_core_layer_hash_result']['status']}",
            f"* changed_paths: {report['protected_core_layer_hash_result']['changed_paths']}",
            "",
            "## Key Leakage Scan",
            "",
            f"* status: {report['key_leakage_scan_result']['status']}",
            f"* hits: {report['key_leakage_scan_result']['hits']}",
            "",
            "## Notes",
            "",
        ]
    )
    lines.extend(f"* {note}" for note in report["notes"])
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
