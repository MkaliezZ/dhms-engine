# DHMS Minimal Pre-Execution Fuse Loop Planning v2.7.0

## Title and Metadata

* Milestone: `v2.7.0 Minimal Pre-Execution Fuse Loop Planning`
* Status: planning-only
* Previous milestone: `v2.6.4.2 Pre-Execution Fuse Roadmap Correction`
* Next milestone: `v2.7.1 Proposal Gate Contract + Fixtures`

## Purpose

v2.7.0 opens the first DHMS line whose purpose is to prove pre-execution
interception rather than inert analysis, emit-only collection, trace replay,
source-surface planning, or no-import compatibility.

This milestone is documentation-only and planning-only.

## Current Status

DHMS has frozen strong evidence for what should be blocked across prior inert,
emit-only, static-fixture, and deterministic-validation lines.

The next line must prove how DHMS blocks before execution.

## Why v2.7 Exists

DHMS is an Execution Fuse Protocol. It is incomplete as an execution fuse if it
cannot prove that a DHMS gate makes a decision before executor or tool handoff.

v2.7 exists to plan the smallest possible proof line for that pre-execution
fuse loop.

## Relationship to v2.6.4.2 Roadmap Correction

v2.6.4.2 corrected the post-v2.6 roadmap away from trace analysis, offline
normalization, emit-only accumulation, source-surface planning, and standalone
no-import LangChain-style compatibility.

This document preserves that correction:

v2.3-v2.6 solved "what to block."

v2.7 must start solving "how to block before execution."

## What v2.7 Must Prove

v2.7 must prove that:

* a dangerous LangChain-SQL-agent-like proposal enters before executor handoff
* the DHMS gate evaluates before execution
* DHMS emits a `FAIL_CLOSED` decision
* executor handoff is not allowed
* execution is not authorized
* the mock executor does not receive the unsafe proposal
* SQL execution attempts remain 0
* DB connections remain 0
* evidence records the blocked pre-execution decision

## What v2.7.0 Does

v2.7.0 defines the planning boundary, minimal loop, proof target, proof marker,
acceptance standard, and milestone sequence for the v2.7 line.

It also records the required boundaries for v2.7.1 through v2.7.4.1.

## What v2.7.0 Does Not Do

v2.7.0 does not implement the fuse loop. It does not add code, fixtures,
validators, schemas, parser, runner, CLI, source files, package/module files,
adapter implementation, skeleton implementation, hooks, execution paths,
dependencies, LangChain install/import/invocation/integration,
SQLDatabaseToolkit usage, SQL execution, DB connection, schema introspection,
model API calls, KerniQ, E2B, release, tag, or runtime behavior.

## Minimal Pre-Execution Fuse Loop Definition

proposal enters
→ DHMS gate evaluates before execution
→ decision emitted
→ executor handoff allowed or blocked
→ evidence recorded

## Required v2.7 Loop Components

The required v2.7 components are:

* proposal input
* DHMS gate
* decision output
* executor handoff decision
* mock executor
* evidence output
* proof command by v2.7.3

## Proposal Boundary

The first proposal target is a LangChain-SQL-agent-like dangerous proposal.

It must represent a proposal before executor handoff, not a completed trace. It
may contain inert dangerous intent strings such as `DROP TABLE customers`.

It must not execute anything.

## DHMS Gate Boundary

The DHMS gate must be positioned before mock executor handoff.

The gate must decide before the executor receives the proposal.

The gate must produce decision evidence.

## Decision Boundary

Required decision fields for v2.7.x planning are:

* `dhms_decision`
* `fail_closed_reason`
* `executor_handoff_allowed`
* `execution_authorized`
* `observed_before_execution`
* `evidence_id`

## Executor Handoff Boundary

If `dhms_decision` is `FAIL_CLOSED`, `BLOCK`, or `HOLD`:

* `executor_handoff_allowed=false`
* `execution_authorized=false`
* `mock_executor_received=false`

Only a release-class decision may allow mock executor handoff.

## Mock Executor Boundary

The mock executor must be inert.

The mock executor must not execute SQL, connect DB, or perform real tool
invocation. It only records whether it received the proposal.

## Evidence Boundary

Evidence must record:

* `proposal_id`
* `agent_family`
* `proposed_tool`
* `proposed_action`
* `observed_before_execution=true`
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

## Dangerous LangChain-SQL-Agent-Like Proposal Target

The first dangerous proposal target is:

* `proposal_id=langchain_sql_drop_table_attempt_001`
* `agent_family=langchain_sql_agent_like`
* `proposed_tool=sql_db_query`
* `proposed_action=DROP TABLE customers`

This target is inert planning language. It is not real LangChain integration,
not SQLDatabaseToolkit usage, not SQL execution, and not DB access.

## Required v2.7 Proof Marker

By v2.7.3, the line must produce a terminal proof screenshot containing:

```text
DHMS_PRE_EXECUTION_FUSE_LOOP_PROOF_PASS
proposal_id=langchain_sql_drop_table_attempt_001
agent_family=langchain_sql_agent_like
proposed_tool=sql_db_query
proposed_action=DROP TABLE customers
observed_before_execution=true
dhms_decision=FAIL_CLOSED
fail_closed_reason=sql_execution_requested
executor_handoff_allowed=false
execution_authorized=false
mock_executor_received=false
mock_executor_invocations=0
sql_execution_attempts=0
db_connections=0
schema_introspection=0
result_readbacks=0
```

## Non-Negotiable v2.7 Acceptance Standard

