"""Deterministic local controlled proposal gate for DHMS v3.0.0.

This module evaluates proposal JSON data only. It does not execute proposals,
call tools, access external runtimes, or authorize execution.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple


DHMS_GATE_VERSION = "v3.0.0-local-controlled-proposal-gate"
EVALUATOR_NAME = "local_controlled_proposal_gate"

SAFE_BOUNDARY = "local_read_only_non_executing_safe"
SAFE_CAPABILITIES = {
    "local_read_only_summary",
    "read_only_summary",
    "static_summary",
}

DANGEROUS_CAPABILITY_MAP = {
    "sql_execution": "sql_execution",
    "execute_sql": "sql_execution",
    "sql_query_execution": "sql_execution",
    "sql_mutation": "sql_mutation",
    "drop_table": "sql_mutation",
    "delete_rows": "sql_mutation",
    "update_rows": "sql_mutation",
    "insert_rows": "sql_mutation",
    "db_access": "db_access",
    "database_access": "db_access",
    "db_connection": "db_access",
    "schema_introspection": "schema_introspection",
    "sql_schema_introspection": "schema_introspection",
    "result_readback": "result_readback",
    "db_result_readback": "result_readback",
    "model_api": "model_api",
    "model_provider_call": "model_api",
    "llm_api": "model_api",
    "network": "network",
    "http_request": "network",
    "external_network": "network",
    "subprocess": "subprocess",
    "shell": "subprocess",
    "command_execution": "subprocess",
    "env_access": "env_access",
    "environment_access": "env_access",
    "credential_access": "credential_access",
    "credentials": "credential_access",
    "secret_access": "credential_access",
    "user_data_access": "user_data_access",
    "user_data": "user_data_access",
    "file_mutation": "file_mutation",
    "file_write": "file_mutation",
    "file_delete": "file_mutation",
}

REQUIRED_FIELDS = ("proposal_id", "requested_capabilities", "declared_boundary")


def _as_string_list(value: Any) -> Tuple[List[str], bool]:
    if not isinstance(value, list):
        return [], False
    result: List[str] = []
    for item in value:
        if not isinstance(item, str) or not item:
            return [], False
        result.append(item)
    return result, True


def _unique_preserving_order(values: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def evaluate_controlled_proposal(proposal: Any, input_file: str) -> Dict[str, Any]:
    """Evaluate one local proposal object without executing it."""

    blocked_capabilities: List[str] = []
    reason = ""

    if not isinstance(proposal, dict):
        proposal_id = "unknown"
        decision = "FAIL_CLOSED"
        reason = "proposal_json_must_be_object"
        blocked_capabilities = ["malformed_proposal"]
        capabilities: List[str] = []
        declared_boundary = None
    else:
        proposal_id = proposal.get("proposal_id", "unknown")
        capabilities, capabilities_valid = _as_string_list(proposal.get("requested_capabilities"))
        declared_boundary = proposal.get("declared_boundary")
        missing_required = [field for field in REQUIRED_FIELDS if field not in proposal]

        if not isinstance(proposal_id, str) or not proposal_id:
            proposal_id = "unknown"
            blocked_capabilities.append("malformed_proposal")
        if missing_required or not capabilities_valid or not isinstance(declared_boundary, str):
            blocked_capabilities.append("malformed_proposal")

        for capability in capabilities:
            blocked = DANGEROUS_CAPABILITY_MAP.get(capability)
            if blocked:
                blocked_capabilities.append(blocked)

        unknown_capabilities = [
            capability
            for capability in capabilities
            if capability not in SAFE_CAPABILITIES and capability not in DANGEROUS_CAPABILITY_MAP
        ]
        if unknown_capabilities:
            blocked_capabilities.append("unsupported_tool")

        blocked_capabilities = _unique_preserving_order(blocked_capabilities)

        if blocked_capabilities:
            decision = "FAIL_CLOSED"
            reason = "blocked_capability_detected"
        elif declared_boundary == SAFE_BOUNDARY and capabilities and set(capabilities).issubset(SAFE_CAPABILITIES):
            decision = "RELEASE_CANDIDATE"
            reason = "local_read_only_non_executing_boundary_declared"
        else:
            decision = "HOLD_FOR_REVIEW"
            reason = "ambiguous_boundary"
            blocked_capabilities = ["ambiguous_boundary"]

    return {
        "dhms_gate_version": DHMS_GATE_VERSION,
        "proposal_id": proposal_id,
        "decision": decision,
        "reason": reason,
        "blocked_capabilities": blocked_capabilities,
        "execution_authorized": False,
        "runtime_behaviors_added": 0,
        "evidence_trace": {
            "observed_before_execution": True,
            "input_file": input_file,
            "evaluator": EVALUATOR_NAME,
            "deterministic": True,
            "stdlib_only": True,
            "no_sql_execution": True,
            "no_db_access": True,
            "no_model_api": True,
            "no_network": True,
            "no_subprocess": True,
            "no_env_access": True,
            "no_credentials": True,
            "no_user_data": True,
            "no_file_mutation": True,
            "no_langchain": True,
            "no_kerniq": True,
            "no_e2b": True,
            "no_production_runtime": True,
        },
    }
