# SQL Sandbox Runtime Execution Policy Freeze v0.5.17

## Purpose

v0.5.17 freezes the DHMS v0.5 SQL sandbox runtime execution policy.

This is policy freeze, not capability expansion. The freeze is scoped only to
SQL sandbox controlled release, specifically:

`DHMS v0.5 SQL sandbox runtime-path controlled execution policy`

This document does not freeze arbitrary SQL execution policy, production SQL
agent policy, production database safety policy, OpenClaw runtime policy,
file/shell/HTTP/MCP tool policy, provider SDK policy, agent SDK policy, or
general enterprise deployment policy.

## Evidence Basis

The freeze is based on:

- v0.5.15 First Actual Controlled Runtime-Path SQL Sandbox Release.
- v0.5.16 SQL Sandbox Runtime First Actual Release Result Review and Freeze.
- README execution fuse narrative patch.

v0.5.15 proved exactly one controlled runtime-path SQL execution:

```sql
SELECT id, label, status FROM toy_accounts ORDER BY id;
```

The execution occurred only inside a temporary local SQLite sandbox with
deterministic synthetic toy data. Rejected inputs did not execute, mutation SQL
did not execute, `mutation_detected_count=0`, and sandbox deletion was verified.

## Frozen Vocabulary

### Proposal Classes

- `SQL_SELECT_ALLOWLIST_CANDIDATE`
- `SQL_MUTATION_PROPOSAL`
- `SQL_MULTI_STATEMENT_PROPOSAL`
- `SQL_COMMENT_HIDDEN_MUTATION_PROPOSAL`
- `SQL_UNKNOWN_OR_MALFORMED_PROPOSAL`
- `NON_SQL_RUNTIME_PROPOSAL`
- `BLOCKED_RUNTIME_INPUT`

### Safety Decisions

- `BLOCK`
- `SANDBOX`
- `FAIL_CLOSED`

### Gate States

- `CLOSED`
- `HELD_FOR_SANDBOX_BRIDGE`
- `FAIL_CLOSED`

### Bridge States

- `REJECTED_BY_BRIDGE`
- `ELIGIBLE_HELD_FOR_REVIEW`
- `FAIL_CLOSED`

### Release Review States

- `REJECTED_BY_RELEASE_REVIEW`
- `CONTROLLED_RELEASE_READY_BUT_NOT_RELEASED`
- `ACTUAL_RELEASE_AUTHORIZATION_READY_BUT_NOT_EXECUTED`
- `BOUNDARY_READY_BUT_NOT_RELEASED`
- `FAIL_CLOSED`

### Actual Release States

- `ACTUAL_RELEASE_EXECUTED_IN_TEMP_SQLITE_SANDBOX`
- `REJECT_ACTUAL_RELEASE_INPUT`
- `FAIL_CLOSED`

### Final Runtime Outcomes

- `BLOCKED_BEFORE_EXECUTION`
- `HELD_FOR_CONTROLLED_RELEASE`
- `EXECUTED_IN_TEMP_SANDBOX`
- `FAIL_CLOSED_BEFORE_EXECUTION`

## Frozen Transition Table

| Proposal class | Safety decision | Gate state | Bridge state | Release eligibility | Actual release state | Final outcome | Execution flags |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `SQL_SELECT_ALLOWLIST_CANDIDATE` | `SANDBOX` | `HELD_FOR_SANDBOX_BRIDGE` | `ELIGIBLE_HELD_FOR_REVIEW` | Unique eligible path | May become `ACTUAL_RELEASE_EXECUTED_IN_TEMP_SQLITE_SANDBOX` only under v0.5.15 conditions | `HELD_FOR_CONTROLLED_RELEASE` in policy stub | All false in v0.5.17 stub |
| `SQL_MUTATION_PROPOSAL` | `BLOCK` | `CLOSED` | `REJECTED_BY_BRIDGE` | Not eligible | `REJECT_ACTUAL_RELEASE_INPUT` | `BLOCKED_BEFORE_EXECUTION` | All false |
| `SQL_MULTI_STATEMENT_PROPOSAL` | `BLOCK` or `FAIL_CLOSED` | `CLOSED` or `FAIL_CLOSED` | `REJECTED_BY_BRIDGE` or `FAIL_CLOSED` | Not eligible | `REJECT_ACTUAL_RELEASE_INPUT` or `FAIL_CLOSED` | `BLOCKED_BEFORE_EXECUTION` or `FAIL_CLOSED_BEFORE_EXECUTION` | All false |
| `SQL_COMMENT_HIDDEN_MUTATION_PROPOSAL` | `BLOCK` or `FAIL_CLOSED` | `CLOSED` or `FAIL_CLOSED` | `REJECTED_BY_BRIDGE` or `FAIL_CLOSED` | Not eligible | `REJECT_ACTUAL_RELEASE_INPUT` or `FAIL_CLOSED` | `BLOCKED_BEFORE_EXECUTION` or `FAIL_CLOSED_BEFORE_EXECUTION` | All false |
| `SQL_UNKNOWN_OR_MALFORMED_PROPOSAL` | `FAIL_CLOSED` | `FAIL_CLOSED` | `FAIL_CLOSED` | Not eligible | `FAIL_CLOSED` | `FAIL_CLOSED_BEFORE_EXECUTION` | All false |
| `NON_SQL_RUNTIME_PROPOSAL` | `BLOCK` or `FAIL_CLOSED` | `CLOSED` or `FAIL_CLOSED` | No SQL sandbox bridge | Not eligible | `REJECT_ACTUAL_RELEASE_INPUT` or `FAIL_CLOSED` | `BLOCKED_BEFORE_EXECUTION` or `FAIL_CLOSED_BEFORE_EXECUTION` | All false |
| `BLOCKED_RUNTIME_INPUT` | `BLOCK` | `CLOSED` | `REJECTED_BY_BRIDGE` | Not eligible | `REJECT_ACTUAL_RELEASE_INPUT` | `BLOCKED_BEFORE_EXECUTION` | All false |

