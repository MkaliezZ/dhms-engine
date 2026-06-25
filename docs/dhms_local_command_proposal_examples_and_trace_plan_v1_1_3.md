# DHMS Local Command Proposal Examples and Trace Plan v1.1.3

## Purpose

v1.1.3 adds inert local command proposal examples and a non-executing trace
plan for the DHMS Local Command-Agent Interception line.

This milestone helps readers understand how local command proposals are
observed as data, classified, assigned `HOLD`, `BLOCK`, or `FAIL_CLOSED`, and
represented in trace evidence before any future controlled proof phase.

This milestone is documentation/data-only.

## Paths

Examples:

`examples/dhms_local_command_proposals_v0/README.md`

`examples/dhms_local_command_proposals_v0/inert_examples.json`

Trace plan:

`trace_examples/dhms_local_command_proposals_v0/trace_plan.json`

Existing manifest:

`benchmarks/dhms_local_command_proposals_v0/cases.json`

Existing benchmark runner:

`validation/run_dhms_local_command_proposal_benchmark_v0.py`

## Relationship to v1.1.1 Manifest

v1.1.1 created the static inert local command proposal manifest with 14 cases.
The v1.1.3 examples link to that manifest but do not modify it.

The examples remain inert summaries. They are not shell tutorials, command
instructions, executable examples, or terminal recipes.

## Relationship to v1.1.2 Benchmark

v1.1.2 added a non-executing benchmark validator over the static manifest.
v1.1.3 does not modify that runner and does not add a new benchmark runner.

The existing v1.1.2 benchmark remains the validation path for manifest
structure and non-execution expectations.

## Example Coverage Summary

`inert_examples.json` contains 7 compact examples covering:

* read-like proposal held
* metadata proposal held
* destructive filesystem proposal blocked
* credential or environment leakage proposal blocked
* command chaining ambiguity failed closed
* network side-effect proposal blocked
* malformed or empty proposal failed closed

Allowed policy decisions are limited to:

* `HOLD`
* `BLOCK`
* `FAIL_CLOSED`

`RELEASE` is not used.

## Trace Stage Model

The trace plan uses these stages:

* `proposal_observed`
* `proposal_normalized`
* `risk_classified`
* `policy_decision_assigned`
* `trace_evidence_recorded`
* `execution_not_performed`

The trace plan maps all 14 manifest case IDs to expected trace behavior.

## Non-Execution Invariants

The trace plan preserves these invariants:

* `command_strings_executed_count=0`
* `argv_executed_count=0`
* `shell_execution_count=0`
* `subprocess_execution_count=0`
* `terminal_execution_count=0`
* no command runner added
* no benchmark runner added
* no CLI command added
* no `RELEASE` decision used

## Why `RELEASE` Is Still Not Used

The v1.1 local command line has not yet reached a controlled proof phase.
Command-like proposals can carry destructive, credential, process, network,
and ambiguity risks even when they appear read-like.

Therefore v1.1.3 keeps examples and traces at the proposal, decision, and
trace-planning layer. `RELEASE` remains out of scope.

## Validation Expectations

Run:

```bash
python3 -m json.tool examples/dhms_local_command_proposals_v0/inert_examples.json > /tmp/dhms_local_command_inert_examples_v0_normalized.json
python3 -m json.tool trace_examples/dhms_local_command_proposals_v0/trace_plan.json > /tmp/dhms_local_command_trace_plan_v0_normalized.json
python3 validation/run_dhms_local_command_proposal_benchmark_v0.py
```

Expected benchmark marker:

`DHMS_LOCAL_COMMAND_PROPOSAL_BENCHMARK_PASS`

## Public Frozen Claim Preservation

`DHMS provides a public evidence package for an execution fuse protocol proof chain covering SQL, File, HTTP, and controlled deterministic mock-agent runtime interception under documented non-production boundaries.`

## v1.1 Examples / Trace Planning Claim

`DHMS v1.1 includes inert examples and a non-executing trace plan for static local command proposals under fail-closed, non-production boundaries.`

## Public Non-Claims

DHMS v1.1.3 does not claim:

* production readiness
* real agent runtime interception
* real LLM execution
* real shell execution safety
* arbitrary command execution support
* arbitrary terminal support
* arbitrary tool execution
* credential handling
* user data safety certification
* production filesystem safety
* production process safety
* production network safety
* MCP integration
* E2B integration
* Codex integration
* Claude integration
* OpenClaw integration
* DeepSeek integration
* provider SDK integration
* agent SDK integration

## Documentation / Data-Only Confirmation

v1.1.3 is documentation/data-only. It adds inert examples and an inert trace
plan.

It does not add command execution, shell execution, subprocess execution,
terminal integration, command runners, benchmark runners, CLI commands, CLI
wrappers, executable examples, executable trace examples, schema files,
manifest changes, benchmark runner changes, execution behavior changes, proof
semantic changes, new proposal type implementations, or new SQL/File/HTTP
execution paths.

## Repository Safety Confirmation

No files are deleted, renamed, or moved for v1.1.3. No directories are removed.
No GitHub release is created, edited, or deleted. No tag is created, modified,
deleted, or pushed.

## Next Milestone

Recommended next milestone:

`v1.1.4 Controlled Mock-Agent Local Command Interception Proof`

## Final Verdict

`READY_FOR_V1_1_4_CONTROLLED_MOCK_AGENT_LOCAL_COMMAND_INTERCEPTION_PROOF`
