# DHMS Real Agent Integration Preview Planning v2.0.0

## Purpose

This document plans a future DHMS real-agent integration preview boundary in
prose only. It defines how DHMS may later approach a controlled real-agent
integration preview while preserving the execution fuse boundary established in
v1.4-v1.7.

v2.0.0 is a planning gate before any real agent integration. It decides what a
future real-agent preview may be allowed to attempt, what it must refuse, and
what evidence must exist before implementation.

v2.0.0 does not add real agent integration, SDK integration, runtime
integration, adapter code, implementation, schema files, runners, CLI commands,
execution behavior, or production runtime claims.

## v2.0.0 Claim

DHMS v2.0.0 plans a future real-agent integration preview boundary without
adding real agent integration, SDK integration, runtime integration, adapter
code, schema files, runners, CLI commands, execution behavior, or production
runtime claims.

## Current Context

v2.0.0 follows the post-v1.3 planning line:

* v1.4 clarified substrate/runtime boundaries.
* v1.5 planned the Agent Proposal Envelope.
* v1.6 planned the External Runtime Handoff Contract.
* v1.7 planned the Controlled Adapter Skeleton boundary.
* v2.0 now plans a future real-agent integration preview, but does not
  implement it.

The v2.0 planning gate exists because real-agent integration crosses a higher
risk boundary than documentation-only planning, static manifests, mock-agent
proofs, and frozen evidence packages.

## Integration Target Principle

Do not integrate multiple agent/runtime targets at once.

The future v2.x implementation line, if separately approved, must choose only
one narrow target first. A single target allows DHMS to define one threat
boundary, one proposal-capture path, one rollback plan, one evidence contract,
and one validation surface before expanding any scope.

Candidate future targets may be discussed only as options:

* local mock-to-real agent boundary
* OpenClaw-style local orchestrator boundary
* Codex-style coding agent proposal boundary
* Claude Code-style coding agent proposal boundary
* MCP tool-call proposal boundary
* E2B-style substrate handoff boundary

None of these targets are integrated in v2.0.0.

## Target-Selection Criteria

The first future integration target should be selected only if it:

* can emit observable proposal before execution
* can be forced into proposal-only / dry-run mode
* can keep execution disabled by default
* can preserve DHMS `RELEASE` / `HOLD` / `BLOCK` / `FAIL_CLOSED`
* can provide evidence and trace continuity
* can fail closed on missing or invalid DHMS decision
* can run locally or in a controlled non-production environment
* does not require production credentials
* does not require user data
* does not require uncontrolled shell/tool/network execution
* can be rolled back cleanly

A target that cannot satisfy these criteria should not be selected for the
first real-agent integration preview.

## Future Preview Boundary

Future DHMS work may define a controlled preview path. v2.0.0 only describes
the conceptual boundary:

```text
real agent or orchestrator proposes action
DHMS receives proposal envelope
DHMS assigns decision
DHMS emits or records handoff boundary
future adapter/skeleton refuses unless decision is RELEASE
future runtime acts only within exact RELEASE boundary
all other states fail closed
```

This flow is not implemented in v2.0.0.

## Preview Constraints

A future real-agent preview must not begin until separately approved and must:

* use a non-production environment
* avoid credentials
* avoid real user data
* avoid production resources
* avoid uncontrolled shell execution
* avoid uncontrolled file mutation
* avoid uncontrolled network access
* avoid broad tool execution
* record evidence before and after decision
* prove rejected paths remain non-executing
* prove missing/invalid/stale decisions fail closed
* preserve rollback plan

These constraints are planning requirements only. v2.0.0 does not enforce them
in code.

## Proposed v2.x Path

The proposed v2.x sequence is planning-only:

```text
v2.0.0 Real Agent Integration Preview Planning
v2.0.1 Real Agent Target Selection and Threat Boundary
v2.0.2 Proposal-Only Dry-Run Contract
v2.0.3 Non-Executing Real-Agent Proposal Capture Plan
v2.0.4 Controlled Real-Agent Preview Proof Planning
v2.0.5 Result Review and Freeze
```

v2.0.0 does not implement any v2.x item.

