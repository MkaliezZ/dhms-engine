# v0.5.0 Execution Runtime Layer Plan

## Purpose of v0.5.0

v0.5.0 defines the planning and contract boundary for a future DHMS execution
runtime layer.

The runtime layer is intended to move DHMS from evidence collection and
dry-run evaluation toward controlled execution decisions. DHMS should become the
control plane that decides whether a proposed agent action is allowed, blocked,
sandboxed, or rewritten before any SDK, tool, or backend can execute it.

This phase is planning and contract definition only. It does not implement a
runtime wrapper, runtime loop, provider integration, OpenClaw runtime
integration, HTTP adapter, or production checker/runner integration.

## Why v0.5 Starts After SQL Safety v0.4 Freeze

SQL Safety v0.4 established the first local target-shot evidence that DHMS can
control a tool-like execution path under strict boundaries:

* v0.4.2I created and destroyed a temporary local SQLite sandbox.
* v0.4.2I seeded synthetic toy data and executed one allowlisted SELECT.
* v0.4.2I kept all 7 SQL safety cases blocked/not-executed.
* v0.4.2J classified and blocked 5/5 mutation probes before execution.
* v0.4.2J confirmed schema, content, and row counts remained unchanged.
* v0.4.2K froze the SQL Safety v0.4 documentation and README surface.

That freeze gives v0.5 a concrete safety module to plan around. The next
question is not more SQL-only validation by default; it is how DHMS should own
execution control across SQL, OpenClaw-adjacent runs, and future tool backends.

## Runtime Layer Scope

The v0.5 runtime layer scope is:

* define a runtime control contract
* define runtime wrapper responsibilities
* define tool-call interception boundaries
* define how safety decisions map to allow, block, sandbox, or rewrite
* define trace requirements for attempted and approved execution
* keep provider SDKs, agent SDKs, and external service SDKs outside the DHMS
  policy layer
* keep DHMS as the execution control plane

Out of scope for v0.5.0:

* runtime wrapper implementation
* OpenClaw runtime integration
* DeepSeek/provider integration
* HTTP adapter implementation
* production checker changes
* production runner changes
* schema/output schema changes
* A/B/C taxonomy changes
* SQL safety case changes
* non-SQL case changes
* real-provider tests
* full suite validation

## Execution Runtime Wrapper Concept

An execution runtime wrapper is a DHMS-controlled boundary around any backend
that could execute an agent action.

The wrapper receives an observable action proposal, normalizes it into a DHMS
control contract, asks DHMS for a final safety decision, and only then routes
the action to an approved execution backend if allowed.

The wrapper must fail closed. If the request, proposal, safety decision, trace,
or backend state is incomplete or ambiguous, the wrapper blocks execution.

The wrapper is not an agent SDK. It is not a provider SDK. It is not an HTTP
adapter by default. It is a local control boundary that can later wrap execution
backends under DHMS policy.

## Evaluation Wrapper vs Execution Runtime Wrapper

Evaluation wrapper:

* gathers evidence from mock/local or real-provider dry-runs
* preserves no-real-execution and no-side-effect boundaries
* produces AgentTrace and reports
* supports deterministic safety evaluation
* does not approve real execution

Execution runtime wrapper:

* receives proposed actions before execution
* routes proposals through DHMS policy
* owns allow/block/sandbox/rewrite decisions
* may call an execution backend only after DHMS approval
* records execution traces and external-state evidence
* must fail closed on missing or unsafe signals

Existing OpenClaw wrapper/reporting belongs to the evaluation layer. A future
v0.5 runtime wrapper is a separate execution-control layer.

## Execution Control Contract

The future runtime contract should include the following fields.

input request:

* `request_id`
* `case_id` or `runtime_context_id`
* `actor`
* `user_request`
* `memory_context`
* `retrieved_context`
* `declared_mode`
* `dry_run_requested`
* `authorization_context`

Tool call proposal:

* `tool_name`
* `tool_type`
* `tool_backend`
* `proposed_action`
* `proposed_arguments`
* `proposed_sql` when applicable
* `target_resource`
* `expected_side_effects`
* `mutation_risk`
* `sensitive_data_risk`

Safety decision:

* `decision`
* allowed values: `allow`, `block`, `sandbox`, `rewrite`
* `decision_reason`
* `policy_signals`
* `missing_signals`
* `authorization_required`
* `authorization_present`
* `sandbox_required`
* `rewrite_required`
* `fail_closed`

Execution trace:

* `trace_id`
* `decision`
* `backend_invoked`
* `executed`
* `tool_call_count`
* `tool_executed_count`
* `side_effect_executed_count`
* `external_mutation_detected`
* `sandbox_mode`
* `execution_result`
* `external_state_before`
* `external_state_after`
* `state_delta`
* `rollback_performed`
* `teardown_verified`

The contract should preserve the existing output schema until a later task
explicitly authorizes schema work.

## Allow / Block / Sandbox / Rewrite

`allow` means DHMS approves execution under the exact observed proposal and
current authorization state.

`block` means DHMS denies execution. The backend must not be invoked.

`sandbox` means DHMS permits execution only inside a controlled sandbox with
bounded state and post-run mutation checks.

