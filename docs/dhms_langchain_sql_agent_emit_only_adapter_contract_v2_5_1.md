# DHMS LangChain SQL Agent Emit-Only Adapter Contract v2.5.1

## Title and Metadata

* Milestone: `v2.5.1 LangChain SQL Agent Emit-Only Adapter Contract`
* Contract subject: `LangChain SQL Agent Emit-Only Adapter Candidate`
* Status: prose-contract-only
* Previous milestone: `v2.5.0 LangChain SQL Agent Emit-Only Adapter Planning`
* Next milestone: `v2.5.2 LangChain SQL Agent Static Adapter Boundary Fixtures`

## Current Status

v2.5.1 converts the v2.5.0 planning boundary into a prose-only contract for a
future LangChain SQL Agent emit-only adapter candidate.

This milestone does not implement an adapter. It does not install, import,
invoke, adapt, or integrate LangChain. It does not use SQLDatabaseToolkit, run a
LangChain SQL Agent, execute SQL, connect to a database, inspect schemas, call
model APIs, call KerniQ, hand off to E2B, access credentials, access user data,
or add runtime behavior.

## Scope

The scope is limited to defining a contract for a future observation-only
boundary. The future candidate may eventually observe proposed LangChain
SQL-agent actions before execution and emit inert DHMS proposal metadata for
DHMS evaluation.

The emitted metadata does not authorize execution. DHMS remains the boundary
evaluator before any execution.

## Non-Scope

v2.5.1 does not add:

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
* dependency changes
* package installation
* LangChain installation, import, invocation, adaptation, or integration
* SQLDatabaseToolkit usage
* SQL execution
* database connection
* schema introspection
* synthetic database creation
* database client or ORM usage
* model-provider clients
* model API calls
* KerniQ calls
* E2B handoff
* environment-variable reads
* credential access
* user data access
* network, subprocess, shell, command, or terminal behavior
* release or tag

## Relationship to v2.5.0

v2.5.0 planned the future LangChain SQL Agent emit-only adapter boundary.
v2.5.1 turns that plan into a prose-only contract with explicit roles,
observation requirements, emit-only constraints, classification terms, evidence
capture fields, fail-closed categories, and later milestone boundaries.

v2.5.1 preserves the v2.5.0 non-execution boundary. It does not implement the
adapter concept described by v2.5.0.

## Contract Subject

The contract subject is:

`LangChain SQL Agent Emit-Only Adapter Candidate`

This subject is a future conceptual boundary only. It is not a supported
adapter, runtime hook, framework integration, database connector, model client,
or execution path in v2.5.1.

## Contract Roles

* LangChain SQL Agent framework: untrusted third-party proposal/runtime subject.
* SQLDatabaseToolkit: prohibited executable boundary subject in this milestone.
* Model provider: untrusted proposal source.
* Future emit-only adapter candidate: future observation-only boundary that may
  emit inert metadata before execution.
* DHMS: boundary evaluator before any execution.
* Database/tool runtime: forbidden in this milestone.
* Evidence artifact: future inert review material only.

## Observation Boundary Contract

DHMS must be able to observe a proposed LangChain SQL-agent action before
execution. If the proposed action cannot be observed before execution, the
future decision must fail closed.

The observation boundary must require:

* hidden framework execution fails closed
* unbounded framework tool loops fail closed
* unbounded retry or self-correction loops fail closed
* proposal metadata is distinguishable from executable tool input
* SQL text status is distinguishable from SQL execution
* database connection intent is distinguishable from an actual connection
* schema introspection intent is distinguishable from actual schema access
* result readback intent is distinguishable from actual result access

## Emit-Only Contract

A future adapter candidate may only emit inert DHMS proposal metadata.

It must not:

* forward executable tool input
* transform metadata into executable SQL or tool calls
* connect to databases
* inspect schemas
* execute SQL
* read SQL results
* call model APIs
* access credentials
* access user data
* manage LangChain runtime loops
* manage retry loops

Emitted metadata does not authorize execution.

## Inert Proposal Classification Contract

The following are prose-only classification terms, not schemas or fixtures:

* `inert_adapter_metadata`
* `executable_tool_input`
* `langchain_runtime_unobserved`
* `sql_database_toolkit_detected`
* `db_connection_request`
* `schema_introspection_request`
* `sql_execution_request`
* `result_readback_request`
* `credential_request`
* `user_data_request`
* `mutation_or_write_intent`
* `framework_managed_tool_loop`
* `retry_loop_unbounded`
* `unsupported_model_behavior`
* `unsupported_langchain_tool_format`
* `adapter_boundary_missing`
* `evidence_capture_missing`

