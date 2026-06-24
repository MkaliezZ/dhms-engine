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
* Protocol examples documentation: [`docs/dhms_agentfuse_protocol_examples_v0_7_1.md`](dhms_agentfuse_protocol_examples_v0_7_1.md)
* Protocol examples directory: [`examples/dhms_agentfuse/`](../examples/dhms_agentfuse/)
* Static trace examples: [`examples/dhms_agentfuse/trace_examples.json`](../examples/dhms_agentfuse/trace_examples.json)
* Protocol examples smoke validation: [`validation/run_dhms_agentfuse_protocol_examples_smoke.py`](../validation/run_dhms_agentfuse_protocol_examples_smoke.py)
* Risk-tiered fuse policy draft: [`docs/dhms_risk_tiered_fuse_policy_v0_7_2.md`](dhms_risk_tiered_fuse_policy_v0_7_2.md)
* Landscape / comparison doc: [`docs/dhms_landscape_comparison_v0_7_3.md`](dhms_landscape_comparison_v0_7_3.md)
* Contribution guide: [`CONTRIBUTING.md`](../CONTRIBUTING.md)
* Contribution and case-format documentation: [`docs/dhms_contribution_guide_case_format_v0_7_4.md`](dhms_contribution_guide_case_format_v0_7_4.md)
* Fresh clone reproduction check: [`docs/dhms_fresh_clone_reproduction_check_v0_7_5.md`](dhms_fresh_clone_reproduction_check_v0_7_5.md)
* File Operation Safety Fuse planning: [`docs/dhms_file_operation_safety_fuse_planning_v0_8_0.md`](dhms_file_operation_safety_fuse_planning_v0_8_0.md)
* File Fuse static case manifest documentation: [`docs/dhms_file_fuse_static_case_manifest_v0_8_1.md`](dhms_file_fuse_static_case_manifest_v0_8_1.md)
* File Fuse static case manifest: [`benchmarks/dhms_agentfuse_file_v0/cases.json`](../benchmarks/dhms_agentfuse_file_v0/cases.json)
* File Fuse static manifest smoke validation: [`validation/run_dhms_file_fuse_static_case_manifest_smoke.py`](../validation/run_dhms_file_fuse_static_case_manifest_smoke.py)
* File Fuse non-executing benchmark documentation: [`docs/dhms_file_fuse_non_executing_benchmark_v0_8_2.md`](dhms_file_fuse_non_executing_benchmark_v0_8_2.md)
* File Fuse non-executing benchmark runner: [`validation/run_dhms_agentfuse_bench_file_v0.py`](../validation/run_dhms_agentfuse_bench_file_v0.py)
* File Fuse non-executing examples documentation: [`docs/dhms_file_fuse_non_executing_examples_v0_8_3.md`](dhms_file_fuse_non_executing_examples_v0_8_3.md)
* File Fuse non-executing examples: [`examples/dhms_agentfuse_file_v0/`](../examples/dhms_agentfuse_file_v0/)
* File Fuse static trace examples: [`examples/dhms_agentfuse_file_v0/trace_examples.json`](../examples/dhms_agentfuse_file_v0/trace_examples.json)
* File Fuse examples smoke validation: [`validation/run_dhms_file_fuse_non_executing_examples_smoke.py`](../validation/run_dhms_file_fuse_non_executing_examples_smoke.py)
* File Fuse constrained temp-directory proof planning: [`docs/dhms_file_fuse_constrained_temp_directory_proof_planning_v0_8_4.md`](dhms_file_fuse_constrained_temp_directory_proof_planning_v0_8_4.md)
* File Fuse constrained temp-directory proof result: [`docs/dhms_file_fuse_constrained_temp_directory_proof_result_v0_8_4_1.md`](dhms_file_fuse_constrained_temp_directory_proof_result_v0_8_4_1.md)
* File Fuse constrained temp-directory proof runner: [`validation/run_dhms_file_fuse_constrained_temp_directory_proof.py`](../validation/run_dhms_file_fuse_constrained_temp_directory_proof.py)
* File Operation Safety Fuse result review and freeze: [`docs/dhms_file_operation_safety_fuse_result_review_and_freeze_v0_8_5.md`](dhms_file_operation_safety_fuse_result_review_and_freeze_v0_8_5.md)
* File Operation Safety Fuse evidence seal: [`docs/dhms_file_operation_safety_fuse_evidence_seal_v0_8_6.md`](dhms_file_operation_safety_fuse_evidence_seal_v0_8_6.md)
* File Fuse CLI demo wrapper: [`docs/dhms_file_fuse_cli_demo_wrapper_v0_8_7.md`](dhms_file_fuse_cli_demo_wrapper_v0_8_7.md)
* DHMS AgentFuse naming and Trademark Notice alignment: [`docs/dhms_agentfuse_naming_and_trademark_alignment_v0_8_8.md`](dhms_agentfuse_naming_and_trademark_alignment_v0_8_8.md)
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

