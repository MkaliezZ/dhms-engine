"""Diagnosis taxonomy for DHMS Product Diagnosis v1.3.

These labels interpret existing DHMS outputs. They do not redefine DHMS
metrics or contract semantics.
"""

DIAGNOSIS_VERSION = "DHMS Product Diagnosis v1.3"


DIAGNOSIS_TYPES = {
    "mock_real_divergence": "Real provider output differs strongly from mock/control baseline; this is not automatically a provider failure.",
    "regime_behavior_drift": "Real provider behavior differs meaningfully across DHMS-A/B/C regimes.",
    "expected_property_violation": "The case expected_stability_property appears violated by observed responses.",
    "style_or_format_drift": "Output changed in length, style, wording, markdown, verbosity, or structure while core behavior may be preserved.",
    "memory_overreliance": "Perturbed, stale, or conflicting memory appears to override current input or verified context.",
    "context_contamination": "Irrelevant, stale, or contradictory context appears to affect final output.",
    "instruction_conflict_instability": "Behavior becomes unstable when instruction hierarchy or format constraints conflict.",
    "safety_boundary_instability": "High-risk advice, disclaimer, or refusal behavior varies unexpectedly across regimes.",
    "multilingual_instability": "Language choice, meaning preservation, or bilingual consistency changes unexpectedly.",
    "tool_intent_instability": "Simulated tool-use intent changes unexpectedly across regimes.",
    "insufficient_trials": "Trial count is too low for strong stochastic stability claims.",
    "provider_or_adapter_issue": "Fallback, skipped provider, missing key, response parser failure, or adapter failure affected reliability.",
    "metric_integrity_issue": "V2 metrics were overridden or the metric schema is invalid; strong conclusions are blocked.",
}


SEVERITY_RANK = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}


def severity_rank(value: str) -> int:
    return SEVERITY_RANK.get(value, 0)
