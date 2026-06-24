#!/usr/bin/env python3
"""CLI for DHMS."""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, List, Optional

ROOT_DIR = Path(__file__).resolve().parent
ENGINE_DIR = ROOT_DIR / "engine"
PRODUCT_DIR = ROOT_DIR / "product"
VALIDATION_DIR = ROOT_DIR / "validation"
PATHS = (
    PRODUCT_DIR,
    ENGINE_DIR,
    ENGINE_DIR / "v0",
    ENGINE_DIR / "v1",
    ENGINE_DIR / "cross_model",
    ENGINE_DIR / "statistics",
    ENGINE_DIR / "v2_cross_model",
    ENGINE_DIR / "v2_5_bridge",
    ROOT_DIR / "binding",
    VALIDATION_DIR,
)
for path in PATHS:
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)

from engine_runner import run  # noqa: E402
from output_formatter import format_output  # noqa: E402
from agent_harness.harness_runner import run_agent_harness  # noqa: E402
from agent_harness.agent_suite_runner import run_agent_suite  # noqa: E402
from agent_harness.adapter_conformance_runner import run_adapter_conformance  # noqa: E402
from product_runner import run_product_test  # noqa: E402
from suite_runner import run_suite  # noqa: E402
from provider_status import format_status_table, models_for, provider_statuses  # noqa: E402
from dhms_agentfuse_bench_sql_v0 import run_dhms_agentfuse_bench_sql_v0  # noqa: E402


FILE_FUSE_DEMO_CHECKS = (
    {
        "name": "static_manifest_smoke",
        "script": "validation/run_dhms_file_fuse_static_case_manifest_smoke.py",
        "expected_verdict": "DHMS_FILE_FUSE_STATIC_CASE_MANIFEST_PASS",
    },
    {
        "name": "file_benchmark",
        "script": "validation/run_dhms_agentfuse_bench_file_v0.py",
        "expected_verdict": "DHMS_AGENTFUSE_BENCH_FILE_V0_PASS",
    },
    {
        "name": "non_executing_examples",
        "script": "validation/run_dhms_file_fuse_non_executing_examples_smoke.py",
        "expected_verdict": "DHMS_FILE_FUSE_NON_EXECUTING_EXAMPLES_PASS",
    },
    {
        "name": "constrained_temp_directory_proof",
        "script": "validation/run_dhms_file_fuse_constrained_temp_directory_proof.py",
        "expected_verdict": "DHMS_FILE_FUSE_CONSTRAINED_TEMP_DIRECTORY_PROOF_PASS",
    },
)

