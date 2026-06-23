# v0.5.13 SQL Sandbox Runtime First Actual Release Boundary Plan

## Purpose

This document defines the v0.5.13 First Actual Release Boundary Plan for the
SQL Sandbox Runtime Bridge.

This phase defines the first actual release boundary. It is not an execution
implementation. No runtime-path SQL execution happens in v0.5.13.

The purpose is to define the exact boundary that must exist before the first
actual runtime-path SQL sandbox release can be implemented in a later phase.
This boundary must prevent accidental escalation from review or stub records
into execution.

## Start HEAD

`ba615a4cda4bcb3a146f8f1d40ac35634474ea4f`

## Files Added

* `docs/sql_sandbox_runtime_first_actual_release_boundary_plan_v0_5_13.md`

## Actual Release Boundary Planning Scope

v0.5.12 authorized the next phase to design the actual release boundary for a
single SQL SELECT-only candidate. The authorization did not execute SQL, did
not create SQLite databases from the runtime path, did not call SQL sandbox
execution from the runtime path, and did not open the execution gate.

A boundary is required before any future phase can ever allow
`release_now=true`, `execution_release_allowed=true`,
`bridge_release_allowed=true`, or `sandbox_execution_released=true`.

v0.5.13 is planning and boundary definition only. It does not implement actual
release execution, actual release boundary code, real SQL sandbox runtime
bridge execution, OpenClaw runtime integration, provider SDK integration, agent
SDK integration, HTTP adapter behavior, production checker changes, production
runner changes, schema changes, output schema changes, or A/B/C taxonomy
changes.

## Why an Actual Release Boundary Is Required

v0.5.12 confirmed that exactly one candidate is ready for future actual release
authorization review, and that `authorize_next_phase=true` applies only to that
candidate.

That authorization is not enough to execute. A separate boundary is needed
before any `release_now=true` or `sandbox_execution_released=true` can ever be
allowed. The boundary must:

* prevent accidental escalation from review records to execution
* verify that the complete trace chain exists
* verify that DHMS owns every approval step
* verify that all prior execution flags are false
* verify that the SQL exactly matches the allowlist
* reject all non-eligible candidates
* require a separate explicit next phase before any real execution can occur

## Authorized Release Candidate

The only candidate eligible for future actual boundary work is:

* `tool_type="SQL"`
* exact SQL:
  `SELECT id, label, status FROM toy_accounts ORDER BY id;`
* SELECT-only
* allowlist matched
* `mutation_risk=false`
* runtime decision: `SANDBOX`
* gate result: `HELD_FOR_SANDBOX_BRIDGE`
* bridge result eligible:
  `ELIGIBLE_HELD_FOR_FUTURE_SANDBOX_EXECUTION`
* held release review ready:
  `REVIEW_READY_BUT_NOT_RELEASED`
* controlled release stub ready:
  `CONTROLLED_RELEASE_READY_BUT_NOT_RELEASED`
* actual release authorization ready but not executed:
  `ACTUAL_RELEASE_AUTHORIZATION_READY_BUT_NOT_EXECUTED`
* `authorize_next_phase=true`
* all previous execution flags are false

No mutation SQL, blocked decision, non-SQL tool, unknown SQL, malformed SQL,
multi-statement SQL, or comment-hidden mutation SQL is eligible.

## Boundary Entry Conditions

Future boundary implementation may proceed only if all of these conditions
hold:

* exactly one authorized candidate exists
* SQL exactly matches the allowlist
* candidate is SELECT-only
* no mutation risk exists
* no multiple statements exist
* no comment-hidden mutation exists
* runtime decision is `SANDBOX`
* gate result is `HELD_FOR_SANDBOX_BRIDGE`
* bridge eligibility is true
* review decision is ready but not released
* controlled release decision is ready but not released
* actual release authorization decision is ready but not executed
* `authorize_next_phase=true`
* all trace IDs exist
* DHMS ownership flags are true
* black-box mode is true
* all previous execution flags are false
* provider, agent SDK, HTTP, and production runner flags are false

The boundary must treat every missing condition as a hard stop.

## Hard Stop and Fail-Closed Conditions

Future boundary implementation must fail closed if any of these conditions
occur:

* zero authorized candidates exist
* multiple authorized candidates exist
* SQL does not exactly match the allowlist
* SQL is mutation, unknown, malformed, multi-statement, or comment-hidden
  mutation
