"""Provenance checks for historical LangChain interception evidence."""

from __future__ import annotations

from dhms_agentfuse.langchain_interception import (
    EVIDENCE_PROVENANCE_VALUES,
    intercept_langchain_tool_call,
)


def test_interception_trace_labels_observations_and_contract_assertions() -> None:
    result = intercept_langchain_tool_call(
        {
            "id": "provenance-call-001",
            "name": "drop_table",
            "args": {"statement": "PROTECTED_STATEMENT"},
            "type": "tool_call",
        },
        "provenance-test",
    )
    trace = result["interception_trace"]
    provenance = result["interception_trace_provenance"]

    assert set(provenance) == set(trace)
    assert set(provenance.values()) <= EVIDENCE_PROVENANCE_VALUES
    assert provenance["langchain_message_or_tool_call_observed"] == "observed"
    assert provenance["converted_to_dhms_proposal"] == "derived"
    assert provenance["tool_not_executed"] == "asserted_by_contract"
    assert provenance["no_network"] == "asserted_by_contract"
    assert provenance["no_subprocess"] == "asserted_by_contract"
    assert provenance["no_file_mutation"] == "asserted_by_contract"
