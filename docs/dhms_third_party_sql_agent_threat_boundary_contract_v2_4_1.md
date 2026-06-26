# DHMS Third-Party SQL Agent Threat Boundary Contract v2.4.1

## Metadata

* Milestone: `v2.4.1 Third-Party SQL Agent Threat Boundary Contract`
* Contract line: third-party SQL Agent threat-boundary review
* Prior milestone: `v2.4.0 Third-Party SQL Agent Threat Boundary Review Planning`
* Status: prose-contract-only

## Current Status

v2.4.1 defines the prose-only contract for reviewing third-party SQL Agent
threat boundaries.

This milestone does not add code, fixtures, validators, schemas, JSON examples,
parser behavior, runner behavior, CLI behavior, dependencies, package installs,
SQL execution, DB connection, framework integration, model API calls, KerniQ
integration, E2B integration, release, tag, or runtime behavior.

## Scope

The v2.4.1 scope is limited to:

* define the contract subject
* define contract roles
* define the observation boundary
* define future proposal classification terms
* define executable tool-input boundaries
* define DB boundaries
* define framework-loop boundaries
* define model/provider variance boundaries
* define future evidence field names in prose only
* define required fail-closed categories
* preserve LangChain, LlamaIndex, domestic LLM, KerniQ, and E2B boundaries
* define the next milestone boundary

## Non-Scope

v2.4.1 does not add:

* code
* fixtures
* validators
* schema
* JSON examples
* parser
* runner
* CLI
* quickstart
* adapter
* hook
* execution path
* dependency changes
* package installs
* LangChain install, import, invocation, adaptation, or integration
* LlamaIndex install, import, invocation, adaptation, or integration
* SQLDatabaseToolkit usage
* SQL agent runtime
* SQL execution
* DB connection
* schema introspection
* real schema access
* real data access
* database mutation
* SQLite synthetic DB
* sqlite/postgres/mysql client
* ORM
* OpenAI / Claude / DeepSeek / Qwen / GLM / Kimi integration
* model API call
* KerniQ integration or runtime call
* E2B integration or handoff
* subprocess, shell, or command execution
* file mutation behavior
* network access
* env access
* credential access
* user-data access
* SDK/model/runtime access
* release
* tag

## Relationship to v2.4.0

v2.4.0 opened the third-party SQL Agent threat-boundary review line as
planning/review-only.

v2.4.1 turns that plan into a prose-only contract. It preserves the v2.4.0
boundary: third-party SQL Agent systems may be discussed as threat-boundary
subjects only, without integration, installation, invocation, or runtime tests.

## Contract Subject

The contract subject is third-party SQL Agent systems as threat-boundary
subjects only.

The subject includes discussion of:

* LangChain SQL Agent
* LlamaIndex SQL Agent / query engine style systems
* future OpenAI-compatible domestic LLM-backed agent runtimes as comparison subjects

This contract does not claim integration with any of those systems.

## Contract Roles

Contract roles:

* Third-party SQL Agent framework: untrusted proposal/runtime subject.
* LLM/model provider: untrusted proposal source.
* DHMS: boundary evaluator before any execution.
* Database/tool runtime: forbidden in this milestone.
* Evidence artifact: future inert review material only.

## Observation Boundary

DHMS must observe the proposed action before execution.

If DHMS cannot observe the proposal before runtime action, a future decision
must fail closed.

Hidden framework execution must fail closed.

Unbounded tool loops must fail closed.

Unbounded retry loops must fail closed.

## Proposal Classification Contract

Future third-party SQL Agent activity should be classified as one of these
prose-only categories:

* `inert_metadata_proposal`
* `executable_tool_input`
* `db_connection_request`
* `schema_introspection_request`
* `sql_execution_request`
* `result_readback_request`
* `credential_request`
* `user_data_request`
* `mutation_or_write_intent`
* `framework_managed_tool_loop`
* `unsupported_model_tool_format`
* `unobserved_runtime_action`

This milestone does not define a schema, JSON fixture, parser, validator, or
runtime mapping for these categories.

## Executable Tool-Input Boundary

Executable tool input is not acceptable as an inert review artifact.

If a future third-party SQL Agent artifact contains tool input that could be
executed by a framework, runtime, database client, adapter, SDK, or agent loop,
the proposed decision must fail closed unless a later explicitly approved phase
defines a controlled non-executing representation.

## DB Boundary

The DB boundary remains closed:

* no database connection
* no SQL execution
* no schema introspection
* no real schema access
* no real data access
* no database mutation
* no SQLite synthetic DB
* no production DB
* no credentialed DB
* no sqlite/postgres/mysql client
* no ORM

