# DHMS Controlled Agent Proposal Gate Contract v2.8.1

## Title and metadata

Milestone: `v2.8.1 Controlled Agent Proposal Gate Contract + README Non-Claims Compression`

Status: `contract-only plus README non-claims compression`

Previous milestone: `v2.8.0 Controlled Agent Proposal Gate Planning`

Next milestone: `v2.8.2 Controlled Agent Proposal Static Fixtures`

Reasoning level: `Super High`

## Purpose

v2.8.1 defines the prose-only Controlled Agent Proposal Gate Contract for the
next DHMS line. The contract describes what a future controlled agent proposal
must look like before DHMS may evaluate it.

This milestone also compresses the README public non-claims into a shorter
public boundary section. The compression is presentation-only and does not
weaken the detailed safety boundaries.

## Current status

The current implemented and frozen proof remains the v2.7 bounded claim:

DHMS has a repository-local, stdlib-only Minimal Pre-Execution Fuse Loop proof
showing that one inert LangChain-SQL-agent-like DROP TABLE proposal is observed
before execution, fail-closed by the DHMS gate before executor handoff, not
received by the inert mock executor, and recorded with zero SQL execution
attempts, zero DB connections, zero schema introspection, and zero result
readbacks.

v2.8.1 does not change that proof.

## Relationship to v2.8.0

v2.8.0 opened the Controlled Agent Proposal Gate planning line. v2.8.1 turns
that planning direction into a prose-only contract.

v2.8.1 does not add fixtures, schemas, validators, runners, CLI commands,
source code, proof behavior, screenshots, or execution behavior.

## Relationship to v2.7 frozen proof

v2.8.1 builds on the frozen v2.7 proof but does not reinterpret, weaken, or
expand it.

The v2.7 proof remains limited to one inert dangerous proposal:

```text
proposal_id=langchain_sql_drop_table_attempt_001
agent_family=langchain_sql_agent_like
proposed_tool=sql_db_query
proposed_action=DROP TABLE customers
```

The frozen v2.7 counters remain:

* `sql_execution_attempts=0`
* `db_connections=0`
* `schema_introspection=0`
* `result_readbacks=0`
* `mock_executor_received=false`
* `mock_executor_invocations=0`

## README non-claims compression note

The README now uses a shorter `Public Boundary` section. That section points
to the full detailed boundaries in:

* v2.7.4 Result Review and Freeze
* v2.7.4.2 README Public Landing Page Polish
* this v2.8.1 contract

This is only a readability change. It does not remove, weaken, or reverse any
non-claim.

## Contract scope

This contract applies only to future repository-local, inert, controlled
proposal fixtures and future non-executing validation.

It does not apply to:

* real agents
* model-connected agents
* LangChain runtimes
* SQL agents
* SQLDatabaseToolkit
* databases
* external runtimes
* model-provider APIs
* KerniQ
* E2B
* production systems

## Controlled agent definition

A controlled agent is a bounded proposal source for future DHMS fixtures. It
must be:

* repository-local
* bounded
* inert
* deterministic or statically described
* a proposal source only
* unable to execute tools, commands, or SQL
* unable to connect to databases
* unable to introspect schemas
* unable to read database results
* unable to call model APIs
* unable to perform network calls
* unable to invoke subprocesses or shells
* unable to access credentials
* unable to access user data
* unable to mutate files
* unable to hand off to real executors

## Controlled agent non-definition

A controlled agent is not:

* a real autonomous agent
* a model-connected agent
* a LangChain agent
* a SQL Agent
* a SQLDatabaseToolkit wrapper
* a database client
* a CLI runtime
* a parser runtime
* a hook runtime
* a KerniQ runtime
* an E2B runtime
* an external runtime
* a production runtime
* a credential-bearing actor
* a user-data-bearing actor

## Controlled proposal definition

A controlled proposal is an inert envelope describing a proposed action before
execution. It exists only as data for DHMS evaluation.

A controlled proposal is not:

* executable authorization
* a tool call to run
* a command to execute
* SQL to execute
* a database operation
* a model API call
* a network request
* a file mutation

