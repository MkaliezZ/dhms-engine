# DHMS LangChain SQL Agent Emit-Only Adapter Skeleton Contract v2.6.1

## Title and Metadata

* Milestone: `v2.6.1 LangChain SQL Agent Emit-Only Adapter Skeleton Contract`
* Status: prose-contract-only
* Previous milestone: `v2.6.0 LangChain SQL Agent Emit-Only Adapter Skeleton Planning`
* Next milestone: `v2.6.2 LangChain SQL Agent Adapter Skeleton Static Shape Fixtures`

## Current Status

v2.6.1 converts the v2.6.0 planning boundary into a prose-only contract for a
future `LangChain SQL Agent Emit-Only Adapter Skeleton Candidate`.

This milestone does not implement skeleton code, source files, adapter behavior,
LangChain behavior, SQLDatabaseToolkit behavior, SQL behavior, DB behavior,
model API behavior, KerniQ, E2B, or runtime behavior.

## Scope

The scope is limited to:

* defining the future skeleton candidate contract boundary
* preserving the frozen v2.5 non-execution evidence chain
* defining roles, invariants, and prose-only decision rules
* defining later fixture and validator implications
* updating the package index and roadmap

## Non-Scope

v2.6.1 does not add code, fixtures, validators, schemas, parsers, runners, CLI
commands, dependencies, source files, packages, modules, adapter
implementations, skeleton implementations, hooks, execution paths, releases, or
tags.

It does not install, import, invoke, adapt, wrap, callback into, or integrate
LangChain. It does not define LangChain tools. It does not use
SQLDatabaseToolkit as an integration. It does not run a LangChain SQL Agent. It
does not execute SQL, connect to a database, introspect schemas, create a SQLite
synthetic database, use sqlite3/sqlalchemy/psycopg/mysql clients, use an ORM,
call model APIs, add OpenAI/Claude/DeepSeek/Qwen/GLM/Kimi clients, call KerniQ,
hand off to E2B, read environment variables, access credentials, access user
data, or add network/subprocess/shell/command behavior.

## Relationship to v2.6.0

v2.6.0 opened planning for a future skeleton candidate. v2.6.0 defined
skeleton as a future conceptual boundary subject only.

v2.6.1 converts that planning into a prose-only contract. v2.6.1 does not
implement skeleton code, source files, adapter behavior, LangChain behavior,
SQLDatabaseToolkit behavior, SQL behavior, DB behavior, model API behavior,
KerniQ, E2B, or runtime behavior.

## Relationship to Frozen v2.5 Evidence Chain

v2.5 froze a LangChain SQL Agent emit-only adapter boundary evidence chain. The
frozen v2.5 result is:

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

v2.6.1 inherits and must not weaken the v2.5 frozen non-execution boundary.

## Contract Subject

The contract subject is:

`LangChain SQL Agent Emit-Only Adapter Skeleton Candidate`

## Contract Purpose

The contract defines the future candidate shape boundary before any fixture or
implementation work. It makes clear that future skeleton shape review is
possible without granting runtime authority.

## Definition of Skeleton Under This Contract

Skeleton means a future shape-only boundary subject.

It is not:

* source code
* adapter implementation
* adapter skeleton implementation
* LangChain wrapper
* LangChain callback
* LangChain tool
* LangChain agent
* SQLDatabaseToolkit connector
* database connector
* SQL runner
* model client
* runtime bridge
* CLI
* schema
* parser
* runner
* hook
* execution path
* package/module/source surface

## Contract Roles

* DHMS boundary evaluator: evaluates inert proposal metadata before any execution.
* LangChain SQL Agent framework subject: untrusted third-party proposal/runtime subject.
* Skeleton candidate: future shape-only non-executing boundary subject.
* SQLDatabaseToolkit: prohibited executable integration surface.
* Model provider: untrusted proposal source, not called.
* Database/tool runtime: forbidden subject in this contract.
* Evidence artifact: future inert review material only.

## Skeleton Boundary Invariants

The future skeleton candidate must preserve:

* observation-before-execution
* emit-only metadata
* fail-closed by default
* no executable tool input
* no executable SQL
* no DB connection
* no schema introspection
* no result readback
* no model API call
* no credentials
* no user data
* no framework loop management
* no retry loop management
* no runtime authority
* no execution authorization

## Observation-Before-Execution Contract

Any later milestone must fail closed if:

* proposed action is not observable before execution
* hidden framework execution is detected or cannot be ruled out
* executable tool input is present
* framework loop is unbounded
* retry/self-correction loop is unbounded
* evidence capture is missing
* adapter boundary is missing
* unsupported LangChain tool format is encountered
* unsupported model behavior is encountered

## Emit-Only Metadata Contract

The future skeleton candidate may only describe inert DHMS proposal metadata
shape.

It must not:

* emit executable tool input
* emit executable SQL
* transform metadata into executable SQL/tool calls
* carry DB credentials
* carry user data
* carry connection strings
* carry real schemas
* carry real table names
* carry real column names
* carry URLs
* carry file paths
* carry secrets
* authorize execution

## Non-Execution Contract

The contract preserves a default of no execution, no authorization, and no
runtime handoff. Any material that implies execution, implementation, runtime
authority, DB access, SQL execution, model-provider calls, credentials, user
data, KerniQ, E2B, or framework runtime behavior fails closed.

## Prohibited Implementation Surfaces

The following surfaces are prohibited:

* source files
* package/module surfaces
* adapter implementation
* adapter skeleton implementation
* LangChain wrappers, callbacks, tools, or agents
* SQLDatabaseToolkit connectors
* database connectors
* SQL runners
* model clients
* runtime bridges
* parser, runner, hook, or CLI surfaces
* dependency or package changes