## Frozen Invariants

1. Fail-closed default: any unknown, malformed, missing, ambiguous, or unsupported proposal must become `FAIL_CLOSED` before execution.
2. DHMS ownership: DHMS owns the final execution decision. SDKs, tools, providers, agents, OpenClaw, DeepSeek, SQL clients, HTTP clients, and backend tools must not own execution policy.
3. No direct execution from `SANDBOX`: a `SANDBOX` decision cannot directly execute. It must pass through gate, bridge, review, authorization, boundary, and controlled release.
4. `BLOCK` never executes: any proposal with `BLOCK` must never create a sandbox, execute SQL, or release to backend tools.
5. `FAIL_CLOSED` never executes: any `FAIL_CLOSED` path must never create a sandbox, execute SQL, or release to backend tools.
6. Rejected inputs never execute: mutation SQL, multi-statement SQL, comment-hidden mutation SQL, malformed SQL, non-SQL runtime proposals, and blocked runtime inputs must not execute.
7. Allowlist is exact: only one SELECT is currently proven and release-eligible.
8. Controlled release is minimal: the only proven actual release is one execution inside a temporary local SQLite sandbox with deterministic synthetic toy data.
9. Sandbox verification is required: actual controlled release requires expected result verification, mutation detection, schema/content/row-count comparison, connection close, sandbox delete, and deletion verification.
10. Trace is required: every decision path must produce an observable trace. Hidden reasoning inspection is not part of the policy.

## Unique Release Eligibility Rule

The only v0.5 release-eligible SQL is exactly:

```sql
SELECT id, label, status FROM toy_accounts ORDER BY id;
```

No other SQL is release-eligible in v0.5. No normalized equivalent, similar
SELECT, reordered SELECT, alternative table, alternative columns, predicate
variation, comment-bearing variation, or multi-statement variant is
release-eligible.

## Non-Execution Rules

These proposal classes must not execute:

- mutation SQL
- multi-statement SQL
- comment-hidden mutation SQL
- unknown or malformed SQL
- non-SQL runtime proposals
- blocked runtime inputs

They must not create SQLite databases, release execution, invoke backend tools,
or mutate external state.

## Trace Contract Minimum

The minimum trace fields for v0.5 SQL sandbox runtime policy are:

- `request_id`
- `proposal_id`
- `proposal_class`
- `raw_tool_event_type`
- `normalized_tool_name`
- `normalized_sql`
- `safety_decision`
- `gate_state`
- `bridge_state`
- `release_review_state`
- `authorization_state`
- `boundary_state`
- `actual_release_state`
- `final_runtime_outcome`
- `execution_requested`
- `execution_release_allowed`
- `sql_executed`
- `sqlite_database_created`
- `sandbox_executed`
- `mutation_detected`
- `sandbox_deleted`
- `sandbox_deletion_verified`
- `policy_owner`
- `fail_closed_reason`
- `not_claimed_scope`

## No SDK / Black-Box Boundary

DHMS owns final execution policy.

SDKs, tools, providers, OpenClaw, DeepSeek, SQL clients, HTTP clients, and
backend tools do not own execution policy.

Validation is black-box and observable. DHMS validates request, proposal,
decision, gate state, bridge state, release state, trace, sandbox result, and
external state. Hidden reasoning is not inspected.

## Not Claimed

- Not arbitrary SQL support.
- Not production SQL agent support.
- Not production database safety.
- Not credentialed DB execution.
- Not network DB execution.
- Not user-data safety certification.
- Not OpenClaw runtime integration.
- Not DeepSeek/provider integration.
- Not provider SDK integration.
- Not agent SDK integration.
- Not HTTP adapter.
- Not file/shell/MCP policy.
- Not full-suite validation.
- Not production runner integration.
- Not production-ready agent runtime.

## Policy Validation Stub

The non-executing policy freeze stub is:

```bash
python3 validation/run_runtime_execution_policy_freeze_stub.py
```

Expected deterministic summary:

- `policy_cases_total=7`
- `policy_cases_passed=7`
- `unique_release_eligible_count=1`
- `blocked_or_fail_closed_count=6`
- `direct_execution_allowed_count=0`
- `sql_executed_count=0`
- `sqlite_database_created_count=0`
- `sandbox_executed_count=0`
- `unsupported_fail_closed_count>=1`
- `failed_checks=[]`

The stub validates policy tables and invariants in memory. It does not execute
SQL, create SQLite databases, call OpenClaw, call DeepSeek, invoke provider
SDKs, invoke agent SDKs, use HTTP, or contact external services.

## Next Milestone

Recommended next milestone:

`READY_FOR_V0_6_0_DHMS_EXECUTION_FUSE_PROTOCOL`

## Final Verdict

`READY_FOR_V0_6_0_DHMS_EXECUTION_FUSE_PROTOCOL`
