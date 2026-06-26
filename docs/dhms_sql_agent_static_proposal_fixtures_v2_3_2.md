# DHMS SQL Agent Static Proposal Fixtures v2.3.2

## Metadata

* Milestone: `v2.3.2 SQL Agent Static Proposal Fixtures`
* Repository branch: `agent-harness-v1`
* Prior milestone: `v2.3.1 SQL Agent Local Emit-Only Contract`
* Next recommended milestone: `v2.3.3 SQL Agent Non-Executing Fixture Validation`

## Current Status

v2.3.2 adds static inert fixtures only for `SQL Proposal Agent Candidate`.
It does not add code, schema, parser, runner, validator, CLI, SQL execution, DB
connection, LangChain, LlamaIndex, KerniQ, E2B, or runtime behavior.

## Scope

The scope is limited to one static fixture manifest and this documentation.
Fixtures are inert metadata only and are intended for later non-executing
validation.

## Non-Scope

v2.3.2 does not add executable SQL statements, real SQL examples, real table
names, real column names, real database names, URLs, file paths, credentials,
user data, production data, parser behavior, runner behavior, validator
behavior, CLI behavior, adapter behavior, hook behavior, execution path, DB
connection, database integration, schema introspection, real schema access,
real data access, database mutation, sqlite/postgres/mysql clients, ORM,
LangChain, LlamaIndex, SQLDatabaseToolkit, KerniQ, E2B, release, or tag.

## Relationship to v2.3.1

v2.3.1 defined the prose-only emit-only contract. v2.3.2 instantiates static
inert fixture examples of that contract without modifying the v2.3.1 contract
and without adding validation behavior.

## Fixture Manifest

Fixture manifest:

`benchmarks/dhms_sql_agent_local_emit_only_v0/proposals.json`

The manifest contains exactly 10 fixtures:

* 1 `ACCEPT_FOR_DHMS_EVALUATION`
* 9 `FAIL_CLOSED`

## Accepted Fixture Boundary

The accepted fixture uses `dry_run=true`, empty `db_connection_scope`, empty
`credential_scope`, empty `user_data_scope`, synthetic or declared-only
`schema_source`, `runtime_target=no-runtime`, inert `sql_candidate` metadata,
synthetic `declared_tables`, synthetic `declared_columns`, and
`expected_fail_closed_reason=null`.

Acceptance for DHMS evaluation is not SQL execution approval.

## Fail-Closed Fixture Coverage

The fail-closed fixtures cover:

* `dry_run_not_true`
* `db_connection_scope_non_empty`
* `credential_scope_non_empty`
* `user_data_scope_non_empty`
* `runtime_target_not_no_runtime`
* `schema_source_real_schema_claim`
* `sql_execution_requested`
* `database_mutation_without_safe_boundary`
* `third_party_or_external_runtime_marker`

Third-party or external runtime markers are inert text only.

## Inert SQL Metadata Boundary

Fixtures are not executable inputs. Fixtures do not contain real SQL statements,
real schema, real data, credentials, or user data. `sql_candidate` values are
inert metadata labels only.

## DB Boundary

v2.3.2 does not connect to any database, execute SQL, inspect schemas, access
real schemas, read real data, mutate databases, use sqlite/postgres/mysql
clients, use ORM, access credentials, or access user data.

## LangChain / LlamaIndex Boundary

v2.3.2 does not use LangChain, LlamaIndex, SQLDatabaseToolkit, SQL agent
runtime, provider SDKs, agent SDKs, or runtime adapters. Markers in fixtures
are inert fail-closed text only.

## KerniQ Boundary

KerniQ remains deferred. v2.3.2 does not install KerniQ, run KerniQ, invoke
KerniQ, integrate KerniQ, or add a KerniQ runtime call. Any KerniQ marker in a
fixture is inert fail-closed text only.

## E2B Boundary

E2B remains later handoff-boundary planning. v2.3.2 does not call E2B, add E2B
integration, create an E2B sandbox, or add an E2B handoff. Any E2B marker in a
fixture is inert fail-closed text only.

## Later Milestone Boundary

The next recommended milestone is `v2.3.3 SQL Agent Non-Executing Fixture
Validation`.

v2.3.3 may add deterministic read-only validation only. v2.3.3 must not add SQL
execution, DB connection, schema introspection, parser-triggered execution,
runner behavior, CLI, LangChain, LlamaIndex, KerniQ, E2B, or runtime behavior.

## Public Claims

v2.3.2 may claim only that DHMS includes static inert fixtures for the future
SQL Proposal Agent Candidate emit-only contract.

## Public Non-Claims

v2.3.2 does not claim:

* SQL agent implementation
* SQL execution
* executable SQL support
* real SQL examples
* DB connection
* database integration
* schema introspection
* real schema access
* real data access
* database mutation
* sqlite/postgres/mysql client support
* ORM support
* LangChain integration
* LlamaIndex integration
* SQLDatabaseToolkit integration
* SQL agent runtime
* parser behavior
* runner behavior
* validator behavior
* CLI behavior
* KerniQ integration
* KerniQ runtime call
* E2B integration
* E2B handoff
* production readiness
* runtime behavior

## Acceptance Checklist

* static fixtures only
* docs only except fixture JSON
* exactly 10 fixtures
* exactly 1 `ACCEPT_FOR_DHMS_EVALUATION`
* exactly 9 `FAIL_CLOSED`
* all fixtures inert metadata only
* no SQL statements
* no real SQL examples
* no real table names
* no real column names
* no real database names
* no URLs
* no file paths
* no credentials
* no user data
* no production data
* no code added
* no schema added
* no parser added
* no runner added
* no validator added
* no CLI added
* no execution path added
* no SQL execution added
* no DB integration added
* no LangChain integration added
* no LlamaIndex integration added
* no KerniQ integration added
* no E2B integration added
* final verdict set correctly

## Final Verdict

`READY_FOR_V2_3_3_SQL_AGENT_NON_EXECUTING_FIXTURE_VALIDATION`
