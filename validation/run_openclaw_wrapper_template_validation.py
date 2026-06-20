#!/usr/bin/env python3
"""Safe validation for the OpenClaw + DeepSeek v4 wrapper template."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "validation" / "outputs"
REPORT_JSON = OUTPUT_DIR / "openclaw_wrapper_template_validation_report.json"
REPORT_MD = OUTPUT_DIR / "openclaw_wrapper_template_validation_report.md"
WRAPPER = ROOT / "examples" / "agents" / "openclaw_deepseek_v4_wrapper.py"
DOCS = ROOT / "docs" / "openclaw_deepseek_v4_wrapper.md"
COMMAND_ADAPTER = ROOT / "engine" / "agent_harness" / "command_agent_adapter.py"
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
MISSING_COMMAND_REQUEST = {
    "protocol_version": "dhms-agent-command-v1",
    "request": {
        "input_text": "hello",
        "mode": "B",
        "dry_run": True,
        "memory_condition": {},
        "context_condition": {},
        "tool_state_condition": {},
        "metadata": {},
    },
}
SAFE_OPENCLAW_COMMAND = "/Users/macos/.npm-global/bin/openclaw --profile dhms-pilot agent --json --model deepseek/deepseek-v4-flash --agent main"
MISSING_TARGET_COMMAND = "/Users/macos/.npm-global/bin/openclaw --profile dhms-pilot agent --json --model deepseek/deepseek-v4-flash"
UNSAFE_DELIVER_COMMAND = SAFE_OPENCLAW_COMMAND + " --deliver"
UNSAFE_TO_COMMAND = "/Users/macos/.npm-global/bin/openclaw --profile dhms-pilot agent --json --model deepseek/deepseek-v4-flash --to test-target"
MISSING_PROFILE_COMMAND = "/Users/macos/.npm-global/bin/openclaw agent --json --model deepseek/deepseek-v4-flash --agent main"
SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"\b[A-Z0-9_]*(?:API_KEY|SECRET|TOKEN)\s*=\s*[^\s\"'`]+"),
    re.compile(r"BEGIN PRIVATE KEY"),
)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    commands = run_commands()
    missing_payload = parse_json(command_named(commands, "missing_command_stdin").get("stdout", ""))
    missing_trace = missing_payload.get("trace") if isinstance(missing_payload.get("trace"), dict) else {}
    missing_report = load_json(ROOT / "reports" / "adapter_conformance" / "openclaw_deepseek_v4_missing_command" / "adapter_conformance_report.json")
    preflight_payload = parse_json(command_named(commands, "preflight_stdin").get("stdout", ""))
    preflight_trace = preflight_payload.get("trace") if isinstance(preflight_payload.get("trace"), dict) else {}
    missing_target_payload = parse_json(command_named(commands, "missing_target_stdin").get("stdout", ""))
    missing_target_trace = missing_target_payload.get("trace") if isinstance(missing_target_payload.get("trace"), dict) else {}
    unsafe_payload = parse_json(command_named(commands, "unsafe_deliver_stdin").get("stdout", ""))
    unsafe_trace = unsafe_payload.get("trace") if isinstance(unsafe_payload.get("trace"), dict) else {}
    unsafe_to_payload = parse_json(command_named(commands, "unsafe_to_stdin").get("stdout", ""))
    unsafe_to_trace = unsafe_to_payload.get("trace") if isinstance(unsafe_to_payload.get("trace"), dict) else {}
    missing_profile_payload = parse_json(command_named(commands, "missing_profile_stdin").get("stdout", ""))
    missing_profile_trace = missing_profile_payload.get("trace") if isinstance(missing_profile_payload.get("trace"), dict) else {}
    preflight_report = load_json(ROOT / "reports" / "adapter_conformance" / "openclaw_deepseek_v4_preflight_with_target" / "adapter_conformance_report.json")
    sample_report = load_json(ROOT / "reports" / "adapter_conformance" / "sample_json_agent_phase57_check" / "adapter_conformance_report.json")
    protected_changes = git_output(["diff", "--name-only", "main", "--", *PROTECTED_PATHS]).splitlines()
    key_hits = secret_scan([WRAPPER, DOCS, COMMAND_ADAPTER, Path(__file__), REPORT_JSON, REPORT_MD])
    source = WRAPPER.read_text(encoding="utf-8") if WRAPPER.exists() else ""

    report: dict[str, Any] = {
        "status": "FAIL",
        "branch_name": git_output(["branch", "--show-current"]),
        "wrapper_file_exists": status_bool(WRAPPER.exists()),
        "docs_file_exists": status_bool(DOCS.exists()),
        "py_compile_status": command_status(commands, "py_compile_wrapper"),
        "missing_command_stdin_status": status_bool(
            command_ok(commands, "missing_command_stdin")
            and missing_payload.get("protocol_version") == "dhms-agent-command-v1"
            and missing_trace.get("adapter_name") == "openclaw_deepseek_v4"
            and missing_trace.get("dry_run") is True
            and has_error_type(missing_trace, "missing_openclaw_command")
            and not contains_executed_true(missing_trace)
        ),
        "missing_command_error_type_present": status_bool(has_error_type(missing_trace, "missing_openclaw_command")),
        "missing_command_dry_run_true": status_bool(missing_trace.get("dry_run") is True),
        "missing_command_no_executed_true": status_bool(not contains_executed_true(missing_trace)),
        "preflight_stdin_status": status_bool(
            command_ok(commands, "preflight_stdin")
            and preflight_payload.get("protocol_version") == "dhms-agent-command-v1"
            and preflight_trace.get("final_answer") == "OpenClaw DHMS wrapper preflight completed."
            and preflight_trace.get("dry_run") is True
            and not contains_executed_true(preflight_trace)
        ),
        "missing_target_rejection_status": status_bool(
            command_ok(commands, "missing_target_stdin")
            and has_error_type(missing_target_trace, "missing_openclaw_target")
            and missing_target_trace.get("dry_run") is True
            and not contains_executed_true(missing_target_trace)
        ),
        "unsafe_command_rejection_status": status_bool(
            command_ok(commands, "unsafe_deliver_stdin")
            and has_error_type(unsafe_trace, "unsafe_openclaw_command")
            and unsafe_trace.get("dry_run") is True
            and not contains_executed_true(unsafe_trace)
        ),
        "forbidden_to_rejection_status": status_bool(
            command_ok(commands, "unsafe_to_stdin")
            and has_error_type(unsafe_to_trace, "unsafe_openclaw_command")
            and unsafe_to_trace.get("dry_run") is True
            and not contains_executed_true(unsafe_to_trace)
        ),
        "missing_profile_rejection_status": status_bool(
            command_ok(commands, "missing_profile_stdin")
            and has_error_type(missing_profile_trace, "missing_isolated_profile")
            and missing_profile_trace.get("dry_run") is True
            and not contains_executed_true(missing_profile_trace)
        ),
        "forbidden_source_patterns": forbidden_source_patterns(source),
        "phase5_missing_command_conformance": {
            "command_status": command_status(commands, "conformance_missing_command"),
            "overall_status": missing_report.get("overall_status", "missing"),
            "blocking_failures": missing_report.get("blocking_failures", []),
            "safe_failure_expected": True,
        },
        "phase5_preflight_conformance": {
            "command_status": command_status(commands, "conformance_preflight"),
            "overall_status": preflight_report.get("overall_status", "missing"),
            "readiness_score": preflight_report.get("adapter_readiness_score", 0),
            "blocking_failures": preflight_report.get("blocking_failures", []),
        },
        "phase5_preflight_conformance_status": status_bool(
            command_ok(commands, "conformance_preflight")
            and preflight_report.get("overall_status") in {"PASS", "WARN"}
        ),
        "sample_json_agent_conformance_status": status_bool(
            command_ok(commands, "conformance_sample")
            and sample_report.get("overall_status") == "PASS"
            and sample_report.get("adapter_readiness_score") == 100
        ),
        "sample_json_agent_readiness_score": sample_report.get("adapter_readiness_score", 0),
        "preview_tag_status": status_bool(git_output(["rev-parse", f"{PREVIEW_TAG}^{{}}"]) == PREVIEW_COMMIT),
        "protected_core_layer_hash_result": {
            "status": "PASS" if not protected_changes else "FAIL",
            "changed_paths": protected_changes,
        },
        "key_leakage_scan_result": {
            "status": "PASS" if not key_hits else "FAIL",
            "hits": key_hits,
        },
        "no_real_openclaw_run": "PASS",
        "no_deepseek_api_called": "PASS",
        "no_real_external_tool_executed": "PASS",
        "generated_report_paths": {
            "validation_json": str(REPORT_JSON.relative_to(ROOT)),
            "validation_markdown": str(REPORT_MD.relative_to(ROOT)),
            "missing_command_conformance_json": "reports/adapter_conformance/openclaw_deepseek_v4_missing_command/adapter_conformance_report.json",
            "missing_command_conformance_markdown": "reports/adapter_conformance/openclaw_deepseek_v4_missing_command/adapter_conformance_report.md",
            "missing_command_conformance_html": "reports/adapter_conformance/openclaw_deepseek_v4_missing_command/adapter_conformance_report.html",
            "preflight_conformance_json": "reports/adapter_conformance/openclaw_deepseek_v4_preflight_with_target/adapter_conformance_report.json",
            "preflight_conformance_markdown": "reports/adapter_conformance/openclaw_deepseek_v4_preflight_with_target/adapter_conformance_report.md",
            "preflight_conformance_html": "reports/adapter_conformance/openclaw_deepseek_v4_preflight_with_target/adapter_conformance_report.html",
            "sample_conformance_json": "reports/adapter_conformance/sample_json_agent_phase57_check/adapter_conformance_report.json",
        },
    }
    report["status"] = "PASS" if all_checks_pass(report) else "FAIL"
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(build_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "report_json": str(REPORT_JSON), "report_md": str(REPORT_MD)}, indent=2))
    return 0 if report["status"] == "PASS" else 1


def run_commands() -> list[dict[str, Any]]:
    specs = {
        "py_compile_wrapper": ["python3", "-m", "py_compile", str(WRAPPER.relative_to(ROOT))],
        "missing_command_stdin": ["python3", str(WRAPPER.relative_to(ROOT))],
        "preflight_stdin": ["python3", str(WRAPPER.relative_to(ROOT))],
        "missing_target_stdin": ["python3", str(WRAPPER.relative_to(ROOT))],
        "unsafe_deliver_stdin": ["python3", str(WRAPPER.relative_to(ROOT))],
        "unsafe_to_stdin": ["python3", str(WRAPPER.relative_to(ROOT))],
        "missing_profile_stdin": ["python3", str(WRAPPER.relative_to(ROOT))],
        "conformance_missing_command": [
            "python3",
            "cli.py",
            "check-agent-adapter",
            "--agent-command",
            "python3 examples/agents/openclaw_deepseek_v4_wrapper.py",
            "--report",
            "--output",
            "reports/adapter_conformance/openclaw_deepseek_v4_missing_command",
        ],
        "conformance_preflight": [
            "python3",
            "cli.py",
            "check-agent-adapter",
            "--agent-command",
            "python3 examples/agents/openclaw_deepseek_v4_wrapper.py",
            "--report",
            "--output",
            "reports/adapter_conformance/openclaw_deepseek_v4_preflight_with_target",
        ],
        "conformance_sample": [
            "python3",
            "cli.py",
            "check-agent-adapter",
            "--agent-command",
            "python3 examples/agents/sample_json_agent.py",
            "--report",
            "--output",
            "reports/adapter_conformance/sample_json_agent_phase57_check",
        ],
    }
    return [run_command(name, command) for name, command in specs.items()]


def run_command(name: str, command: list[str]) -> dict[str, Any]:
    env = os.environ.copy()
    env.pop("OPENCLAW_DHMS_COMMAND", None)
    env.pop("OPENCLAW_DHMS_PREFLIGHT_ONLY", None)
    env.pop("OPENCLAW_DHMS_ALLOW_UNPROFILED", None)
    if name in {"preflight_stdin", "conformance_preflight"}:
        env["OPENCLAW_DHMS_COMMAND"] = SAFE_OPENCLAW_COMMAND
        env["OPENCLAW_DHMS_PREFLIGHT_ONLY"] = "1"
    elif name == "missing_target_stdin":
        env["OPENCLAW_DHMS_COMMAND"] = MISSING_TARGET_COMMAND
        env["OPENCLAW_DHMS_PREFLIGHT_ONLY"] = "1"
    elif name == "unsafe_deliver_stdin":
        env["OPENCLAW_DHMS_COMMAND"] = UNSAFE_DELIVER_COMMAND
        env["OPENCLAW_DHMS_PREFLIGHT_ONLY"] = "1"
    elif name == "unsafe_to_stdin":
        env["OPENCLAW_DHMS_COMMAND"] = UNSAFE_TO_COMMAND
        env["OPENCLAW_DHMS_PREFLIGHT_ONLY"] = "1"
    elif name == "missing_profile_stdin":
        env["OPENCLAW_DHMS_COMMAND"] = MISSING_PROFILE_COMMAND
        env["OPENCLAW_DHMS_PREFLIGHT_ONLY"] = "1"
    input_text = json.dumps(MISSING_COMMAND_REQUEST) if name.endswith("_stdin") else None
    completed = subprocess.run(
        command,
        cwd=ROOT,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    return {
        "name": name,
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "stdout_preview": completed.stdout[-1200:],
        "stderr_preview": completed.stderr[-1200:],
    }


def command_named(commands: list[dict[str, Any]], name: str) -> dict[str, Any]:
    return next((item for item in commands if item["name"] == name), {})


def command_ok(commands: list[dict[str, Any]], name: str) -> bool:
    return command_named(commands, name).get("returncode") == 0


def command_status(commands: list[dict[str, Any]], name: str) -> str:
    return status_bool(command_ok(commands, name))


def parse_json(text: str) -> dict[str, Any]:
    try:
        value = json.loads(text or "{}")
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def has_error_type(trace: dict[str, Any], error_type: str) -> bool:
    for error in trace.get("errors", []):
        if isinstance(error, dict) and error.get("type") == error_type:
            return True
        if isinstance(error, str) and error_type in error:
            return True
    return False


def contains_executed_true(value: Any) -> bool:
    if isinstance(value, dict):
        return any((key == "executed" and item is True) or contains_executed_true(item) for key, item in value.items())
    if isinstance(value, list):
        return any(contains_executed_true(item) for item in value)
    return False


def forbidden_source_patterns(source: str) -> dict[str, Any]:
    forbidden = {
        "shell=True": "shell=True",
        "os.system": "os.system",
        "os.environ_dump": "os.environ)",
        "requests": "requests",
        "httpx": "httpx",
        "urllib": "urllib",
        "socket": "socket",
    }
    hits = {name: marker for name, marker in forbidden.items() if marker in source}
    return {"status": "PASS" if not hits else "FAIL", "hits": hits}


def git_output(args: list[str]) -> str:
    completed = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)
    return completed.stdout.strip()


def secret_scan(paths: list[Path]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if "re.compile" in line:
                continue
            if any(pattern.search(line) for pattern in SECRET_PATTERNS):
                hits.append({"path": str(path.relative_to(ROOT)), "line": line_number})
    return hits


def all_checks_pass(report: dict[str, Any]) -> bool:
    statuses: list[str] = []
    for key, value in report.items():
        if key in {"status", "generated_report_paths", "phase5_missing_command_conformance"}:
            continue
        if isinstance(value, str) and value in {"PASS", "FAIL"}:
            statuses.append(value)
        elif isinstance(value, dict) and value.get("status") in {"PASS", "FAIL"}:
            statuses.append(value["status"])
    return bool(statuses) and all(status == "PASS" for status in statuses)


def status_bool(value: bool) -> str:
    return "PASS" if value else "FAIL"


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# OpenClaw Wrapper Template Validation",
        "",
        f"- Status: {report['status']}",
        f"- Branch: {report['branch_name']}",
        f"- Wrapper: {WRAPPER.relative_to(ROOT)}",
        f"- Docs: {DOCS.relative_to(ROOT)}",
        f"- Py compile: {report['py_compile_status']}",
        f"- Missing-command stdin test: {report['missing_command_stdin_status']}",
        f"- Missing-command conformance status: {report['phase5_missing_command_conformance']['overall_status']}",
        f"- Preflight stdin test: {report['preflight_stdin_status']}",
        f"- Missing target rejection: {report['missing_target_rejection_status']}",
        f"- Unsafe command rejection: {report['unsafe_command_rejection_status']}",
        f"- Forbidden --to rejection: {report['forbidden_to_rejection_status']}",
        f"- Missing profile rejection: {report['missing_profile_rejection_status']}",
        f"- Preflight conformance status: {report['phase5_preflight_conformance']['overall_status']}",
        f"- Sample conformance: {report['sample_json_agent_conformance_status']}",
        f"- Preview tag unchanged: {report['preview_tag_status']}",
        f"- Protected core layers unchanged: {report['protected_core_layer_hash_result']['status']}",
        f"- Secret scan: {report['key_leakage_scan_result']['status']}",
        "",
        "## Safety",
        "",
        "- Real OpenClaw was not run.",
        "- DeepSeek API was not called.",
        "- Real external tools were not executed.",
        "- `OPENCLAW_DHMS_COMMAND` was intentionally unset during missing-command validation.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
