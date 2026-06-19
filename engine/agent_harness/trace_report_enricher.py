"""Report enrichment for Agent Harness trace diagnosis."""

from __future__ import annotations

from .trace_diagnosis_engine import diagnose_agent_harness_result


def enrich_agent_harness_result(result: dict, input_text: str) -> dict:
    enriched = dict(result)
    enriched["input_text"] = input_text
    diagnosis = diagnose_agent_harness_result(enriched)
    enriched.update(diagnosis)
    return enriched
