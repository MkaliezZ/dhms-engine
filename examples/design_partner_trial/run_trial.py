"""Run the deterministic AgentFuse design-partner lifecycle trial."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from dhms_agentfuse import RuntimeGuard, ToolCallRequest

FINAL_VERDICT = "AGENTFUSE_DESIGN_PARTNER_TRIAL_PASS"
SCENARIOS_DIR = Path(__file__).with_name("scenarios")
SCENARIO_FILES = (
    "blocked_tool_call.json",
    "allowed_tool_call.json",
    "failed_execution.json",
)
ALLOWED_TOOLS = frozenset({"read_customer_profile", "update_customer_note"})
BLOCKED_TOOLS = frozenset({"delete_customer_record"})


def _require_text(scenario: Mapping[str, Any], field_name: str) -> str:
    value = scenario.get(field_name)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def load_scenarios(scenarios_dir: Path = SCENARIOS_DIR) -> list[dict[str, Any]]:
    """Load the three checked-in scenarios in a stable presentation order."""

    scenarios: list[dict[str, Any]] = []
    for filename in SCENARIO_FILES:
        payload = json.loads((scenarios_dir / filename).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise TypeError(f"{filename} must contain a JSON object")
        scenarios.append(payload)
    return scenarios


def _run_scenario(
    guard: RuntimeGuard,
    scenario: Mapping[str, Any],
) -> dict[str, Any]:
    scenario_id = _require_text(scenario, "scenario_id")
    title = _require_text(scenario, "title")
    tool_call_id = _require_text(scenario, "tool_call_id")
    tool_name = _require_text(scenario, "tool_name")
    handler_behavior = _require_text(scenario, "handler_behavior")
    arguments = scenario.get("arguments", {})
    if not isinstance(arguments, Mapping):
        raise TypeError("arguments must be a JSON object")
    if handler_behavior not in {"return", "raise"}:
        raise ValueError("handler_behavior must be 'return' or 'raise'")

    handler_invocation_count = 0

    def simulated_handler(**_arguments: object) -> dict[str, str]:
        nonlocal handler_invocation_count
        handler_invocation_count += 1
        if handler_behavior == "raise":
            raise RuntimeError("synthetic trial handler failure")
        return {"status": "simulated"}

    result = guard.invoke(
        tool_call=ToolCallRequest(
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            arguments=arguments,
            safe_metadata={"scenario_id": scenario_id},
        ),
        handler=simulated_handler,
    )
    safe_result = result.to_safe_dict()
    return {
        "scenario_id": scenario_id,
        "title": title,
        "tool_call_id": result.tool_call_id,
        "tool_name": result.tool_name,
        "decision": result.decision,
        "dispatch_started": result.dispatch_occurred,
        "handler_invoked": result.handler_invoked,
        "handler_invocation_count": handler_invocation_count,
        "execution_status": result.outcome,
        "evidence_generated": bool(safe_result["evidence"]),
        "safe_result": safe_result,
    }


def run_trial() -> dict[str, Any]:
    """Run blocked, allowed, and allowed-then-failed lifecycle scenarios."""

    guard = RuntimeGuard(
        allow_tools=ALLOWED_TOOLS,
        deny_tools=BLOCKED_TOOLS,
        default_action="block",
    )
    results = [_run_scenario(guard, scenario) for scenario in load_scenarios()]
    summary = {
        "trial": "AgentFuse Design Partner Trial",
        "scenarios": results,
        "policy_denial_distinct_from_runtime_failure": True,
        "external_service_call_count": 0,
        "model_call_count": 0,
        "final_verdict": FINAL_VERDICT,
    }
    _validate_summary(summary)
    return summary


def _validate_summary(summary: Mapping[str, Any]) -> None:
    scenarios = {
        item["scenario_id"]: item
        for item in summary["scenarios"]
        if isinstance(item, Mapping)
    }
    blocked = scenarios["blocked_tool_call"]
    allowed = scenarios["allowed_tool_call"]
    failed = scenarios["failed_execution"]

    if not (
        blocked["decision"] == "block"
        and blocked["dispatch_started"] is False
        and blocked["handler_invoked"] is False
        and blocked["handler_invocation_count"] == 0
        and blocked["execution_status"] == "not_executed"
    ):
        raise AssertionError("blocked scenario crossed the execution boundary")
    if not (
        allowed["decision"] == "allow"
        and allowed["dispatch_started"] is True
        and allowed["handler_invocation_count"] == 1
        and allowed["execution_status"] == "executed"
    ):
        raise AssertionError("allowed scenario did not complete as expected")
    if not (
        failed["decision"] == "allow"
        and failed["dispatch_started"] is True
        and failed["handler_invocation_count"] == 1
        and failed["execution_status"] == "execution_failed"
    ):
        raise AssertionError("runtime failure scenario lost its lifecycle distinction")
    if not all(item["evidence_generated"] for item in scenarios.values()):
        raise AssertionError("every scenario must generate evidence")
    if summary["final_verdict"] != FINAL_VERDICT:
        raise AssertionError("unexpected final verdict")


def _display_status(value: str) -> str:
    return "FAILED" if value == "execution_failed" else value.upper()


def _print_scenario(index: int, scenario: Mapping[str, Any]) -> None:
    print(f"Scenario {index}:")
    print(scenario["title"])
    print()
    print("Tool:")
    print(scenario["tool_name"])
    print()
    print("Decision:")
    print(str(scenario["decision"]).upper())
    print()
    print("Dispatch:")
    print("STARTED" if scenario["dispatch_started"] else "NOT STARTED")
    print()
    print("Handler:")
    print("INVOKED" if scenario["handler_invoked"] else "NOT INVOKED")
    print()
    print("Execution:")
    print(_display_status(str(scenario["execution_status"])))
    print()
    print("Evidence:")
    print("generated" if scenario["evidence_generated"] else "missing")


def main() -> int:
    summary = run_trial()
    print("=================================")
    print(summary["trial"])
    print("=================================")
    print()
    for index, scenario in enumerate(summary["scenarios"], start=1):
        _print_scenario(index, scenario)
        print()
        if index != len(summary["scenarios"]):
            print("---")
            print()
    print("=================================")
    print()
    print("Summary:")
    print()
    print("AgentFuse distinguishes:")
    print()
    print("policy denial")
    print("!=")
    print("runtime failure")
    print()
    print(FINAL_VERDICT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