* runtime decision is `BLOCK`
* gate result is `CLOSED`
* bridge eligibility is rejected
* held release review is rejected
* controlled release stub is rejected
* actual release authorization is rejected
* `authorize_next_phase=false`
* any execution flag is already true
* any trace ID is missing
* any DHMS ownership flag is missing
* provider, agent SDK, HTTP, or production runner flag is true
* credentials or production data are present
* sandbox lifecycle cannot be built
* mutation detection cannot be measured
* teardown or delete verification cannot be guaranteed
* external mutation cannot be observed

Fail-closed means the future boundary must keep `release_now=false`,
`execution_release_allowed=false`, `bridge_release_allowed=false`,
`sandbox_execution_released=false`, `execution_requested=false`,
`sql_executed=false`, and `sqlite_database_created=false`.

## Planned Boundary Data Structures

### Actual Release Boundary Input

Planned fields:

* `actual_release_boundary_input_id`
* `actual_release_authorization_id`
* `actual_release_review_input_id`
* `controlled_release_decision_id`
* `controlled_release_input_id`
* `review_decision_id`
* `bridge_input_id`
* `runtime_decision_id`
* `gate_id`
* `tool_type="SQL"`
* `sql_text`
* `allowlist_matched=true`
* `select_only_candidate=true`
* `mutation_risk=false`
* `authorize_next_phase=true`
* `previous_execution_detected=false`
* `black_box_mode=true`

### Actual Release Boundary Decision

Planned fields:

* `actual_release_boundary_decision_id`
* `actual_release_boundary_input_id`
* `boundary_decision`
* `boundary_reason_code`
* `boundary_ready_for_future_stub`
* `release_now=false`
* `execution_release_allowed=false`
* `bridge_release_allowed=false`
* `sandbox_execution_released=false`
* `execution_requested=false`
* `requires_explicit_next_phase=true`
* `requires_temp_sqlite_sandbox=true`
* `requires_mutation_detection=true`
* `requires_teardown_verification=true`
* `requires_delete_verification=true`
* `dhms_boundary_owner=true`

Allowed boundary decisions:

* `BOUNDARY_READY_FOR_FUTURE_ACTUAL_RELEASE_STUB`
* `BOUNDARY_REJECTED`
* `BOUNDARY_FAIL_CLOSED`

Allowed boundary reason codes:

* `ALLOWLISTED_SELECT_AUTHORIZED_FOR_FUTURE_BOUNDARY_STUB`
* `REJECTED_NO_AUTHORIZED_CANDIDATE`
* `REJECTED_MULTIPLE_AUTHORIZED_CANDIDATES`
* `REJECTED_ALLOWLIST_MISMATCH`
* `REJECTED_MUTATION_OR_UNSAFE_SQL`
* `REJECTED_MISSING_TRACE_CHAIN`
* `REJECTED_PREVIOUS_EXECUTION_DETECTED`
* `REJECTED_MISSING_DHMS_OWNERSHIP`
* `FAIL_CLOSED_INVALID_BOUNDARY_INPUT`

### Planned Actual Release Boundary Trace

Planned fields:

* `actual_release_boundary_trace_id`
* `actual_release_boundary_input_id`
* `actual_release_boundary_decision_id`
* `dry_run_only=true`
* `plan_only=true`
* `release_now=false`
* `execution_release_allowed=false`
* `bridge_release_allowed=false`
* `sandbox_execution_released=false`
* `execution_requested=false`
* `executed=false`
* `tool_executed=false`
* `sql_executed=false`
* `sandbox_executed=false`
* `sqlite_database_created=false`
* `openclaw_invoked=false`
* `provider_invoked=false`
* `agent_sdk_invoked=false`
* `external_service_sdk_invoked=false`
* `production_runner_invoked=false`
* `http_adapter_invoked=false`
* `external_mutation_detected=false`
* `black_box_validated=true`
* `dhms_boundary_owner=true`

## Future v0.5.14 Boundary Stub Requirements

The next phase should implement a non-executing boundary stub first. It should:

* consume v0.5.12 authorization records
* verify exactly one authorized candidate
* produce boundary input records
* produce boundary decision records
* produce boundary traces
* still keep `release_now=false`
* still keep `execution_release_allowed=false`
* still keep `bridge_release_allowed=false`
* still keep `sandbox_execution_released=false`
* not execute SQL
* not create SQLite
* not call SQL sandbox execution

The v0.5.14 stub must prove the boundary contract before any later phase may
attempt actual runtime-path sandbox execution.

## Future Actual Runtime-Path Sandbox Release Requirements

A later explicitly authorized execution phase may only:

* execute the exact allowlisted SELECT
* use Python standard-library `sqlite3` only
* create a temporary local disposable SQLite database only
* use synthetic toy data only
* never use credentials
* never use production data
* never use network DB
* never use persistent DB
* compute pre/post schema hash
* compute pre/post content hash
* compare row counts
* close connection
* delete sandbox file
* verify deletion
* produce runtime-compatible sandbox result trace
* fail closed on any deviation

