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

## Not Implemented Yet

Phase 1 does not implement command adapters, HTTP adapters, SaaS/dashboard/server work, real tool execution, or real provider API calls.

## Trace Schema Overview

Agent traces include final answer, tool calls, memory reads, state transitions, side effects, errors, adapter name, dry-run status, mode, input preservation, and trace version.

## Dry-Run Side-Effect Policy

Dry-run is the default and only Phase 1 mode. File writes, email sends, shell commands, network calls, API mutations, purchases, bookings, deletions, refunds, and other external actions may be recorded as attempted but must be blocked.

## Future Phases

* command adapter
* local HTTP adapter
* trace diagnosis
* agent suite runner
