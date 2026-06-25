# DHMS Substrate Boundary / Runtime Boundary Planning v1.4.0

## Purpose

This document adds the v1.4.0 planning milestone for DHMS substrate boundary
and runtime boundary positioning after the confirmed v1.3 Runtime Adapter
Boundary Public Evidence Package.

DHMS is an execution fuse protocol. This document clarifies how DHMS relates to
execution substrates, runtime systems, tool connection protocols, SDKs,
guardrails, policy engines, observability systems, and approval workflows.

v1.4.0 is documentation and planning only. It does not add implementation, SDK
integration, adapter code, runners, CLI commands, schemas, execution behavior,
or production runtime claims.

## v1.4.0 Claim

DHMS v1.4.0 plans the substrate and runtime boundary positioning for DHMS after
the v1.3 Runtime Adapter Boundary Public Evidence Package without adding
substrate integration, runtime adapter implementation, SDK integration,
execution behavior, or production runtime claims.

## Current Context After v1.3 Release

The v1.3 Runtime Adapter Boundary Public Evidence Package is released and
confirmed. That package freezes the runtime adapter boundary evidence line as
inert, deterministic, non-production evidence. It does not create real runtime
adapter integration.

v1.4.0 starts the next planning direction: explain where DHMS sits relative to
the substrate or runtime that may eventually receive a decision. The purpose is
to prevent a category mistake: DHMS is not the same layer as a sandbox, E2B,
MCP, an agent SDK, a guardrail, a policy engine, an observability backend, or a
human approval queue.

## Substrate / Runtime Boundary Problem

Agent systems often mix several questions:

* How is a tool connected?
* Where can execution happen?
* Which SDK owns the agent workflow?
* Which system records telemetry?
* Which policy engine evaluates rules?
* Which approval workflow asks a human?
* Whether the proposed action should cross into execution at all.

DHMS focuses on the final question. It sits before execution and evaluates the
observable proposal boundary: what the agent is proposing to do, what decision
DHMS assigns, whether the proposal is released, held, blocked, or failed
closed, and what evidence must be recorded.

## Core Distinction: Sandbox / E2B vs DHMS

```text
Sandbox / E2B asks:
Where can this action run safely?

DHMS asks:
Should this proposed action be released at all, under what boundary, and with what evidence?
```

This distinction is the center of v1.4.0. A sandbox or E2B-style substrate may
be useful for isolating execution. DHMS decides whether a proposal should be
released toward any execution boundary, held for more review, blocked, or
failed closed.

## What DHMS Owns

DHMS owns the execution fuse boundary:

* proposal observation before execution
* safety decision assignment
* release / hold / block / fail-closed boundary
* evidence requirements
* trace expectations
* non-claim boundaries
* fail-closed behavior for unsupported or unknown proposals

DHMS should remain able to say that a proposal is not allowed to cross into
execution even if an external runtime, substrate, SDK, or tool connector could
technically run it.

## What DHMS Does Not Own

DHMS does not own:

* sandbox hosting
* E2B execution
* MCP tool connection
* agent SDK orchestration
* policy-engine replacement
* observability storage
* production runtime hosting
* credential management
* provider SDK execution
* real LLM execution

DHMS is not a sandbox. DHMS is not an MCP replacement. DHMS is not a runtime
adapter. DHMS is not a production runtime.

## Comparison Matrix

