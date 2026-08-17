# Changelog

## dhms-agentfuse 3.6.3 - Unreleased

* Froze the reviewed v3.6.0-v3.6.2 integration evidence chain and its bounded
  supported claims, non-claims, runtime versions, fixture provenance, and N/A
  boundaries.
* Confirmed the reviewed matrix remains 52 PASS, 4 justified N/A, and 0 FAIL.
* Kept RuntimeGuard, Evidence Schema v0.1, and the LangGraph adapter unchanged.

## dhms-agentfuse 3.6.2 - Unreleased

* Added 14 provider-neutral conformance fixtures for policy and host-lifecycle
  separation across the RuntimeGuard, reference-consumer, LangGraph, and
  independently versioned DSH adapter paths.
* Added deterministic result and matrix generation with explicit N/A reasons,
  identity checks, terminal-settlement scope, and safe-output checks.
* Kept RuntimeGuard core and Evidence Schema v0.1 unchanged.

## dhms-agentfuse 3.6.1 - Unreleased

* Added a provider-neutral consumer integration contract for immutable
  `RuntimeGuardDecision` values.
* Added deterministic reference-consumer proof for blocked, executed,
  interrupted, and handler-failure host lifecycles.
* Clarified that a policy decision is separate from approval, host dispatch,
  execution outcome, process completion, and goal achievement.

## dhms-agentfuse 3.6.0 — Unreleased

* Added immutable `RuntimeGuardDecision`.
* Added public decision-only `RuntimeGuard.evaluate()`.
* Added public decision-only `RuntimeGuard.aevaluate()`.
* `evaluate()` and `aevaluate()` never accept or dispatch handlers.
* `invoke()` and `ainvoke()` reuse the same canonical decision path.
* Policy exceptions and invalid policy results remain fail closed.

## Unreleased — Agent Harness v1

* Phase 1: mock dry-run skeleton and trace contract.
* Phase 2: trace diagnosis layer and rule-based trace recommendations.
* Phase 3: command adapter and BYOA local agent JSON protocol.
* Phase 4: agent case-suite runner and aggregate agent diagnosis reports.
* Phase 4.5: MVP demo guide, adapter conformance checklist, bad-agent examples, and smoke validation.
* Phase 4.6: polished command-adapter failure diagnosis labels for invalid JSON, wrong protocol, timeout, nonzero exit, and trace validation errors.
* Phase 4.7: added static HTML reports for single-case Agent Harness reports and aggregate suite reports.
* Phase 4.8: added preview release readiness checklist and validation report for Agent Harness MVP branch.
* Phase 5: Adapter Conformance Test Kit for local BYOA command agents.
* Next: command adapter hardening, HTTP adapter planning, and trace diagnosis on real agents.

## v0.1.3-product-diagnosis - 2026-06-20

* Sealed DHMS Product Diagnosis v1.3 as the stable checkpoint before Agent Harness v1.
* Added diagnosis taxonomy, deterministic expected-property checks, and rule-based recommendations.
* Documented public demo path with DeepSeek `deepseek:flash` live verification and BYOK adapter-ready providers.
* Added top critical case interpretation examples and optional `n>=3` rerun guidance.
* Clarified that high drift is diagnostic evidence, not automatic provider failure.
* Confirmed `v2_metrics_overridden=false`, API key leakage scan passed, and protected core layers unchanged.
