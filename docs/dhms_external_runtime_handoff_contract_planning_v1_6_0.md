# DHMS External Runtime Handoff Contract Planning v1.6.0

## Purpose

This document plans a future DHMS External Runtime Handoff Contract in prose
only. The contract describes how a future external runtime or substrate should
consume a DHMS decision without bypassing or weakening the DHMS execution fuse
boundary.

v1.6.0 does not add implementation, schema files, SDK integration, runtime
integration, adapter code, runners, CLI commands, execution behavior, or
production runtime claims.

## v1.6.0 Claim

DHMS v1.6.0 plans a future external runtime handoff contract for transferring
DHMS decisions to external runtimes or substrates without adding
implementation, schema files, runtime integration, SDK integration, adapter
code, execution behavior, or production runtime claims.

## Current Context

v1.6.0 follows the post-v1.3 planning line:

* v1.4 clarified DHMS substrate/runtime boundaries.
* v1.5 planned the Agent Proposal Envelope.
* v1.6 now plans how a future DHMS decision may be handed off to an external
  runtime.

This remains planning-only. It does not create an external runtime handoff,
runtime adapter, SDK integration, handoff parser, handoff executor, or
execution path.

## Core Rule

External runtimes must treat DHMS decisions as boundary decisions, not
advisory logs.

If DHMS says `HOLD`, `BLOCK`, or `FAIL_CLOSED`, the external runtime must not
execute. If the DHMS decision is missing, incomplete, expired, stale,
ambiguous, or mismatched, the external runtime must fail closed rather than
treating the proposal as released.

## Decision Outputs

The future handoff contract must support exactly these DHMS decision outputs:

* `RELEASE`
* `HOLD`
* `BLOCK`
* `FAIL_CLOSED`

## Decision Semantics

`RELEASE`: external runtime may proceed only within the exact documented DHMS
boundary.

`HOLD`: external runtime must not execute; the proposal requires more
evidence, review, or constrained proof.

`BLOCK`: external runtime must not execute.

`FAIL_CLOSED`: external runtime must not execute; the proposal is unsupported,
malformed, ambiguous, incomplete, or unsafe.

## Handoff Invariant

An external runtime must never reinterpret:

* `HOLD` as `RELEASE`
* `BLOCK` as `RELEASE`
* `FAIL_CLOSED` as `RELEASE`
* missing decision as `RELEASE`
* incomplete handoff as `RELEASE`
* stale evidence as `RELEASE`

The handoff contract preserves the DHMS boundary. It does not delegate DHMS
policy ownership to the external runtime.

## Handoff Concept

These fields are prose planning fields only. v1.6.0 does not create a
machine-readable schema.

### `handoff_id`

What it means: A stable identifier for one future handoff record from DHMS to
an external runtime.

Why DHMS needs it: DHMS needs to correlate the decision, evidence, trace, and
runtime acknowledgement for a single handoff event.

What it must not authorize: A handoff ID does not authorize execution or prove
that a runtime may proceed.

### `proposal_id`

What it means: The proposal identifier from the agent proposal envelope that
the handoff refers to.

Why DHMS needs it: DHMS needs to bind the handoff to the exact observed
proposal.

What it must not authorize: A matching proposal ID does not authorize release
unless the DHMS decision is `RELEASE` and all boundaries match.

### `decision_id`

What it means: The identifier of the DHMS decision assigned to the proposal.

Why DHMS needs it: DHMS needs a decision-level key for auditability and
handoff verification.

What it must not authorize: A decision ID alone is not permission to execute.

### `dhms_decision`

What it means: The DHMS decision output: `RELEASE`, `HOLD`, `BLOCK`, or
`FAIL_CLOSED`.

Why DHMS needs it: The external runtime must know the exact boundary decision.

What it must not authorize: Any value other than `RELEASE` must not authorize
execution. Unknown or missing values fail closed.

### `decision_boundary`

What it means: The exact boundary under which the decision applies, including
scope, limits, and proof-line assumptions.

Why DHMS needs it: DHMS needs to prevent a narrow release from being broadened
into arbitrary runtime behavior.

What it must not authorize: A decision boundary must not be widened by the
external runtime.

### `allowed_runtime_target`

What it means: The runtime or substrate target that a `RELEASE` decision may
apply to.

Why DHMS needs it: DHMS needs to bind a release to a specific target rather
than allowing target substitution.

What it must not authorize: Naming a target does not create integration with
that target or authorize other targets.

### `allowed_capability`

What it means: The narrow capability that may be used if the decision is
`RELEASE`.

Why DHMS needs it: DHMS needs to limit the handoff to the approved capability.

What it must not authorize: The allowed capability must not expand into
adjacent tool, network, file, command, SDK, or adapter behavior.

### `forbidden_capabilities`

What it means: Explicit capabilities that must remain unavailable for this
handoff.

Why DHMS needs it: DHMS needs negative constraints so that the runtime cannot
fill gaps with broader behavior.

What it must not authorize: Listing forbidden capabilities does not imply that
unlisted capabilities are allowed.

### `evidence_reference`

What it means: A reference to DHMS evidence that supports the decision.

Why DHMS needs it: DHMS needs the external runtime and later reviewers to know
which evidence record the decision depends on.

What it must not authorize: An evidence reference does not prove that evidence
is valid, fresh, complete, or sufficient unless DHMS has already accepted it.

### `trace_reference`

What it means: A reference to the trace expectations or trace record attached
to the handoff.

Why DHMS needs it: DHMS needs trace continuity from proposal observation to
decision transfer.