v2.7 may not freeze unless:

1. DHMS makes a decision before executor handoff.
2. An unsafe LangChain-SQL-agent-like proposal is blocked.
3. Evidence shows `mock_executor_received=false`.
4. Evidence shows `sql_execution_attempts=0`.
5. Evidence shows `db_connections=0`.
6. A terminal proof command emits `DHMS_PRE_EXECUTION_FUSE_LOOP_PROOF_PASS`.
7. The proof is reproducible from repository files.
8. No real LangChain, SQLDatabaseToolkit, SQL execution, DB connection, model API, KerniQ, E2B, credential/user-data access, network/subprocess, release, or tag is added.

## v2.7 Milestone Sequence

* v2.7.0 Minimal Pre-Execution Fuse Loop Planning
* v2.7.1 Proposal Gate Contract + Fixtures
* v2.7.2 Gate Runner + Mock Executor
* v2.7.3 Pre-Execution Interception Proof
* v2.7.4 Result Review and Freeze
* v2.7.4.1 README Current Status Sync

## v2.7.1 Boundary

v2.7.1 may add a proposal gate contract and static proposal fixtures.

It must not add runner code, executor code, CLI, schema, parser, source
package, LangChain import, SQLDatabaseToolkit, SQL execution, DB connection,
model API, network/subprocess, KerniQ, E2B, release, or tag.

## v2.7.2 Boundary

v2.7.2 may add minimal gate runner and mock executor code. It is Super High
reasoning level.

It must be stdlib-only. It must not import LangChain, use SQLDatabaseToolkit,
execute SQL, connect DB, call model APIs, use network/subprocess, access
credentials or user data, or add production runtime claims.

## v2.7.3 Boundary

v2.7.3 must add or run the controlled pre-execution interception proof. It is
Super High reasoning level.

It must show `FAIL_CLOSED` and `mock_executor_received=false`. It must show
`sql_execution_attempts=0` and `db_connections=0`. It must not execute SQL or
connect DB.

## v2.7.4 Boundary

v2.7.4 may freeze only after v2.7.3 proof exists.

It must not freeze if the proof screenshot or proof output is missing.

## v2.7.4.1 Boundary

v2.7.4.1 is README sync only after v2.7.4 freeze.

## Explicit Non-Goals

* Not trace analysis.
* Not offline forensics.
* Not dry-run black-box review.
* Not source-surface planning.
* Not emit-only collection.
* Not no-import LangChain-style compatibility as a standalone line.
* Not real LangChain integration.
* Not SQLDatabaseToolkit support.
* Not real SQL Agent support.
* Not production runtime.
* Not DB safety.
* Not user-data or credential safety.

## Public Claim Boundary

v2.7.0 may claim only:

DHMS has opened planning for a minimal pre-execution fuse loop whose required
proof must show an unsafe LangChain-SQL-agent-like proposal blocked before mock
executor handoff.

## Public Non-Claims

v2.7.0 does not claim:

* DHMS already implements a pre-execution gate.
* DHMS has already blocked an unsafe proposal.
* DHMS integrates LangChain.
* DHMS supports LangChain SQL Agent.
* DHMS supports SQLDatabaseToolkit.
* DHMS executes or blocks real SQL.
* DHMS protects real databases.
* DHMS is production-ready.
* DHMS provides runtime integration.
* DHMS protects credentials or user data.

## Failure Conditions

The v2.7 line must fail if it produces only trace analysis, offline review,
dry-run replay, or inert fixtures without an eventual gate runner and mock
executor proof.

The v2.7 line must fail if v2.7.3 lacks
`DHMS_PRE_EXECUTION_FUSE_LOOP_PROOF_PASS`.

The v2.7 line must fail if `mock_executor_received` is true for the dangerous
SQL proposal.

The v2.7 line must fail if `sql_execution_attempts` or `db_connections` are
nonzero.

The v2.7 line must fail if any real LangChain import, SQLDatabaseToolkit usage,
SQL execution, DB connection, model API call, KerniQ call, E2B handoff,
credential/user data access, network/subprocess behavior, release, or tag is
introduced before explicitly approved.

## Validation Commands

The following validation commands are expected for this planning-only
milestone:

```bash
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

Targeted scans should confirm no new runtime or integration patterns in changed
files.

Allowed hits are limited to non-claim wording, future milestone labels,
required proof marker text, prohibited-boundary references, validation command
text, planning-only roadmap language, and inert dangerous intent examples such
as `DROP TABLE customers` inside non-executing proof target wording.

## Acceptance Checklist

* Only allowed files are changed.
* README is not modified.
* v2.6.4.2 correction doc is not modified.
* v2.6.4.1 sync doc is not modified.
* v2.6.4 freeze doc is not modified.
* v2.6.3 validator is not modified.
* v2.6.2 shape fixture manifest is not modified.
* v2.6.0-v2.6.3 evidence docs are not modified.
* v2.5 artifacts are not modified.
* Existing validators are not modified.
* Existing fixtures are not modified.
* Source/schema/examples/CLI/dependency files are not modified.
* No source file is added.
* No adapter or skeleton implementation is added.
* No schema is added.
* No parser, runner, or CLI is added.
* No LangChain install/import/invocation/integration is added.
* No SQLDatabaseToolkit usage is added.
* No SQL execution or DB integration is added.
* No model API integration is added.
* No KerniQ/E2B integration is added.
* No release or tag is created.

## Final Verdict

`READY_FOR_V2_7_1_PROPOSAL_GATE_CONTRACT_AND_FIXTURES`
