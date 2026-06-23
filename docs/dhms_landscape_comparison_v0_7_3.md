# DHMS Landscape / Comparison Doc v0.7.3

## Purpose

v0.7.3 defines DHMS's position relative to adjacent agent infrastructure and
safety categories.

This is not a competitive attack document. It is not a current market report.
It is a conceptual boundary document that explains where DHMS fits and where it
does not fit.

DHMS is complementary to many adjacent tools. v0.7.3 does not add runtime
capability, does not add execution behavior, does not add adapters, and does
not expand the v0.5 SQL Sandbox Execution Fuse proof line.

## Core Positioning

DHMS is an execution fuse protocol for AI agents.

MCP helps agents connect to tools. DHMS focuses on whether an agent action is
allowed to cross into execution, and under what evidence, gate, review,
sandbox, verification, and trace requirements.

DHMS sits between agent intent and real-world execution. It focuses on
observable runtime requests, tool-call proposals, safety decisions, execution
gates, controlled release, verification, and trace.

DHMS does not require hidden chain-of-thought access. DHMS does not require
provider SDK policy ownership. DHMS policy ownership remains with DHMS.

## Comparison Table

| Category | Primary focus | What it usually protects or standardizes | What it usually does not fully standardize | How DHMS relates | Complementary or overlapping? |
| --- | --- | --- | --- | --- | --- |
| MCP / tool connection protocols | Connecting models or agents to tools, resources, and capabilities | Tool discovery, tool schemas, resource access patterns, connector shape | Whether a proposed action should cross into execution, release evidence, teardown verification | DHMS can sit around tool proposals and decide whether execution is blocked, held, sandboxed, or traced | Complementary |
| Agent SDKs / orchestration frameworks | Building agent workflows, state, tools, memory, and execution loops | Agent composition, tool registration, event flow, orchestration logic | Independent execution policy ownership and fail-closed release chains | DHMS should remain SDK-agnostic and should not depend on an SDK as the final execution authority | Complementary with limited overlap |
| Guardrails / policy filters | Filtering inputs, outputs, content, prompts, or policy violations | Content constraints, policy checks, prompt/output boundaries | Full execution proposal lifecycle, controlled release, external state verification, teardown trace | DHMS complements guardrails by focusing on execution boundary decisions and evidence | Complementary with some policy overlap |
| Sandboxes | Isolating execution from broader systems | Runtime isolation, disposable environments, limited execution scope | Deciding when execution is allowed, held, reviewed, or verified | DHMS defines whether and how a sandbox is used; sandboxing is one mechanism in the fuse path | Complementary |
| AI security / AppSec scanners | Finding vulnerabilities, risky code, prompt risks, governance gaps, or application issues | Codebases, applications, dependencies, prompts, deployments, governance surfaces | Per-action execution release gates and trace contracts for agent runtime proposals | DHMS focuses on agent actions crossing into execution rather than general application security | Complementary |
| Observability / logging / tracing systems | Recording behavior and system state | Logs, spans, metrics, traces, audit events | Safety decisions and fail-closed execution gates before or around execution | DHMS produces traceable evidence, but its trace is part of the safety contract, not only a log | Complementary with trace overlap |
| Human approval workflows | Asking a person to approve or deny actions | High-risk review, accountability, human-in-the-loop control | Automated tiered routing, sandbox verification, teardown verification, non-human fast paths | DHMS can include human review as one L3 path, but should not make every action a human approval task | Complementary |
| Policy engines | Evaluating rules against structured inputs | Rule decisions, authorization logic, constraints | Proposal capture, controlled release, sandbox execution result verification, trace lifecycle | DHMS may use or interoperate with policy engines later, but DHMS is a broader execution fuse lifecycle | Complementary with policy overlap |
| DHMS Execution Fuse Protocol | Controlling whether observable agent actions cross into execution | Runtime proposals, fail-closed decisions, gates, bridge/review, controlled release, verification, trace | It does not currently provide arbitrary tool execution, production runtime support, or universal safety | DHMS defines the execution boundary layer itself | Category under definition |

## MCP and DHMS

