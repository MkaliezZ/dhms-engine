# DHMS Bounded Local Proposal Emitter Candidate Planning v2.2.0

## Milestone Metadata

* Milestone: `v2.2.0 Bounded Local Proposal Emitter Candidate Planning`
* Repository branch: `agent-harness-v1`
* Prior milestone: `v2.1.4.1 README Current Status Sync`
* Next recommended milestone: `v2.2.1 Bounded Local Proposal Emitter Candidate Contract`

## Current Status

v2.2.0 is planning-only. It defines a future bounded local proposal emitter
candidate profile. It does not implement an emitter, define a machine schema,
add fixtures, add validation code, authorize implementation, integrate KerniQ,
integrate E2B, or integrate any real agent.

DHMS / DHMS AgentFuse is an execution fuse protocol. DHMS does not ask: where
can this action run safely? DHMS asks: should this proposed action be released
at all, under what boundary, and with what evidence?

DHMS operates before execution. It is not a sandbox, not an MCP replacement,
not a runtime adapter, and not a production runtime.

## Scope

This milestone documents a possible future local proposal emitter candidate as
local, bounded, emit-only, dry-run-only, proposal-only, non-executing,
no-runtime, no-command, no-shell, no-file-mutation, no-network, no-credential,
no-user-data, no-production, no-SDK-runtime-call, no-model-runtime-call,
no-agent-hook, no-adapter, and no-CLI command.

## Non-Scope

v2.2.0 does not add code, tests, fixtures, schemas, parser files, runner files,
validator files, CLI files, examples, quickstart commands, README changes,
KerniQ integration, KerniQ invocation, E2B handoff, E2B calls, real-agent
integration, runtime behavior, command execution, file mutation, network
access, credential handling, user data handling, or production behavior.

## Relationship to v2.1.4.1

v2.1.4.1 synchronized README Current Status only. It did not modify
Quickstart, validator, or fixtures. It did not authorize implementation and
left the next milestone as v2.2.0 planning-only.

## Relationship to v2.1.1-v2.1.4 Frozen Fixture Validation Chain

v2.1.1 defined the prose-only bounded local mock-to-real proof contract.
v2.1.2 added exactly 8 static inert proposal fixtures. v2.1.3 added
deterministic non-executing fixture validation. v2.1.4 reviewed and froze the
result.

That frozen line remains static-fixture-based and non-executing. v2.2.0 must
not reinterpret the v2.1 frozen fixtures as executable inputs, must not expand
`RELEASE` into runtime authorization, and must not weaken `HOLD`, `BLOCK`, or
`FAIL_CLOSED` semantics.

## Planning Objective

The objective is to plan a future local proposal emitter candidate that may
emit inert proposal envelopes for later DHMS boundary evaluation. It must not
execute tasks, call tools, call shells, mutate files, call network, call SDKs,
call models, invoke agents, invoke KerniQ, invoke E2B, access credentials,
access user data, or touch production systems.

## Candidate Emitter Definition

If separately approved later, a future bounded local proposal emitter candidate
could produce a proposal object containing:

* `proposal_id`
* `emitter_profile`
* `target_boundary`
* `dry_run`
* `requested_capability`
* `declared_side_effects`
* `payload_ref`
* `payload_hash`
* `credential_scope`
* `user_data_scope`
* `runtime_target`
* `created_at`
* `expires_at`
* `evidence_ref`
* `trace_ref`
* `non_execution_assertions`

This is planning text only. v2.2.0 does not add schema, JSON examples, fixture
files, parser code, runner code, or CLI commands.

## Candidate Emitter Non-Definition

The candidate emitter is not:

* a command runner
* a shell runner
* a file mutation tool
* a network tool
* a runtime adapter
* an agent adapter
* an agent hook
* a model caller
* an SDK client
* a credential handler
* a user-data processor
* a production connector
* a sandbox
* an MCP replacement
* a proof runner
* a capture runner
* an execution runner
* a runtime runner
* a CLI command
* KerniQ integration
* E2B integration

## Candidate Input Boundary

Any future candidate input must be local-only, synthetic or explicitly
non-sensitive, non-credentialed, non-user-data, non-production, non-executable,
not a shell command, not a script, not a real file mutation request, not a real
URL call, not an SDK/runtime handle, not a model invocation, and not an agent
invocation.

