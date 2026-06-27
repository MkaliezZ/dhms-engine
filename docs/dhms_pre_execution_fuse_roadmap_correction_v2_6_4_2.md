# DHMS Pre-Execution Fuse Roadmap Correction v2.6.4.2

## Title and Metadata

* Milestone: `v2.6.4.2 Pre-Execution Fuse Roadmap Correction`
* Status: documentation-only roadmap correction
* Previous milestone: `v2.6.4.1 README Current Status Sync`
* Corrected next milestone: `v2.7.0 Minimal Pre-Execution Fuse Loop Planning`

## Purpose

v2.6.4.2 corrects the DHMS post-v2.6 roadmap so the project pivots back to its
core identity: `Execution Fuse Protocol`.

The corrected roadmap makes v2.7 the start of a minimal pre-execution fuse loop,
not another source-surface planning line.

## Current Status

DHMS has frozen multiple evidence chains for inert proposals, emit-only
contracts, shape fixtures, deterministic validators, and result-review docs.
Those artifacts are useful domain knowledge, but they are not enough to prove
DHMS as an execution fuse.

DHMS is incomplete as an execution fuse unless it can prove pre-execution
interception.

## Why This Correction Exists

The post-v2.6 roadmap had started extending compatibility-shaped work instead
of moving toward the core fuse loop.

The old route was:

`trace -> normalize -> offline analysis -> dry-run -> package`

That route risks producing a black-box analysis system instead of an execution
fuse.

The corrected route is:

`proposal enters -> DHMS gate evaluates before execution -> decision emitted -> executor handoff allowed or blocked -> evidence recorded`

## Prior Route Errors

The previous route over-prioritized inert fixtures, emit-only contracts,
shape-only boundaries, README/status sync, and freeze documents.

The trace -> normalization -> offline analysis -> dry-run route would have
produced a black-box analysis system instead of an execution fuse.

The previous Source Surface Planning direction delayed the first real
pre-execution gate and risked more shell-building.

The standalone LangChain-style compatibility line repeated the old pattern:
looking close to LangChain while avoiding real framework contact.

## What Remains Useful from v2.3-v2.6

The old work is partially reusable as domain knowledge:

* proposal fields
* fail_closed_reason taxonomy
* threat categories
* deterministic validation habits
* inert fixture discipline
* non-execution boundary wording

v2.3-v2.6 solved "what to block."

v2.7 must start solving "how to block before execution."

## What Must Stop Expanding

The inert fixture, emit-only contract, shape-only boundary, README/status sync,
and freeze-doc lines should stop expanding as the mainline.

Future inert or shape work must support a pre-execution gate proof instead of
replacing it.

## Old Route vs Corrected Route

Old route:

`trace -> normalize -> offline analysis -> dry-run -> package`

Corrected route:

`proposal enters -> DHMS gate evaluates before execution -> decision emitted -> executor handoff allowed or blocked -> evidence recorded`

## Non-Negotiable Acceptance Standard

From v2.7 onward, no milestone line may freeze unless all three questions are
answered with explicit evidence:

1. Did DHMS make a decision before executor/tool handoff?
2. Was the unsafe proposal/tool-call blocked?
3. Is there evidence that the executor/tool did not receive or execute the unsafe request?

The v2.7 proof marker must include:

```text
DHMS_PRE_EXECUTION_FUSE_LOOP_PROOF_PASS
dhms_decision=FAIL_CLOSED
executor_handoff_allowed=false
execution_authorized=false
mock_executor_received=false
mock_executor_invocations=0
sql_execution_attempts=0
db_connections=0
```

## Corrected Strategic Roadmap

* v2.7.x Minimal Pre-Execution Fuse Loop
* v2.8.x Controlled Agent Proposal Gate
* v2.9.x Tool-Call Interception Surface with LangChain-Style Shape
* v3.0.x Local Interception CLI
* v3.1.x Real LangChain Toy-Tool Callback Boundary
* v3.2.x SQL Agent Pre-Execution Boundary Re-Entry
* v3.3.x Public MVP Packaging
* v3.4.x Next Runtime Boundary Decision

## v2.7.x Minimal Pre-Execution Fuse Loop

Milestones:

* v2.7.0 Minimal Pre-Execution Fuse Loop Planning
* v2.7.1 Proposal Gate Contract + Fixtures
* v2.7.2 Gate Runner + Mock Executor
* v2.7.3 Pre-Execution Interception Proof
* v2.7.4 Result Review and Freeze
* v2.7.4.1 README Current Status Sync

