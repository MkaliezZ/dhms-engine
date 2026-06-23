# DHMS Execution Fuse Protocol v0.6.0

## Purpose

DHMS is an execution fuse protocol for AI agents: it sits between agent intent
and real-world execution, captures observable proposals, applies fail-closed
safety decisions, gates execution, routes eligible actions through controlled
release, verifies external state, and records traces.

DHMS began as memory/context/tool-state perturbation testing. That original
line remains part of the project. DHMS has now evolved into an agent execution
safety and runtime control kernel. v0.5 proved the first narrow implementation
line, the SQL Sandbox Execution Fuse. v0.6.0 defines the protocol abstraction
around that proven line before adding benchmarks, demos, CLI surfaces, adapters,
or future tool-family policies.

The execution fuse metaphor maps to agent runtime safety in a specific way:
DHMS does not claim that all execution must be blocked forever. It interrupts
unsafe paths before they can mutate external state, and it allows only the
smallest explicitly authorized action to pass through controlled release,
sandbox constraints, observable verification, and teardown checks.

This protocol is based on observable behavior. DHMS validates request,
proposal, decision, gate, bridge, release review, sandbox result, trace, and
external state. Hidden model reasoning is not inspected.

v0.6.0 adds no new execution capability, no new SQL execution path, and no SQL
allowlist expansion. Future tool families are future adapters, not current
claims.

## Protocol Positioning

DHMS is not just a guardrail.

DHMS is not just a sandbox.

DHMS is not just an approval workflow.

DHMS is not just a SQL safety checker.

DHMS is an execution fuse protocol that combines:

- perturbation lineage
- black-box observation
- runtime contract
- tool-call proposal capture
- safety decision
- execution gate
- bridge/review
- controlled release
- sandbox execution
- external state verification
- teardown verification
- trace recording

The protocol layer matters because v0.5 proved a concrete controlled release
path, while v0.6 needs a stable vocabulary and lifecycle before DHMS can safely
describe benchmarks, demos, command-line flows, or future adapter boundaries.

## Proven Implementation Line

The only proven implementation line in v0.6.0 is:

`SQL Sandbox Execution Fuse`

The single proven runtime-path SQL execution from v0.5.15 was exactly:

```sql
SELECT id, label, status FROM toy_accounts ORDER BY id;
```

That execution was limited to:

- a temporary local SQLite sandbox
- a randomized disposable SQLite database file
- deterministic synthetic toy data only
- one actual controlled release
- mutation detection
- schema/content/row-count comparison
- connection close
- sandbox deletion
- deletion verification

The expected and observed result rows were:

```json
[[1, "alpha", "active"], [2, "beta", "inactive"]]
```

Rejected paths remained non-executing. Mutation SQL did not execute. The
v0.5.17 policy freeze records the exact allowlist, rejected-input behavior,
fail-closed invariants, trace requirements, and non-claim boundaries. The
pre-v0.6 integrity check confirmed that v0.5 is internally consistent and ready
for protocol abstraction.

This is the only proven implementation line in v0.6.0. It is not arbitrary SQL
support, production SQL agent support, OpenClaw runtime integration, provider
SDK integration, agent SDK integration, HTTP integration, file/shell/MCP
policy, or production-ready runtime support.

## Protocol Object Model

### RuntimeRequest

`RuntimeRequest` represents the observable request entering DHMS.

Minimum fields:

- `request_id`
- `source_agent`
- `requested_action_type`
- `raw_intent`
- `declared_execution_mode`
- `timestamp`
- `context_refs`
- `memory_refs`
- `tool_state_refs`

### ToolCallProposal

`ToolCallProposal` represents a normalized observable action proposal.

Minimum fields:

- `proposal_id`
- `request_id`
- `raw_tool_event_type`
- `normalized_tool_name`
- `proposal_class`
- `normalized_payload`
- `normalized_sql`
- `target_resource_class`
- `side_effect_class`
- `proposal_confidence`
- `normalization_notes`

### SafetyDecision

`SafetyDecision` represents DHMS safety classification.

Minimum fields:

- `decision_id`
- `proposal_id`
- `decision`
- `risk_class`
- `reason_code`
- `fail_closed_reason`
- `policy_version`
- `policy_owner`

Allowed decisions for v0.6.0:

- `BLOCK`
- `SANDBOX`
- `FAIL_CLOSED`

Optional future decision vocabulary may include `ALLOW`, `REWRITE`, and
`HUMAN_REVIEW`, but these are future work and are not implemented by v0.6.0.

### ExecutionGateDecision

`ExecutionGateDecision` represents the immediate gate before backend or tool
execution.

Minimum fields:

- `gate_id`
- `decision_id`
- `gate_state`
- `execution_requested`
- `execution_release_allowed`
- `held_reason`
- `closed_reason`

