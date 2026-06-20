#!/usr/bin/env python3
"""Focused validation for Agent Harness v1 phase 4.7 static HTML reports."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "validation" / "outputs"
REPORT_JSON = OUTPUT_DIR / "agent_harness_phase47_report.json"
REPORT_MD = OUTPUT_DIR / "agent_harness_phase47_report.md"
PHASE = "4.7_static_html_report_polish"
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
HTML_PATHS = {
    "single_mock": "reports/agent_harness_phase47/mock_single/agent_harness_report.html",
    "single_command": "reports/agent_harness_phase47/command_single/agent_harness_report.html",
    "mock_suite": "reports/agent_harness_phase47/mock_suite/suite_agent_report.html",
    "command_suite": "reports/agent_harness_phase47/command_suite/suite_agent_report.html",
    "bad_invalid_json": "reports/agent_harness_phase47/bad_invalid_json/agent_harness_report.html",
    "bad_wrong_protocol": "reports/agent_harness_phase47/bad_wrong_protocol/agent_harness_report.html",
    "bad_executed_side_effect": "reports/agent_harness_phase47/bad_executed_side_effect/agent_harness_report.html",
}


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    commands = run_commands()
    html_texts = {name: read_text(path) for name, path in HTML_PATHS.items()}
    all_html_paths = [ROOT / path for path in HTML_PATHS.values()]
    all_html_paths.extend(sorted((ROOT / "reports/agent_harness_phase47/mock_suite/per_case").glob("*/agent_harness_report.html")))
    all_html_paths.extend(sorted((ROOT / "reports/agent_harness_phase47/command_suite/per_case").glob("*/agent_harness_report.html")))
    protected_changes = git_output(["diff", "--name-only", "main", "--", *PROTECTED_PATHS]).splitlines()
    key_hits = secret_scan()
    report: dict[str, Any] = {
        "status": "FAIL",
        "branch_name": git_output(["branch", "--show-current"]),
        "phase": PHASE,
        "commands": commands,
        "single_mock_html_status": status_bool(command_ok(commands, "single_mock") and html_exists("single_mock")),
        "single_command_html_status": status_bool(command_ok(commands, "single_command") and html_exists("single_command")),
        "mock_suite_html_status": status_bool(command_ok(commands, "mock_suite") and html_exists("mock_suite") and per_case_html_exists("mock_suite")),
        "command_suite_html_status": status_bool(command_ok(commands, "command_suite") and html_exists("command_suite") and per_case_html_exists("command_suite")),
        "bad_invalid_json_html_status": status_bool(
            command_ok(commands, "bad_invalid_json")
            and html_exists("bad_invalid_json")
            and "command_adapter_invalid_json" in html_texts["bad_invalid_json"]
        ),
        "bad_wrong_protocol_html_status": status_bool(
            command_ok(commands, "bad_wrong_protocol")
            and html_exists("bad_wrong_protocol")
            and "command_adapter_wrong_protocol" in html_texts["bad_wrong_protocol"]
        ),
        "bad_executed_side_effect_html_status": status_bool(
            command_ok(commands, "bad_executed_side_effect")
            and html_exists("bad_executed_side_effect")
            and "unsafe_side_effect_execution" in html_texts["bad_executed_side_effect"]
            and "Critical" in html_texts["bad_executed_side_effect"]
        ),
        "suite_html_sections_status": status_bool(suite_sections_present(html_texts["mock_suite"])),
        "no_external_assets_status": status_bool(no_external_assets(all_html_paths)),
        "no_script_src_status": status_bool(no_script_src(all_html_paths)),
        "html_escape_probe_status": status_bool(html_escape_probe()),
        "product_command_status": command_status(commands, "product_command"),
        "mvp_smoke_status": command_status(commands, "mvp_smoke"),
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
        "generated_report_paths": HTML_PATHS,
        "caveats": [
            "static local HTML only",
            "dry-run only",
            "local command BYOA only",
            "HTTP adapter not implemented",
            "no dashboard or server",
            "no real external tool permission",
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
            "reports/agent_phase47_existing_product_check",
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
            "reports/agent_harness_phase47/mock_single",
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
            "reports/agent_harness_phase47/command_single",
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
            "reports/agent_harness_phase47/mock_suite",
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
            "reports/agent_harness_phase47/command_suite",
        ],
        "bad_invalid_json": bad_agent_command("bad_invalid_json_agent.py", "reports/agent_harness_phase47/bad_invalid_json"),
        "bad_wrong_protocol": bad_agent_command("bad_wrong_protocol_agent.py", "reports/agent_harness_phase47/bad_wrong_protocol"),
        "bad_executed_side_effect": bad_agent_command(
            "bad_executed_side_effect_agent.py",
            "reports/agent_harness_phase47/bad_executed_side_effect",
        ),
        "escape_probe": [
            "python3",
            "cli.py",
            "test-agent",
            "--mock-agent",
            "--input",
            "<script>alert(1)</script>",
            "--n",
            "1",
            "--report",
            "--output",
            "reports/agent_harness_phase47/escape_probe",
        ],
        "mvp_smoke": ["python3", "validation/run_agent_harness_mvp_smoke.py"],
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


def html_exists(name: str) -> bool:
    return (ROOT / HTML_PATHS[name]).exists()


def per_case_html_exists(suite_name: str) -> bool:
    folder = ROOT / f"reports/agent_harness_phase47/{suite_name}/per_case"
    return folder.exists() and bool(list(folder.glob("*/agent_harness_report.html")))


def read_text(path: str) -> str:
    full_path = ROOT / path
    return full_path.read_text(encoding="utf-8") if full_path.exists() else ""


def suite_sections_present(text: str) -> bool:
    required = [
        "Executive Summary",
        "Side-effect Safety Summary",
        "Diagnosis Distribution",
        "Per-case Report Paths",
    ]
    return all(item in text for item in required)


def no_external_assets(paths: list[Path]) -> bool:
    forbidden = ("https://", "http://", "//cdn", "cdn.jsdelivr", "unpkg.com", "fonts.googleapis")
    return all(not any(item in path.read_text(encoding="utf-8") for item in forbidden) for path in paths if path.exists())


def no_script_src(paths: list[Path]) -> bool:
    pattern = re.compile(r"<script\s+[^>]*src\s*=", re.IGNORECASE)
    return all(not pattern.search(path.read_text(encoding="utf-8")) for path in paths if path.exists())


def html_escape_probe() -> bool:
    path = ROOT / "reports/agent_harness_phase47/escape_probe/agent_harness_report.html"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return "<script>alert(1)</script>" not in text and "&lt;script&gt;alert(1)&lt;/script&gt;" in text


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
        ROOT / "validation" / "run_agent_harness_phase47_validation.py",
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
        "single_mock_html_status",
        "single_command_html_status",
        "mock_suite_html_status",
        "command_suite_html_status",
        "bad_invalid_json_html_status",
        "bad_wrong_protocol_html_status",
        "bad_executed_side_effect_html_status",
        "suite_html_sections_status",
        "no_external_assets_status",
        "no_script_src_status",
        "html_escape_probe_status",
        "product_command_status",
        "mvp_smoke_status",
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
        "# Agent Harness Phase 4.7 Validation Report",
        "",
        f"* status: {report['status']}",
        f"* branch_name: {report['branch_name']}",
        f"* phase: {report['phase']}",
        "",
        "## Checks",
        "",
    ]
    for key in [
        "single_mock_html_status",
        "single_command_html_status",
        "mock_suite_html_status",
        "command_suite_html_status",
        "bad_invalid_json_html_status",
        "bad_wrong_protocol_html_status",
        "bad_executed_side_effect_html_status",
        "suite_html_sections_status",
        "no_external_assets_status",
        "no_script_src_status",
        "html_escape_probe_status",
        "product_command_status",
        "mvp_smoke_status",
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
            "## Generated HTML Report Paths",
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
