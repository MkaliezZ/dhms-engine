# SQL Safety Local Disposable Sandbox Design

## Purpose

This document defines the v0.4.2B design for a future SQL Safety local
disposable sandbox phase.

The purpose is to describe how DHMS could move from fully mock dry-fire target
validation toward a controlled local disposable SQL sandbox while preserving the
same safety posture:

* deterministic local validation
* default deny
* fail closed
* no network database
* no persistent database
* no user database
* no production database
* no provider invocation
* no production runner integration at first

This phase does not create, connect to, or execute any database or SQL.

## Design-only Boundary

v0.4.2B is design-only because the current SQL safety target is still proving
the shape of local dry-fire validation. A disposable sandbox introduces a new
risk surface even when it is local and temporary, so implementation must be
designed before any database artifact exists.

No SQLite database is created in v0.4.2B. No SQL is executed. No database
connection is opened. No database credentials are used. No database client code
is added.

## Terminology Boundary

A/B/C remain the only perturbation taxonomy groups:

* A-domain: direct action, tool, or side-effect risk
* B-domain: single memory/context signal risk
* C-domain: coordination risk across multiple context-bearing elements

v0.4.1E/F/H/I/J and v0.4.2A/B are implementation or validation stage names only.
They are not taxonomy groups.

The current dry-fire wrapper is a local mock wrapper only. This design is not an
HTTP adapter and is not production SQL agent integration.

## Proposed Future Architecture

The future disposable sandbox should remain outside the production runner at
first and should be invoked only through an isolated SQL safety validation path.

Proposed future flow:

```text
SQL safety fixture
-> isolated SQL safety validation path
-> local disposable sandbox controller
-> local temporary SQLite sandbox
-> explicitly allowed dry/sandbox operation gate
-> trace collector
-> mutation detector
-> rollback / destroy verifier
-> SQL safety validation report
```

The sandbox controller should own lifecycle, permission checks, trace capture,
mutation detection, rollback, and destruction. The production checker, production
runner, output schema, and A/B/C taxonomy should remain unchanged.

## Proposed Future Sandbox Lifecycle

1. Create disposable sandbox.

   A future implementation may create a local temporary SQLite database only
   when a task explicitly approves sandbox creation. The sandbox must be
   disposable, isolated from user data, and generated from toy schema/data.

2. Seed toy schema/data.

   Seed data must be fake, minimal, deterministic, and non-sensitive. It must
   not include real user data, real credentials, production exports, or copied
   application data.

3. Run only explicitly allowed dry/sandbox operations.

   The default permission model is deny. SELECT is allowed only in explicitly
   marked sandbox cases. Mutating operations remain blocked unless a later test
   explicitly marks disposable mutation as allowed.

4. Collect trace.

   The trace should record proposed SQL, blocked SQL, allowed sandbox SQL if any,
   decision, safety fields, mutation detector inputs, and cleanup status.

5. Detect mutation.

   Mutation detection should compare pre-operation and post-operation sandbox
   state using row counts, schema hash, table content hash, and transaction
   status.

6. Rollback / destroy sandbox.

   The sandbox must be rolled back or destroyed after each validation run.
   Destruction must be verified before the run is considered complete.

## Proposed Future Safety Fields

Future sandbox traces should include these fields when the sandbox stub is
implemented:

* `sandbox_mode=true`
* `disposable_database=true`
* `real_database=false`
* `database_connected`
* `sql_executed`
* `mutation_attempted`
* `mutation_allowed`
* `mutation_detected`
* `rollback_performed`
* `sandbox_destroyed`
* `credential_used=false`

Field expectations:

* `database_connected` may become true only for an approved local temporary
  SQLite sandbox, never for network, persistent, user, or production databases.
* `sql_executed` may become true only for explicitly allowed sandbox operations,
  and must remain false for blocked dry-fire cases.
* `mutation_attempted` records whether a request tried to mutate sandbox state.
* `mutation_allowed` records whether a specific test explicitly allowed
  disposable mutation.
* `mutation_detected` records whether the before/after state comparison found
  mutation.
* `rollback_performed` records transaction rollback or equivalent cleanup.
* `sandbox_destroyed` records verified deletion or teardown of the disposable
  sandbox.
* `credential_used=false` must remain false. The sandbox must not require or
  accept database credentials.

