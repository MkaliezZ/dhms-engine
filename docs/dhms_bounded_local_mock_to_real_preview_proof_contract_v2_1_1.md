# DHMS Bounded Local Mock-to-Real Preview Proof Contract v2.1.1

## 1. Title and Milestone Metadata

* Milestone: `v2.1.1 Bounded Local Mock-to-Real Preview Proof Contract`
* Branch: `agent-harness-v1`
* Current reviewed base: `v2.1.0 Bounded Local Mock-to-Real Preview Proof Planning`
* Future proof target: `local mock-to-real agent boundary`
* Next recommended milestone: `v2.1.2 Bounded Local Mock-to-Real Inert Proposal Fixtures`

DHMS / DHMS AgentFuse is an execution fuse protocol.

DHMS does not ask:

`Where can this action run safely?`

DHMS asks:

`Should this proposed action be released at all, under what boundary, and with what evidence?`

DHMS operates before execution. It is not a sandbox, not an MCP replacement,
not a runtime adapter, and not a production runtime.

## 2. Current Status

v2.1.0 planned the future bounded local mock-to-real preview proof boundary.
v2.1.1 defines the prose-only contract shape for future proof inputs,
decisions, evidence, and traces.

This milestone is planning/contract-only. It does not implement the proof,
does not authorize implementation, does not add runtime behavior, does not add
schema files, does not add parser code, and does not add validation runner code.

## 3. Scope

This document defines a future bounded local mock-to-real preview proof contract
in prose only.

The contract may describe:

* inert proposal envelope fields
* dry-run marker requirements
* target boundary fields
* requested capability declarations
* expected side-effect declarations
* payload reference requirements
* payload hash requirements
* credential scope requirements
* user data scope requirements
* runtime target requirements
* decision labels
* evidence fields
* trace fields
* acceptance rules
* rejection rules
* fail-closed rules
* non-execution confirmations

## 4. Non-Scope

v2.1.1 does not create:

* machine-enforced schema files
* parser code
* validation runner code
* proof runner code
* examples
* fixtures
* CLI commands
* runtime integration
* source code
* execution behavior

## 5. Relationship to v2.1.0

* v2.1.0 planned the future bounded local mock-to-real preview proof boundary.
* v2.1.0 did not authorize implementation.
* v2.1.1 defines a prose-only contract for future proof inputs, decisions, evidence, and traces.
* v2.1.1 does not add a schema file.
* v2.1.1 does not add parser code.
* v2.1.1 does not add runner code.
* v2.1.1 does not add examples or fixtures.
* v2.1.1 does not authorize implementation.

## 6. Contract Objective

The contract defines how a future local mock-to-real proposal should be
represented as inert data before any implementation begins.

The contract ensures:

* proposal material is inert
* dry-run marker is explicit
* target boundary is explicit
* requested capability is declarative only
* expected side effects are declarative only
* payload reference is inert
* payload hash is metadata only
* credential scope must be empty
* user data scope must be empty
* runtime target must be none / inert / no-runtime
* DHMS decision labels are preserved
* `HOLD`, `BLOCK`, and `FAIL_CLOSED` are non-executing
* `RELEASE` remains non-executing unless a later explicitly approved bounded proof implementation defines otherwise
* unknown, missing, malformed, stale, ambiguous, unsupported, executable-looking, credential-involving, user-data-involving, or production-resource-involving inputs fail closed

## 7. Inert Proposal Envelope Contract

A future inert proposal envelope may include these fields:

* `contract_version`
* `proposal_id`
* `source_profile`
* `target_boundary`
* `dry_run`
* `requested_capability`
* `expected_side_effects`
* `payload_ref`
* `payload_hash`
* `credential_scope`
* `user_data_scope`
* `runtime_target`
* `execution_allowed`
* `created_at`
* `expires_at`
* `evidence_ref`
* `trace_ref`

This document does not add a JSON schema file, validation code, or fixture
files. The envelope is a prose contract only.

## 8. Required Fields

Required field semantics:

* `contract_version`: identifies the future contract version.
* `proposal_id`: stable inert identifier.
* `source_profile`: identifies the local mock-to-real proposal source profile without implying integration.
* `target_boundary`: must match the selected local mock-to-real boundary.
* `dry_run`: must be true for future preview proof inputs.
* `requested_capability`: declarative only.
* `expected_side_effects`: declarative only.
* `payload_ref`: inert reference only, not dereferenced into real resources.
* `payload_hash`: metadata-only integrity reference.
* `credential_scope`: must be empty.
* `user_data_scope`: must be empty.
* `runtime_target`: must be none / inert / no-runtime.
* `execution_allowed`: must be false.
* `created_at` / `expires_at`: support stale-input fail-closed behavior.
* `evidence_ref` / `trace_ref`: inert references for evidence and trace continuity.

