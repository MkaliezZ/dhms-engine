#!/usr/bin/env python3
"""DHMS AgentFuse unsupported non-SQL proposal example.

The unsupported proposal is inert data only. This example does not invoke
OpenClaw, DeepSeek, provider SDKs, agent SDKs, HTTP, shell, file, MCP, or any
external tool.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
root_value = str(ROOT)
if root_value not in sys.path:
    sys.path.insert(0, root_value)

from dhms_agentfuse import (  # noqa: E402
    apply_execution_gate,
    build_agentfuse_trace,
    create_runtime_request,
    create_tool_call_proposal,
    evaluate_proposal,
)


def main() -> int:
    result = run_example()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


def run_example() -> dict[str, Any]:
    request = create_runtime_request(
        request_id="example_request_unsupported_non_sql",
        source="dhms_agentfuse_protocol_example",
        intent_summary="Review unsupported non-SQL proposal without execution",
        raw_event={"event_type": "tool_call_proposal", "observed_only": True},
        metadata={"example_id": "unsupported_non_sql_blocked_or_fail_closed"},
    )
    proposal = create_tool_call_proposal(
        proposal_id="example_proposal_unsupported_non_sql",
        request_id=request.request_id,
        tool_name="openclaw.runtime",
        tool_type="OPENCLAW",
        requested_effect="external_runtime_action",
        payload={"action": "inert unsupported proposal"},
        metadata={"example_id": "unsupported_non_sql_blocked_or_fail_closed"},
    )
    decision = evaluate_proposal(proposal)
    gate = apply_execution_gate(proposal, decision)
    trace = build_agentfuse_trace(request, proposal, decision, gate)

    failed_checks: list[str] = []
    if decision.decision not in {"BLOCK", "FAIL_CLOSED"}:
        failed_checks.append("unsupported_non_sql_not_blocked_or_fail_closed")
    if decision.release_eligible:
        failed_checks.append("unsupported_non_sql_release_eligible")
    if decision.direct_execution_allowed:
        failed_checks.append("direct_execution_allowed")
    if gate.execution_allowed:
        failed_checks.append("gate_execution_allowed")
    if trace.executed:
        failed_checks.append("trace_executed")
    if trace.execution_result is not None:
        failed_checks.append("trace_has_execution_result")

    status = "PASS" if not failed_checks else "FAIL"
    return {
        "example_name": "DHMS AgentFuse Unsupported Non-SQL Proposal Example",
        "example_id": "unsupported_non_sql_blocked_or_fail_closed",
        "status": status,
        "request_id": request.request_id,
        "proposal_id": proposal.proposal_id,
        "decision": decision.decision,
        "decision_reason": decision.reason,
        "gate_state": gate.gate_state,
        "release_eligible": decision.release_eligible,
        "direct_execution_allowed": decision.direct_execution_allowed,
        "execution_allowed": gate.execution_allowed,
        "executed": trace.executed,
        "execution_result": trace.execution_result,
        "openclaw_invoked": False,
        "deepseek_invoked": False,
        "provider_sdk_invoked": False,
        "agent_sdk_invoked": False,
        "http_adapter_invoked": False,
        "file_shell_mcp_policy_added": False,
        "failed_checks": failed_checks,
        "final_verdict": (
            "UNSUPPORTED_NON_SQL_PROPOSAL_EXAMPLE_PASS"
            if status == "PASS"
            else "UNSUPPORTED_NON_SQL_PROPOSAL_EXAMPLE_FAIL"
        ),
    }


if __name__ == "__main__":
    raise SystemExit(main())
