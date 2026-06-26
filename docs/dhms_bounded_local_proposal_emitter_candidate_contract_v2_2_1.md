# DHMS Bounded Local Proposal Emitter Candidate Contract v2.2.1

## Metadata

* Milestone: `v2.2.1 Bounded Local Proposal Emitter Candidate Contract`
* Repository branch: `agent-harness-v1`
* Prior milestone: `v2.2.0 Bounded Local Proposal Emitter Candidate Planning`
* Next recommended milestone: `v2.2.2 Bounded Local Proposal Emitter Candidate Static Fixtures`

## Current Status

v2.2.1 is docs-only and prose-contract-only. It converts v2.2.0 planning into a
written contract for a future bounded local proposal emitter candidate. It does
not add machine schema, examples, fixtures, parser, runner, validator, CLI,
adapter, hook, execution path, or implementation approval.

## Scope

This contract defines how a future bounded local proposal emitter candidate may
describe inert proposal envelopes for later DHMS boundary evaluation. The
contract is local-only, dry-run-only, proposal-only, non-executing,
non-production, non-credentialed, non-user-data, and no-runtime.

## Non-Scope

v2.2.1 does not implement anything. It adds no code, schema, JSON examples,
fixtures, parser, runner, validator, CLI command, quickstart command, adapter,
hook, execution path, KerniQ integration, KerniQ invocation, KerniQ runtime
call, KerniQ command, E2B integration, E2B handoff, E2B sandbox, real-agent
integration, SDK/runtime integration, command execution, shell execution,
subprocess usage, file mutation, network access, credential handling, user data
handling, or production behavior.

## Relationship to v2.2.0

v2.2.0 planned a future bounded local proposal emitter candidate profile. It
was planning-only and docs-only. v2.2.1 preserves that boundary and turns the
planning language into a prose contract without adding machine-readable schema
or implementation artifacts.

## Contract Objective

The objective is to define the minimum contract for future inert proposal
envelopes that may be emitted locally for later DHMS boundary evaluation. The
candidate emitter can only describe proposed intent. It cannot execute,
authorize, dispatch, call, mutate, fetch, run, or hand off anything.

## Candidate Emitter Contract

A future bounded local proposal emitter candidate is an upstream metadata
producer only. It may produce proposal envelopes that describe requested
capability and declared side effects. It is not an executor, runtime, adapter,
agent hook, parser-triggered execution path, proof runner, capture runner,
execution runner, runtime runner, CLI command, SDK client, model caller,
credential handler, user-data processor, production connector, KerniQ
integration, or E2B integration.

## Candidate Proposal Envelope Contract

A candidate proposal envelope is inert metadata only. It is not a command,
script, runtime call, model call, SDK call, tool call, KerniQ payload, or E2B
handoff. It must be treated as non-executing until a separate future approved
boundary explicitly defines otherwise.

## Required Proposal Fields

Future candidate proposals must describe these fields in prose-contract terms:

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

## Field Semantics

`dry_run` must be true. The proposal is inert metadata only.
`requested_capability` must be declarative. `declared_side_effects` must be
explicit and declarative. `payload_ref` must be inert and must not be
dereferenced. `payload_hash` is required. `evidence_ref` and `trace_ref` are
metadata only. `credential_scope` must be empty for acceptable proposals.
`user_data_scope` must be empty for acceptable proposals. `runtime_target` must
be `none`, `inert`, or `no-runtime`.

`non_execution_assertions` must explicitly deny command, shell, file mutation,
network, SDK, model, runtime, adapter, KerniQ, E2B, credential, user-data, and
production access.

## Input Boundary

Input to any future candidate emitter must be local-only, synthetic or
explicitly non-sensitive, non-credentialed, non-user-data, non-production, and
non-executable. It must not be a shell command, script, real file mutation
request, real URL call, SDK/runtime handle, model invocation, agent invocation,
credential, user data, or production resource.

## Output Boundary

Output from any future candidate emitter must be inert proposal metadata only.
It must be dry-run-only, non-executing, declarative, bounded, hash-addressed or
hash-described, evidence-referenced, trace-referenced, and explicit about
requested capability, declared side effects, credential scope, user-data scope,
runtime target, and non-execution assertions.

## Dry-Run Boundary

`dry_run=true` is mandatory. `dry_run` does not authorize execution, side
effects, runtime release, command execution, shell execution, file mutation,
network access, SDK/model/runtime calls, KerniQ calls, or E2B handoff. It is an
inert declaration only.

## Payload Reference Boundary

`payload_ref` must be inert and must not be dereferenced. It must not be a real
file path, real URL, shell command, script, executable-looking reference, or
identifier for credentials, user data, production data, or production resources.
If a future contract includes executable-looking labels for negative testing,
those labels must be expected fail-closed cases.

## Hash / Evidence / Trace Boundary

`payload_hash` is required. Missing `payload_hash` fails closed in later
evaluation. `evidence_ref` and `trace_ref` are metadata references only and must
not be dereferenced as runtime inputs. Evidence and trace references do not
authorize execution.

