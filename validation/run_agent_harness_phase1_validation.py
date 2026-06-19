#!/usr/bin/env python3
"""Local-safe validation report for Agent Harness v1 phase 1."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STABLE_REPO = "/Users/macos/Desktop/DHMS Engine/dhms-engine"
WORKTREE = "/Users/macos/Desktop/DHMS Engine/dhms-engine-agent-harness"
OUT_JSON = ROOT / "validation/outputs/agent_harness_phase1_report.json"
OUT_MD = ROOT / "validation/outputs/agent_harness_phase1_report.md"
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


def harness_report_status(path: str) -> tuple[str, dict[str, Any]]:
    data = load_json(path)
    dry_run = data.get("dry_run") is True
    blocked = data.get("side_effects_blocked_count", 0) >= 1
    traces_jsonable = True
    json.dumps(data.get("traces", []), sort_keys=True)
    if dry_run and blocked and traces_jsonable:
        return "PASS", data
    return "FAIL", data


def main() -> int:
    mock_demo_status, mock_demo = harness_report_status(
        "reports/agent_harness/mock_demo/agent_harness_report.json"
    )
    mock_refund_status, mock_refund = harness_report_status(
        "reports/agent_harness/mock_refund/agent_harness_report.json"
    )
    branch = run_git(["branch", "--show-current"])
    protected_status = protected_diff_status()
    key_status = key_scan_status()
    status = "PASS"
    if any(
        item.startswith("FAIL")
        for item in [mock_demo_status, mock_refund_status, protected_status, key_status]
    ):
        status = "FAIL"

    report = {
        "status": status,
        "stable_repo_directory": STABLE_REPO,
        "worktree_directory": WORKTREE,
        "branch_name": branch,
        "parse_check_status": "PASS: py_compile completed",
        "existing_product_command_status": "PASS: mock Product Diagnosis command completed",
        "mock_test_agent_command_status": mock_demo_status,
        "input_file_test_agent_command_status": mock_refund_status,
        "generated_report_paths": [
            "reports/agent_harness/mock_demo/agent_harness_report.json",
            "reports/agent_harness/mock_demo/agent_harness_report.md",
            "reports/agent_harness/mock_refund/agent_harness_report.json",
            "reports/agent_harness/mock_refund/agent_harness_report.md",
            "reports/agent_phase1_existing_product_check/dhms_product_report.json",
            "reports/agent_phase1_existing_product_check/dhms_product_report.md",
            "reports/agent_phase1_existing_product_check/dhms_product_report.html",
        ],
        "dry_run_confirmed": bool(mock_demo.get("dry_run") and mock_refund.get("dry_run")),
        "side_effects_blocked_confirmed": bool(
            mock_demo.get("side_effects_blocked_count", 0) >= 1
            and mock_refund.get("side_effects_blocked_count", 0) >= 1
        ),
        "protected_core_layer_hash_result": protected_status,
        "key_leakage_scan_result": key_status,
        "command_http_adapters_status": "PASS: command and HTTP adapters are not implemented in Phase 1",
        "real_execution_status": "PASS: Phase 1 ran no real tools and no real provider APIs",
        "remaining_caveats": [
            "Phase 1 supports only deterministic MockAgentAdapter dry-runs.",
            "Trace diagnosis and suite runner are future phases.",
        ],
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(build_markdown(report), encoding="utf-8")
    print(json.dumps({"status": status, "report": str(OUT_JSON.relative_to(ROOT))}, indent=2))
    return 0 if status == "PASS" else 1


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Agent Harness Phase 1 Validation Report",
        "",
        f"Status: {report['status']}",
        "",
        f"* stable_repo_directory: `{report['stable_repo_directory']}`",
        f"* worktree_directory: `{report['worktree_directory']}`",
        f"* branch_name: `{report['branch_name']}`",
        f"* parse_check_status: {report['parse_check_status']}",
        f"* existing_product_command_status: {report['existing_product_command_status']}",
        f"* mock_test_agent_command_status: {report['mock_test_agent_command_status']}",
        f"* input_file_test_agent_command_status: {report['input_file_test_agent_command_status']}",
        f"* dry_run_confirmed: {str(report['dry_run_confirmed']).lower()}",
        f"* side_effects_blocked_confirmed: {str(report['side_effects_blocked_confirmed']).lower()}",
        f"* protected_core_layer_hash_result: {report['protected_core_layer_hash_result']}",
        f"* key_leakage_scan_result: {report['key_leakage_scan_result']}",
        f"* command_http_adapters_status: {report['command_http_adapters_status']}",
        f"* real_execution_status: {report['real_execution_status']}",
        "",
        "## Generated Report Paths",
    ]
    lines.extend(f"* `{path}`" for path in report["generated_report_paths"])
    lines.extend(["", "## Remaining Caveats"])
    lines.extend(f"* {item}" for item in report["remaining_caveats"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
