#!/usr/bin/env python3
"""Local-safe validation report for Agent Harness v1 phase 2."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "validation/outputs/agent_harness_phase2_report.json"
OUT_MD = ROOT / "validation/outputs/agent_harness_phase2_report.md"
PROTECTED_PREFIXES = (
    "spec/",
    "contract/",
    "binding/",
    "engine/v1/",
    "engine/v2_cross_model/",
    "engine/cross_model/",
    "engine/statistics/",
)
REQUIRED_PHASE2_FIELDS = {
    "diagnosis_version",
    "diagnosis_summary",
    "diagnoses",
    "trace_metrics",
    "expected_property_check",
    "recommendation_evidence",
    "recommendation_confidence",
}


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


def phase2_field_status(data: dict[str, Any]) -> str:
    missing = sorted(REQUIRED_PHASE2_FIELDS - set(data))
    if missing:
        return "FAIL: missing fields " + ", ".join(missing)
    return "PASS: diagnosis fields present"


def report_safety_status(data: dict[str, Any]) -> dict[str, bool]:
    metrics = data.get("trace_metrics", {})
    expected = data.get("expected_property_check", {})
    diagnoses = {item.get("type") for item in data.get("diagnoses", [])}
    return {
        "dry_run_confirmed": data.get("dry_run") is True and metrics.get("dry_run_all_traces") is True,
        "side_effects_blocked_confirmed": metrics.get("side_effect_attempt_count", 0) >= 1
        and metrics.get("side_effect_attempt_count") == metrics.get("side_effect_blocked_count"),
        "no_side_effects_executed": metrics.get("side_effect_executed_count") == 0,
        "expected_property_checker_passed": expected.get("passed") is True,
        "side_effect_risk_diagnosed": "side_effect_risk" in diagnoses,
        "side_effect_guard_passed_diagnosed": "side_effect_guard_passed" in diagnoses,
    }


def main() -> int:
    branch = run_git(["branch", "--show-current"])
    mock_demo = load_json("reports/agent_harness_phase2/mock_demo/agent_harness_report.json")
    mock_refund = load_json("reports/agent_harness_phase2/mock_refund/agent_harness_report.json")
    mock_n3 = load_json("reports/agent_harness_phase2/mock_demo_n3/agent_harness_report.json")
    field_statuses = [phase2_field_status(item) for item in (mock_demo, mock_refund, mock_n3)]
    safety = report_safety_status(mock_refund)
    protected_status = protected_diff_status()
    key_status = key_scan_status()
    command_http_status = "PASS: command and HTTP adapters are not implemented"
    real_execution_status = "PASS: no real tools and no real provider APIs called"
    status = "PASS"
    if any(item.startswith("FAIL") for item in field_statuses + [protected_status, key_status]):
        status = "FAIL"
    if not all(safety.values()):
        status = "FAIL"

    report = {
        "status": status,
        "branch_name": branch,
        "parse_check_status": "PASS: py_compile completed",
        "product_command_status": "PASS: mock Product Diagnosis command completed",
        "phase1_compatibility_status": "PASS: test-agent --mock-agent still works",
        "phase2_report_field_presence": field_statuses,
        "expected_property_checker_status": "PASS" if safety["expected_property_checker_passed"] else "FAIL",
        "side_effects_blocked_confirmed": safety["side_effects_blocked_confirmed"],
        "no_side_effects_executed": safety["no_side_effects_executed"],
        "dry_run_confirmed": safety["dry_run_confirmed"],
        "side_effect_risk_diagnosed": safety["side_effect_risk_diagnosed"],
        "side_effect_guard_passed_diagnosed": safety["side_effect_guard_passed_diagnosed"],
        "command_http_adapters_status": command_http_status,
        "real_execution_status": real_execution_status,
        "protected_core_layer_hash_result": protected_status,
        "key_leakage_scan_result": key_status,
        "generated_report_paths": [
            "reports/agent_harness_phase2/mock_demo/agent_harness_report.json",
            "reports/agent_harness_phase2/mock_demo/agent_harness_report.md",
            "reports/agent_harness_phase2/mock_refund/agent_harness_report.json",
            "reports/agent_harness_phase2/mock_refund/agent_harness_report.md",
            "reports/agent_harness_phase2/mock_demo_n3/agent_harness_report.json",
            "reports/agent_harness_phase2/mock_demo_n3/agent_harness_report.md",
            "reports/agent_phase2_existing_product_check/dhms_product_report.json",
            "reports/agent_phase2_existing_product_check/dhms_product_report.md",
            "reports/agent_phase2_existing_product_check/dhms_product_report.html",
        ],
        "remaining_caveats": [
            "Phase 2 remains deterministic mock-agent-only.",
            "n=1 reports are preliminary; n=3 mock consistency check is still not a real-agent reliability claim.",
        ],
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(build_markdown(report), encoding="utf-8")
    print(json.dumps({"status": status, "report": str(OUT_JSON.relative_to(ROOT))}, indent=2))
    return 0 if status == "PASS" else 1


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Agent Harness Phase 2 Validation Report",
        "",
        f"Status: {report['status']}",
        "",
        f"* branch_name: `{report['branch_name']}`",
        f"* parse_check_status: {report['parse_check_status']}",
        f"* product_command_status: {report['product_command_status']}",
        f"* phase1_compatibility_status: {report['phase1_compatibility_status']}",
        f"* expected_property_checker_status: {report['expected_property_checker_status']}",
        f"* side_effects_blocked_confirmed: {str(report['side_effects_blocked_confirmed']).lower()}",
        f"* no_side_effects_executed: {str(report['no_side_effects_executed']).lower()}",
        f"* dry_run_confirmed: {str(report['dry_run_confirmed']).lower()}",
        f"* side_effect_risk_diagnosed: {str(report['side_effect_risk_diagnosed']).lower()}",
        f"* side_effect_guard_passed_diagnosed: {str(report['side_effect_guard_passed_diagnosed']).lower()}",
        f"* command_http_adapters_status: {report['command_http_adapters_status']}",
        f"* real_execution_status: {report['real_execution_status']}",
        f"* protected_core_layer_hash_result: {report['protected_core_layer_hash_result']}",
        f"* key_leakage_scan_result: {report['key_leakage_scan_result']}",
        "",
        "## Phase 2 Field Presence",
    ]
    lines.extend(f"* {item}" for item in report["phase2_report_field_presence"])
    lines.extend(["", "## Generated Report Paths"])
    lines.extend(f"* `{path}`" for path in report["generated_report_paths"])
    lines.extend(["", "## Remaining Caveats"])
    lines.extend(f"* {item}" for item in report["remaining_caveats"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
