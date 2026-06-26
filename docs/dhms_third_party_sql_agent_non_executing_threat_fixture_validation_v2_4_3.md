# DHMS Third-Party SQL Agent Non-Executing Threat Fixture Validation v2.4.3

## Metadata

* Milestone: `v2.4.3 Third-Party SQL Agent Non-Executing Threat Fixture Validation`
* Validator: `validation/run_dhms_third_party_sql_agent_threat_fixture_validation_v0.py`
* Input manifest: `benchmarks/dhms_third_party_sql_agent_threat_boundary_v0/threat_fixtures.json`
* Status: deterministic read-only validation

## Current Status

v2.4.3 adds deterministic read-only validation for the v2.4.2 static inert
third-party SQL Agent threat fixtures.

This milestone does not modify fixtures, add schemas, add parser behavior, add
runner behavior, add CLI behavior, install packages, call frameworks, execute
SQL, connect to databases, call model APIs, call KerniQ, hand off to E2B, or add
runtime behavior.

## Scope

The v2.4.3 scope is limited to:

* read the v2.4.2 static threat fixture JSON
* parse JSON only
* validate manifest metadata
* validate fixture count and decision counts
* validate required fields
* validate non-execution assertion keys
* validate all non-execution assertion values are false
* validate fail-closed category coverage
* validate accepted fixture boundary
* validate inert string boundaries
* print deterministic pass/fail output

## Non-Scope

v2.4.3 does not add:

* fixture changes
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
* DB connection
* schema introspection
* real schema or real data
* SQLite synthetic DB
* DB client or ORM
* model API call
* DeepSeek/Qwen/GLM/Kimi/OpenAI/Claude client
* KerniQ runtime call
* E2B handoff
* network/env/credential/user-data access
* subprocess, shell, or command execution
* release
* tag

## Relationship to v2.4.2

v2.4.2 added static inert threat fixtures for the third-party SQL Agent
threat-boundary line.

v2.4.3 validates that fixture manifest without changing it. The validator reads
only the committed static fixture file and treats every fixture value as inert
metadata.

## Validator Boundary

The validator is Python stdlib-only.

Allowed imports are limited to:

* `json`
* `sys`
* `pathlib.Path`
* `collections.Counter`

The validator reads only:

`benchmarks/dhms_third_party_sql_agent_threat_boundary_v0/threat_fixtures.json`

It does not write files, read environment variables, open network connections,
launch subprocesses, execute commands, execute SQL, connect to databases, call
frameworks, or call model providers.

## Validation Checks

The validator checks:

* `manifest_version == v2.4.2`
* `fixture_count == 16`
* exactly 16 fixtures
* `decision_counts == ACCEPT_FOR_DHMS_EVALUATION:1, FAIL_CLOSED:15`
* `fixtures_are_static_inert_metadata_only == true`
* unique fixture IDs
* all required fields are present
* exactly 1 `ACCEPT_FOR_DHMS_EVALUATION`
* exactly 15 `FAIL_CLOSED`
* accepted fixture has `expected_fail_closed_reason=null`
* fail-closed reasons cover each required category once
* all non-execution assertion keys are present
* all non-execution assertion values are false
* no executable SQL statement forms appear in string values
* no URL, file path, credential, user-data, or production markers appear
* no framework/model/runtime execution markers appear outside inert false assertions
* no DB connection, schema introspection, SQL execution, model API, KerniQ, or E2B assertion is true

## Expected Pass Output

```text
DHMS_THIRD_PARTY_SQL_AGENT_THREAT_FIXTURE_VALIDATION_PASS
fixture_count=16
accepted_for_dhms_evaluation=1
fail_closed=15
all_required_fields_present=true
all_non_execution_assertions_present=true
all_non_execution_assertions_false=true
all_threat_fixtures_inert=true
sql_execution_attempts=0
db_connections=0
schema_introspection=0
framework_imports=0
framework_invocations=0
model_api_calls=0
kerniq_runtime_calls=0
e2b_handoffs=0
```

Failure output starts with:

`DHMS_THIRD_PARTY_SQL_AGENT_THREAT_FIXTURE_VALIDATION_FAIL`

and then deterministic `failed_check=` lines.

## Fail-Closed Coverage Validation

The validator requires exactly one fixture for each fail-closed category:

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

## Inert Metadata Validation

The validator treats every fixture as inert metadata. It checks for obvious
raw SQL statement forms and disallowed real-world markers while preserving the
allowed synthetic marker vocabulary used by the v2.4.2 fixture manifest.

## LangChain/LlamaIndex Boundary

v2.4.3 does not install, import, invoke, adapt, or integrate LangChain or
LlamaIndex.

The validator does not use SQLDatabaseToolkit.

## Domestic LLM Boundary

v2.4.3 does not add DeepSeek, Qwen, GLM, Kimi, OpenAI, Claude, or other model
clients. It does not add API calls, credentials, SDKs, adapters, benchmarks, or
runtime integration.

## DB Boundary

v2.4.3 adds no database capability:

* no SQL execution
* no DB connection
* no schema introspection
* no real schema
* no real data
* no SQLite synthetic DB
* no DB client
* no ORM

## KerniQ/E2B Boundary

v2.4.3 does not call KerniQ and does not hand off to E2B.

## Next Milestone Boundary

The next milestone is:

`v2.4.4 Third-Party SQL Agent Threat Fixture Validation Result Review and Freeze`

v2.4.4 must be docs-only result review/freeze. It must not add code, fixtures,
validators, schemas, parser, runner, CLI, dependencies, LangChain/LlamaIndex
integration, SQL execution, DB connection, model API call, KerniQ, E2B, release,
tag, or runtime behavior.

## Public Claims

v2.4.3 claims only that DHMS can deterministically validate the v2.4.2 static
inert threat fixtures without SQL execution, DB connection, framework runtime,
model API calls, KerniQ calls, E2B handoff, or runtime behavior.

## Public Non-Claims

v2.4.3 does not claim:

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

* read-only validator added
* validator reads only the v2.4.2 fixture manifest
* validator uses stdlib-only imports
* validator imports only `json`, `sys`, `Path`, and `Counter`
* validator confirms 16 fixtures
* validator confirms 1 accepted fixture
* validator confirms 15 fail-closed fixtures
* validator confirms all fail-closed reasons exactly once
* validator confirms required fields
* validator confirms non-execution assertions
* validator confirms inert fixture boundaries
* no fixture changes
* no schema/parser/runner/CLI added
* no SQL execution or DB integration added
* no framework install/import/invocation added
* no model API integration added
* no KerniQ/E2B integration added
* no release or tag created
* final verdict set correctly

## Final Verdict

`READY_FOR_V2_4_4_THIRD_PARTY_SQL_AGENT_THREAT_FIXTURE_VALIDATION_RESULT_REVIEW_AND_FREEZE`
