#!/usr/bin/env python3
"""Deterministic per-call denial lifecycle trial demo.

The batch is local and inert. It demonstrates that one denied call receives a
terminal non-execution result while a separate allowed call still executes.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dhms_agentfuse.evidence_schema import (  # noqa: E402
    AgentFuseEvidenceRecord,
    safe_read_only_summary_evidence,
    sql_mutation_block_evidence,
)


FINAL_VERDICT = "AGENTFUSE_PER_CALL_DENIAL_TRIAL_DEMO_PASS"
ALLOWED_CALL_ID = "call:safe_read_only_summary_tool:001"
ALLOWED_TOOL_NAME = "safe_read_only_summary_tool"
DENIED_CALL_ID = "call:dangerous_sql_mutation_tool:001"
DENIED_TOOL_NAME = "dangerous_sql_mutation_tool"
_RAW_SENSITIVE_PAYLOAD = "RAW_SENSITIVE_TRIAL_PAYLOAD_MUST_NOT_APPEAR"


@dataclass(frozen=True)
class TrialToolCallRequest:
    """One local inert request in the deterministic two-call batch."""

    call_id: str
    tool_name: str
    payload: str
    evidence_factory: Callable[[], AgentFuseEvidenceRecord]
    handler: Callable[[dict[str, int], str], dict[str, str] | None]


def _safe_read_only_handler(state: dict[str, int], _payload: str) -> dict[str, str]:
    state["allowed_handler_execution_count"] += 1
    return {"summary": "deterministic inert local summary"}


def _denied_mutation_handler(state: dict[str, int], _payload: str) -> None:
    state["denied_handler_execution_count"] += 1
    raise AssertionError("denied handler must never run")


def _allowed_terminal_record(
    call_id: str,
    tool_name: str,
    evidence: AgentFuseEvidenceRecord,
    handler: Callable[[dict[str, int], str], dict[str, str]],
    state: dict[str, int],
    payload: str,
) -> dict[str, Any]:
    result = handler(state, payload)
    return {
        "tool_call_id": call_id,
        "tool_name": tool_name,
        "decision": evidence.boundary_decision.decision,
        "outcome": "executed",
        "terminal": True,
        "handler_invoked": True,
        "handler_execution_count": state["allowed_handler_execution_count"],
        "result": result,
        "evidence": evidence.to_dict(),
    }


def _denied_terminal_record(
    call_id: str,
    tool_name: str,
    evidence: AgentFuseEvidenceRecord,
) -> dict[str, Any]:
    non_execution = evidence.non_execution
    if non_execution is None:
        raise AssertionError("denied record requires non-execution evidence")
    if non_execution.call_id != call_id or evidence.trace_metadata.tool_name != tool_name:
        raise AssertionError("denied result must remain bound to the original call")
    return {
        "tool_call_id": call_id,
        "tool_name": tool_name,
        "decision": evidence.boundary_decision.decision,
        "outcome": non_execution.status,
        "execution": non_execution.execution,
        "terminal": True,
        "handler_invoked": False,
        "payload_executed": non_execution.payload_executed,
        "side_effect_occurred": non_execution.side_effect_occurred,
        "tool_failure": non_execution.tool_failure,
        "reason_code": evidence.boundary_decision.reason_code,
        "result_ref": non_execution.result_ref,
        "evidence": evidence.to_dict(),
    }


def run_demo() -> dict[str, Any]:
    state = {
        "allowed_handler_execution_count": 0,
        "denied_handler_execution_count": 0,
    }
    # Denied first makes continuation of the remaining allowed call observable.
    batch = [
        TrialToolCallRequest(
            call_id=DENIED_CALL_ID,
            tool_name=DENIED_TOOL_NAME,
            payload=_RAW_SENSITIVE_PAYLOAD,
            evidence_factory=sql_mutation_block_evidence,
            handler=_denied_mutation_handler,
        ),
        TrialToolCallRequest(
            call_id=ALLOWED_CALL_ID,
            tool_name=ALLOWED_TOOL_NAME,
            payload=_RAW_SENSITIVE_PAYLOAD,
            evidence_factory=safe_read_only_summary_evidence,
            handler=_safe_read_only_handler,
        ),
    ]
    records: list[dict[str, Any]] = []
    for request in batch:
        evidence = request.evidence_factory()
        if evidence.boundary_decision.decision == "block":
            records.append(
                _denied_terminal_record(
                    request.call_id,
                    request.tool_name,
                    evidence,
                )
            )
            continue
        records.append(
            _allowed_terminal_record(
                request.call_id,
                request.tool_name,
                evidence,
                request.handler,
                state,
                request.payload,
            )
        )

    denied_record, allowed_record = records

    summary = {
        "batch_completed": True,
        "batch_request_count": len(batch),
        "batch_tool_call_count": len(records),
        "allowed_tool_call_id": ALLOWED_CALL_ID,
        "allowed_decision": allowed_record["decision"],
        "allowed_outcome": allowed_record["outcome"],
        "allowed_handler_execution_count": state["allowed_handler_execution_count"],
        "denied_tool_call_id": DENIED_CALL_ID,
        "denied_decision": denied_record["decision"],
        "denied_outcome": denied_record["outcome"],
        "denied_execution": denied_record["execution"],
        "denied_handler_invoked": denied_record["handler_invoked"],
        "denied_payload_executed": denied_record["payload_executed"],
        "denied_side_effect_occurred": denied_record["side_effect_occurred"],
        "denied_handler_execution_count": state["denied_handler_execution_count"],
        "remaining_allowed_call_continued": state["allowed_handler_execution_count"] == 1,
        "safe_trace_only": all(
            record["evidence"]["trace_metadata"]["raw_inputs_in_trace"] is False
            and record["evidence"]["trace_metadata"]["model_visible_trace_sanitized"] is True
            for record in records
        ),
        "network_request_count": 0,
        "sql_execution_count": 0,
        "filesystem_mutation_count": 0,
        "credential_access_count": 0,
        "provider_call_count": 0,
        "model_call_count": 0,
        "graph_invocation_count": 0,
        "external_service_call_count": 0,
        "terminal_lifecycle_records": records,
        "final_verdict": FINAL_VERDICT,
    }
    _validate_summary(summary)
    return summary


def _validate_summary(summary: dict[str, Any]) -> None:
    expected = {
        "batch_completed": True,
        "batch_request_count": 2,
        "batch_tool_call_count": 2,
        "allowed_decision": "allow",
        "allowed_outcome": "executed",
        "allowed_handler_execution_count": 1,
        "denied_decision": "block",
        "denied_outcome": "not_executed",
        "denied_execution": "not_started",
        "denied_handler_invoked": False,
        "denied_payload_executed": False,
        "denied_side_effect_occurred": False,
        "denied_handler_execution_count": 0,
        "remaining_allowed_call_continued": True,
        "safe_trace_only": True,
    }
    for key, value in expected.items():
        if summary[key] != value:
            raise AssertionError(f"{key} must be {value!r}")
    if summary["final_verdict"] != FINAL_VERDICT:
        raise AssertionError("unexpected final verdict")


def main() -> int:
    summary = run_demo()
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(FINAL_VERDICT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