v0.7.1 adds non-executing DHMS AgentFuse protocol examples for SQL held,
SQL blocked, unsupported non-SQL blocked/fail-closed behavior, and static
trace examples.

v0.7.2 defines the risk-tiered fuse policy draft for routing observable agent
actions into L0-L4 fuse tiers.

v0.7.3 clarifies how DHMS relates to MCP, guardrails, agent SDKs, sandboxes,
observability, human approval workflows, policy engines, and AI security /
AppSec categories.

v0.7.4 defines contribution and case-format guidance for DHMS AgentFuse and
clarifies that adding cases does not authorize new execution paths.

v0.7.5 verifies the public DHMS AgentFuse protocol package from a fresh clone
and documents the reproducible command path.

v0.8.0 plans the File Operation Safety Fuse as DHMS's preferred second
execution fuse proof line. It does not implement file policy or file operation
capability.

v0.8.1 adds a static, inert File Operation Safety Fuse case manifest with 13
planned cases. It does not implement file policy or file operation capability.

v0.8.2 adds a non-executing File Operation Safety Fuse benchmark over the
static v0.8.1 manifest. It evaluates expected decisions in memory and does not
implement file policy or file operation capability.

v0.8.3 adds non-executing File Operation Safety Fuse examples and static trace
examples. It does not implement file policy or file operation capability.

v0.8.4 plans the safety envelope for a possible constrained temp-directory
proof. It does not implement the proof or add file operation capability.

v0.8.4.1 implements an explicitly approved constrained temp-directory proof.
It performs only synthetic read/write operations inside a disposable temp root
and verifies cleanup. It does not add arbitrary file operation support or a
file adapter.

v0.8.5 reviews and freezes the File Operation Safety Fuse evidence chain from
v0.8.0 through v0.8.4.1. It adds no new capability and keeps the frozen claim
limited to the constrained temp-directory proof result.

v0.8.6 adds README File Fuse Quickstart alignment and seals the v0.8 File
Operation Safety Fuse evidence chain. It adds no new capability and does not
add a file adapter or arbitrary file operation support.

v0.8.7 adds a File Fuse CLI demo wrapper and the public command
`python3 cli.py demo-file-fuse`. It aggregates existing deterministic checks
and does not add new file operation capability.

v0.8.8 aligns DHMS AgentFuse public naming and updates the README Trademark
Notice to include the current DHMS AgentFuse project-mark surface. It does not
rename the repository or branches.

## Reproducible Commands

Current public commands:

```bash
python3 cli.py demo-sql-fuse
python3 validation/run_dhms_agentfuse_bench_sql_v0.py
python3 validation/run_dhms_agentfuse_minimal_api_skeleton_smoke.py
python3 validation/run_dhms_agentfuse_protocol_examples_smoke.py
python3 validation/run_dhms_file_fuse_static_case_manifest_smoke.py
python3 validation/run_dhms_agentfuse_bench_file_v0.py
python3 validation/run_dhms_file_fuse_non_executing_examples_smoke.py
python3 validation/run_dhms_file_fuse_constrained_temp_directory_proof.py
python3 cli.py demo-file-fuse
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
* v0.8.0 File Operation Safety Fuse Planning
* v0.8.1 File Fuse Static Case Manifest
* v0.8.2 Non-Executing File Fuse Benchmark
* v0.8.3 Non-Executing File Fuse Examples
* v0.8.4 Constrained Temp-Directory Proof Planning
* v0.8.4.1 Constrained Temp-Directory Proof Implementation
* v0.8.5 File Operation Safety Fuse Result Review and Freeze
* v0.8.6 File Fuse Quickstart and Evidence Seal
* v0.8.7 File Fuse CLI Demo Wrapper
* v0.8.8 DHMS AgentFuse Naming and Trademark Notice Alignment

Final document verdict:

`READY_FOR_V0_7_1_PROTOCOL_EXAMPLES`
