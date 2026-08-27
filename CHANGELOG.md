# Changelog

## dhms-agentfuse 3.7.4 - Unreleased

* Made LangGraph receipts distinguish observed host-continuation dispatch from
  unknown physical handler entry, including success, interruption, and opaque
  host failure paths.
* Added canonical SHA-256 validation, immutable policy-candidate evidence,
  identity-chain checks, and explicit provenance for historical interception
  assertions.
* Declared historical LangChain proof helpers as an optional dependency and
  made the v3.7.3 release seal validate canonical Git bytes across checkout
  line-ending conventions.

## dhms-agentfuse 3.7.3 - 2026-08-18

* Sealed the exact v3.7.2 review and post-merge compatibility evidence in a
  concise machine-readable release record and public release document.
* Opened the Experimental Public Beta with a truthful tagged-source install,
  a visible five-minute LangGraph trial, and a low-friction integration request
  form.
* Rotated the existing wheel-first CI to package 3.7.3 while preserving the
  exact three-cell Python/LangGraph compatibility matrix.
* Kept RuntimeGuard, Evidence Schema v0.1, integration profiles and registry,
  the LangGraph adapter, and policy semantics unchanged.

## dhms-agentfuse 3.7.2 - Unreleased

* Added a manifest-driven wheel compatibility matrix for exact Python and
  LangGraph combinations, including the declared runtime floor and frozen
  `langgraph 1.2.11` evidence baseline.
* Added a repository-external public-API compatibility probe with deterministic
  JSON results, source-fallback protection, and explicit runtime validation.
* Extended AgentFuse CI to build one wheel and reuse it across all matrix cells
  while preserving the existing editable-install regression job.
* Kept RuntimeGuard, Evidence Schema v0.1, integration profiles and registry,
  the LangGraph adapter, and the declared dependency range unchanged.

## dhms-agentfuse 3.7.1 - Unreleased

* Added a bounded public-API LangGraph `ToolNode` consumer trial at the frozen
  `langgraph 1.2.11` version.
* Added deterministic allow-once and block-zero-handler trial results plus
  JSON-only output and clean-wheel isolation validation guidance.
* Kept RuntimeGuard, Evidence Schema v0.1, integration profiles, registry, and
  LangGraph adapter behavior unchanged.

## dhms-agentfuse 3.7.0 - Unreleased

* Added an immutable, metadata-only integration profile for each reviewed
  RuntimeGuard, reference-consumer, LangGraph, and external DSH mapping.
* Added deterministic `list_integrations()` and `get_integration()` registry
  operations without runtime discovery, execution, or external dependencies.
* Preserved the frozen v3.6.2 fixture provenance, capability differences, N/A
  boundaries, host ownership, and tested-version limitations.

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
