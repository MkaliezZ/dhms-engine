# DHMS AgentFuse Protocol Examples v0.7.1

## Purpose

v0.7.1 adds public protocol examples for DHMS AgentFuse. The examples show how
DHMS AgentFuse represents runtime requests, tool-call proposals, safety
decisions, execution gate decisions, trace objects, and no-execution outcomes.

The examples are non-executing. They are not production adapters and do not add
execution capability.

DHMS is an execution fuse protocol for AI agents. DHMS AgentFuse is the
benchmark, demo, API, and adapter-skeleton tool family around that protocol.

## Relationship to v0.7.0

v0.7.0 packaged the completed v0.6 line into a public protocol package.
v0.7.1 adds concrete examples for readers and future contributors. It does not
add execution capability, alter the benchmark, alter the CLI demo, or alter the
minimal API semantics.

## Example Map

* `examples/dhms_agentfuse/sql_fuse_allowlisted_candidate_example.py`
* `examples/dhms_agentfuse/sql_mutation_blocked_example.py`
* `examples/dhms_agentfuse/unsupported_non_sql_proposal_example.py`
* `examples/dhms_agentfuse/trace_examples.json`

## Example 1: SQL Fuse Allowlisted Candidate Held

The allowlisted candidate example represents the known SQL SELECT candidate:

```sql
SELECT id, label, status FROM toy_accounts ORDER BY id;
```

The example creates a runtime request, creates a tool-call proposal, evaluates
the proposal, applies the execution gate, and builds an AgentFuse trace. The
candidate is held and release-eligible according to the current minimal API,
but it is not directly executed.

Expected properties:

* `executed=false`
* `execution_allowed=false`
* `direct_execution_allowed=false`
* no SQL execution
* no SQLite database creation

## Example 2: SQL Mutation Blocked

The mutation example represents this SQL as inert data:

```sql
DELETE FROM toy_accounts WHERE id = 1;
```

The proposal is blocked or failed closed before execution. The example does
not execute SQL, does not import `sqlite3`, does not create SQLite databases,
and does not create sandbox files.

Expected properties:

* `executed=false`
* `execution_allowed=false`
* `direct_execution_allowed=false`
* no side effect

## Example 3: Unsupported Non-SQL Proposal

The unsupported non-SQL example represents an external runtime proposal as
inert data only. It does not call OpenClaw, does not invoke DeepSeek, does not
use provider SDKs, does not use agent SDKs, does not use HTTP, does not use
shell, does not use file adapters, and does not call MCP.

The proposal is blocked or failed closed.

Expected properties:

* `executed=false`
* `execution_allowed=false`
* `direct_execution_allowed=false`
* no external integration

## Trace Examples

`examples/dhms_agentfuse/trace_examples.json` contains three deterministic
trace examples:

* `sql_fuse_allowlisted_candidate_held`
* `sql_mutation_blocked`
* `unsupported_non_sql_blocked_or_fail_closed`

Each trace shows:

* `RuntimeRequest`
* `ToolCallProposal`
* `SafetyDecision`
* `ExecutionGateDecision`
* `AgentFuseTrace`
* `executed=false`
* `execution_result=null`
* `tool_family="DHMS AgentFuse"`
* protocol version reference

## How to Run

```bash id="3u0hif"
python3 examples/dhms_agentfuse/sql_fuse_allowlisted_candidate_example.py
python3 examples/dhms_agentfuse/sql_mutation_blocked_example.py
python3 examples/dhms_agentfuse/unsupported_non_sql_proposal_example.py
python3 validation/run_dhms_agentfuse_protocol_examples_smoke.py
```

Existing cross-checks:

```bash id="263sdr"
python3 cli.py demo-sql-fuse
python3 validation/run_dhms_agentfuse_bench_sql_v0.py
python3 validation/run_dhms_agentfuse_minimal_api_skeleton_smoke.py
```

## Non-execution Guarantees

The examples do not:

* execute SQL
* create SQLite DBs
* create sandbox files
* invoke OpenClaw
* invoke DeepSeek
* use provider SDKs
* use agent SDKs
* use HTTP/network clients
* implement file/shell/MCP policy
* implement production runtime support

## Not Claimed

v0.7.1 does not claim:

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
* MCP replacement
* universal agent safety

## Next Milestone

Recommended next milestone:

`v0.7.2 Risk-Tiered Fuse Policy Draft`

Final document verdict:

`READY_FOR_V0_7_2_RISK_TIERED_FUSE_POLICY_DRAFT`
