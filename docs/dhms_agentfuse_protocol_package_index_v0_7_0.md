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
* README public surface polish: [`docs/dhms_readme_public_surface_polish_v0_8_9.md`](dhms_readme_public_surface_polish_v0_8_9.md)
* HTTP / Network Request Safety Fuse selection and risk review: [`docs/dhms_http_network_request_safety_fuse_selection_and_risk_review_v0_9_0.md`](dhms_http_network_request_safety_fuse_selection_and_risk_review_v0_9_0.md)
* HTTP / Network Request Safety Fuse planning: [`docs/dhms_http_network_request_safety_fuse_planning_v0_9_1.md`](dhms_http_network_request_safety_fuse_planning_v0_9_1.md)
* HTTP Fuse static case manifest documentation: [`docs/dhms_http_fuse_static_case_manifest_v0_9_2.md`](dhms_http_fuse_static_case_manifest_v0_9_2.md)
* HTTP Fuse static case manifest: [`benchmarks/dhms_agentfuse_http_v0/cases.json`](../benchmarks/dhms_agentfuse_http_v0/cases.json)
* HTTP Fuse non-executing benchmark documentation: [`docs/dhms_non_executing_http_fuse_benchmark_v0_9_3.md`](dhms_non_executing_http_fuse_benchmark_v0_9_3.md)
* HTTP Fuse non-executing benchmark runner: [`validation/run_dhms_agentfuse_bench_http_v0.py`](../validation/run_dhms_agentfuse_bench_http_v0.py)
* Proof-line protocol lifecycle mapping clarification: [`docs/dhms_proof_line_protocol_lifecycle_mapping_v0_9_3_1.md`](dhms_proof_line_protocol_lifecycle_mapping_v0_9_3_1.md)
* HTTP Fuse non-executing examples documentation: [`docs/dhms_http_fuse_non_executing_examples_v0_9_4.md`](dhms_http_fuse_non_executing_examples_v0_9_4.md)
* HTTP Fuse non-executing examples: [`examples/dhms_agentfuse_http_v0/`](../examples/dhms_agentfuse_http_v0/)
* HTTP Fuse example cases: [`examples/dhms_agentfuse_http_v0/non_executing_examples.json`](../examples/dhms_agentfuse_http_v0/non_executing_examples.json)
* HTTP Fuse trace examples: [`examples/dhms_agentfuse_http_v0/trace_examples.json`](../examples/dhms_agentfuse_http_v0/trace_examples.json)
* Constrained local mock HTTP proof planning: [`docs/dhms_constrained_local_mock_http_proof_planning_v0_9_5.md`](dhms_constrained_local_mock_http_proof_planning_v0_9_5.md)
* Constrained local mock HTTP proof result: [`docs/dhms_constrained_local_mock_http_proof_result_v0_9_5_1.md`](dhms_constrained_local_mock_http_proof_result_v0_9_5_1.md)
* Constrained local mock HTTP proof runner: [`validation/run_dhms_constrained_local_mock_http_proof.py`](../validation/run_dhms_constrained_local_mock_http_proof.py)
* HTTP Fuse result review and freeze: [`docs/dhms_http_fuse_result_review_and_freeze_v0_9_6.md`](dhms_http_fuse_result_review_and_freeze_v0_9_6.md)
* HTTP Fuse CLI demo wrapper: [`docs/dhms_http_fuse_cli_demo_wrapper_v0_9_7.md`](dhms_http_fuse_cli_demo_wrapper_v0_9_7.md)
* SQL/File/HTTP evidence alignment: [`docs/dhms_sql_file_http_evidence_alignment_v0_9_8.md`](dhms_sql_file_http_evidence_alignment_v0_9_8.md)
* Mock Agent Runtime Interception Proof planning: [`docs/dhms_mock_agent_runtime_interception_proof_planning_v0_10_0.md`](dhms_mock_agent_runtime_interception_proof_planning_v0_10_0.md)
* Static mock agent tool-call proposal manifest documentation: [`docs/dhms_static_mock_agent_tool_call_proposal_manifest_v0_10_1.md`](dhms_static_mock_agent_tool_call_proposal_manifest_v0_10_1.md)
* Static mock agent tool-call proposal manifest: [`benchmarks/dhms_mock_agent_runtime_interception_v0/proposals.json`](../benchmarks/dhms_mock_agent_runtime_interception_v0/proposals.json)
* Non-executing agent interception benchmark documentation: [`docs/dhms_non_executing_agent_interception_benchmark_v0_10_2.md`](dhms_non_executing_agent_interception_benchmark_v0_10_2.md)
* Non-executing agent interception benchmark runner: [`validation/run_dhms_mock_agent_interception_benchmark_v0.py`](../validation/run_dhms_mock_agent_interception_benchmark_v0.py)
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

v0.8.9 polishes the README public surface, keeps SQL/File Fuse demos as primary
quickstarts, preserves historical Agent Harness commands as legacy reproduction
material, and simplifies the README Trademark Notice.

v0.9.0 selects HTTP / Network Request Safety Fuse as the next DHMS proof line
after the completed SQL Sandbox Execution Fuse and File Operation Safety Fuse
lines. It is planning-only and does not implement HTTP execution or network
adapters.

v0.9.1 plans inert HTTP/network request proposal shapes, risk categories,
decision boundaries, trace expectations, future metrics, fail-closed behavior,
and approval requirements. It does not implement HTTP execution, create static
HTTP case manifests, add benchmark runners, or add HTTP examples.

v0.9.2 adds a static inert HTTP Fuse case manifest with 16 synthetic
HTTP/network request proposal cases as data-only safety contracts. It does not
implement HTTP execution, perform network calls, create HTTP clients, add HTTP
adapters, add benchmark runners, add examples, or authorize real network
activity.