## Comparison With Prior DHMS Lines

### v0.10 Mock-Agent Runtime Interception Proof

The v0.10 proof used deterministic mock-agent proposals. v2.0 planning
considers a future boundary where a real agent or orchestrator may emit
observable proposals. v2.0.0 does not add real agent runtime interception.

### v1.1 Local Command Proposal Interception

v1.1 froze local command proposals as inert, non-executing evidence. v2.0
planning treats command-like behavior as a high-risk boundary that must remain
disabled unless a later explicit phase narrows the target. v2.0.0 does not add
shell execution or command execution.

### v1.2 Runtime Adapter Boundary Proof

v1.2 froze runtime adapter boundary evidence without real adapter behavior.
v2.0 planning uses that boundary discipline to avoid turning a preview into a
runtime adapter implementation. v2.0.0 does not add runtime adapter
implementation.

### v1.4 Substrate / Runtime Boundary Positioning

v1.4 clarified that DHMS is not a sandbox, E2B replacement, MCP replacement,
runtime adapter, or production runtime. v2.0 planning carries that boundary
forward before any preview target is selected.

### v1.5 Agent Proposal Envelope Planning

v1.5 planned the proposal envelope as the pre-execution object an agent may
submit to DHMS. v2.0 planning assumes a future target must emit or preserve an
observable proposal envelope before execution.

### v1.6 External Runtime Handoff Contract Planning

v1.6 planned how DHMS decisions may be handed off without being weakened. v2.0
planning requires any future preview target to respect `RELEASE`, `HOLD`,
`BLOCK`, and `FAIL_CLOSED` as boundary decisions.

### v1.7 Controlled Adapter Skeleton Planning

v1.7 planned a controlled adapter skeleton that refuses unless the decision is
`RELEASE`. v2.0 planning may later choose one narrow preview target, but
v2.0.0 does not implement a controlled adapter skeleton.

## Why v2.0.0 Remains Planning-Only

Real-agent integration crosses a higher-risk boundary than prior mock-agent and
documentation milestones. A real agent or orchestrator may be connected to
tools, files, network paths, commands, credentials, user data, provider
services, or production-like resources if the boundary is not designed
carefully.

For that reason, v2.0.0 only prepares target-selection and threat-boundary
criteria. It does not choose a target, implement a preview, connect to an
agent, invoke a model, add an adapter, add a parser, add a runner, or add an
execution path.

## Public Boundaries

v2.0.0 keeps real-agent integration preview work in the planning layer:

* no real agent integration
* no real agent runtime interception
* no real LLM execution
* no OpenClaw integration
* no Codex integration
* no Claude integration
* no DeepSeek integration
* no MCP integration
* no E2B integration
* no provider SDK integration
* no agent SDK integration
* no runtime adapter implementation
* no controlled adapter implementation
* no sandbox implementation
* no shell execution
* no command execution
* no file mutation support
* no network execution support
* no arbitrary tool execution
* no schema implementation
* no proposal parser
* no handoff parser
* no adapter parser
* no adapter executor
* no credential handling
* no user data handling
* no production runtime behavior

## Public Non-Claims

DHMS v2.0.0 does not claim:

* production readiness
* real agent integration
* real agent runtime interception
* real LLM execution
* OpenClaw integration
* Codex integration
* Claude integration
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
* handoff parser
* adapter parser
* adapter executor
* production runtime behavior
* credential handling
* user data handling
* universal agent safety
* industry standard status

## Validation Expectations

v2.0.0 should be validated as documentation-only:

* only allowed documentation files should change
* README should not change
* no source code should change
* no validation runner should change
* no benchmark manifest should change
* no example or trace artifact should change
* no schema file should be added
* no parser should be added
* no adapter should be added
* no SDK, runtime integration, runner, CLI command, or execution path should be
  added
* targeted scans should confirm that sensitive phrases appear only as explicit
  non-claims or planning boundaries

## Next Milestone

`v2.0.1 Real Agent Target Selection and Threat Boundary`

## Final Verdict

`READY_FOR_V2_0_1_REAL_AGENT_TARGET_SELECTION_AND_THREAT_BOUNDARY`
