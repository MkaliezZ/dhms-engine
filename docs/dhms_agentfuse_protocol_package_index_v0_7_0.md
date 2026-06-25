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
* Mock agent interception examples and trace documentation: [`docs/dhms_mock_agent_interception_examples_and_traces_v0_10_3.md`](dhms_mock_agent_interception_examples_and_traces_v0_10_3.md)
* Mock agent interception examples: [`examples/dhms_mock_agent_runtime_interception_v0/interception_examples.json`](../examples/dhms_mock_agent_runtime_interception_v0/interception_examples.json)
* Mock agent interception trace examples: [`examples/dhms_mock_agent_runtime_interception_v0/trace_examples.json`](../examples/dhms_mock_agent_runtime_interception_v0/trace_examples.json)
* Controlled mock agent runtime interception proof documentation: [`docs/dhms_controlled_mock_agent_runtime_interception_proof_v0_10_4.md`](dhms_controlled_mock_agent_runtime_interception_proof_v0_10_4.md)
* Controlled mock agent runtime interception proof runner: [`validation/run_dhms_controlled_mock_agent_runtime_interception_proof.py`](../validation/run_dhms_controlled_mock_agent_runtime_interception_proof.py)
* Agent runtime interception result review and freeze: [`docs/dhms_agent_runtime_interception_result_review_and_freeze_v0_10_5.md`](dhms_agent_runtime_interception_result_review_and_freeze_v0_10_5.md)
* Public evidence package: [`docs/dhms_public_evidence_package_v1_0.md`](dhms_public_evidence_package_v1_0.md)
* Fresh clone reproduction check: [`docs/dhms_fresh_clone_reproduction_check_v1_0_1.md`](dhms_fresh_clone_reproduction_check_v1_0_1.md)
* README public launch polish: [`docs/dhms_readme_public_launch_polish_v1_0_2.md`](dhms_readme_public_launch_polish_v1_0_2.md)
* GitHub release notes: [`docs/dhms_github_release_notes_v1_0_3.md`](dhms_github_release_notes_v1_0_3.md)
* v1.0 tag / release preparation: [`docs/dhms_v1_0_tag_release_preparation_v1_0_4.md`](dhms_v1_0_tag_release_preparation_v1_0_4.md)
* Manual GitHub release confirmation: [`docs/dhms_manual_github_release_confirmation_v1_0_5.md`](dhms_manual_github_release_confirmation_v1_0_5.md)
* README slim public landing page: [`docs/dhms_readme_slim_public_landing_page_v1_0_6.md`](dhms_readme_slim_public_landing_page_v1_0_6.md)
* Local Command-Agent Interception planning: [`docs/dhms_local_command_agent_interception_planning_v1_1_0.md`](dhms_local_command_agent_interception_planning_v1_1_0.md)
* Local Command Proposal Static Manifest documentation: [`docs/dhms_local_command_proposal_static_manifest_v1_1_1.md`](dhms_local_command_proposal_static_manifest_v1_1_1.md)
* Local Command Proposal Static Manifest: [`benchmarks/dhms_local_command_proposals_v0/cases.json`](../benchmarks/dhms_local_command_proposals_v0/cases.json)
* Non-executing Local Command Proposal Benchmark documentation: [`docs/dhms_non_executing_local_command_proposal_benchmark_v1_1_2.md`](dhms_non_executing_local_command_proposal_benchmark_v1_1_2.md)
* Non-executing Local Command Proposal Benchmark runner: [`validation/run_dhms_local_command_proposal_benchmark_v0.py`](../validation/run_dhms_local_command_proposal_benchmark_v0.py)
* Local Command Proposal Examples and Trace Plan documentation: [`docs/dhms_local_command_proposal_examples_and_trace_plan_v1_1_3.md`](dhms_local_command_proposal_examples_and_trace_plan_v1_1_3.md)
* Local Command Proposal examples README: [`examples/dhms_local_command_proposals_v0/README.md`](../examples/dhms_local_command_proposals_v0/README.md)
* Local Command Proposal inert examples: [`examples/dhms_local_command_proposals_v0/inert_examples.json`](../examples/dhms_local_command_proposals_v0/inert_examples.json)
* Local Command Proposal trace plan: [`trace_examples/dhms_local_command_proposals_v0/trace_plan.json`](../trace_examples/dhms_local_command_proposals_v0/trace_plan.json)
* Controlled Mock-Agent Local Command Interception Proof documentation: [`docs/dhms_controlled_mock_agent_local_command_interception_proof_v1_1_4.md`](dhms_controlled_mock_agent_local_command_interception_proof_v1_1_4.md)
* Controlled Mock-Agent Local Command Interception Proof runner: [`validation/run_dhms_controlled_mock_agent_local_command_interception_proof.py`](../validation/run_dhms_controlled_mock_agent_local_command_interception_proof.py)
* Local Command Interception Result Review and Freeze: [`docs/dhms_local_command_interception_result_review_and_freeze_v1_1_5.md`](dhms_local_command_interception_result_review_and_freeze_v1_1_5.md)
* Runtime Adapter Boundary Planning: [`docs/dhms_runtime_adapter_boundary_planning_v1_2_0.md`](dhms_runtime_adapter_boundary_planning_v1_2_0.md)
* Runtime Adapter Proposal Static Manifest documentation: [`docs/dhms_runtime_adapter_proposal_static_manifest_v1_2_1.md`](dhms_runtime_adapter_proposal_static_manifest_v1_2_1.md)
* Runtime Adapter Proposal Static Manifest: [`benchmarks/dhms_runtime_adapter_proposals_v0/cases.json`](../benchmarks/dhms_runtime_adapter_proposals_v0/cases.json)
* Non-executing Runtime Adapter Proposal Benchmark documentation: [`docs/dhms_non_executing_runtime_adapter_proposal_benchmark_v1_2_2.md`](dhms_non_executing_runtime_adapter_proposal_benchmark_v1_2_2.md)
* Non-executing Runtime Adapter Proposal Benchmark runner: [`validation/run_dhms_runtime_adapter_proposal_benchmark_v0.py`](../validation/run_dhms_runtime_adapter_proposal_benchmark_v0.py)
* Runtime Adapter Proposal Examples and Trace Plan documentation: [`docs/dhms_runtime_adapter_proposal_examples_and_trace_plan_v1_2_3.md`](dhms_runtime_adapter_proposal_examples_and_trace_plan_v1_2_3.md)
* Runtime Adapter Proposal inert examples: [`examples/dhms_runtime_adapter_proposals_v0/inert_examples.json`](../examples/dhms_runtime_adapter_proposals_v0/inert_examples.json)
* Runtime Adapter Proposal trace plan: [`trace_examples/dhms_runtime_adapter_proposals_v0/trace_plan.json`](../trace_examples/dhms_runtime_adapter_proposals_v0/trace_plan.json)
* Controlled Mock-Agent Runtime Adapter Boundary Proof documentation: [`docs/dhms_controlled_mock_agent_runtime_adapter_boundary_proof_v1_2_4.md`](dhms_controlled_mock_agent_runtime_adapter_boundary_proof_v1_2_4.md)
* Controlled Mock-Agent Runtime Adapter Boundary Proof runner: [`validation/run_dhms_controlled_mock_agent_runtime_adapter_boundary_proof.py`](../validation/run_dhms_controlled_mock_agent_runtime_adapter_boundary_proof.py)
* Runtime Adapter Boundary Result Review and Freeze: [`docs/dhms_runtime_adapter_boundary_result_review_and_freeze_v1_2_5.md`](dhms_runtime_adapter_boundary_result_review_and_freeze_v1_2_5.md)
* Runtime Adapter Boundary Public Evidence Package Planning: [`docs/dhms_runtime_adapter_boundary_public_evidence_package_planning_v1_3_0.md`](dhms_runtime_adapter_boundary_public_evidence_package_planning_v1_3_0.md)
* Runtime Adapter Boundary Public Evidence Package Assembly: [`docs/dhms_runtime_adapter_boundary_public_evidence_package_v1_3_1.md`](dhms_runtime_adapter_boundary_public_evidence_package_v1_3_1.md)
* Runtime Adapter Boundary Fresh Clone Reproduction Check: [`docs/dhms_runtime_adapter_boundary_fresh_clone_reproduction_check_v1_3_2.md`](dhms_runtime_adapter_boundary_fresh_clone_reproduction_check_v1_3_2.md)
* Runtime Adapter Boundary README Public Launch Polish: [`docs/dhms_runtime_adapter_boundary_readme_public_launch_polish_v1_3_3.md`](dhms_runtime_adapter_boundary_readme_public_launch_polish_v1_3_3.md)
* Runtime Adapter Boundary GitHub Release Notes Draft: [`docs/dhms_runtime_adapter_boundary_github_release_notes_draft_v1_3_4.md`](dhms_runtime_adapter_boundary_github_release_notes_draft_v1_3_4.md)
* Runtime Adapter Boundary Tag / Release Preparation: [`docs/dhms_runtime_adapter_boundary_tag_release_preparation_v1_3_5.md`](dhms_runtime_adapter_boundary_tag_release_preparation_v1_3_5.md)
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

