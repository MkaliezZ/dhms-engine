"""Focused tests for the AgentFuse design-partner lifecycle trial."""

from __future__ import annotations

import json

from examples.design_partner_trial.run_trial import FINAL_VERDICT, run_trial


def _scenarios() -> dict[str, dict[str, object]]:
    return {scenario["scenario_id"]: scenario for scenario in run_trial()["scenarios"]}


def test_blocked_scenario_never_invokes_handler() -> None:
    blocked = _scenarios()["blocked_tool_call"]

    assert blocked["decision"] == "block"
    assert blocked["dispatch_started"] is False
    assert blocked["handler_invoked"] is False
    assert blocked["handler_invocation_count"] == 0
    assert blocked["execution_status"] == "not_executed"
    assert blocked["evidence_generated"] is True


def test_allowed_scenario_executes_simulated_handler() -> None:
    allowed = _scenarios()["allowed_tool_call"]

    assert allowed["decision"] == "allow"
    assert allowed["dispatch_started"] is True
    assert allowed["handler_invoked"] is True
    assert allowed["handler_invocation_count"] == 1
    assert allowed["execution_status"] == "executed"


def test_runtime_failure_remains_distinct_from_policy_denial() -> None:
    scenarios = _scenarios()
    blocked = scenarios["blocked_tool_call"]
    failed = scenarios["failed_execution"]

    assert failed["decision"] == "allow"
    assert failed["dispatch_started"] is True
    assert failed["handler_invoked"] is True
    assert failed["handler_invocation_count"] == 1
    assert failed["execution_status"] == "execution_failed"
    assert (failed["decision"], failed["execution_status"]) != (
        blocked["decision"],
        blocked["execution_status"],
    )


def test_trial_output_is_safe_and_deterministic() -> None:
    first = run_trial()
    second = run_trial()
    serialized = json.dumps(first, sort_keys=True)

    assert first == second
    assert first["final_verdict"] == FINAL_VERDICT
    assert first["policy_denial_distinct_from_runtime_failure"] is True
    assert "synthetic-record" not in serialized
    assert "synthetic-profile" not in serialized
    assert "synthetic-note" not in serialized
    assert "synthetic trial handler failure" not in serialized