## Proposal envelope contract

The proposal envelope contract is prose-only in v2.8.1. No schema file is
added. Future fixtures may use this contract as a writing guide only after a
separate milestone explicitly authorizes them.

## Required envelope fields

Future controlled proposal envelopes should include:

* `proposal_id`
* `agent_family`
* `controlled_agent_profile`
* `proposed_tool`
* `proposed_action`
* `tool_input_summary`
* `declared_boundary`
* `observed_before_execution`
* `expected_dhms_decision`
* `expected_executor_handoff_allowed`
* `expected_execution_authorized`
* `expected_mock_executor_received`
* `expected_mock_executor_invocations`
* `expected_sql_execution_attempts`
* `expected_db_connections`
* `expected_schema_introspection`
* `expected_result_readbacks`
* `expected_model_api_calls`
* `expected_network_calls`
* `expected_subprocess_calls`
* `expected_credential_accesses`
* `expected_user_data_accesses`
* `expected_file_mutation_attempts`
* `expected_executor_handoffs`

When the expected decision is `FAIL_CLOSED`, the envelope must also include:

* `expected_fail_closed_reason`

When the expected decision is `HOLD_FOR_REVIEW`, the envelope must also
include:

* `expected_hold_reason`

## Optional future envelope fields

Future prose or fixture work may consider:

* `evidence_id`
* `risk_family`
* `risk_tier`
* `source_fixture_family`
* `proposal_created_at_static`
* `notes`
* `non_execution_assertions`
* `public_claim_boundary`

These are optional future fields only. v2.8.1 does not add a schema.

## Forbidden envelope behavior

A proposal envelope must not contain:

* executable code
* secrets
* credentials
* real user data
* live URLs intended for calling
* shell commands intended for execution
* SQL intended for execution
* database connection strings
* API keys
* tokens
* runtime handles

## Gate input boundary

The DHMS gate must receive the proposal before execution. Post-hoc traces are
not sufficient evidence for this contract.

A future validator should reject any fixture that cannot assert:

```text
observed_before_execution=true
```

## Gate decision contract

Future controlled proposal gate decisions should remain explicit and bounded.
The planned decision classes are:

* `RELEASE_CANDIDATE`
* `FAIL_CLOSED`
* `HOLD_FOR_REVIEW`

v2.8.1 does not implement these decisions and does not alter v2.7 logic.

## Decision classes

`RELEASE_CANDIDATE` means the proposal is inert, bounded, declared, supported,
and eligible for a future mock handoff only under a future bounded validator.
It is not production authorization or real execution authorization.

`FAIL_CLOSED` means the proposal is blocked before executor handoff because it
requests, implies, or lacks boundaries around dangerous behavior.

`HOLD_FOR_REVIEW` means the proposal is unclear or lacks sufficient clarity,
boundary definition, or evidence for a release-candidate decision.

## Fail-closed reason contract

Allowed future fail-closed reasons should include:

* `sql_execution_requested`
* `sql_mutation_requested`
* `db_connection_requested`
* `schema_introspection_requested`
* `result_readback_requested`
* `model_api_requested`
* `network_requested`
* `subprocess_requested`
* `file_mutation_requested`
* `credential_scope_requested`
* `user_data_scope_requested`
* `unsupported_tool_requested`
* `malformed_proposal`
* `missing_declared_boundary`
* `ambiguous_executor_handoff`
* `undeclared_runtime_dependency`

## Hold-for-review reason contract

Allowed future hold reasons should include:

* `ambiguous_tool_intent`
* `incomplete_boundary`
* `insufficient_non_execution_assertions`
* `unsupported_agent_family_unclear_risk`
* `missing_counter_expectations`
* `unclear_release_condition`

## Release-candidate boundary

`RELEASE_CANDIDATE` is a candidate for future bounded mock handoff only. It
must not authorize:

* SQL execution
* database connection
* model API calls
* network calls
* subprocess calls
* file mutation
* credential access
* user data access
* KerniQ runtime behavior
* E2B handoff
* production runtime behavior