HTTP_FUSE_DEMO_CHECKS = (
    {
        "name": "non_executing_http_benchmark",
        "script": "validation/run_dhms_agentfuse_bench_http_v0.py",
        "expected_verdict": "DHMS_AGENTFUSE_BENCH_HTTP_V0_PASS",
    },
    {
        "name": "constrained_local_mock_http_proof",
        "script": "validation/run_dhms_constrained_local_mock_http_proof.py",
        "expected_verdict": "DHMS_CONSTRAINED_LOCAL_MOCK_HTTP_PROOF_PASS",
    },
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dhms")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--mode", required=True, choices=["A", "B", "C"])
    run_parser.add_argument("--input", required=True, dest="input_text")
    run_parser.add_argument("--n", type=int, default=1, help="number of repeated DHMS trials")
    run_parser.add_argument("--models", default="mock", help="comma-separated models, e.g. mock,external")

    test_parser = subparsers.add_parser("test")
    test_parser.add_argument("--input", dest="input_text")
    test_parser.add_argument("--input-file")
    test_parser.add_argument("--models", default="mock")
    test_parser.add_argument("--n", type=int, default=5)
    test_parser.add_argument("--mode", default="B", choices=["A", "B", "C"])
    test_parser.add_argument("--report", action="store_true")
    test_parser.add_argument("--output", default="reports/latest")
    test_parser.add_argument("--diagnose", action="store_true", help="explicitly include diagnosis fields in product reports")

    suite_parser = subparsers.add_parser("test-suite")
    suite_parser.add_argument("--suite", required=True)
    suite_parser.add_argument("--models", default="mock")
    suite_parser.add_argument("--n", type=int, default=1)
    suite_parser.add_argument("--mode", default="B", choices=["A", "B", "C"])
    suite_parser.add_argument("--report", action="store_true")
    suite_parser.add_argument("--output", default="reports/latest_suite")
    suite_parser.add_argument("--diagnose", action="store_true", help="explicitly include diagnosis fields in suite reports")

    agent_parser = subparsers.add_parser("test-agent")
    agent_adapter_group = agent_parser.add_mutually_exclusive_group()
    agent_adapter_group.add_argument("--mock-agent", action="store_true")
    agent_adapter_group.add_argument("--agent-command")
    agent_parser.add_argument("--input", dest="input_text")
    agent_parser.add_argument("--input-file")
    agent_parser.add_argument("--n", type=int, default=1)
    agent_parser.add_argument("--mode", default="B", choices=["A", "B", "C"])
    agent_parser.add_argument("--report", action="store_true")
    agent_parser.add_argument("--output", default="reports/agent_harness/latest")
    agent_parser.add_argument("--timeout-seconds", type=int, default=10)
    agent_parser.add_argument("--judge-mode", choices=["deterministic", "mock", "none"], default="deterministic")

    agent_suite_parser = subparsers.add_parser("test-agent-suite")
    agent_suite_parser.add_argument("--suite", required=True)
    agent_suite_adapter_group = agent_suite_parser.add_mutually_exclusive_group()
    agent_suite_adapter_group.add_argument("--mock-agent", action="store_true")
    agent_suite_adapter_group.add_argument("--agent-command")
    agent_suite_parser.add_argument("--n", type=int, default=1)
    agent_suite_parser.add_argument("--mode", default="B", choices=["A", "B", "C"])
    agent_suite_parser.add_argument("--report", action="store_true")
    agent_suite_parser.add_argument("--output", default="reports/agent_harness_suite/latest")
    agent_suite_parser.add_argument("--timeout-seconds", "--case-timeout-seconds", dest="timeout_seconds", type=int, default=10)
    agent_suite_parser.add_argument("--max-cases", "--limit-cases", dest="max_cases", type=int)
    agent_suite_parser.add_argument("--case", "--case-id", dest="case_id", help="run exactly one suite case by case id or file stem")
    agent_suite_parser.add_argument("--run-all-cases", action="store_true", help="run every case in deterministic suite order")
    agent_suite_parser.add_argument("--judge-mode", choices=["deterministic", "mock", "none"], default="deterministic")

    conformance_parser = subparsers.add_parser("check-agent-adapter")
    conformance_parser.add_argument("--agent-command", required=True)
    conformance_parser.add_argument("--timeout-seconds", "--case-timeout-seconds", dest="timeout_seconds", type=int, default=10)
    conformance_parser.add_argument("--report", action="store_true")
    conformance_parser.add_argument("--output", default="reports/adapter_conformance/latest")

    subparsers.add_parser("doctor")
    subparsers.add_parser("demo-sql-fuse")
    subparsers.add_parser("demo-file-fuse")
    subparsers.add_parser("demo-http-fuse")
    subparsers.add_parser("bench-mock-agent-interception")

    providers_parser = subparsers.add_parser("providers")
    providers_parser.add_argument("subcommand", nargs="?", choices=["models"])
    providers_parser.add_argument("provider", nargs="?")
    return parser


