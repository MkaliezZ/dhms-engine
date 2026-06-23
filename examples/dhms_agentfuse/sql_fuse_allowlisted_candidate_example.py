#!/usr/bin/env python3
"""DHMS AgentFuse allowlisted SQL candidate example.

This example is non-executing. It builds DHMS AgentFuse protocol objects for
the known allowlisted SQL candidate and shows that the candidate is held rather
than executed.
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
    ALLOWLISTED_SQL,
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
        request_id="example_request_sql_fuse_allowlisted_candidate",
        source="dhms_agentfuse_protocol_example",
        intent_summary="Review allowlisted SQL candidate without execution",
        raw_event={"event_type": "tool_call_proposal", "observed_only": True},
        metadata={"example_id": "sql_fuse_allowlisted_candidate_held"},
    )
    proposal = create_tool_call_proposal(
        proposal_id="example_proposal_sql_fuse_allowlisted_candidate",
        request_id=request.request_id,
        tool_name="sql.query",
        tool_type="SQL",
        requested_effect="read_sandbox_candidate",
        payload={"sql": ALLOWLISTED_SQL},
        metadata={"example_id": "sql_fuse_allowlisted_candidate_held"},
    )
    decision = evaluate_proposal(proposal)
    gate = apply_execution_gate(proposal, decision)
    trace = build_agentfuse_trace(request, proposal, decision, gate)

    failed_checks: list[str] = []
    if decision.decision not in {"ALLOWLIST_CANDIDATE_HELD", "SANDBOX_HELD"}:
        failed_checks.append("candidate_not_held")
    if not decision.release_eligible:
        failed_checks.append("candidate_not_release_eligible")
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
        "example_name": "DHMS AgentFuse SQL Fuse Allowlisted Candidate Example",
        "example_id": "sql_fuse_allowlisted_candidate_held",
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
        "sql_executed": False,
        "sqlite_database_created": False,
        "sandbox_created": False,
        "failed_checks": failed_checks,
        "final_verdict": (
            "SQL_FUSE_ALLOWLISTED_CANDIDATE_EXAMPLE_PASS"
            if status == "PASS"
            else "SQL_FUSE_ALLOWLISTED_CANDIDATE_EXAMPLE_FAIL"
        ),
    }


if __name__ == "__main__":
    raise SystemExit(main())
