# DHMS Controlled Real-Agent Preview Proof Planning v2.0.4

## Title and Milestone Metadata

Milestone:

`v2.0.4 Controlled Real-Agent Preview Proof Planning`

DHMS v2.0.4 plans a controlled real-agent preview proof boundary for the
selected future local mock-to-real agent boundary without adding real agent
integration, real agent runtime interception, real LLM execution, SDK
integration, runtime integration, adapter code, schema files, parsers, runners,
agent hooks, CLI commands, execution behavior, credential handling, user data
handling, or production runtime claims.

## Current Status

DHMS / DHMS AgentFuse is an execution fuse protocol.

DHMS does not ask:

```text
Where can this action run safely?
```

DHMS asks:

```text
Should this proposed action be released at all, under what boundary, and with what evidence?
```

DHMS operates before execution. It is not a sandbox, not an MCP replacement,
not a runtime adapter, and not a production runtime.

v2.0.4 is documentation and planning only. It does not implement a controlled
preview proof.

## Scope

v2.0.4 defines, in prose only, what a future controlled real-agent preview
proof would need to prove before any implementation begins.

The planning scope covers:

* proposal inertness before capture
* non-executing capture requirements
* proposal envelope boundaries
* dry-run marker boundaries
* handoff metadata boundaries
* DHMS decision preservation
* evidence continuity requirements
* trace continuity requirements
* rollback requirements
* freeze requirements
* public non-claims

## Non-Scope

v2.0.4 does not:

* implement proof execution
* add a proof runner
* add a capture runner
* add a proposal parser
* add a capture parser
* add an agent hook
* add adapter code
* add SDK integration
* add runtime integration
* add CLI commands
* add shell execution
* add command execution
* add file mutation
* add network access
* add credential handling
* add user data handling
* add any execution path

## Relationship to v2.0.1, v2.0.2, and v2.0.3

v2.0.1 selected `local mock-to-real agent boundary` as the future planning
target and defined its threat boundary.

v2.0.2 defined the Proposal-Only Dry-Run Contract for that selected boundary.

v2.0.3 planned how a future non-executing proposal capture path may observe
inert proposal data while preserving dry-run and trace constraints.

v2.0.4 does not implement any of those prior plans. It defines what a future
controlled preview proof would need to demonstrate before that proof may be
implemented in a later explicit milestone.

## Controlled Preview Proof Objective

A future controlled preview proof would need to prove that:

* the selected target can prepare an inert proposal
* the proposal remains inert before capture
* capture remains non-executing
* the proposal envelope does not authorize execution
* the dry-run marker does not authorize execution
* handoff metadata does not authorize execution
* DHMS preserves `RELEASE`, `HOLD`, `BLOCK`, and `FAIL_CLOSED` semantics
* `RELEASE` remains planning-level unless a later explicit bounded proof
  implements it
* `HOLD`, `BLOCK`, and `FAIL_CLOSED` are never reinterpreted as `RELEASE`
* all non-`RELEASE` decisions remain non-executing
* missing, malformed, stale, ambiguous, unsupported, or executable-looking
  inputs fail closed unless explicitly covered by a later approved bounded proof
* evidence continuity is preserved
* trace continuity is preserved
* rollback and freeze requirements are defined before implementation

## Proof Boundary Model

The future proof boundary would be:

```text
selected local mock-to-real target prepares inert proposal
proposal remains inert before capture
capture observes proposal metadata only
DHMS evaluates completeness and boundary constraints
DHMS assigns RELEASE / HOLD / BLOCK / FAIL_CLOSED
evidence and trace expectations are recorded
non-RELEASE decisions remain non-executing
RELEASE remains planning-level unless a later explicit bounded proof implements it
```

v2.0.4 does not implement this model.

## Proposal Inertness Requirements

A future proof must require:

* proposal payload remains inert before capture
* payload reference is not dereferenced into real resources
* payload hash is used only as evidence metadata
* requested capability is descriptive only
* expected side effects are descriptive only
* proposal envelope does not authorize execution
* dry-run marker does not authorize execution
* handoff metadata does not authorize execution
* executable-looking input fails closed unless a later bounded proof explicitly
  covers it

## Capture Non-Execution Requirements

A future proof must preserve:

* no tool invocation
* no command execution
* no shell execution
* no file mutation
* no network request
* no SDK call
* no model call
* no runtime call
* no MCP call
* no E2B handoff
* no OpenClaw, Codex, Claude Code, or DeepSeek call
* no credential access
* no user data access
* no production resource access

