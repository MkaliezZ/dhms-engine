# DHMS Proof-Line Protocol Lifecycle Mapping Clarification v0.9.3.1

## Audited Base Commit

`bf1642629d1a185cfb96aaac9f919f1cee89b1e2`

## Purpose

v0.9.3.1 clarifies how the completed SQL, File, and HTTP proof lines map back
to the v0.6.0 DHMS Execution Fuse Protocol lifecycle and object model.

This clarification is documentation-only. It does not change runners,
manifests, benchmark behavior, examples, CLI commands, adapters, proof
semantics, or runtime behavior.

## Relationship to v0.6.0 Protocol

The v0.6.0 DHMS Execution Fuse Protocol lifecycle is:

```text
RuntimeRequest
-> ToolCallProposal
-> SafetyDecision
-> ExecutionGateDecision
-> BridgeDecision
-> ReleaseReview
-> ReleaseAuthorization
-> SandboxExecutionResult
-> ExternalStateVerification
-> ExecutionTrace
```

Not every proof line implements these as concrete code objects. Each proof
line must still map its evidence back to this lifecycle:

* unsafe proposals terminate before execution;
* unknown, malformed, unsupported, missing, or ambiguous paths fail closed;
* controlled release requires explicit boundaries;
* actual execution, where present, must be minimal, explicit,
  sandboxed/constrained, verified, and traceable.

## Bounded Claim

v0.9.3.1 clarifies how the SQL, File, and HTTP proof lines map back to the
v0.6.0 DHMS Execution Fuse Protocol lifecycle. It is documentation-only and
does not add execution capability, modify benchmark runners, change manifests,
add adapters, change proof semantics, or authorize new runtime behavior.

## Why This Clarification Is Needed

DHMS now has three proof-line shapes:

* SQL: a controlled runtime-path sandbox release.
* File: a constrained synthetic temp-directory proof.
* HTTP: static inert cases and a non-executing benchmark.

These proof shapes differ intentionally. The clarification prevents readers
from assuming that every line has identical implementation objects or identical
release depth. SQL is the closest completed controlled runtime-path sandbox
release mapping. File follows the same lifecycle semantics through a constrained
synthetic proof. HTTP currently stops at inert/non-executing proposal
validation, gate expectations, metrics, and trace evidence.

## SQL Proof-Line Mapping

| v0.6 Protocol Object        | SQL v0.5/v0.6 Mapping                                                    |
| --------------------------- | ------------------------------------------------------------------------ |
| `RuntimeRequest`            | controlled SQL request / SQL safety case                                 |
| `ToolCallProposal`          | normalized SQL proposal                                                  |
| `SafetyDecision`            | `BLOCK` / `SANDBOX` / `FAIL_CLOSED`                                      |
| `ExecutionGateDecision`     | `CLOSED` / `HELD_FOR_SANDBOX_BRIDGE` / `FAIL_CLOSED`                     |
| `BridgeDecision`            | sandbox bridge eligibility or rejection                                  |
| `ReleaseReview`             | controlled release readiness review                                      |
| `ReleaseAuthorization`      | explicit authorization for the exact allowlisted SELECT                  |
| `SandboxExecutionResult`    | temporary SQLite sandbox execution result                                |
| `ExternalStateVerification` | schema/content/row-count/mutation verification and teardown verification |
| `ExecutionTrace`            | SQL lifecycle trace and final outcome                                    |

SQL v0.5/v0.6 proves only one exact allowlisted SELECT inside a temporary local
SQLite sandbox:

```sql
SELECT id, label, status FROM toy_accounts ORDER BY id;
```

It does not claim arbitrary SQL support, production SQL support, provider SDK
integration, agent SDK integration, HTTP integration, file/shell/MCP policy, or
production-ready runtime support.

## File Proof-Line Mapping

| v0.6 Protocol Object        | File v0.8 Mapping                                                                             |
| --------------------------- | --------------------------------------------------------------------------------------------- |
| `RuntimeRequest`            | file operation safety case / constrained proof case                                           |
| `ToolCallProposal`          | file read/write/delete/unsupported proposal                                                   |
| `SafetyDecision`            | `BLOCK` / `FAIL_CLOSED` / `HOLD` / `CONSTRAINED_ACTION_CANDIDATE`                             |
| `ExecutionGateDecision`     | `CLOSED` / `HELD` / `RELEASED_IN_CONSTRAINED_TEMP_ROOT`                                       |
| `BridgeDecision`            | constrained temp-root eligibility                                                             |
| `ReleaseReview`             | v0.8.4 planning and explicit boundary review                                                  |
| `ReleaseAuthorization`      | process-level explicit approval evidence                                                      |
| `SandboxExecutionResult`    | synthetic fixture read and deterministic synthetic report write inside a disposable temp root |
| `ExternalStateVerification` | temp root cleanup and deletion verification                                                   |
| `ExecutionTrace`            | case results, summary metrics, failed checks, and final verdict                               |

