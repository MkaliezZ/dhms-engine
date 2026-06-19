#!/usr/bin/env python3
"""Local-safe validation for DHMS Product Diagnosis v1.3."""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "validation" / "outputs"
OUTPUT.mkdir(parents=True, exist_ok=True)


COMMANDS = [
    {
        "name": "parse_check",
        "cmd": ["python3", "-m", "py_compile"],
        "dynamic_py_files": True,
        "real_api": False,
    },
    {
        "name": "product_mock_single",
        "cmd": ["python3", "cli.py", "test", "--input", "Does this agent stay consistent?", "--models", "mock", "--n", "1", "--report", "--output", "reports/diagnosis_mock_single"],
        "real_api": False,
    },
    {
        "name": "suite_mock",
        "cmd": ["python3", "cli.py", "test-suite", "--suite", "cases/llm_core", "--models", "mock", "--n", "1", "--report", "--output", "reports/diagnosis_llm_core_mock"],
        "real_api": False,
    },
]


REQUIRED_PER_CASE_FIELDS = [
    "case_id",
    "case_path",
    "case_category",
    "suite_name",
    "suite_run_id",
    "suite_output_dir",
    "requested_models",
    "trial_count",
    "real_api_used",
    "provider_statuses",
    "diagnosis_version",
    "diagnosis_summary",
    "diagnoses",
    "recommendation_evidence",
    "recommendation_confidence",
]


def main() -> int:
    checks = []
    for item in COMMANDS:
        cmd = list(item["cmd"])
        if item.get("dynamic_py_files"):
            cmd.extend(str(path.relative_to(ROOT)) for path in ROOT.rglob("*.py") if ".venv" not in path.parts)
        checks.append(run_command(item["name"], cmd, item["real_api"]))

    suite_path = ROOT / "reports" / "diagnosis_llm_core_mock" / "suite_report.json"
    product_path = ROOT / "reports" / "diagnosis_mock_single" / "dhms_product_report.json"
    deepseek_suite_path = ROOT / "reports" / "diagnosis_llm_core_deepseek_flash" / "suite_report.json"
    schema_check = check_schema(suite_path, product_path)
    leak_check = key_leak_scan([
        ROOT / "reports" / "diagnosis_llm_core_mock",
        ROOT / "reports" / "diagnosis_mock_single",
        ROOT / "reports" / "diagnosis_llm_core_deepseek_flash",
        ROOT / "product",
        ROOT / "docs",
        ROOT / "README_PRODUCT.md",
    ])
    report = {
        "status": "PASS" if all(check["passed"] for check in checks) and schema_check["passed"] and leak_check["passed"] else "FAIL",
        "commands_run": checks,
        "report_paths_generated": {
            "product_mock_single": str(product_path.relative_to(ROOT)),
            "suite_mock": str(suite_path.relative_to(ROOT)),
            "suite_deepseek_flash": str(deepseek_suite_path.relative_to(ROOT)) if deepseek_suite_path.exists() else "not_run_or_not_available",
        },
        "deepseek_suite_report_present": deepseek_suite_path.exists(),
        "diagnosis_fields_present": schema_check["diagnosis_fields_present"],
        "per_case_schema_fields_present": schema_check["per_case_schema_fields_present"],
        "missing_schema_fields": schema_check["missing_schema_fields"],
        "key_leakage_scan": leak_check,
        "v2_metrics_overridden": schema_check["v2_metrics_overridden"],
        "remaining_caveats": [
            "This validator is local-safe; DeepSeek suite evidence is included only if it was run separately.",
            "n=1 mock suite validates schema and deterministic diagnosis wiring, not stochastic stability.",
            "Expected property checker is heuristic and should be reviewed by a human.",
        ],
    }
    write_reports(report)
    print(json.dumps({"status": report["status"], "checks": len(checks) + 2, "report": "validation/outputs/diagnosis_v13_validation_report.json"}, indent=2))
    return 0 if report["status"] == "PASS" else 1


def run_command(name: str, cmd: list[str], real_api: bool) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {
        "name": name,
        "cmd": cmd,
        "passed": proc.returncode == 0,
        "real_api": real_api,
        "output_snippet": (proc.stdout + proc.stderr)[-1200:],
    }


def check_schema(suite_path: Path, product_path: Path) -> dict[str, Any]:
    missing: dict[str, list[str]] = {}
    suite = json.loads(suite_path.read_text(encoding="utf-8")) if suite_path.exists() else {}
    product = json.loads(product_path.read_text(encoding="utf-8")) if product_path.exists() else {}
    case_results = suite.get("case_results", [])
    first_case = case_results[0] if case_results else {}
    for field in REQUIRED_PER_CASE_FIELDS:
        if field not in first_case:
            missing.setdefault("suite_first_case", []).append(field)
        if field in {"suite_name", "suite_run_id", "suite_output_dir"}:
            continue
        if field not in product:
            missing.setdefault("product_single", []).append(field)
    summary = suite.get("summary", {})
    diagnosis_fields = all(key in summary for key in ["diagnosis_summary", "diagnosis_distribution", "top_actionable_cases"])
    per_case_fields = not missing
    return {
        "passed": diagnosis_fields and per_case_fields,
        "diagnosis_fields_present": diagnosis_fields,
        "per_case_schema_fields_present": per_case_fields,
        "missing_schema_fields": missing,
        "v2_metrics_overridden": bool(summary.get("v2_metrics_overridden") or product.get("calibration", {}).get("current_run", {}).get("v2_metrics_overridden")),
    }


def key_leak_scan(paths: list[Path]) -> dict[str, Any]:
    pattern = re.compile(r"sk-[A-Za-z0-9_\-]{12,}|DEEPSEEK_API_KEY=|OPENAI_API_KEY=|ANTHROPIC_API_KEY=")
    leak_files = []
    checked = 0
    for root in paths:
        files = [root] if root.is_file() else list(root.rglob("*"))
        for path in files:
            if not path.is_file() or path.suffix.lower() not in {".py", ".md", ".json", ".html", ".txt"}:
                continue
            checked += 1
            text = path.read_text(encoding="utf-8", errors="ignore")
            if pattern.search(text):
                leak_files.append(str(path.relative_to(ROOT)))
    return {"passed": not leak_files, "checked_files": checked, "leak_files": leak_files}


def write_reports(report: dict[str, Any]) -> None:
    json_path = OUTPUT / "diagnosis_v13_validation_report.json"
    md_path = OUTPUT / "diagnosis_v13_validation_report.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# DHMS Product Diagnosis v1.3 Validation",
        "",
        f"Status: {report['status']}",
        "",
        "## Commands Run",
        "",
    ]
    for item in report["commands_run"]:
        lines.append(f"* {item['name']}: {'PASS' if item['passed'] else 'FAIL'}")
    lines.extend([
        "",
        "## Report Paths Generated",
        "",
    ])
    for key, value in report["report_paths_generated"].items():
        lines.append(f"* {key}: {value}")
    lines.extend([
        "",
        "## Schema Checks",
        "",
        f"* diagnosis_fields_present: {report['diagnosis_fields_present']}",
        f"* per_case_schema_fields_present: {report['per_case_schema_fields_present']}",
        f"* v2_metrics_overridden: {report['v2_metrics_overridden']}",
        "",
        "## Key Leakage Scan",
        "",
        f"* passed: {report['key_leakage_scan']['passed']}",
        f"* checked_files: {report['key_leakage_scan']['checked_files']}",
        "",
        "## Remaining Caveats",
        "",
    ])
    for caveat in report["remaining_caveats"]:
        lines.append(f"* {caveat}")
    md_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
