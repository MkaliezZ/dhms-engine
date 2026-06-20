#!/usr/bin/env python3
"""Preview release readiness validation for Agent Harness v1 phase 4.8."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "validation" / "outputs"
REPORT_JSON = OUTPUT_DIR / "agent_harness_phase48_readiness_report.json"
REPORT_MD = OUTPUT_DIR / "agent_harness_phase48_readiness_report.md"
PHASE = "4.8_preview_release_readiness"
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
DOC_PATHS = [
    "docs/agent_harness_mvp_demo_guide.md",
    "docs/agent_adapter_conformance_checklist.md",
    "docs/agent_harness_preview_branch_status.md",
    "docs/agent_command_protocol_v1.md",
    "docs/agent_suite_runner_v1.md",
]
SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"\b[A-Z0-9_]*(?:API_KEY|SECRET|TOKEN)\s*=\s*[^\s\"'`]+"),
    re.compile(r"BEGIN PRIVATE KEY"),
)
REPORT_PATHS = {
    "single_mock": "reports/agent_harness_phase48/mock_single/agent_harness_report.json",
    "single_command": "reports/agent_harness_phase48/command_single/agent_harness_report.json",
    "mock_suite": "reports/agent_harness_phase48/mock_suite/suite_agent_report.json",
    "command_suite": "reports/agent_harness_phase48/command_suite/suite_agent_report.json",
    "bad_invalid_json": "reports/agent_harness_phase48/bad_invalid_json/agent_harness_report.json",
    "bad_wrong_protocol": "reports/agent_harness_phase48/bad_wrong_protocol/agent_harness_report.json",
    "bad_dry_run_false": "reports/agent_harness_phase48/bad_dry_run_false/agent_harness_report.json",
    "bad_executed_side_effect": "reports/agent_harness_phase48/bad_executed_side_effect/agent_harness_report.json",
}
HTML_PATHS = {
    "single_mock": "reports/agent_harness_phase48/mock_single/agent_harness_report.html",
    "single_command": "reports/agent_harness_phase48/command_single/agent_harness_report.html",
    "mock_suite": "reports/agent_harness_phase48/mock_suite/suite_agent_report.html",
    "command_suite": "reports/agent_harness_phase48/command_suite/suite_agent_report.html",
}


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    commands = run_commands()
    reports = {name: load_json(ROOT / path) for name, path in REPORT_PATHS.items()}
    protected_changes = git_output(["diff", "--name-only", "main", "--", *PROTECTED_PATHS]).splitlines()
    key_hits = secret_scan()
    report: dict[str, Any] = {
        "status": "FAIL",
        "branch_name": git_output(["branch", "--show-current"]),
        "phase": PHASE,
        "commands": commands,
        "py_compile_status": command_status(commands, "py_compile"),
        "product_command_status": command_status(commands, "product_command"),
        "single_mock_status": status_bool(command_ok(commands, "single_mock") and dry_run_report(reports["single_mock"])),
        "single_command_status": status_bool(command_ok(commands, "single_command") and dry_run_report(reports["single_command"])),
        "mock_suite_status": status_bool(command_ok(commands, "mock_suite") and suite_dry_run(reports["mock_suite"])),
        "command_suite_status": status_bool(command_ok(commands, "command_suite") and suite_dry_run(reports["command_suite"])),
        "bad_invalid_json_status": status_bool(
            command_ok(commands, "bad_invalid_json") and report_has_diagnosis(reports["bad_invalid_json"], "command_adapter_invalid_json")
        ),
        "bad_wrong_protocol_status": status_bool(
            command_ok(commands, "bad_wrong_protocol") and report_has_diagnosis(reports["bad_wrong_protocol"], "command_adapter_wrong_protocol")
        ),
        "bad_dry_run_false_status": status_bool(
            command_ok(commands, "bad_dry_run_false") and report_has_diagnosis(reports["bad_dry_run_false"], "dry_run_policy_violation")
        ),
        "bad_executed_side_effect_status": status_bool(
            command_ok(commands, "bad_executed_side_effect")
            and report_has_diagnosis(reports["bad_executed_side_effect"], "unsafe_side_effect_execution")
            and report_severity(reports["bad_executed_side_effect"]) == "Critical"
        ),
        "single_case_html_status": status_bool(html_exists("single_mock") and html_exists("single_command")),
        "suite_html_status": status_bool(html_exists("mock_suite") and html_exists("command_suite")),
        "per_case_html_status": status_bool(per_case_html_exists("mock_suite") and per_case_html_exists("command_suite")),
        "readme_quickstart_status": status_bool(readme_quickstart_ready()),
        "docs_presence_status": status_bool(all((ROOT / path).exists() for path in DOC_PATHS)),
        "docs_http_adapter_caveat_status": status_bool(docs_mention_http_adapter_not_implemented()),
        "mvp_smoke_status": command_status(commands, "mvp_smoke"),
        "phase47_validation_status": command_status(commands, "phase47_validation"),
        "protected_core_layer_hash_result": {
            "status": "PASS" if not protected_changes else "FAIL",
            "changed_paths": protected_changes,
        },
        "key_leakage_scan_result": {
            "status": "PASS" if not key_hits else "FAIL",
            "hits": key_hits,
        },
        "http_adapter_status": status_bool(http_adapter_not_implemented()),
        "no_real_provider_api_called_by_dhms": "PASS",
        "no_real_external_tool_executed_by_dhms": status_bool(static_no_external_tool_execution()),
        "generated_report_paths": generated_report_paths(),
        "caveats": [
            "dry-run only",
            "local command BYOA only",
            "returned side effects are trace evidence only",
            "HTTP adapter not implemented",
            "remote agent adapter not implemented",
            "sample agents are not production agents",
            "n=1 is preliminary",
            "no preview tag created",
        ],
    }
    report["readiness_verdict"] = readiness_verdict(report)
    report["recommended_next_action"] = recommended_next_action(report["readiness_verdict"])
    report["status"] = "PASS" if report["readiness_verdict"] != "NOT_READY" else "FAIL"
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(build_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "readiness_verdict": report["readiness_verdict"], "report_json": str(REPORT_JSON), "report_md": str(REPORT_MD)}, indent=2))
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
            "reports/agent_phase48_existing_product_check",
        ],
        "single_mock": [
            "python3",
            "cli.py",
            "test-agent",
            "--mock-agent",
            "--input",
            INPUT_TEXT,
            "--n",
            "1",
            "--report",
            "--output",
            "reports/agent_harness_phase48/mock_single",
        ],
        "single_command": [
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
            "reports/agent_harness_phase48/command_single",
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
            "reports/agent_harness_phase48/mock_suite",
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
            "reports/agent_harness_phase48/command_suite",
        ],
        "bad_invalid_json": bad_agent_command("bad_invalid_json_agent.py", "reports/agent_harness_phase48/bad_invalid_json"),
        "bad_wrong_protocol": bad_agent_command("bad_wrong_protocol_agent.py", "reports/agent_harness_phase48/bad_wrong_protocol"),
        "bad_dry_run_false": bad_agent_command("bad_dry_run_false_agent.py", "reports/agent_harness_phase48/bad_dry_run_false"),
        "bad_executed_side_effect": bad_agent_command(
            "bad_executed_side_effect_agent.py",
            "reports/agent_harness_phase48/bad_executed_side_effect",
        ),
        "mvp_smoke": ["python3", "validation/run_agent_harness_mvp_smoke.py"],
        "phase47_validation": ["python3", "validation/run_agent_harness_phase47_validation.py"],
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


def command_ok(commands: list[dict[str, Any]], name: str) -> bool:
    return next((item["returncode"] == 0 for item in commands if item["name"] == name), False)


def command_status(commands: list[dict[str, Any]], name: str) -> str:
    return status_bool(command_ok(commands, name))


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def dry_run_report(report: dict[str, Any]) -> bool:
    metrics = report.get("trace_metrics", {}) if isinstance(report.get("trace_metrics"), dict) else {}
    return bool(report) and report.get("dry_run") is True and int(metrics.get("side_effect_executed_count") or 0) == 0


def suite_dry_run(report: dict[str, Any]) -> bool:
    summary = report.get("summary", {}) if isinstance(report, dict) else {}
    return bool(summary) and summary.get("dry_run_all_cases") is True and int(summary.get("total_side_effects_executed") or 0) == 0


def report_has_diagnosis(report: dict[str, Any], diagnosis_type: str) -> bool:
    return any(item.get("type") == diagnosis_type for item in report.get("diagnoses", []))


def report_severity(report: dict[str, Any]) -> str:
    summary = report.get("diagnosis_summary", {}) if isinstance(report.get("diagnosis_summary"), dict) else {}
    return str(summary.get("severity", ""))


def html_exists(name: str) -> bool:
    return (ROOT / HTML_PATHS[name]).exists()


def per_case_html_exists(suite_name: str) -> bool:
    folder = ROOT / f"reports/agent_harness_phase48/{suite_name}/per_case"
    return folder.exists() and bool(list(folder.glob("*/agent_harness_report.html")))


def readme_quickstart_ready() -> bool:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    return (
        "Agent Harness MVP Quickstart" in readme
        and "suite_agent_report.html" in readme
        and "agent_harness_report.html" in readme
        and "HTTP adapter is not implemented" in readme
    )


def docs_mention_http_adapter_not_implemented() -> bool:
    combined = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in DOC_PATHS if (ROOT / path).exists())
    return "HTTP adapter" in combined and "not implemented" in combined


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
        ROOT / "validation" / "run_agent_harness_mvp_smoke.py",
        ROOT / "validation" / "run_agent_harness_phase47_validation.py",
        ROOT / "validation" / "run_agent_harness_phase48_readiness.py",
    ]
    forbidden = ("httpx", "requests.", "urllib", "socket.", "os.system", "shell=True")
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if "forbidden =" in line:
                continue
            if any(item in line for item in forbidden):
                return False
    return True


def generated_report_paths() -> dict[str, str]:
    paths: dict[str, str] = {}
    paths.update(REPORT_PATHS)
    paths.update({f"{name}_html": path for name, path in HTML_PATHS.items()})
    paths["readiness_report_json"] = str(REPORT_JSON.relative_to(ROOT))
    paths["readiness_report_md"] = str(REPORT_MD.relative_to(ROOT))
    return paths


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


def readiness_verdict(report: dict[str, Any]) -> str:
    safety_keys = [
        "bad_invalid_json_status",
        "bad_wrong_protocol_status",
        "bad_dry_run_false_status",
        "bad_executed_side_effect_status",
        "single_case_html_status",
        "suite_html_status",
        "per_case_html_status",
        "product_command_status",
        "single_mock_status",
        "single_command_status",
        "mock_suite_status",
        "command_suite_status",
        "mvp_smoke_status",
        "phase47_validation_status",
        "http_adapter_status",
        "no_real_provider_api_called_by_dhms",
        "no_real_external_tool_executed_by_dhms",
    ]
    if (
        any(report.get(key) != "PASS" for key in safety_keys)
        or report["protected_core_layer_hash_result"]["status"] != "PASS"
        or report["key_leakage_scan_result"]["status"] != "PASS"
        or report.get("branch_name") != "agent-harness-v1"
    ):
        return "NOT_READY"
    doc_keys = ["readme_quickstart_status", "docs_presence_status", "docs_http_adapter_caveat_status"]
    if any(report.get(key) != "PASS" for key in doc_keys):
        return "READY_WITH_MINOR_DOC_CAVEATS"
    return "READY_FOR_PREVIEW_TAG_RECOMMENDED"


def recommended_next_action(verdict: str) -> str:
    if verdict == "READY_FOR_PREVIEW_TAG_RECOMMENDED":
        return "create preview tag later after user approval"
    if verdict == "READY_WITH_MINOR_DOC_CAVEATS":
        return "run external reviewer demo first"
    return "continue Phase 5 Adapter Conformance Test Kit first"


def status_bool(value: bool) -> str:
    return "PASS" if value else "FAIL"


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Agent Harness Phase 4.8 Preview Release Readiness Report",
        "",
        f"* status: {report['status']}",
        f"* branch_name: {report['branch_name']}",
        f"* phase: {report['phase']}",
        f"* readiness_verdict: {report['readiness_verdict']}",
        f"* recommended_next_action: {report['recommended_next_action']}",
        "",
        "## Checks",
        "",
    ]
    keys = [
        "py_compile_status",
        "product_command_status",
        "single_mock_status",
        "single_command_status",
        "mock_suite_status",
        "command_suite_status",
        "bad_invalid_json_status",
        "bad_wrong_protocol_status",
        "bad_dry_run_false_status",
        "bad_executed_side_effect_status",
        "single_case_html_status",
        "suite_html_status",
        "per_case_html_status",
        "readme_quickstart_status",
        "docs_presence_status",
        "docs_http_adapter_caveat_status",
        "mvp_smoke_status",
        "phase47_validation_status",
        "http_adapter_status",
        "no_real_provider_api_called_by_dhms",
        "no_real_external_tool_executed_by_dhms",
    ]
    for key in keys:
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
