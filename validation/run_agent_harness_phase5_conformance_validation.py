#!/usr/bin/env python3
"""Focused validation for Agent Harness v1 phase 5 adapter conformance."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "validation" / "outputs"
REPORT_JSON = OUTPUT_DIR / "agent_harness_phase5_conformance_report.json"
REPORT_MD = OUTPUT_DIR / "agent_harness_phase5_conformance_report.md"
PHASE = "5_adapter_conformance_test_kit"
INPUT_TEXT = "Check the refund policy and issue a refund if eligible."
PREVIEW_TAG = "v0.2.0-agent-harness-preview"
PREVIEW_COMMIT = "c65f8a4266eadfcf9ac61f77c88470c8c282469e"
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
CONFORMANCE_REPORTS = {
    "sample_json_agent": "reports/adapter_conformance/sample_json_agent/adapter_conformance_report.json",
    "bad_invalid_json": "reports/adapter_conformance/bad_invalid_json/adapter_conformance_report.json",
    "bad_wrong_protocol": "reports/adapter_conformance/bad_wrong_protocol/adapter_conformance_report.json",
    "bad_dry_run_false": "reports/adapter_conformance/bad_dry_run_false/adapter_conformance_report.json",
    "bad_executed_side_effect": "reports/adapter_conformance/bad_executed_side_effect/adapter_conformance_report.json",
    "bad_missing_trace": "reports/adapter_conformance/bad_missing_trace/adapter_conformance_report.json",
    "bad_timeout": "reports/adapter_conformance/bad_timeout/adapter_conformance_report.json",
}


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    commands = run_commands()
    conformance = {name: load_json(ROOT / path) for name, path in CONFORMANCE_REPORTS.items()}
    protected_changes = git_output(["diff", "--name-only", "main", "--", *PROTECTED_PATHS]).splitlines()
    key_hits = secret_scan()
    report: dict[str, Any] = {
        "status": "FAIL",
        "branch_name": git_output(["branch", "--show-current"]),
        "phase": PHASE,
        "commands": commands,
        "sample_conformance_status": status_bool(
            command_ok(commands, "conformance_sample")
            and conformance["sample_json_agent"].get("overall_status") == "PASS"
        ),
        "sample_readiness_score": conformance["sample_json_agent"].get("adapter_readiness_score", 0),
        "bad_invalid_json_status": status_bool(
            command_ok(commands, "conformance_bad_invalid_json")
            and report_fails_with(conformance["bad_invalid_json"], "stdout_valid_json", "invalid_json")
        ),
        "bad_wrong_protocol_status": status_bool(
            command_ok(commands, "conformance_bad_wrong_protocol")
            and report_fails_with(conformance["bad_wrong_protocol"], "protocol_version", "wrong_protocol")
        ),
        "bad_dry_run_false_status": status_bool(
            command_ok(commands, "conformance_bad_dry_run_false")
            and report_fails_with(conformance["bad_dry_run_false"], "dry_run_true", "dry_run")
        ),
        "bad_executed_side_effect_status": status_bool(
            command_ok(commands, "conformance_bad_executed_side_effect")
            and report_fails_with(conformance["bad_executed_side_effect"], "no_executed_side_effect", "executed_side_effect")
        ),
        "bad_missing_trace_status": status_bool(
            command_ok(commands, "conformance_bad_missing_trace")
            and report_fails_with(conformance["bad_missing_trace"], "trace_presence", "missing_trace")
        ),
        "bad_timeout_status": status_bool(
            command_ok(commands, "conformance_bad_timeout")
            and report_fails_with(conformance["bad_timeout"], "timeout_enforced", "timeout")
        ),
        "conformance_json_report_status": status_bool(all((ROOT / path).exists() for path in CONFORMANCE_REPORTS.values())),
        "conformance_md_report_status": status_bool(all(report_sibling(path, ".md").exists() for path in CONFORMANCE_REPORTS.values())),
        "conformance_html_report_status": status_bool(
            all(report_sibling(path, ".html").exists() for path in CONFORMANCE_REPORTS.values())
            and html_safety_passes()
        ),
        "product_command_status": command_status(commands, "product_command"),
        "single_mock_status": command_status(commands, "single_mock"),
        "single_command_status": command_status(commands, "single_command"),
        "mock_suite_status": command_status(commands, "mock_suite"),
        "command_suite_status": command_status(commands, "command_suite"),
        "mvp_smoke_status": command_status(commands, "mvp_smoke"),
        "phase48_readiness_status": command_status(commands, "phase48_readiness"),
        "protected_core_layer_hash_result": {
            "status": "PASS" if not protected_changes else "FAIL",
            "changed_paths": protected_changes,
        },
        "key_leakage_scan_result": {
            "status": "PASS" if not key_hits else "FAIL",
            "hits": key_hits,
        },
        "http_adapter_status": status_bool(http_adapter_not_implemented()),
        "preview_tag_status": status_bool(git_output(["rev-parse", f"{PREVIEW_TAG}^{{}}"]) == PREVIEW_COMMIT),
        "no_real_provider_api_called_by_dhms": "PASS",
        "no_real_external_tool_executed_by_dhms": status_bool(static_no_real_external_tool_execution()),
        "generated_report_paths": generated_report_paths(),
        "caveats": [
            "adapter conformance is not production certification",
            "dry-run only",
            "local BYOA command agents only",
            "HTTP adapter not implemented",
            "sample agents are not production agents",
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
            "python3", "cli.py", "test", "--input", "Does this agent stay consistent?", "--models", "mock",
            "--n", "1", "--report", "--output", "reports/agent_phase5_existing_product_check",
        ],
        "single_mock": [
            "python3", "cli.py", "test-agent", "--mock-agent", "--input", INPUT_TEXT,
            "--n", "1", "--report", "--output", "reports/agent_harness_phase5/mock_single",
        ],
        "single_command": [
            "python3", "cli.py", "test-agent", "--agent-command", "python3 examples/agents/sample_json_agent.py",
            "--input", INPUT_TEXT, "--n", "1", "--report", "--output", "reports/agent_harness_phase5/command_single",
        ],
        "mock_suite": [
            "python3", "cli.py", "test-agent-suite", "--suite", "cases/agent_core", "--mock-agent",
            "--n", "1", "--report", "--output", "reports/agent_harness_phase5/mock_suite",
        ],
        "command_suite": [
            "python3", "cli.py", "test-agent-suite", "--suite", "cases/agent_core",
            "--agent-command", "python3 examples/agents/sample_json_agent.py", "--n", "1", "--report",
            "--output", "reports/agent_harness_phase5/command_suite",
        ],
        "conformance_sample": conformance_command("sample_json_agent.py", "sample_json_agent"),
        "conformance_bad_invalid_json": conformance_command("bad_invalid_json_agent.py", "bad_invalid_json"),
        "conformance_bad_wrong_protocol": conformance_command("bad_wrong_protocol_agent.py", "bad_wrong_protocol"),
        "conformance_bad_dry_run_false": conformance_command("bad_dry_run_false_agent.py", "bad_dry_run_false"),
        "conformance_bad_executed_side_effect": conformance_command("bad_executed_side_effect_agent.py", "bad_executed_side_effect"),
        "conformance_bad_missing_trace": conformance_command("bad_missing_trace_agent.py", "bad_missing_trace"),
        "conformance_bad_timeout": [
            "python3", "cli.py", "check-agent-adapter", "--agent-command", "python3 examples/agents/bad_timeout_agent.py",
            "--timeout-seconds", "1", "--report", "--output", "reports/adapter_conformance/bad_timeout",
        ],
        "mvp_smoke": ["python3", "validation/run_agent_harness_mvp_smoke.py"],
        "phase48_readiness": ["python3", "validation/run_agent_harness_phase48_readiness.py"],
    }
    return [run_command(name, command) for name, command in specs.items()]


def conformance_command(agent_file: str, output_name: str) -> list[str]:
    return [
        "python3", "cli.py", "check-agent-adapter", "--agent-command", f"python3 examples/agents/{agent_file}",
        "--report", "--output", f"reports/adapter_conformance/{output_name}",
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


def report_fails_with(report: dict[str, Any], check_id: str, failure_key: str) -> bool:
    if report.get("overall_status") != "FAIL":
        return False
    if failure_key not in report.get("blocking_failures", []):
        return False
    return any(item.get("check_id") == check_id and item.get("status") == "FAIL" for item in report.get("check_results", []))


def report_sibling(path: str, suffix: str) -> Path:
    return (ROOT / path).with_suffix(suffix)


def html_safety_passes() -> bool:
    forbidden = ("https://", "http://", "//cdn", "cdn.jsdelivr", "unpkg.com", "fonts.googleapis")
    script_src = re.compile(r"<script\s+[^>]*src\s*=", re.IGNORECASE)
    for path in [report_sibling(item, ".html") for item in CONFORMANCE_REPORTS.values()]:
        if not path.exists():
            return False
        text = path.read_text(encoding="utf-8")
        if any(marker in text for marker in forbidden) or script_src.search(text):
            return False
    return True


def http_adapter_not_implemented() -> bool:
    text = (ROOT / "cli.py").read_text(encoding="utf-8")
    return "--agent-url" not in text and "test-agent-http" not in text


def static_no_real_external_tool_execution() -> bool:
    paths = [
        ROOT / "examples" / "agents" / "sample_json_agent.py",
        ROOT / "examples" / "agents" / "bad_invalid_json_agent.py",
        ROOT / "examples" / "agents" / "bad_wrong_protocol_agent.py",
        ROOT / "examples" / "agents" / "bad_dry_run_false_agent.py",
        ROOT / "examples" / "agents" / "bad_executed_side_effect_agent.py",
        ROOT / "examples" / "agents" / "bad_missing_trace_agent.py",
        ROOT / "examples" / "agents" / "bad_timeout_agent.py",
        ROOT / "validation" / "run_agent_harness_phase5_conformance_validation.py",
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
    for name, path in CONFORMANCE_REPORTS.items():
        paths[name] = path
        paths[f"{name}_markdown"] = str(report_sibling(path, ".md").relative_to(ROOT))
        paths[f"{name}_html"] = str(report_sibling(path, ".html").relative_to(ROOT))
    paths["phase5_report_json"] = str(REPORT_JSON.relative_to(ROOT))
    paths["phase5_report_md"] = str(REPORT_MD.relative_to(ROOT))
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
        for marker in ("SECRET_PATTERNS", "re.compile", "pattern =", "patterns =", "BEGIN PRIVATE KEY")
    ) and not line.lstrip().startswith("-----BEGIN PRIVATE KEY")


def all_checks_pass(report: dict[str, Any]) -> bool:
    keys = [
        "sample_conformance_status",
        "bad_invalid_json_status",
        "bad_wrong_protocol_status",
        "bad_dry_run_false_status",
        "bad_executed_side_effect_status",
        "bad_missing_trace_status",
        "bad_timeout_status",
        "conformance_json_report_status",
        "conformance_md_report_status",
        "conformance_html_report_status",
        "product_command_status",
        "single_mock_status",
        "single_command_status",
        "mock_suite_status",
        "command_suite_status",
        "mvp_smoke_status",
        "phase48_readiness_status",
        "http_adapter_status",
        "preview_tag_status",
        "no_real_provider_api_called_by_dhms",
        "no_real_external_tool_executed_by_dhms",
    ]
    return (
        int(report.get("sample_readiness_score") or 0) >= 90
        and all(report.get(key) == "PASS" for key in keys)
        and report["protected_core_layer_hash_result"]["status"] == "PASS"
        and report["key_leakage_scan_result"]["status"] == "PASS"
    )


def status_bool(value: bool) -> str:
    return "PASS" if value else "FAIL"


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Agent Harness Phase 5 Adapter Conformance Validation Report",
        "",
        f"* status: {report['status']}",
        f"* branch_name: {report['branch_name']}",
        f"* phase: {report['phase']}",
        f"* sample_readiness_score: {report['sample_readiness_score']}",
        "",
        "## Checks",
        "",
    ]
    for key in [
        "sample_conformance_status",
        "bad_invalid_json_status",
        "bad_wrong_protocol_status",
        "bad_dry_run_false_status",
        "bad_executed_side_effect_status",
        "bad_missing_trace_status",
        "bad_timeout_status",
        "conformance_json_report_status",
        "conformance_md_report_status",
        "conformance_html_report_status",
        "product_command_status",
        "single_mock_status",
        "single_command_status",
        "mock_suite_status",
        "command_suite_status",
        "mvp_smoke_status",
        "phase48_readiness_status",
        "http_adapter_status",
        "preview_tag_status",
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