All real-world counters must remain 0.

## Executor handoff contract

Executor handoff is blocked unless a future validation milestone explicitly
marks a proposal eligible for bounded mock handoff.

Even then, the only permitted future evidence is inert mock receipt. v2.8.1
adds no handoff behavior.

## Non-execution evidence contract

Future evidence should preserve:

* `observed_before_execution=true`
* `execution_authorized=false` for dangerous or held proposals
* `executor_handoff_allowed=false` for dangerous or held proposals
* `mock_executor_received=false` for dangerous or held proposals
* `mock_executor_invocations=0` for dangerous or held proposals
* real-world execution counters at 0

## Counter contract

Future controlled proposal evidence should track these counters:

* `sql_execution_attempts`
* `db_connections`
* `schema_introspection`
* `result_readbacks`
* `model_api_calls`
* `network_calls`
* `subprocess_calls`
* `credential_accesses`
* `user_data_accesses`
* `file_mutation_attempts`
* `executor_handoffs`

All counters must be 0 for inert fixtures unless a future bounded mock-only
release-candidate milestone records mock receipt without real-world execution.

## Fixture inertness contract

Future fixtures must be static inert data. They must not contain:

* secrets
* real user data
* live database endpoints
* runnable shell commands intended for execution
* runnable SQL intended for execution
* network calls
* model API calls
* subprocess behavior
* environment-variable access
* credentials
* local machine state dependencies

## Future validator contract

A future validator for this line should be:

* stdlib-only
* read-only
* limited to static fixtures
* non-executing
* fail-closed by default

It must not use LangChain, SQLDatabaseToolkit, SQL execution, database
connections, model APIs, network calls, subprocesses, environment access,
credentials, user data, or CLI integration.

## Contract examples in prose

Example 1: a safe inert proposal with a complete declared boundary may be a
`RELEASE_CANDIDATE`. This is not real execution authorization.

Example 2: a DROP TABLE proposal must be `FAIL_CLOSED` with
`sql_execution_requested`.

Example 3: a proposal missing a declared boundary must be `FAIL_CLOSED` with
`missing_declared_boundary`.

Example 4: a proposal with ambiguous tool intent should be `HOLD_FOR_REVIEW`
with `ambiguous_tool_intent`.

Example 5: a proposal requesting a model API call must be `FAIL_CLOSED` with
`model_api_requested`.

These are prose examples only, not executable fixtures.

## What v2.8.1 adds

v2.8.1 adds:

* this contract document
* README non-claims compression
* package index link update
* roadmap status update

## What v2.8.1 does not add

v2.8.1 does not add:

* source code
* runner
* validator
* fixture
* JSON manifest
* schema
* CLI command
* parser
* proof script
* screenshot
* LangChain integration
* SQLDatabaseToolkit support
* SQL execution
* database access
* model API calls
* KerniQ integration
* E2B integration
* network behavior
* subprocess behavior
* environment access
* credential handling
* user-data handling
* production runtime behavior
* release
* tag

## Public claim boundary

DHMS has defined a prose-only Controlled Agent Proposal Gate Contract for
future repository-local, inert, non-executing controlled proposal fixtures and
validators. The contract builds on the frozen v2.7 Minimal Pre-Execution Fuse
Loop proof and does not add runtime behavior, source code, CLI, fixtures,
validators, schemas, LangChain integration, SQLDatabaseToolkit support, SQL
execution, DB access, model APIs, KerniQ, E2B, network/subprocess behavior,
credential/user-data behavior, production runtime, release, or tag.

The README compression claim is limited to this: README compressed detailed
non-claims into a high-level public boundary summary while preserving detailed
boundaries in linked documents.

## Explicit non-claims

v2.8.1 does not claim:

* production readiness
* real-world agent protection
* real database protection
* LangChain integration
* SQLDatabaseToolkit support
* SQL Agent support
* SQL execution support
* DB connection support
* schema introspection support
* result readback support
* model API integration
* KerniQ integration
* E2B integration
* external runtime integration
* CLI gate-proposal support
* parser support
* hook support
* schema support
* arbitrary execution authorization
* credential safety
* user-data safety
* production runtime behavior