## Framework-Loop Boundary

Framework-managed tool loops are untrusted unless DHMS can observe and classify
each proposed action before execution.

Unbounded framework tool loops must fail closed.

Unbounded retry / self-correction loops must fail closed.

Hidden framework behavior that bypasses DHMS observation must fail closed.

## Model/Provider Variance Boundary

LLM/model providers are untrusted proposal sources.

Model-dependent proposal variance must be treated as a threat-boundary concern.
If a future provider-specific tool format cannot be normalized into inert
metadata before execution, the proposal must fail closed.

## Evidence Capture Contract

Future evidence may record these prose-only field names:

* `framework_subject`
* `model_provider_subject`
* `observed_action_stage`
* `proposal_shape`
* `tool_input_status`
* `db_connection_scope`
* `schema_introspection_scope`
* `sql_execution_scope`
* `result_readback_scope`
* `credential_scope`
* `user_data_scope`
* `mutation_intent`
* `retry_loop_status`
* `framework_loop_status`
* `expected_dhms_decision`
* `expected_fail_closed_reason`
* `non_execution_assertions`

These are prose-only field names. v2.4.1 does not create schema, fixtures, JSON
examples, parser behavior, validator behavior, or runtime behavior.

## Required Fail-Closed Categories

Required future fail-closed categories:

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

## LangChain Boundary

LangChain SQL Agent may be discussed only as a threat-boundary subject.

v2.4.1 does not install, import, invoke, adapt, run, mock through SDKs, or
integrate LangChain. It does not add package dependencies or runtime tests.

## LlamaIndex Boundary

LlamaIndex SQL Agent / query engine style systems may be discussed only as
threat-boundary subjects.

v2.4.1 does not install, import, invoke, adapt, run, mock through SDKs, or
integrate LlamaIndex. It does not add package dependencies or runtime tests.

## Domestic LLM Comparison Boundary

Future comparison may mention DeepSeek, Qwen, GLM, Kimi, or other
OpenAI-compatible providers as subjects only.

v2.4.1 does not add API calls, clients, credentials, SDKs, adapters,
benchmarks, provider tests, or runtime integration.

## KerniQ Boundary

v2.4.1 does not integrate with KerniQ and does not call a KerniQ runtime.

KerniQ remains outside this contract except as a forbidden integration boundary.

## E2B Boundary

v2.4.1 does not integrate with E2B and does not hand off to E2B.

E2B remains outside this contract except as a forbidden integration boundary.

## Later Milestone Boundary

The next milestone is:

`v2.4.2 Third-Party SQL Agent Static Threat Fixtures`

v2.4.2 may add static inert threat fixtures only. v2.4.2 must not add code,
validator, schema, parser, runner, CLI, dependencies, LangChain/LlamaIndex
integration, SQL execution, DB connection, model API call, KerniQ, E2B, release,
tag, or runtime behavior.

## Public Claims

v2.4.1 claims only that DHMS has defined a prose-only contract for reviewing
third-party SQL Agent threat boundaries after the frozen v2.3 SQL Agent Local
Emit-Only evidence chain.

## Public Non-Claims

v2.4.1 does not claim:

* LangChain integration
* LlamaIndex integration
* SQLDatabaseToolkit usage
* third-party SQL Agent implementation
* SQL agent runtime support
* OpenAI integration
* Claude integration
* DeepSeek integration
* Qwen integration
* GLM integration
* Kimi integration
* model API support
* SQL execution support
* arbitrary SQL safety
* DB connection support
* schema introspection support
* real schema access
* real data access
* database mutation safety
* SQLite synthetic DB support
* sqlite/postgres/mysql client support
* ORM support
* KerniQ integration
* KerniQ runtime execution
* E2B integration
* E2B handoff
* runtime behavior
* production readiness

## Acceptance Checklist

* prose-only contract added
* contract subject defined
* contract roles defined
* observation boundary defined
* proposal classifications listed
* executable tool-input boundary defined
* DB boundary defined
* framework-loop boundary defined
* model/provider variance boundary defined
* evidence field names listed in prose only
* fail-closed categories listed
* LangChain boundary stated
* LlamaIndex boundary stated
* domestic LLM comparison boundary stated
* KerniQ boundary stated
* E2B boundary stated
* no code added
* no fixture added
* no validator added
* no schema or JSON examples added
* no parser/runner/CLI added
* no dependencies changed
* no package installed
* no framework imported or invoked
* no SQL execution or DB integration added
* no model API integration added
* no release or tag created
* final verdict set correctly

## Final Verdict

`READY_FOR_V2_4_2_THIRD_PARTY_SQL_AGENT_STATIC_THREAT_FIXTURES`
