# DHMS Bounded Local Mock-to-Real Preview Proof Planning v2.1.0

## 1. Title and Milestone Metadata

* Milestone: `v2.1.0 Bounded Local Mock-to-Real Preview Proof Planning`
* Branch: `agent-harness-v1`
* Current reviewed base: `v2.0.5.1 README Current Status Sync`
* Future target boundary: `local mock-to-real agent boundary`
* Next recommended milestone: `v2.1.1 Bounded Local Mock-to-Real Preview Proof Contract`

DHMS / DHMS AgentFuse is an execution fuse protocol.

DHMS does not ask:

`Where can this action run safely?`

DHMS asks:

`Should this proposed action be released at all, under what boundary, and with what evidence?`

DHMS operates before execution. It is not a sandbox, not an MCP replacement,
not a runtime adapter, and not a production runtime.

## 2. Current Status

The v2.0.0-v2.0.5 chain has been reviewed and frozen as planning-only,
non-executing, and non-production. v2.0.5.1 synchronized README status only.

v2.1.0 is the next planning gate only. It does not implement the proof, does
not authorize implementation, and does not add runtime behavior.

## 3. Scope

This document plans what a future bounded local mock-to-real preview proof would
require before any implementation can be considered.

This planning milestone may define:

* proof objective
* bounded local-only target assumptions
* inert proposal requirements
* proposal-only dry-run requirements
* non-executing capture requirements
* decision semantics
* fail-closed behavior
* evidence requirements
* trace requirements
* rollback requirements
* freeze requirements
* implementation approval gate for a later milestone

## 4. Non-Scope

v2.1.0 does not create or add:

* proof runner
* capture runner
* proposal parser
* capture parser
* agent hook
* adapter code
* SDK integration
* runtime integration
* CLI command
* schema file
* execution path
* shell execution
* command execution
* file mutation
* network access
* credential handling
* user data handling
* production behavior

## 5. Relationship to v2.0.0-v2.0.5.1

* v2.0.0 planned the real-agent integration preview direction but did not implement integration.
* v2.0.1 selected the future local mock-to-real agent boundary.
* v2.0.2 defined proposal-only dry-run constraints.
* v2.0.3 planned non-executing proposal capture.
* v2.0.4 planned controlled real-agent preview proof requirements.
* v2.0.5 froze the v2.0.0-v2.0.4 chain as planning-only, non-executing, and non-production.
* v2.0.5.1 synchronized README status only.
* v2.1.0 remains planning-only and does not authorize implementation.

## 6. Future Proof Objective

A future bounded local mock-to-real preview proof would need to demonstrate,
before any production or external integration claim, that:

* a selected local mock-to-real target can prepare an inert proposal
* the proposal remains inert before capture
* capture observes metadata only
* no command, shell, file, network, SDK, model, runtime, credential, user-data, or production resource is touched
* DHMS evaluates boundary completeness before any release semantics are considered
* `RELEASE` remains non-executing unless a later explicitly approved bounded proof implementation defines otherwise
* `HOLD`, `BLOCK`, and `FAIL_CLOSED` remain non-executing
* `HOLD`, `BLOCK`, and `FAIL_CLOSED` can never be reinterpreted as `RELEASE`
* missing, malformed, stale, ambiguous, unsupported, executable-looking, credential-involving, user-data-involving, or production-resource-involving inputs fail closed
* evidence continuity is preserved
* trace continuity is preserved
* rollback and freeze rules are defined before implementation

## 7. Bounded Local Mock-to-Real Target Assumptions

The future bounded proof may only be planned around:

* local-only target
* mock-to-real shaped proposal
* no external agent process
* no real LLM call
* no external SDK
* no network access
* no credentials
* no user data
* no production resources
* no shell or command execution
* no file mutation
* no adapter runtime
* no CLI command

The future proof target remains the local mock-to-real agent boundary. It is a
bounded preview target, not an OpenClaw, Codex, Claude Code, DeepSeek, MCP, E2B,
provider SDK, or agent SDK integration.

## 8. Inert Proposal Boundary

Future proposal material must be inert data before capture.

An inert proposal may describe requested action intent, boundary metadata,
expected decision class, payload reference labels, or evidence identifiers. It
must not contain executable instructions that are run by the proof, must not
carry credentials, and must not require access to user data or production
resources.

## 9. Proposal-Only Dry-Run Boundary

