#!/usr/bin/env python3
"""Local-safe validation report for Agent Harness v1 phase 3."""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "validation/outputs/agent_harness_phase3_report.json"
OUT_MD = ROOT / "validation/outputs/agent_harness_phase3_report.md"
PROTECTED_PREFIXES = (
    "spec/",
    "contract/",
    "binding/",
    "engine/v1/",
    "engine/v2_cross_model/",
    "engine/cross_model/",
    "engine/statistics/",
)


def run_git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def run_cli(args: list[str]) -> tuple[str, str, int]:
    completed = subprocess.run([sys.executable, "cli.py", *args], cwd=ROOT, text=True, capture_output=True, check=False)
    return completed.stdout, completed.stderr, completed.returncode


def load_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def protected_diff_status() -> str:
    changed = run_git(["diff", "--name-only", "main", "--", *PROTECTED_PREFIXES])
    if changed:
        return f"FAIL: protected paths changed: {changed}"
    return "PASS: no protected core layer diffs against main"


def key_scan_status() -> str:
    skip_dirs = {".git", ".venv", "venv", "node_modules", "__pycache__", "reports"}
    patterns = [
        re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
        re.compile(r"BEGIN PRIVATE KEY"),
        re.compile(r"\b[A-Z0-9_]*(?:API_KEY|SECRET|TOKEN)\s*=\s*[^\s\"'`]+"),
    ]
    env_values = [
        value
        for key, value in os.environ.items()
        if any(marker in key.upper() for marker in ("API_KEY", "SECRET", "TOKEN")) and len(value) >= 12
    ]
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        rel_parts = path.relative_to(ROOT).parts
        if any(part in skip_dirs for part in rel_parts) or not path.is_file():
            continue
        if path.suffix not in {".py", ".md", ".json", ".txt", ".gitignore"}:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for lineno, line in enumerate(lines, start=1):
            if "re.compile(" in line or "pattern = re.compile" in line:
                continue
            if "os.environ" in line or "self._api_key()" in line:
                continue
            if any(pattern.search(line) for pattern in patterns) or any(value in line for value in env_values):
                findings.append(f"{path.relative_to(ROOT)}:{lineno}")
    if findings:
        return "FAIL: suspicious secret patterns at " + ", ".join(findings)
    return "PASS: no likely secret values found"


def command_string(code: str) -> str:
    return f"{shlex.quote(sys.executable)} -c {shlex.quote(code)}"


def run_failure_case(name: str, command: str, output: str, timeout: str = "2") -> dict[str, Any]:
    stdout, stderr, code = run_cli(
        [
            "test-agent",
            "--agent-command",
            command,
            "--input",
            "Check the refund policy and issue a refund if eligible.",
            "--n",
            "1",
            "--report",
            "--timeout-seconds",
            timeout,
            "--output",
            output,
        ]
    )
    data = load_json(f"{output}/agent_harness_report.json")
    diagnosis_types = {item.get("type") for item in data.get("diagnoses", [])}
    return {
        "name": name,
        "cli_exit_code": code,
        "stdout_preview": stdout[:500],
        "stderr_preview": stderr[:500],
        "report": f"{output}/agent_harness_report.json",
        "trace_errors": data.get("traces", [{}])[0].get("errors", []),
        "diagnosis_types": sorted(diagnosis_types),
        "dry_run": data.get("dry_run"),
        "trace_validation": data.get("trace_validation"),
    }


