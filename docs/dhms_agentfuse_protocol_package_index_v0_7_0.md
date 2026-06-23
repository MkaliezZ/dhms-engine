# DHMS AgentFuse Public Protocol Package v0.7.0

## Purpose

v0.7.0 packages the completed v0.6 line into a public-facing protocol package.
It is documentation and package organization only.

DHMS is an execution fuse protocol for AI agents. DHMS AgentFuse is the
benchmark, demo, API, and adapter-skeleton tool family around that protocol.

v0.7.0 does not add execution capability, does not add runtime behavior, and
does not expand the v0.5 SQL Sandbox Execution Fuse proof line.

## Current Package Map

Core public materials:

* README quickstart: [`../README.md`](../README.md)
* Protocol specification: [`docs/dhms_execution_fuse_protocol_v0_6_0.md`](dhms_execution_fuse_protocol_v0_6_0.md)
* SQL benchmark documentation: [`docs/dhms_agentfuse_bench_sql_v0_6_1.md`](dhms_agentfuse_bench_sql_v0_6_1.md)
* SQL Fuse demo CLI documentation: [`docs/dhms_sql_fuse_demo_cli_v0_6_2.md`](dhms_sql_fuse_demo_cli_v0_6_2.md)
* Minimal API / Adapter Skeleton documentation: [`docs/dhms_agentfuse_minimal_api_adapter_skeleton_v0_6_3.md`](dhms_agentfuse_minimal_api_adapter_skeleton_v0_6_3.md)
* Development roadmap: [`docs/dhms_agentfuse_development_roadmap.md`](dhms_agentfuse_development_roadmap.md)
* Benchmark case manifest: [`benchmarks/dhms_agentfuse_sql_v0/cases.json`](../benchmarks/dhms_agentfuse_sql_v0/cases.json)
* Minimal API package: [`dhms_agentfuse/`](../dhms_agentfuse/)
* Minimal API smoke validation: [`validation/run_dhms_agentfuse_minimal_api_skeleton_smoke.py`](../validation/run_dhms_agentfuse_minimal_api_skeleton_smoke.py)
* Benchmark runner: [`validation/run_dhms_agentfuse_bench_sql_v0.py`](../validation/run_dhms_agentfuse_bench_sql_v0.py)

## What v0.6 Completed

* v0.6.0: DHMS Execution Fuse Protocol specification.
* v0.6.1: DHMS-AgentFuse-Bench SQL v0 benchmark.
* v0.6.2: non-executing SQL Fuse demo CLI.
* v0.6.3: DHMS AgentFuse Minimal API and Adapter Skeleton.

Together, these make the v0.5 SQL Sandbox Execution Fuse proof reproducible,
visible, and structurally connectable without connecting to real agent
runtimes or adding execution capability.

## Reproducible Commands

Current public commands:

```bash
python3 cli.py demo-sql-fuse
python3 validation/run_dhms_agentfuse_bench_sql_v0.py
python3 validation/run_dhms_agentfuse_minimal_api_skeleton_smoke.py
```

Optional historical cross-checks:

```bash
python3 validation/run_runtime_execution_policy_freeze_stub.py
python3 validation/run_sql_sandbox_runtime_first_actual_controlled_release.py
python3 validation/run_sql_safety_temp_sqlite_mutation_block_test.py
```

## Current Evidence Summary

* 7 SQL v0 benchmark cases.
* 1 release-eligible SQL candidate.
* 6 blocked/fail-closed paths.
* Benchmark runner is non-executing.
* CLI demo is non-executing.
* Minimal API skeleton is non-executing.
* v0.5.15 remains the linked actual controlled-release proof.
* v0.6.3 direct execution count remains 0.

The only proven SQL controlled-release candidate remains exactly:

```sql
SELECT id, label, status FROM toy_accounts ORDER BY id;
```

## Integration Shape

v0.6.3 exposes these public object shapes:

* `RuntimeRequest`
* `ToolCallProposal`
* `SafetyDecision`
* `ExecutionGateDecision`
* `AgentFuseTrace`

The shape is:

agent intent / runtime event -> runtime request -> tool-call proposal -> DHMS
AgentFuse policy evaluation -> safety decision -> execution gate decision ->
trace object.

This is an integration shape only. It is not production runtime support, not a
real adapter, and not an execution API.

## Not Claimed

v0.7.0 does not claim:

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

## Next Package Steps

* v0.7.1 Protocol Examples
* v0.7.2 Risk-Tiered Fuse Policy Draft
* v0.7.3 Landscape / Comparison Doc
* v0.7.4 Contribution Guide / Case Format
* v0.7.5 Fresh Clone Reproduction Check

Final document verdict:

`READY_FOR_V0_7_1_PROTOCOL_EXAMPLES`