The dry-run boundary means the future proof may describe what would be proposed,
but must not cause the proposed action to execute.

Dry-run inputs should remain metadata-only. Dry-run outputs should be DHMS
decision and trace expectations, not runtime side effects.

`RELEASE` is a planning-level decision label in v2.1.0. It does not execute
anything in this milestone.

## 10. Non-Executing Capture Boundary

Future capture, if later approved, must observe proposal metadata before
execution. It must not execute, dispatch, transform into an executable runtime
call, call an SDK, contact a network endpoint, mutate files, invoke a shell, or
touch credentials or user data.

Capture completeness must be evaluated before any release semantics are
considered.

## 11. Decision Semantics Boundary

The planned decision labels are:

* `RELEASE`
* `HOLD`
* `BLOCK`
* `FAIL_CLOSED`

In v2.1.0, all labels are planning semantics only.

`RELEASE` remains non-executing unless a later explicitly approved bounded
proof implementation defines otherwise. `HOLD`, `BLOCK`, and `FAIL_CLOSED`
remain non-executing and can never be reinterpreted as `RELEASE`.

## 12. Fail-Closed Requirements

Future bounded proof planning must fail closed for:

* missing inputs
* malformed inputs
* stale inputs
* ambiguous inputs
* unsupported proposal types
* executable-looking inputs
* credential-involving inputs
* user-data-involving inputs
* production-resource-involving inputs
* missing evidence references
* missing trace expectations
* decision labels outside the approved boundary
* any attempt to execute during capture or dry-run

## 13. Evidence Requirements

Future evidence would need to show:

* target boundary declaration
* proposal inertness
* dry-run marker presence
* capture metadata completeness
* no command, shell, file, network, SDK, model, runtime, credential, user-data, or production resource touch
* DHMS decision assignment
* gate behavior expectation
* fail-closed behavior for invalid or out-of-boundary inputs
* continuity to the frozen SQL/File/HTTP/mock-agent evidence style

## 14. Trace Requirements

Future trace planning should preserve:

* proposal identifier
* target boundary identifier
* inert payload reference
* dry-run marker
* capture completeness status
* safety decision
* gate state
* evidence references
* non-execution counters
* fail-closed reason when applicable
* rollback and freeze references

Trace continuity must be preserved before implementation. Trace records must not
include credentials, user data, production resources, or executable secrets.

## 15. Rollback Requirements

Before any later implementation is approved, the future proof plan must define:

* how to stop on unexpected executable behavior
* how to stop on credential or user-data scope
* how to stop on production-resource scope
* how to stop on network, shell, command, file mutation, SDK, model, or runtime access
* how to preserve failure evidence without escalating execution
* how to keep all rejected paths non-executing

## 16. Freeze Requirements

A later freeze, if an implementation is separately approved and completed, must
review:

* proof scope
* decision counts
* non-execution counters
* fail-closed behavior
* rejected-path behavior
* evidence continuity
* trace continuity
* public non-claims
* rollback evidence

The freeze must not broaden the claim beyond the explicitly approved bounded
local-only proof.

## 17. Later Implementation Approval Gate

v2.1.0 does not approve implementation.

Any later implementation would require a separate explicit milestone, separate
prompt, separate allowed files, separate review, and stricter approval.

The next implementation-like milestone, if ever approved, must be bounded,
local-only, mock-only, non-credentialed, non-user-data, non-production, and must
not expand into OpenClaw, Codex, Claude Code, DeepSeek, MCP, E2B, provider SDK,
or agent SDK integration.

v2.1.1 should be planning/contract only, not implementation.

## 18. Public Non-Claims

v2.1.0 does not claim:

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

## 19. Acceptance Checklist

* docs-only milestone
* planning-only milestone
* no implementation approval
* no source code added
* no schema files added
* no parser added
* no runner added
* no adapter added
* no agent hook added
* no CLI command added
* no execution path added
* no shell or command execution added
* no file mutation added
* no network access added
* no credential handling added
* no user data handling added
* no production runtime claim added
* no real agent integration claim added
* no SDK/runtime integration claim added
* README not modified because it is not actively misleading after v2.0.5.1
* package index updated
* roadmap updated
* final verdict set correctly

## 20. Final Verdict

`READY_FOR_V2_1_1_BOUNDED_LOCAL_MOCK_TO_REAL_PREVIEW_PROOF_CONTRACT`
