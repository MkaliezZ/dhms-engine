"""Cross-adapter conformance tests generated from the canonical v3.6.2 fixtures."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

from examples.conformance.cross_adapter_v3_6_2.run_conformance import (
    ADAPTER_IDS,
    FIXTURE_PATH,
    _failed,
    load_fixture_document,
    render_matrix,
    run_conformance,
    summary,
)


REQUIRED_CASE_IDS = {
    "01_STATIC_ALLOW",
    "02_STATIC_BLOCK",
    "03_EXPLICIT_DENY_WINS",
    "04_NOT_ALLOWLISTED",
    "05_POLICY_EXCEPTION_FAIL_CLOSED",
    "06_INVALID_POLICY_DECISION_FAIL_CLOSED",
    "07_ALLOW_THEN_EXECUTE",
    "08_ALLOW_THEN_HANDLER_FAILURE",
    "09_ALLOW_THEN_INTERRUPT",
    "10_SAFE_RECEIPT",
    "11_DETERMINISTIC_REEVALUATION",
    "12_TOOL_CALL_IDENTITY",
    "13_SYNC_ASYNC_PARITY",
    "14_ONE_TERMINAL_SETTLEMENT",
}
FIXTURE_SHA256 = "1f66c9e20ff28ebeeae128b8aaf38a5b251582496a753acded9530b819056d7b"


def _results():
    return run_conformance(load_fixture_document())


def test_canonical_fixture_is_provider_neutral_bounded_and_deterministic() -> None:
    document = load_fixture_document()
    serialized = json.dumps(document, sort_keys=True, separators=(",", ":"))

    assert {case["case_id"] for case in document["cases"]} == REQUIRED_CASE_IDS
    assert document["canonical_policy_actions"] == ["allow", "block"]
    assert "langgraph" not in serialized.lower()
    assert "deepseek" not in serialized.lower()
    assert "dsh" not in serialized.lower()
    assert "agentfuse-v3.6.2-synthetic-sentinel" not in serialized
    assert "/Users/" not in serialized
    assert "C:\\" not in serialized
    assert hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest() == FIXTURE_SHA256


def test_all_python_owned_adapter_cases_conform_without_hidden_failures() -> None:
    results = _results()
    report = summary(results)

    assert len(results) == len(REQUIRED_CASE_IDS) * len(ADAPTER_IDS)
    assert report["counts"] == {"PASS": 41, "FAIL": 0, "NOT_APPLICABLE": 1}
    not_applicable = [result for result in results if result.verdict == "NOT_APPLICABLE"]
    assert [(result.adapter_id, result.case_id) for result in not_applicable] == [
        ("python-runtime-guard", "09_ALLOW_THEN_INTERRUPT")
    ]
    assert "no host interruption surface" in not_applicable[0].verdict_reason


def test_canonical_policy_semantics_do_not_drift_across_applicable_adapters() -> None:
    document = load_fixture_document()
    expected_by_case = {
        case["case_id"]: (case["expected_policy"]["decision"], case["expected_policy"]["reason"])
        for case in document["cases"]
    }

    for result in _results():
        if result.verdict == "NOT_APPLICABLE":
            continue
        assert (result.policy_decision, result.policy_reason) == expected_by_case[result.case_id]
        assert result.safe_output is True
        assert result.identity_preserved is True


def test_block_cases_never_report_dispatch_or_handler_start() -> None:
    for result in _results():
        if result.verdict == "PASS" and result.policy_decision == "block":
            assert result.dispatch_observed is False
            assert result.handler_started is False
            assert result.execution_outcome == "not_executed"
            assert result.interruption_observed is False


def test_allow_failure_and_interrupt_do_not_rewrite_policy_decision() -> None:
    results = {
        (result.adapter_id, result.case_id): result
        for result in _results()
    }
    for adapter_id in ADAPTER_IDS:
        failed = results[(adapter_id, "08_ALLOW_THEN_HANDLER_FAILURE")]
        assert failed.policy_decision == "allow"
        assert failed.execution_outcome == "execution_failed"

    for adapter_id in ("provider-neutral-reference", "langgraph-tool-node"):
        interrupted = results[(adapter_id, "09_ALLOW_THEN_INTERRUPT")]
        assert interrupted.policy_decision == "allow"
        assert interrupted.execution_outcome == "interrupted"
        assert interrupted.interruption_observed is True


def test_terminal_settlement_claim_is_bounded_to_one_tested_result() -> None:
    terminal_results = [
        result
        for result in _results()
        if result.case_id == "14_ONE_TERMINAL_SETTLEMENT"
    ]

    assert all(result.verdict == "PASS" for result in terminal_results)
    assert all(result.terminal_settlement_count == 1 for result in terminal_results)


def test_generated_report_and_matrix_exclude_raw_protected_arguments() -> None:
    results = _results()
    rendered = json.dumps(summary(results), sort_keys=True) + "\n" + render_matrix(results)

    assert "agentfuse-v3.6.2-synthetic-sentinel" not in rendered
    assert "RAW_" not in rendered
    assert "PASS" in rendered
    assert "NOT_APPLICABLE" in rendered


def test_failure_report_redacts_raw_protected_argument() -> None:
    document = load_fixture_document()
    result = _failed(
        document,
        document["cases"][0],
        "review-adapter",
        RuntimeError("echoed agentfuse-v3.6.2-synthetic-sentinel"),
    )

    assert result.verdict == "FAIL"
    assert result.safe_output is True
    assert "agentfuse-v3.6.2-synthetic-sentinel" not in result.verdict_reason
    assert "<redacted-sensitive-value>" in result.verdict_reason


def test_json_only_cli_emits_one_machine_readable_document() -> None:
    runner = Path(__file__).parents[1] / "examples/conformance/cross_adapter_v3_6_2/run_conformance.py"
    completed = subprocess.run(
        [sys.executable, str(runner), "--json-only"],
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)

    assert completed.stderr == ""
    assert report["counts"] == {"PASS": 41, "FAIL": 0, "NOT_APPLICABLE": 1}


def test_generated_matrix_order_and_values_are_repeatable() -> None:
    first = _results()
    second = _results()

    assert summary(first) == summary(second)
    assert render_matrix(first) == render_matrix(second)