MCP connects tools; DHMS controls execution boundaries.

MCP-style systems are primarily about connecting models or agents to tools,
resources, and external capabilities. DHMS is not an MCP replacement. DHMS can
be positioned as a safety and control layer that evaluates whether a proposed
action should cross into execution.

Future DHMS work may define MCP-facing policy or adapter concepts, but v0.7.3
does not implement MCP integration.

## Guardrails and DHMS

Guardrails often focus on input filtering, output filtering, content policy,
prompt constraints, or policy checks. DHMS focuses on observable action
proposals and execution gate outcomes.

DHMS does not replace guardrails. DHMS can complement guardrails by adding
execution boundary decisions, controlled-release logic, external state
verification, teardown verification, and trace evidence.

## Agent SDKs and DHMS

Agent SDKs often help define tools, workflows, state, memory, and
orchestration. DHMS should remain SDK-agnostic where possible.

DHMS policy owner remains DHMS. DHMS should not depend on an agent SDK being
the final execution authority. v0.7.3 does not add SDK integration.

## Sandboxes and DHMS

Sandboxes isolate execution. DHMS defines when execution should be blocked,
held, reviewed, sandboxed, controlled-released, verified, and traced.

A sandbox is a mechanism. DHMS is the execution fuse decision layer around
whether and how a sandbox is used.

The v0.5.15 SQL sandbox controlled release is the first proof line. v0.7.3
does not add new sandbox execution.

## Observability and DHMS

Observability tools record what happened. DHMS records traceable evidence, but
also makes safety and gate decisions before or around execution.

DHMS trace is not only logging. It is part of the execution fuse contract.
DHMS can complement observability systems by producing structured evidence for
each blocked, held, failed-closed, or controlled-release path.

## Human Approval and DHMS

Human approval is useful for high-risk actions. DHMS should not route every
action to human review.

The DHMS Risk-Tiered Fuse Policy enables fast paths for lower-risk actions and
hold, review, sandbox, or block paths for higher-risk actions. Human review is
one possible L3 path, not the whole protocol.

## AI Security, AppSec, and DHMS

Many security tools focus on applications, prompts, codebases,
vulnerabilities, or governance. DHMS focuses on agent action crossing into
real-world execution.

Code security protects codebases. DHMS protects execution boundaries.

DHMS does not replace AppSec or AI security platforms. v0.7.3 does not make
vendor-specific claims and does not define a current market map.

## Policy Engines and DHMS

Policy engines can evaluate rules. DHMS includes policy-like decisions, but
also defines proposal capture, gate decision, controlled release, verification,
and trace.

DHMS can use or interoperate with policy engines in the future, but v0.7.3
does not implement one.

## DHMS Unique Focus

DHMS focuses on:

* observable runtime request capture
* tool-call proposal normalization
* fail-closed default behavior
* execution gate decisions
* controlled-release path
* sandbox verification
* external state verification
* teardown verification
* traceable evidence contract
* benchmark and examples through DHMS AgentFuse
* risk-tiered fuse policy direction

## Current Maturity Level

DHMS is an early public protocol package. DHMS has a SQL proof line, a
benchmark, a CLI demo, a minimal API skeleton, protocol examples, and a
risk-tiered policy draft.

DHMS is not production-ready. DHMS is not an industry standard. DHMS is not yet
widely adopted. DHMS is not a universal agent safety system.

## Not Claimed

v0.7.3 does not claim:

* arbitrary SQL support
* direct SQL execution
* mutation SQL execution
* production DB safety
* production SQL agent support
* user data safety
* credentialed DB execution
* network DB execution
* OpenClaw runtime integration
* DeepSeek/provider integration
* provider SDK integration
* agent SDK integration
* HTTP adapter
* file adapter
* shell adapter
* MCP integration
* MCP replacement
* a production SDK
* a production-ready agent runtime
* universal agent safety
* an industry standard
* a current market map

## Next Milestone

Recommended next milestone:

`v0.7.4 Contribution Guide / Case Format`

Final document verdict:

`READY_FOR_V0_7_4_CONTRIBUTION_GUIDE_CASE_FORMAT`