def normalize_argv(argv: List[str]) -> List[str]:
    if argv and argv[0] == "dhms":
        return argv[1:]
    return argv


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(normalize_argv(list(sys.argv[1:] if argv is None else argv)))
    if args.command == "run":
        result = run(args.mode, args.input_text, n=args.n, models=args.models)
        print(format_output(result))
        return 0
    if args.command == "doctor":
        print(format_status_table(provider_statuses()))
        return 0
    if args.command == "demo-sql-fuse":
        result = run_dhms_agentfuse_bench_sql_v0()
        print(sql_fuse_demo_console_summary(result))
        return 0 if result.get("status") == "PASS" else 1
    if args.command == "demo-file-fuse":
        result = run_file_fuse_demo()
        print(file_fuse_demo_console_summary(result))
        return 0 if result["final_verdict"] == "DHMS_FILE_FUSE_DEMO_PASS" else 1
    if args.command == "demo-http-fuse":
        result = run_http_fuse_demo()
        print(http_fuse_demo_console_summary(result))
        return 0 if result["final_verdict"] == "DHMS_HTTP_FUSE_DEMO_PASS" else 1
    if args.command == "bench-mock-agent-interception":
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT_DIR / "validation/run_dhms_mock_agent_interception_benchmark_v0.py"),
            ],
            cwd=ROOT_DIR,
            check=False,
            shell=False,
        )
        return completed.returncode
    if args.command == "providers":
        if args.subcommand == "models":
            print(json.dumps(models_for(args.provider), indent=2, sort_keys=True))
        else:
            print(format_status_table(provider_statuses()))
        return 0
    if args.command == "test-suite":
        if args.n < 1:
            parser.error("--n must be >= 1")
        result = run_suite(suite=args.suite, models=args.models, n=args.n, mode=args.mode, report=args.report, output=args.output)
        if args.report:
            print(suite_console_summary(result))
        else:
            print(json.dumps(result["summary"], indent=2, sort_keys=True))
        return 0
    if args.command == "test-agent":
        if not args.mock_agent and not args.agent_command:
            print("Agent Harness requires --mock-agent or --agent-command. HTTP adapters will be added later.")
            return 1
        if not args.input_text and not args.input_file:
            parser.error("test-agent requires either --input or --input-file")
        if args.n < 1:
            parser.error("--n must be >= 1")
        if args.timeout_seconds < 1:
            parser.error("--timeout-seconds must be >= 1")
        input_text = args.input_text
        if args.input_file:
            input_text = Path(args.input_file).read_text(encoding="utf-8")
        adapter = "command" if args.agent_command else "mock"
        result = run_agent_harness(
            input_text=input_text or "",
            adapter=adapter,
            n=args.n,
            mode=args.mode,
            report=args.report,
            output=args.output,
            agent_command=args.agent_command,
            timeout_seconds=args.timeout_seconds,
            judge_mode=args.judge_mode,
        )
        if args.report:
            print(agent_console_summary(result))
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if args.command == "test-agent-suite":
        if not args.mock_agent and not args.agent_command:
            print("Agent Harness suite requires --mock-agent or --agent-command. HTTP adapters will be added later.")
            return 1
        if args.n < 1:
            parser.error("--n must be >= 1")
        if args.timeout_seconds < 1:
            parser.error("--timeout-seconds must be >= 1")
        if args.max_cases is not None and args.max_cases < 1:
            parser.error("--max-cases/--limit-cases must be >= 1")
        if args.case_id and args.max_cases is not None:
            parser.error("--case/--case-id cannot be combined with --max-cases/--limit-cases")
        if args.run_all_cases and args.max_cases is not None:
            parser.error("--run-all-cases cannot be combined with --max-cases/--limit-cases")
        adapter = "command" if args.agent_command else "mock"
        try:
            result = run_agent_suite(
                suite=args.suite,
                adapter=adapter,
                agent_command=args.agent_command,
                n=args.n,
                mode=args.mode,
                report=args.report,
                output=args.output,
                timeout_seconds=args.timeout_seconds,
                max_cases=args.max_cases,
                case_id=args.case_id,
                run_all_cases=args.run_all_cases,
                judge_mode=args.judge_mode,
            )
        except ValueError as exc:
            parser.error(str(exc))
        if args.report:
            print(agent_suite_console_summary(result))
        else:
            print(json.dumps(result["summary"], indent=2, sort_keys=True))
        return 0
    if args.command == "check-agent-adapter":
        if args.timeout_seconds < 1:
            parser.error("--timeout-seconds must be >= 1")
        result = run_adapter_conformance(
            agent_command=args.agent_command,
            timeout_seconds=args.timeout_seconds,
            report=args.report,
            output=args.output,
        )
        if args.report:
            print(adapter_conformance_console_summary(result))
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if not args.input_text and not args.input_file:
        parser.error("test requires either --input or --input-file")
    if args.n < 1:
        parser.error("--n must be >= 1")
    result = run_product_test(
        input_text=args.input_text,
        input_file=args.input_file,
        models=args.models,
        n=args.n,
        mode=args.mode,
        report=args.report,
        output=args.output,
    )
    if args.report:
        print(product_console_summary(result))
    else:
        print(json.dumps(compact_product_summary(result), indent=2, sort_keys=True))
    return 0


