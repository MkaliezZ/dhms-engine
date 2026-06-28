# DHMS Controlled Agent Proposal Gate Planning v2.8.0

## Title and Metadata

* Milestone: `v2.8.0 Controlled Agent Proposal Gate Planning`
* Status: `planning-only`
* Previous milestone: `v2.7.4.2 README Public Landing Page Polish`
* Next milestone: `v2.8.1 Controlled Agent Proposal Gate Contract`
* Reasoning level: `Super High`

## Purpose

v2.8.0 opens the planning line for a Controlled Agent Proposal Gate that
evaluates controlled agent proposals before executor handoff.

This milestone is documentation-only and planning-only. It does not add runtime
behavior, source code, fixtures, validators, schemas, CLI commands, dependencies,
proof scripts, screenshots, release artifacts, or tags.

## Current Status

The current frozen proof boundary remains v2.7:

DHMS has a repository-local, stdlib-only Minimal Pre-Execution Fuse Loop proof
showing that one inert LangChain-SQL-agent-like DROP TABLE proposal is observed
before execution, fail-closed by the DHMS gate before executor handoff, not
received by the inert mock executor, and recorded with zero SQL execution
attempts, zero DB connections, zero schema introspection, and zero result
readbacks.

## Relationship to v2.7

v2.7 proved that one inert dangerous LangChain-SQL-agent-like DROP TABLE
proposal can be observed before execution, fail-closed, blocked before mock
executor handoff, and recorded with zero SQL/DB/schema/result counters.

v2.8.0 does not modify or reinterpret v2.7. It plans the next bounded line
after v2.7.

## Why v2.8 Exists

v2.7 proves the minimal loop over a specific proposal. v2.8 plans a controlled
proposal-gate structure for future controlled agent-like proposal sources.

The goal is to define the safe next route without jumping directly into CLI,
LangChain, SQLDatabaseToolkit, real SQL, real DB, model APIs, KerniQ, E2B,
production runtime, or release/tag work.

## Controlled Agent Proposal Gate Concept

A Controlled Agent Proposal Gate is a future bounded DHMS gate that receives a
structured proposal envelope from a controlled agent-like source before
execution and decides whether the proposal is eligible for future handoff,
fail-closed, or held.

This is a planning concept only. It is not a real agent integration, not a CLI,
not LangChain integration, not SQLDatabaseToolkit support, not real SQL/DB
behavior, and not production runtime behavior.

## Controlled Agent Definition

For v2.8 planning, a controlled agent is:

* a bounded, repository-local, inert proposal source for future proof design
* not a real autonomous agent
* not a model-connected agent
* not a LangChain agent
* not a SQL Agent
* not an E2B or KerniQ runtime
* not an external runtime
* not allowed to execute tools, commands, SQL, DB calls, network calls, model
  calls, or file mutations

## Proposal Envelope Concept

Future v2.8 work may describe a proposal envelope with fields such as:

* `proposal_id`
* `agent_family`
* `controlled_agent_profile`
* `proposed_tool`
* `proposed_action`
* `tool_input_summary`
* `declared_boundary`
* `observed_before_execution`
* `expected_dhms_decision`
* `expected_fail_closed_reason`
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

v2.8.0 does not add this schema as a file. It describes the concept only.

## Gate Boundary Concept

The gate must receive proposal data before execution. Post-hoc traces are not
acceptable as proof of interception because they do not prove that DHMS blocked
or held the proposal before executor handoff.

## Executor Handoff Boundary

Future executor handoff remains blocked unless a proposal is explicitly
eligible under a bounded future release condition.

v2.8.0 does not define runtime execution, real executor handoff, or production
authorization.

## Evidence Model

Future controlled proposal gate evidence should record fields such as:

* `observed_before_execution`
* `dhms_decision`
* `fail_closed_reason`
* `executor_handoff_allowed`
* `execution_authorized`
* `mock_executor_received`
* `mock_executor_invocations`
* `sql_execution_attempts`
* `db_connections`
* `schema_introspection`
* `result_readbacks`
* `model_api_calls`
* `network_calls`
* `subprocess_calls`
* `credential_accesses`
* `user_data_accesses`

## Planned Fixture Families

Future v2.8 fixture families may include:

* safe inert controlled proposal
* dangerous SQL execution proposal
* SQL mutation proposal
* schema introspection proposal
* result readback proposal
* DB connection proposal
* credential scope proposal
* user data scope proposal
* unsupported tool proposal
* malformed proposal
* missing boundary proposal
* ambiguous handoff proposal
* model API proposal
* network proposal
* subprocess proposal
* file mutation proposal

v2.8.0 does not create fixture files.

## Planned Decision Classes

Future v2.8 planning may use these decision classes:

* `RELEASE_CANDIDATE`
* `FAIL_CLOSED`
* `HOLD_FOR_REVIEW`

v2.8.0 does not implement these classes and does not alter current v2.7
decision names or logic.

## Planned Non-Execution Counters

Future evidence may track:

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

## Planned Future Validation Path

Proposed future sequence:

* `v2.8.1 Controlled Agent Proposal Gate Contract`
* `v2.8.2 Controlled Agent Proposal Static Fixtures`
* `v2.8.3 Controlled Agent Proposal Gate Non-Executing Validation`
* `v2.8.4 Controlled Agent Proposal Gate Result Review and Freeze`
* `v2.8.4.1 README Current Status Sync` if needed

v2.8.1 should still be docs-only and contract-only unless explicitly approved
later.

## What v2.8.0 Adds

v2.8.0 adds:

* one planning document
* package index update
* roadmap update

