# DHMS AgentFuse v3.6.2 Cross-Adapter Conformance Kit

## Purpose

AgentFuse v3.6.1 froze a provider-neutral consumer contract around immutable
`RuntimeGuardDecision` values. v3.6.2 checks whether independently owned
consumer paths preserve that policy meaning while retaining their own runtime
lifecycle semantics.

Conformance here means semantic agreement for a bounded fixture set. It does
not require byte-identical receipts and does not make an adapter the source of
canonical truth.

## Canonical Fixture Vocabulary

The canonical fixture is
[`examples/conformance/cross_adapter_v3_6_2/fixtures.json`](../examples/conformance/cross_adapter_v3_6_2/fixtures.json).
It contains 14 stable cases, fixture version
`agentfuse-cross-adapter-conformance-v3.6.2`, and only the canonical policy
actions `allow | block`.

Each case separates canonical policy facts from host observations.

Canonical policy facts include:

- case, tool-call, and tool-name identity;
- expected `allow | block` decision and reason class;
- whether policy permits host dispatch;
- deterministic arguments-digest semantics; and
- prohibition of raw protected arguments in safe output.

Host observations include:

- whether dispatch and handler start occurred;
- executed, execution-failed, interrupted, or not-executed lifecycle outcome;
- interruption observation;
- identity preservation; and
- terminal settlement count in the tested path.

Approval, retry, recovery, process completion, and goal achievement remain
host-owned facts. DSH `ask` is a host approval deferral and is not a third
canonical AgentFuse policy action.

## Tested Adapters

1. `python-runtime-guard`: canonical Python RuntimeGuard evaluation and guarded
   invocation.
2. `provider-neutral-reference`: the v3.6.1 reference consumer, including host
   interruption semantics.
3. `langgraph-tool-node`: the installed LangGraph `ToolNode` adapter and real
   LangGraph interrupt control flow.
4. `dsh-tools-pre-execute`: the independent DSH plugin over the pinned real
   DeepSeek Harness integration path.

## Result Matrix

The first three columns are rendered by the DHMS conformance runner. The DSH
column is rendered independently from the same fixture snapshot by the DSH
runner. The combined table below records those observed results.

| Case | Python RuntimeGuard | Reference consumer | LangGraph ToolNode | DSH pre-execute |
|---|---:|---:|---:|---:|
| 01 STATIC_ALLOW | PASS | PASS | PASS | PASS |
| 02 STATIC_BLOCK | PASS | PASS | PASS | PASS |
| 03 EXPLICIT_DENY_WINS | PASS | PASS | PASS | PASS |
| 04 NOT_ALLOWLISTED | PASS | PASS | PASS | PASS |
| 05 POLICY_EXCEPTION_FAIL_CLOSED | PASS | PASS | PASS | N/A |
| 06 INVALID_POLICY_DECISION_FAIL_CLOSED | PASS | PASS | PASS | N/A |
| 07 ALLOW_THEN_EXECUTE | PASS | PASS | PASS | PASS |
| 08 ALLOW_THEN_HANDLER_FAILURE | PASS | PASS | PASS | PASS |
| 09 ALLOW_THEN_INTERRUPT | N/A | PASS | PASS | PASS |
| 10 SAFE_RECEIPT | PASS | PASS | PASS | PASS |
| 11 DETERMINISTIC_REEVALUATION | PASS | PASS | PASS | PASS |
| 12 TOOL_CALL_IDENTITY | PASS | PASS | PASS | PASS |
| 13 SYNC_ASYNC_PARITY | PASS | PASS | PASS | N/A |
| 14 ONE_TERMINAL_SETTLEMENT | PASS | PASS | PASS | PASS |

Totals: 56 adapter-case results, 52 PASS, 0 FAIL, and 4 N/A.

## N/A Semantics

N/A means the named capability is absent from that adapter's existing public
surface; it does not hide a failed applicable invariant.

- Python RuntimeGuard case 09: `RuntimeGuard.invoke` has no host interruption
  surface. The reference consumer and LangGraph paths own and prove that host
  lifecycle fact.
- DSH cases 05 and 06: the current TypeScript core exposes static
  configuration, not a call-level custom policy callback that can throw or
  return an invalid decision.
- DSH case 13: `ToolRuntime` exposes one asynchronous execute path rather than
  separate sync and async APIs.

## DSH Provenance

The DSH repository contains a byte-identical fixture snapshot plus provenance:

- canonical repository: `https://github.com/MkaliezZ/dhms-engine`
- canonical fixture commit: `3ed2ccd0aadfcc61ad48ac5a49a54632f7911a91`
- canonical fixture path:
  `examples/conformance/cross_adapter_v3_6_2/fixtures.json`
- fixture SHA-256:
  `1f66c9e20ff28ebeeae128b8aaf38a5b251582496a753acded9530b819056d7b`
- DSH plugin conformance commit:
  `70abcc6b5efcbb3e5b832692ef6b804b4fac5468`
- tested DeepSeek Harness commit:
  `99f6f02fecdb7dff40c3fbc9470f5907c29f74ca`
- tested upstream package version: `0.1.0-rc.7`

The DSH plugin has no Python runtime dependency. DHMS has no DSH runtime
dependency.

## Semantic Drift Invariants

The tests reject these drifts:

- a canonical block becoming allow in another adapter;
- a policy block being reported as an executed handler failure;
- later handler failure mutating an earlier allow decision into block;
- host interruption becoming either policy block or ordinary execution failure;
- raw protected arguments entering safe evidence or report serialization;
- tool-call identity being lost or regenerated where the host exposes it; and
- DSH approval vocabulary leaking into canonical `allow | block` semantics.

For every applicable block case, the tested protected body invocation count is
zero. For allow/failure and allow/interruption cases, the earlier policy
decision remains allow.

## Safe Evidence Boundary

The fixture stores an arguments profile and expected digest, not the raw
sentinel. Runners construct a deterministic synthetic protected value locally
and assert that it is absent from decision-safe output, adapter receipts,
events, result JSON, and rendered matrices. A digest may remain visible.

## Validation Commands

DHMS:

```bash
python3.11 -m pytest tests/test_cross_adapter_conformance_v3_6_2.py -q
python3.11 -m pytest
python3.11 -m compileall -q dhms_agentfuse
python3.11 examples/conformance/cross_adapter_v3_6_2/run_conformance.py
python3.11 -m build
git diff --check
```

DSH uses the workflow
`.github/workflows/agentfuse-conformance.yml`. It checks out the pinned DSH
commit, performs the upstream frozen-lockfile install before overlaying the two
AgentFuse packages, builds them, runs the core/adapter/conformance tests, and
renders the independent matrix.

## Explicit Non-Claims

This milestone does not claim production readiness, universal interception,
formal verification, official LangGraph or DeepSeek certification, exactly-once
physical execution, replay prevention, process sandboxing, DLP, malware
prevention, Claude Code integration, MCP integration, correctness of unwrapped
paths, or external product/deployment validation.