## 9. Forbidden Fields and Forbidden Behavior

The contract forbids any field or behavior that triggers:

* command execution
* shell execution
* subprocess execution
* file mutation
* network access
* SDK call
* model call
* runtime call
* adapter call
* MCP call
* E2B handoff
* OpenClaw call
* Codex call
* Claude Code call
* DeepSeek call
* credential access
* user data access
* production resource access
* parser-triggered execution
* runner-triggered execution
* CLI-triggered execution

## 10. Dry-Run Contract

`dry_run` must be explicitly true for future preview proof inputs. A missing,
false, ambiguous, stale, or malformed dry-run marker fails closed.

Dry-run status is declarative only. It must not cause execution, SDK calls,
model calls, adapter calls, network access, shell execution, command execution,
file mutation, credential access, or user data access.

## 11. Target Boundary Contract

`target_boundary` must match the selected local mock-to-real boundary.

The target boundary must remain local-only, mock-to-real shaped, inert,
non-credentialed, non-user-data, non-production, and no-runtime. Any external
agent process, real LLM, SDK, network, shell, command, file mutation, adapter
runtime, or production-resource target fails closed.

## 12. Capability Declaration Contract

`requested_capability` is declarative only. It may describe the capability the
future proof would evaluate, but it must not contain executable commands,
runtime invocation strings, SDK call instructions, network endpoints to call, or
file paths to mutate.

Unsupported, missing, ambiguous, malformed, or executable-looking capabilities
fail closed.

## 13. Side-Effect Declaration Contract

`expected_side_effects` is declarative only. It describes expected side-effect
classifications for decision evaluation, not actions to perform.

Missing, unsupported, ambiguous, malformed, executable-looking, credential-
involving, user-data-involving, or production-resource-involving side-effect
declarations fail closed.

## 14. Payload Reference and Hash Contract

`payload_ref` is an inert reference only. It must not be dereferenced into real
resources by this contract and must not point to credentials, user data,
production resources, executable scripts, shell commands, network endpoints to
call, or mutable files.

`payload_hash` is a metadata-only integrity reference. Missing or mismatched
hash metadata fails closed in future proof evaluation.

## 15. Credential and User Data Scope Contract

`credential_scope` must be empty.

`user_data_scope` must be empty.

Any non-empty credential scope, user data scope, secret reference, token
reference, customer-data reference, private account reference, or production-data
reference fails closed.

## 16. Runtime Target Contract

`runtime_target` must be none / inert / no-runtime.

Any runtime target that names or implies a real agent runtime, real LLM,
OpenClaw, Codex, Claude Code, DeepSeek, MCP, E2B, provider SDK, agent SDK,
KerniQ runtime, shell, command runner, adapter runtime, network endpoint,
filesystem mutation target, credential source, user-data source, or production
resource fails closed.

## 17. Decision Label Contract

The contract preserves exactly these decision labels:

* `RELEASE`
* `HOLD`
* `BLOCK`
* `FAIL_CLOSED`

Decision semantics:

* `RELEASE` is still non-executing unless a later explicitly approved bounded proof implementation defines otherwise.
* `HOLD` is non-executing.
* `BLOCK` is non-executing.
* `FAIL_CLOSED` is non-executing.
* `HOLD`, `BLOCK`, and `FAIL_CLOSED` must never be reinterpreted as `RELEASE`.
* Missing or unknown decision labels fail closed.

## 18. Acceptance Rules

The future proof input may be accepted for DHMS decision evaluation only if:

* `contract_version` is present
* `proposal_id` is present
* `source_profile` is present and local-only
* `target_boundary` matches selected local mock-to-real boundary
* `dry_run` is true
* `requested_capability` is declarative
* `expected_side_effects` are declarative
* `payload_ref` is inert
* `payload_hash` is present
* `credential_scope` is empty
* `user_data_scope` is empty
* `runtime_target` is none / inert / no-runtime
* `execution_allowed` is false
* `created_at` / `expires_at` are present and not stale
* `evidence_ref` is present
* `trace_ref` is present
* no executable trigger is present

Acceptance for decision evaluation does not authorize execution.