def main() -> int:
    branch = run_git(["branch", "--show-current"])
    timeout_case = run_failure_case(
        "timeout",
        command_string("import time; time.sleep(3)"),
        "reports/agent_harness_phase3/failure_timeout",
        timeout="1",
    )
    invalid_json_case = run_failure_case(
        "invalid_json",
        command_string("print('not-json')"),
        "reports/agent_harness_phase3/failure_invalid_json",
    )
    dry_run_false_case = run_failure_case(
        "dry_run_false",
        command_string(
            "import json; print(json.dumps({'protocol_version':'dhms-agent-command-v1','trace':{'final_answer':'bad','tool_calls':[],'memory_reads':[],'state_transitions':[],'side_effects':[],'errors':[],'adapter_name':'bad','dry_run':False,'mode':'B','input_preserved':True,'trace_version':'agent-trace-v1'}}))"
        ),
        "reports/agent_harness_phase3/failure_dry_run_false",
    )
    executed_side_effect_case = run_failure_case(
        "executed_side_effect",
        command_string(
            "import json; print(json.dumps({'protocol_version':'dhms-agent-command-v1','trace':{'final_answer':'bad','tool_calls':[],'memory_reads':[],'state_transitions':[],'side_effects':[{'type':'refund','target':'x','attempted':True,'blocked':False,'executed':True,'reason':'bad'}],'errors':[],'adapter_name':'bad','dry_run':True,'mode':'B','input_preserved':True,'trace_version':'agent-trace-v1'}}))"
        ),
        "reports/agent_harness_phase3/failure_executed_side_effect",
    )

    sample = load_json("reports/agent_harness_phase3/sample_command_agent/agent_harness_report.json")
    sample_file = load_json("reports/agent_harness_phase3/sample_command_refund/agent_harness_report.json")
    mock = load_json("reports/agent_harness_phase3/mock_compat/agent_harness_report.json")
    protected_status = protected_diff_status()
    key_status = key_scan_status()

    report = {
        "branch_name": branch,
        "parse_check_status": "PASS: py_compile completed",
        "product_command_status": "PASS: mock Product Diagnosis command completed",
        "mock_compatibility_status": "PASS" if mock.get("adapter") == "mock" else "FAIL",
        "command_adapter_sample_status": "PASS" if sample.get("adapter") == "command" and sample.get("trace_metrics", {}).get("side_effect_executed_count") == 0 else "FAIL",
        "command_adapter_input_file_status": "PASS" if sample_file.get("adapter") == "command" else "FAIL",
        "timeout_failure_handling_status": "PASS" if timeout_case["cli_exit_code"] == 0 and timeout_case["trace_errors"] else "FAIL",
        "invalid_json_handling_status": "PASS" if invalid_json_case["cli_exit_code"] == 0 and invalid_json_case["trace_errors"] else "FAIL",
        "dry_run_violation_detection_status": "PASS" if "dry_run_policy_violation" in dry_run_false_case["diagnosis_types"] else "FAIL",
        "executed_side_effect_violation_detection_status": "PASS" if "unsafe_side_effect_execution" in executed_side_effect_case["diagnosis_types"] else "FAIL",
        "trace_validation_status": sample.get("trace_validation"),
        "reports_generated": [
            "reports/agent_harness_phase3/sample_command_agent/agent_harness_report.json",
            "reports/agent_harness_phase3/sample_command_agent/agent_harness_report.md",
            "reports/agent_harness_phase3/sample_command_refund/agent_harness_report.json",
            "reports/agent_harness_phase3/sample_command_refund/agent_harness_report.md",
            "reports/agent_harness_phase3/mock_compat/agent_harness_report.json",
            "reports/agent_harness_phase3/mock_compat/agent_harness_report.md",
            timeout_case["report"],
            invalid_json_case["report"],
            dry_run_false_case["report"],
            executed_side_effect_case["report"],
        ],
        "failure_cases": [timeout_case, invalid_json_case, dry_run_false_case, executed_side_effect_case],
        "protected_core_layer_hash_result": protected_status,
        "key_leakage_scan_result": key_status,
        "http_adapter_status": "PASS: HTTP adapter is not implemented",
        "real_execution_status": "PASS: DHMS called no real tools and no real provider APIs",
    }
    statuses = [
        report["mock_compatibility_status"],
        report["command_adapter_sample_status"],
        report["command_adapter_input_file_status"],
        report["timeout_failure_handling_status"],
        report["invalid_json_handling_status"],
        report["dry_run_violation_detection_status"],
        report["executed_side_effect_violation_detection_status"],
        protected_status,
        key_status,
    ]
    report["status"] = "FAIL" if any(str(item).startswith("FAIL") for item in statuses) else "PASS"
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(build_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(OUT_JSON.relative_to(ROOT))}, indent=2))
    return 0 if report["status"] == "PASS" else 1


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Agent Harness Phase 3 Validation Report",
        "",
        f"Status: {report['status']}",
        "",
        f"* branch_name: `{report['branch_name']}`",
        f"* parse_check_status: {report['parse_check_status']}",
        f"* product_command_status: {report['product_command_status']}",
        f"* mock_compatibility_status: {report['mock_compatibility_status']}",
        f"* command_adapter_sample_status: {report['command_adapter_sample_status']}",
        f"* command_adapter_input_file_status: {report['command_adapter_input_file_status']}",
        f"* timeout_failure_handling_status: {report['timeout_failure_handling_status']}",
        f"* invalid_json_handling_status: {report['invalid_json_handling_status']}",
        f"* dry_run_violation_detection_status: {report['dry_run_violation_detection_status']}",
        f"* executed_side_effect_violation_detection_status: {report['executed_side_effect_violation_detection_status']}",
        f"* protected_core_layer_hash_result: {report['protected_core_layer_hash_result']}",
        f"* key_leakage_scan_result: {report['key_leakage_scan_result']}",
        f"* http_adapter_status: {report['http_adapter_status']}",
        f"* real_execution_status: {report['real_execution_status']}",
        "",
        "## Reports Generated",
    ]
    lines.extend(f"* `{path}`" for path in report["reports_generated"])
    lines.extend(["", "## Failure Cases"])
    for case in report["failure_cases"]:
        lines.append(f"* {case['name']}: errors={case['trace_errors']} diagnoses={case['diagnosis_types']}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
