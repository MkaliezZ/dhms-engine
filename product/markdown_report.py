"""Markdown report generator for DHMS Product Diagnosis v1.3."""

import json
from pathlib import Path
from typing import Any, Mapping

from display_format import display_bool, display_value


def write_markdown_report(product_result: Mapping[str, Any], output_dir: Path) -> str:
    path = output_dir / "dhms_product_report.md"
    path.write_text(build_markdown(product_result), encoding="utf-8")
    return str(path)


def build_markdown(result: Mapping[str, Any]) -> str:
    calibration = result.get("calibration", {})
    baseline = calibration.get("deepseek_smoke_baseline", {})
    current = calibration.get("current_run", {})
    expected = result.get("expected_property_check", {})
    diagnosis_summary = result.get("diagnosis_summary", {})
    lines = [
        "# DHMS Product Report: LLM Memory Stability Tester",
        "",
        "## Executive Summary",
        "",
        f"* Risk Label: **{result['risk_label']}**",
        f"* Primary Diagnosis: **{diagnosis_summary.get('primary_issue', 'not_available')}**",
        f"* Diagnosis Severity: {diagnosis_summary.get('severity', 'not_available')}",
        f"* Diagnosis Confidence: {diagnosis_summary.get('confidence', 'not_available')}",
        f"* Explanation: {diagnosis_summary.get('short_explanation', 'not_available')}",
        f"* Stability Score: {display_value(result['stability_score'])}",
        f"* Sensitivity Score: {display_value(result['sensitivity_score'])}",
        f"* Isolation Strength: {display_value(result['isolation_strength_score'])}",
        f"* Drift Risk: {display_value(result['drift_risk'])}",
        f"* Recommendation: {result['recommendation']}",
        f"* 中文摘要: {result.get('summary_zh', '')}",
        "",
        "## Case Identity",
        "",
        f"* case_id: {result.get('case_id', 'not_available')}",
        f"* case_path: {result.get('case_path', 'not_available')}",
        f"* case_category: {result.get('case_category', 'not_available')}",
        f"* suite_name: {result.get('suite_name', 'not_available')}",
        f"* suite_run_id: {result.get('suite_run_id', 'not_available')}",
        f"* suite_output_dir: {result.get('suite_output_dir', 'not_available')}",
        f"* requested_models: {', '.join(result.get('requested_models') or result.get('models') or [])}",
        f"* Trials: {result['trial_count']}",
        f"* real_api_used: {display_bool(result.get('real_api_used'))}",
        f"* Input preview: {result['input_summary']['preview']}",
        "",
        "## Product Scores",
        "",
        "These are product-level interpretations derived from existing DHMS metrics; DHMS metric semantics are not changed.",
        "",
        f"* Stability: {display_value(result['stability_score'])}",
        f"* Sensitivity: {display_value(result['sensitivity_score'])}",
        f"* Isolation strength: {display_value(result['isolation_strength_score'])}",
        f"* Drift risk: {display_value(result['drift_risk'])}",
        "",
        "## Calibration",
        "",
        f"* Baseline status: {baseline.get('status', 'not_available')}",
        f"* Baseline real API used: {display_bool(baseline.get('real_api_used'))}",
        f"* Baseline fallback used: {display_bool(baseline.get('fallback_used'))}",
        f"* Baseline total real API calls: {display_value(baseline.get('total_real_api_calls'))}",
        f"* Baseline v2_metrics_overridden: {display_bool(baseline.get('v2_metrics_overridden'))}",
        "",
        "## Current Run Real API Status",
        "",
        f"* Current run real API used: {display_bool(current.get('real_api_used'))}",
        f"* Current real API models: {', '.join(current.get('real_api_models') or []) or 'none'}",
        f"* Current fallback used: {display_bool(current.get('fallback_used'))}",
        f"* Current drift score: {display_value(current.get('drift_score'))}",
        f"* Current instability index: {display_value(current.get('instability_index'))}",
        "",
        "### Provider / Model Status",
        "",
    ]
    for status in current.get("provider_statuses", []):
        lines.extend([
            f"* requested_model_spec: {status.get('requested_model_spec')}",
            f"  * provider: {status.get('provider')}",
            f"  * requested_alias: {status.get('requested_alias')}",
            f"  * resolved_model_id: {status.get('resolved_model_id')}",
            f"  * real_api_used: {display_bool(status.get('real_api_used'))}",
            f"  * fallback_used: {display_bool(status.get('fallback_used'))}",
            f"  * failure_mode: {status.get('failure_mode') or 'none'}",
        ])
    lines.extend([
        "",
        "## Expected Property Check",
        "",
        f"* expected_stability_property: {result.get('expected_stability_property') or 'not_available'}",
        f"* passed: {expected.get('passed', 'unknown')}",
        f"* confidence: {expected.get('confidence', 'low')}",
        f"* notes: {expected.get('notes', 'not_available')}",
        "",
        "### Evidence",
        "",
    ])
    for item in expected.get("evidence", []):
        lines.append(f"* {item}")
    lines.extend([
        "",
        "## Diagnosis Summary",
        "",
        f"* primary_issue: {diagnosis_summary.get('primary_issue', 'not_available')}",
        f"* severity: {diagnosis_summary.get('severity', 'not_available')}",
        f"* confidence: {diagnosis_summary.get('confidence', 'not_available')}",
        f"* is_actionable: {display_bool(diagnosis_summary.get('is_actionable'))}",
        f"* short_explanation: {diagnosis_summary.get('short_explanation', 'not_available')}",
        "",
        "## Diagnoses",
        "",
    ])
    for diagnosis in result.get("diagnoses", []):
        lines.extend([
            f"### {diagnosis.get('type', 'unknown')}",
            "",
            f"* severity: {diagnosis.get('severity', 'not_available')}",
            f"* confidence: {diagnosis.get('confidence', 'not_available')}",
            f"* interpretation: {diagnosis.get('interpretation', 'not_available')}",
            "* recommended_actions:",
        ])
        for action in diagnosis.get("recommended_actions", []):
            lines.append(f"  * {action}")
        lines.extend(["", "```json", json.dumps(diagnosis.get("evidence", {}), indent=2, sort_keys=True), "```", ""])
    lines.extend([
        "## Recommendation Evidence",
        "",
        f"* recommendation_confidence: {result.get('recommendation_confidence', 'not_available')}",
        "",
    ])
    for rec in result.get("recommendation_evidence", []):
        lines.extend([
            f"### {rec.get('priority', 'P2')} - {rec.get('affected_layer', 'not_available')}",
            "",
            f"* action: {rec.get('action')}",
            f"* reason: {rec.get('reason')}",
            f"* confidence: {rec.get('confidence')}",
            f"* evidence: {', '.join(rec.get('evidence', []))}",
            "",
        ])
    lines.extend([
        "## Metric Integrity",
        "",
        "* Existing DHMS metrics were not redefined.",
        "* V2 metrics remained authoritative.",
        "* Product Layer only derives user-facing interpretations.",
        f"* v2_metrics_overridden = {display_bool(current.get('v2_metrics_overridden'))}",
        "",
        "## Confidence",
        "",
        f"* diagnosis_confidence: {diagnosis_summary.get('confidence', 'not_available')}",
        f"* recommendation_confidence: {result.get('recommendation_confidence', 'not_available')}",
        f"* n=1 caveat present: {display_bool(result.get('trial_count') == 1)}",
        "",
        "## Recommendation",
        "",
        result["recommendation"],
        "",
        "## Caveats",
        "",
        "* High drift does not automatically mean provider failure.",
        "* n=1 cannot establish general stochastic stability.",
        "* Critical due to expected_property_violation is stronger than Critical due to mock_real_divergence alone.",
        "* Expected property checker is heuristic and should be reviewed by a human.",
        "",
        "## Raw Metric Snapshot",
        "",
        "```json",
        snapshot_json(result),
        "```",
        "",
        "## Reproduction Command",
        "",
        "```bash",
        result["reproduction_command"],
        "```",
        "",
        "## Safety Note",
        "",
        "DHMS measures behavioral stability under controlled perturbation. It does not prove causal internal memory mechanisms.",
        "",
    ])
    return "\n".join(lines)


def snapshot_json(result: Mapping[str, Any]) -> str:
    current = result.get("calibration", {}).get("current_run", {})
    data = {
        "stability_score": display_value(result["stability_score"]),
        "sensitivity_score": display_value(result["sensitivity_score"]),
        "isolation_strength_score": display_value(result["isolation_strength_score"]),
        "drift_risk": display_value(result["drift_risk"]),
        "risk_label": result["risk_label"],
        "current_real_api_used": current.get("real_api_used"),
        "current_drift_score": display_value(current.get("drift_score")),
        "current_instability_index": display_value(current.get("instability_index")),
    }
    return json.dumps(data, indent=2, sort_keys=True)