def compact_product_summary(result):
    return {
        "product_name": result["product_name"],
        "product_version": result["product_version"],
        "risk_label": result["risk_label"],
        "stability_score": result["stability_score"],
        "sensitivity_score": result["sensitivity_score"],
        "isolation_strength_score": result["isolation_strength_score"],
        "drift_risk": result["drift_risk"],
        "recommendation": result["recommendation"],
        "report_paths": result.get("report_paths", {}),
    }


def product_console_summary(result) -> str:
    lines = [
        "DHMS Product Report",
        f"Product: {result['product_name']}",
        f"Risk: {result['risk_label']}",
        f"Stability Score: {result['stability_score']}",
        f"Sensitivity Score: {result['sensitivity_score']}",
        f"Isolation Strength: {result['isolation_strength_score']}",
        f"Recommendation: {result['recommendation']}",
        "",
        "Reports:",
    ]
    for path in result.get("report_paths", {}).values():
        lines.append(f"* {path}")
    return "\n".join(lines)


def suite_console_summary(result) -> str:
    summary = result["summary"]
    lines = [
        "DHMS Suite Report",
        f"Suite: {summary['suite_name']}",
        f"Total cases: {summary['total_cases']}",
        f"Models: {', '.join(summary['models_tested'])}",
        f"Average Stability: {summary['average_scores']['stability_score']}",
        f"Average Drift Risk: {summary['average_scores']['drift_risk']}",
        f"Recommendation: {summary['recommendation']}",
        "",
        "Reports:",
    ]
    for path in result.get("report_paths", {}).values():
        lines.append(f"* {path}")
    return "\n".join(lines)


def agent_console_summary(result) -> str:
    lines = [
        "DHMS Agent Harness Report",
        f"Adapter: {result['adapter']}",
        f"Command: {result.get('agent_command', 'not_applicable')}",
        f"Mode: {result['mode']}",
        f"Trials: {result['trial_count']}",
        f"Dry run: {str(result['dry_run']).lower()}",
        f"Primary diagnosis: {result.get('diagnosis_summary', {}).get('primary_issue', 'not_available')}",
        f"Tool calls: {result['tool_call_count']}",
        f"Memory reads: {result['memory_read_count']}",
        f"Side effects blocked: {result['side_effects_blocked_count']}",
        "",
        "Reports:",
    ]
    for path in result.get("report_paths", {}).values():
        lines.append(f"* {path}")
    return "\n".join(lines)


def agent_suite_console_summary(result) -> str:
    summary = result["summary"]
    lines = [
        "DHMS Agent Harness Suite Report",
        f"Suite: {result['suite_name']}",
        f"Run: {result['suite_run_id']}",
        f"Adapter: {result['adapter']}",
        f"Cases: {summary['total_cases']}",
        f"Trials: {result['trial_count']}",
        f"Dry run all cases: {str(summary['dry_run_all_cases']).lower()}",
        f"Side effects blocked: {summary['total_side_effects_blocked']}",
        f"Side effects executed: {summary['total_side_effects_executed']}",
        f"Suite severity: {summary['suite_severity']}",
        f"Recommendation: {summary['suite_recommendation']}",
        "",
        "Reports:",
    ]
    for path in result.get("report_paths", {}).values():
        lines.append(f"* {path}")
    return "\n".join(lines)


def adapter_conformance_console_summary(result) -> str:
    lines = [
        "DHMS Adapter Conformance Report",
        f"Adapter command: {result['adapter_command']}",
        f"Overall status: {result['overall_status']}",
        f"Readiness score: {result['adapter_readiness_score']}",
        f"Blocking failures: {len(result.get('blocking_failures', []))}",
        "",
        "Reports:",
    ]
    for path in result.get("report_paths", {}).values():
        lines.append(f"* {path}")
    return "\n".join(lines)


