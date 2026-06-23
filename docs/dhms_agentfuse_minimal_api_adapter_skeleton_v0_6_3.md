# DHMS AgentFuse Minimal API / Adapter Skeleton v0.6.3

## Purpose

v0.6.3 adds the DHMS AgentFuse Minimal API and DHMS AgentFuse Adapter Skeleton.
This phase defines integration shape, not runtime integration. It is part of
the DHMS Execution Fuse Protocol line and remains non-executing.

The intended shape is:

agent intent / runtime event -> runtime request -> tool-call proposal -> DHMS
AgentFuse policy evaluation -> safety decision -> execution gate decision ->
trace object.

No proposal is executed in v0.6.3.

## Naming

Use these names consistently:

* Main brand: `DHMS`
* Protocol name: `DHMS Execution Fuse Protocol`
* Formal long name: `DHMS Agent Execution Fuse Protocol`
* Tool family: `DHMS AgentFuse`
* Benchmark family: `DHMS-AgentFuse-Bench`
* CLI family: `DHMS AgentFuse CLI`
* v0.6.3 API name: `DHMS AgentFuse Minimal API`
* v0.6.3 adapter name: `DHMS AgentFuse Adapter Skeleton`

DHMS AgentFuse is the benchmark, demo, API, and adapter-skeleton tool family
around the DHMS Execution Fuse Protocol.

Preferred public sentence:

`DHMS is an execution fuse protocol for AI agents. DHMS AgentFuse is the benchmark, demo, API, and adapter-skeleton tool family around that protocol.`

## Relationship to v0.6.0 / v0.6.1 / v0.6.2

* v0.6.0 defines the DHMS Execution Fuse Protocol.
* v0.6.1 creates DHMS-AgentFuse-Bench SQL v0.
* v0.6.2 exposes the SQL Fuse demo through a non-executing CLI.
* v0.6.3 defines the safe in-memory API and adapter skeleton.

The current proven line remains the v0.5 SQL Sandbox Execution Fuse. The actual
controlled-release proof remains v0.5.15 existing controlled runtime-path SQL
sandbox release validation.

## API Shape

The minimal API defines these objects:

* `RuntimeRequest`: observable request entering DHMS.
* `ToolCallProposal`: normalized observable proposal.
* `SafetyDecision`: DHMS policy evaluation result.
* `ExecutionGateDecision`: immediate non-executing gate result.
* `AgentFuseTrace`: end-to-end observable trace.

Allowed v0.6.3 safety decisions:

* `BLOCK`
* `FAIL_CLOSED`
* `SANDBOX_HELD`
* `ALLOWLIST_CANDIDATE_HELD`

Allowed v0.6.3 gate states:

* `CLOSED`
* `FAIL_CLOSED`
* `HELD_FOR_REVIEW`
* `HELD_FOR_SANDBOX_BRIDGE`

`ALLOW` is not exposed in v0.6.3. The skeleton communicates that no direct
execution is allowed.

## Non-execution Guarantees

v0.6.3 guarantees:

* no SQL execution
* no SQLite DB creation
* no sandbox creation
* no new execution path
* no allowlist expansion
* no OpenClaw runtime integration
* no DeepSeek/provider integration
* no provider SDK integration
* no agent SDK integration
* no HTTP adapter
* no file adapter
* no shell adapter
* no MCP integration
* no production database support
* no production runtime support

The adapter skeleton is only an in-memory reference shape.

## Example Usage

```python
from dhms_agentfuse import ALLOWLISTED_SQL, run_non_executing_agentfuse_flow

trace = run_non_executing_agentfuse_flow(
    source="demo",
    intent_summary="review allowlisted SQL candidate",
    raw_event={"kind": "runtime_event"},
    tool_name="sql.query",
    tool_type="SQL",
    requested_effect="read_sandbox_candidate",
    payload={"sql": ALLOWLISTED_SQL},
)

print(trace.safety_decision.decision)
print(trace.gate_decision.gate_state)
print(trace.executed)
```

Expected property:

```text
executed=False
```

This example creates a proposal, returns a decision, returns a gate, and builds
a trace. It does not execute SQL.

## How to Validate

```bash
python3 validation/run_dhms_agentfuse_minimal_api_skeleton_smoke.py
```

Existing cross-checks:

```bash
python3 cli.py demo-sql-fuse
python3 validation/run_dhms_agentfuse_bench_sql_v0.py
python3 validation/run_runtime_execution_policy_freeze_stub.py
python3 validation/run_sql_sandbox_runtime_first_actual_controlled_release.py
python3 validation/run_sql_safety_temp_sqlite_mutation_block_test.py
```

## Not Claimed

v0.6.3 does not claim:

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
* file/shell/MCP policy
* a production SDK
* a production-ready agent runtime
* an MCP replacement

## Next Milestone

Recommended next milestone:

`v0.7.0 Public Protocol Package`

Final verdict:

`READY_FOR_V0_7_0_PUBLIC_PROTOCOL_PACKAGE`
