# DHMS LangChain SQL Agent Emit-Only Adapter Skeleton Planning v2.6.0

## Title and Metadata

* Milestone: `v2.6.0 LangChain SQL Agent Emit-Only Adapter Skeleton Planning`
* Status: planning-only
* Previous milestone: `v2.5.4.1 README Current Status Sync`
* Next milestone: `v2.6.1 LangChain SQL Agent Emit-Only Adapter Skeleton Contract`

## Current Status

v2.6.0 opens planning for a future `LangChain SQL Agent Emit-Only Adapter
Skeleton Candidate`.

This milestone is documentation-only. It does not implement a skeleton, create
adapter source files, import LangChain, invoke LangChain, connect to a database,
execute SQL, call model APIs, call KerniQ, hand off to E2B, or add runtime
behavior.

## Scope

The scope is limited to:

* planning the future adapter skeleton boundary
* defining what "skeleton" means in this milestone
* preserving the frozen v2.5 non-execution evidence chain
* defining evidence obligations for later skeleton milestones
* updating the package index and roadmap

## Non-Scope

v2.6.0 does not add code, fixtures, validators, schemas, parsers, runners, CLI
commands, dependencies, source packages, adapter implementations, skeleton
implementations, hooks, execution paths, releases, or tags.

It does not install, import, invoke, adapt, or integrate LangChain. It does not
use SQLDatabaseToolkit as an integration. It does not run a LangChain SQL Agent.
It does not execute SQL, connect to a database, introspect schemas, create a
SQLite synthetic database, use sqlite3/sqlalchemy/psycopg/mysql clients, use an
ORM, call model APIs, add OpenAI/Claude/DeepSeek/Qwen/GLM/Kimi clients, call
KerniQ, hand off to E2B, read environment variables, access credentials, access
user data, or add network/subprocess/shell/command behavior.

## Relationship to v2.5.0-v2.5.4.1

v2.5.0 planned the future LangChain SQL Agent emit-only adapter boundary.
v2.5.1 converted it into a prose-only contract. v2.5.2 added 17 static inert
adapter-boundary fixtures. v2.5.3 added deterministic read-only validation.
v2.5.4 froze the validation result. v2.5.4.1 synchronized README public status.

v2.6.0 starts planning for a future adapter skeleton candidate without changing
the frozen v2.5 evidence chain.

## Why Skeleton Planning Starts After v2.5 Freeze

The v2.5 chain established a frozen, non-executing evidence baseline before any
skeleton-shaped work is considered. Planning after the freeze keeps the order
explicit: evidence first, boundary definition second, implementation only if a
later phase explicitly authorizes it.

## Definition of Skeleton in v2.6.0

In v2.6.0, "skeleton" means a future candidate boundary concept only.

It is not:

* source code
* adapter implementation
* LangChain wrapper
* LangChain callback
* LangChain tool
* SQLDatabaseToolkit integration
* DB connector
* SQL runner
* model client
* runtime bridge
* CLI
* schema
* parser
* runner
* hook
* execution path

## Future Skeleton Candidate Subject

The future candidate subject is:

`LangChain SQL Agent Emit-Only Adapter Skeleton Candidate`

## Future Skeleton Boundary Goals

If later explicitly approved, the future candidate may only aim to:

* represent a non-executing adapter boundary shape
* preserve observation-before-execution requirements
* preserve emit-only metadata constraints
* preserve fail-closed behavior for unsupported or executable surfaces
* preserve v2.5 frozen non-execution evidence
* make future review of adapter skeleton shape possible without granting runtime authority

## Future Skeleton Non-Goals

The future candidate must not aim to:

* execute LangChain
* import LangChain
* call LangChain APIs
* connect to SQLDatabaseToolkit
* connect to a database
* inspect schemas
* execute SQL
* read SQL results
* call model APIs
* access credentials
* access user data
* manage framework loops
* manage retry loops
* authorize execution
* provide production readiness

## Observation-Before-Execution Planning Boundary

Any later skeleton milestone must preserve:

* DHMS sees proposed action before execution
* unobserved runtime behavior fails closed
* executable tool input fails closed
* hidden framework execution fails closed
* unbounded framework loops fail closed
* unbounded retry/self-correction loops fail closed
* evidence capture remains deterministic and non-executing

## Emit-Only Planning Boundary

Any later skeleton milestone must preserve:

* only inert DHMS proposal metadata may be emitted
* emitted metadata does not authorize execution
* metadata must not be transformable into executable SQL or tool calls
* metadata must not contain DB credentials, user data, connection strings, real schemas, real tables, real columns, URLs, file paths, or secrets

## Non-Execution Requirements

