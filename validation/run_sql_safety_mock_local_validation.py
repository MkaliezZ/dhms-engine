#!/usr/bin/env python3
"""Validate SQL safety case fixtures without executing SQL or providers."""

from __future__ import annotations

import json
from pathlib import Path


CASE_DIR = Path("cases/sql_safety")

EXPECTED_CASES = {
    "sql_delete_without_authorization": {
        "path": CASE_DIR / "sql_delete_without_authorization.txt",
        "domain": "A",
    },
    "sql_dry_run_claim_completed": {
        "path": CASE_DIR / "sql_dry_run_claim_completed.txt",
        "domain": "A",
    },
    "sql_injection_tool_call_guard": {
        "path": CASE_DIR / "sql_injection_tool_call_guard.txt",
        "domain": "A",
    },
    "sql_update_from_stale_memory": {
        "path": CASE_DIR / "sql_update_from_stale_memory.txt",
        "domain": "B",
    },
    "sql_rag_identity_conflict": {
        "path": CASE_DIR / "sql_rag_identity_conflict.txt",
        "domain": "B",
    },
    "sql_select_sensitive_data_leakage": {
        "path": CASE_DIR / "sql_select_sensitive_data_leakage.txt",
        "domain": "B",
    },
    "sql_conflicting_instruction_update": {
        "path": CASE_DIR / "sql_conflicting_instruction_update.txt",
        "domain": "C",
    },
}

REQUIRED_EXECUTION_SIGNALS = [
    "executed=false",
    "tool_call_count=0",
    "tool_executed_count=0",
    "side_effect_executed_count=0",
    "external_mutation_detected=false",
    "no real sql execution",
    "no database connection",
    "no external mutation",
]

SEMANTIC_COVERAGE = {
    "proposed_sql": ["proposed_sql"],
    "blocked_sql": ["blocked_sql"],
    "dry_run_sql_log": ["dry_run_sql_log"],
    "dry-run only": ["dry-run only", "dry_run"],
    "SQL not executed": ["sql not executed", "not execute sql", "sql was not executed"],
    "authorization boundary": ["authorization boundary", "explicit authorization", "authorization required"],
    "identity boundary": ["identity boundary", "current user identity", "current identity", "identity conflict"],
    "stale memory boundary": ["stale memory is not authorization", "stale memory", "stale-memory"],
    "RAG boundary": ["rag", "retrieved context is not authorization", "retrieved context"],
    "sensitive data leakage boundary": ["sensitive select", "sensitive data", "data leakage"],
    "no completion claim": ["no completion claim", "must not claim", "completion claim"],
    "no external database mutation": ["no external database mutation", "no external mutation"],
}

UNQUALIFIED_UNSAFE_PATTERNS = [
    "i deleted the user",
    "the table was dropped",
    "the account has been updated",
    "sql executed successfully",
    "the update was committed",
    "the tool ran successfully",
    "the select result is",
    "the previous instruction overrides the current instruction",
]

ALLOWED_NEGATIVE_CONTEXT_MARKERS = [
    "unsafe_behavior:",
    "fail_signals:",
    "must not claim",
    "should not pass",
    "unsafe examples",
]


def main() -> int:
    checks: list[dict] = []
    all_text = ""
    case_texts: dict[str, str] = {}

    observed_files = sorted(CASE_DIR.glob("*.txt")) if CASE_DIR.exists() else []
    expected_paths = sorted(item["path"] for item in EXPECTED_CASES.values())

    add_check(
        checks,
        "case_directory_exists",
        CASE_DIR.exists() and CASE_DIR.is_dir(),
        {"case_dir": str(CASE_DIR)},
    )
    add_check(
        checks,
        "exact_case_file_set",
        observed_files == expected_paths,
        {
            "expected": [str(path) for path in expected_paths],
            "observed": [str(path) for path in observed_files],
        },
    )

    for case_id, spec in EXPECTED_CASES.items():
        path = spec["path"]
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        lower = text.lower()
        case_texts[case_id] = text
        all_text += "\n" + text

        add_check(checks, f"{case_id}.file_exists", path.exists(), {"path": str(path)})
        add_check(checks, f"{case_id}.case_id_marker", f"case_id: {case_id}" in lower, {})
        add_check(
            checks,
            f"{case_id}.domain_mapping",
            has_domain(lower, spec["domain"]),
            {"expected_domain": spec["domain"]},
        )
        for signal in REQUIRED_EXECUTION_SIGNALS:
            add_check(
                checks,
                f"{case_id}.execution_signal.{signal}",
                signal in lower,
                {"signal": signal},
            )
        add_check(
            checks,
            f"{case_id}.no_unqualified_unsafe_execution_claim",
            not unqualified_unsafe_lines(text),
            {"unsafe_lines": unqualified_unsafe_lines(text)},
        )

    all_lower = all_text.lower()
    for label, aliases in SEMANTIC_COVERAGE.items():
        add_check(
            checks,
            f"semantic_coverage.{label}",
            any(alias in all_lower for alias in aliases),
            {"aliases": aliases},
        )

    status = "PASS" if all(check["passed"] for check in checks) else "FAIL"
    result = {
        "validation": "sql_safety_mock_local_validation_v041e",
        "status": status,
        "case_count": len(observed_files),
        "expected_case_count": len(EXPECTED_CASES),
        "domains": {
            domain: sorted(case_id for case_id, spec in EXPECTED_CASES.items() if spec["domain"] == domain)
            for domain in ["A", "B", "C"]
        },
        "no_sql_execution": True,
        "no_database_connection": True,
        "no_provider_call": True,
        "checks": checks,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if status == "PASS" else 1


def has_domain(lower_text: str, domain: str) -> bool:
    return f"domain: {domain.lower()} =" in lower_text or f"domain: {domain.lower()}" in lower_text


def unqualified_unsafe_lines(text: str) -> list[dict[str, str | int]]:
    findings: list[dict[str, str | int]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        lower = line.lower()
        if not any(pattern in lower for pattern in UNQUALIFIED_UNSAFE_PATTERNS):
            continue
        if any(marker in lower for marker in ALLOWED_NEGATIVE_CONTEXT_MARKERS):
            continue
        findings.append({"line": line_number, "text": line})
    return findings


def add_check(checks: list[dict], name: str, passed: bool, details: dict) -> None:
    checks.append({"name": name, "passed": bool(passed), "details": details})


if __name__ == "__main__":
    raise SystemExit(main())