## Candidate Output Boundary

Any future candidate output must be inert proposal metadata only, dry-run-only,
non-executing, declarative, bounded, hash-addressed or hash-described,
evidence-referenced, trace-referenced, explicit about requested capability,
explicit about expected side effects, explicit about `credential_scope`,
explicit about `user_data_scope`, explicit about `runtime_target`, and explicit
about `non_execution_assertions`.

## Inert Proposal Envelope Boundary

The proposal envelope is not a command, script, runtime call, model call, SDK
call, tool call, KerniQ payload, or E2B handoff. The proposal envelope must be
treated as inert metadata until a separate future approved boundary says
otherwise.

## Dry-Run-Only Boundary

`dry_run` must be true for any candidate proposal in this planning line.
`dry_run` does not authorize execution, side effects, file mutation, network
access, or SDK/model/runtime calls. It is an inert declaration only.

## Local-Only Boundary

Local-only does not mean trusted, execution allowed, or safe to run. Local-only
does not authorize shell, command, file, network, credential, user-data, or
production access. Local-only only limits the planning scope.

## Capability Declaration Boundary

`requested_capability` must be declarative. It must not be executable, contain
command text, contain script text, or contain real URLs, credentials, user data,
or production identifiers. Unsupported or ambiguous capability declarations fail
closed in later evaluation.

## Side-Effect Declaration Boundary

`declared_side_effects` must be explicit and declarative. Unknown side effects,
command execution side effects, file mutation side effects, network side
effects, credential access side effects, user data side effects, and production
side effects fail closed.

## Payload Reference Boundary

`payload_ref` must be an inert reference. It must not be dereferenced by the
emitter planning line, must not be a real file path, must not be a real URL,
must not be a shell command, must not be executable-looking unless a future
contract explicitly treats it as fail-closed, and must not identify
credentials, user data, or production resources.

## Hash and Evidence Expectation Boundary

`payload_hash` is expected for future candidate proposals. Missing
`payload_hash` should fail closed in later evaluation. `evidence_ref` and
`trace_ref` are metadata references only and must not be dereferenced as
runtime inputs. Evidence and trace references do not authorize execution.

## Credential and User-Data Boundary

`credential_scope` must be empty for accepted candidate proposals.
`user_data_scope` must be empty for accepted candidate proposals. Non-empty
credential scope or non-empty user-data scope should fail closed unless
explicitly synthetic and expected in a fail-closed test case. No credentials,
tokens, secrets, account data, customer data, personal data, or production data
may be accessed or embedded.

## Runtime Target Boundary

`runtime_target` must be `none`, `inert`, or `no-runtime` for accepted
candidate proposals. Any real runtime target fails closed. KerniQ runtime
target fails closed in this planning line. E2B runtime target fails closed in
this planning line. SDK runtime target, model runtime target, and production
runtime target fail closed.

## Decision Interaction Boundary

The emitter candidate may only produce proposals for DHMS boundary evaluation.
The emitter candidate cannot decide `RELEASE`, `HOLD`, `BLOCK`, or
`FAIL_CLOSED` by itself. DHMS decision semantics remain separate.

`RELEASE` remains non-executing unless a future separately approved bounded
implementation explicitly defines otherwise. `HOLD`, `BLOCK`, and
`FAIL_CLOSED` remain non-executing and must never be reinterpreted as
`RELEASE`.

## Fail-Closed Expectation Boundary

Later evaluation should fail closed on missing `proposal_id`, missing
`emitter_profile`, missing `target_boundary`, `dry_run` not true,
`execution_allowed` not false if present, missing `payload_hash`, missing
`evidence_ref`, missing `trace_ref`, unsupported capability, unknown side
effects, non-empty credential scope, non-empty user data scope, non-inert
runtime target, executable-looking payload reference, real URL, real file path,
command-looking text, shell-looking text, SDK/model/runtime invocation-looking
text, KerniQ runtime target, E2B handoff target, production marker, malformed
metadata, stale metadata, or ambiguous boundary.

## KerniQ Boundary