v1.0.1 verifies the v1.0 DHMS Public Evidence Package from a fresh clone and
documents that the public SQL/File/HTTP demos plus mock-agent benchmark and
controlled proof commands pass without hidden local state.

v1.0.2 polishes the README public launch surface for external technical
readers while preserving the evidence chain, reproduction commands, fresh clone
reproduction evidence, and public non-claims.

v1.0.3 prepares GitHub release notes for the v1.0 public evidence package. It
does not create a GitHub release or tag.

v1.0.4 prepares the manual tag and GitHub release checklist for the v1.0
public evidence package. It does not create a GitHub release, create a tag, or
push tags.

v1.0.5 documents that the v1.0 public evidence package GitHub release and tag
were manually created and confirmed. It does not create or edit a GitHub
release, create/modify/delete/push a tag, add execution behavior, or change
proof semantics.

v1.0.6 slims the README into a concise public landing page while preserving
the public frozen claim, SQL/File/HTTP/Mock-agent evidence lines, reproduction
commands, v1.0 release link, fresh clone reproduction link, docs index, public
non-claims, License section, and Trademark Notice.

v1.1.0 opens planning for Local Command-Agent Interception. It defines how DHMS
will reason about inert local command proposals before execution, under
fail-closed, non-production boundaries. It does not add command execution,
shell execution, subprocess execution, terminal integration, runners,
manifests, examples, source code, or proof behavior.

