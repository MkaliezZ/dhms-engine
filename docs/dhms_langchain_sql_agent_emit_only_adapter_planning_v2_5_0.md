# DHMS LangChain SQL Agent Emit-Only Adapter Planning v2.5.0

## Title and Metadata

* Milestone: `v2.5.0 LangChain SQL Agent Emit-Only Adapter Planning`
* Subject: `LangChain SQL Agent Emit-Only Adapter Candidate`
* Status: planning-only
* Previous milestone: `v2.4.4.1 README Current Status Sync`
* Next milestone: `v2.5.1 LangChain SQL Agent Emit-Only Adapter Contract`

## Current Status

v2.5.0 starts a planning-only line for a future LangChain SQL Agent emit-only
adapter boundary. The milestone defines concepts, boundaries, fail-closed
conditions, and future evidence needs.

This milestone does not implement an adapter. It does not install, import,
invoke, adapt, or integrate LangChain. It does not run a LangChain SQL Agent,
use SQLDatabaseToolkit, execute SQL, connect to a database, inspect schemas,
call model APIs, call KerniQ, hand off to E2B, or add runtime behavior.

## Scope

The scope is limited to prose planning for a future conceptual adapter boundary.
The future subject is:

`LangChain SQL Agent Emit-Only Adapter Candidate`

The candidate may eventually observe proposed LangChain SQL-agent actions before
execution and emit inert DHMS proposal metadata. The emitted metadata would be
for DHMS evaluation only and would not itself authorize execution.

## Non-Scope

v2.5.0 does not add:

* code
* fixtures
* validators
* schemas
* parsers
* runners
* CLI commands
* adapter implementation
* hooks
* execution paths
* dependencies
* package installation
* LangChain installation, import, invocation, adaptation, or integration
* SQLDatabaseToolkit usage
* SQL execution
* database connection
* schema introspection
* synthetic database creation
* database client or ORM usage
* model API calls
* KerniQ calls
* E2B handoff
* credential access
* user data access
* network, subprocess, shell, or command behavior
* release or tag

## Relationship to v2.4.4.1

v2.4.4.1 synchronized README, package index, and roadmap after the v2.4.4
third-party SQL Agent threat-boundary freeze. That frozen line treats
LangChain, LlamaIndex, and domestic LLMs as threat-boundary subjects only.

v2.5.0 narrows the next planning target to LangChain SQL Agent emit-only adapter
boundary design. It preserves the v2.4 frozen non-execution evidence and does
not convert threat-boundary review into integration.

## Future Adapter Concept

The future adapter concept is an observation boundary. It may eventually sit
between a LangChain SQL Agent proposal surface and DHMS, translating observed
proposed actions into inert DHMS proposal metadata before any execution.

The future adapter must not be an execution adapter. It must not forward,
transform, or produce executable tool input. It must not manage the LangChain
runtime loop. It must not retry actions. It must not connect to a database,
inspect schemas, execute SQL, read results, call model APIs, access credentials,
or touch user data.

DHMS asks whether a proposed action should be released at all, under what
boundary, and with what evidence. LangChain remains an untrusted third-party
proposal/runtime subject.

## Emit-Only Boundary

Emit-only means the candidate can only emit inert metadata for DHMS evaluation.
The emitted metadata must be non-executable, deterministic, and bounded.

The future boundary must guarantee:

* observed proposed actions are captured before execution
* emitted records are inert DHMS proposal metadata only
* no executable tool input is generated
* no SQL is executed
* no database is contacted
* no schema is inspected
* no model provider is called
* no credential or user data is accessed
* no runtime loop is controlled
* no retry loop is managed
* rejected or unsupported proposals fail closed

## Observation Boundary

The observation boundary is the point at which DHMS can see a proposed action
before it crosses into execution. If a proposed action cannot be observed before
execution, the future adapter must fail closed.

Observation must distinguish:

* proposal metadata from executable tool input
* proposed SQL text status from SQL execution
* database connection intent from an actual database connection
* schema introspection intent from actual schema access
* result readback intent from actual result access
* mutation intent from non-mutating proposal metadata
* bounded framework behavior from unbounded runtime loops

## Proposed Inert Envelope Shape, Prose-Only

A future prose-only envelope may describe these fields:

* `adapter_subject`
* `framework_subject`
* `observed_action_stage`
* `proposal_source`
* `proposal_shape`
* `tool_input_status`
* `sql_text_status`
* `db_connection_scope`
* `schema_introspection_scope`
* `sql_execution_scope`
* `result_readback_scope`
* `credential_scope`
* `user_data_scope`
* `mutation_intent`
* `framework_loop_status`
* `retry_loop_status`
* `expected_dhms_decision`
* `expected_fail_closed_reason`
* `non_execution_assertions`

