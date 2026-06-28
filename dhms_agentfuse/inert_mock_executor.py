"""Inert mock executor for DHMS v2.7 pre-execution gate validation.

The mock executor records receipt only. It does not execute proposed actions,
tool input, SQL, database access, model calls, network calls, subprocesses, or
external runtimes.
"""

from typing import Any


def run_inert_mock_executor(proposal: dict[str, Any]) -> dict[str, Any]:
    """Return inert receipt counters for a proposal dictionary."""

    if not isinstance(proposal, dict):
        return {
            "mock_executor_received": False,
            "mock_executor_invocations": 0,
            "sql_execution_attempts": 0,
            "db_connections": 0,
            "schema_introspection": 0,
            "result_readbacks": 0,
        }

    return {
        "mock_executor_received": True,
        "mock_executor_invocations": 1,
        "sql_execution_attempts": 0,
        "db_connections": 0,
        "schema_introspection": 0,
        "result_readbacks": 0,
    }