## Failure conditions

A future proposal fixture or validator should fail if it:

* omits `observed_before_execution=true`
* authorizes dangerous execution
* permits executor handoff for dangerous or held proposals
* omits required fail-closed reasons
* omits required hold reasons
* contains executable code
* contains secrets or credentials
* contains real user data
* depends on local machine state
* calls SQL, databases, model APIs, network, subprocesses, KerniQ, E2B, or
  external runtimes

## Proposed next milestone

The proposed next milestone is:

`v2.8.2 Controlled Agent Proposal Static Fixtures`

v2.8.2 should add static inert fixtures only if explicitly approved. It should
not jump to validators, runners, CLI commands, LangChain, SQLDatabaseToolkit,
real SQL, real DB access, model APIs, KerniQ, E2B, production runtime, release,
or tag work.

## Files changed

v2.8.1 is expected to change only:

* `README.md`
* `docs/dhms_controlled_agent_proposal_gate_contract_v2_8_1.md`
* `docs/dhms_agentfuse_protocol_package_index_v0_7_0.md`
* `docs/dhms_agentfuse_development_roadmap.md`

## Files intentionally not modified

v2.8.1 intentionally does not modify:

* v2.8.0 planning document
* v2.7 proof documents
* v2.7 screenshot
* v2.7 proof script
* v2.7 runner validation
* v2.7 gate runner
* v2.7 mock executor
* v2.7 fixtures
* source files
* schema files
* CLI files
* dependency files
* release files

## Validation commands

Expected validation commands:

```bash
python3 validation/run_dhms_pre_execution_fuse_loop_proof_v0.py
python3 validation/run_dhms_pre_execution_fuse_loop_runner_validation_v0.py
python3 -m json.tool benchmarks/dhms_pre_execution_fuse_loop_v0/proposals.json >/dev/null
python3 validation/run_dhms_langchain_sql_agent_adapter_skeleton_shape_fixture_validation_v0.py
python3 validation/run_dhms_langchain_sql_agent_emit_only_adapter_fixture_validation_v0.py
python3 validation/run_dhms_third_party_sql_agent_threat_fixture_validation_v0.py
python3 validation/run_dhms_sql_agent_local_emit_only_fixture_validation_v0.py
python3 validation/run_dhms_bounded_local_mock_to_real_fixture_validation_v0.py
python3 validation/run_dhms_bounded_local_proposal_emitter_candidate_fixture_validation_v0.py
python3 -m json.tool benchmarks/dhms_langchain_sql_agent_adapter_skeleton_shape_v0/shape_fixtures.json >/dev/null
python3 -m json.tool benchmarks/dhms_langchain_sql_agent_emit_only_adapter_v0/adapter_boundary_fixtures.json >/dev/null
git diff --check
git diff --cached --check
```

## Targeted scan summary

Targeted scans should confirm:

* only allowed files changed
* README changed only for status, v2.8.1 link, and public boundary compression
* v2.8.0 planning doc was not modified
* v2.7 freeze, sync, polish, screenshot, proof, runner, gate, mock executor, and
  fixtures were not modified
* no source, schema, CLI, validator, fixture, JSON manifest, screenshot, or
  dependency file was added or changed

## Acceptance checklist

* Controlled agent definition recorded
* Controlled agent non-definition recorded
* Controlled proposal definition recorded
* Proposal envelope contract recorded
* Required envelope fields recorded
* Optional future envelope fields recorded
* Forbidden envelope behavior recorded
* Gate input boundary recorded
* Decision classes recorded
* Fail-closed reasons recorded
* Hold-for-review reasons recorded
* Release-candidate boundary recorded
* Executor handoff contract recorded
* Non-execution evidence contract recorded
* Counter contract recorded
* Fixture inertness contract recorded
* Future validator contract recorded
* README public boundary compressed without weakening detailed non-claims

## Final verdict

`READY_FOR_V2_8_2_CONTROLLED_AGENT_PROPOSAL_STATIC_FIXTURES`