v1.1.1 creates the first static inert local command proposal manifest for
future command-agent interception evidence. It does not add command execution,
shell execution, subprocess execution, terminal integration, benchmark runners,
CLI commands, source code, schemas, executable examples, trace examples, or
proof behavior.

v1.1.2 adds a non-executing benchmark validator for the static inert local
command proposal manifest. It validates the manifest in memory and does not
execute command strings, execute argv, invoke shells, invoke subprocess
execution, add terminal integration, add a command runner, or add a CLI
command.

v1.1.3 adds inert local command proposal examples and a non-executing trace
plan. It maps the static manifest cases to proposal observation, risk
classification, policy decision, trace evidence, and execution_not_performed
expectations without adding command execution, terminal integration, benchmark
runners, CLI commands, executable examples, or executable trace examples.

v1.1.4 adds a controlled deterministic mock-agent local command interception
proof. It simulates a mock agent proposing all 14 static local command cases as
inert data, validates `HOLD`, `BLOCK`, and `FAIL_CLOSED` decisions plus trace
behavior, and keeps command_string, argv, shell, subprocess, terminal, command
runner, real agent runtime, and real LLM execution counts at 0.

v1.1.5 reviews and freezes the Local Command-Agent Interception evidence line.
It freezes the claim over 14 static inert local command proposals and confirms
`proposal_count=14`, `intercepted_proposal_count=14`, `release_count=0`, and
all command_string, argv, shell, subprocess, terminal, command runner, real
agent runtime, and real LLM execution counts at 0.

v1.2.0 opens runtime adapter boundary planning by defining runtime adapter
proposals as inert proposed actions under fail-closed, non-executing,
non-production boundaries. It does not implement MCP, E2B, Codex, Claude,
OpenClaw, DeepSeek, provider SDK, agent SDK, or real runtime adapter
integration.

v1.2.1 defines a static inert manifest of 19 runtime adapter proposal cases.
It keeps decisions limited to `HOLD`, `BLOCK`, and `FAIL_CLOSED`, keeps
`RELEASE=0`, and does not implement runtime adapter behavior, SDK calls,
network calls, shell/subprocess execution, CLI commands, schemas, or proof
behavior.

v1.2.2 adds a non-executing benchmark validator for the static inert runtime
adapter proposal manifest. It validates 19 cases, `HOLD=2`, `BLOCK=11`,
`FAIL_CLOSED=6`, `RELEASE=0`, and no SDK/runtime/tool/network/shell/subprocess
execution indicators.

v1.2.3 adds inert runtime adapter proposal examples and a non-executing trace
plan over all 19 manifest cases. It preserves `HOLD=2`, `BLOCK=11`,
`FAIL_CLOSED=6`, `RELEASE=0`, and does not add runtime adapter behavior,
SDK calls, network calls, shell/subprocess execution, CLI commands, schemas, or
proof behavior.