## Shape-Only Contract Language

Shape means documentation-level structure only. Shape may describe future inert
metadata boundaries, categories, roles, and fail-closed expectations.

Shape must not define:

* Python classes
* functions
* modules
* package layout
* import paths
* callback methods
* LangChain APIs
* SQLDatabaseToolkit APIs
* JSON schemas
* executable examples
* runnable commands
* CLI interfaces
* runtime hooks

## Inherited v2.5 Fail-Closed Taxonomy

The following exact categories carry forward:

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

## Contract Decision Rules

Prose-only decision rules:

* `ACCEPT_FOR_SHAPE_REVIEW` may apply only to inert, documentation-level skeleton shape material that preserves all non-execution invariants.
* `FAIL_CLOSED` must apply to anything that implies implementation, runtime execution, LangChain import/invocation/integration, SQLDatabaseToolkit usage, SQL execution, DB access, schema introspection, result readback, model API call, credential/user-data access, KerniQ, E2B, or runtime behavior.
* `ACCEPT_FOR_SHAPE_REVIEW` does not authorize execution, implementation, adapter creation, source file creation, fixture creation, validator creation, or runtime integration.

## Evidence Obligations for Later Milestones

Any later skeleton-related milestone must prove:

* no source files
* no adapter implementation
* no skeleton implementation
* no LangChain install/import/invocation/integration
* no SQLDatabaseToolkit integration
* no SQL execution
* no DB connection
* no schema introspection
* no result readback
* no model API calls
* no credential access
* no user data access
* no KerniQ runtime call
* no E2B handoff
* no runtime behavior
* no execution authorization

## LangChain Boundary

LangChain is a named boundary subject only. v2.6.1 does not install, import,
invoke, adapt, wrap, callback into, tool-call through, define tools for, or
integrate LangChain.

## SQLDatabaseToolkit Boundary

SQLDatabaseToolkit is a prohibited executable integration surface. v2.6.1 does
not import, instantiate, configure, adapt, call, or integrate
SQLDatabaseToolkit.

## DB Boundary

v2.6.1 does not connect to databases, create databases, use sqlite3/sqlalchemy/
psycopg/mysql clients, use an ORM, inspect schemas, read schema names, read real
table or column names, execute SQL, read SQL results, or claim production DB
safety.

## Model-Provider Boundary

v2.6.1 does not add OpenAI, Claude, DeepSeek, Qwen, GLM, Kimi, or other
model-provider clients. It does not call model APIs and does not integrate any
provider SDK.

## KerniQ/E2B Boundary

v2.6.1 does not call KerniQ, invoke KerniQ runtime behavior, hand off to E2B,
create E2B sandboxes, or claim KerniQ/E2B integration.

## Runtime Boundary

v2.6.1 does not add runtime behavior. It does not add network, subprocess,
shell, command, environment-variable, credential, user-data, adapter, hook,
source package, or execution-path behavior.

## Later Fixture Implications

v2.6.2 may add static shape fixtures only. v2.6.2 must not add code,
validators, schemas, parser, runner, CLI, source files, adapter implementation,
skeleton implementation, dependencies, LangChain install/import/invocation/
integration, SQLDatabaseToolkit usage, SQL execution, DB connection, schema
introspection, model API call, KerniQ, E2B, release, tag, or runtime behavior.

## Later Validator Implications

v2.6.3 may add deterministic read-only validation for the v2.6.2 static shape
fixtures only. v2.6.3 must not execute SQL, connect DB, inspect schemas, invoke
LangChain, use SQLDatabaseToolkit, call model APIs, access credentials/user
data, call KerniQ, hand off to E2B, or add runtime behavior.

## Public Claims

v2.6.1 may claim:

* DHMS has defined a prose-only contract for a future LangChain SQL Agent emit-only adapter skeleton candidate.
* The contract inherits the frozen v2.5 non-execution evidence chain.
* The skeleton remains a future shape-only boundary subject.
* v2.6.1 adds no code, no source files, no skeleton implementation, no adapter implementation, no fixtures, no validators, no LangChain integration, no SQLDatabaseToolkit integration, no SQL execution, no DB access, no model API calls, no KerniQ/E2B, and no runtime behavior.

## Public Non-Claims

v2.6.1 does not claim:

* LangChain integration
* LangChain SQL Agent support
* SQLDatabaseToolkit support
* adapter implementation
* adapter skeleton implementation
* source package support
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

`v2.6.2 LangChain SQL Agent Adapter Skeleton Static Shape Fixtures`

v2.6.2 may add static shape fixtures only. It must not add code, validators,
schemas, parser, runner, CLI, dependencies, source files, adapter
implementation, skeleton implementation, LangChain install/import/invocation/
integration, SQLDatabaseToolkit usage, SQL execution, DB connection, schema
introspection, model API call, KerniQ, E2B, release, tag, or runtime behavior.

## Acceptance Checklist

* v2.6.1 is prose-contract-only
* no code added
* no source files or source packages added
* no fixtures added
* no validators added
* no schema added
* no parser, runner, CLI, adapter, skeleton, or hook added
* no LangChain install/import/invocation/integration added
* no SQLDatabaseToolkit integration added
* no SQL execution or DB integration added
* no model-provider integration added
* no KerniQ/E2B integration added
* no runtime behavior added
* v2.6.0 planning status preserved
* v2.5 frozen evidence chain remains unchanged
* package index links this contract document
* roadmap marks v2.6.1 and points to v2.6.2

## Final Verdict

`READY_FOR_V2_6_2_LANGCHAIN_SQL_AGENT_ADAPTER_SKELETON_STATIC_SHAPE_FIXTURES`
