# DHMS SQL Agent Local Emit-Only Test Planning v2.3.0

## Metadata

* Milestone: `v2.3.0 SQL Agent Local Emit-Only Test Planning`
* Repository branch: `agent-harness-v1`
* Prior milestone: `v2.2.4.1 README and Roadmap Current Status Sync`
* Next recommended milestone: `v2.3.1 SQL Agent Local Emit-Only Contract`

## Current Status

v2.3.0 is planning-only and docs-only. It plans the first SQL Agent proof line
as an emit-only, proposal-only, non-executing boundary.

## Scope

The planning target is `SQL Proposal Agent Candidate`. The intended future
shape is:

Natural language request -> inert SQL proposal envelope -> DHMS boundary
evaluation

DHMS remains the boundary evaluator before execution. The future candidate may
only emit inert proposal envelopes.

## Non-Scope

v2.3.0 does not implement a SQL agent, use LangChain, use LlamaIndex, connect
to any database, execute SQL, inspect real schemas, read real data, mutate
databases, use sqlite/postgres/mysql clients, use ORM, add schema, add JSON
examples, add fixtures, add parser, add runner, add validator, add CLI, add
quickstart, add adapter, add hook, add execution path, add subprocess usage,
add shell behavior, add command execution, add file mutation behavior, add
network access, add env access, add credential access, add user-data access,
add SDK/model/runtime access, integrate KerniQ, invoke KerniQ, add KerniQ
runtime call, integrate E2B, add E2B handoff, add E2B sandbox, create a release,
or create a tag.

## Relationship to v2.2.4.1

v2.2.4.1 synced README and roadmap after the bounded local proposal emitter
candidate validation freeze. It redirected the next proof-line direction from
KerniQ-first to SQL Agent Local Emit-Only Test Planning. v2.3.0 opens that
planning line without adding implementation.

## Why SQL Agent First

SQL Agent is first because it has a narrower action space, clearer risk
taxonomy, natural continuity with the DHMS SQL Fuse line, and easier inert
proposal validation than broader runtime-emitter targets.

## SQL Proposal Agent Candidate Boundary

`SQL Proposal Agent Candidate` is not a LangChain SQL Agent, LlamaIndex SQL
Agent, real database agent, DB execution agent, SQL runner, SQL parser, SQL
validator, ORM adapter, or runtime integration.

It is only a future planning target for a local component that may emit inert
SQL proposal envelopes for DHMS boundary evaluation.

## Emit-Only Proposal Objective

The objective is to plan a candidate that can describe proposed SQL intent
without executing, validating, parsing-for-execution, connecting, inspecting,
or mutating anything. The output remains inert metadata until a separately
approved future phase defines static fixtures or validation.

## Candidate Envelope Fields, Prose-Only

Future planning fields may include:

* `proposal_id`
* `agent_profile`
* `natural_language_request`
* `sql_dialect`
* `sql_candidate`
* `sql_operation_type`
* `declared_tables`
* `declared_columns`
* `declared_side_effects`
* `read_write_class`
* `risk_markers`
* `where_clause_present`
* `limit_clause_present`
* `credential_scope`
* `user_data_scope`
* `db_connection_scope`
* `schema_source`
* `runtime_target`
* `dry_run`
* `expected_dhms_decision`
* `expected_fail_closed_reason`
* `non_execution_assertions`

These are prose-only planning fields. v2.3.0 does not create schema, JSON
examples, fixtures, parser behavior, or runtime behavior.

Required future boundary values:

* `dry_run` must be true in later fixtures.
* `db_connection_scope` must remain empty.
* `credential_scope` must remain empty.
* `user_data_scope` must remain empty.
* `schema_source` must be synthetic or declared-only.
* `runtime_target` must be `no-runtime`.
* SQL proposal text must remain inert metadata, not executable input.

## SQL Risk Taxonomy, Prose-Only

Future risk categories may include:

* read-only query proposal
* write or mutation proposal
* destructive DDL proposal
* missing WHERE mutation proposal
* broad table scan proposal
* sensitive-data query proposal
* cross-database access proposal
* credential-seeking proposal
* schema-introspection proposal

These are category names only. v2.3.0 does not include real SQL statements.

## DB Boundary

v2.3.0 does not connect to any database, execute SQL, inspect real schemas,
read real data, mutate databases, use sqlite/postgres/mysql clients, use ORM,
access credentials, access user data, or authorize database runtime behavior.

The target is SQL Proposal Agent, not a real database agent.

## LangChain / LlamaIndex Boundary

v2.3.0 does not use LangChain, LlamaIndex, SQLDatabaseToolkit, SQL agent
runtime, provider SDKs, agent SDKs, or runtime adapters. Any future discussion
of third-party frameworks requires separate planning and approval.

## KerniQ Deferral Boundary

KerniQ remains deferred to a later candidate line after SQL Agent emit-only
proof planning. v2.3.0 does not install KerniQ, run KerniQ, invoke KerniQ,
integrate KerniQ, or add a KerniQ runtime call.

## E2B Deferral Boundary

E2B remains later handoff-boundary planning. v2.3.0 does not call E2B, add E2B
integration, create an E2B sandbox, or add an E2B handoff.

## Later Milestone Boundary

The next recommended milestone is `v2.3.1 SQL Agent Local Emit-Only Contract`.

v2.3.1 must be prose-contract-only. It must not add code, schema, fixtures,
parser, runner, validator, CLI, SQL execution, DB connection, LangChain,
LlamaIndex, KerniQ, E2B, or runtime behavior.

## Public Claims

v2.3.0 may claim only that DHMS has opened planning for a future SQL Proposal
Agent Candidate emit-only proof line.

## Public Non-Claims

v2.3.0 does not claim:

* SQL agent implementation
* LangChain SQL Agent support
* LlamaIndex SQL Agent support
* real database agent support
* DB execution agent support
* SQL runner support
* SQL parser support
* SQL validator support
* ORM adapter support
* runtime integration
* SQL execution
* DB connection
* database integration
* schema introspection
* real schema access
* real data access
* database mutation
* sqlite/postgres/mysql client support
* credential access
* user-data access
* KerniQ integration
* KerniQ runtime call
* E2B integration
* E2B handoff
* production readiness
* implementation readiness
* runtime behavior

## Acceptance Checklist

* planning-only milestone
* docs-only milestone
* no SQL examples added
* no code added
* no schema added
* no JSON examples added
* no fixtures added
* no parser added
* no runner added
* no validator added
* no CLI added
* no quickstart added
* no adapter added
* no hook added
* no execution path added
* no SQL execution added
* no DB connection added
* no schema introspection added
* no real data access added
* no database mutation added
* no sqlite/postgres/mysql client added
* no ORM added
* no LangChain integration added
* no LlamaIndex integration added
* no KerniQ integration added
* no E2B integration added
* final verdict set correctly

## Final Verdict

`READY_FOR_V2_3_1_SQL_AGENT_LOCAL_EMIT_ONLY_CONTRACT`