## What v2.8.0 Does Not Add

v2.8.0 adds no:

* source code
* runner
* validator
* fixture
* schema
* CLI
* parser
* proof script
* screenshot
* LangChain integration
* SQLDatabaseToolkit support
* SQL execution
* DB connection
* model API
* KerniQ
* E2B
* network/subprocess/env behavior
* credential/user-data behavior
* production runtime
* release or tag

## Public Claim Boundary

v2.8.0 may claim only:

DHMS has opened a planning-only Controlled Agent Proposal Gate line that builds
on the frozen v2.7 Minimal Pre-Execution Fuse Loop proof. v2.8.0 defines the
intended bounded planning concepts for future controlled proposal-gate evidence,
without adding runtime behavior, CLI, fixtures, validators, schemas, LangChain
integration, SQLDatabaseToolkit support, SQL execution, DB access, model APIs,
KerniQ, E2B, network/subprocess behavior, credential/user-data behavior,
production runtime, release, or tag.

## Explicit Non-Claims

v2.8.0 does not claim:

* production readiness
* real agent integration
* real LangChain integration
* SQLDatabaseToolkit support
* real SQL Agent support
* real SQL execution support
* real DB protection
* schema introspection protection for real DBs
* model-provider integration
* credential safety
* user-data safety
* KerniQ integration
* E2B integration
* CLI support
* parser support
* hook support
* schema support
* fixture support for v2.8
* validator support for v2.8
* real execution authorization
* production runtime behavior
* protection against arbitrary real-world agents
* support for external databases
* support for real tool calls
* `python3 cli.py gate-proposal` support
* `examples/proposals/drop_table.json` support

## Failure Conditions

v2.8.0 fails if it:

* modifies README
* modifies source files
* modifies proof scripts
* modifies runners
* modifies mock executors
* modifies fixtures
* modifies screenshots
* adds CLI, schema, parser, validator, runner, fixtures, source files,
  dependencies, release, or tag
* adds or claims LangChain, SQLDatabaseToolkit, SQL, DB, model, KerniQ, E2B,
  network, subprocess, env, credential, or user-data behavior
* claims production readiness
* claims real third-party runtime support
* claims real DB safety
* claims v2.8 implementation rather than planning

## Proposed v2.8 Milestone Sequence

* `v2.8.0 Controlled Agent Proposal Gate Planning`
* `v2.8.1 Controlled Agent Proposal Gate Contract`
* `v2.8.2 Controlled Agent Proposal Static Fixtures`
* `v2.8.3 Controlled Agent Proposal Gate Non-Executing Validation`
* `v2.8.4 Controlled Agent Proposal Gate Result Review and Freeze`
* `v2.8.4.1 README Current Status Sync` if needed

## Files Changed

* `docs/dhms_controlled_agent_proposal_gate_planning_v2_8_0.md`
* `docs/dhms_agentfuse_protocol_package_index_v0_7_0.md`
* `docs/dhms_agentfuse_development_roadmap.md`

## Files Intentionally Not Modified

* `README.md`
* `docs/dhms_readme_public_landing_page_polish_v2_7_4_2.md`
* `docs/dhms_readme_current_status_sync_v2_7_4_1.md`
* `docs/dhms_pre_execution_fuse_loop_result_review_and_freeze_v2_7_4.md`
* `docs/development/screenshots/v2_7_3_pre_execution_interception_proof/v2_7_3_pre_execution_interception_proof_terminal.png`
* `validation/run_dhms_pre_execution_fuse_loop_proof_v0.py`
* `docs/dhms_pre_execution_interception_proof_v2_7_3.md`
* `dhms_agentfuse/pre_execution_gate.py`
* `dhms_agentfuse/inert_mock_executor.py`
* `validation/run_dhms_pre_execution_fuse_loop_runner_validation_v0.py`
* `docs/dhms_gate_runner_and_mock_executor_v2_7_2.md`
* `docs/dhms_proposal_gate_contract_and_fixtures_v2_7_1.md`
* `benchmarks/dhms_pre_execution_fuse_loop_v0/proposals.json`
* `docs/dhms_minimal_pre_execution_fuse_loop_planning_v2_7_0.md`
* existing validators, fixtures, examples, source files, schemas, CLI files,
  dependency/package files, release docs, and frozen artifacts

## Validation Commands

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

## Targeted Scan Summary

Targeted scans should show only planning-only wording, explicit non-claims,
future milestone labels, required proof marker text, runner validation marker
references, inherited screenshot path references from the package index context,
prohibited-boundary references, validation command text, inert dangerous-intent
examples such as `DROP TABLE customers`, and proof evidence such as
`execution_authorized=false` and `mock_executor_received=false`.

## Acceptance Checklist

* [x] v2.8.0 is planning-only.
* [x] v2.8.0 does not modify v2.7 frozen proof behavior.
* [x] v2.8.0 defines a controlled agent proposal gate concept.
* [x] v2.8.0 defines a controlled agent as repository-local and inert.
* [x] v2.8.0 describes a future proposal envelope concept without adding a
  schema file.
* [x] v2.8.0 describes planned fixture families without creating fixtures.
* [x] v2.8.0 describes planned decision classes without implementing them.
* [x] v2.8.0 describes planned non-execution counters.
* [x] v2.8.0 defines the future v2.8 validation path.
* [x] v2.8.0 adds no source code, runner, validator, fixture, schema, CLI,
  parser, dependency, screenshot, release, or tag.

## Final Verdict

`READY_FOR_V2_8_1_CONTROLLED_AGENT_PROPOSAL_GATE_CONTRACT`
