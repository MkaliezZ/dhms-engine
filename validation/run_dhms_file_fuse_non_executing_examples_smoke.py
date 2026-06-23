#!/usr/bin/env python3
"""Smoke validation for DHMS File Fuse non-executing examples v0.8.3."""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any


ROOT = __file__.rsplit("/validation/", 1)[0]
EXAMPLES_DIR = f"{ROOT}/examples/dhms_agentfuse_file_v0"
TRACE_EXAMPLES_PATH = f"{EXAMPLES_DIR}/trace_examples.json"

EXAMPLES = [
    {
        "name": "file_read_allowlisted_readme_candidate",
        "path": f"{EXAMPLES_DIR}/file_read_allowlisted_readme_candidate_example.py",
        "case_id": "file_read_allowlisted_readme_candidate",
    },
    {
        "name": "file_read_env_blocked",
        "path": f"{EXAMPLES_DIR}/file_read_env_blocked_example.py",
        "case_id": "file_read_env_blocked",
    },
    {
        "name": "file_write_source_overwrite_held",
        "path": f"{EXAMPLES_DIR}/file_write_source_overwrite_held_example.py",
        "case_id": "file_write_source_overwrite_held",
    },
    {
        "name": "file_operation_unsupported_fail_closed",
        "path": f"{EXAMPLES_DIR}/file_operation_unsupported_fail_closed_example.py",
        "case_id": "file_operation_unsupported_fail_closed",
    },
]

FORBIDDEN_IMPORTS = [
    "pathlib",
    "os",
    "glob",
    "shutil",
    "subprocess",
    "sqlite3",
    "requests",
    "httpx",
    "urllib",
    "socket",
    "openai",
    "anthropic",
    "langchain",
    "autogen",
    "crewai",
    "llama_index",
    "mcp",
]

FORBIDDEN_CALL_MARKERS = [
    "open(",
    ".open(",
    ".resolve(",
    ".exists(",
    "listdir",
    "glob",
    "remove",
    "unlink",
    "rmdir",
    "mkdir",
    "write_text",
    "read_text",
]


def read_known_file(path: str) -> tuple[str, list[str]]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read(), []
    except FileNotFoundError:
        return "", [f"missing_file:{path}"]


def scan_example_source(example: dict[str, str]) -> list[str]:
    source, failed_checks = read_known_file(example["path"])
    if failed_checks:
        return failed_checks

    for module_name in FORBIDDEN_IMPORTS:
        if f"import {module_name}" in source or f"from {module_name}" in source:
            failed_checks.append(f"{example['name']}.forbidden_import:{module_name}")
    for marker in FORBIDDEN_CALL_MARKERS:
        if marker in source:
            failed_checks.append(f"{example['name']}.forbidden_call_marker:{marker}")
    return failed_checks


def run_example(example: dict[str, str]) -> dict[str, Any]:
    failed_checks = scan_example_source(example)
    completed = subprocess.run(
        [sys.executable, example["path"]],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        shell=False,
    )
    parsed: dict[str, Any] = {}
    if completed.returncode != 0:
        failed_checks.append(f"{example['name']}.exit_code_nonzero")
    try:
        parsed = json.loads(completed.stdout)
    except json.JSONDecodeError:
        failed_checks.append(f"{example['name']}.output_not_json")

    if parsed.get("case_id") != example["case_id"]:
        failed_checks.append(f"{example['name']}.case_id_mismatch")
    if parsed.get("final_verdict") != "DHMS_FILE_FUSE_EXAMPLE_PASS":
        failed_checks.append(f"{example['name']}.verdict_mismatch")
    if parsed.get("actual_executed") is not False:
        failed_checks.append(f"{example['name']}.actual_executed_not_false")
    if parsed.get("expected_executed") is not False:
        failed_checks.append(f"{example['name']}.expected_executed_not_false")
    if parsed.get("direct_execution_allowed") is not False:
        failed_checks.append(f"{example['name']}.direct_execution_allowed_not_false")
    if parsed.get("expected_direct_execution_allowed") is not False:
        failed_checks.append(f"{example['name']}.expected_direct_execution_allowed_not_false")
    if parsed.get("execution_result") is not None:
        failed_checks.append(f"{example['name']}.execution_result_not_null")
    if parsed.get("path_template_treated_as_inert") is not True:
        failed_checks.append(f"{example['name']}.path_template_not_inert")
    if parsed.get("path_template_opened") is not False:
        failed_checks.append(f"{example['name']}.path_template_opened_not_false")
    if parsed.get("path_template_resolved") is not False:
        failed_checks.append(f"{example['name']}.path_template_resolved_not_false")

    return {
        "example_name": example["name"],
        "case_id": parsed.get("case_id"),
        "exit_code": completed.returncode,
        "passed": not failed_checks,
        "actual_executed": bool(parsed.get("actual_executed", True)),
        "direct_execution_allowed": bool(parsed.get("direct_execution_allowed", True)),
        "path_template_opened": bool(parsed.get("path_template_opened", True)),
        "path_template_resolved": bool(parsed.get("path_template_resolved", True)),
        "final_verdict": parsed.get("final_verdict"),
        "failed_checks": failed_checks,
    }


