# DHMS LangChain SQL Agent Static Adapter Boundary Fixtures v2.5.2

## Title and Metadata

* Milestone: `v2.5.2 LangChain SQL Agent Static Adapter Boundary Fixtures`
* Manifest: `benchmarks/dhms_langchain_sql_agent_emit_only_adapter_v0/adapter_boundary_fixtures.json`
* Contract source: `docs/dhms_langchain_sql_agent_emit_only_adapter_contract_v2_5_1.md`
* Status: static inert fixtures only
* Previous milestone: `v2.5.1 LangChain SQL Agent Emit-Only Adapter Contract`
* Next milestone: `v2.5.3 LangChain SQL Agent Non-Executing Adapter Fixture Validation`

## Current Status

v2.5.2 adds static inert fixture coverage for the v2.5.1 LangChain SQL Agent
Emit-Only Adapter Contract. The fixtures describe the future LangChain SQL
Agent Emit-Only Adapter Candidate boundary as inert metadata only.

v2.5.2 does not add code, validators, schemas, parser, runner, CLI,
dependencies, LangChain install/import/invocation/integration,
SQLDatabaseToolkit integration, SQL execution, DB connection, schema
introspection, model API call, KerniQ, E2B, release, tag, or runtime behavior.

## Scope

The scope is limited to:

* one static inert fixture manifest
* this documentation page
* package index links
* roadmap status update

The fixture manifest contains exactly 17 fixtures: one
`ACCEPT_FOR_DHMS_EVALUATION` fixture and 16 `FAIL_CLOSED` fixtures.

## Non-Scope

v2.5.2 does not add:

* code
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
* SQLDatabaseToolkit support
* SQL execution
* executable SQL
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

## Relationship to v2.5.1

v2.5.1 defined the prose-only contract for the future LangChain SQL Agent
Emit-Only Adapter Candidate. v2.5.2 provides static inert fixtures for that
contract without implementing the adapter, invoking LangChain, using
SQLDatabaseToolkit, executing SQL, connecting to a database, inspecting schemas,
or calling model APIs.

## Fixture Manifest Summary

Manifest path:

`benchmarks/dhms_langchain_sql_agent_emit_only_adapter_v0/adapter_boundary_fixtures.json`

The manifest declares:

* `manifest_name=DHMS LangChain SQL Agent Emit-Only Adapter Static Boundary Fixtures`
* `manifest_version=v2.5.2`
* `fixture_count=17`
* `ACCEPT_FOR_DHMS_EVALUATION=1`
* `FAIL_CLOSED=16`
* `fixtures_are_static_inert_metadata_only=true`

## Accepted Fixture Boundary

The accepted fixture is:

`langchain_emit_only_accept_inert_adapter_metadata`

It represents inert adapter metadata observed before execution. It has no
executable tool input, no SQL execution scope, no database connection scope, no
schema introspection scope, no result readback scope, no credential scope, no
user data scope, no mutation intent, no framework loop, and no retry loop.

The accepted fixture is accepted for DHMS evaluation only. It does not authorize
execution.

## Fail-Closed Fixture Coverage

The 16 `FAIL_CLOSED` fixtures cover each v2.5.1 fail-closed category exactly
once:

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

Each category is represented as synthetic inert metadata only.

## Inert Metadata Boundary

Fixture values are inert metadata only. Static fixtures do not authorize
execution. Static fixtures are not executable tool input. Static fixtures are
not adapter implementation.

The manifest includes no executable SQL, executable tool payload, real table
names, real database names, connection strings, credentials, URLs, file paths,
user data, package commands, Python examples, or runtime invocation strings.

## LangChain Boundary

LangChain remains an untrusted third-party proposal/runtime subject. v2.5.2
does not install, import, invoke, adapt, or integrate LangChain. The fixtures
use only synthetic inert subject markers.

## SQLDatabaseToolkit Boundary

SQLDatabaseToolkit appears only as a prohibited boundary concept through inert
fixture metadata and documentation. v2.5.2 does not support, call, import, or
integrate SQLDatabaseToolkit.

## DB Boundary

v2.5.2 does not connect to a database, inspect schemas, execute SQL, read
results, mutate data, create synthetic databases, or use database clients or
ORMs.

## Model-Provider Boundary

The model-provider subject is represented only by a synthetic inert marker.
v2.5.2 does not add provider clients and does not call model APIs.

## KerniQ/E2B Boundary

v2.5.2 does not call KerniQ and does not hand off to E2B. KerniQ and E2B remain
out of scope.

## Next Milestone Boundary

The next milestone is:

`v2.5.3 LangChain SQL Agent Non-Executing Adapter Fixture Validation`

v2.5.3 may add deterministic read-only validation for the v2.5.2 static inert
fixtures. It must not add SQL execution, DB connection, schema introspection,
framework runtime, LangChain import/invocation/integration, SQLDatabaseToolkit
usage, model API call, KerniQ, E2B, release, tag, or runtime behavior.

## Public Claims

v2.5.2 may claim:

* static inert fixtures exist for the future LangChain SQL Agent emit-only
  adapter boundary
* fixture count is exactly 17
* one fixture is `ACCEPT_FOR_DHMS_EVALUATION`
* 16 fixtures are `FAIL_CLOSED`
* each v2.5.1 fail-closed category is covered exactly once
* fixture values are inert metadata only
* static fixtures do not authorize execution

## Public Non-Claims

v2.5.2 does not claim:

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

* v2.5.2 is static inert fixtures only
* fixture count is exactly 17
* exactly one fixture is `ACCEPT_FOR_DHMS_EVALUATION`
* exactly 16 fixtures are `FAIL_CLOSED`
* each v2.5.1 fail-closed category is covered exactly once
* all fixture IDs are unique
* all fixture payload values are inert metadata
* all non-execution assertions are present and false
* no code added
* no validator added
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
* package index links this document and manifest
* roadmap marks v2.5.2 and points to v2.5.3

## Final Verdict

`READY_FOR_V2_5_3_LANGCHAIN_SQL_AGENT_NON_EXECUTING_ADAPTER_FIXTURE_VALIDATION`
