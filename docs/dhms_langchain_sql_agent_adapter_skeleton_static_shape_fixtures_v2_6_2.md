# DHMS LangChain SQL Agent Adapter Skeleton Static Shape Fixtures v2.6.2

## Title and Metadata

* Milestone: `v2.6.2 LangChain SQL Agent Adapter Skeleton Static Shape Fixtures`
* Status: static inert shape fixtures only
* Previous milestone: `v2.6.1 LangChain SQL Agent Emit-Only Adapter Skeleton Contract`
* Next milestone: `v2.6.3 LangChain SQL Agent Adapter Skeleton Non-Executing Shape Validation`

## Current Status

v2.6.2 adds static inert shape fixtures for a future `LangChain SQL Agent
Emit-Only Adapter Skeleton Candidate`.

The fixtures are documentation-level shape metadata only. They are not
executable examples, schemas, adapter skeleton code, LangChain callback/tool/API
examples, SQL examples, or runtime behavior.

## Scope

The scope is limited to:

* one static JSON fixture manifest
* one documentation file for the static shape fixtures
* package index link updates
* roadmap status updates

## Non-Scope

v2.6.2 does not add code, validators, schemas, parsers, runners, CLI commands,
source files, package/module files, adapter implementations, skeleton
implementations, hooks, execution paths, dependencies, package installs,
releases, or tags.

It does not install, import, invoke, adapt, wrap, callback into, or integrate
LangChain. It does not define LangChain tools. It does not use
SQLDatabaseToolkit as an integration or reference SQLDatabaseToolkit APIs as
executable examples. It does not run a LangChain SQL Agent, execute SQL,
connect to a database, introspect schemas, create a SQLite synthetic database,
use database clients, use an ORM, include real database/schema/table/column
names, include URLs, include file paths, include connection strings, include
credentials, include secrets, include tokens, include account/customer/user data,
include production data, call model APIs, call KerniQ, hand off to E2B, read
environment variables, or add network/subprocess/shell/command behavior.

## Relationship to v2.6.1

v2.6.1 defined the prose-only contract for the future skeleton candidate.
v2.6.2 adds static shape-review fixtures based on that contract.

v2.6.2 does not weaken the v2.6.1 contract and does not turn the contract into
implementation.

## Relationship to Frozen v2.5 Evidence Chain

v2.6.2 inherits the frozen v2.5 LangChain SQL Agent emit-only adapter boundary
evidence chain.

The frozen v2.5 result remains:

* `fixture_count=17`
* `accepted_for_dhms_evaluation=1`
* `fail_closed=16`
* `all_required_fields_present=true`
* `all_non_execution_assertions_present=true`
* `all_non_execution_assertions_false=true`
* `all_adapter_fixtures_inert=true`
* `all_fail_closed_reasons_covered_once=true`
* `sql_execution_attempts=0`
* `db_connections=0`
* `schema_introspection=0`
* `result_readbacks=0`
* `langchain_installs=0`
* `langchain_imports=0`
* `langchain_invocations=0`
* `langchain_integrations=0`
* `sql_database_toolkit_integrations=0`
* `model_api_calls=0`
* `credential_accesses=0`
* `user_data_accesses=0`
* `kerniq_runtime_calls=0`
* `e2b_handoffs=0`
* `runtime_behaviors=0`

## Static Shape Fixture Manifest

The manifest is:

`benchmarks/dhms_langchain_sql_agent_adapter_skeleton_shape_v0/shape_fixtures.json`

It contains exactly 17 static inert shape fixtures:

* 1 `ACCEPT_FOR_SHAPE_REVIEW`
* 16 `FAIL_CLOSED`

Each inherited v2.5 fail-closed category is covered exactly once.

## Manifest Fields

The manifest includes:

* `manifest_name`
* `manifest_version`
* `milestone`
* `contract_source`
* `fixture_count`
* `decision_counts`
* `fixtures_are_static_inert_shape_metadata_only`
* `non_execution_manifest_assertions`
* `fixtures`

All `non_execution_manifest_assertions` values are `false`.

## Fixture Fields

Each fixture includes:

* `fixture_id`
* `contract_subject`
* `fixture_kind`
* `shape_subject`
* `shape_surface`
* `observation_boundary`
* `emit_boundary`
* `executable_surface_status`
* `langchain_surface_status`
* `sql_database_toolkit_surface_status`
* `sql_text_status`
* `db_scope_status`
* `schema_scope_status`
* `result_scope_status`
* `model_provider_scope_status`
* `credential_scope_status`
* `user_data_scope_status`
* `runtime_scope_status`
* `framework_loop_status`
* `retry_loop_status`
* `expected_dhms_decision`
* `expected_fail_closed_reason`
* `non_execution_assertions`

All fixture `non_execution_assertions` values are `false`.

## Accepted Shape-Review Fixture

The accepted fixture is:

`skeleton_shape_accept_inert_documentation_boundary`

It is accepted only for shape review. It does not authorize execution,
implementation, source file creation, adapter creation, skeleton creation,
fixture validation behavior, LangChain integration, SQLDatabaseToolkit
integration, SQL execution, DB access, model API calls, KerniQ, E2B, or runtime
behavior.

## Fail-Closed Fixture Coverage