def sql_fuse_demo_console_summary(result) -> str:
    failed_checks = json.dumps(result.get("failed_checks", []), separators=(",", ":"))
    lines = [
        "DHMS SQL Fuse Demo",
        "mode=non-executing benchmark wrapper",
        f"benchmark_name={result['benchmark_name']}",
        f"benchmark_version={result['benchmark_version']}",
        f"protocol_version={result['protocol_version']}",
        f"proven_line={result['proven_line']}",
        f"cases_total={result['cases_total']}",
        f"cases_passed={result['cases_passed']}",
        f"release_eligible_count={result['release_eligible_count']}",
        f"blocked_or_fail_closed_count={result['blocked_or_fail_closed_count']}",
        f"direct_execution_allowed_count={result['direct_execution_allowed_count']}",
        f"sql_executed_by_benchmark_count={result['sql_executed_by_benchmark_count']}",
        f"sqlite_database_created_by_benchmark_count={result['sqlite_database_created_by_benchmark_count']}",
        f"sandbox_executed_by_benchmark_count={result['sandbox_executed_by_benchmark_count']}",
        f"mutation_sql_executed_count={result['mutation_sql_executed_count']}",
        f"rejected_input_executed_count={result['rejected_input_executed_count']}",
        f"failed_checks={failed_checks}",
        f"linked_actual_release_proof={result['linked_actual_release_proof']}",
        "demo_executed_sql=false",
        "demo_created_sqlite_database=false",
        "demo_created_sandbox=false",
        "actual_controlled_release_proof_linked_not_reimplemented=true",
        f"summary_json={result['reports']['summary_json']}",
        f"summary_md={result['reports']['summary_md']}",
        "final_verdict=SQL_FUSE_DEMO_PASS"
        if result.get("status") == "PASS"
        else "final_verdict=SQL_FUSE_DEMO_FAIL",
    ]
    return "\n".join(lines)


def parse_first_json_object(stdout: str) -> dict[str, Any]:
    text = stdout.lstrip()
    if not text:
        raise ValueError("empty_stdout")
    parsed, _ = json.JSONDecoder().raw_decode(text)
    if not isinstance(parsed, dict):
        raise ValueError("stdout_json_not_object")
    return parsed


def parse_key_value_summary(stdout: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in stdout.splitlines():
        if not line or line.startswith("{"):
            break
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values


def run_fixed_file_fuse_check(check: dict[str, str]) -> dict[str, Any]:
    script = ROOT_DIR / check["script"]
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT_DIR,
        text=True,
        capture_output=True,
        check=False,
        shell=False,
    )

    failed_checks: list[str] = []
    summary: dict[str, Any] = {}
    if completed.returncode != 0:
        failed_checks.append(f"{check['name']}.exit_code_nonzero")
    try:
        summary = parse_first_json_object(completed.stdout)
    except (json.JSONDecodeError, ValueError) as exc:
        failed_checks.append(f"{check['name']}.stdout_json_parse_failed:{type(exc).__name__}")

    observed_verdict = summary.get("final_verdict")
    if observed_verdict != check["expected_verdict"]:
        failed_checks.append(
            f"{check['name']}.verdict_expected_{check['expected_verdict']}_got_{observed_verdict}"
        )

    nested_failed_checks = summary.get("failed_checks", [])
    if nested_failed_checks:
        failed_checks.append(f"{check['name']}.nested_failed_checks_present")

    return {
        "name": check["name"],
        "script": check["script"],
        "expected_verdict": check["expected_verdict"],
        "observed_verdict": observed_verdict,
        "exit_code": completed.returncode,
        "passed": not failed_checks,
        "summary": summary,
        "failed_checks": failed_checks,
        "stderr": completed.stderr.strip(),
    }