| Category | Primary question | What it controls | What it does not control | How DHMS relates to it |
| --- | --- | --- | --- | --- |
| Sandbox | Where can code or tools run with isolation? | Execution environment, isolation boundary, disposable runtime constraints | Whether a proposed action should be released before execution, evidence contract, DHMS trace expectations | DHMS may decide whether a proposal is eligible to enter a sandbox path, but v1.4.0 adds no sandbox implementation. |
| E2B | Where can an agent action run in a hosted sandbox-like substrate? | External substrate execution environment and runtime affordances | DHMS policy ownership, release/hold/block/fail-closed decision boundary, DHMS evidence requirements | DHMS can conceptually sit before an E2B-like substrate, but v1.4.0 adds no E2B integration. |
| MCP | How are models or agents connected to tools and resources? | Tool/resource connection shape and invocation interface | Whether a proposed tool action should be released, held, blocked, failed closed, or traced by DHMS | MCP connects tools; DHMS controls execution boundaries. v1.4.0 adds no MCP integration. |
| Agent SDK | How is an agent workflow, memory, state, or tool loop orchestrated? | Agent orchestration, tool definitions, workflow structure | Independent DHMS policy ownership and fail-closed release boundary | DHMS should remain SDK-agnostic. v1.4.0 adds no agent SDK integration. |
| Guardrails | How are inputs, outputs, or policy constraints filtered? | Input/output checks, content constraints, policy filters | Full execution proposal lifecycle, controlled release evidence, external state verification, trace contract | DHMS complements guardrails by focusing on proposed action crossing into execution. |
| Policy Engine | Which rules evaluate a decision? | Rule evaluation and policy logic | Proposal capture, execution gate boundary, controlled release path, evidence and trace lifecycle | DHMS may use policy-like decisions but is not only a policy engine. v1.4.0 adds no policy-engine replacement. |
| Observability | What happened, and how is it recorded? | Logs, metrics, traces, telemetry storage, dashboards | Pre-execution release decision, fail-closed gate, controlled-release requirements | DHMS produces evidence and trace expectations, but v1.4.0 adds no observability backend. |
| Human Approval Workflow | Should a human approve a high-risk action? | Human review and approval queue | Tiered execution fuse policy, low-risk fast paths, blocked/fail-closed defaults, full evidence contract | Human approval can be one HOLD path, but DHMS is not just a human approval workflow. |

## Future Handoff Model

Future DHMS work may define a handoff contract from a DHMS decision to an
external runtime or substrate. v1.4.0 only describes the conceptual flow:

```text
agent proposes action
DHMS observes proposal
DHMS assigns RELEASE / HOLD / BLOCK / FAIL_CLOSED
DHMS records evidence and trace expectations
external runtime may only proceed according to DHMS decision boundary
```

This flow is not implemented in v1.4.0.

The key rule is that an external runtime must not reinterpret a DHMS `BLOCK` or
`FAIL_CLOSED` decision as `RELEASE`. A future runtime handoff contract should
preserve the DHMS decision boundary rather than treating DHMS as advisory
logging.

## Public Boundaries

v1.4.0 keeps DHMS in a planning layer:

* no substrate integration
* no runtime adapter implementation
* no SDK integration
* no runner
* no CLI command
* no schema
* no execution path
* no sandbox implementation
* no E2B integration
* no MCP integration
* no Codex integration
* no Claude integration
* no OpenClaw integration
* no DeepSeek integration
* no provider SDK integration
* no agent SDK integration
* no production runtime behavior

## Public Non-Claims

DHMS v1.4.0 does not claim:

* production readiness
* real agent runtime integration
* real LLM execution
* E2B integration
* MCP integration
* Codex integration
* Claude integration
* OpenClaw integration
* DeepSeek integration
* provider SDK integration
* agent SDK integration
* runtime adapter implementation
* sandbox implementation
* policy engine replacement
* observability backend
* command execution
* arbitrary tool execution
* production runtime behavior
* universal agent safety
* industry standard status

## Validation Expectations

v1.4.0 should be validated as documentation-only:

* only allowed documentation files should change
* no source code should change
* no validation runner should change
* no benchmark manifest should change
* no example or trace artifact should change
* no CLI command should be added
* no SDK, adapter, runner, schema, or execution path should be added
* targeted scans should confirm that any sensitive phrases appear only as
  explicit non-claims or planning boundaries

## Next Milestone

`v1.5.0 Agent Proposal Envelope Planning`

## Final Verdict

`READY_FOR_V1_5_0_AGENT_PROPOSAL_ENVELOPE_PLANNING`