## Credential and User-Data Boundary

`credential_scope` must be empty for acceptable proposals. `user_data_scope`
must be empty for acceptable proposals. Non-empty credential scope or user-data
scope fails closed unless explicitly synthetic and expected in a fail-closed
test case. No credentials, tokens, secrets, account data, customer data,
personal data, or production data may be accessed or embedded.

## Runtime Target Boundary

`runtime_target` must be `none`, `inert`, or `no-runtime`. A real runtime target
fails closed. KerniQ runtime target fails closed. E2B handoff target fails
closed. SDK runtime target, model runtime target, and production runtime target
fail closed.

## Non-Execution Assertion Boundary

Future proposal envelopes must explicitly assert no command execution, no shell
execution, no subprocess usage, no file mutation, no network access, no SDK
call, no model call, no runtime call, no adapter call, no KerniQ runtime call,
no E2B handoff, no credential access, no user-data access, and no production
resource access.

## DHMS Decision Interaction

The emitter candidate cannot decide `RELEASE`, `HOLD`, `BLOCK`, or
`FAIL_CLOSED`. It can only produce inert proposals for later DHMS evaluation.
DHMS decision semantics remain separate.

`RELEASE` does not execute anything in this contract. `RELEASE` does not
authorize runtime release, command execution, file mutation, network access,
SDK/model/runtime calls, KerniQ calls, or E2B handoff.

`HOLD`, `BLOCK`, and `FAIL_CLOSED` are non-executing. `HOLD`, `BLOCK`, and
`FAIL_CLOSED` must never be reinterpreted as `RELEASE`.

## Acceptance Rules

Later evaluation may accept a candidate proposal for further DHMS boundary
evaluation only if all required fields are present, `dry_run=true`, all scopes
and runtime targets remain inert, `payload_hash` is present, evidence and trace
metadata are present, and all non-execution assertions explicitly deny side
effects and runtime access.

Acceptance for evaluation is not execution approval.

## Rejection / Fail-Closed Rules

Later evaluation must fail closed on:

* missing required field
* malformed metadata
* stale metadata
* ambiguous boundary
* `dry_run` not true
* missing `payload_hash`
* missing `evidence_ref`
* missing `trace_ref`
* unsupported capability
* unknown side effects
* non-empty `credential_scope`
* non-empty `user_data_scope`
* real `runtime_target`
* KerniQ runtime target
* E2B handoff target
* SDK/model/runtime invocation marker
* real URL
* real file path
* command-looking text
* shell-looking text
* executable-looking `payload_ref`
* credential marker
* user-data marker
* production marker

## KerniQ Boundary

KerniQ is not integrated. KerniQ is not invoked. No KerniQ runtime call is
added. No KerniQ command is run. No KerniQ repository is inspected. No KerniQ
adapter, CLI, payload format, or dependency is added.

KerniQ remains deferred as a possible future local proposal emitter candidate
only. Future KerniQ work requires a separate milestone, prompt, allowed files,
review, and stricter approval.

## E2B Boundary

E2B is not integrated. E2B is not invoked. No E2B handoff is added. No E2B API
key is used. No E2B sandbox is created. No E2B command, filesystem, or network
access occurs.

Future E2B work requires separate handoff-boundary planning.

## Provider / Agent Boundary

There is no OpenClaw integration, Codex integration, Claude Code integration,
DeepSeek integration, provider SDK integration, or agent execution in v2.2.1.

## Later Fixture Milestone Boundary

The next recommended milestone is `v2.2.2 Bounded Local Proposal Emitter
Candidate Static Fixtures`.

v2.2.2 must be static-fixture-only. It must not add parser, runner, validator,
CLI, KerniQ integration, E2B integration, or execution behavior.

## Public Claims

v2.2.1 may claim only that DHMS has a prose-only contract for a future bounded
local proposal emitter candidate. The contract is for inert proposal metadata
only and preserves the v2.1 frozen non-execution boundaries.

## Public Non-Claims

v2.2.1 does not claim:

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

* docs-only milestone
* prose-contract-only milestone
* no implementation approval
* no code added
* no schema files added
* no JSON examples added
* no fixtures added
* no parser added
* no runner added
* no validator added
* no CLI command added
* no quickstart command added
* no adapter added
* no agent hook added
* no execution path added
* no KerniQ integration added
* no KerniQ invocation added
* no KerniQ runtime call added
* no E2B integration added
* no E2B handoff added
* no E2B sandbox added
* no real-agent integration added
* no SDK/runtime integration added
* no command execution added
* no shell execution added
* no subprocess usage added
* no file mutation added
* no network access added
* no credential handling added
* no user data handling added
* no production behavior added
* README not modified
* validator not modified
* fixture file not modified
* package index updated
* roadmap updated
* final verdict set correctly

## Final Verdict

`READY_FOR_V2_2_2_BOUNDED_LOCAL_PROPOSAL_EMITTER_CANDIDATE_STATIC_FIXTURES`