v1.2.4 adds a controlled deterministic mock-agent proof for runtime adapter
proposal boundary interception. It validates all 19 inert proposals exactly
once, intercepts them before execution, preserves `HOLD=2`, `BLOCK=11`,
`FAIL_CLOSED=6`, `RELEASE=0`, and keeps runtime adapter, SDK, network, shell,
subprocess, terminal, tool, credential, user-data, model-provider, and
production-runtime behavior at 0.

v1.2.5 reviews and freezes the Runtime Adapter Boundary evidence line with the
frozen claim over 19 static inert runtime adapter proposals under fail-closed,
non-production boundaries. It is documentation/freeze-only and does not add
runtime execution behavior.

v1.3.0 plans a public evidence package for the frozen v1.2 Runtime Adapter
Boundary evidence line. It is planning-only and does not create a GitHub
release, create tags, assemble the final package, or add runtime execution
behavior.

v1.3.1 assembles the public evidence package for the frozen v1.2 Runtime
Adapter Boundary evidence line. It is documentation/package-assembly only and
does not create a GitHub release, create tags, add runtime adapter
implementation, add SDK integration, or add execution behavior.

v1.3.2 records a fresh-clone reproduction check for the v1.3.1 Runtime Adapter
Boundary Public Evidence Package. It is documentation/reproduction-record only
and does not create a GitHub release, create tags, add runtime adapter
implementation, add SDK integration, or add execution behavior.

v1.3.3 polishes the README public landing page for the v1.3 Runtime Adapter
Boundary Public Evidence Package. It is documentation/README-polish only and
does not create a GitHub release, create tags, add runtime adapter
implementation, add SDK integration, or add execution behavior.

v1.3.4 drafts GitHub release notes for the v1.3 Runtime Adapter Boundary
Public Evidence Package. It is documentation/release-notes-draft only and
does not create a GitHub release, create or push tags, select a final target
commit, add runtime adapter implementation, add SDK integration, or add
execution behavior.

v1.3.5 prepares the tag and GitHub release plan for the v1.3 Runtime Adapter
Boundary Public Evidence Package. It is documentation/tag-release-preparation
only and does not create a GitHub release, create or push tags, add runtime
adapter implementation, add SDK integration, or add execution behavior.

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

v0.10.3 adds static mock-agent interception examples and trace examples for
exactly 9 SQL/File/HTTP proposals. It is static-examples-only and does not add
runners, benchmark runners, CLI commands, source code, execution behavior, real
agent runtimes, real LLMs, MCP/E2B/OpenClaw/DeepSeek/Codex/Claude integrations,
SDK integrations, adapters, API clients, credentials, or production runtime
behavior.

v0.10.4 adds a controlled deterministic mock-agent runtime interception proof
for exactly 9 inert SQL/File/HTTP proposals. It intercepts every proposal before
execution, releases 3 constrained candidates only through existing public
SQL/File/HTTP proof/demo commands, keeps rejected actions non-executing, and
does not claim real agent runtime interception or production readiness.

v0.10.5 reviews and freezes the v0.10 mock-agent runtime interception proof
line. It freezes exactly 9 intercepted inert SQL/File/HTTP proposals, 3
constrained releases through existing public proof/demo commands, 0 rejected
action executions, 0 proposal payload direct executions, and no real agent
runtime or production runtime claim.

v1.0 packages the public DHMS evidence chain across SQL, File, HTTP, and
controlled deterministic mock-agent runtime interception under documented
non-production boundaries. It is documentation and release-preparation only and
does not add capability or execution behavior.

## Reproducible Commands

Current public commands:

```bash
python3 cli.py demo-sql-fuse
python3 validation/run_dhms_agentfuse_bench_sql_v0.py
python3 validation/run_dhms_agentfuse_minimal_api_skeleton_smoke.py
python3 validation/run_dhms_agentfuse_protocol_examples_smoke.py
python3 cli.py bench-mock-agent-interception
python3 cli.py proof-mock-agent-interception
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
* v0.10.4 Controlled Mock Agent Runtime Interception Proof
* v0.10.5 Agent Runtime Interception Result Review and Freeze
* v1.0 Public Evidence Package
* v1.0.1 Fresh Clone Reproduction Check

Final document verdict:

`READY_FOR_V0_7_1_PROTOCOL_EXAMPLES`
