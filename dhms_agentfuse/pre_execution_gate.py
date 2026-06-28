"""Stdlib-only DHMS pre-execution gate for static v2.7 fixtures.

The gate evaluates inert proposal dictionaries before any executor handoff. It
does not execute proposed actions, tool input, SQL, database access, model
calls, network calls, subprocesses, or external runtimes.
"""

from typing import Any


ALLOWED_AGENT_FAMILIES = {"dhms_inert_mock_agent", "langchain_sql_agent_like"}


def _base_decision(proposal_id: str, observed_before_execution: bool) -> dict[str, Any]:
    return {
        "proposal_id": proposal_id,
        "dhms_decision": "FAIL_CLOSED",
        "fail_closed_reason": "malformed_tool_input",
        "executor_handoff_allowed": False,
        "execution_authorized": False,
        "observed_before_execution": observed_before_execution,
        "mock_executor_received": False,
        "mock_executor_invocations": 0,
        "sql_execution_attempts": 0,
        "db_connections": 0,
        "schema_introspection": 0,
        "result_readbacks": 0,
        "evidence_id": f"dhms-v2.7.2-{proposal_id}",
    }


def _fail_closed(proposal_id: str, observed_before_execution: bool, reason: str) -> dict[str, Any]:
    decision = _base_decision(proposal_id, observed_before_execution)
    decision["fail_closed_reason"] = reason
    return decision


def _release(proposal_id: str, observed_before_execution: bool) -> dict[str, Any]:
    decision = _base_decision(proposal_id, observed_before_execution)
    decision["dhms_decision"] = "RELEASE"
    decision["fail_closed_reason"] = None
    decision["executor_handoff_allowed"] = True
    decision["execution_authorized"] = True
    return decision


def evaluate_pre_execution_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    """Evaluate an inert proposal before executor handoff.

    The function is deterministic, in-memory, and fail-closed by default. It
    only inspects proposal fields as inert data for classification.
    """

    if not isinstance(proposal, dict):
        return _fail_closed("missing_proposal_id", False, "malformed_tool_input")

    proposal_id_value = proposal.get("proposal_id")
    proposal_id = proposal_id_value if isinstance(proposal_id_value, str) else ""
    observed_before_execution = proposal.get("observed_before_execution") is True

    if not proposal_id:
        return _fail_closed("missing_proposal_id", observed_before_execution, "malformed_tool_input")

    if not observed_before_execution:
        return _fail_closed(proposal_id, False, "malformed_tool_input")

    declared_boundary = proposal.get("declared_boundary")
    if declared_boundary is None or declared_boundary == "":
        return _fail_closed(proposal_id, observed_before_execution, "missing_declared_boundary")

    agent_family = proposal.get("agent_family")
    if agent_family not in ALLOWED_AGENT_FAMILIES:
        return _fail_closed(proposal_id, observed_before_execution, "unknown_agent_family")

    risk_markers_value = proposal.get("risk_markers")
    risk_markers = risk_markers_value if isinstance(risk_markers_value, list) else []
    risk_marker_set = {marker for marker in risk_markers if isinstance(marker, str)}

    proposed_tool = proposal.get("proposed_tool")
    requested_capability = proposal.get("requested_capability")
    proposed_action_value = proposal.get("proposed_action")
    proposed_action = proposed_action_value if isinstance(proposed_action_value, str) else ""
    proposed_action_upper = proposed_action.upper()
    tool_input = proposal.get("tool_input")

    if proposed_tool == "unknown_runtime_tool" or "unsupported_tool" in risk_marker_set:
        return _fail_closed(proposal_id, observed_before_execution, "unsupported_tool_requested")

    if (
        "malformed_input" in risk_marker_set
        or not isinstance(tool_input, dict)
        or tool_input.get("input_kind") == "malformed_by_contract"
    ):
        return _fail_closed(proposal_id, observed_before_execution, "malformed_tool_input")

    if "db_connection" in risk_marker_set or requested_capability == "db_connection":
        return _fail_closed(proposal_id, observed_before_execution, "db_connection_requested")

    if "schema_introspection" in risk_marker_set or requested_capability == "schema_introspection":
        return _fail_closed(proposal_id, observed_before_execution, "schema_introspection_requested")

    if "result_readback" in risk_marker_set or requested_capability == "result_readback":
        return _fail_closed(proposal_id, observed_before_execution, "result_readback_requested")

    if "credential_scope" in risk_marker_set or requested_capability == "credential_scope":
        return _fail_closed(proposal_id, observed_before_execution, "credential_scope_requested")

    if "user_data_scope" in risk_marker_set or requested_capability == "user_data_scope":
        return _fail_closed(proposal_id, observed_before_execution, "user_data_scope_requested")

    if "DELETE FROM" in proposed_action_upper or requested_capability == "sql_mutation":
        return _fail_closed(proposal_id, observed_before_execution, "sql_mutation_requested")

    if (
        "sql_execution" in risk_marker_set
        or requested_capability == "sql_execution"
        or (proposed_tool == "sql_db_query" and "DROP TABLE" in proposed_action_upper)
    ):
        return _fail_closed(proposal_id, observed_before_execution, "sql_execution_requested")

    if (
        proposal_id == "safe_inert_release_candidate_001"
        and proposed_tool == "noop_review_tool"
        and risk_marker_set == set()
        and declared_boundary == "inert_mock_executor_only"
        and requested_capability == "metadata_review_only"
    ):
        return _release(proposal_id, observed_before_execution)

    return _fail_closed(proposal_id, observed_before_execution, "unsupported_tool_requested")
