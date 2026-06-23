# v0.5.7 SQL Sandbox Runtime Bridge Plan

## Purpose

v0.5.7 defines the SQL Sandbox Runtime Bridge Plan after the v0.5.6 Runtime
Execution Gate Stub.

This is a bridge plan, not bridge implementation. It prepares the transition
from `HELD_FOR_SANDBOX_BRIDGE` to a future controlled sandbox bridge for SQL
SELECT-only runtime decisions. No runtime-path SQL execution happens in this
phase.

Start HEAD: `13661b998a3c218ecc708d1b51e1474410b253e6`

## Files Added or Modified

* Added `docs/sql_sandbox_runtime_bridge_plan_v0_5_7.md`

No validation script was added. This phase is planning and contract design
only.

## Bridge Planning Scope

The future SQL sandbox runtime bridge is the controlled connection between the
v0.5 runtime execution gate and the already proven temporary local SQLite
sandbox validation model from SQL Safety v0.4.

The bridge is needed because:

* v0.5.3 can decide SQL SELECT-only proposals as `SANDBOX`.
* v0.5.5 can carry `SANDBOX` through the runtime dry-run loop.
* v0.5.6 can hold `SANDBOX` at the execution gate as
  `HELD_FOR_SANDBOX_BRIDGE`.
* A future bridge is required before any sandbox execution can be released.

v0.5.7 does not open the gate, does not release execution, does not create a
SQLite database from the runtime path, and does not call SQL sandbox execution
from the runtime path.

## Relationship to SQL Safety v0.4

SQL Safety v0.4 is frozen and proven under its scoped validation model:

* v0.4.2I completed the first real temporary local SQLite SELECT-only target
  shot.
* v0.4.2J completed mutation-block validation.
* v0.4.2K froze documentation and README status.
* SQLite usage was limited to temporary local disposable sandbox validation
  code.
* Mutation SQL was blocked before execution.

v0.5.7 does not repeat SQL-only validation. It designs how runtime-approved
SELECT-only requests may later enter that proven sandbox pattern. Mutation SQL
remains blocked and must never reach bridge execution.

## Relationship to v0.5 Runtime Layer

v0.5 runtime progress so far:

* v0.5.0: Execution Runtime Layer Planning.
* v0.5.1: Execution Runtime Contract Stub.
* v0.5.2: Tool Call Interceptor Stub.
* v0.5.3: SQL Safety Module Mounted into Runtime Stub.
* v0.5.4: OpenClaw Evaluation Wrapper Runtime Adaptation Review.
* v0.5.5: First Runtime Dry-Run Loop.
* v0.5.6: Runtime Execution Gate Stub.

v0.5.3 provides the SQL safety mount decision. v0.5.5 carries the decision
through the dry-run loop. v0.5.6 keeps the decision at the final gate. v0.5.7
defines what a future bridge must check before that gate can release a
temporary local SQLite sandbox request.

## Bridge Eligibility Rules

A future runtime SQL sandbox bridge may only accept inputs where all of the
following are true:

* `tool_type="SQL"`
* runtime decision is `SANDBOX`
* gate result is `HELD_FOR_SANDBOX_BRIDGE`
* `sandbox_required=true`
* `sandbox_bridge_required=true`
* SQL is classified as SELECT-only
* mutation risk is false
* DHMS final decision exists
* DHMS gate owner is true
* request, proposal, decision, and gate trace IDs exist
* black-box mode is true
* no previous execution flag is true

The bridge must not accept mutation SQL, unknown SQL, malformed SQL,
non-SQL tools, or any input that lacks DHMS decision ownership.

## Bridge Rejection and Fail-Closed Rules

The future bridge must fail closed if:

* runtime decision is `BLOCK`
* gate result is `CLOSED`
* tool type is not `SQL`
* SQL is mutation, unknown, or malformed
* multiple SQL statements are detected
* hidden mutation in comments is detected
* SQL is not allowlisted
* request IDs or trace IDs are missing
* DHMS final decision is missing
* DHMS gate ownership is missing
* any execution flag is already true
* provider, agent SDK, HTTP, or production runner flags are true
* external mutation cannot be observed
* sandbox lifecycle cannot be completed
* teardown or delete verification fails

Fail-closed means no bridge release, no sandbox request execution, no SQL
execution, and a traceable rejection reason.

## Planned SQL Sandbox Bridge Data Structures

### A. SQL Sandbox Bridge Input

Planned fields:

* `bridge_input_id`
* `dry_run_request_id`
* `request_id`
* `proposal_id`
* `runtime_decision_id`
* `gate_id`
* `tool_type="SQL"`
* `runtime_decision="SANDBOX"`
* `gate_result="HELD_FOR_SANDBOX_BRIDGE"`
* `sql_text`
* `select_only_candidate`
* `mutation_risk=false`
* `sandbox_required=true`
* `sandbox_bridge_required=true`
* `dhms_final_decision=true`
* `dhms_gate_owner=true`
* `black_box_mode=true`
* `previous_execution_detected=false`

### B. SQL Sandbox Bridge Authorization

Planned fields:

* `bridge_authorization_id`
* `bridge_input_id`
* `authorization_decision`
* `authorization_reason_code`
* `bridge_release_allowed`
* `sandbox_mode_required=true`
* `temporary_database_required=true`
* `synthetic_data_only=true`
* `mutation_detection_required=true`
* `teardown_required=true`
* `delete_verification_required=true`

Allowed future authorization decisions:

* `AUTHORIZE_SANDBOX_EXECUTION`
* `REJECT_BRIDGE_INPUT`
* `FAIL_CLOSED`

For v0.5.7 planning only, no authorization is executed.

### C. SQL Sandbox Execution Request

Planned fields:

* `sandbox_request_id`
* `bridge_authorization_id`
* `sql_text`
* `allowlisted_select`
* `temporary_database=true`
* `real_database=false`
* `network_database=false`
* `credential_used=false`
* `production_data_used=false`
* `execution_requested=false` in v0.5.7 planning

### D. SQL Sandbox Bridge Trace

Planned fields:

* `bridge_trace_id`
* `bridge_input_id`
* `bridge_authorization_id`
* `sandbox_request_id`
* `dry_run_only=true` for v0.5.7
* `bridge_implemented=false`
* `sandbox_execution_released=false`
* `sql_executed=false`
* `sandbox_executed=false`
* `external_mutation_detected=false`
* `black_box_validated=true`

## Future Sandbox Lifecycle Requirements

The future bridge implementation must require:

* system temp directory only
* randomized disposable SQLite filename
* synthetic toy data only
* no user path
* no persistent database
* no network database
* no credentials
* no production data
* pre-state schema hash
* pre-state content hash
* post-state schema hash
* post-state content hash
* row count comparison
* connection close
* file deletion
* deletion verification

The sandbox lifecycle must be observable in trace output. If any lifecycle
step cannot be observed or verified, the bridge must fail closed.

## Future Allowlist Requirements

The first future bridge implementation should only allow the existing control
SELECT:

```sql
SELECT id, label, status FROM toy_accounts ORDER BY id;
```

Everything else should fail closed until explicitly expanded. The bridge must
deny mutation SQL, multiple statements, hidden mutation comments, unknown SQL,
non-allowlisted SELECT statements, network paths, user paths, credentials, and
production data.

## Future Trace Integration

The future bridge trace should connect the complete observable runtime path:

* runtime request trace
* interceptor trace
* SQL safety mount decision
* runtime dry-run trace
* execution gate trace
* future sandbox bridge trace
* future sandbox result trace

Trace IDs should preserve request, proposal, runtime decision, gate, bridge,
authorization, sandbox request, and sandbox result lineage. Hidden reasoning is
not part of the trace contract.

## No SDK / SDK-Agnostic Boundary

The future bridge must preserve the no SDK / SDK-agnostic boundary:

* no provider SDK
* no agent SDK
* no external service SDK
* no production DB SDK
* no network DB client
* only Python standard-library `sqlite3` may be used later inside the
  temporary local SQLite sandbox bridge implementation
* DHMS remains the execution control plane

Provider, agent, external service, HTTP, production runner, and OpenClaw
backends must not own SQL sandbox policy.

## Black-Box Validation Boundary

The future bridge must preserve black-box validation:

* no hidden reasoning inspection
* validate only observable request
* validate observable proposal
* validate runtime decision
* validate gate verdict
* validate bridge input
* validate sandbox result
* validate trace
* validate external state

The bridge must not depend on hidden model reasoning or private chain-of-thought.

## Relationship to OpenClaw

OpenClaw remains blocked in runtime dry-run and execution gate stages.

v0.5.7 is SQL bridge planning only. It does not implement an OpenClaw runtime
adapter, does not invoke OpenClaw, and does not invoke DeepSeek.

## Proposed Next Phase

Expected next phase:

`v0.5.8 SQL Sandbox Runtime Bridge Stub`

The next phase should implement a non-executing bridge stub first. It should
not perform real runtime SQL execution.

## Commands Run

```bash
python3 validation/run_execution_runtime_contract_stub.py
python3 validation/run_tool_call_interceptor_stub.py
python3 validation/run_sql_safety_runtime_mount_stub.py
python3 validation/run_runtime_dry_run_loop_stub.py
python3 validation/run_runtime_execution_gate_stub.py
python3 validation/run_sql_safety_temp_sqlite_select_only_first_real_run.py
python3 validation/run_sql_safety_temp_sqlite_mutation_block_test.py
git diff --check
```

Targeted grep checks, import-only disallowed SDK/client scan, and secret scan
were also run over changed files.

## Non-Execution Confirmation

No SQL sandbox runtime bridge was implemented. No execution gate opened. No
execution release flag was set. No SQL execution occurred from the runtime
path. SQL sandbox execution was not called from the runtime path.

No runtime wrapper execution, tool execution, OpenClaw runtime integration,
OpenClaw invocation, DeepSeek invocation, provider SDK integration, agent SDK
integration, HTTP adapter, production checker, production runner, real LLM
Judge, real-provider test, full suite validation, tag creation, or tag move
occurred in this phase.

Production checker logic, production runner logic, schema, output schema, A/B/C
taxonomy, SQL safety cases, and non-SQL cases were not modified.

## Final Verdict

READY_FOR_V0_5_8_SQL_SANDBOX_RUNTIME_BRIDGE_STUB
