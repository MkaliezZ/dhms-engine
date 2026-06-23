# v0.5.10 SQL Sandbox Runtime Bridge First Controlled Release Plan

## Purpose

This document defines the v0.5.10 First Controlled Release Plan for the SQL
Sandbox Runtime Bridge.

This is a controlled release plan, not a release implementation. It prepares
the future transition from `REVIEW_READY_BUT_NOT_RELEASED` to a future
controlled sandbox release.

No runtime-path SQL execution happens in v0.5.10. This phase does not release
execution, does not create SQLite databases from the runtime path, does not call
the v0.4 SQLite sandbox execution code, and does not open the runtime execution
gate.

## Start HEAD

`4d4004d8ba42cbb3367567a5d54e788fcc81ce62`

## Files Added

* `docs/sql_sandbox_runtime_bridge_first_controlled_release_plan_v0_5_10.md`

## Controlled Release Planning Scope

v0.5.8 proved that the SQL sandbox runtime bridge stub can identify one
eligible but held SELECT-only bridge input while rejecting mutation, blocked,
non-SQL, malformed, multi-statement, and comment-hidden mutation inputs.

v0.5.9 proved that this single held candidate is structurally ready for a
future controlled release plan, while keeping `release_now=false`,
`bridge_release_allowed=false`, `sandbox_execution_released=false`,
`sql_executed=false`, and `sqlite_database_created=false`.

v0.5.10 defines the release contract required before that candidate may later
request a temporary local SQLite sandbox execution path. It does not implement
the release.

## Why Controlled Release Needs a Dedicated Plan

v0.5.8 and v0.5.9 proved eligibility and review readiness, but neither phase
released execution. The next real risk boundary is allowing the runtime path to
request sandbox execution. That boundary changes the system from proving a
held decision to authorizing a controlled sandbox handoff.

Because that transition introduces execution-release risk, it needs a separate
release contract before any execution is allowed. The contract must specify the
only eligible candidate, required traces, ownership flags, sandbox lifecycle
requirements, mutation detection requirements, teardown requirements, and
fail-closed rejection rules.

## Controlled Release Candidate Definition

The only candidate eligible for future release is the v0.5.9 held review
candidate with all of these properties:

* SQL SELECT-only
* exact allowlisted SQL:
  `SELECT id, label, status FROM toy_accounts ORDER BY id;`
* runtime decision: `SANDBOX`
* gate result: `HELD_FOR_SANDBOX_BRIDGE`
* bridge result: `ELIGIBLE_HELD_FOR_FUTURE_SANDBOX_EXECUTION`
* review decision: `REVIEW_READY_BUT_NOT_RELEASED`
* `mutation_risk=false`
* `allowlist_matched=true`
* `dhms_final_decision=true`
* `dhms_gate_owner=true`
* `dhms_bridge_owner=true`
* `dhms_release_owner=true`
* all previous execution flags are false

No other SQL, tool type, decision state, or bridge result is eligible for the
first controlled release path.

## Controlled Release Eligibility Checklist

A future first controlled release may proceed only if all of these conditions
hold:

* exactly one eligible candidate exists
* candidate SQL exactly matches the allowlist
* candidate is SELECT-only
* no mutation risk is present
* no multiple statements are present
* no comment-hidden mutation is present
* runtime decision is `SANDBOX`
* gate result is `HELD_FOR_SANDBOX_BRIDGE`
* bridge eligibility is true
* review decision is `REVIEW_READY_BUT_NOT_RELEASED`
* release plan exists
* all trace IDs are present
* all DHMS ownership flags are true
* all previous execution flags are false
* no provider, agent SDK, HTTP, or production runner flags are true
* black-box mode is true
* sandbox lifecycle requirements are available
* mutation detection requirements are available
* teardown and delete verification requirements are available

## Rejection and Fail-Closed Rules

Future controlled release must fail closed if any of these conditions occur:

