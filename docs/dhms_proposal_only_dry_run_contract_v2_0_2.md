# DHMS Proposal-Only Dry-Run Contract v2.0.2

## Purpose

DHMS v2.0.2 plans a proposal-only dry-run contract for the selected future
local mock-to-real agent boundary without adding real agent integration, SDK
integration, runtime integration, adapter code, schema files, parsers, runners,
CLI commands, execution behavior, or production runtime claims.

The purpose of this document is to define, in prose only, what a future
proposal-only dry-run contract must require before any real-agent preview
implementation can begin.

This milestone does not implement the selected target, dry-run path, parser,
runner, adapter, SDK integration, or execution behavior.

## Context

v2.0.0 planned the Real Agent Integration Preview boundary.

v2.0.1 selected `local mock-to-real agent boundary` as the first future target
in planning form only.

v2.0.2 defines the proposal-only / dry-run contract for that selected future
target. It does not connect to any real agent, real LLM, SDK, runtime,
adapter, or external tool.

## Dry-Run Contract Principle

A future dry-run contract must prove that the selected target can emit
observable proposals before execution while keeping execution disabled by
default.

Dry-run means:

* no command execution
* no shell execution
* no file mutation
* no network request
* no SDK call
* no provider call
* no MCP call
* no E2B handoff
* no OpenClaw / Codex / Claude Code / DeepSeek call
* no credential access
* no user data access
* no production resource access

The contract is about proposal visibility and decision recording. It is not an
execution path.

## Dry-Run Contract Responsibilities

### What the Selected Target May Emit

The selected future local mock-to-real target may emit an inert proposal
envelope in a later approved phase. That envelope may describe requested
capability, payload reference, runtime target label, and evidence references.

The emitted proposal must not execute, call tools, call SDKs, read credentials,
read user data, mutate files, or reach a production resource.

### What DHMS May Observe

DHMS may observe the inert proposal envelope before execution. Observation
means reading the proposal data shape in a controlled future dry-run context,
not executing the described action.

### What Must Remain Inert

These items must remain inert:

* proposal envelope reference
* inert payload reference
* payload hash
* requested capability
* runtime target label
* credential scope declaration
* user data scope declaration
* evidence reference
* trace reference

### What Must Remain Non-Executing

The dry-run contract must keep all proposed actions non-executing:

* no shell or command execution
* no file mutation
* no network request
* no SDK call
* no provider call
* no MCP call
* no E2B handoff
* no OpenClaw, Codex, Claude Code, or DeepSeek call
* no credential access
* no user data access
* no production resource access

### DHMS Decision Outputs to Preserve

The dry-run contract must preserve exactly these DHMS decision outputs:

* `RELEASE`
* `HOLD`
* `BLOCK`
* `FAIL_CLOSED`

In v2.0.2, each decision is a planning-level label only. No decision executes
anything in this milestone.

### Evidence to Record

A later approved dry-run phase must record:

* selected target identifier
* proposal envelope reference
* proposal completeness outcome
* inert payload reference
* payload hash check outcome
* requested capability classification
* credential scope declaration result
* user data scope declaration result
* DHMS decision
* refusal or acceptance boundary
* no-execution confirmation
* evidence reference
* trace reference

### Trace Continuity Required

Trace continuity must connect:

* selected target emits inert proposal
* proposal remains non-executing
* DHMS receives proposal envelope
* DHMS validates dry-run completeness
* DHMS assigns `RELEASE`, `HOLD`, `BLOCK`, or `FAIL_CLOSED`
* DHMS records evidence and trace expectations
* dry-run result records decision and refusal/acceptance boundary
* no action executes in v2.0.2

### What Must Fail Closed

The contract must fail closed when completeness, boundary, evidence, trace,
or decision requirements are missing, malformed, stale, unknown, or outside
the selected target boundary.

### What Must Not Be Interpreted as Support or Integration

The presence of a contract term must not be interpreted as:

