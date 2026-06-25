# DHMS Controlled Adapter Skeleton Planning v1.7.0

## Purpose

This document plans a future DHMS Controlled Adapter Skeleton in prose only. It
defines what a future controlled adapter skeleton may be allowed to demonstrate
and what it must not do.

v1.7.0 is documentation and planning only. It does not add adapter code,
implementation, schema files, SDK integration, runtime integration, runners,
CLI commands, execution behavior, or production runtime claims.

## v1.7.0 Claim

DHMS v1.7.0 plans a future controlled adapter skeleton boundary without adding
adapter code, implementation, schema files, SDK integration, runtime
integration, runners, CLI commands, execution behavior, or production runtime
claims.

## Current Context After v1.4-v1.6

v1.7.0 follows the post-v1.3 planning line:

* v1.4 clarified substrate/runtime boundaries.
* v1.5 planned the Agent Proposal Envelope.
* v1.6 planned the External Runtime Handoff Contract.
* v1.7 now plans a future controlled adapter skeleton, but does not implement
  it.

This phase keeps DHMS at the planning layer. It does not create a production
adapter, runtime adapter implementation, SDK integration, MCP adapter, E2B
adapter, provider integration, agent runtime integration, parser, executor, or
execution path.

## Controlled Adapter Skeleton Concept

A future controlled adapter skeleton may eventually demonstrate this conceptual
path only:

```text
agent proposal envelope
DHMS decision
handoff contract
controlled adapter skeleton receives the boundary
adapter skeleton refuses unless decision is RELEASE
adapter skeleton remains fail-closed by default
```

This flow is not implemented in v1.7.0.

## What The Future Skeleton May Demonstrate

A future controlled adapter skeleton may be allowed to demonstrate:

* receiving a proposal envelope reference as inert data
* receiving a DHMS decision as inert data
* receiving a handoff contract reference as inert data
* validating that the decision is `RELEASE` before any conceptual acceptance
* refusing `HOLD`, `BLOCK`, `FAIL_CLOSED`, missing, invalid, stale, or
  unverifiable handoffs
* preserving evidence continuity markers
* preserving trace continuity markers
* returning no-execution outcomes for refused decisions
* proving that a skeleton boundary remains fail-closed by default

Any future demonstration must remain bounded by an explicit later phase. This
planning document does not authorize implementation.

## What The Future Skeleton Must Not Demonstrate

The future controlled adapter skeleton must not demonstrate:

* production adapter behavior
* runtime adapter implementation
* SDK integration
* MCP adapter behavior
* E2B adapter behavior
* Codex integration
* Claude integration
* OpenClaw integration
* DeepSeek integration
* provider SDK integration
* agent SDK integration
* command runner behavior
* tool executor behavior
* production runtime behavior
* broadening a DHMS `RELEASE` boundary
* converting a non-`RELEASE` decision into execution

## Fail-Closed Adapter Behavior

The controlled adapter skeleton must remain fail-closed by default.

Required invariants:

* The adapter skeleton must never convert a non-`RELEASE` decision into
  execution.
* The adapter skeleton must never broaden a `RELEASE` boundary.
* The adapter skeleton must never treat missing or invalid DHMS evidence as
  sufficient.

If the adapter boundary cannot verify the decision, handoff contract, evidence,
trace continuity, runtime target, allowed capability, or expiry rule, the
future skeleton must refuse.

## Adapter Boundary Inputs

These are prose-only future input concepts. v1.7.0 does not add schema files or
an adapter parser.

* proposal envelope reference: points to the observed proposal envelope
* DHMS decision: carries `RELEASE`, `HOLD`, `BLOCK`, or `FAIL_CLOSED`
* handoff contract reference: points to the planned DHMS handoff boundary
* decision boundary: defines the exact release boundary, if any
* allowed capability: identifies the narrow capability allowed only under
  `RELEASE`
* forbidden capabilities: identifies capabilities that must remain unavailable
* evidence reference: links to DHMS evidence expectations or evidence record
* trace reference: links to DHMS trace expectations or trace record
* runtime target: identifies the future runtime target named by the boundary
* expiry / revalidation rule: defines when the boundary becomes stale or must
  be rechecked

None of these inputs authorize execution by themselves.

## Adapter Boundary Outputs

These are prose-only future output concepts. v1.7.0 does not add an adapter
executor.

* accepted boundary acknowledgement: acknowledges a valid `RELEASE` boundary
  without broadening it
* refused boundary acknowledgement: records refusal for non-`RELEASE`, invalid,
  missing, stale, or unverifiable handoffs
* refusal reason: records why the boundary was refused
* evidence continuity marker: links refusal or acceptance to DHMS evidence
* trace continuity marker: links refusal or acceptance to DHMS trace
* no-execution result for `HOLD`, `BLOCK`, `FAIL_CLOSED`, invalid, missing, or
  stale handoff

Outputs must not claim production execution, runtime integration, SDK
integration, tool execution, command execution, or adapter implementation.

## Refusal Behavior

The future adapter skeleton must refuse and remain non-executing when:

* decision is `HOLD`
* decision is `BLOCK`
* decision is `FAIL_CLOSED`
* decision is missing
* handoff contract is incomplete
* handoff contract is stale or expired
* `proposal_id` mismatches
* `payload_hash` mismatches
* `evidence_reference` is missing
* `trace_reference` is missing
* runtime target mismatches
* requested capability exceeds allowed capability
* forbidden capability is requested
* boundary cannot be verified

No refusal case may be converted into execution.

## Future Validation Expectations

A future controlled adapter skeleton phase, if separately approved, should
validate:

* all non-`RELEASE` decisions remain non-executing
* missing, stale, invalid, or incomplete handoffs remain non-executing
* a `RELEASE` boundary is never broadened
* evidence references and trace references remain connected
* no SDKs, external runtimes, tools, commands, MCP, E2B, Codex, Claude,
  OpenClaw, DeepSeek, provider SDKs, or agent SDKs are invoked unless a future
  phase explicitly approves a narrower target

v1.7.0 does not implement these validations.

## Public Boundaries

The controlled adapter skeleton is not:

* a production adapter
* a runtime adapter implementation
* an SDK integration
* an MCP adapter
* an E2B adapter
* a Codex integration
* a Claude integration
* an OpenClaw integration
* a DeepSeek integration
* a provider SDK integration
* an agent SDK integration
* a command runner
* a tool executor
* a production runtime

## Public Non-Claims

DHMS v1.7.0 does not claim:

* production readiness
* real controlled adapter implementation
* real external runtime handoff
* real agent runtime integration
* real LLM execution
* E2B integration
* MCP integration
* Codex integration
* Claude integration
* OpenClaw integration
* DeepSeek integration
* provider SDK integration
* agent SDK integration
* runtime adapter implementation
* sandbox implementation
* policy engine replacement
* observability backend
* command execution
* arbitrary tool execution
* schema implementation
* adapter parser
* adapter executor
* production runtime behavior
* universal agent safety
* industry standard status

## Next Milestone

`v2.0.0 Real Agent Integration Preview Planning`

## Final Verdict

`READY_FOR_V2_0_0_REAL_AGENT_INTEGRATION_PREVIEW_PLANNING`
