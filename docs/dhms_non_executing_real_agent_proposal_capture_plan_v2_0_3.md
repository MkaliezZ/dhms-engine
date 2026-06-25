# DHMS Non-Executing Real-Agent Proposal Capture Plan v2.0.3

## Purpose

DHMS v2.0.3 plans a non-executing real-agent proposal capture path for the
selected future local mock-to-real agent boundary without adding real agent
integration, real agent runtime interception, SDK integration, runtime
integration, adapter code, schema files, parsers, runners, agent hooks, CLI
commands, execution behavior, or production runtime claims.

The purpose of this document is to define, in prose only, how a future
selected local mock-to-real target may emit or expose proposal data for DHMS
capture while remaining non-executing.

This milestone does not implement capture, parser, runner, agent hook,
adapter, SDK integration, runtime integration, or execution behavior.

## Context

v2.0.0 planned the Real Agent Integration Preview boundary.

v2.0.1 selected `local mock-to-real agent boundary` as the first future target
in planning form only.

v2.0.2 defined the Proposal-Only Dry-Run Contract for that selected target.

v2.0.3 plans how future non-executing proposal capture may be structured. It
does not implement capture, parser, runner, agent hook, adapter, SDK
integration, runtime integration, or execution behavior.

## Capture Principle

A future proposal capture path must capture only inert proposal data before
execution.

The capture path must not execute the proposal, invoke a tool, call an SDK,
call a model, mutate files, access credentials, access user data, or reach a
network/runtime target.

Capture means:

* observe inert proposal data
* record proposal metadata
* preserve payload reference and hash
* preserve evidence and trace references
* keep proposed action non-executing
* fail closed on missing, malformed, stale, unsupported, or executable-looking
  input

Capture does not mean:

* real agent integration
* real runtime interception
* tool invocation
* command execution
* shell execution
* file mutation
* network request
* SDK call
* model call
* parser implementation
* runner implementation
* adapter implementation
* CLI command

## Future Capture Scope

The following items may be captured in a future approved phase. In v2.0.3 they
are prose-only planning items, not schema fields and not parser requirements.

| capture item | what it means | why DHMS needs it | what it must not authorize by itself |
| --- | --- | --- | --- |
| proposal envelope reference | inert reference to the proposal container | lets DHMS link capture to the future dry-run contract | must not authorize parsing, dereferencing, or execution |
| selected target identifier | identifies the selected local mock-to-real target boundary | lets DHMS confirm the proposal belongs to the v2.0.1 selected target | must not authorize real agent integration |
| `proposal_id` | stable proposal identifier | lets DHMS connect capture, decision, evidence, and trace records | must not authorize execution |
| inert payload reference | inert reference to the proposed payload | lets DHMS reason about payload identity without reading or executing real payload resources | must not authorize payload execution or real resource access |
| payload hash | stable digest for the inert payload reference | lets DHMS detect mismatch or stale capture data | must not authorize trust, parsing, or execution |
| requested capability | declared capability the proposal is asking about | lets DHMS classify capability risk and boundary fit | must not authorize the capability |
| expected side effects | declared side effects if execution were ever considered later | lets DHMS reject unsafe or unclear action proposals | must not authorize side effects |
| dry-run mode marker | explicit marker that the proposal is dry-run only | lets DHMS refuse proposals that are not clearly non-executing | must not implement dry-run behavior |
| credential scope declaration | declaration that credential scope is empty or non-empty | lets DHMS fail closed on credential involvement | must not authorize credential access |
| user data scope declaration | declaration that user data scope is empty or non-empty | lets DHMS fail closed on user-data involvement | must not authorize user data access |
| runtime target label | inert label for the future target boundary | lets DHMS detect target mismatch | must not connect to a runtime |
| evidence reference | inert reference to planned evidence continuity | lets DHMS preserve evidence linkage | must not claim evidence validation by itself |
| trace reference | inert reference to planned trace continuity | lets DHMS preserve trace linkage | must not claim real agent runtime interception |
| capture timestamp or deterministic marker | stable marker for capture ordering or determinism | lets DHMS reason about stale capture records | must not imply live runtime observation |
| capture completeness status | planned status for whether required capture fields are present | lets DHMS refuse incomplete capture inputs | must not mean the proposal was evaluated or executed |

## Conceptual Non-Executing Capture Flow

```text
selected local mock-to-real target prepares inert proposal
capture boundary observes proposal metadata only
proposal remains non-executing
DHMS receives proposal envelope reference
DHMS checks dry-run marker and completeness
DHMS records evidence and trace references
DHMS assigns RELEASE / HOLD / BLOCK / FAIL_CLOSED as planning-level labels
capture result records no-execution confirmation
no parser, runner, hook, adapter, SDK call, or execution path is implemented in v2.0.3
```

This is a conceptual flow only. v2.0.3 does not implement it.

## Future Capture Acceptance Criteria

