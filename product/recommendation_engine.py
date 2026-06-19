"""Rule-based recommendation engine for DHMS Product Diagnosis v1.3."""

from typing import Any, Mapping, Sequence


def build_recommendations(diagnoses: Sequence[Mapping[str, Any]], context: Mapping[str, Any]) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    diagnosis_types = {item.get("type") for item in diagnoses}
    category = context.get("case_category") or "not_available"
    drift = context.get("drift_score")

    if "metric_integrity_issue" in diagnosis_types:
        return [rec(
            "Block interpretation until metric integrity is restored.",
            "v2_metrics_overridden or invalid metric schema prevents reliable product conclusions.",
            ["metric_integrity_issue"],
            "P0",
            "high",
            "metric_integrity",
        )]

    if "provider_or_adapter_issue" in diagnosis_types:
        recommendations.append(rec(
            "Fix provider configuration or adapter failures before interpreting drift.",
            "Provider fallback or skipped execution can make real-model comparisons unreliable.",
            ["provider_or_adapter_issue"],
            "P0",
            "high",
            "provider_config",
        ))

    if "mock_real_divergence" in diagnosis_types:
        recommendations.append(rec(
            "Calibrate the mock baseline against representative real-provider outputs.",
            "High mock-real divergence can reflect baseline/style differences rather than real provider failure.",
            [f"drift_score={drift}", f"case_category={category}"],
            "P1",
            "medium",
            "test_design",
        ))

    if "style_or_format_drift" in diagnosis_types:
        recommendations.append(rec(
            "Add an explicit output contract or structured response schema if format matters.",
            "Observed drift appears at least partly stylistic or structural.",
            [f"case_category={category}"],
            "P1",
            "medium",
            "output_schema",
        ))

    if category == "agent_memory" or "memory_overreliance" in diagnosis_types:
        recommendations.append(rec(
            "Add explicit memory priority hierarchy: current user input > verified context > recent memory > old memory > noisy memory.",
            "Memory perturbation cases need a deterministic conflict policy.",
            [f"case_category={category}", f"drift_score={drift}"],
            "P0",
            "medium",
            "memory_policy",
        ))
        recommendations.append(rec(
            "Add stale/conflicting memory handling that asks for clarification instead of overcommitting.",
            "Conflicting or outdated memory should not silently override current input.",
            [f"case_category={category}"],
            "P0",
            "medium",
            "memory_policy",
        ))

    if category == "rag_context" or "context_contamination" in diagnosis_types:
        recommendations.append(rec(
            "Add retrieval relevance, freshness, and source-confidence filters before context injection.",
            "RAG perturbation cases are sensitive to irrelevant, stale, or contradictory context.",
            [f"case_category={category}"],
            "P0",
            "medium",
            "retrieval_policy",
        ))

    if category == "instruction_conflict" or "instruction_conflict_instability" in diagnosis_types:
        recommendations.append(rec(
            "Add an instruction hierarchy lock and conflict-resolution rule before generation.",
            "Instruction conflict cases require predictable priority handling.",
            [f"case_category={category}"],
            "P0",
            "medium",
            "prompt_contract",
        ))

    if category == "safety_boundary" or "safety_boundary_instability" in diagnosis_types:
        recommendations.append(rec(
            "Add a safety boundary template with escalation and professional-consultation language.",
            "High-risk cases should preserve caution across all regimes.",
            [f"case_category={category}"],
            "P0",
            "medium",
            "safety_policy",
        ))

    if category == "multilingual" or "multilingual_instability" in diagnosis_types:
        recommendations.append(rec(
            "Add a language lock that states the required output language or bilingual field contract.",
            "Multilingual cases need explicit language preservation.",
            [f"case_category={category}"],
            "P1",
            "medium",
            "prompt_contract",
        ))

    if category == "tool_use_prompt" or "tool_intent_instability" in diagnosis_types:
        recommendations.append(rec(
            "Add a verification-before-action policy for simulated tool-use decisions.",
            "The model should not imply real tool execution when only simulation is available.",
            [f"case_category={category}"],
            "P0",
            "medium",
            "prompt_contract",
        ))

    if "expected_property_violation" in diagnosis_types:
        recommendations.append(rec(
            "Rerun the suite after applying the policy fix and compare diagnosis distribution plus drift risk.",
            "Expected-property failures are stronger evidence than mock-real divergence alone.",
            ["expected_property_violation"],
            "P1",
            "medium",
            "test_design",
        ))

    if "insufficient_trials" in diagnosis_types:
        recommendations.append(rec(
            "Rerun with n>=3 before making strong stochastic stability claims.",
            "n=1 is enough for smoke diagnosis but not for general stability confidence.",
            [f"trial_count={context.get('trial_count')}"],
            "P2",
            "high",
            "test_design",
        ))

    return dedupe(recommendations)


def rec(action: str, reason: str, evidence: list[str], priority: str, confidence: str, affected_layer: str) -> dict[str, Any]:
    return {
        "action": action,
        "reason": reason,
        "evidence": evidence,
        "priority": priority,
        "confidence": confidence,
        "affected_layer": affected_layer,
    }


def dedupe(items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    out = []
    for item in items:
        key = (item.get("action"), item.get("affected_layer"))
        if key in seen:
            continue
        seen.add(key)
        out.append(dict(item))
    return out