## Proposed Future Allowed Database Type

The only proposed future database type is local temporary SQLite only, and only
when the future task explicitly approves it.

Not allowed:

* no network DB
* no persistent DB
* no user DB
* no production DB
* no database credentials
* no external database service

The preferred first stub may still avoid SQL execution entirely and only model
the sandbox lifecycle state machine.

## Proposed Future SQL Permission Model

The future permission model should be default deny and fail closed:

* SELECT allowed only in explicitly marked sandbox cases
* INSERT blocked by default
* UPDATE blocked by default
* DELETE blocked by default
* DROP blocked by default
* ALTER blocked by default
* TRUNCATE blocked by default
* any unsupported SQL operation blocked by default
* any ambiguous authorization blocked by default
* any missing sandbox cleanup signal fails the run

INSERT / UPDATE / DELETE / DROP / ALTER may only be allowed if a later test
explicitly marks disposable mutation as allowed and the sandbox teardown
verification remains mandatory.

## Proposed Future Mutation Detection Strategy

Mutation detection should use multiple deterministic checks:

* before/after row counts for every seeded table
* schema hash before and after the operation
* table content hash before and after the operation
* transaction rollback confirmation
* sandbox file deletion confirmation
* explicit `mutation_detected` trace field
* explicit `rollback_performed` trace field
* explicit `sandbox_destroyed` trace field

If any detector fails, cannot run, or reports inconsistent state, the sandbox
validation should fail closed.

## Proposed Future Integration Boundary

The disposable sandbox must remain outside production runner integration at
first.

The future stub must not:

* modify production checker logic
* modify production runner logic
* modify schema or output schema
* modify A/B/C taxonomy
* use an HTTP adapter
* use a real provider
* use database credentials
* connect to network, persistent, user, or production databases
* rewrite historical SQL safety evidence

The sandbox should remain a validation-layer target until the lifecycle,
permission model, mutation detector, and cleanup guarantees are validated.

## Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Accidental connection to non-disposable data | Allow only local temporary SQLite and require `real_database=false` plus `credential_used=false`. |
| Hidden SQL execution outside approved cases | Default deny, explicit allowlist, and fail closed on `sql_executed` when not approved. |
| Mutation not detected | Use row counts, schema hash, table content hash, rollback confirmation, and deletion confirmation. |
| Sandbox cleanup failure | Require `rollback_performed=true` or equivalent and `sandbox_destroyed=true` before pass. |
| Taxonomy drift | Keep A/B/C as the only perturbation taxonomy groups. Stage names remain stage names only. |
| Production runner coupling too early | Keep the sandbox outside production runner integration until explicitly approved. |
| HTTP/provider confusion | State that the sandbox is local-only and not an HTTP adapter, provider path, or production SQL agent integration. |

## Recommended Next Phase

Recommended next phase:

`v0.4.2C SQL Safety Local Disposable Sandbox Stub`

The v0.4.2C stub should remain deterministic. It may create only temporary local
SQLite if explicitly approved by task scope. If approval is not explicit, the
stub should model lifecycle and trace behavior without creating a database.

Minimum v0.4.2C expectations:

* local-only
* deterministic
* no network DB
* no persistent DB
* no user DB
* no production DB
* no database credentials
* no HTTP adapter
* no real provider
* no provider invocation
* no production runner invocation
* no production checker modification
* no schema or taxonomy modification
* default deny
* fail closed

## Validation Commands

Allowed validation commands for this design phase:

```bash
python3 validation/run_sql_safety_isolated_validation_path.py
python3 validation/run_sql_safety_dry_fire_target_validation.py
git diff --check
```

Targeted grep checks and a simple sensitive-token pattern scan may be run over
this document.

## Non-execution Confirmation

v0.4.2B creates only this design document.

No SQL/database/provider/checker/runner/HTTP execution occurred:

* no SQLite database was created
* no database connection occurred
* no SQL was executed
* no database credentials were used
* no database client code was added
* no provider was invoked
* no OpenClaw run occurred
* no DeepSeek call occurred
* no real LLM Judge was invoked
* no production checker logic was modified
* no production runner logic was modified
* no HTTP adapter was added
* no full suite validation was run

## Final Verdict

`READY_FOR_V0_4_2C_SQL_SAFETY_LOCAL_DISPOSABLE_SANDBOX_STUB`
