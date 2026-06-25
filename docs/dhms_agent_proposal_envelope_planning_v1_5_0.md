# DHMS Agent Proposal Envelope Planning v1.5.0

## Purpose

This document plans a future DHMS Agent Proposal Envelope in prose only. The
envelope describes what an agent would submit to DHMS before execution so DHMS
can evaluate whether the proposed action should be `RELEASE`, `HOLD`, `BLOCK`,
or `FAIL_CLOSED`.

v1.5.0 does not add implementation, schema files, SDK integration, runtime
integration, adapter code, runners, CLI commands, execution behavior, or
production runtime claims.

## v1.5.0 Claim

DHMS v1.5.0 plans a future agent proposal envelope for observable agent
actions before execution without adding schema files, runtime integration, SDK
integration, adapter implementation, execution behavior, or production runtime
claims.

## Current Context

The proposal envelope planning sits after the public DHMS evidence and boundary
lines:

* v1.0 public evidence package is released.
* v1.1 froze local command proposal interception.
* v1.2 froze runtime adapter boundary evidence.
* v1.3 released the runtime adapter boundary public evidence package.
* v1.4 clarified DHMS substrate/runtime boundaries.
* v1.5 now plans the proposal envelope that may later connect these proof
  lines to future agent/runtime handoff work.

The envelope is a future boundary object. It is not a schema, parser, SDK,
adapter, runtime hook, or execution API.

## Envelope Concept

An agent proposal envelope is the conceptual package of information DHMS would
observe before a proposed action crosses into execution. The envelope should be
complete enough for DHMS to classify the proposal, assign a decision, record
evidence requirements, and produce trace expectations.

The envelope must support exactly these DHMS decision outputs:

* `RELEASE`
* `HOLD`
* `BLOCK`
* `FAIL_CLOSED`

Invariant:

An envelope is not permission to execute. A proposal remains non-executing
unless DHMS returns `RELEASE` within a documented boundary.

## Conceptual Fields

These fields are prose planning fields only. v1.5.0 does not create a
machine-readable schema.

### `proposal_id`

What it means: A stable identifier for one proposed action.

Why DHMS needs it: DHMS needs a proposal-level key for decisions, evidence, and
trace correlation.

What it must not authorize: A proposal ID does not authorize execution or imply
that the proposal is valid.

### `agent_id`

What it means: The identifier of the agent or mock agent that emitted the
proposal.

Why DHMS needs it: DHMS needs to attribute proposals to their source for trace
and accountability boundaries.

What it must not authorize: An agent ID does not grant trust, execution rights,
or production access.

### `agent_runtime`

What it means: The runtime family or environment that produced the proposal.

Why DHMS needs it: DHMS needs runtime context to evaluate boundary assumptions
without letting the runtime own DHMS policy.

What it must not authorize: Naming a runtime does not create runtime
integration or allow the runtime to reinterpret DHMS decisions.

### `proposal_type`

What it means: The broad proposal class, such as SQL, File, HTTP, local
command, or runtime adapter proposal.

Why DHMS needs it: DHMS needs the proposal class to route risk classification
and evidence expectations.

What it must not authorize: A proposal type does not expand supported
capabilities or create a new execution path.

### `tool_family`

What it means: The tool or capability family the proposal belongs to.

Why DHMS needs it: DHMS needs to distinguish SQL, file, HTTP, command, adapter,
and future families for policy and trace mapping.

What it must not authorize: A tool family label is not permission to invoke a
tool.

### `intent`

What it means: A concise statement of what the agent claims it wants to do.

Why DHMS needs it: DHMS can compare stated intent with requested capability,
payload reference, and expected side effects.

What it must not authorize: Intent text is not trusted proof of safety.

### `requested_capability`

What it means: The capability requested by the proposal, such as read, write,
query, request, command, adapter call, or metadata access.

Why DHMS needs it: DHMS needs capability information to classify risk and
decide whether the proposal can be released, held, blocked, or failed closed.

What it must not authorize: A requested capability does not mean that
capability exists or is allowed.

### `operation_summary`

What it means: A normalized human-readable summary of the proposed operation.

Why DHMS needs it: DHMS needs a compact summary for review, trace, and
comparison across proposal families.

What it must not authorize: A summary does not replace policy evaluation or
evidence checks.

### `payload_reference`

What it means: A reference to the inert proposal payload, such as a manifest
case ID, static payload object, or bounded content reference.

Why DHMS needs it: DHMS needs to know which payload is being evaluated without
requiring uncontrolled payload execution.

What it must not authorize: A payload reference does not authorize reading,
opening, resolving, sending, executing, or invoking the payload.

### `payload_hash`

What it means: A planned integrity marker for the inert payload representation.