The 16 fail-closed fixtures cover these inherited v2.5 categories exactly once:

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

## Non-Execution Assertions

The manifest and every fixture assert `false` for source files, adapter
implementation, skeleton implementation, validators, schemas, CLI, parser,
runner, hooks, LangChain install/import/invocation/integration/wrapping,
LangChain callbacks/tools, SQLDatabaseToolkit integration, SQL execution, DB
connection, schema introspection, result readback, model API calls, credential
access, user-data access, KerniQ runtime calls, E2B handoffs, runtime behavior,
and execution authorization.

## Inert Content Rules

The fixtures use inert marker strings only. They do not contain executable SQL,
real SQL snippets, database names, schema names, table names, column names,
credentials, user data, file paths, URLs, import statements, package commands,
Python class/function/module examples, LangChain API examples,
SQLDatabaseToolkit API examples, model-provider API examples, or runtime
commands.

## Shape-Only Boundary

Shape means documentation-level metadata only. Shape fixtures may describe
future inert boundary categories and fail-closed expectations, but they do not
define schemas, source surfaces, runtime hooks, executable examples, commands,
or integrations.

## LangChain Boundary

LangChain is a named boundary subject only. v2.6.2 does not install, import,
invoke, adapt, wrap, callback into, define tools for, or integrate LangChain.

## SQLDatabaseToolkit Boundary

SQLDatabaseToolkit is a prohibited executable integration surface. v2.6.2 does
not import, instantiate, configure, adapt, call, or integrate
SQLDatabaseToolkit.

## DB Boundary

v2.6.2 does not connect to databases, create databases, use database clients,
use an ORM, inspect schemas, name real schemas/tables/columns, execute SQL, read
SQL results, or claim production DB safety.

## Model-Provider Boundary

v2.6.2 does not add model-provider clients, call model APIs, or integrate any
provider SDK.

## KerniQ/E2B Boundary

v2.6.2 does not call KerniQ, invoke KerniQ runtime behavior, hand off to E2B,
create E2B sandboxes, or claim KerniQ/E2B integration.

## Runtime Boundary

v2.6.2 does not add runtime behavior. It does not add network, subprocess,
shell, command, environment-variable, credential, user-data, adapter, hook,
source package, schema, validator, CLI, parser, runner, or execution-path
behavior.

## Later Validator Implications

v2.6.3 may add deterministic read-only validation for the v2.6.2 static shape
fixtures only.

v2.6.3 must not execute SQL, connect DB, inspect schemas, invoke LangChain,
import LangChain, install LangChain, use SQLDatabaseToolkit, call model APIs,
access credentials or user data, call KerniQ, hand off to E2B, add source files,
add adapter/skeleton implementation, add schema/parser/runner/CLI, or add
runtime behavior.

## Public Claims

v2.6.2 may claim:

* DHMS has added static inert shape fixtures for a future LangChain SQL Agent emit-only adapter skeleton candidate.
* The fixture manifest contains exactly 17 static shape fixtures.
* Exactly 1 fixture is `ACCEPT_FOR_SHAPE_REVIEW`.
* Exactly 16 fixtures are `FAIL_CLOSED`.
* Each inherited v2.5 fail-closed category is covered exactly once.
* The fixtures remain documentation-level, inert, non-executing shape metadata only.
* v2.6.2 adds no code, no source files, no skeleton implementation, no adapter implementation, no validators, no schemas, no LangChain integration, no SQLDatabaseToolkit integration, no SQL execution, no DB access, no model API calls, no KerniQ/E2B, and no runtime behavior.

## Public Non-Claims

v2.6.2 does not claim:

* LangChain integration
* LangChain SQL Agent support
* SQLDatabaseToolkit support
* adapter implementation
* adapter skeleton implementation
* source package support
* schema support
* validator support
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
* CLI support
* parser support
* runner support
* hook support
* execution authorization

## Next Milestone Boundary

The next milestone is:

`v2.6.3 LangChain SQL Agent Adapter Skeleton Non-Executing Shape Validation`

v2.6.3 may add deterministic read-only validation for the v2.6.2 static shape
fixtures only. It must not execute SQL, connect DB, inspect schemas, invoke
LangChain, import LangChain, install LangChain, use SQLDatabaseToolkit, call
model APIs, access credentials/user data, call KerniQ, hand off to E2B, add
source files, add adapter/skeleton implementation, add schema/parser/runner/CLI,
or add runtime behavior.

## Acceptance Checklist

* exactly 17 static inert shape fixtures added
* exactly 1 `ACCEPT_FOR_SHAPE_REVIEW`
* exactly 16 `FAIL_CLOSED`
* each inherited v2.5 fail-closed category covered exactly once
* all manifest non-execution assertions are false
* all fixture non-execution assertions are false
* no executable SQL
* no real DB/schema/table/column data
* no URLs, file paths, secrets, credentials, user data, or production data
* no LangChain executable API examples
* no SQLDatabaseToolkit executable API examples
* no model-provider API examples
* no runtime commands
* no code, source files, validators, schemas, parser, runner, CLI, adapter, skeleton, hook, or execution path added

## Final Verdict

`READY_FOR_V2_6_3_LANGCHAIN_SQL_AGENT_ADAPTER_SKELETON_NON_EXECUTING_SHAPE_VALIDATION`
