"""Non-executing benchmark for the DHMS runtime adapter proposal manifest."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path


BENCHMARK_NAME = "DHMS Non-Executing Runtime Adapter Proposal Benchmark"
VERSION = "v1.2.2"
FINAL_PASS = "DHMS_RUNTIME_ADAPTER_PROPOSAL_BENCHMARK_PASS"
FINAL_FAIL = "DHMS_RUNTIME_ADAPTER_PROPOSAL_BENCHMARK_FAIL"
MANIFEST_PATH = Path("benchmarks/dhms_runtime_adapter_proposals_v0/cases.json")
EXPECTED_BOUNDARY = (
    "This manifest contains inert runtime adapter proposals only. No adapter "
    "proposal in this file is intended to be executed by DHMS, by tests, by "
    "CI, by SDKs, by agent runtimes, by model providers, or by human operators."
)

REQUIRED_TOP_LEVEL_FIELDS = {
    "manifest_id",
    "version",
    "purpose",
    "execution_boundary",
    "proposal_count",
    "allowed_policy_decisions",
    "cases",
}

REQUIRED_CASE_FIELDS = {
    "proposal_id",
    "adapter_family",
    "adapter_target",
    "runtime_context",
    "operation_intent",
    "capability_requested",
    "input_payload_class",
    "credential_intent",
    "network_intent",
    "filesystem_intent",
    "process_or_shell_intent",
    "model_provider_intent",
    "memory_or_state_mutation_intent",
    "cost_or_quota_intent",
    "expected_output_class",
    "risk_indicators",
    "proposed_policy_decision",
    "decision_rationale",
    "trace_evidence_reference",
    "execution_allowed",
    "production_safe_claimed",
}

ALLOWED_POLICY_DECISIONS = ["HOLD", "BLOCK", "FAIL_CLOSED"]
EXPECTED_DECISION_COUNTS = {
    "HOLD": 2,
    "BLOCK": 11,
    "FAIL_CLOSED": 6,
}

REQUIRED_CAPABILITY_CATEGORIES = {
    "resource_listing",
    "model_metadata_read",
    "credential_access",
    "user_data_export",
    "network_write_effect",
    "filesystem_mutation",
    "process_or_shell_escalation",
    "unbounded_tool_invocation",
    "model_provider_side_effect",
    "agent_loop_escalation",
    "persistent_memory_mutation",
    "external_workspace_mutation",
    "hidden_runtime_state_access",
    "billing_or_token_cost_side_effect",
    "rate_limit_or_quota_impact",
    "ambiguous_runtime_target",
    "unsupported_adapter_type",
    "malformed_adapter_proposal",
    "production_runtime_access",
}


def joined(*parts: str) -> str:
    return "".join(parts)


FORBIDDEN_CONTENT_PATTERNS = [
    joined("s", "k-"),
    joined("g", "hp_"),
    joined("x", "oxb-"),
    joined("AK", "IA"),
    joined("BEGIN ", "PRIVATE", " KEY"),
    joined("api.", "op", "enai", ".com"),
    joined("api.", "anth", "ropic", ".com"),
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    joined("m", "cp", "://"),
    joined("http", "://"),
    joined("https", "://"),
    joined("/", "Users", "/"),
    joined("/", "home", "/"),
    joined("/", "root", "/"),
    joined("/", "etc", "/"),
    joined("/", "var", "/"),
    ".ssh",
    ".env",
    "rm -rf",
    "curl ",
    "wget ",
    "bash ",
    "sh ",
    "python -c",
    "python3 -c",
    "node -e",
    "os.system",
    "Popen",
    "shell=True",
]

# The manifest intentionally contains inert local-command risk vocabulary such
# as process_or_shell_intent and shell/subprocess escalation. The benchmark
# blocks executable runtime indicators, while allowing those risk labels as
# static coverage categories.
FORBIDDEN_EXECUTION_SYNTAX_PATTERNS = [
    joined("import ", "sub", "process"),
    joined("from ", "sub", "process"),
    joined("sub", "process", ".run"),
    joined("sub", "process", ".call"),
    joined("sub", "process", ".check"),
    joined("sub", "process", ".P", "open"),
]

SOURCE_SELF_CHECK_TERMS = [
    ("import ", "sub", "process"),
    ("from ", "sub", "process"),
    ("sub", "process", "."),
    ("os", ".", "system", "("),
    ("os", ".", "popen", "("),
    ("P", "open", "("),
    ("import ", "pty"),
    ("from ", "pty"),
    ("pty", "."),
    ("asyncio", ".", "create_", "subprocess_", "exec"),
    ("asyncio", ".", "create_", "subprocess_", "shell"),
    ("socket", "."),
    ("urllib", "."),
    ("re", "quests"),
    ("ht", "tpx"),
    ("open", "ai"),
    ("anth", "ropic"),
    ("m", "cp"),
    ("e", "2b"),
    ("co", "dex"),
    ("clau", "de"),
    ("deep", "seek"),
]


def source_self_check() -> list[str]:
    source = Path(__file__).read_text(encoding="utf-8")
    findings: list[str] = []
    for parts in SOURCE_SELF_CHECK_TERMS:
        term = joined(*parts)
        if term in source:
            findings.append(term)
    return findings


def load_manifest(failed_checks: list[str]) -> tuple[str, object | None]:
    if not MANIFEST_PATH.exists():
        failed_checks.append("manifest_missing")
        return "", None
    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    try:
        return manifest_text, json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        failed_checks.append(f"json_invalid:{exc.msg}")
        return manifest_text, None


def find_forbidden_patterns(manifest_text: str) -> list[str]:
    findings = [pattern for pattern in FORBIDDEN_CONTENT_PATTERNS if pattern in manifest_text]
    findings.extend(pattern for pattern in FORBIDDEN_EXECUTION_SYNTAX_PATTERNS if pattern in manifest_text)

    domain_matches = set(re.findall(r"\b[A-Za-z0-9-]+\.(?:com|net|org|io|ai|dev)\b", manifest_text))
    real_domains = sorted(domain for domain in domain_matches if domain != "example.invalid")
    findings.extend(f"real_domain:{domain}" for domain in real_domains)
    return sorted(set(findings))


def validate_manifest(data: object, failed_checks: list[str]) -> dict[str, int | str | dict[str, int]]:
    required_fields_missing_count = 0
    coverage_categories_missing_count = 0
    coverage_categories_validated_count = 0
    release_count = 0
    execution_allowed_true_count = 0
    production_safe_claimed_true_count = 0
    decision_counts: Counter[str] = Counter()

    if not isinstance(data, dict):
        failed_checks.append("top_level_not_dict")
        return {
            "proposal_count": 0,
            "hold_count": 0,
            "block_count": 0,
            "fail_closed_count": 0,
            "release_count": 0,
            "execution_allowed_true_count": 0,
            "production_safe_claimed_true_count": 0,
            "required_fields_missing_count": 0,
            "coverage_categories_validated_count": 0,
            "coverage_categories_missing_count": 19,
        }

    missing_top = sorted(REQUIRED_TOP_LEVEL_FIELDS - set(data.keys()))
    if missing_top:
        required_fields_missing_count += len(missing_top)
        failed_checks.append(f"missing_top_level_fields:{','.join(missing_top)}")

    if data.get("manifest_id") != "dhms_runtime_adapter_proposals_v0":
        failed_checks.append("manifest_id_mismatch")
    if data.get("version") != "v1.2.1":
        failed_checks.append("version_mismatch")
    if data.get("execution_boundary") != EXPECTED_BOUNDARY:
        failed_checks.append("execution_boundary_mismatch")
    if data.get("proposal_count") != 19:
        failed_checks.append("proposal_count_field_mismatch")
    if data.get("allowed_policy_decisions") != ALLOWED_POLICY_DECISIONS:
        failed_checks.append("allowed_policy_decisions_mismatch")

    cases = data.get("cases")
    if not isinstance(cases, list):
        failed_checks.append("cases_not_list")
        cases = []
    if len(cases) != 19:
        failed_checks.append("case_count_mismatch")

    proposal_ids: list[str] = []
    capability_categories: list[str] = []

    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            failed_checks.append(f"case_not_dict:{index}")
            continue

        proposal_id = str(case.get("proposal_id", f"case_{index}"))
        proposal_ids.append(proposal_id)
        missing_case = sorted(REQUIRED_CASE_FIELDS - set(case.keys()))
        if missing_case:
            required_fields_missing_count += len(missing_case)
            failed_checks.append(f"missing_case_fields:{proposal_id}:{','.join(missing_case)}")

        decision = case.get("proposed_policy_decision")
        if isinstance(decision, str):
            decision_counts[decision] += 1
            if decision == "RELEASE":
                release_count += 1
            if decision not in ALLOWED_POLICY_DECISIONS:
                failed_checks.append(f"decision_not_allowed:{proposal_id}:{decision}")
        else:
            failed_checks.append(f"decision_missing_or_not_string:{proposal_id}")

        capability = case.get("capability_requested")
        if isinstance(capability, str):
            capability_categories.append(capability)
        else:
            failed_checks.append(f"capability_missing_or_not_string:{proposal_id}")

        if case.get("execution_allowed") is not False:
            execution_allowed_true_count += 1
            failed_checks.append(f"execution_allowed_not_false:{proposal_id}")
        if case.get("production_safe_claimed") is not False:
            production_safe_claimed_true_count += 1
            failed_checks.append(f"production_safe_claimed_not_false:{proposal_id}")

        risk_indicators = case.get("risk_indicators")
        if not isinstance(risk_indicators, list) or not risk_indicators:
            failed_checks.append(f"risk_indicators_invalid:{proposal_id}")
        if not proposal_id.startswith("runtime_adapter_"):
            failed_checks.append(f"proposal_id_prefix_invalid:{proposal_id}")

        trace_reference = case.get("trace_evidence_reference")
        if not isinstance(trace_reference, str) or not trace_reference.startswith("trace.runtime_adapter."):
            failed_checks.append(f"trace_reference_invalid:{proposal_id}")

    duplicate_ids = sorted({proposal_id for proposal_id in proposal_ids if proposal_ids.count(proposal_id) > 1})
    if duplicate_ids:
        failed_checks.append(f"duplicate_proposal_ids:{','.join(duplicate_ids)}")

    for decision, expected_count in EXPECTED_DECISION_COUNTS.items():
        if decision_counts.get(decision, 0) != expected_count:
            failed_checks.append(f"decision_count_mismatch:{decision}")
    if release_count != 0:
        failed_checks.append("release_count_not_zero")

    actual_capabilities = set(capability_categories)
    missing_capabilities = sorted(REQUIRED_CAPABILITY_CATEGORIES - actual_capabilities)
    extra_capabilities = sorted(actual_capabilities - REQUIRED_CAPABILITY_CATEGORIES)
    if missing_capabilities:
        coverage_categories_missing_count = len(missing_capabilities)
        failed_checks.append(f"coverage_missing:{','.join(missing_capabilities)}")
    if extra_capabilities:
        failed_checks.append(f"coverage_extra:{','.join(extra_capabilities)}")
    coverage_categories_validated_count = len(REQUIRED_CAPABILITY_CATEGORIES & actual_capabilities)

    return {
        "proposal_count": len(cases),
        "hold_count": decision_counts.get("HOLD", 0),
        "block_count": decision_counts.get("BLOCK", 0),
        "fail_closed_count": decision_counts.get("FAIL_CLOSED", 0),
        "release_count": release_count,
        "execution_allowed_true_count": execution_allowed_true_count,
        "production_safe_claimed_true_count": production_safe_claimed_true_count,
        "required_fields_missing_count": required_fields_missing_count,
        "coverage_categories_validated_count": coverage_categories_validated_count,
        "coverage_categories_missing_count": coverage_categories_missing_count,
    }


def main() -> int:
    failed_checks: list[str] = []
    manifest_text, manifest = load_manifest(failed_checks)
    source_findings = source_self_check()
    forbidden_findings = find_forbidden_patterns(manifest_text)

    if source_findings:
        failed_checks.append("source_self_check_failed")
    if forbidden_findings:
        failed_checks.append("forbidden_patterns_found")

    metrics = validate_manifest(manifest, failed_checks) if manifest is not None else {
        "proposal_count": 0,
        "hold_count": 0,
        "block_count": 0,
        "fail_closed_count": 0,
        "release_count": 0,
        "execution_allowed_true_count": 0,
        "production_safe_claimed_true_count": 0,
        "required_fields_missing_count": 0,
        "coverage_categories_validated_count": 0,
        "coverage_categories_missing_count": 19,
    }

    final_verdict = FINAL_PASS if not failed_checks else FINAL_FAIL
    summary = {
        "benchmark_name": BENCHMARK_NAME,
        "version": VERSION,
        "manifest_path": str(MANIFEST_PATH),
        "manifest_id": manifest.get("manifest_id") if isinstance(manifest, dict) else None,
        **metrics,
        "forbidden_pattern_finding_count": len(forbidden_findings),
        "real_endpoint_finding_count": len([finding for finding in forbidden_findings if "domain" in finding or "api." in finding]),
        "sdk_import_or_call_count": len(source_findings),
        "network_call_count": 0,
        "shell_execution_count": 0,
        "subprocess_execution_count": 0,
        "terminal_execution_count": 0,
        "tool_invocation_count": 0,
        "runtime_adapter_implementation_count": 0,
        "failed_checks": failed_checks,
        "final_verdict": final_verdict,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(final_verdict)
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    sys.exit(main())