File v0.8 follows the DHMS protocol lifecycle semantics, but does not implement
the full v0.6 object model as concrete code objects. It is a constrained
synthetic temp-directory proof.

File v0.8 does not claim arbitrary file operation support, direct general file
read/write/delete support, file adapter support, MCP file tool integration,
production filesystem safety, or user-data safety.

## HTTP Proof-Line Mapping

| v0.6 Protocol Object        | HTTP v0.9.2/v0.9.3 Mapping                                                                                                                                              |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `RuntimeRequest`            | inert HTTP/network request proposal case                                                                                                                                |
| `ToolCallProposal`          | method, URL, header, body, credential indicator, and target proposal as inert data                                                                                      |
| `SafetyDecision`            | `ALLOW_INERT` / `HOLD_FOR_REVIEW` / `BLOCK` / `FAIL_CLOSED`                                                                                                             |
| `ExecutionGateDecision`     | `INERT_ANALYSIS_ONLY` / `HELD_FOR_REVIEW` / `BLOCKED` / `FAIL_CLOSED`                                                                                                   |
| `BridgeDecision`            | not reached in v0.9.2/v0.9.3                                                                                                                                            |
| `ReleaseReview`             | not authorized in v0.9.2/v0.9.3                                                                                                                                         |
| `ReleaseAuthorization`      | not authorized in v0.9.2/v0.9.3                                                                                                                                         |
| `SandboxExecutionResult`    | none; no HTTP/network execution                                                                                                                                         |
| `ExternalStateVerification` | invariant verification: `network_calls_executed_count == 0`, `http_clients_created_count == 0`, `credentials_used_count == 0`, `external_mutation_attempted_count == 0` |
| `ExecutionTrace`            | benchmark metrics, per-case validation result, failed checks, and final verdict                                                                                         |

HTTP v0.9.2/v0.9.3 is currently non-executing only. `ALLOW_INERT` means inert
analysis/documentation only and does not authorize real network requests. No
bridge, release review, release authorization, sandbox/network execution,
adapter behavior, or real external state mutation exists in v0.9.2/v0.9.3.

## Cross-Line Consistency Summary

SQL, File, and HTTP use different proof shapes. All three must remain traceable
to the v0.6 DHMS Execution Fuse Protocol lifecycle:

* SQL has a controlled runtime-path sandbox release.
* File has a constrained synthetic temp-directory proof.
* HTTP currently has static inert cases and a non-executing benchmark.
* Future HTTP constrained proof, if any, must be separately approved and should
  remain synthetic/local/mock-only/loopback-only with no real external network
  calls.

## Explicit Non-Claims

v0.9.3.1 does not claim:

* new execution capability;
* real HTTP execution;
* real network calls;
* new SQL execution;
* new file execution;
* arbitrary SQL support;
* arbitrary file operation support;
* HTTP adapter support;
* API client support;
* credential handling;
* SSRF protection;
* production outbound request safety;
* production filesystem safety;
* data exfiltration protection;
* external API mutation safety;
* MCP integration;
* OpenClaw integration;
* DeepSeek/provider integration;
* provider SDK integration;
* agent SDK integration;
* shell execution;
* arbitrary tool execution;
* production readiness;
* industry standard status;
* replacement of MCP, guardrails, sandboxes, SDKs, or human approval systems.

## Implementation Boundaries

This patch does not modify:

* `validation/run_dhms_agentfuse_bench_http_v0.py`;
* `benchmarks/dhms_agentfuse_http_v0/cases.json`;
* SQL/File runners;
* CLI commands;
* examples;
* source code;
* benchmark manifests;
* proof semantics;
* release tags.

It does not add HTTP examples, CLI wrapper commands, HTTP execution, network
calls, API clients, HTTP adapters, credential handling, OpenClaw integration,
DeepSeek/provider integration, provider SDK integration, agent SDK integration,
MCP integration, shell execution, or arbitrary tool execution.

## Next Recommended Milestone

`v0.9.4 HTTP Fuse Non-Executing Examples`

Final document verdict:

`READY_FOR_V0_9_4_HTTP_FUSE_NON_EXECUTING_EXAMPLES`
