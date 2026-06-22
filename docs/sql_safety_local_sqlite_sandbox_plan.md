# SQL Safety Local SQLite Sandbox Plan

## Purpose

This document defines the v0.4.2D plan for a future SQL Safety local temporary
SQLite sandbox phase.

The goal is to plan the exact conditions, lifecycle, permission model, trace
fields, and fail-closed rules required before DHMS may move from the
non-executing disposable sandbox stub to a controlled local SQLite sandbox.

## Plan-only Boundary

v0.4.2D is plan-only.

This phase does not create SQLite files, import database clients, connect to any
database, execute SQL, seed schema/data, perform rollback, or delete sandbox
files. It only records the future implementation plan.

No SQLite/database/SQL/provider/checker/runner/HTTP execution occurs in this
phase.

## Future Conditions For Temporary Local SQLite

Temporary local SQLite may be allowed only in a later task that explicitly
authorizes SQLite sandbox creation and execution.

Future authorization must state all of the following:

* the phase allows temporary local SQLite
* the database is disposable
* the database is created under a temp directory only
* the database filename is randomized and disposable
* the schema/data are toy-only
* the permission model is SELECT-only first
* no network DB is allowed
* no persistent DB is allowed
* no user DB is allowed
* no production DB is allowed
* no DB credentials are allowed
* no provider/checker/runner/HTTP invocation is allowed

If any condition is missing, the implementation must remain a non-executing
stub.

## Required Future Guardrails Before SQLite Creation

Before any future SQLite creation, the guardrail layer must verify:

* temp directory only
* randomized disposable filename
* no user path
* no persistent DB
* no network DB
* no DB credentials
* no production data
* no external mutation
* no provider invocation
* no production checker invocation
* no production runner invocation
* no HTTP adapter invocation
* no A/B/C taxonomy change

The future guardrail layer must fail closed before opening a connection if any
path, filename, source data, permission, or invocation boundary is ambiguous.

## Future Sandbox Lifecycle

The first executable sandbox phase should use this lifecycle:

1. Create temporary SQLite sandbox.

   Create a disposable SQLite file only under a system temp directory, with a
   randomized filename and no user-controlled path.

2. Seed toy schema only.

   Seed a minimal deterministic toy schema and fake rows. Do not import user
   data, production data, logs, exports, provider output, or credentials.

3. Compute pre-state hashes.

   Compute deterministic pre-state row counts, schema hash, and table content
   hash before any allowed sandbox operation.

4. Run allowed sandbox operation.

   In the first executable sandbox phase, allow only explicitly allowlisted
   SELECT operations. Do not allow INSERT / UPDATE / DELETE / DROP / ALTER.

5. Compute post-state hashes.

   Compute post-state row counts, schema hash, and table content hash after the
   allowed operation.

6. Detect mutation.

   Compare pre-state and post-state hashes. In the SELECT-only first phase, any
   mutation must fail closed.

7. Rollback if needed.

   If a transaction exists, rollback and record `rollback_performed`.

8. Close connection.

   Close the SQLite connection and record `connection_closed`.

9. Delete database file.

   Delete the temporary database file and record `sandbox_deleted`.

10. Verify deletion.

   Verify the file no longer exists and record `sandbox_deletion_verified`.

## Future SQL Permission Model

The future permission model is default deny and fail closed.

First executable sandbox phase:

* SELECT-only first
* SELECT allowed only when explicitly allowlisted for the sandbox case
* no INSERT / UPDATE / DELETE / DROP / ALTER in first executable sandbox phase
* no PRAGMA that changes database state
* no ATTACH
* no extension loading
* no filesystem access through SQL
* no network access
* no mutation tests

Mutation tests require a separate explicit later phase. They must not be folded
into the first executable local SQLite sandbox.

## Future Trace Fields

Future SQLite sandbox traces should include:

* `sandbox_mode=true`
* `sqlite_sandbox=true`
* `temporary_database=true`
* `real_database=false`
* `credential_used=false`
* `database_connected`
* `sql_executed`
* `allowed_sql_only`
* `mutation_attempted`
* `mutation_allowed`
* `mutation_detected`
* `rollback_performed`
* `connection_closed`
* `sandbox_deleted`
* `sandbox_deletion_verified`

Field expectations:

* `database_connected` may become true only for the approved temporary local
  SQLite sandbox.
* `sql_executed` may become true only for allowlisted SELECT in the first
  executable sandbox phase.
* `allowed_sql_only` must be true when SQL is executed.
* `mutation_attempted` records whether the requested action attempted mutation.
* `mutation_allowed` must remain false in the SELECT-only first phase.
* `mutation_detected` must remain false in the SELECT-only first phase.
* `rollback_performed`, `connection_closed`, `sandbox_deleted`, and
  `sandbox_deletion_verified` must be recorded before pass.

## Future Fail-closed Rules

The future sandbox must fail closed if:

* database path is not temp
* database filename is not randomized and disposable
* credential is used
* production data is used
* SQL is not allowlisted
* non-SELECT SQL appears in the SELECT-only first phase
* mutation is detected in SELECT-only phase
* rollback verification fails when rollback is required
* connection close verification fails
* delete verification fails
* `sandbox_deletion_verified` is not true
* provider is invoked
* real checker is invoked
* production runner is invoked
* HTTP adapter is invoked
* external mutation is detected
* A/B/C taxonomy changes are required
* output schema changes are required

Any unknown or missing safety field must also fail closed.

## Boundary With Existing Validation

Future SQLite sandbox work must preflight v0.4.2C stub before attempting any
SQLite creation.

The future executable sandbox must remain outside production runner integration
at first. It must not modify production checker logic, production runner logic,
schema, output schema, or A/B/C taxonomy.

A/B/C remain the only perturbation taxonomy groups. v0.4.1E/F/H/I/J and
v0.4.2A/B/C/D are validation, implementation, or planning stage names only.

The future sandbox is not an HTTP adapter. It is not production SQL agent
integration. It must not use real providers, database credentials, user
databases, persistent databases, network databases, or production databases.

## Recommended Next Phase

Recommended next phase:

`v0.4.2E SQL Safety Local SQLite Sandbox Guardrail Stub`

v0.4.2E should still avoid real SQLite execution unless explicitly authorized in
that task. The safest next step is a guardrail stub that validates temp path,
randomized disposable filename shape, allowlist structure, and cleanup field
requirements without creating a database.

## Validation Commands

Allowed validation commands for v0.4.2D:

```bash
python3 validation/run_sql_safety_isolated_validation_path.py
python3 validation/run_sql_safety_dry_fire_target_validation.py
python3 validation/run_sql_safety_local_disposable_sandbox_stub.py
git diff --check
```

Targeted grep checks, a sensitive-token pattern scan, and sqlite/db client
import grep may be run over changed files.

## Non-execution Confirmation

v0.4.2D creates only this plan document.

No SQLite/database/SQL/provider/checker/runner/HTTP execution occurred:

* no SQLite database was created
* no sqlite client was imported
* no database connection occurred
* no SQL was executed
* no schema/data was seeded
* no rollback was performed
* no database file was deleted
* no database credentials were used
* no provider was invoked
* no OpenClaw run occurred
* no DeepSeek call occurred
* no real LLM Judge was invoked
* no production checker was invoked
* no production runner was invoked
* no HTTP adapter was invoked
* no external mutation occurred

Production checker logic, production runner logic, schema, output schema, and
A/B/C taxonomy were not modified.

## Final Verdict

`READY_FOR_V0_4_2E_SQL_SAFETY_LOCAL_SQLITE_SANDBOX_GUARDRAIL_STUB`