Allowed v0.6.0 gate states:

- `CLOSED`
- `HELD_FOR_SANDBOX_BRIDGE`
- `FAIL_CLOSED`

### BridgeDecision

`BridgeDecision` represents transition into controlled-release review.

Minimum fields:

- `bridge_id`
- `gate_id`
- `bridge_state`
- `bridge_release_allowed`
- `eligibility_reason`
- `rejection_reason`

Allowed v0.6.0 bridge states:

- `REJECTED_BY_BRIDGE`
- `ELIGIBLE_HELD_FOR_REVIEW`
- `FAIL_CLOSED`

### ReleaseReview

`ReleaseReview` represents non-executing release readiness review.

Minimum fields:

- `review_id`
- `bridge_id`
- `release_review_state`
- `release_candidate_id`
- `allowlist_match`
- `review_notes`

Allowed v0.6.0 release review states:

- `REJECTED_BY_RELEASE_REVIEW`
- `CONTROLLED_RELEASE_READY_BUT_NOT_RELEASED`
- `ACTUAL_RELEASE_AUTHORIZATION_READY_BUT_NOT_EXECUTED`
- `BOUNDARY_READY_BUT_NOT_RELEASED`
- `FAIL_CLOSED`

### ReleaseAuthorization

`ReleaseAuthorization` represents the final authorization boundary.

Minimum fields:

- `authorization_id`
- `review_id`
- `authorized`
- `authorization_state`
- `authorization_reason`
- `authorized_by_policy`
- `authorized_sql`
- `authorized_sandbox_profile`

### SandboxExecutionResult

`SandboxExecutionResult` represents actual sandbox execution result.

Minimum fields:

- `sandbox_result_id`
- `authorization_id`
- `sandbox_profile`
- `execution_started`
- `execution_completed`
- `sql_executed`
- `sqlite_database_created`
- `sandbox_executed`
- `result_rows`
- `execution_error`
- `sandbox_deleted`
- `sandbox_deletion_verified`

### ExternalStateVerification

`ExternalStateVerification` represents mutation and external state checks.

Minimum fields:

- `verification_id`
- `sandbox_result_id`
- `schema_hash_before`
- `schema_hash_after`
- `content_hash_before`
- `content_hash_after`
- `row_count_before`
- `row_count_after`
- `mutation_detected`
- `verification_passed`

### ExecutionTrace

`ExecutionTrace` represents the end-to-end observable trace.

Minimum fields:

- `trace_id`
- `request_id`
- `proposal_id`
- `decision_id`
- `gate_id`
- `bridge_id`
- `review_id`
- `authorization_id`
- `sandbox_result_id`
- `verification_id`
- `final_runtime_outcome`
- `policy_owner`
- `not_claimed_scope`
- `trace_created_at`

## Protocol Lifecycle

The DHMS Execution Fuse Protocol lifecycle is:

```text
RuntimeRequest
-> ToolCallProposal
-> SafetyDecision
-> ExecutionGateDecision
-> BridgeDecision
-> ReleaseReview
-> ReleaseAuthorization
-> SandboxExecutionResult
-> ExternalStateVerification
-> ExecutionTrace
```

Most unsafe proposals terminate before execution. `SANDBOX` does not mean
direct execution. Controlled release requires multiple held states. Actual
execution is minimal, explicit, sandboxed, and verified. A trace must exist for
every path. Unknown, malformed, unsupported, missing, or ambiguous paths fail
closed before execution.

## Frozen v0.5 SQL Lifecycle Mapping

The frozen v0.5 SQL policy maps into the v0.6 protocol as follows.

### SQL Mutation Path

```text
ToolCallProposal(SQL_MUTATION_PROPOSAL)
-> SafetyDecision(BLOCK)
-> ExecutionGateDecision(CLOSED)
-> final_runtime_outcome=BLOCKED_BEFORE_EXECUTION
```

Mutation SQL does not reach controlled release and does not execute.

### Malformed SQL Path

```text
ToolCallProposal(SQL_UNKNOWN_OR_MALFORMED_PROPOSAL)
-> SafetyDecision(FAIL_CLOSED)
-> final_runtime_outcome=FAIL_CLOSED_BEFORE_EXECUTION
```

Unknown or malformed SQL fails closed before execution.

### Unique Allowlisted SELECT Path

```text
SQL_SELECT_ALLOWLIST_CANDIDATE
-> SANDBOX
-> HELD_FOR_SANDBOX_BRIDGE
-> ELIGIBLE_HELD_FOR_REVIEW
-> CONTROLLED_RELEASE_READY_BUT_NOT_RELEASED
-> ACTUAL_RELEASE_AUTHORIZATION_READY_BUT_NOT_EXECUTED
-> BOUNDARY_READY_BUT_NOT_RELEASED
-> ACTUAL_RELEASE_EXECUTED_IN_TEMP_SQLITE_SANDBOX
-> ExternalStateVerification
-> teardown/delete verification
```

