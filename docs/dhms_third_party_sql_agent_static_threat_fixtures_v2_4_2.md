# DHMS Third-Party SQL Agent Static Threat Fixtures v2.4.2

## Metadata

* Milestone: `v2.4.2 Third-Party SQL Agent Static Threat Fixtures`
* Fixture manifest: `benchmarks/dhms_third_party_sql_agent_threat_boundary_v0/threat_fixtures.json`
* Prior milestone: `v2.4.1 Third-Party SQL Agent Threat Boundary Contract`
* Status: static inert fixtures only

## Current Status

v2.4.2 adds static inert threat fixtures for the third-party SQL Agent
threat-boundary line.

This milestone adds JSON fixture data and documentation only. It does not add
code, validators, schemas, parser behavior, runner behavior, CLI behavior,
dependencies, package installs, SQL execution, DB connection, framework
integration, model API calls, KerniQ integration, E2B integration, release, tag,
or runtime behavior.

## Scope

The v2.4.2 scope is limited to:

* create a static inert threat fixture manifest
* include exactly 16 fixtures
* include exactly 1 `ACCEPT_FOR_DHMS_EVALUATION` fixture
* include exactly 15 `FAIL_CLOSED` fixtures
* cover all required third-party SQL Agent fail-closed categories
* keep fixture values inert metadata only
* document the fixture boundary
* update package index and roadmap links

## Non-Scope

v2.4.2 does not add:

* code
* validator
* schema
* parser
* runner
* CLI
* adapter
* hook
* execution path
* dependency changes
* package installs
* LangChain install, import, invocation, or integration
* LlamaIndex install, import, invocation, or integration
* SQLDatabaseToolkit usage
* SQL agent runtime
* SQL execution
* executable SQL statements
* DB connection
* schema introspection
* real schema or real data
* database mutation
* SQLite synthetic DB
* DB client or ORM
* model API call
* DeepSeek/Qwen/GLM/Kimi/OpenAI/Claude client
* KerniQ integration or runtime call
* E2B integration or handoff
* network/env/credential/user-data access
* subprocess, shell, or command execution
* release
* tag

## Relationship to v2.4.1

v2.4.1 defined a prose-only contract for reviewing third-party SQL Agent threat
boundaries.

v2.4.2 turns that prose contract into static inert threat fixtures. The fixtures
are not executable, do not include SQL statements, do not include real database
metadata, and do not invoke any framework or model provider.

## Fixture Manifest Summary

Manifest:

`benchmarks/dhms_third_party_sql_agent_threat_boundary_v0/threat_fixtures.json`

Summary:

* fixture count: 16
* `ACCEPT_FOR_DHMS_EVALUATION`: 1
* `FAIL_CLOSED`: 15
* static inert metadata only
* no executable SQL
* no real table names
* no real column names
* no real database names
* no URLs
* no file paths
* no credentials
* no user data
* no production data
* no SDK calls
* no imports
* no runtime targets
* no framework invocation

## Accepted Fixture Boundary

The accepted fixture uses:

* `expected_dhms_decision=ACCEPT_FOR_DHMS_EVALUATION`
* `expected_fail_closed_reason=null`
* `proposal_shape=inert_metadata_proposal`
* `tool_input_status=none`
* `observed_action_stage=pre_execution_observed`
* empty DB, schema, SQL, result readback, credential, and user-data scopes
* runtime/framework/model assertions all false

Acceptance means only that the inert metadata may be evaluated by DHMS. It does
not authorize execution or runtime integration.

## Fail-Closed Fixture Coverage

The 15 fail-closed fixtures cover:

* `third_party_runtime_unobserved`
* `executable_tool_input_detected`
* `db_connection_requested`
* `schema_introspection_requested`
* `sql_execution_requested`
* `credential_scope_non_empty`
* `user_data_scope_non_empty`
* `mutation_or_write_intent`
* `framework_tool_loop_unbounded`
* `retry_loop_unbounded`
* `result_readback_requested`
* `runtime_adapter_missing`
* `evidence_capture_missing`
* `unsupported_model_behavior`
* `unsupported_domestic_llm_tool_format`

Each fail-closed fixture uses inert markers only and does not contain executable
tool payloads or SQL statements.

## Inert Metadata Boundary

The fixture manifest is JSON-only static metadata. Fixture values are not
commands, SQL statements, framework calls, model calls, DB connection strings,
URLs, file paths, credentials, or user data.

## LangChain/LlamaIndex Boundary

v2.4.2 does not install, import, invoke, adapt, or integrate LangChain or
LlamaIndex.

The fixture manifest records only generic third-party SQL Agent threat-boundary
subjects and non-execution assertions.

## Domestic LLM Boundary

Future domestic LLM comparison may discuss provider-specific behavior as a
threat-boundary subject only.

v2.4.2 does not add DeepSeek, Qwen, GLM, Kimi, OpenAI, Claude, or other model
clients. It does not add API calls, credentials, SDKs, adapters, benchmarks, or
runtime integration.

## DB Boundary

v2.4.2 adds no database capability:

* no SQL execution
* no DB connection
* no schema introspection
* no real schema
* no real data
* no database mutation
* no SQLite synthetic DB
* no DB client
* no ORM

## KerniQ/E2B Boundary

v2.4.2 does not integrate with KerniQ or E2B.

It does not call a KerniQ runtime and does not hand off to E2B.

## Next Milestone Boundary

The next milestone is:

`v2.4.3 Third-Party SQL Agent Non-Executing Threat Fixture Validation`

v2.4.3 may add deterministic read-only validation for these static inert
fixtures. v2.4.3 must not add SQL execution, DB connection, schema
introspection, framework runtime, model API call, KerniQ, E2B, release, tag, or
runtime behavior.

## Public Claims

v2.4.2 claims only that DHMS has static inert threat fixtures for the
third-party SQL Agent threat-boundary line.

## Public Non-Claims

v2.4.2 does not claim:

* LangChain integration
* LlamaIndex integration
* SQLDatabaseToolkit usage
* third-party SQL Agent implementation
* SQL agent runtime support
* model API support
* SQL execution support
* arbitrary SQL safety
* DB connection support
* schema introspection support
* real schema access
* real data access
* database mutation safety
* SQLite synthetic DB support
* DB client support
* ORM support
* KerniQ integration
* KerniQ runtime execution
* E2B integration
* E2B handoff
* runtime behavior
* production readiness

## Acceptance Checklist

* static inert fixture JSON added
* exactly 16 fixtures
* exactly 1 `ACCEPT_FOR_DHMS_EVALUATION`
* exactly 15 `FAIL_CLOSED`
* all required fail-closed categories covered
* all non-execution assertions set to false
* no executable SQL statements
* no real table/column/database names
* no URLs or file paths
* no credentials or user data
* no framework install/import/invocation
* no model API call
* no DB connection
* no KerniQ runtime call
* no E2B handoff
* no code/schema/parser/runner/CLI added
* final verdict set correctly

## Final Verdict

`READY_FOR_V2_4_3_THIRD_PARTY_SQL_AGENT_NON_EXECUTING_THREAT_FIXTURE_VALIDATION`