Why DHMS needs it: DHMS may need to detect payload drift between observation,
decision, and trace.

What it must not authorize: A hash does not prove payload safety or permit
execution.

### `risk_tier`

What it means: The planned DHMS risk tier or risk classification for the
proposal.

Why DHMS needs it: DHMS needs a risk tier to route proposals through fast,
constrained, hold, block, or fail-closed paths.

What it must not authorize: A lower risk tier does not bypass DHMS or create
automatic release.

### `decision_requested`

What it means: The decision the caller is asking DHMS to consider, such as
release or hold.

Why DHMS needs it: DHMS may use the requested decision as context when
validating whether the request is appropriate.

What it must not authorize: Requested decision is advisory input only. DHMS
assigns the actual decision.

### `evidence_required`

What it means: The evidence DHMS expects before a proposal can be treated as
complete for its decision boundary.

Why DHMS needs it: DHMS needs explicit evidence requirements to avoid silent
release or unclear proof claims.

What it must not authorize: Listing evidence requirements does not mean the
requirements have been satisfied.

### `trace_required`

What it means: The trace fields or trace events DHMS expects for the proposal.

Why DHMS needs it: DHMS needs trace expectations to preserve reviewability and
proof-line consistency.

What it must not authorize: Trace requirements do not replace enforcement or
permit execution.

### `expected_side_effects`

What it means: The claimed side-effect profile of the proposal.

Why DHMS needs it: DHMS needs to distinguish read-like, write-like, network,
command, adapter, credential, user-data, and production-risk effects.

What it must not authorize: A claim of no side effect does not prove the action
is safe.

### `credential_scope`

What it means: Whether credentials are requested, referenced, or expected to be
used.

Why DHMS needs it: DHMS needs to block or fail closed around credential access
unless a future explicit boundary authorizes otherwise.

What it must not authorize: Naming a credential scope does not authorize
credential access.

### `user_data_scope`

What it means: Whether user data, customer data, private data, or production
data is involved.

Why DHMS needs it: DHMS needs data-sensitivity context for risk classification
and non-claim preservation.

What it must not authorize: Declaring data scope does not authorize data
access, export, or processing.

### `runtime_target`

What it means: The runtime or target environment the proposal would eventually
reach if released.

Why DHMS needs it: DHMS needs the target to reason about handoff boundaries and
policy ownership.

What it must not authorize: A runtime target does not create runtime
integration or production runtime support.

### `sandbox_or_substrate_target`

What it means: The sandbox, substrate, or constrained environment the proposal
may request as a future release boundary.

Why DHMS needs it: DHMS needs to distinguish release target context from the
decision about whether release should occur at all.

What it must not authorize: Naming a sandbox or substrate does not implement
or invoke that substrate.

### `fallback_behavior`

What it means: The expected behavior when the envelope is incomplete,
unsupported, ambiguous, or rejected.

Why DHMS needs it: DHMS needs explicit fallback behavior to preserve
fail-closed defaults.

What it must not authorize: Fallback behavior cannot reinterpret `BLOCK` or
`FAIL_CLOSED` as release.

### `created_at`

What it means: A creation timestamp or deterministic creation marker for the
proposal envelope.

Why DHMS needs it: DHMS may need ordering, replay, and trace correlation.

What it must not authorize: A timestamp does not prove freshness, safety, or
permission to execute.

## Existing Evidence Line Mapping

### SQL Proposals

Representation: SQL proposals would use `proposal_type=SQL`, SQL-specific
payload references, and explicit capability fields such as read-like SELECT,
mutation, malformed SQL, or unsupported SQL.

Important fields: `requested_capability`, `payload_reference`, `risk_tier`,
`expected_side_effects`, `evidence_required`, and `trace_required`.

Current non-claims: no arbitrary SQL support, no direct SQL execution, no
mutation SQL execution, no production DB safety, no credentialed DB execution,
and no production SQL agent support.

Execution today: The only controlled SQL execution remains the historical
approved SQL Sandbox Execution Fuse proof path. The envelope does not add SQL
execution.

### File Proposals

Representation: File proposals would use `proposal_type=File`, inert path or
payload references, and capability fields such as read, write, append, delete,
list, metadata, or unsupported file operation.

Important fields: `requested_capability`, `payload_reference`,
`credential_scope`, `user_data_scope`, `risk_tier`,
`sandbox_or_substrate_target`, and `fallback_behavior`.

Current non-claims: no arbitrary file operation support, no production
file-system safety, no credential safety, no user data safety, and no file
adapter.

Execution today: File proof evidence is limited to the existing constrained
synthetic temp-directory proof line. The envelope does not add file operation
capability.

### HTTP Proposals