* zero eligible candidates exist
* more than one eligible candidate exists
* SQL does not exactly match the allowlist
* SQL is mutation, unknown, or malformed
* SQL contains multiple statements
* SQL contains comment-hidden mutation
* runtime decision is `BLOCK`
* gate result is `CLOSED`
* bridge result is rejected
* review decision is not `REVIEW_READY_BUT_NOT_RELEASED`
* any execution flag is already true
* any trace ID is missing
* DHMS ownership is missing
* sandbox lifecycle cannot be created
* mutation detection cannot be measured
* teardown or delete verification cannot be performed
* external mutation cannot be observed
* provider, agent SDK, HTTP, or production runner flags are true
* any production data or credential is present

Fail-closed means the future release layer must produce a rejected or
fail-closed result and must keep `release_now=false`,
`bridge_release_allowed=false`, `sandbox_execution_released=false`,
`execution_requested=false`, and `sql_executed=false`.

## Planned Controlled Release Data Structures

### Controlled Release Plan Input

Planned fields:

* `controlled_release_input_id`
* `review_input_id`
* `review_decision_id`
* `bridge_input_id`
* `bridge_eligibility_id`
* `bridge_authorization_id`
* `sandbox_request_id`
* `runtime_decision_id`
* `gate_id`
* `tool_type="SQL"`
* `runtime_decision="SANDBOX"`
* `gate_result="HELD_FOR_SANDBOX_BRIDGE"`
* `bridge_result="ELIGIBLE_HELD_FOR_FUTURE_SANDBOX_EXECUTION"`
* `review_decision="REVIEW_READY_BUT_NOT_RELEASED"`
* `sql_text`
* `allowlist_matched=true`
* `select_only_candidate=true`
* `mutation_risk=false`
* `previous_execution_detected=false`
* `black_box_mode=true`

### Controlled Release Authorization Plan

Planned fields:

* `controlled_release_authorization_id`
* `controlled_release_input_id`
* `planned_authorization_decision`
* `planned_authorization_reason_code`
* `future_release_allowed_conditionally`
* `release_now=false`
* `bridge_release_allowed=false`
* `sandbox_execution_released=false`
* `execution_requested=false`
* `requires_explicit_next_phase=true`
* `requires_temp_sqlite_sandbox=true`
* `requires_synthetic_data_only=true`
* `requires_mutation_detection=true`
* `requires_teardown_verification=true`
* `requires_delete_verification=true`
* `dhms_release_owner=true`

Allowed planned authorization decisions:

* `PLAN_READY_FOR_FUTURE_CONTROLLED_RELEASE_STUB`
* `PLAN_REJECTED`
* `PLAN_FAIL_CLOSED`

### Planned Runtime Sandbox Release Request

Planned fields:

* `planned_release_request_id`
* `controlled_release_authorization_id`
* `sql_text`
* `allowlisted_select`
* `temporary_database_required=true`
* `real_database=false`
* `network_database=false`
* `credential_used=false`
* `production_data_used=false`
* `sandbox_execution_requested=false`
* `release_now=false`
* `sql_executed=false`
* `sqlite_database_created=false`

### Controlled Release Plan Trace

Planned fields:

* `controlled_release_plan_trace_id`
* `controlled_release_input_id`
* `controlled_release_authorization_id`
* `planned_release_request_id`
* `dry_run_only=true`
* `plan_only=true`
* `release_now=false`
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
* `dhms_release_owner=true`

## Future Controlled Release Stub Requirements

The next implementation phase must still be non-executing at first. It should:

* consume the v0.5.9 held release review candidate
* produce controlled release authorization stubs
* still keep `release_now=false`
* still keep `bridge_release_allowed=false`
* still keep `sandbox_execution_released=false`
* not execute SQL
* not create SQLite
* not call SQL sandbox execution
* prove the release contract before implementation of actual sandbox execution

## Future Actual Controlled Sandbox Release Requirements

When actual runtime-path sandbox execution is later allowed in a separate
explicitly authorized phase, it must:

* only execute the exact allowlisted SELECT
* only use Python standard-library `sqlite3`
* only create a temporary local disposable SQLite database
* only use synthetic toy data
* not use credentials
* not use production data
* not use network DB
* not use persistent DB
* compute pre/post schema hash
* compute pre/post content hash
* compare row counts
* close connection
* delete sandbox file
* verify deletion
* produce runtime-compatible sandbox result trace
* fail closed on any deviation

