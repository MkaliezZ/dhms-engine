# DHMS Bounded Local Mock-to-Real Inert Proposal Fixtures v2.1.2

## 1. Title and Milestone Metadata

* Milestone: `v2.1.2 Bounded Local Mock-to-Real Inert Proposal Fixtures`
* Branch: `agent-harness-v1`
* Current reviewed base: `v2.1.1 Bounded Local Mock-to-Real Preview Proof Contract`
* Fixture file: `benchmarks/dhms_bounded_local_mock_to_real_v0/proposals.json`
* Next recommended milestone: `v2.1.3 Bounded Local Mock-to-Real Non-Executing Fixture Validation`

DHMS / DHMS AgentFuse is an execution fuse protocol.

DHMS does not ask:

`Where can this action run safely?`

DHMS asks:

`Should this proposed action be released at all, under what boundary, and with what evidence?`

DHMS operates before execution. It is not a sandbox, not an MCP replacement,
not a runtime adapter, and not a production runtime.

## 2. Current Status

v2.1.1 defined the prose-only bounded local mock-to-real proof contract.
v2.1.2 adds static inert proposal fixtures that follow that contract shape.

The fixtures are examples of inert data only. They are not executable inputs,
not runtime hooks, not real agent integration, and not proof execution.

## 3. Scope

This milestone adds:

* static fixture documentation
* a static JSON fixture file with exactly 8 inert proposal fixtures
* package index links
* roadmap status updates

The fixtures are static, synthetic, local-only, mock-to-real-shaped,
non-executing, non-credentialed, non-user-data, non-production, no-runtime,
no-network, no-shell, no-command, no-file-mutation, no-SDK, no-model-call,
no-adapter, no-KerniQ-runtime-call, and no-E2B-handoff.

## 4. Non-Scope

v2.1.2 does not add:

* schema files
* parser code
* validation runner code
* proof runner code
* runtime behavior
* implementation approval
* executable scripts
* generated outputs
* shell commands to run
* real file paths to mutate
* URLs to call
* credentials, tokens, secrets, account data, customer data, or production resource references

## 5. Relationship to v2.1.1

* v2.1.1 defined the prose-only bounded local mock-to-real proof contract.
* v2.1.1 did not add schema files, parsers, runners, examples, fixtures, CLI commands, runtime integration, or execution paths.
* v2.1.2 adds static inert fixtures only.
* v2.1.2 does not add schema files.
* v2.1.2 does not add parser code.
* v2.1.2 does not add validation runner code.
* v2.1.2 does not add proof runner code.
* v2.1.2 does not authorize implementation.

## 6. Fixture Objective

The objective is to provide a small inert data set that future validation work
can inspect without executing anything.

The fixtures cover one non-executing future `RELEASE` candidate, one `HOLD`
candidate, one `BLOCK` candidate, and five `FAIL_CLOSED` cases. `RELEASE` in
these fixtures means only `eligible_for_future_bounded_decision_evaluation`. It
does not mean execution approval, runtime release, command execution, file
mutation, network access, SDK call, model call, adapter call, KerniQ runtime
call, or E2B handoff.

## 7. Fixture File Location

Fixture file:

`benchmarks/dhms_bounded_local_mock_to_real_v0/proposals.json`

This file contains static JSON only.

## 8. Fixture Class List

The fixture file contains exactly these 8 inert proposal fixtures:

1. `valid_release_candidate_inert_read_only`
2. `valid_hold_candidate_needs_review`
3. `valid_block_candidate_unsupported_capability`
4. `valid_fail_closed_missing_payload_hash`
5. `valid_fail_closed_non_empty_credential_scope`
6. `valid_fail_closed_non_empty_user_data_scope`
7. `valid_fail_closed_runtime_target_not_none`
8. `valid_fail_closed_executable_looking_payload_ref`

## 9. Fixture Field Contract

Each fixture includes:

* `case_id`
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
* `expected_dhms_decision`
* `expected_gate_state`
* `expected_fail_closed_reason`
* `non_execution_assertions`
* `notes`

All fixture payload references are inert labels. They are not real file paths,
real URLs, shell commands, executable scripts, production resources, credential
references, or user data references.

## 10. Decision Coverage

Decision coverage:

* `RELEASE`: 1 static inert future decision-evaluation candidate
* `HOLD`: 1 static inert review candidate
* `BLOCK`: 1 static inert unsupported-capability candidate
* `FAIL_CLOSED`: 5 static inert fail-closed candidates

Every fixture has `execution_allowed=false`.

## 11. Fail-Closed Coverage

Fail-closed coverage includes:

* missing payload hash
* non-empty credential scope
* non-empty user data scope
* runtime target outside none / inert / no-runtime
* executable-looking payload reference

All fail-closed fixtures remain inert and non-executing.

## 12. Non-Execution Assertions

Every fixture includes `non_execution_assertions` confirming:

* no command execution
* no shell execution
* no file mutation
* no network access
* no SDK call
* no model call
* no runtime call
* no adapter call
* no KerniQ runtime call
* no E2B handoff
* no credential access
* no user data access
* no production resource access

## 13. KerniQ Boundary

KerniQ is not integrated in v2.1.2.

KerniQ is not invoked in v2.1.2. KerniQ is not treated as a runtime, executor,
adapter, hook, CLI, SDK, or source of live data in v2.1.2.

v2.1.2 fixtures may be KerniQ-shaped or KerniQ-compatible in the abstract only
if phrased as future, deferred, or candidate profile language. No KerniQ runtime
call is added.

## 14. E2B Boundary

E2B is not integrated in v2.1.2.

E2B is not invoked in v2.1.2. E2B is not used as a sandbox substrate in v2.1.2.
No E2B handoff, SDK call, API key, sandbox lifecycle, command execution,
filesystem access, or network access is added.

E2B remains deferred to a later handoff-boundary planning line, if ever
approved.

## 15. Later Validation Runner Boundary

A later milestone may be:

`v2.1.3 Bounded Local Mock-to-Real Non-Executing Fixture Validation`

v2.1.2 does not add validation runner code, parser code, schema files, CLI
commands, runtime integration, KerniQ calls, E2B handoff, or execution paths.

## 16. Later Implementation Approval Gate

v2.1.2 does not approve implementation.

Any later implementation would require a separate explicit milestone, separate
prompt, separate allowed files, separate review, and stricter approval.

This fixture milestone does not authorize proof runner behavior,
parser-triggered execution, adapter behavior, hooks, CLI commands, SDK/runtime
integration, KerniQ runtime calls, E2B handoff, command execution, file
mutation, network access, credential handling, user data handling, or production
behavior.

## 17. Public Non-Claims

v2.1.2 does not claim:

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

## 18. Acceptance Checklist

* docs + inert fixture milestone only
* static JSON fixtures only
* no implementation approval
* no source code added
* no schema files added
* no parser added
* no runner added
* no validation runner added
* no adapter added
* no agent hook added
* no CLI command added
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
* no KerniQ runtime call added
* no E2B integration claim added
* no E2B handoff added
* README not modified because it is not actively misleading after v2.0.5.1
* package index updated
* roadmap updated
* final verdict set correctly

## 19. Final Verdict

`READY_FOR_V2_1_3_BOUNDED_LOCAL_MOCK_TO_REAL_NON_EXECUTING_FIXTURE_VALIDATION`