The only v0.5/v0.6.0 proven allowlisted SQL is exactly:

```sql
SELECT id, label, status FROM toy_accounts ORDER BY id;
```

No normalized equivalent, reordered SELECT, predicate variation, alternate
table, alternate column set, comment-bearing version, multi-statement version,
mutation SQL, unknown SQL, or malformed SQL is release-eligible in v0.6.0.

## Invariants

The v0.6.0 protocol freezes these invariants:

- DHMS owns final execution policy.
- SDKs, tools, providers, agents, OpenClaw, DeepSeek, SQL clients, HTTP
  clients, and backend tools do not own execution policy.
- Unknown, malformed, missing, ambiguous, or unsupported proposals fail closed.
- `BLOCK` never executes.
- `FAIL_CLOSED` never executes.
- `SANDBOX` never executes directly.
- Bridge does not equal release.
- Release review does not equal execution.
- Authorization must be explicit.
- Actual execution must be minimal and sandboxed.
- External state verification is required after any controlled release.
- Teardown verification is required after any controlled release.
- Every path must produce an observable trace.
- Hidden reasoning inspection is not part of DHMS validation.
- v0.6.0 does not expand the v0.5 SQL allowlist.

## Trace Contract

The minimum trace contract for v0.6.0 is organized by protocol object.

Runtime request fields:

- `request_id`
- `source_agent`
- `requested_action_type`
- `raw_intent`
- `declared_execution_mode`
- `timestamp`
- `context_refs`
- `memory_refs`
- `tool_state_refs`

Proposal fields:

- `proposal_id`
- `raw_tool_event_type`
- `normalized_tool_name`
- `proposal_class`
- `normalized_payload`
- `normalized_sql`
- `target_resource_class`
- `side_effect_class`
- `proposal_confidence`
- `normalization_notes`

Decision fields:

- `decision_id`
- `decision`
- `risk_class`
- `reason_code`
- `fail_closed_reason`
- `policy_version`
- `policy_owner`

Gate fields:

- `gate_id`
- `gate_state`
- `execution_requested`
- `execution_release_allowed`
- `held_reason`
- `closed_reason`

Bridge fields:

- `bridge_id`
- `bridge_state`
- `bridge_release_allowed`
- `eligibility_reason`
- `rejection_reason`

Review fields:

- `review_id`
- `release_review_state`
- `release_candidate_id`
- `allowlist_match`
- `review_notes`

Authorization fields:

- `authorization_id`
- `authorized`
- `authorization_state`
- `authorization_reason`
- `authorized_by_policy`
- `authorized_sql`
- `authorized_sandbox_profile`

Sandbox result fields:

- `sandbox_result_id`
- `sandbox_profile`
- `execution_started`
- `execution_completed`
- `sql_executed`
- `sqlite_database_created`
- `sandbox_executed`
- `result_rows`
- `execution_error`
- `sandbox_deleted`
- `sandbox_deletion_verified`

Verification fields:

- `verification_id`
- `schema_hash_before`
- `schema_hash_after`
- `content_hash_before`
- `content_hash_after`
- `row_count_before`
- `row_count_after`
- `mutation_detected`
- `verification_passed`

Final outcome fields:

- `final_runtime_outcome`
- `policy_owner`
- `not_claimed_scope`
- `trace_created_at`

## Not Claimed

v0.6.0 does not claim:

- arbitrary SQL support
- production SQL agent support
- production database safety
- credentialed DB execution
- network DB execution
- user-data safety certification
- OpenClaw runtime integration
- DeepSeek/provider integration
- provider SDK integration
- agent SDK integration
- HTTP adapter
- file/shell/MCP policy
- full-suite validation
- production runner integration
- production-ready agent runtime
- general autonomous agent safety certification

## Future Protocol Adapters

Future adapters may be designed after v0.6.0, but none are implemented in this
phase. Candidate future work includes:

- SQL Benchmark Adapter
- CLI Demo Adapter
- File Operation Safety Fuse
- HTTP/API Safety Fuse
- Shell Command Safety Fuse
- OpenClaw Runtime Adapter Boundary Plan
- MCP Tool Safety Adapter

These are future protocol adapter directions, not current claims.

## Recommended Next Milestone

Recommended next milestone:

`v0.6.1 DHMS-AgentFuse-Bench SQL v0`

## Final Verdict

`READY_FOR_V0_6_1_DHMS_AGENTFUSE_BENCH_SQL_V0`