v2.7 must prove:

`dangerous LangChain-SQL-agent-like proposal enters before executor handoff -> DHMS gate evaluates first -> DHMS returns FAIL_CLOSED -> executor_handoff_allowed=false -> execution_authorized=false -> mock_executor_received=false -> sql_execution_attempts=0 -> db_connections=0`

v2.7 remains forbidden from real LangChain import, SQLDatabaseToolkit, real SQL
execution, real DB connection, model API, KerniQ, E2B, network/subprocess,
credential/user data, and production claims.

v2.7 must produce a terminal proof screenshot by v2.7.3. There is no v2.7
freeze without `FAIL_CLOSED` and `mock_executor_received=false` evidence.

## v2.8.x Controlled Agent Proposal Gate

Milestones:

* v2.8.0 Controlled Agent Proposal Gate Planning
* v2.8.1 Agent Proposal Envelope Contract
* v2.8.2 Mock Agent Proposal Fixtures
* v2.8.3 Mock Agent -> Gate -> Executor Proof
* v2.8.4 Result Review and Freeze
* v2.8.4.1 README Current Status Sync

v2.8 must prove:

```text
mock_agent_emitted=true
dhms_gate_observed_before_execution=true
dhms_decision=FAIL_CLOSED
executor_handoff_allowed=false
mock_executor_received=false
```

## v2.9.x Tool-Call Interception Surface with LangChain-Style Shape

Milestones:

* v2.9.0 Tool-Call Interception Surface Planning
* v2.9.1 Tool-Call Gate Contract
* v2.9.2 Tool-Call Gate Fixtures including LangChain-Style Shapes
* v2.9.3 Tool-Call Gate Runner
* v2.9.4 Tool-Call Interception Proof
* v2.9.5 Result Review and Freeze
* v2.9.5.1 README Current Status Sync

v2.9 must prove:

```text
DHMS_TOOL_CALL_INTERCEPTION_PROOF_PASS
dhms_decision=FAIL_CLOSED
tool_handoff_allowed=false
mock_tool_executor_received=false
tool_invocation_performed=false
```

v2.9 folds LangChain-style shape handling into the tool-call interception
surface. It must not create a separate no-import LangChain-style compatibility
line.

## v3.0.x Local Interception CLI

Milestones:

* v3.0.0 Local Interception CLI Planning
* v3.0.1 Local Interception CLI Contract
* v3.0.2 Local Interception CLI Implementation
* v3.0.3 Local Interception CLI Proof
* v3.0.4 Result Review and Freeze
* v3.0.4.1 README Current Status Sync

Command shape:

```bash
python3 cli.py gate-proposal examples/proposals/sql_execution_request.json
```

v3.0 must prove:

```text
DHMS_LOCAL_INTERCEPTION_CLI_PROOF_PASS
dhms_decision=FAIL_CLOSED
executor_handoff_allowed=false
mock_executor_received=false
```

## v3.1.x Real LangChain Toy-Tool Callback Boundary

Milestones:

* v3.1.0 Real LangChain Callback Boundary Planning
* v3.1.1 Real LangChain Callback Interception Contract
* v3.1.2 Controlled LangChain Toy-Tool Interception
* v3.1.3 Real LangChain Toy-Tool Interception Proof
* v3.1.4 Result Review and Freeze
* v3.1.4.1 README Current Status Sync

v3.1 is the first real LangChain import line and is Super High risk. It is
limited to toy-tool callback interception.

v3.1 forbids SQLDatabaseToolkit, SQL execution, DB access, credentials, user
data, and production runtime.

v3.1 must prove:

```text
DHMS_REAL_LANGCHAIN_TOY_TOOL_INTERCEPTION_PROOF_PASS
dhms_decision=FAIL_CLOSED
tool_execution_performed=false
```

## v3.2.x SQL Agent Pre-Execution Boundary Re-Entry

Milestones:

* v3.2.0 SQL Agent Pre-Execution Boundary Planning
* v3.2.1 SQL Tool Handoff Gate Contract
* v3.2.2 SQL Tool Handoff Fixtures
* v3.2.3 Controlled SQL Tool Handoff Gate
* v3.2.4 SQL Tool Handoff Interception Proof
* v3.2.5 Result Review and Freeze
* v3.2.5.1 README Current Status Sync

v3.2 must prove:

```text
DHMS_SQL_TOOL_HANDOFF_GATE_PROOF_PASS
dhms_decision=FAIL_CLOSED
sql_tool_handoff_allowed=false
mock_sql_executor_received=false
sql_execution_attempts=0
db_connections=0
```

## v3.3.x Public MVP Packaging

Milestones:

* v3.3.0 Public MVP Packaging Planning
* v3.3.1 Public MVP Demo Contract
* v3.3.2 Public MVP Demo Pack
* v3.3.3 README Reposition
* v3.3.4 MVP Freeze

The MVP must include:

* gate-proposal command
* dangerous proposal sample
* FAIL_CLOSED output
* mock executor blocked evidence
* copy-paste reproduction command
* screenshot guide

## v3.4.x Next Runtime Boundary Decision

Possible future targets:

* real LangChain SQL Agent callback
* OpenClaw / Claude Code proposal interception
* KerniQ proposal gate
* E2B sandbox handoff gate
* local command executor gate
* file operation gate
* HTTP/network operation gate

## Deleted Roadmap Line

Deleted as a standalone line:

`LangChain-Style Pre-Tool Interception as a standalone no-import milestone line`

Reason:

It repeats the old pattern: looks close to LangChain, but avoids importing
LangChain.

Replacement:

LangChain-style shape fixtures belong in v2.9. Real LangChain toy-tool callback
moves up to v3.1.

## README Update

README is updated to:

* Current milestone: `v2.6.4.2 Pre-Execution Fuse Roadmap Correction`
* Previous milestone: `v2.6.4.1 README Current Status Sync`
* Corrected next recommended milestone: `v2.7.0 Minimal Pre-Execution Fuse Loop Planning`

README now states that the next line is pre-execution fuse loop planning, not
source-surface planning.

## Package Index Update

The package index links this roadmap correction document:

`docs/dhms_pre_execution_fuse_roadmap_correction_v2_6_4_2.md`

## Roadmap Update

The roadmap marks v2.6.4.2 as current/completed and sets the next recommended
milestone to:

`v2.7.0 Minimal Pre-Execution Fuse Loop Planning`

It includes the corrected strategic roadmap from v2.7.x through v3.4.x.

## Validation Commands

The following validation commands are expected for this documentation-only
correction:

```bash
python3 validation/run_dhms_langchain_sql_agent_adapter_skeleton_shape_fixture_validation_v0.py
python3 validation/run_dhms_langchain_sql_agent_emit_only_adapter_fixture_validation_v0.py
python3 validation/run_dhms_third_party_sql_agent_threat_fixture_validation_v0.py
python3 validation/run_dhms_sql_agent_local_emit_only_fixture_validation_v0.py
python3 validation/run_dhms_bounded_local_mock_to_real_fixture_validation_v0.py
python3 validation/run_dhms_bounded_local_proposal_emitter_candidate_fixture_validation_v0.py
python3 -m json.tool benchmarks/dhms_langchain_sql_agent_adapter_skeleton_shape_v0/shape_fixtures.json >/dev/null
python3 -m json.tool benchmarks/dhms_langchain_sql_agent_emit_only_adapter_v0/adapter_boundary_fixtures.json >/dev/null
git diff --check
git diff --cached --check
```

## Targeted Scan Summary

Targeted scans should confirm no new runtime or integration patterns in changed
files.

Allowed hits are limited to non-claim wording, deleted-route explanation,
future roadmap labels, prohibited-boundary references, validation command text,
and roadmap correction language.

## Acceptance Checklist

* Only allowed files are changed.
* README is modified only for roadmap correction, current status, and next milestone sync.
* v2.6.4.1 sync doc is not modified.
* v2.6.4 freeze doc is not modified.
* v2.6.3 validator is not modified.
* v2.6.2 shape fixture manifest is not modified.
* v2.6.0-v2.6.3 evidence docs are not modified.
* v2.5 artifacts are not modified.
* Existing validators are not modified.
* Existing fixtures are not modified.
* Source/schema/examples/CLI/dependency files are not modified.
* No source file is added.
* No adapter or skeleton implementation is added.
* No schema is added.
* No parser, runner, or CLI is added.
* No LangChain install/import/invocation/integration is added.
* No SQLDatabaseToolkit usage is added.
* No SQL execution or DB integration is added.
* No model API integration is added.
* No KerniQ/E2B integration is added.
* No release or tag is created.

## Final Verdict

`READY_FOR_V2_7_0_MINIMAL_PRE_EXECUTION_FUSE_LOOP_PLANNING`
