# DHMS Agent Harness v1 Plan

## Purpose

Agent Harness treats an agent as a callable system that returns a behavior trace: input plus memory, context, and tool-state conditions produce a final answer, tool calls, memory reads, state transitions, and side-effect records.

## Phase 1 Scope

Phase 1 builds only a safe mock dry-run vertical slice:

* Agent trace schema
* deterministic `MockAgentAdapter`
* side-effect guard
* `test-agent --mock-agent` CLI path
* local dry-run report generation

## Phase 2 Trace Diagnosis Layer

Phase 2 upgrades the mock dry-run trace dump into a diagnosis-driven trace report. It analyzes final answers, tool calls, memory reads, state transitions, side effects, trace consistency, and deterministic expected-agent properties.

The Phase 2 diagnosis taxonomy covers:

* final answer drift
* tool-call drift
* memory-read drift
* state-transition drift
* side-effect risk
* side-effect guard pass
* unsafe side-effect execution
* trace completeness
* dry-run policy violations
* insufficient trials
* expected-agent property violations
* mock-agent-only caveats

The expected-property checker is deterministic and non-LLM. For refund scenarios, it checks whether the mock agent records verification or policy intent before refund action and whether the refund side effect remains blocked.

Side-effect risk means an action such as refund, send, delete, book, purchase, modify, file write, shell, network, or API mutation was attempted. In Phase 2 this is acceptable only when the dry-run side-effect guard blocks it. Any executed side effect is a Critical safety failure.

## Phase 3 Command Adapter / BYOA Local Agent Protocol

Phase 3 adds a local command adapter for user-owned agents. DHMS sends an `AgentRunRequest` as stdin JSON and expects an `AgentTrace` as stdout JSON using `dhms-agent-command-v1`.

The adapter enforces timeout, validates trace schema, rejects `dry_run=false`, diagnoses executed side effects, and still enriches reports with the Phase 2 trace diagnosis layer.

Phase 3 still does not grant real tool permission. Tool calls and side effects in the returned trace remain evidence for diagnosis, not execution authorization.

HTTP adapters, remote agents, real-agent execution, real tool execution, and agent suite runner remain future work.

## Not Implemented Yet

Phase 1 and Phase 2 do not implement command adapters, HTTP adapters, SaaS/dashboard/server work, real tool execution, real agent execution, or real provider API calls.

## Trace Schema Overview

Agent traces include final answer, tool calls, memory reads, state transitions, side effects, errors, adapter name, dry-run status, mode, input preservation, and trace version.

## Dry-Run Side-Effect Policy

Dry-run is the default and only Phase 1 mode. File writes, email sends, shell commands, network calls, API mutations, purchases, bookings, deletions, refunds, and other external actions may be recorded as attempted but must be blocked.

## Future Phases

* command adapter hardening
* local HTTP adapter
* trace diagnosis on real agents
* agent suite runner