## Executable Tool-Input Boundary

Executable tool input is outside the v2.5.1 contract. If the future boundary
detects executable tool input, it must fail closed.

Inert metadata may describe a proposal. It must not be directly usable as a
tool call, database action, SQL execution request, model-provider request, or
runtime-loop instruction.

## SQLDatabaseToolkit Boundary

SQLDatabaseToolkit is a prohibited executable boundary subject in v2.5.1. The
contract does not support SQLDatabaseToolkit usage.

If SQLDatabaseToolkit is detected as part of an executable action path, the
future decision must fail closed unless a later phase explicitly approves a
separate constrained proof boundary.

## Database Boundary

Database/tool runtime access is forbidden in this milestone. The future
candidate must not connect to databases, inspect schemas, execute SQL, read
results, mutate data, or request database credentials.

Any proposed database connection, schema introspection, SQL execution, result
readback, credential request, user-data request, or mutation/write intent must
fail closed.

## Framework-Loop Boundary

Framework-managed tool loops are not trusted by default. If a LangChain SQL
Agent framework loop can execute hidden actions, retry without bounds,
self-correct into execution, or obscure proposal evidence, the future decision
must fail closed.

DHMS must evaluate the proposal boundary before execution. The framework must
not be treated as the policy owner or final execution authority.

## Model-Provider Boundary

The model provider is an untrusted proposal source. Model output is not proof of
safe execution.

Unsupported model behavior, missing proposal evidence, ambiguous tool format,
runtime-loop ambiguity, or model output that cannot be separated from executable
tool input must fail closed.

## Evidence Capture Contract

Future evidence fields are prose-only planning terms:

* `adapter_subject`
* `framework_subject`
* `model_provider_subject`
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

Future evidence must show that no SQL execution, database connection, schema
introspection, result readback, model API call, LangChain invocation, KerniQ
call, E2B handoff, credential access, user-data access, or runtime behavior
occurred unless a later phase explicitly approves a constrained proof boundary.

## Required Fail-Closed Categories

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

LangChain remains an untrusted third-party proposal/runtime subject. v2.5.1
does not cite version-specific LangChain APIs and does not install, import,
invoke, adapt, or integrate LangChain.

The future candidate may only be considered if proposed actions can be observed
before execution and represented as inert DHMS proposal metadata.

## KerniQ/E2B Boundary

KerniQ and E2B are out of scope for this contract. v2.5.1 does not call KerniQ,
does not hand off to E2B, and does not define a runtime bridge.

Any future KerniQ or E2B boundary would require explicit later approval.

## Later Milestone Boundary

The next milestone is:

`v2.5.2 LangChain SQL Agent Static Adapter Boundary Fixtures`

v2.5.2 may add static inert fixtures only. It must not add code, validators,
schemas, parser, runner, CLI, dependencies, LangChain install/import/invocation
or integration, SQLDatabaseToolkit usage, SQL execution, DB connection, schema
introspection, model API call, KerniQ, E2B, release, tag, or runtime behavior.

## Public Claims

v2.5.1 may claim:

* DHMS has a prose-only contract for a future LangChain SQL Agent emit-only
  adapter boundary
* the contract subject is `LangChain SQL Agent Emit-Only Adapter Candidate`
* DHMS must observe proposed actions before execution
* emitted metadata must be inert
* executable, hidden, DB-connected, schema-introspective, SQL-executing,
  result-reading, credential-seeking, user-data-seeking, mutation-oriented,
  evidence-missing, unsupported, or unbounded loop behavior fails closed

## Public Non-Claims

v2.5.1 does not claim:

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

* v2.5.1 is prose-contract-only
* no code added
* no fixtures added or modified
* no validators added or modified
* no schema added
* no parser added
* no runner added
* no CLI command added
* no dependency added
* no LangChain install/import/invocation/integration added
* no SQLDatabaseToolkit usage added as integration
* no SQL execution or DB integration added
* no model API integration added
* no KerniQ/E2B integration added
* package index links this document
* roadmap marks v2.5.1 and points to v2.5.2

## Final Verdict

`READY_FOR_V2_5_2_LANGCHAIN_SQL_AGENT_STATIC_ADAPTER_BOUNDARY_FIXTURES`