These are planning fields only. v2.5.0 does not add a schema or fixture.

## Required Future Evidence Fields, Prose-Only

Future evidence should be able to prove:

* the proposal was observed before execution
* emitted metadata was inert
* no executable tool input was produced
* no SQL execution was attempted
* no database connection was attempted
* no schema introspection was attempted
* no result readback was attempted
* no credentials were requested or accessed
* no user data was requested or accessed
* no model API call was made
* no LangChain runtime was invoked
* no SQLDatabaseToolkit usage occurred
* no KerniQ call occurred
* no E2B handoff occurred
* unsupported proposal shapes failed closed

## Fail-Closed Conditions

The future boundary must fail closed for:

* `langchain_runtime_unobserved`
* `executable_tool_input_detected`
* `sql_database_toolkit_detected`
* `db_connection_requested`
* `schema_introspection_requested`
* `sql_execution_requested`
* `result_readback_requested`
* `credential_scope_non_empty`
* `user_data_scope_non_empty`
* `mutation_or_write_intent`
* `framework_tool_loop_unbounded`
* `retry_loop_unbounded`
* `adapter_boundary_missing`
* `evidence_capture_missing`
* `unsupported_model_behavior`
* `unsupported_langchain_tool_format`

## LangChain Boundary

LangChain is treated as an untrusted third-party proposal/runtime subject. DHMS
does not assume LangChain is the policy owner or final execution authority.

v2.5.0 does not cite version-specific LangChain APIs. It does not install,
import, invoke, adapt, or integrate LangChain. It only defines the future
boundary conditions under which a LangChain SQL Agent proposal could be observed
as inert DHMS metadata.

## SQLDatabaseToolkit Boundary

SQLDatabaseToolkit is a boundary subject, not a supported integration in
v2.5.0. If future evidence detects SQLDatabaseToolkit usage, executable tool
input, database connection, schema introspection, SQL execution, or result
readback, the future adapter boundary must fail closed unless a later phase
explicitly approves a constrained proof path.

## DB Boundary

The future boundary must treat database access as prohibited unless a later
phase explicitly approves a constrained proof. v2.5.0 does not connect to any
database, inspect schemas, create synthetic databases, use database clients, use
ORMs, execute SQL, or read results.

## Model-Provider Boundary

The future boundary must not call model APIs. Model behavior is a proposal
source risk, not proof of safe execution. Unsupported model behavior, missing
proposal evidence, or unbounded runtime-loop behavior must fail closed.

## KerniQ/E2B Boundary

v2.5.0 does not call KerniQ and does not hand off to E2B. KerniQ and E2B remain
out of scope for this milestone. Any future handoff or runtime bridge would
require explicit approval in a later phase.

## Future Milestone Path

`v2.5.1 LangChain SQL Agent Emit-Only Adapter Contract`

v2.5.1 must be prose-contract-only. It must not add code, fixtures, validators,
schemas, parser, runner, CLI, dependencies, LangChain install/import/invocation
or integration, SQLDatabaseToolkit usage, SQL execution, DB connection, schema
introspection, model API call, KerniQ, E2B, release, tag, or runtime behavior.

## Public Claims

v2.5.0 may claim:

* DHMS has a planning-only LangChain SQL Agent emit-only adapter boundary
* the planned subject is a future conceptual adapter boundary only
* DHMS would require observation before execution
* emitted metadata must be inert
* unsupported, unobserved, executable, DB-connected, schema-introspective,
  credential-seeking, user-data-seeking, mutation-oriented, or evidence-missing
  proposals fail closed

## Public Non-Claims

v2.5.0 does not claim:

* LangChain integration
* LangChain SQL Agent support
* SQLDatabaseToolkit support
* SQL agent implementation
* SQL execution support
* arbitrary SQL safety
* database connection support
* schema introspection support
* real schema access
* real data access
* database mutation safety
* database client or ORM support
* model-provider integration
* KerniQ integration
* E2B integration
* runtime behavior
* production readiness
* user data safety
* credential safety

## Acceptance Checklist

* v2.5.0 is planning-only
* no code added
* no fixtures added or modified
* no validators added or modified
* no schema added
* no parser added
* no runner added
* no CLI command added
* no dependency added
* no LangChain install/import/invocation/integration added
* no SQLDatabaseToolkit usage added
* no SQL execution or DB integration added
* no model API integration added
* no KerniQ/E2B integration added
* package index links this document
* roadmap marks v2.5.0 and points to v2.5.1

## Final Verdict

`READY_FOR_V2_5_1_LANGCHAIN_SQL_AGENT_EMIT_ONLY_ADAPTER_CONTRACT`