def run_file_fuse_demo() -> dict[str, Any]:
    check_results = [run_fixed_file_fuse_check(check) for check in FILE_FUSE_DEMO_CHECKS]
    failed_checks = [
        failed_check
        for result in check_results
        for failed_check in result["failed_checks"]
    ]

    by_name = {result["name"]: result for result in check_results}
    static_summary = by_name["static_manifest_smoke"]["summary"]
    benchmark_summary = by_name["file_benchmark"]["summary"]
    examples_summary = by_name["non_executing_examples"]["summary"]
    proof_summary = by_name["constrained_temp_directory_proof"]["summary"]

    checks_passed = sum(1 for result in check_results if result["passed"])
    actual_file_operations_executed_count = int(
        proof_summary.get("actual_file_operations_executed_count", 0)
    )
    approved_constrained_release_cases = int(
        proof_summary.get("approved_constrained_release_cases", 0)
    )
    blocked_or_fail_closed_cases = int(
        proof_summary.get("blocked_or_fail_closed_cases", 0)
    )
    rejected_path_opened_count = int(proof_summary.get("rejected_path_opened_count", 0))
    rejected_path_resolved_count = int(proof_summary.get("rejected_path_resolved_count", 0))

    if static_summary.get("file_paths_opened_count") != 0:
        failed_checks.append("static_manifest_smoke.file_paths_opened_count_not_zero")
    if static_summary.get("file_paths_resolved_count") != 0:
        failed_checks.append("static_manifest_smoke.file_paths_resolved_count_not_zero")
    if benchmark_summary.get("actual_file_operations_executed_count") != 0:
        failed_checks.append("file_benchmark.actual_file_operations_executed_count_not_zero")
    if benchmark_summary.get("requested_path_templates_opened_count") != 0:
        failed_checks.append("file_benchmark.requested_path_templates_opened_count_not_zero")
    if benchmark_summary.get("requested_path_templates_resolved_count") != 0:
        failed_checks.append("file_benchmark.requested_path_templates_resolved_count_not_zero")
    if examples_summary.get("actual_file_operations_executed_count") != 0:
        failed_checks.append("non_executing_examples.actual_file_operations_executed_count_not_zero")
    if examples_summary.get("requested_path_templates_opened_count") != 0:
        failed_checks.append("non_executing_examples.requested_path_templates_opened_count_not_zero")
    if examples_summary.get("requested_path_templates_resolved_count") != 0:
        failed_checks.append("non_executing_examples.requested_path_templates_resolved_count_not_zero")
    if actual_file_operations_executed_count != 2:
        failed_checks.append("constrained_temp_directory_proof.actual_file_operations_executed_count_not_two")
    if approved_constrained_release_cases != 2:
        failed_checks.append("constrained_temp_directory_proof.approved_constrained_release_cases_not_two")
    if blocked_or_fail_closed_cases != 8:
        failed_checks.append("constrained_temp_directory_proof.blocked_or_fail_closed_cases_not_eight")
    if rejected_path_opened_count != 0:
        failed_checks.append("constrained_temp_directory_proof.rejected_path_opened_count_not_zero")
    if rejected_path_resolved_count != 0:
        failed_checks.append("constrained_temp_directory_proof.rejected_path_resolved_count_not_zero")

    return {
        "demo_name": "DHMS File Fuse Demo",
        "mode": "fixed deterministic File Fuse validation wrapper",
        "checks_total": len(FILE_FUSE_DEMO_CHECKS),
        "checks_passed": checks_passed,
        "static_manifest_smoke_passed": by_name["static_manifest_smoke"]["passed"],
        "file_benchmark_passed": by_name["file_benchmark"]["passed"],
        "non_executing_examples_passed": by_name["non_executing_examples"]["passed"],
        "constrained_temp_directory_proof_passed": by_name["constrained_temp_directory_proof"]["passed"],
        "actual_file_operations_executed_count": actual_file_operations_executed_count,
        "approved_constrained_release_cases": approved_constrained_release_cases,
        "blocked_or_fail_closed_cases": blocked_or_fail_closed_cases,
        "rejected_path_opened_count": rejected_path_opened_count,
        "rejected_path_resolved_count": rejected_path_resolved_count,
        "file_adapter_added": False,
        "arbitrary_file_operation_support_added": False,
        "check_results": check_results,
        "failed_checks": failed_checks,
        "final_verdict": "DHMS_FILE_FUSE_DEMO_PASS"
        if not failed_checks and checks_passed == len(FILE_FUSE_DEMO_CHECKS)
        else "DHMS_FILE_FUSE_DEMO_FAIL",
    }