Any future skeleton-related milestone must keep execution at zero unless a later
prompt explicitly authorizes a constrained proof path. For v2.6.0, all execution
and integration counts remain zero by definition.

## Inherited v2.5 Fail-Closed Taxonomy

The following v2.5 fail-closed categories carry forward:

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

## Evidence Obligations for Any Later Skeleton Milestone

Any later skeleton-related milestone must prove:

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

## Prohibited Implementation Surfaces

The following surfaces remain prohibited in v2.6.0:

* adapter source files
* skeleton source files
* LangChain wrappers, callbacks, tools, or agents
* SQLDatabaseToolkit connectors
* database connectors
* SQL runners
* model clients
* runtime bridges
* parser, runner, hook, or CLI surfaces
* dependency or package changes

## LangChain Boundary

LangChain is a named boundary subject only. v2.6.0 does not install, import,
invoke, adapt, wrap, callback into, tool-call through, or integrate LangChain.

## SQLDatabaseToolkit Boundary

SQLDatabaseToolkit is a prohibited integration surface. v2.6.0 does not import,
instantiate, configure, adapt, or call SQLDatabaseToolkit.

## DB Boundary

v2.6.0 does not connect to databases, create databases, use sqlite3/sqlalchemy/
psycopg/mysql clients, inspect schemas, read schema names, read real table or
column names, execute SQL, read SQL results, or claim production DB safety.

## Model-Provider Boundary

v2.6.0 does not add OpenAI, Claude, DeepSeek, Qwen, GLM, Kimi, or other
model-provider clients. It does not call model APIs and does not integrate any
provider SDK.

## KerniQ/E2B Boundary

v2.6.0 does not call KerniQ, invoke KerniQ runtime behavior, hand off to E2B,
create E2B sandboxes, or claim KerniQ/E2B integration.

## Runtime Boundary

v2.6.0 does not add runtime behavior. It does not add network, subprocess,
shell, command, environment-variable, credential, user-data, adapter, hook, or
execution-path behavior.

## Proposed v2.6 Evidence Ladder

The conservative future sequence is:

* v2.6.0 LangChain SQL Agent Emit-Only Adapter Skeleton Planning
* v2.6.1 LangChain SQL Agent Emit-Only Adapter Skeleton Contract
* v2.6.2 LangChain SQL Agent Adapter Skeleton Static Shape Fixtures
* v2.6.3 LangChain SQL Agent Adapter Skeleton Non-Executing Shape Validation
* v2.6.4 LangChain SQL Agent Adapter Skeleton Result Review and Freeze
* v2.6.4.1 README Current Status Sync

This proposed ladder is planning only and does not authorize those milestones to
add code unless a later prompt explicitly permits it. For now, v2.6.1 must be
prose-contract-only.

## Public Claims

v2.6.0 may claim:

* DHMS has started planning a future LangChain SQL Agent emit-only adapter skeleton candidate.
* The planning builds on the frozen v2.5 evidence chain.
* The skeleton is only a future conceptual boundary subject in v2.6.0.
* v2.6.0 adds no code, no skeleton, no adapter implementation, no LangChain integration, no SQL execution, no DB access, no model API calls, no KerniQ/E2B, and no runtime behavior.

## Public Non-Claims

v2.6.0 does not claim:

* LangChain integration
* LangChain SQL Agent support
* SQLDatabaseToolkit support
* adapter implementation
* adapter skeleton implementation
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
* parser/runner/hook support
* source package support

## Next Milestone Boundary

The next milestone is:

`v2.6.1 LangChain SQL Agent Emit-Only Adapter Skeleton Contract`

v2.6.1 must be prose-contract-only. It must not add code, fixtures, validators,
schemas, parser, runner, CLI, dependencies, source files, adapter
implementation, skeleton implementation, LangChain install/import/invocation/
integration, SQLDatabaseToolkit usage, SQL execution, DB connection, schema
introspection, model API call, KerniQ, E2B, release, tag, or runtime behavior.

## Acceptance Checklist

* v2.6.0 is planning-only
* no code added
* no source package added
* no fixture changed
* no validator changed
* no schema added
* no parser, runner, CLI, adapter, skeleton, or hook added
* no LangChain install/import/invocation/integration added
* no SQLDatabaseToolkit integration added
* no SQL execution or DB integration added
* no model-provider integration added
* no KerniQ/E2B integration added
* no runtime behavior added
* v2.5 frozen evidence chain remains unchanged
* package index links this planning document
* roadmap marks v2.6.0 and points to v2.6.1

## Final Verdict

`READY_FOR_V2_6_1_LANGCHAIN_SQL_AGENT_EMIT_ONLY_ADAPTER_SKELETON_CONTRACT`
