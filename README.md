# DHMS / AgentFuse

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](pyproject.toml)
[![AgentFuse](https://img.shields.io/badge/AgentFuse-3.6.0-green.svg)](pyproject.toml)
[![Historical Evidence](https://img.shields.io/badge/historical%20evidence-v3.5.2-purple.svg)](docs/dhms_real_langgraph_bigtool_api_wiring_demo_v3_5_2.md)
[![Docs](https://img.shields.io/badge/docs-available-informational.svg)](docs/)

**AgentFuse is an experimental in-process pre-dispatch policy and authorization boundary for AI agent tools.**

An integrating runtime validates its own action, approval, identity, risk, and business-policy contracts, maps trusted context into a `ToolCallRequest`, and asks AgentFuse for a canonical `allow` or `block` decision. AgentFuse can return that decision without dispatch or enforce it before a handler supplied through the guarded invocation path.

AgentFuse is not a process sandbox, malware detector, intrinsic danger classifier, or universal interceptor for unwrapped execution paths.

Chinese overview: [README.zh-CN.md](README.zh-CN.md)

## Current Status

```text
PACKAGE=dhms-agentfuse 3.6.0
PUBLIC_API=RuntimeGuardDecision|evaluate|aevaluate|invoke|ainvoke
EVIDENCE_SCHEMA=agentfuse-evidence-schema-v0.1
HISTORICAL_EVIDENCE_MILESTONE=v3.5.2
CURRENT_BRANCH=agent-harness-v1
```

Current externally relevant evidence:

- **KerniQ v0.6.1 Project Command** — a bounded native Desktop Project Command path is gated by explicit application approval, a durable AgentFuse decision, durable start evidence, and KerniQ-owned native execution. The reviewed real Tauri proof is frozen.
- **KerniQ v0.7 Coding Pack Export** — a separate bounded export profile uses AgentFuse 3.6.0 before durable export start; the native atomic-export path passed a controlled real macOS proof and the v0.7 line is frozen.
- **Hermes #53021 external threat-model proof** — a standalone proof models a deny-by-default session terminal allowlist and verifies pre-dispatch blocking, retry identity, deterministic re-evaluation, and safe receipts. It does not modify Hermes and is not a production Hermes integration.
- **Historical v3.5.2 external-project wiring demo** — real `langgraph_bigtool.create_agent()` API wiring remains a historical evidence checkpoint; it is not the current package version.

## Quickstart

```bash
pip install -e .
python examples/runtime_guard/runtime_guard_mvp_demo.py
python examples/runtime_guard/langgraph_runtime_guard_demo.py
```

Expected final verdicts:

```text
AGENTFUSE_RUNTIME_GUARD_MVP_DEMO_PASS
AGENTFUSE_LANGGRAPH_RUNTIME_GUARD_DEMO_PASS
```

Run the latest external threat-model proof:

```bash
python examples/external_integrations/hermes_53021/session_allowlist_proof.py
python -m pytest tests/test_hermes_53021_external_proof.py -q
```

Expected verdict:

```text
AGENTFUSE_HERMES_53021_EXTERNAL_PROOF_PASS
```

If your system `python` is older than Python 3.10, use a Python 3.11 runtime. This repository documents an editable local package; this README does not claim a PyPI release.

## Runtime Guard

The Runtime Guard evaluates a tool call before guarded dispatch, blocks calls rejected by configured policy, and produces structured decision or execution evidence from the same control path.

### Decision-only API

Use `evaluate()` when another runtime owns approval, persistence, dispatch, and physical outcome recording:

```python
decision = guard.evaluate(tool_call)

assert decision.action in {"allow", "block"}
assert decision.evidence.schema_version == "agentfuse-evidence-schema-v0.1"
```

For asynchronous custom policies, use `await guard.aevaluate(tool_call)`.

`evaluate()` and `aevaluate()` accept no handler and perform no protected side effect. `invoke()` and `ainvoke()` reuse the same public decision path and may dispatch only after that path allows the call.

Complete contract: [AgentFuse Public Decision API 3.6.0](docs/dhms_agentfuse_public_decision_api_v3_6_0.md).

## Responsibility Boundary

### The integrating application owns

- `ActionProposal` and `ActionApproval` creation and validation
- proposal digest, approval identity, expiry, and generation validation
- project, session, task, and action identity validation
- trusted capability and risk classification
- business and organizational safety policy
- durable lifecycle rules around the decision
- physical dispatch, outcome recording, and recovery

Risk classification must come from trusted application configuration or another deterministic application-owned source. It must not be inferred by AgentFuse from prompt text, model arguments, provider metadata, or command output.

### The bridge or adapter owns

- protocol and trusted metadata mapping
- request and response identity validation
- source, schema, policy revision, and protocol checks

Trusted values may be placed in `ToolCallRequest.safe_metadata` for a custom policy to inspect. AgentFuse 3.6.0 does not define or universally validate another runtime's approval schema.

### AgentFuse owns

- deterministic `ToolCallRequest` policy evaluation
- canonical `allow` or `block` decision evidence
- fail-closed handling of policy exceptions and malformed policy results
- pre-dispatch enforcement only for handlers routed through guarded invocation APIs

### AgentFuse does not own

- intrinsic danger classification
- user-intent interpretation
- business correctness
- malware detection
- physical execution owned by another runtime
- universal interception of direct or unwrapped execution paths

```text
AGENTFUSE_CORE_INPUT=ToolCallRequest
AGENTFUSE_CORE_DECISIONS=allow|block
AGENTFUSE_CORE_APPROVAL_CONTRACT=false
AGENTFUSE_CORE_HOLD_DECISION=false
DHMS_IS_A_DANGER_CLASSIFIER=false
DHMS_IS_A_POLICY_AND_AUTHORIZATION_BOUNDARY=true
RISK_CLASSIFICATION_OWNER=INTEGRATING_APPLICATION
PHYSICAL_DISPATCH_OWNER=INTEGRATING_APPLICATION
```

KerniQ maps AgentFuse `allow|block` into its own application vocabulary. `hold` exists in KerniQ's generic action contract but is not emitted by the canonical AgentFuse 3.6.0 bridge.

## Real Consumer Integration: KerniQ

[KerniQ](https://github.com/MkaliezZ/qodex) is a real external consumer of the public AgentFuse 3.6.0 decision-only API. Its pinned canonical AgentFuse source for the frozen consumer proofs is commit [`ec4b5842339dccfba0db62df7541920759203bc9`](https://github.com/MkaliezZ/dhms-engine/commit/ec4b5842339dccfba0db62df7541920759203bc9).

KerniQ owns proposal and approval contracts, lifecycle persistence, dispatch, execution, settlement, and recovery. AgentFuse evaluates the mapped `ToolCallRequest`; the KerniQ bridge and adapter validate source, protocol, policy, schema, request, and response identity before the application treats the decision as dispatch authority.

### Frozen boundary 1: Project Command v0.6.1

The bounded native Desktop Project Command path uses the `kerniq-project-command-v1` profile. The reviewed chain proves, within that path:

- explicit application approval before AgentFuse evaluation;
- a durable AgentFuse decision before `COMMAND_STARTED`;
- zero native dispatch for deny/block, stale authority, cancellation before start, and decision/start persistence failures;
- Rust-side trusted catalog re-resolution and direct no-shell execution;
- truthful `Interrupted` state when settlement persistence is uncertain; and
- restart no-replay with controlled-lifecycle at-most-once behavior in the reviewed proof scope.

References: [freeze activation merge](https://github.com/MkaliezZ/qodex/commit/0486704d613ea203672d75bee455346cceafb225) · [real Tauri proof PR #14](https://github.com/MkaliezZ/qodex/pull/14)

### Frozen boundary 2: Coding Pack Export v0.7

The separate `kerniq-coding-pack-export-v1` profile governs one bounded Coding Pack export lifecycle. The reviewed chain proves, within that path:

- exact proposal and confirmation identity before policy evaluation;
- a digest-only AgentFuse request with no raw source content or absolute local path;
- durable `PACK_DECIDED allow|deny|error` evidence before export start;
- zero destination writes when the durable allow/start boundary is not satisfied;
- native source revalidation, same-filesystem staging, and no-overwrite atomic promotion on the proven macOS path; and
- truthful uncertainty when terminal persistence or post-promotion sync cannot be proven.

The controlled real native proof passed and the v0.7 Coding Pack line is frozen.

References: [v0.7 freeze merge](https://github.com/MkaliezZ/qodex/commit/2aa335dd21453ecf5d3ad44c2279b2c9362bef9f) · [real native export proof PR #24](https://github.com/MkaliezZ/qodex/pull/24)

These integrations do **not** mean all KerniQ actions are AgentFuse-protected. Patch, Git, MCP, browser actions, arbitrary direct IPC, arbitrary file writes, arbitrary shell, and other unreviewed paths remain outside these bounded claims unless separately integrated and proven.

## Latest External Threat-Model Proof: Hermes #53021

The current `agent-harness-v1` head includes a standalone proof for the session-scoped deny-by-default terminal allowlist threat model described in [NousResearch/hermes-agent#53021](https://github.com/NousResearch/hermes-agent/issues/53021).

It models that policy through the public Runtime Guard API and verifies:

- a matching skill-script command can reach the protected in-memory handler;
- a non-allowlisted command is blocked before dispatch;
- compound shell-control syntax is blocked before dispatch;
- retrying the same blocked action keeps the same canonical arguments hash and does not start the handler;
- deterministic re-evaluation of the same blocked action remains blocked;
- a changed action receives a different arguments hash; and
- safe receipts do not contain the original command text.

The proof does not patch Hermes, does not run a real shell, and does not claim Hermes restart persistence or a production Hermes integration.

References: [proof README](examples/external_integrations/hermes_53021/README.md) · [proof script](examples/external_integrations/hermes_53021/session_allowlist_proof.py) · [regression tests](tests/test_hermes_53021_external_proof.py) · [merged proof commit](https://github.com/MkaliezZ/dhms-engine/commit/dd808442c18b104aac24871a660a37bf6e9124fe)

## LangGraph Adapter

AgentFuse includes an explicit installed-LangGraph `ToolNode` adapter. Blocked calls receive a terminal `ToolMessage` bound to the original tool-call ID; allowed handlers use the normal ToolNode execution path. Evidence receipts are available through `adapter.receipts` and `adapter.receipt_for(tool_call_id)`.

This adapter does not make AgentFuse a universal LangGraph interceptor. Only the explicitly wrapped path is controlled.

## Evidence Schema v0.1

AgentFuse Evidence Schema v0.1 represents a blocked tool call as a completed policy decision with non-execution evidence, not as a failed physical tool execution.

The schema keeps decision and execution as separate lifecycle facts. Safe evidence can retain tool-call identity, policy resolution, reason codes, execution state, and digests without including raw arguments, raw paths, environment variables, request bodies, credentials, or other sensitive payloads by default.

Provider-neutral denial regression fixtures are available at [`examples/trial/denial_lifecycle_regression_fixtures/`](examples/trial/denial_lifecycle_regression_fixtures/).

## Historical Evidence Archive

Earlier frozen proof lines remain valid historical evidence; they are not the current package version.

Key checkpoints:

- [v3.4.2 real LangChain multi-tool selective interception result review](docs/dhms_real_langchain_multi_tool_selective_interception_result_review_and_readme_sync_v3_4_2.md)
- [v3.5.2 real `langgraph_bigtool.create_agent()` API wiring demo](docs/dhms_real_langgraph_bigtool_api_wiring_demo_v3_5_2.md)
- [AgentFuse Public Decision API 3.6.0](docs/dhms_agentfuse_public_decision_api_v3_6_0.md)
- [AgentFuse protocol package index](docs/dhms_agentfuse_protocol_package_index_v0_7_0.md)
- [Development roadmap](docs/dhms_agentfuse_development_roadmap.md)
- [Documentation directory](docs/)

The historical v3.5.2 demo remains the latest historical `langgraph_bigtool.create_agent()` wiring checkpoint. It builds a guarded registry but does not compile, invoke, or stream that historical graph and makes no provider, database, SQL, credential, or production-runtime claim.

## What AgentFuse Does Not Claim

AgentFuse is alpha/experimental infrastructure and does not claim:

- production readiness, certification, enterprise compliance, or universal side-effect prevention;
- process sandboxing, network firewalling, descendant-process containment, or malware detection;
- interception of execution paths that do not route through an integrated guard or adapter;
- intrinsic understanding of whether an action is dangerous, correct, authorized, or appropriate for a business;
- that every KerniQ action is protected by AgentFuse;
- that the Hermes #53021 proof is a production Hermes integration; or
- that historical evidence automatically proves arbitrary real-world agent protection.

A real integrating application must still design its own trustworthy action identities, approvals, policy context, durable lifecycle, execution boundary, recovery semantics, and defense-in-depth controls.

## Feedback Wanted

Feedback is especially useful from developers building agent runtimes, tool gateways, approval systems, or side-effect-capable agent products.

Useful feedback includes:

- whether the `evaluate()` decision-only contract is straightforward to integrate into an existing Action Runtime;
- whether the responsibility split between application, adapter, AgentFuse, and physical executor is clear;
- whether the safe evidence vocabulary is sufficient for durable lifecycle recording;
- real execution-boundary threat models similar to Hermes #53021 that can be reduced to a bounded reproducible proof; and
- results from anyone willing to try RuntimeGuard in a real but controlled integration.

Discussion or interest alone is not treated as successful runtime adoption without an actual integration or trial result.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).

Copyright 2026 Huaxinsheng Zhong.

## Trademark Notice

DHMS, DHMS Engine, DHMS AgentFuse, and DHMS Agent Harness are project names and marks of Huaxinsheng Zhong.

Use of these names is permitted for accurate reference to this project, but does not imply endorsement, sponsorship, or affiliation unless explicitly authorized.

The Apache-2.0 license applies to the source code and documentation in this repository. It does not grant trademark rights.