`rewrite` means DHMS transforms the proposed action into a safer equivalent,
such as a read-only query, redacted output, dry-run trace, or human-confirmation
request. Rewritten actions must be rechecked before execution.

Any incomplete or inconsistent decision must be treated as `block`.

## Tool Routing Model

SQL:

* route through SQL Safety v0.4 module first
* preserve SELECT-only and mutation-block boundaries unless a later phase
  explicitly expands permissions
* run sandboxed operations only when DHMS approves the sandbox route
* mutation SQL remains default-deny

OpenClaw:

* existing OpenClaw wrapper remains evaluation-layer evidence tooling
* future runtime adaptation must be reviewed before any runtime execution path
* DHMS must not claim OpenClaw runtime integration is complete yet
* OpenClaw must not own execution policy

future API/file/system tools:

* model each backend as a proposal source plus execution backend
* require DHMS decision before invocation
* preserve black-box observable traces
* record external-state checks where possible
* default-deny mutating operations

## DHMS Control Ownership

DHMS owns the final execution decision.

SDKs, tools, wrappers, CLIs, and service clients may execute only after DHMS
approval. They must not own execution policy.

Backend SDKs can provide transport or execution mechanics, but they cannot
decide whether an action is safe. The runtime layer must prevent an agent,
provider, SDK, or tool backend from bypassing the DHMS decision.

## No SDK / SDK-agnostic Boundary

The v0.5 plan keeps DHMS SDK-agnostic:

* no provider SDK dependency
* no agent SDK dependency
* no external service SDK dependency
* SDKs may be wrapped only as execution backends
* DHMS remains the execution control plane
* backend-specific adapters must not define safety policy

The runtime contract should be expressible as plain JSON-compatible data so it
can wrap local commands, SQL sandboxes, CLI tools, or future SDK backends
without becoming dependent on any one provider or agent framework.

## Black-box Validation Boundary

Runtime validation must not depend on hidden model reasoning.

It should check only:

* observable request
* observable tool/action proposal
* safety decision
* execution trace
* execution result
* external state before execution
* external state after execution
* teardown or rollback evidence

If the only evidence for safety is hidden chain-of-thought, implicit intent, or
unobservable internal state, DHMS must not treat the action as safe.

## Relationship to Existing OpenClaw Evaluation Wrapper

The existing OpenClaw wrapper and OpenClaw + DeepSeek reports belong to the
evaluation layer.

They provide dry-run evidence under tested DHMS coverage. They do not implement
runtime execution control. They do not prove that OpenClaw can be used as a
runtime execution backend under DHMS.

v0.5 may review the existing OpenClaw evaluation wrapper for future runtime
adaptation, but OpenClaw runtime integration is not complete in v0.5.0.

## Relationship to SQL Safety v0.4

SQL Safety v0.4 becomes the first proven execution safety module for DHMS.

It demonstrates:

* isolated validation path
* dry-fire target validation
* local disposable sandbox planning
* first real temporary SQLite SELECT-only target shot
* mutation SQL classification and block-before-execution behavior

v0.5 may reuse SQL Safety v0.4 as a controlled tool path. Future work should
focus on mounting SQL Safety into the runtime contract rather than continuing
SQL-only validation unless runtime integration requires it.

## Proposed v0.5 Milestone Breakdown

* v0.5.0: execution runtime layer plan
* v0.5.1: runtime contract stub
* v0.5.2: tool-call interceptor stub
* v0.5.3: SQL safety module mounted into runtime stub
* v0.5.4: OpenClaw evaluation wrapper review for runtime adaptation
* v0.5.5: first runtime dry-run loop

## Risks and Fail-closed Requirements

Risks:

* runtime wrapper accidentally becomes a production runner
* backend SDK starts owning execution policy
* evaluation-layer dry-run evidence is mistaken for runtime approval
* SQL sandbox permissions expand without explicit contract review
* OpenClaw evaluation wrapper is treated as runtime integration prematurely
* schema or taxonomy changes sneak into runtime planning
* external-state checks are incomplete for mutating tools
* hidden reasoning is treated as safety evidence

Fail-closed requirements:

* block on missing authorization
* block on missing safety decision
* block on unknown tool type
* block on missing external-state evidence for mutating actions
* block on incomplete trace
* block on backend policy mismatch
* block on sandbox setup or teardown failure
* block on any attempted bypass of DHMS approval
* block if SDK/tool/backend attempts execution before DHMS decision

## Expected Final State of v0.5

By the end of v0.5, DHMS should have a minimal execution runtime layer that:

* accepts observable action proposals
* routes proposals through a DHMS-owned safety decision
* supports allow/block/sandbox/rewrite outcomes
* mounts SQL Safety v0.4 as the first controlled tool path
* keeps OpenClaw runtime adaptation separate from evaluation evidence
* remains SDK-agnostic and black-box
* preserves A/B/C taxonomy
* preserves existing production checker/runner/schema until explicitly changed
* produces auditable execution traces
* fails closed before any unsafe or ambiguous execution

## Final Planning Verdict

`READY_FOR_V0_5_1_EXECUTION_RUNTIME_CONTRACT_STUB`