A future proposal capture may be considered complete only if:

* proposal is explicitly marked dry-run
* `proposal_id` is present
* selected target identifier matches the v2.0.1 target
* payload is represented only by inert reference
* payload hash is present
* requested capability is declared
* expected side effects are declared
* credential scope is empty
* user data scope is empty
* runtime target label is inert
* evidence reference is present
* trace reference is present
* no execution is attempted
* no external SDK/runtime/tool/network call is attempted

Acceptance for capture completeness must not be interpreted as `RELEASE`,
runtime support, SDK integration, parser support, runner support, agent hook
support, or execution authorization.

## Refusal and Fail-Closed Cases

The future capture plan must refuse and fail closed for:

| refusal / fail-closed case | required behavior |
| --- | --- |
| missing dry-run marker | `FAIL_CLOSED`; no execution |
| missing proposal envelope reference | `FAIL_CLOSED`; no execution |
| malformed proposal envelope reference | `FAIL_CLOSED`; no execution |
| missing `proposal_id` | `FAIL_CLOSED`; no execution |
| missing inert payload reference | `FAIL_CLOSED`; no execution |
| payload hash mismatch | `FAIL_CLOSED`; no execution |
| unsupported proposal type | `FAIL_CLOSED` or `BLOCK`; no execution |
| executable payload content | `FAIL_CLOSED` or `BLOCK`; no execution |
| requested capability outside selected boundary | `FAIL_CLOSED` or `BLOCK`; no execution |
| non-empty credential scope | `FAIL_CLOSED` or `BLOCK`; no execution |
| non-empty user data scope | `FAIL_CLOSED` or `BLOCK`; no execution |
| runtime target mismatch | `FAIL_CLOSED`; no execution |
| missing evidence reference | `FAIL_CLOSED`; no execution |
| missing trace reference | `FAIL_CLOSED`; no execution |
| stale capture marker | `FAIL_CLOSED`; no execution |
| any attempt to execute | `FAIL_CLOSED`; no execution |
| any attempt to call tool / SDK / runtime / model / network | `FAIL_CLOSED`; no execution |
| any attempt to mutate files | `FAIL_CLOSED`; no execution |
| any attempt to access credentials or user data | `FAIL_CLOSED`; no execution |

## Decision Behavior

The capture plan must preserve exactly these DHMS decisions:

* `RELEASE`
* `HOLD`
* `BLOCK`
* `FAIL_CLOSED`

Decision semantics:

* `RELEASE`: in v2.0.3, this is still only a planning-level decision label; it
  does not execute anything.
* `HOLD`: non-executing.
* `BLOCK`: non-executing.
* `FAIL_CLOSED`: non-executing.

No decision in v2.0.3 authorizes real agent integration, real agent runtime
interception, SDK integration, runtime integration, adapter code, schema files,
parser code, capture runner code, agent hooks, CLI commands, or execution
behavior.

## Relationship to Previous Milestones

### v2.0.0 Real Agent Integration Preview Planning

v2.0.0 defined the broad planning boundary for a future real-agent integration
preview. v2.0.3 remains narrower: it plans only how inert proposal capture may
be structured before any execution.

### v2.0.1 Target Selection and Threat Boundary

v2.0.1 selected `local mock-to-real agent boundary` and defined its threat
boundary. v2.0.3 uses that selected boundary as the only future capture target.

### v2.0.2 Proposal-Only Dry-Run Contract

v2.0.2 defined the dry-run contract. v2.0.3 describes how a future capture
path may preserve the dry-run marker, inert payload reference, payload hash,
evidence reference, and trace reference without implementing capture.

### v1.7 Controlled Adapter Skeleton Planning

v1.7 planned a controlled adapter skeleton in prose. v2.0.3 does not implement
or extend that skeleton; it only plans non-executing proposal capture for the
selected future target.

### v0.10 Mock-Agent Runtime Interception Proof

v0.10 proved controlled deterministic mock-agent interception over existing
SQL/File/HTTP proposals. v2.0.3 does not extend that proof into real-agent
runtime interception; it only plans a future non-executing capture boundary.

## Why v2.0.3 Still Does Not Implement

Capture planning is not capture implementation.

Proposal capture planning is not parser support.

Proposal capture planning is not runner support.

Proposal capture planning is not agent hook support.

Proposal capture planning is not adapter support.

Proposal capture planning is not SDK/runtime integration.

Proposal capture planning is not real-agent integration.

Implementation requires a later explicit milestone with allowed files,
forbidden paths, validation commands, trace expectations, and bounded proof
criteria.

## Public Non-Claims

DHMS v2.0.3 does not claim:

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

## Next Milestone

Recommended next milestone:

`v2.0.4 Controlled Real-Agent Preview Proof Planning`

## Final Verdict

`READY_FOR_V2_0_4_CONTROLLED_REAL_AGENT_PREVIEW_PROOF_PLANNING`