Representation: HTTP proposals would use `proposal_type=HTTP`, inert request
references, method/target summaries, and capability fields for local mock,
external network, credentialed request, hidden request, or unsupported request.

Important fields: `runtime_target`, `credential_scope`, `user_data_scope`,
`expected_side_effects`, `evidence_required`, and `trace_required`.

Current non-claims: no arbitrary HTTP support, no external network execution,
no HTTP adapter, no API client, no credentialed network request support, and no
production network safety claim.

Execution today: HTTP proof evidence is limited to static inert cases,
non-executing benchmark evidence, and the constrained local mock HTTP proof.
The envelope does not add HTTP execution.

### Mock-Agent SQL/File/HTTP Proposals

Representation: Mock-agent SQL/File/HTTP proposals would include
`agent_id`, `agent_runtime`, `proposal_type`, `proposal_id`, and a static
payload reference tied to existing mock-agent evidence.

Important fields: `agent_id`, `agent_runtime`, `proposal_type`,
`decision_requested`, `evidence_required`, and `trace_required`.

Current non-claims: no real agent runtime integration, no real LLM execution,
no Codex integration, no Claude integration, no OpenClaw integration, no
DeepSeek integration, no provider SDK integration, and no agent SDK
integration.

Execution today: The mock-agent line uses deterministic controlled proof
evidence over inert proposals. It does not prove real agent runtime
interception.

### Local Command Proposals

Representation: Local command proposals would use `proposal_type=LocalCommand`
or a future equivalent prose category, inert command references, argv/string
summaries, and explicit command-execution risk fields.

Important fields: `requested_capability`, `operation_summary`,
`expected_side_effects`, `risk_tier`, `fallback_behavior`, and
`trace_required`.

Current non-claims: no command execution, no shell execution, no subprocess
execution, no terminal integration, no command runner, and no production
runtime behavior.

Execution today: Local command evidence remains non-executing and frozen with
release count 0. The envelope does not add command execution.

### Runtime Adapter Proposals

Representation: Runtime adapter proposals would use a proposal type or tool
family that identifies adapter-boundary intent while keeping SDK/runtime calls
inert.

Important fields: `agent_runtime`, `tool_family`, `runtime_target`,
`requested_capability`, `credential_scope`, `user_data_scope`, and
`fallback_behavior`.

Current non-claims: no runtime adapter implementation, no SDK imports or SDK
calls, no MCP integration, no E2B integration, no Codex integration, no Claude
integration, no OpenClaw integration, no DeepSeek integration, no provider SDK
integration, no agent SDK integration, and no production runtime behavior.

Execution today: Runtime adapter boundary evidence remains inert and frozen.
The envelope does not add adapter behavior.

## Decision Model

The future envelope must support exactly these DHMS decision outputs:

* `RELEASE`
* `HOLD`
* `BLOCK`
* `FAIL_CLOSED`

`RELEASE` means DHMS has authorized release only within a documented boundary.
It does not mean arbitrary execution.

`HOLD` means DHMS has not released the proposal. The proposal remains
non-executing pending review, evidence, or a constrained proof path.

`BLOCK` means the proposal must not execute.

`FAIL_CLOSED` means the proposal is unsupported, malformed, ambiguous, or
otherwise not safe to release.

## Future Flow

Future DHMS work may define how an agent or runtime submits an envelope. v1.5.0
only describes the conceptual flow:

```text
agent emits proposal envelope
DHMS observes envelope
DHMS validates envelope completeness
DHMS assigns risk tier and decision
DHMS records evidence requirements and trace expectations
external runtime may only act according to DHMS decision boundary
```

This flow is not implemented in v1.5.0.

## Public Boundaries

v1.5.0 keeps the envelope as prose-only planning:

* no schema file
* no schema implementation
* no envelope parser
* no runner
* no CLI command
* no SDK integration
* no runtime integration
* no adapter implementation
* no execution behavior
* no production runtime behavior

## Public Non-Claims

DHMS v1.5.0 does not claim:

* production readiness
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
* envelope parser
* production runtime behavior
* universal agent safety
* industry standard status

## Validation Expectations

v1.5.0 should be validated as documentation-only:

* only allowed documentation files should change
* no source code should change
* no validation runner should change
* no benchmark manifest should change
* no example or trace artifact should change
* no schema file should be added
* no parser, runner, adapter, SDK integration, CLI command, or execution path
  should be added
* targeted scans should confirm that sensitive phrases appear only as explicit
  non-claims or planning boundaries

## Next Milestone

`v1.6.0 External Runtime Handoff Contract Planning`

## Final Verdict

`READY_FOR_V1_6_0_EXTERNAL_RUNTIME_HANDOFF_CONTRACT_PLANNING`
