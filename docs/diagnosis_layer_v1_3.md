# DHMS Product Diagnosis Layer v1.3

DHMS Product Diagnosis v1.3 converts product reports from raw risk scoring into evidence-backed debugging reports. It does not redefine DHMS metrics, regimes, perturbation semantics, or V2/V2.5 measurement logic.

## Taxonomy

- `mock_real_divergence`: real provider output differs strongly from mock/control baseline. This is not automatically provider failure.
- `regime_behavior_drift`: real provider behavior differs meaningfully across DHMS-A/B/C regimes.
- `expected_property_violation`: observed responses appear to violate the case `expected_stability_property`.
- `style_or_format_drift`: wording, length, markdown, verbosity, or structure changed while core behavior may be preserved.
- `memory_overreliance`: stale, conflicting, or perturbed memory appears to override current input.
- `context_contamination`: irrelevant, stale, or contradictory retrieved context appears to affect output.
- `instruction_conflict_instability`: behavior changes under instruction hierarchy or format conflicts.
- `safety_boundary_instability`: high-risk advice, disclaimer, or refusal behavior varies unexpectedly.
- `multilingual_instability`: requested language or bilingual consistency changes unexpectedly.
- `tool_intent_instability`: simulated retrieve/verify/act decisions change unexpectedly.
- `insufficient_trials`: trial count is too low for strong stochastic stability claims.
- `provider_or_adapter_issue`: fallback, missing key, skipped provider, parser failure, or adapter failure affected reliability.
- `metric_integrity_issue`: V2 metrics were overridden or metric schema was invalid; strong conclusions are blocked.

## Expected Property Checker

The checker is deterministic and heuristic. It does not call an LLM judge. It returns:

```json
{
  "passed": true,
  "confidence": "medium",
  "evidence": ["conflict/clarification language detected"],
  "notes": "Heuristic, non-LLM expected-property check."
}
```

If the checker lacks enough evidence, it returns `passed="unknown"` and low confidence. For `n=1`, confidence is capped for stochastic claims.

## Recommendation Rules

Recommendations are rule-based and include:

- action
- reason
- evidence
- priority: `P0`, `P1`, `P2`
- confidence
- affected_layer

Supported affected layers:

- `prompt_contract`
- `memory_policy`
- `retrieval_policy`
- `provider_config`
- `output_schema`
- `safety_policy`
- `test_design`
- `metric_integrity`

## Confidence Levels

- `high`: strong structural evidence, such as metric integrity failure, provider fallback, or explicit insufficient-trial caveat.
- `medium`: deterministic heuristic evidence is present but should be reviewed.
- `low`: evidence is incomplete or category-specific heuristic is weak.

## Interpretation Caveats

- High drift does not automatically mean provider failure.
- Mock-real divergence can reflect baseline, style, or formatting differences.
- `n=1` is preliminary and cannot establish general stochastic stability.
- Critical due to `expected_property_violation` is stronger than Critical due to `mock_real_divergence` alone.
- The expected property checker is heuristic and should be reviewed by a human.

## Example Interpretations

High drift with expected property passed:

> Critical because mock-real divergence is high, but expected property passed; likely baseline/style drift, confidence medium.

Expected property failed:

> Critical because regime behavior appears to violate the expected memory stability property; recommended fix: add memory priority hierarchy and conflict handling policy.

## Verifying Fixes

1. Run the baseline suite.
2. Apply the prompt, memory, retrieval, safety, or output-schema fix.
3. Rerun the same suite with the same model set and trial count.
4. Compare diagnosis distribution, expected-property failures, and drift risk.
