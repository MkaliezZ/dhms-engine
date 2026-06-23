#!/usr/bin/env python3
"""CLI for DHMS."""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

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


if __name__ == "__main__":
    raise SystemExit(main())