def file_fuse_demo_console_summary(result: dict[str, Any]) -> str:
    failed_checks = json.dumps(result.get("failed_checks", []), separators=(",", ":"))
    lines = [
        "DHMS File Fuse Demo",
        f"mode={result['mode']}",
        f"checks_total={result['checks_total']}",
        f"checks_passed={result['checks_passed']}",
        f"static_manifest_smoke_passed={str(result['static_manifest_smoke_passed']).lower()}",
        f"file_benchmark_passed={str(result['file_benchmark_passed']).lower()}",
        f"non_executing_examples_passed={str(result['non_executing_examples_passed']).lower()}",
        f"constrained_temp_directory_proof_passed={str(result['constrained_temp_directory_proof_passed']).lower()}",
        f"actual_file_operations_executed_count={result['actual_file_operations_executed_count']}",
        f"approved_constrained_release_cases={result['approved_constrained_release_cases']}",
        f"blocked_or_fail_closed_cases={result['blocked_or_fail_closed_cases']}",
        f"rejected_path_opened_count={result['rejected_path_opened_count']}",
        f"rejected_path_resolved_count={result['rejected_path_resolved_count']}",
        f"file_adapter_added={str(result['file_adapter_added']).lower()}",
        f"arbitrary_file_operation_support_added={str(result['arbitrary_file_operation_support_added']).lower()}",
        f"failed_checks={failed_checks}",
        f"final_verdict={result['final_verdict']}",
    ]
    if result["final_verdict"] != "DHMS_FILE_FUSE_DEMO_PASS":
        failed_detail = [
            {
                "name": check_result["name"],
                "script": check_result["script"],
                "exit_code": check_result["exit_code"],
                "observed_verdict": check_result["observed_verdict"],
                "failed_checks": check_result["failed_checks"],
                "stderr": check_result["stderr"],
            }
            for check_result in result["check_results"]
            if not check_result["passed"]
        ]
        lines.append(
            "failed_check_details="
            + json.dumps(failed_detail, separators=(",", ":"), sort_keys=True)
        )
    return "\n".join(lines)


def run_fixed_http_fuse_check(check: dict[str, str]) -> dict[str, Any]:
    script = ROOT_DIR / check["script"]
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT_DIR,
        text=True,
        capture_output=True,
        check=False,
        shell=False,
    )

    failed_checks: list[str] = []
    summary = parse_key_value_summary(completed.stdout)
    output_lines = completed.stdout.splitlines()
    observed_verdict = output_lines[0].strip() if output_lines else None

    if completed.returncode != 0:
        failed_checks.append(f"{check['name']}.exit_code_nonzero")
    if observed_verdict != check["expected_verdict"]:
        failed_checks.append(
            f"{check['name']}.verdict_expected_{check['expected_verdict']}_got_{observed_verdict}"
        )
    if summary.get("failed_checks") not in {"[]", None}:
        failed_checks.append(f"{check['name']}.nested_failed_checks_present")

    return {
        "name": check["name"],
        "script": check["script"],
        "expected_verdict": check["expected_verdict"],
        "observed_verdict": observed_verdict,
        "exit_code": completed.returncode,
        "passed": not failed_checks,
        "summary": summary,
        "failed_checks": failed_checks,
        "stderr": completed.stderr.strip(),
    }


