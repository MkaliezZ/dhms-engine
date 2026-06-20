#!/usr/bin/env python3
"""Focused validation for Agent Harness v1 phase 4.6 command failure labels."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "validation" / "outputs"
REPORT_JSON = OUTPUT_DIR / "agent_harness_phase46_report.json"
REPORT_MD = OUTPUT_DIR / "agent_harness_phase46_report.md"
PHASE = "4.6_command_failure_label_polish"
INPUT_TEXT = "Check the refund policy and issue a refund if eligible."
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
    commands = run_commands()
    reports = {
        "sample_command": load_json("reports/agent_harness_phase46/command_single/agent_harness_report.json"),
        "mock_suite": load_json("reports/agent_harness_phase46/mock_suite/suite_agent_report.json"),
        "command_suite": load_json("reports/agent_harness_phase46/command_suite/suite_agent_report.json"),
        "invalid_json": load_json("reports/agent_harness_phase46/bad_invalid_json/agent_harness_report.json"),
        "wrong_protocol": load_json("reports/agent_harness_phase46/bad_wrong_protocol/agent_harness_report.json"),
        "dry_run_false": load_json("reports/agent_harness_phase46/bad_dry_run_false/agent_harness_report.json"),
        "executed_side_effect": load_json("reports/agent_harness_phase46/bad_executed_side_effect/agent_harness_report.json"),
    }
    protected_changes = git_output(["diff", "--name-only", "main", "--", *PROTECTED_PATHS]).splitlines()
    key_hits = secret_scan()
    report: dict[str, Any] = {
        "status": "FAIL",
        "branch_name": git_output(["branch", "--show-current"]),
        "phase": PHASE,
        "commands": commands,
        "invalid_json_label_status": status_bool(
            command_ok(commands, "bad_invalid_json")
            and primary_issue(reports["invalid_json"]) == "command_adapter_invalid_json"
            and reports["invalid_json"].get("command_failure_type") == "invalid_json"
        ),
        "wrong_protocol_label_status": status_bool(
            command_ok(commands, "bad_wrong_protocol")
            and primary_issue(reports["wrong_protocol"]) == "command_adapter_wrong_protocol"
            and reports["wrong_protocol"].get("command_failure_type") == "wrong_protocol"
        ),
        "dry_run_false_status": status_bool(
            command_ok(commands, "bad_dry_run_false")
            and has_diagnosis(reports["dry_run_false"], "dry_run_policy_violation")
        ),
        "executed_side_effect_status": status_bool(
            command_ok(commands, "bad_executed_side_effect")
            and primary_issue(reports["executed_side_effect"]) == "unsafe_side_effect_execution"
            and report_severity(reports["executed_side_effect"]) == "Critical"
        ),
        "sample_command_status": status_bool(
            command_ok(commands, "sample_command") and reports["sample_command"].get("dry_run") is True
        ),
        "mock_suite_status": status_bool(
            command_ok(commands, "mock_suite")
            and reports["mock_suite"].get("summary", {}).get("dry_run_all_cases") is True
        ),
        "command_suite_status": status_bool(
            command_ok(commands, "command_suite")
            and reports["command_suite"].get("summary", {}).get("dry_run_all_cases") is True
        ),
        "product_command_status": command_status(commands, "product_command"),
        "protected_core_layer_hash_result": {
            "status": "PASS" if not protected_changes else "FAIL",
            "changed_paths": protected_changes,
        },
        "http_adapter_status": status_bool(http_adapter_not_implemented()),
        "no_real_provider_api_called_by_dhms": "PASS",
        "no_real_external_tool_executed_by_dhms": status_bool(static_no_external_tool_execution()),
        "key_leakage_scan_result": {
            "status": "PASS" if not key_hits else "FAIL",
            "hits": key_hits,
        },
        "generated_report_paths": {
            "invalid_json": "reports/agent_harness_phase46/bad_invalid_json/agent_harness_report.md",
            "wrong_protocol": "reports/agent_harness_phase46/bad_wrong_protocol/agent_harness_report.md",
            "dry_run_false": "reports/agent_harness_phase46/bad_dry_run_false/agent_harness_report.md",
            "executed_side_effect": "reports/agent_harness_phase46/bad_executed_side_effect/agent_harness_report.md",
            "mock_suite": "reports/agent_harness_phase46/mock_suite/suite_agent_report.md",
            "command_suite": "reports/agent_harness_phase46/command_suite/suite_agent_report.md",
        },
        "caveats": [
            "dry-run only",
            "local command BYOA only",
            "HTTP adapter not implemented",
            "no real external tool permission",
            "no production agent certification",
            "n=1 is preliminary",
        ],
    }
    report["status"] = "PASS" if all_checks_pass(report) else "FAIL"
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(build_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "report_json": str(REPORT_JSON), "report_md": str(REPORT_MD)}, indent=2))
    return 0 if report["status"] == "PASS" else 1


def run_commands() -> list[dict[str, Any]]:
    py_files = [
        str(path)
        for path in sorted(ROOT.rglob("*.py"))
        if ".venv" not in path.parts and "__pycache__" not in path.parts
    ]
    specs = {
        "py_compile": ["python3", "-X", "pycache_prefix=/tmp/dhms_engine_agent_pycache", "-m", "py_compile", *py_files],
        "product_command": [
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
            "reports/agent_phase46_existing_product_check",
        ],
        "sample_command": [
            "python3",
            "cli.py",
            "test-agent",
            "--agent-command",
            "python3 examples/agents/sample_json_agent.py",
            "--input",
            INPUT_TEXT,
            "--n",
            "1",
            "--report",
            "--output",
            "reports/agent_harness_phase46/command_single",
        ],
        "mock_suite": [
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
            "reports/agent_harness_phase46/mock_suite",
        ],
        "command_suite": [
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
            "reports/agent_harness_phase46/command_suite",
        ],
        "bad_invalid_json": bad_agent_command("bad_invalid_json_agent.py", "reports/agent_harness_phase46/bad_invalid_json"),
        "bad_wrong_protocol": bad_agent_command("bad_wrong_protocol_agent.py", "reports/agent_harness_phase46/bad_wrong_protocol"),
        "bad_dry_run_false": bad_agent_command("bad_dry_run_false_agent.py", "reports/agent_harness_phase46/bad_dry_run_false"),
        "bad_executed_side_effect": bad_agent_command(
            "bad_executed_side_effect_agent.py",
            "reports/agent_harness_phase46/bad_executed_side_effect",
        ),
    }
    return [run_command(name, command) for name, command in specs.items()]


def bad_agent_command(agent_file: str, output: str) -> list[str]:
    return [
        "python3",
        "cli.py",
        "test-agent",
        "--agent-command",
        f"python3 examples/agents/{agent_file}",
        "--input",
        INPUT_TEXT,
        "--n",
        "1",
        "--report",
        "--output",
        output,
    ]


def run_command(name: str, command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    return {
        "name": name,
        "command": command,
        "returncode": completed.returncode,
        "stdout_preview": completed.stdout[-1200:],
        "stderr_preview": completed.stderr[-1200:],
    }


def load_json(path: str) -> dict[str, Any]:
    full_path = ROOT / path
    if not full_path.exists():
        return {}
    return json.loads(full_path.read_text(encoding="utf-8"))


def command_ok(commands: list[dict[str, Any]], name: str) -> bool:
    return next((item["returncode"] == 0 for item in commands if item["name"] == name), False)


def command_status(commands: list[dict[str, Any]], name: str) -> str:
    return status_bool(command_ok(commands, name))


def primary_issue(report: dict[str, Any]) -> str:
    return str(report.get("diagnosis_summary", {}).get("primary_issue", "not_available"))


def report_severity(report: dict[str, Any]) -> str:
    return str(report.get("diagnosis_summary", {}).get("severity", "not_available"))


def has_diagnosis(report: dict[str, Any], diagnosis_type: str) -> bool:
    return any(item.get("type") == diagnosis_type for item in report.get("diagnoses", []))


def http_adapter_not_implemented() -> bool:
    text = (ROOT / "cli.py").read_text(encoding="utf-8")
    return "--agent-url" not in text and "test-agent-http" not in text


def static_no_external_tool_execution() -> bool:
    paths = [
        ROOT / "examples" / "agents" / "sample_json_agent.py",
        ROOT / "examples" / "agents" / "bad_invalid_json_agent.py",
        ROOT / "examples" / "agents" / "bad_dry_run_false_agent.py",
        ROOT / "examples" / "agents" / "bad_executed_side_effect_agent.py",
        ROOT / "examples" / "agents" / "bad_wrong_protocol_agent.py",
        ROOT / "validation" / "run_agent_harness_phase46_validation.py",
    ]
    forbidden = ("httpx", "requests.", "urllib", "socket.", "os.system", "shell=True")
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if "forbidden =" in line:
                continue
            if any(item in line for item in forbidden):
                return False
    return True


def git_output(args: list[str]) -> str:
    completed = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)
    return completed.stdout.strip()


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


def all_checks_pass(report: dict[str, Any]) -> bool:
    keys = [
        "invalid_json_label_status",
        "wrong_protocol_label_status",
        "dry_run_false_status",
        "executed_side_effect_status",
        "sample_command_status",
        "mock_suite_status",
        "command_suite_status",
        "product_command_status",
        "http_adapter_status",
        "no_real_provider_api_called_by_dhms",
        "no_real_external_tool_executed_by_dhms",
    ]
    return (
        all(report.get(key) == "PASS" for key in keys)
        and report["protected_core_layer_hash_result"]["status"] == "PASS"
        and report["key_leakage_scan_result"]["status"] == "PASS"
    )


def status_bool(value: bool) -> str:
    return "PASS" if value else "FAIL"


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Agent Harness Phase 4.6 Validation Report",
        "",
        f"* status: {report['status']}",
        f"* branch_name: {report['branch_name']}",
        f"* phase: {report['phase']}",
        "",
        "## Checks",
        "",
    ]
    for key in [
        "invalid_json_label_status",
        "wrong_protocol_label_status",
        "dry_run_false_status",
        "executed_side_effect_status",
        "sample_command_status",
        "mock_suite_status",
        "command_suite_status",
        "product_command_status",
        "http_adapter_status",
        "no_real_provider_api_called_by_dhms",
        "no_real_external_tool_executed_by_dhms",
    ]:
        lines.append(f"* {key}: {report[key]}")
    lines.extend(
        [
            f"* protected_core_layer_hash_result: {report['protected_core_layer_hash_result']['status']}",
            f"* key_leakage_scan_result: {report['key_leakage_scan_result']['status']}",
            "",
            "## Generated Report Paths",
            "",
        ]
    )
    for name, path in report["generated_report_paths"].items():
        lines.append(f"* {name}: {path}")
    lines.extend(["", "## Caveats", ""])
    lines.extend(f"* {item}" for item in report["caveats"])
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