## 19. Rejection and Fail-Closed Rules

The future proof input must fail closed if:

* `contract_version` is missing or unsupported
* `proposal_id` is missing
* `source_profile` is missing or non-local
* `target_boundary` is missing or mismatched
* `dry_run` is missing or false
* `requested_capability` is missing, unsupported, or executable-looking
* `expected_side_effects` are missing, unsupported, or executable-looking
* `payload_ref` is missing, dereferenceable into real resources, or executable-looking
* `payload_hash` is missing or mismatched
* `credential_scope` is non-empty
* `user_data_scope` is non-empty
* `runtime_target` is not none / inert / no-runtime
* `execution_allowed` is not false
* `created_at` / `expires_at` are missing or stale
* `evidence_ref` is missing
* `trace_ref` is missing
* any command / shell / file / network / SDK / model / runtime / adapter / CLI / credential / user-data / production-resource trigger is present
* any field is ambiguous or malformed
* any decision label is missing or unknown

## 20. Evidence Contract

Evidence must be planned as metadata only and may include:

* contract version observed
* proposal id observed
* source profile classification
* target boundary match result
* dry-run validation result
* requested capability classification
* expected side-effect classification
* payload reference inertness result
* payload hash check result
* credential scope empty result
* user data scope empty result
* runtime target inertness result
* `execution_allowed` false result
* stale check result
* DHMS decision
* fail-closed reason when applicable
* no-execution confirmation
* evidence reference
* trace reference

Evidence must not include credentials, user data, production data, executable
payloads, runtime handles, SDK tokens, or network-access material.

## 21. Trace Contract

Trace must be planned as metadata only and may include:

* `proposal_received`
* `contract_checked`
* `target_boundary_checked`
* `dry_run_checked`
* `capability_classified`
* `side_effects_classified`
* `payload_ref_checked`
* `credential_scope_checked`
* `user_data_scope_checked`
* `runtime_target_checked`
* `stale_checked`
* `decision_assigned`
* `gate_state_recorded`
* `no_execution_confirmed`
* `fail_closed_reason_recorded`

Trace records must confirm non-execution and must not become a parser, runner,
adapter, hook, CLI command, runtime call, SDK call, model call, shell command,
network request, credential access, user data access, or production-resource
access path.

## 22. Later Fixture / Validation Planning Boundary

A later milestone may be:

`v2.1.2 Bounded Local Mock-to-Real Inert Proposal Fixtures`

v2.1.1 does not add examples, fixtures, validation runners, schema files,
parser code, CLI commands, runtime integration, or execution paths.

Any future fixture milestone must remain inert unless a separate explicit
milestone authorizes a narrower scope.

## 23. Later Implementation Approval Gate

v2.1.1 does not approve implementation.

Any later implementation would require a separate explicit milestone, separate
prompt, separate allowed files, separate review, and stricter approval.

This contract does not authorize any proof runner, parser, adapter, hook, CLI
command, SDK/runtime integration, KerniQ runtime call, E2B handoff, or execution
path.

## 24. Public Non-Claims

v2.1.1 does not claim:

* production readiness
* real agent integration
* real agent runtime interception
* real LLM execution
* local mock-to-real implementation
* KerniQ integration
* KerniQ runtime support
* KerniQ execution support
* OpenClaw integration
* Codex integration
* Claude integration
* Claude Code integration
* DeepSeek integration
* MCP integration
* E2B integration
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
* validation runner
* agent hook
* handoff parser
* adapter parser
* adapter executor
* runner implementation
* CLI command
* production runtime behavior
* credential handling
* user data handling
* universal agent safety
* industry standard status

## 25. Acceptance Checklist

* docs-only milestone
* planning/contract-only milestone
* prose-only contract
* no implementation approval
* no source code added
* no schema files added
* no parser added
* no runner added
* no validation runner added
* no adapter added
* no agent hook added
* no CLI command added
* no fixtures added
* no examples added
* no execution path added
* no shell or command execution added
* no file mutation added
* no network access added
* no SDK/model/runtime access added
* no credential handling added
* no user data handling added
* no production runtime claim added
* no real agent integration claim added
* no KerniQ integration claim added
* no E2B integration claim added
* README not modified because it is not actively misleading after v2.0.5.1
* package index updated
* roadmap updated
* final verdict set correctly

## 26. Final Verdict

`READY_FOR_V2_1_2_BOUNDED_LOCAL_MOCK_TO_REAL_INERT_PROPOSAL_FIXTURES`
