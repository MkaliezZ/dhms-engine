# SQL Sandbox Runtime First Actual Controlled Release Log v0.5.15

## Purpose

v0.5.15 implements the first actual controlled runtime-path SQL sandbox release.
This phase releases only the single v0.5.14 boundary-ready SQL SELECT candidate
into a temporary local SQLite sandbox and keeps every rejected input
non-executing.

Start HEAD: `81e96904d236aa39b1a697df79ad8c85ada84f61`

## Files Added

- `validation/sql_sandbox_runtime_first_actual_controlled_release.py`
- `validation/run_sql_sandbox_runtime_first_actual_controlled_release.py`
- `docs/sql_sandbox_runtime_first_actual_controlled_release_log_v0_5_15.md`

## First Actual Controlled Release Boundary

The release boundary remains narrow:

- exactly one runtime-path SQL execution is allowed
- the SQL must exactly match the allowlisted SELECT
- execution may occur only inside a temporary local SQLite sandbox
- rejected inputs cannot create SQLite databases
- rejected inputs cannot execute SQL
- mutation SQL cannot execute
- OpenClaw, DeepSeek, providers, agent SDKs, HTTP adapters, production checker,
  production runner, and full-suite validation are not invoked

## Actual Release Input Fields

Each actual release input records:

- `actual_release_input_id`
- `actual_release_boundary_input_id`
- `actual_release_boundary_decision_id`
- `actual_release_boundary_trace_id`
- `tool_type`
- `sql_text`
- `allowlist_matched`
- `select_only_candidate`
- `mutation_risk`
- `boundary_decision`
- `boundary_ready_for_future_actual_release`
- `black_box_mode=true`

## Authorization Fields

Each authorization records:

- `actual_release_execution_authorization_id`
- `actual_release_input_id`
- `authorization_decision`
- `authorization_reason_code`
- `actual_release_result`
- `release_now`
- `execution_release_allowed`
- `bridge_release_allowed`
- `sandbox_execution_released`
- `execution_requested`
- `requires_temp_sqlite_sandbox=true`
- `requires_synthetic_data_only=true`
- `requires_mutation_detection=true`
- `requires_teardown_verification=true`
- `requires_delete_verification=true`
- `dhms_actual_release_owner=true`

Allowed authorization decisions:

- `AUTHORIZE_SINGLE_ALLOWLISTED_SELECT_SANDBOX_EXECUTION`
- `REJECT_ACTUAL_RELEASE_INPUT`
- `FAIL_CLOSED`

The executed candidate records:

- `actual_release_result=ACTUAL_RELEASE_EXECUTED_IN_TEMP_SQLITE_SANDBOX`

## Sandbox Result Fields

The executed candidate produces:

- `sandbox_mode=true`
- `temporary_database=true`
- `real_database=false`
- `network_database=false`
- `credential_used=false`
- `production_data_used=false`
- `system_temp_directory_used=true`
- `randomized_sqlite_filename_used=true`
- `sqlite_database_created=true`
- `connection_opened=true`
- `setup_schema_created=true`
- `synthetic_seed_data_inserted=true`
- `allowlisted_select_executed=true`
- `sql_executed=true`
- `result_row_count=2`
- `result_rows=[[1, "alpha", "active"], [2, "beta", "inactive"]]`
- `mutation_detected=false`
- `connection_closed=true`
- `sandbox_deleted=true`
- `sandbox_deletion_verified=true`

Rejected inputs produce no SQLite sandbox and no SQL execution.

## Release Trace Fields

Each trace records:

- `actual_release_trace_id`
- `actual_release_input_id`
- `actual_release_execution_authorization_id`
- `sandbox_execution_result_id`
- `dry_run_only`
- `actual_release`
- `release_now`
- `execution_release_allowed`
- `bridge_release_allowed`
- `sandbox_execution_released`
- `execution_requested`
- `executed`
- `tool_executed`
- `sql_executed`
- `sandbox_executed`
- `sqlite_database_created`
- `openclaw_invoked=false`
- `provider_invoked=false`
- `agent_sdk_invoked=false`
- `external_service_sdk_invoked=false`
- `production_runner_invoked=false`
- `http_adapter_invoked=false`
- `external_mutation_detected=false`
- `black_box_validated=true`
- `dhms_actual_release_owner=true`

## Exact Allowlisted SELECT

Only this SQL may execute:

```sql
SELECT id, label, status FROM toy_accounts ORDER BY id;
```

## Deterministic Toy Schema and Data

The temporary SQLite sandbox seeds synthetic toy data only:

```sql
CREATE TABLE toy_accounts (
  id INTEGER PRIMARY KEY,
  label TEXT,
  status TEXT
);
```

Rows:

- `(1, "alpha", "active")`
- `(2, "beta", "inactive")`