def validate_trace_examples() -> dict[str, Any]:
    text, failed_checks = read_known_file(TRACE_EXAMPLES_PATH)
    if failed_checks:
        return {
            "trace_examples_total": 0,
            "trace_examples_passed": 0,
            "failed_checks": failed_checks,
        }

    try:
        trace_doc = json.loads(text)
    except json.JSONDecodeError:
        return {
            "trace_examples_total": 0,
            "trace_examples_passed": 0,
            "failed_checks": ["trace_examples_json_invalid"],
        }

    traces = trace_doc.get("traces", [])
    if len(traces) != 4:
        failed_checks.append("trace_examples_total_not_four")
    if trace_doc.get("implementation_status") != "static_trace_examples_only":
        failed_checks.append("trace_doc_implementation_status_mismatch")

    trace_passed = 0
    for trace in traces:
        trace_id = trace.get("trace_id", "unknown")
        before_count = len(failed_checks)
        if trace.get("actual_executed") is not False:
            failed_checks.append(f"{trace_id}.actual_executed_not_false")
        if trace.get("expected_executed") is not False:
            failed_checks.append(f"{trace_id}.expected_executed_not_false")
        if trace.get("direct_execution_allowed") is not False:
            failed_checks.append(f"{trace_id}.direct_execution_allowed_not_false")
        if trace.get("expected_direct_execution_allowed") is not False:
            failed_checks.append(f"{trace_id}.expected_direct_execution_allowed_not_false")
        if trace.get("execution_result") is not None:
            failed_checks.append(f"{trace_id}.execution_result_not_null")
        if trace.get("path_template_treated_as_inert") is not True:
            failed_checks.append(f"{trace_id}.path_template_not_inert")
        if trace.get("path_template_opened") is not False:
            failed_checks.append(f"{trace_id}.path_template_opened_not_false")
        if trace.get("path_template_resolved") is not False:
            failed_checks.append(f"{trace_id}.path_template_resolved_not_false")
        if trace.get("final_verdict") != "DHMS_FILE_FUSE_TRACE_EXAMPLE_PASS":
            failed_checks.append(f"{trace_id}.verdict_mismatch")
        if len(failed_checks) == before_count:
            trace_passed += 1

    return {
        "trace_examples_total": len(traces),
        "trace_examples_passed": trace_passed,
        "failed_checks": failed_checks,
    }


def run_smoke() -> dict[str, Any]:
    example_results = [run_example(example) for example in EXAMPLES]
    trace_result = validate_trace_examples()

    failed_checks = [
        check
        for result in example_results
        for check in result["failed_checks"]
    ]
    failed_checks.extend(trace_result["failed_checks"])

    examples_passed = sum(1 for result in example_results if result["passed"])
    actual_file_operations_executed_count = sum(1 for result in example_results if result["actual_executed"])
    direct_execution_allowed_count = sum(1 for result in example_results if result["direct_execution_allowed"])
    requested_path_templates_opened_count = sum(1 for result in example_results if result["path_template_opened"])
    requested_path_templates_resolved_count = sum(1 for result in example_results if result["path_template_resolved"])

    if actual_file_operations_executed_count != 0:
        failed_checks.append("actual_file_operations_executed_count_not_zero")
    if direct_execution_allowed_count != 0:
        failed_checks.append("direct_execution_allowed_count_not_zero")
    if requested_path_templates_opened_count != 0:
        failed_checks.append("requested_path_templates_opened_count_not_zero")
    if requested_path_templates_resolved_count != 0:
        failed_checks.append("requested_path_templates_resolved_count_not_zero")

    status = "PASS" if not failed_checks and examples_passed == 4 and trace_result["trace_examples_passed"] == 4 else "FAIL"
    return {
        "smoke_name": "DHMS File Fuse Non-Executing Examples Smoke",
        "version": "v0.8.3",
        "status": status,
        "examples_total": len(EXAMPLES),
        "examples_passed": examples_passed,
        "trace_examples_total": trace_result["trace_examples_total"],
        "trace_examples_passed": trace_result["trace_examples_passed"],
        "example_scripts_executed_count": len(EXAMPLES),
        "actual_file_operations_executed_count": actual_file_operations_executed_count,
        "direct_execution_allowed_count": direct_execution_allowed_count,
        "requested_path_templates_opened_count": requested_path_templates_opened_count,
        "requested_path_templates_resolved_count": requested_path_templates_resolved_count,
        "file_reads_performed_count": 0,
        "file_writes_performed_count": 0,
        "file_appends_performed_count": 0,
        "file_deletes_performed_count": 0,
        "file_lists_performed_count": 0,
        "file_adapter_added": False,
        "runtime_behavior_added": False,
        "example_results": example_results,
        "trace_validation": trace_result,
        "failed_checks": failed_checks,
        "final_verdict": "DHMS_FILE_FUSE_NON_EXECUTING_EXAMPLES_PASS"
        if status == "PASS"
        else "DHMS_FILE_FUSE_NON_EXECUTING_EXAMPLES_FAIL",
    }


def main() -> int:
    summary = run_smoke()
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(summary["final_verdict"])
    return 0 if summary["final_verdict"] == "DHMS_FILE_FUSE_NON_EXECUTING_EXAMPLES_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