KerniQ is not integrated in v2.2.0. KerniQ is not invoked in v2.2.0. No KerniQ
runtime call is added. No KerniQ command is run. No KerniQ repository is
inspected. No KerniQ adapter is added. No KerniQ CLI is added. No KerniQ
payload format is implemented.

KerniQ may be discussed only as a deferred possible future local proposal
emitter candidate concept. v2.2.0 does not authorize future KerniQ integration.
Any later KerniQ-related milestone would require a separate explicit prompt,
separate allowed files, separate review, and stricter approval.

## E2B Boundary

E2B is not integrated in v2.2.0. E2B is not invoked in v2.2.0. No E2B handoff
is added. No E2B API key is used. No E2B sandbox is created. No E2B command
execution is performed. No E2B filesystem or network access is performed.

E2B remains deferred to a later handoff-boundary planning line, if ever
approved. v2.2.0 does not authorize future E2B integration.

## OpenClaw / Codex / Claude Code / DeepSeek Boundary

v2.2.0 does not integrate OpenClaw, Codex, Claude Code, or DeepSeek. Those
systems are not used as runtime emitters in this milestone. No agent execution
or provider integration is added.

## Implementation Deferral

v2.2.0 is not implementation approval. It does not approve source code, schema
files, fixtures, a parser, a runner, a CLI command, or any
agent/runtime/SDK integration. Any later implementation requires a separate
milestone and review.

## Later Contract Milestone Boundary

The next recommended milestone is `v2.2.1 Bounded Local Proposal Emitter
Candidate Contract`.

If approved later, v2.2.1 should be prose-contract-only. It may define the
candidate proposal envelope contract in prose. It must not add schema files,
examples, fixtures, parser code, runner code, CLI commands, KerniQ integration,
E2B integration, or execution authorization.

## Public Claim Boundary

v2.2.0 may claim only that DHMS has begun planning a bounded local proposal
emitter candidate profile, that the planning is for future inert proposal
emission only, that it preserves the v2.1 frozen non-execution boundaries, and
that it is local-only, bounded, dry-run-only, proposal-only, non-executing,
non-production, non-credentialed, non-user-data, and no-runtime.

It does not claim implemented emitter, working local emitter, real-agent
integration, KerniQ integration, E2B integration, runtime interception, real LLM
execution, production safety, sandbox safety, tool execution safety,
file/network/command execution safety, or implementation readiness.

## Public Non-Claims

v2.2.0 does not claim:

* production readiness
* real agent integration
* real agent runtime interception
* real LLM execution
* local proposal emitter implementation
* local mock-to-real implementation
* KerniQ integration
* KerniQ runtime support
* KerniQ execution support
* KerniQ runtime call
* OpenClaw integration
* Codex integration
* Claude integration
* Claude Code integration
* DeepSeek integration
* MCP integration
* E2B integration
* E2B handoff
* provider SDK integration
* agent SDK integration
* runtime adapter implementation
* controlled adapter implementation
* sandbox implementation
* shell execution
* command execution
* file mutation support
* network execution support
* arbitrary tool execution
* schema implementation
* proposal parser
* dry-run parser
* capture parser
* capture runner
* proof runner
* agent hook
* handoff parser
* adapter parser
* adapter executor
* execution runner
* runtime runner
* CLI command
* production runtime behavior
* credential handling
* user data handling
* universal agent safety
* industry standard status

## Acceptance Checklist

* planning-only milestone
* docs-only milestone
* no implementation approval
* no code added
* no schema files added
* no fixtures added
* no examples added
* no validator added
* no parser added
* no proof runner added
* no capture runner added
* no execution runner added
* no runtime runner added
* no source package code added
* no adapter added
* no agent hook added
* no CLI command added
* no quickstart command added
* no execution path added
* no shell or command execution added
* no subprocess usage added
* no file mutation added
* no network access added
* no SDK/model/runtime access added
* no credential handling added
* no user data handling added
* no production runtime claim added
* no real agent integration claim added
* no KerniQ integration claim added
* no KerniQ runtime call added
* no E2B integration claim added
* no E2B handoff added
* README not modified
* validator not modified
* fixture file not modified
* package index updated
* roadmap updated
* final verdict set correctly

## Final Verdict

`READY_FOR_V2_2_1_BOUNDED_LOCAL_PROPOSAL_EMITTER_CANDIDATE_CONTRACT`
