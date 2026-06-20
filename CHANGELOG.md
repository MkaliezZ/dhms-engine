# Changelog

## Unreleased — Agent Harness v1

* Phase 1: mock dry-run skeleton and trace contract.
* Phase 2: trace diagnosis layer and rule-based trace recommendations.
* Phase 3: command adapter and BYOA local agent JSON protocol.
* Phase 4: agent case-suite runner and aggregate agent diagnosis reports.
* Phase 4.5: MVP demo guide, adapter conformance checklist, bad-agent examples, and smoke validation.
* Phase 4.6: polished command-adapter failure diagnosis labels for invalid JSON, wrong protocol, timeout, nonzero exit, and trace validation errors.
* Phase 4.7: added static HTML reports for single-case Agent Harness reports and aggregate suite reports.
* Next: command adapter hardening, HTTP adapter planning, and trace diagnosis on real agents.

## v0.1.3-product-diagnosis - 2026-06-20

* Sealed DHMS Product Diagnosis v1.3 as the stable checkpoint before Agent Harness v1.
* Added diagnosis taxonomy, deterministic expected-property checks, and rule-based recommendations.
* Documented public demo path with DeepSeek `deepseek:flash` live verification and BYOK adapter-ready providers.
* Added top critical case interpretation examples and optional `n>=3` rerun guidance.
* Clarified that high drift is diagnostic evidence, not automatic provider failure.
* Confirmed `v2_metrics_overridden=false`, API key leakage scan passed, and protected core layers unchanged.