* real agent integration
* SDK integration
* runtime integration
* adapter support
* parser support
* runner support
* CLI support
* production readiness

## Conceptual Dry-Run Flow

```text
selected local mock-to-real target emits inert proposal
proposal remains non-executing
DHMS receives proposal envelope
DHMS validates dry-run completeness
DHMS assigns RELEASE / HOLD / BLOCK / FAIL_CLOSED
DHMS records evidence and trace expectations
dry-run result records decision and refusal/acceptance boundary
no action executes in v2.0.2
```

This is a conceptual flow only. v2.0.2 does not implement this flow.

## Future Dry-Run Inputs

These are prose-only future inputs. They are not schema fields in v2.0.2.

| input | what it means | why DHMS needs it | what it must not authorize by itself |
| --- | --- | --- | --- |
| selected target identifier | identifies the planned local mock-to-real target boundary | lets DHMS confirm the proposal belongs to the selected v2.0.1 boundary | must not authorize integration with the target |
| proposal envelope reference | identifies the inert proposal container | lets DHMS reason about completeness and trace linkage | must not authorize parsing or execution |
| inert payload reference | points to the inert payload description | lets DHMS identify what the proposal is describing without executing it | must not authorize payload execution or dereferencing into real resources |
| payload hash | stable digest of the inert payload | lets DHMS detect mismatch or stale evidence in a future dry-run | must not authorize trusting or executing the payload |
| requested capability | describes what capability the target is asking about | lets DHMS classify the proposal and compare it to the selected boundary | must not authorize the capability |
| expected side effects | declares the side effects the proposal would have if ever executed | lets DHMS reject or fail closed on unsafe or unclear effects | must not authorize side effects |
| runtime target label | names the inert future runtime target label | lets DHMS detect target mismatch | must not connect to a runtime |
| credential scope declaration | states whether credentials are required | lets DHMS fail closed when credential scope is not empty | must not authorize credential access |
| user data scope declaration | states whether user data is involved | lets DHMS fail closed when user data scope is not empty | must not authorize user data access |
| dry-run mode marker | marks the proposal as dry-run only | lets DHMS reject proposals that are not explicitly dry-run | must not create a dry-run implementation by itself |
| evidence reference | links to planned evidence | lets DHMS preserve evidence continuity | must not claim evidence exists without validation |
| trace reference | links to planned trace continuity | lets DHMS preserve trace continuity | must not claim runtime interception or execution trace support |

## Future Dry-Run Outputs

These are prose-only future outputs. They are not implemented by v2.0.2.

| output | what it means | why DHMS needs it | what it must not claim by itself |
| --- | --- | --- | --- |
| dry-run accepted-for-evaluation marker | DHMS accepted the inert proposal for decision evaluation | separates complete dry-run proposals from refused proposals | must not mean `RELEASE` or execution |
| dry-run refused marker | DHMS refused to evaluate or proceed with the proposal | preserves fail-closed behavior for incomplete or unsafe proposals | must not mean a runtime error was observed in a real agent |
| DHMS decision | one of `RELEASE`, `HOLD`, `BLOCK`, or `FAIL_CLOSED` | preserves the decision vocabulary needed for later boundaries | must not execute anything in v2.0.2 |
| evidence continuity marker | indicates that evidence references are present and consistent | supports future reproducibility | must not claim external proof execution |
| trace continuity marker | indicates that trace references are present and consistent | supports future trace review | must not claim real agent runtime interception |
| no-execution confirmation | records that no action executed | preserves dry-run safety invariant | must not claim production runtime safety |
| refusal reason | explains why the proposal was refused | supports review and fail-closed behavior | must not imply the action was attempted |
| unsupported proposal reason | explains why a proposal type or capability is unsupported | prevents unsupported proposals from drifting into release | must not add support for that proposal |
| fail-closed reason | explains why DHMS failed closed | supports bounded evidence | must not imply recovery, retry, or execution |