v0.9.3 adds a deterministic non-executing HTTP Fuse benchmark runner over the
static inert v0.9.2 manifest. It evaluates expected decisions in memory and
does not implement HTTP execution, perform network calls, create HTTP clients,
add HTTP adapters, add examples, add CLI wrapper commands, or authorize real
network activity.

v0.9.3.1 clarifies how the SQL, File, and HTTP proof lines map back to the
v0.6 DHMS Execution Fuse Protocol lifecycle. It is documentation-only and does
not modify runners, manifests, examples, CLI commands, adapters, proof
semantics, or runtime behavior.

v0.9.4 adds static non-executing HTTP Fuse examples and trace examples. The
examples map inert HTTP proposal cases to protocol lifecycle traces and do not
implement HTTP execution, perform network calls, create HTTP clients, add HTTP
adapters, add API clients, add benchmark runners, add validation runners, add
CLI commands, or authorize real network activity.

v0.9.5 plans a future constrained local mock HTTP proof. It is planning-only
and does not implement a mock server, HTTP client, socket creation, network
request, proof runner, validation runner, adapter, API client, credential
handling, provider SDK integration, agent SDK integration, MCP integration, or
arbitrary tool execution.

v0.9.5.1 implements the explicitly approved constrained local mock HTTP proof.
It releases exactly one approved synthetic GET to a disposable loopback-only
mock target, keeps all rejected HTTP/network proposal classes non-executing,
verifies teardown, and does not implement general HTTP execution, external
network access, HTTP adapter support, API client support, SDK/tool/browser
paths, OpenClaw, DeepSeek, or arbitrary tool execution.

v0.9.6 reviews and freezes the HTTP Fuse evidence chain from proof-line
selection through the constrained local mock HTTP proof result. It is
documentation-only and does not add execution capability, modify runners,
change manifests, add adapters, add API clients, add CLI commands, change
proof semantics, or authorize new runtime behavior.

v0.9.7 adds a minimal HTTP Fuse CLI demo wrapper. It runs the existing
non-executing HTTP benchmark and constrained local mock HTTP proof in order and
does not modify existing runners, manifests, examples, proof semantics, or
execution behavior.

v0.9.8 aligns the public evidence presentation for SQL, File, and HTTP proof
lines. It classifies SQL as a controlled runtime-path SQLite sandbox release
proof, File as a constrained synthetic temp-directory proof, and HTTP as static
inert cases plus a non-executing benchmark plus constrained local mock HTTP
proof. It does not add runners, manifests, examples, CLI commands, adapters, or
execution behavior.

v0.10.0 plans deterministic mock-agent runtime interception for existing
SQL/File/HTTP tool-call proposals only. It defines the mock agent boundary,
proposal schema, interception lifecycle, v0.10.1-v0.10.5 expected scopes,
success metrics, and frozen non-claims. It does not add a runner, manifest,
examples, trace examples, CLI command, source code, integration, or execution
behavior.

v0.10.1 adds the static mock-agent tool-call proposal manifest with exactly 9
SQL/File/HTTP proposals. It is static-manifest-only and does not add a runner,
benchmark runner, examples, trace examples, CLI command, source code,
integration, or execution behavior.

v0.10.2 adds a non-executing benchmark over the v0.10.1 static mock-agent
proposal manifest. It validates 9 SQL/File/HTTP proposals in memory, keeps
unsupported proposal types at zero, confirms rejected actions do not execute,
and adds only a minimal CLI wrapper around the benchmark runner.

## Reproducible Commands

Current public commands:

```bash
python3 cli.py demo-sql-fuse
python3 validation/run_dhms_agentfuse_bench_sql_v0.py
python3 validation/run_dhms_agentfuse_minimal_api_skeleton_smoke.py
python3 validation/run_dhms_agentfuse_protocol_examples_smoke.py
python3 cli.py bench-mock-agent-interception
python3 validation/run_dhms_file_fuse_static_case_manifest_smoke.py
python3 validation/run_dhms_agentfuse_bench_file_v0.py
python3 validation/run_dhms_file_fuse_non_executing_examples_smoke.py
python3 validation/run_dhms_file_fuse_constrained_temp_directory_proof.py
python3 cli.py demo-file-fuse
python3 validation/run_dhms_agentfuse_bench_http_v0.py
python3 validation/run_dhms_constrained_local_mock_http_proof.py
python3 cli.py demo-http-fuse
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
* v0.8.9 DHMS README Public Surface Polish
* v0.9.0 HTTP / Network Request Safety Fuse Selection and Risk Review
* v0.9.1 HTTP / Network Request Safety Fuse Planning
* v0.9.2 HTTP Fuse Static Case Manifest
* v0.9.3 Non-Executing HTTP Fuse Benchmark
* v0.9.3.1 DHMS Proof-Line Protocol Lifecycle Mapping Clarification
* v0.9.4 HTTP Fuse Non-Executing Examples
* v0.9.5 Constrained Local Mock HTTP Proof Planning
* v0.9.5.1 Constrained Local Mock HTTP Proof Implementation
* v0.9.6 HTTP Fuse Result Review and Freeze
* v0.9.7 HTTP Fuse CLI Demo Wrapper
* v0.9.8 SQL/File/HTTP Evidence Alignment
* v0.9.8 GitHub Release before v0.10.0
* v0.10.0 Agent Runtime Interception Proof Planning
* v0.10.1 Static Mock Agent Tool-Call Proposal Manifest
* v0.10.2 Non-Executing Agent Interception Benchmark
* v0.10.3 Mock Agent Interception Examples and Trace Examples

Final document verdict:

`READY_FOR_V0_7_1_PROTOCOL_EXAMPLES`