Capture must mean observation of inert proposal metadata only.

## Decision Preservation Requirements

The future proof must preserve exactly these DHMS decisions:

* `RELEASE`
* `HOLD`
* `BLOCK`
* `FAIL_CLOSED`

Decision requirements:

* `RELEASE` remains planning-level in v2.0.4.
* `RELEASE` must not execute anything unless a later explicit bounded proof
  implements it.
* `HOLD` remains non-executing.
* `BLOCK` remains non-executing.
* `FAIL_CLOSED` remains non-executing.
* `HOLD`, `BLOCK`, and `FAIL_CLOSED` must never be reinterpreted as `RELEASE`.
* Missing, unknown, stale, ambiguous, or malformed decisions must fail closed.

## Failure and Fail-Closed Requirements

A future controlled preview proof must fail closed for:

* missing proposal envelope
* malformed proposal envelope
* missing dry-run marker
* missing `proposal_id`
* missing payload reference
* payload hash mismatch
* missing selected target identifier
* selected target mismatch
* missing requested capability
* missing expected side effects
* non-empty credential scope
* non-empty user data scope
* missing evidence reference
* missing trace reference
* stale evidence
* stale trace
* stale capture marker
* ambiguous input
* unsupported input
* executable-looking input outside a later approved bounded proof
* missing DHMS decision
* unknown DHMS decision
* any attempt to execute
* any attempt to call tool / SDK / runtime / model / network
* any attempt to mutate files
* any attempt to access credentials or user data

## Evidence Continuity Requirements

A future proof must define evidence continuity before implementation:

* selected target identifier
* proposal envelope reference
* proposal completeness result
* inert payload reference
* payload hash result
* requested capability classification
* expected side-effect declaration
* dry-run marker validation result
* credential scope declaration result
* user data scope declaration result
* DHMS decision
* no-execution confirmation
* refusal or acceptance boundary
* evidence reference
* proof boundary reference
* rollback reference
* freeze reference

Evidence continuity must not imply production runtime safety.

## Trace Continuity Requirements

A future proof must define trace continuity before implementation:

* target proposal prepared
* proposal inertness checked
* capture boundary observed metadata only
* dry-run marker checked
* completeness checked
* DHMS decision assigned
* execution boundary recorded
* non-`RELEASE` decision refused
* no-execution confirmation recorded
* evidence reference linked
* trace verdict recorded

Trace continuity must not imply real agent runtime interception in v2.0.4.

## Rollback and Freeze Requirements

A future proof plan must define rollback and freeze requirements:

* rollback must remove any later proof-only wiring if a boundary check fails
* rollback must preserve evidence of the failure
* rollback must not reinterpret rejected actions as successful releases
* freeze must lock the final claim to the exact proof boundary
* freeze must record whether any future bounded `RELEASE` path was implemented
* freeze must record all non-`RELEASE` decisions as non-executing
* freeze must preserve public non-claims

v2.0.4 does not create the rollback mechanism or freeze artifact. It only
plans the requirements.

## Public Non-Claims

DHMS v2.0.4 does not claim:

* production readiness
* real agent integration
* real agent runtime interception
* real LLM execution
* local mock-to-real implementation
* OpenClaw integration
* Codex integration
* Claude integration
* Claude Code integration
* DeepSeek integration
* MCP integration
* E2B integration
* provider SDK integration
* agent SDK integration
* runtime adapter implementation
* controlled adapter implementation
* sandbox implementation
* shell execution
* command execution
* file mutation support
* network execution support
* arbitrary tool execution
* schema implementation
* proposal parser
* dry-run parser
* capture parser
* capture runner
* proof runner
* agent hook
* handoff parser
* adapter parser
* adapter executor
* runner implementation
* CLI command
* production runtime behavior
* credential handling
* user data handling
* universal agent safety
* industry standard status

## Acceptance Checklist

v2.0.4 confirms:

* docs-only milestone
* no source code added
* no schema files added
* no parser added
* no runner added
* no adapter added
* no agent hook added
* no CLI command added
* no execution path added
* no production runtime claim added
* no real agent integration claim added
* no SDK/runtime integration claim added
* package index updated
* roadmap updated
* final verdict set correctly

## Final Verdict

`READY_FOR_V2_0_5_RESULT_REVIEW_AND_FREEZE`