Actual runtime-path sandbox execution is not authorized by v0.5.10.

## Trace Chain Requirements

The future controlled release must connect:

* runtime input request
* raw tool event
* interceptor trace
* SQL safety mount decision
* runtime dry-run trace
* runtime execution gate trace
* SQL sandbox bridge trace
* held release review trace
* controlled release plan trace
* future controlled sandbox result trace

The chain must remain observable and black-box. Hidden reasoning must not be a
dependency for validation.

## No SDK / SDK-Agnostic Boundary

The controlled release path must preserve:

* no provider SDK
* no agent SDK
* no external service SDK
* no production DB SDK
* no network DB client
* only Python standard-library `sqlite3` may be used later inside the temporary
  local SQLite sandbox implementation
* DHMS remains the execution control plane
* SDKs and tools may execute only after DHMS approval in future phases

## Black-Box Validation Boundary

The future release path must not inspect hidden reasoning. It may validate only
observable request, proposal, decision, gate verdict, bridge input, review
result, sandbox result, trace, and external state.

## Relationship to v0.5.9 Held Release Review

v0.5.9 marked exactly one held bridge candidate as
`REVIEW_READY_BUT_NOT_RELEASED`, with all release and execution flags false.
v0.5.10 converts that review posture into a controlled release plan. It does
not alter the held candidate or release it.

## Relationship to v0.5.8 Bridge Stub

v0.5.8 established the bridge stub and identified one eligible held SELECT-only
input. v0.5.10 relies on that single eligible bridge result and keeps all other
v0.5.8 rejected inputs out of the release path.

## Relationship to v0.5.6 Runtime Execution Gate

v0.5.6 held SQL SELECT-only `SANDBOX` decisions at
`HELD_FOR_SANDBOX_BRIDGE`. v0.5.10 does not open that gate and does not set
`execution_release_allowed=true`.

## Relationship to SQL Safety v0.4

SQL Safety v0.4 remains frozen and proven through:

* v0.4.2I first real temporary local SQLite SELECT-only target shot
* v0.4.2J mutation-block validation
* v0.4.2K SQL Safety v0.4 freeze documentation

v0.5.10 does not repeat or extend SQL-only validation. It defines how a future
runtime-approved SELECT-only request may later enter the proven temporary local
SQLite sandbox pattern.

## Relationship to OpenClaw Review

OpenClaw remains blocked in runtime dry-run and gate stages. v0.5.10 is SQL
controlled release planning only. It does not implement an OpenClaw runtime
adapter and does not invoke OpenClaw or DeepSeek.

## Commands Run

* `python3 validation/run_execution_runtime_contract_stub.py`
* `python3 validation/run_tool_call_interceptor_stub.py`
* `python3 validation/run_sql_safety_runtime_mount_stub.py`
* `python3 validation/run_runtime_dry_run_loop_stub.py`
* `python3 validation/run_runtime_execution_gate_stub.py`
* `python3 validation/run_sql_sandbox_runtime_bridge_stub.py`
* `python3 validation/run_sql_sandbox_runtime_bridge_first_held_release_review.py`
* `python3 validation/run_sql_safety_temp_sqlite_select_only_first_real_run.py`
* `python3 validation/run_sql_safety_temp_sqlite_mutation_block_test.py`
* `git diff --check`
* targeted grep checks
* import-only disallowed SDK/client scan
* secret scan

## Non-Execution Confirmation

No controlled release was implemented. No release occurred. No SQL execution
occurred from the runtime path. No SQLite database was created from the runtime
path. No SQL sandbox execution was called from the runtime path. No OpenClaw,
DeepSeek, provider SDK, agent SDK, HTTP adapter, production checker,
production runner, real-provider test, or full suite validation was invoked by
this planning layer.

## Final Verdict

`READY_FOR_V0_5_11_SQL_SANDBOX_RUNTIME_BRIDGE_FIRST_CONTROLLED_RELEASE_STUB`
