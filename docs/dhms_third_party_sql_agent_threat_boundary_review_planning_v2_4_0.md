# DHMS Third-Party SQL Agent Threat Boundary Review Planning v2.4.0

## Metadata

* Milestone: `v2.4.0 Third-Party SQL Agent Threat Boundary Review Planning`
* Review line: third-party SQL Agent threat-boundary review
* Prior frozen line: `v2.3 SQL Agent Local Emit-Only`
* Status: planning/review-only

## Current Status

v2.4.0 starts a planning-only review line for third-party SQL Agent systems as
threat-boundary subjects.

This milestone does not add code, fixtures, validators, schemas, parser
behavior, runner behavior, CLI behavior, dependencies, package installs, SQL
execution, DB connection, framework integration, model API calls, KerniQ
integration, E2B integration, release, tag, or runtime behavior.

## Scope

The v2.4.0 scope is limited to:

* define the third-party SQL Agent review subject
* document threat-boundary motivation
* describe SQL Agent risk surfaces in prose
* define DHMS boundary questions
* propose future review dimensions
* propose fail-closed categories
* document LangChain and LlamaIndex boundaries
* document domestic LLM comparison boundaries
* document DB, KerniQ, and E2B boundaries
* define the next milestone boundary

## Non-Scope

v2.4.0 does not add:

* code
* fixtures
* validators
* schema
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
* sqlite/postgres/mysql client
* ORM
* OpenAI integration
* Claude integration
* DeepSeek integration
* Qwen integration
* GLM integration
* Kimi integration
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

## Relationship to v2.3.4.1

v2.3.4.1 synced README and roadmap after the v2.3 SQL Agent Local Emit-Only
evidence-chain freeze.

v2.4.0 does not reopen or alter that frozen evidence chain. It uses the frozen
v2.3 result as the boundary before discussing third-party SQL Agent systems.

## Review Subject

The review subject is third-party SQL Agent systems as threat-boundary subjects
only.

Allowed subject names for planning discussion:

* LangChain SQL Agent
* LlamaIndex SQL Agent / query engine style systems
* OpenAI-compatible domestic LLM-backed agent runtimes as future comparison subjects

This document does not claim integration with any of those systems.

## Threat-Boundary Motivation

Third-party SQL Agent frameworks may combine model output, tool selection,
schema access, query generation, query checking, retries, result readback, and
runtime-managed tool loops. DHMS needs to reason about where the proposed action
can be observed before execution and where fail-closed control must happen.

The v2.3 local emit-only line froze inert proposal validation. v2.4.0 plans how
to review third-party SQL Agent boundaries before any later contract, fixture,
validator, or controlled test is considered.

## Third-Party SQL Agent Risk Surfaces

Threat surfaces to review in prose only:

* tool selection
* tool argument generation
* schema discovery request
* table listing request
* query generation
* query checking
* SQL execution request
* result readback
* retry / self-correction loop
* DB credential request
* DB connection request
* unsafe write or mutation intent
* hidden runtime behavior
* framework-managed tool loop
* model-dependent proposal variance

## DHMS Boundary Questions

DHMS should ask:

* Can DHMS observe the proposed action before execution?
* Is the proposal inert metadata or executable tool input?
* Does the proposal request DB connection?
* Does the proposal request schema introspection?
* Does the proposal request SQL execution?
* Does the proposal request credentials or user data?
* Does the framework hide execution behind a tool abstraction?
* Can DHMS fail closed before the third-party runtime acts?
* What evidence must be captured before any later controlled test?

## Proposed Review Dimensions

Future review may classify each third-party SQL Agent boundary by:

* observability before execution
* proposal shape and serialization
* inert metadata versus executable tool input
* credential boundary
* DB connection boundary
* schema introspection boundary
* SQL execution boundary
* mutation/write intent boundary
* retry-loop boundary
* result-readback boundary
* framework-managed tool-loop transparency
* evidence capture requirements
* fail-closed feasibility
* model/provider-dependent variance
* unsupported runtime behavior

## Proposed Fail-Closed Categories

Future fail-closed categories:

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

v2.4.0 does not install, import, invoke, adapt, run, mock through SDKs, or
integrate LangChain. It does not add package dependencies or runtime tests.

## LlamaIndex Boundary

LlamaIndex SQL Agent / query engine style systems may be discussed only as
threat-boundary subjects.

v2.4.0 does not install, import, invoke, adapt, run, mock through SDKs, or
integrate LlamaIndex. It does not add package dependencies or runtime tests.

## Domestic LLM Comparison Boundary

Future domestic LLM comparison may include DeepSeek, Qwen, GLM, Kimi, or other
OpenAI-compatible providers as comparison subjects.

This is planning-only. v2.4.0 does not add API calls, model clients,
credentials, SDKs, adapters, runtime integration, benchmarks, or provider tests.

## DB Boundary

v2.4.0 adds no database capability:

* no database connection
* no SQL execution
* no schema introspection
* no real schema
* no real data
* no SQLite synthetic DB yet
* no production DB
* no credentialed DB
* no DB client
* no ORM

## KerniQ Boundary

v2.4.0 does not integrate with KerniQ and does not call a KerniQ runtime.

KerniQ remains outside this planning line except as a forbidden integration
boundary.

## E2B Boundary

v2.4.0 does not integrate with E2B and does not hand off to E2B.

E2B remains outside this planning line except as a forbidden integration
boundary.

## Later Milestone Boundary

The next milestone is:

`v2.4.1 Third-Party SQL Agent Threat Boundary Contract`

v2.4.1 must be prose-contract-only. It must not add code, fixtures, validators,
schemas, parser, runner, CLI, dependencies, LangChain/LlamaIndex integration,
SQL execution, DB connection, model API call, KerniQ, E2B, release, tag, or
runtime behavior.

## Public Claims

v2.4.0 claims only that DHMS has opened a planning-only review line for
third-party SQL Agent threat boundaries after the frozen v2.3 local emit-only
evidence chain.

## Public Non-Claims

v2.4.0 does not claim:

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
* sqlite/postgres/mysql client support
* ORM support
* KerniQ integration
* KerniQ runtime execution
* E2B integration
* E2B handoff
* runtime behavior
* production readiness

## Acceptance Checklist

* planning/review-only document added
* third-party SQL Agent review subject defined
* threat surfaces listed
* DHMS boundary questions listed
* review dimensions proposed
* fail-closed categories proposed
* LangChain boundary stated
* LlamaIndex boundary stated
* domestic LLM comparison boundary stated
* DB boundary stated
* KerniQ boundary stated
* E2B boundary stated
* no code added
* no fixture added
* no validator added
* no schema/parser/runner/CLI added
* no dependencies changed
* no package installed
* no framework imported or invoked
* no SQL execution or DB integration added
* no model API integration added
* no release or tag created
* final verdict set correctly

## Final Verdict

`READY_FOR_V2_4_1_THIRD_PARTY_SQL_AGENT_THREAT_BOUNDARY_CONTRACT`