def run_http_fuse_demo() -> dict[str, Any]:
    check_results = [run_fixed_http_fuse_check(check) for check in HTTP_FUSE_DEMO_CHECKS]
    failed_checks = [
        failed_check
        for result in check_results
        for failed_check in result["failed_checks"]
    ]

    by_name = {result["name"]: result for result in check_results}
    proof_summary = by_name["constrained_local_mock_http_proof"]["summary"]

    checks_passed = sum(1 for result in check_results if result["passed"])
    actual_http_requests_executed_count = int(
        proof_summary.get("actual_http_requests_executed_count", 0)
    )
    approved_mock_get_request_count = int(
        proof_summary.get("approved_mock_get_request_count", 0)
    )
    rejected_http_requests_executed_count = int(
        proof_summary.get("rejected_http_requests_executed_count", 0)
    )
    external_network_requests_attempted_count = int(
        proof_summary.get("external_network_requests_attempted_count", 0)
    )
    dns_resolution_attempted_count = int(
        proof_summary.get("dns_resolution_attempted_count", 0)
    )
    credentials_used_count = int(proof_summary.get("credentials_used_count", 0))

    if actual_http_requests_executed_count != 1:
        failed_checks.append("constrained_local_mock_http_proof.actual_http_requests_executed_count_not_one")
    if approved_mock_get_request_count != 1:
        failed_checks.append("constrained_local_mock_http_proof.approved_mock_get_request_count_not_one")
    if rejected_http_requests_executed_count != 0:
        failed_checks.append("constrained_local_mock_http_proof.rejected_http_requests_executed_count_not_zero")
    if external_network_requests_attempted_count != 0:
        failed_checks.append("constrained_local_mock_http_proof.external_network_requests_attempted_count_not_zero")
    if dns_resolution_attempted_count != 0:
        failed_checks.append("constrained_local_mock_http_proof.dns_resolution_attempted_count_not_zero")
    if credentials_used_count != 0:
        failed_checks.append("constrained_local_mock_http_proof.credentials_used_count_not_zero")

    return {
        "demo_name": "DHMS HTTP Fuse Demo",
        "mode": "fixed deterministic HTTP Fuse validation wrapper",
        "checks_total": len(HTTP_FUSE_DEMO_CHECKS),
        "checks_passed": checks_passed,
        "non_executing_http_benchmark_passed": by_name["non_executing_http_benchmark"]["passed"],
        "constrained_local_mock_http_proof_passed": by_name["constrained_local_mock_http_proof"]["passed"],
        "actual_http_requests_executed_count": actual_http_requests_executed_count,
        "approved_mock_get_request_count": approved_mock_get_request_count,
        "rejected_http_requests_executed_count": rejected_http_requests_executed_count,
        "external_network_requests_attempted_count": external_network_requests_attempted_count,
        "dns_resolution_attempted_count": dns_resolution_attempted_count,
        "credentials_used_count": credentials_used_count,
        "http_adapter_added": False,
        "api_client_added": False,
        "credential_handling_added": False,
        "check_results": check_results,
        "failed_checks": failed_checks,
        "final_verdict": "DHMS_HTTP_FUSE_DEMO_PASS"
        if not failed_checks and checks_passed == len(HTTP_FUSE_DEMO_CHECKS)
        else "DHMS_HTTP_FUSE_DEMO_FAIL",
    }


def http_fuse_demo_console_summary(result: dict[str, Any]) -> str:
    failed_checks = json.dumps(result.get("failed_checks", []), separators=(",", ":"))
    lines = [
        "DHMS HTTP Fuse Demo",
        f"mode={result['mode']}",
        f"checks_total={result['checks_total']}",
        f"checks_passed={result['checks_passed']}",
        f"non_executing_http_benchmark_passed={str(result['non_executing_http_benchmark_passed']).lower()}",
        f"constrained_local_mock_http_proof_passed={str(result['constrained_local_mock_http_proof_passed']).lower()}",
        f"actual_http_requests_executed_count={result['actual_http_requests_executed_count']}",
        f"approved_mock_get_request_count={result['approved_mock_get_request_count']}",
        f"rejected_http_requests_executed_count={result['rejected_http_requests_executed_count']}",
        f"external_network_requests_attempted_count={result['external_network_requests_attempted_count']}",
        f"dns_resolution_attempted_count={result['dns_resolution_attempted_count']}",
        f"credentials_used_count={result['credentials_used_count']}",
        f"http_adapter_added={str(result['http_adapter_added']).lower()}",
        f"api_client_added={str(result['api_client_added']).lower()}",
        f"credential_handling_added={str(result['credential_handling_added']).lower()}",
        f"failed_checks={failed_checks}",
        f"final_verdict={result['final_verdict']}",
    ]
    if result["final_verdict"] != "DHMS_HTTP_FUSE_DEMO_PASS":
        failed_detail = [
            {
                "name": check_result["name"],
                "script": check_result["script"],
                "exit_code": check_result["exit_code"],
                "observed_verdict": check_result["observed_verdict"],
                "failed_checks": check_result["failed_checks"],
                "stderr": check_result["stderr"],
            }
            for check_result in result["check_results"]
            if not check_result["passed"]
        ]
        lines.append(
            "failed_check_details="
            + json.dumps(failed_detail, separators=(",", ":"), sort_keys=True)
        )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