## Decision Behavior

The dry-run contract must preserve exactly these decisions:

* `RELEASE`
* `HOLD`
* `BLOCK`
* `FAIL_CLOSED`

Decision semantics:

* `RELEASE`: in v2.0.2, this is only a planning-level decision label; it does
  not execute anything.
* `HOLD`: non-executing.
* `BLOCK`: non-executing.
* `FAIL_CLOSED`: non-executing.

No decision in v2.0.2 authorizes real-agent integration, runtime integration,
SDK integration, adapter code, parser code, runner code, CLI commands, or
execution behavior.

## Failure Cases

| failure case | required behavior |
| --- | --- |
| dry-run marker missing | `FAIL_CLOSED`; no execution |
| proposal envelope missing | `FAIL_CLOSED`; no execution |
| malformed proposal envelope | `FAIL_CLOSED`; no execution |
| missing `proposal_id` | `FAIL_CLOSED`; no execution |
| missing payload reference | `FAIL_CLOSED`; no execution |
| payload hash mismatch | `FAIL_CLOSED`; no execution |
| unsupported proposal type | `FAIL_CLOSED` or `BLOCK`; no execution |
| requested capability outside selected target boundary | `FAIL_CLOSED` or `BLOCK`; no execution |
| credential scope not empty | `FAIL_CLOSED` or `BLOCK`; no execution |
| user data scope not empty | `FAIL_CLOSED` or `BLOCK`; no execution |
| runtime target mismatch | `FAIL_CLOSED`; no execution |
| evidence reference missing | `FAIL_CLOSED`; no execution |
| trace reference missing | `FAIL_CLOSED`; no execution |
| unknown DHMS decision | `FAIL_CLOSED`; no execution |
| missing DHMS decision | `FAIL_CLOSED`; no execution |
| any attempt to execute during dry-run | `FAIL_CLOSED`; no execution |
| any attempt to call external SDK/runtime/tool/network | `FAIL_CLOSED`; no execution |

## Relationship to Adjacent Milestones

### v2.0.0 Real Agent Integration Preview Planning

v2.0.0 defined the broad planning boundary for a future real-agent integration
preview. v2.0.2 narrows that direction into a proposal-only dry-run contract
for the selected target.

### v2.0.1 Target Selection and Threat Boundary

v2.0.1 selected `local mock-to-real agent boundary` and defined its threat
boundary. v2.0.2 defines what a future dry-run contract must require for that
selected boundary.

### v1.7 Controlled Adapter Skeleton Planning

v1.7 planned a controlled adapter skeleton in prose. v2.0.2 does not implement
or extend that skeleton; it defines dry-run contract expectations before any
adapter planning can become implementation.

### v1.6 External Runtime Handoff Contract Planning

v1.6 planned how DHMS decisions should be handed to an external runtime in the
future. v2.0.2 stays earlier in the lifecycle: it defines dry-run proposal
visibility before any external runtime handoff can exist.

### v0.10 Mock-Agent Runtime Interception Proof

v0.10 proved controlled deterministic mock-agent interception over existing
SQL/File/HTTP proposals. v2.0.2 does not extend that proof into real-agent
runtime interception; it only plans what a future proposal-only dry-run
contract must require.

## Why v2.0.2 Still Does Not Implement

Defining a dry-run contract is not implementing dry-run.

Dry-run planning is not parser support.

Dry-run planning is not runner support.

Dry-run planning is not adapter support.

Dry-run planning is not real-agent integration.

Implementation requires a later explicit milestone with allowed files,
forbidden paths, validation commands, trace expectations, and bounded proof
criteria.

## Public Non-Claims

DHMS v2.0.2 does not claim:

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

`v2.0.3 Non-Executing Real-Agent Proposal Capture Plan`

## Final Verdict

`READY_FOR_V2_0_3_NON_EXECUTING_REAL_AGENT_PROPOSAL_CAPTURE_PLAN`