What it must not authorize: Trace reference does not authorize execution.

### `payload_hash`

What it means: A hash or integrity marker for the proposal payload that the
handoff decision covers.

Why DHMS needs it: DHMS needs to detect payload mismatch, substitution, or
drift.

What it must not authorize: A hash match does not authorize execution unless
the decision is `RELEASE` and all boundaries match.

### `decision_timestamp`

What it means: The time or deterministic marker when DHMS assigned the
decision.

Why DHMS needs it: DHMS needs a basis for expiry, replay prevention, and trace
ordering.

What it must not authorize: A timestamp does not prove freshness by itself.

### `expiry_or_revalidation_rule`

What it means: The rule that determines when the handoff decision expires or
must be revalidated.

Why DHMS needs it: DHMS needs to prevent stale decisions from being reused as
release authority.

What it must not authorize: An expired or unverifiable decision must not be
treated as release.

### `fallback_behavior`

What it means: The required behavior when the handoff is missing, incomplete,
unknown, stale, mismatched, or unverifiable.

Why DHMS needs it: DHMS needs the external runtime to preserve fail-closed
semantics.

What it must not authorize: Fallback behavior must not reinterpret any failure
case as release.

### `runtime_acknowledgement`

What it means: A future runtime acknowledgement that it received and accepted
the handoff boundary.

Why DHMS needs it: DHMS needs to know whether the runtime acknowledged the
decision boundary before acting.

What it must not authorize: Acknowledgement is not permission to exceed the
DHMS decision boundary.

### `runtime_refusal_reason`

What it means: The reason an external runtime refuses to act on a handoff.

Why DHMS needs it: DHMS needs refusal reasons to preserve traceability when the
runtime fails closed.

What it must not authorize: Refusal reason must not trigger alternative
execution outside DHMS.

## Future Flow

Future DHMS work may define how this handoff is represented. v1.6.0 only
describes the conceptual flow:

```text
agent emits proposal envelope
DHMS observes proposal envelope
DHMS assigns RELEASE / HOLD / BLOCK / FAIL_CLOSED
DHMS records evidence and trace expectations
DHMS emits future handoff contract
external runtime validates contract completeness
external runtime acts only if decision is RELEASE and boundary matches
external runtime refuses HOLD / BLOCK / FAIL_CLOSED / missing / stale / incomplete decisions
```

This flow is not implemented in v1.6.0.

## Failure Handling

A future external runtime handoff must fail closed for these cases:

* missing decision: no `RELEASE` exists, so no execution may occur
* unknown decision: decision is outside `RELEASE`, `HOLD`, `BLOCK`, and
  `FAIL_CLOSED`
* expired decision: the decision must be revalidated before any release
* mismatched `proposal_id`: handoff does not bind to the observed proposal
* mismatched `payload_hash`: payload may have drifted or been substituted
* missing `evidence_reference`: evidence boundary is incomplete
* missing `trace_reference`: trace boundary is incomplete
* runtime target mismatch: release does not apply to this runtime target
* requested capability outside allowed boundary: release is too narrow for the
  requested action
* external runtime cannot verify contract completeness: runtime must refuse
  rather than execute

None of these failure modes may be converted into `RELEASE`.

## Comparison With Adjacent Layers

### Sandbox Execution

Sandbox execution asks where code or a tool can run with isolation. DHMS
handoff planning asks whether the proposal may be released to a boundary at
all. v1.6.0 adds no sandbox implementation.

### E2B-Style Substrate Execution

E2B-style substrates provide hosted execution environments. DHMS handoff
planning describes how a DHMS decision should constrain a future substrate
handoff. v1.6.0 adds no E2B integration.

### MCP Tool Invocation

MCP-style systems connect agents to tools and resources. DHMS handoff planning
describes a decision boundary that a tool invocation must not bypass. v1.6.0
adds no MCP integration.

### Agent SDK Orchestration

Agent SDKs orchestrate agents, tools, memory, and workflows. DHMS handoff
planning keeps DHMS policy ownership separate from SDK orchestration. v1.6.0
adds no agent SDK integration.

### Observability Logging

Observability logging records behavior. DHMS handoff planning defines a
decision boundary and evidence expectations before or around execution. The
handoff is not advisory logging. v1.6.0 adds no observability backend.

### Human Approval Workflow

Human approval can be one review path for held actions. DHMS handoff planning
requires the external runtime to respect DHMS decisions whether or not a human
approval workflow exists. v1.6.0 adds no approval workflow implementation.

## Public Boundaries

v1.6.0 keeps the handoff contract as prose-only planning:

* no schema file
* no schema implementation
* no handoff parser
* no handoff executor
* no runner
* no CLI command
* no SDK integration
* no runtime integration
* no adapter implementation
* no execution behavior
* no production runtime behavior

## Public Non-Claims

DHMS v1.6.0 does not claim:

* production readiness
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
* handoff parser
* handoff executor
* production runtime behavior
* universal agent safety
* industry standard status

## Validation Expectations

v1.6.0 should be validated as documentation-only:

* only allowed documentation files should change
* no source code should change
* no validation runner should change
* no benchmark manifest should change
* no example or trace artifact should change
* no schema file should be added
* no handoff parser or executor should be added
* no SDK, adapter, runner, CLI command, or execution path should be added
* targeted scans should confirm that sensitive phrases appear only as explicit
  non-claims or planning boundaries

## Next Milestone

`v1.7.0 Controlled Adapter Skeleton Planning`

## Final Verdict

`READY_FOR_V1_7_0_CONTROLLED_ADAPTER_SKELETON_PLANNING`
