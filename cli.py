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
)
for path in PATHS:
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)

from engine_runner import run  # noqa: E402
from output_formatter import format_output  # noqa: E402
from agent_harness.harness_runner import run_agent_harness  # noqa: E402
from product_runner import run_product_test  # noqa: E402
from suite_runner import run_suite  # noqa: E402
from provider_status import format_status_table, models_for, provider_statuses  # noqa: E402


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
    agent_parser.add_argument("--mock-agent", action="store_true")
    agent_parser.add_argument("--input", dest="input_text")
    agent_parser.add_argument("--input-file")
    agent_parser.add_argument("--n", type=int, default=1)
    agent_parser.add_argument("--mode", default="B", choices=["A", "B", "C"])
    agent_parser.add_argument("--report", action="store_true")
    agent_parser.add_argument("--output", default="reports/agent_harness/latest")

    subparsers.add_parser("doctor")

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
        if not args.mock_agent:
            print("Phase 1 supports only --mock-agent. Command/HTTP adapters will be added later.")
            return 1
        if not args.input_text and not args.input_file:
            parser.error("test-agent requires either --input or --input-file")
        if args.n < 1:
            parser.error("--n must be >= 1")
        input_text = args.input_text
        if args.input_file:
            input_text = Path(args.input_file).read_text(encoding="utf-8")
        result = run_agent_harness(
            input_text=input_text or "",
            adapter="mock",
            n=args.n,
            mode=args.mode,
            report=args.report,
            output=args.output,
        )
        if args.report:
            print(agent_console_summary(result))
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
        "DHMS Agent Harness Phase 1 Report",
        f"Adapter: {result['adapter']}",
        f"Mode: {result['mode']}",
        f"Trials: {result['trial_count']}",
        f"Dry run: {str(result['dry_run']).lower()}",
        f"Tool calls: {result['tool_call_count']}",
        f"Memory reads: {result['memory_read_count']}",
        f"Side effects blocked: {result['side_effects_blocked_count']}",
        "",
        "Reports:",
    ]
    for path in result.get("report_paths", {}).values():
        lines.append(f"* {path}")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