Expected result:

- `[1, "alpha", "active"]`
- `[2, "beta", "inactive"]`

## Execution Result Summary

Expected deterministic summary:

- `total_actual_release_inputs=7`
- `passed_actual_release_inputs=7`
- `actual_release_executed_count=1`
- `rejected_actual_release_count=6`
- `sqlite_database_created_count=1`
- `sql_executed_count=1`
- `sandbox_executed_count=1`
- `result_row_count=2`
- `mutation_detected_count=0`
- `sandbox_deleted_count=1`
- `sandbox_deletion_verified_count=1`
- `failed_checks=[]`

## Rejected Input Summary

The six rejected inputs remain rejected and non-executing:

- mutation SQL input
- BLOCK decision input
- non-SQL OpenClaw input
- unknown or malformed SQL input
- multi-statement SQL input
- comment-hidden mutation SQL input

For all rejected inputs:

- `release_now=false`
- `execution_release_allowed=false`
- `bridge_release_allowed=false`
- `sandbox_execution_released=false`
- `execution_requested=false`
- `sql_executed=false`
- `sqlite_database_created=false`

## Mutation Detection

For the executed candidate, the validator computes:

- pre-state schema hash
- post-state schema hash
- pre-state content hash
- post-state content hash
- pre-state row count
- post-state row count

The allowlisted SELECT must not change schema, content, or row count.
`mutation_detected=false` is required.

## Teardown and Delete Verification

The temporary SQLite connection must close, the disposable SQLite file must be
deleted, and deletion must be verified. The validator fails closed if teardown
or deletion verification fails.

## Relationship to v0.5.14

v0.5.14 proved exactly one boundary-ready candidate without releasing
execution. v0.5.15 is the first phase that releases that one candidate into a
temporary local SQLite sandbox.

## Relationship to v0.5.12

v0.5.12 authorized readiness for a future actual release boundary. v0.5.15 uses
the downstream v0.5.14 boundary result and does not broaden the authorized SQL
surface.

## Relationship to SQL Safety v0.4

SQL Safety v0.4 proved the temporary local SQLite SELECT-only sandbox and
mutation-block model. v0.5.15 brings the single allowlisted SELECT through the
runtime-path release chain while preserving the same local-only, synthetic-only,
mutation-detected sandbox constraints.

## No SDK / Black-Box Boundary

No provider SDK, agent SDK, external service SDK, production DB SDK, network DB
client, HTTP adapter, OpenClaw, DeepSeek, production checker, production runner,
real LLM Judge, or full-suite validation is added or invoked.

Only Python standard-library `sqlite3` is used, and only inside the new
temporary local SQLite sandbox implementation.

Validation remains black-box: it checks observable inputs, authorization
records, traces, result rows, safety flags, mutation detection, and external
sandbox file state. It does not inspect hidden reasoning.

## Commands Run

Allowed validation commands for this phase:

- `python3 validation/run_execution_runtime_contract_stub.py`
- `python3 validation/run_tool_call_interceptor_stub.py`
- `python3 validation/run_sql_safety_runtime_mount_stub.py`
- `python3 validation/run_runtime_dry_run_loop_stub.py`
- `python3 validation/run_runtime_execution_gate_stub.py`
- `python3 validation/run_sql_sandbox_runtime_bridge_stub.py`
- `python3 validation/run_sql_sandbox_runtime_bridge_first_held_release_review.py`
- `python3 validation/run_sql_sandbox_runtime_bridge_first_controlled_release_stub.py`
- `python3 validation/run_sql_sandbox_runtime_bridge_actual_release_authorization_review.py`
- `python3 validation/run_sql_sandbox_runtime_first_actual_release_boundary_stub.py`
- `python3 validation/run_sql_sandbox_runtime_first_actual_controlled_release.py`
- `python3 validation/run_sql_safety_temp_sqlite_select_only_first_real_run.py`
- `python3 validation/run_sql_safety_temp_sqlite_mutation_block_test.py`
- `git diff --check`
- targeted grep checks
- import-only disallowed SDK/client scan
- secret scan

## Explicit Confirmation

This was the first actual runtime-path SQL sandbox release.

Only the exact allowlisted SELECT executed.

Rejected inputs did not execute.

No mutation SQL executed.

Only a temporary local SQLite sandbox with synthetic toy data was used.

Sandbox deletion was verified.

No OpenClaw, DeepSeek, provider SDK, agent SDK, HTTP adapter, production checker,
production runner, real LLM Judge, or full-suite validation was added or run.

## Final Verdict

`READY_FOR_V0_5_16_SQL_SANDBOX_RUNTIME_FIRST_ACTUAL_RELEASE_RESULT_REVIEW_AND_FREEZE`