Actual runtime-path SQL execution remains out of scope for v0.5.13.

## Trace Chain Requirements

The boundary must preserve the complete trace chain:

* runtime input request
* raw tool event
* interceptor trace
* SQL safety mount decision
* runtime dry-run trace
* runtime execution gate trace
* SQL sandbox bridge trace
* held release review trace
* controlled release stub trace
* actual release authorization trace
* actual release boundary trace
* future sandbox execution result trace

The trace chain must be observable and black-box. Hidden reasoning must not be
required for validation.

## No SDK / SDK-Agnostic Boundary

The future actual release boundary must preserve:

* no provider SDK
* no agent SDK
* no external service SDK
* no production DB SDK
* no network DB client
* only Python standard-library `sqlite3` may be used later inside temporary
  local SQLite sandbox implementation
* DHMS remains the execution control plane

SDKs and tools may execute only after DHMS approval in explicitly authorized
future phases.

## Black-Box Validation Boundary

The future boundary must not inspect hidden reasoning. It may validate only
observable request, proposal, decision, gate verdict, bridge input, release
authorization, boundary decision, sandbox result, trace, and external state.

## Relationship to v0.5.12 Actual Release Authorization Review

v0.5.12 confirmed exactly one actual release authorization candidate and set
`authorize_next_phase=true` only for that candidate. v0.5.13 uses that
authorization to define the first actual release boundary, but does not execute
or release anything.

## Relationship to v0.5.11 Controlled Release Stub

v0.5.11 produced one `CONTROLLED_RELEASE_READY_BUT_NOT_RELEASED` candidate and
six rejected inputs. v0.5.13 keeps only that candidate eligible for future
boundary work.

## Relationship to v0.5.8 Bridge Stub

v0.5.8 identified one eligible bridge input and rejected mutation SQL, blocked
decisions, non-SQL tools, unknown SQL, multi-statement SQL, and comment-hidden
mutation. v0.5.13 preserves those bridge decisions.

## Relationship to v0.5.6 Execution Gate

v0.5.6 held SQL SELECT-only `SANDBOX` decisions at
`HELD_FOR_SANDBOX_BRIDGE`. v0.5.13 does not open the execution gate and does
not set `execution_release_allowed=true`.

## Relationship to SQL Safety v0.4

SQL Safety v0.4 remains frozen and proven through:

* v0.4.2I first real temporary local SQLite SELECT-only target shot
* v0.4.2J mutation-block validation
* v0.4.2K SQL Safety v0.4 freeze documentation

v0.5.13 does not execute SQL from the runtime path and does not call SQL
sandbox execution from the runtime path.

## Relationship to OpenClaw Review

OpenClaw remains blocked in runtime dry-run and gate stages. v0.5.13 is SQL
actual release boundary planning only. It does not implement an OpenClaw
runtime adapter and does not invoke OpenClaw or DeepSeek.

## Commands Run

* `python3 validation/run_execution_runtime_contract_stub.py`
* `python3 validation/run_tool_call_interceptor_stub.py`
* `python3 validation/run_sql_safety_runtime_mount_stub.py`
* `python3 validation/run_runtime_dry_run_loop_stub.py`
* `python3 validation/run_runtime_execution_gate_stub.py`
* `python3 validation/run_sql_sandbox_runtime_bridge_stub.py`
* `python3 validation/run_sql_sandbox_runtime_bridge_first_held_release_review.py`
* `python3 validation/run_sql_sandbox_runtime_bridge_first_controlled_release_stub.py`
* `python3 validation/run_sql_sandbox_runtime_bridge_actual_release_authorization_review.py`
* `python3 validation/run_sql_safety_temp_sqlite_select_only_first_real_run.py`
* `python3 validation/run_sql_safety_temp_sqlite_mutation_block_test.py`
* `git diff --check`
* targeted grep checks
* import-only disallowed SDK/client scan
* secret scan

## Non-Execution Confirmation

No actual release boundary was implemented. No release occurred. No execution
gate opened. No SQL execution occurred from the runtime path. No SQLite
database was created from the runtime path. No SQL sandbox execution was called
from the runtime path. No OpenClaw, DeepSeek, provider SDK, agent SDK, HTTP
adapter, production checker, production runner, real-provider test, or full
suite validation was invoked by this planning layer.

## Final Verdict

`READY_FOR_V0_5_14_SQL_SANDBOX_RUNTIME_FIRST_ACTUAL_RELEASE_BOUNDARY_STUB`
