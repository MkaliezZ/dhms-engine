# DHMS Agent Harness v1 Preview

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

DHMS is an execution fuse protocol for AI agents. It records reproducible evidence for release, block, hold, and fail-closed decisions under documented non-production boundaries.

DHMS began as memory/context/tool-state perturbation testing. The current `agent-harness-v1` branch is the public DHMS AgentFuse evidence line for the DHMS Execution Fuse Protocol.

## Current Status

* Current branch: `agent-harness-v1`.
* Current milestone: `v2.6.4.1 README Current Status Sync`.
* Previous milestone: `v2.6.4 LangChain SQL Agent Adapter Skeleton Shape Validation Result Review and Freeze`.
* Next recommended milestone: `v2.7.0 LangChain SQL Agent Adapter Skeleton Source Surface Planning` (planning-only).
* Public release: [`DHMS v1.3 Runtime Adapter Boundary Public Evidence Package`](https://github.com/MkaliezZ/dhms-engine/releases/tag/v1.3.0-runtime-adapter-boundary-public-evidence-package).
* Release tag: `v1.3.0-runtime-adapter-boundary-public-evidence-package`.
* Confirmed tag target commit: `23311e7484e1a603c56a479189463a9d18f97741`.
* Prior public release: [`DHMS v1.0 Public Evidence Package`](https://github.com/MkaliezZ/dhms-engine/releases/tag/v1.0.0-public-evidence-package), tag `v1.0.0-public-evidence-package`, target `24319dfa3db0f272b13b220201e6f4528c62a6f2`.

v1.1 freezes the Local Command-Agent Interception evidence line over inert local command proposals: [planning](docs/dhms_local_command_agent_interception_planning_v1_1_0.md), [manifest](docs/dhms_local_command_proposal_static_manifest_v1_1_1.md), [benchmark](docs/dhms_non_executing_local_command_proposal_benchmark_v1_1_2.md), [examples](docs/dhms_local_command_proposal_examples_and_trace_plan_v1_1_3.md), [proof](docs/dhms_controlled_mock_agent_local_command_interception_proof_v1_1_4.md), and [freeze](docs/dhms_local_command_interception_result_review_and_freeze_v1_1_5.md). It adds no command, shell, subprocess, terminal, CLI, schema, tag, release, or execution behavior.

v1.2 freezes the Runtime Adapter Boundary line: [planning](docs/dhms_runtime_adapter_boundary_planning_v1_2_0.md), [manifest](docs/dhms_runtime_adapter_proposal_static_manifest_v1_2_1.md), [benchmark](docs/dhms_non_executing_runtime_adapter_proposal_benchmark_v1_2_2.md), [examples](docs/dhms_runtime_adapter_proposal_examples_and_trace_plan_v1_2_3.md), [proof](docs/dhms_controlled_mock_agent_runtime_adapter_boundary_proof_v1_2_4.md), and [freeze](docs/dhms_runtime_adapter_boundary_result_review_and_freeze_v1_2_5.md). It adds no runtime adapter implementation, SDK calls, network calls, shell/subprocess execution, CLI commands, schemas, or proof-semantics expansion.

v1.3 packages the frozen v1.2 Runtime Adapter Boundary line for public reading: [planning](docs/dhms_runtime_adapter_boundary_public_evidence_package_planning_v1_3_0.md), [assembly](docs/dhms_runtime_adapter_boundary_public_evidence_package_v1_3_1.md), [fresh-clone reproduction](docs/dhms_runtime_adapter_boundary_fresh_clone_reproduction_check_v1_3_2.md), [README polish](docs/dhms_runtime_adapter_boundary_readme_public_launch_polish_v1_3_3.md), [release notes draft](docs/dhms_runtime_adapter_boundary_github_release_notes_draft_v1_3_4.md), [tag/release preparation](docs/dhms_runtime_adapter_boundary_tag_release_preparation_v1_3_5.md), and [manual release confirmation](docs/dhms_runtime_adapter_boundary_manual_github_release_confirmation_v1_3_6.md).
It does not add runtime adapter implementation, SDK integration, CLI commands, schemas, or runtime execution behavior.

v1.4-v1.7 extend the planning chain with [substrate/runtime boundary](docs/dhms_substrate_boundary_runtime_boundary_planning_v1_4_0.md), [Agent Proposal Envelope](docs/dhms_agent_proposal_envelope_planning_v1_5_0.md), [External Runtime Handoff Contract](docs/dhms_external_runtime_handoff_contract_planning_v1_6_0.md), and [Controlled Adapter Skeleton Planning](docs/dhms_controlled_adapter_skeleton_planning_v1_7_0.md). They add no adapter implementation, SDK/runtime integration, CLI commands, schemas, or execution behavior.

v2.0.0-v2.0.5 is a real-agent-adjacent planning chain: [planning](docs/dhms_real_agent_integration_preview_planning_v2_0_0.md), [target selection](docs/dhms_real_agent_target_selection_and_threat_boundary_v2_0_1.md), [dry-run contract](docs/dhms_proposal_only_dry_run_contract_v2_0_2.md), [capture plan](docs/dhms_non_executing_real_agent_proposal_capture_plan_v2_0_3.md), [controlled proof planning](docs/dhms_controlled_real_agent_preview_proof_planning_v2_0_4.md), and [freeze](docs/dhms_controlled_real_agent_preview_result_review_and_freeze_v2_0_5.md). It selects the future local mock-to-real agent boundary, defines proposal-only dry-run constraints, plans non-executing proposal capture and controlled preview-proof requirements, then freezes the chain as planning-only, non-executing, and non-production. It does not implement real agent integration, real runtime interception, SDK/runtime integration, parser, runner, adapter, agent hook, CLI command, credential handling, user data handling, or execution behavior.

v2.1.0-v2.1.4 freezes the bounded local mock-to-real fixture validation evidence line: v2.1.1 defined a prose-only contract, v2.1.2 added static inert fixtures, v2.1.3 added deterministic non-executing fixture validation, and v2.1.4 reviewed and froze the result. It adds no real-agent integration, KerniQ integration, E2B handoff, CLI command, SDK/runtime integration, command execution, file mutation, network access, credential handling, user data handling, or production behavior.

v2.2.0-v2.2.4 freezes the bounded local proposal emitter candidate evidence chain: v2.2.0 planning-only profile, v2.2.1 prose-only contract, v2.2.2 exactly 8 static inert fixtures, and v2.2.3 deterministic read-only non-executing validation. The frozen validator result is `fixture_count=8`, `accepted_for_dhms_evaluation=1`, `fail_closed=7`, `kerniq_runtime_calls=0`, and `e2b_handoffs=0`.

v2.3.0-v2.3.4 freezes the SQL Agent Local Emit-Only evidence chain: v2.3.0 selected SQL Proposal Agent Candidate as a planning-only target, v2.3.1 defined a prose-only emit-only contract, v2.3.2 added exactly 10 static inert fixtures, v2.3.3 added deterministic read-only validation, and v2.3.4 reviewed and froze the result. The frozen result is `fixture_count=10`, `ACCEPT_FOR_DHMS_EVALUATION=1`, `FAIL_CLOSED=9`, SQL execution attempts `0`, DB connections `0`, schema introspection `0`, LangChain runtime calls `0`, LlamaIndex runtime calls `0`, KerniQ runtime calls `0`, and E2B handoffs `0`. The v2.3.4.1 status sync is documented in [DHMS README Current Status Sync v2.3.4.1](docs/dhms_readme_current_status_sync_v2_3_4_1.md).

v2.4.0-v2.4.4 freezes the third-party SQL Agent threat-boundary evidence chain: v2.4.0 planned the review line, v2.4.1 defined a prose-only threat-boundary contract, v2.4.2 added exactly 16 static inert threat fixtures, v2.4.3 added deterministic read-only validation, and v2.4.4 reviewed and froze the result. The frozen result is `fixture_count=16`, `ACCEPT_FOR_DHMS_EVALUATION=1`, `FAIL_CLOSED=15`, `all_required_fields_present=true`, `all_non_execution_assertions_present=true`, `all_non_execution_assertions_false=true`, `all_threat_fixtures_inert=true`, SQL execution attempts `0`, DB connections `0`, schema introspection `0`, framework imports `0`, framework invocations `0`, model API calls `0`, KerniQ runtime calls `0`, and E2B handoffs `0`. LangChain, LlamaIndex, and domestic LLMs are only threat-boundary subjects so far; DHMS does not install, import, invoke, adapt, or integrate them. The v2.4.4.1 status sync is documented in [DHMS README Current Status Sync v2.4.4.1](docs/dhms_readme_current_status_sync_v2_4_4_1.md).

v2.5.0-v2.5.4 freezes the LangChain SQL Agent emit-only adapter boundary evidence chain: v2.5.0 planned the future boundary, v2.5.1 converted it into a prose-only contract, v2.5.2 added 17 static inert adapter-boundary fixtures, v2.5.3 added deterministic read-only validation, and v2.5.4 reviewed and froze the result. The frozen result is `fixture_count=17`, `accepted_for_dhms_evaluation=1`, `fail_closed=16`, `all_required_fields_present=true`, `all_non_execution_assertions_present=true`, `all_non_execution_assertions_false=true`, `all_adapter_fixtures_inert=true`, `all_fail_closed_reasons_covered_once=true`, SQL execution attempts `0`, DB connections `0`, schema introspection `0`, result readbacks `0`, LangChain installs/imports/invocations/integrations `0`, SQLDatabaseToolkit integrations `0`, model API calls `0`, credential accesses `0`, user data accesses `0`, KerniQ runtime calls `0`, E2B handoffs `0`, and runtime behaviors `0`. DHMS has frozen a LangChain SQL Agent emit-only adapter boundary evidence chain showing deterministic validation without LangChain installation/import/invocation/integration, SQLDatabaseToolkit integration, SQL execution, database connection, schema introspection, result readback, model API calls, credential access, user-data access, KerniQ runtime calls, E2B handoffs, or runtime behavior. Details: [freeze](docs/dhms_langchain_sql_agent_adapter_fixture_validation_result_review_and_freeze_v2_5_4.md), [status sync](docs/dhms_readme_current_status_sync_v2_5_4_1.md).

v2.6.0-v2.6.4 freezes the LangChain SQL Agent Adapter Skeleton Shape evidence chain: v2.6.0 opened planning for a future shape candidate, v2.6.1 converted planning into a prose-only contract, v2.6.2 added exactly 17 static inert shape fixtures, v2.6.3 added deterministic read-only stdlib validation, and v2.6.4 reviewed and froze the result. v2.6.4.1 synchronizes README public status. The frozen result is `fixture_count=17`, `ACCEPT_FOR_SHAPE_REVIEW=1`, `FAIL_CLOSED=16`, `all_required_fields_present=true`, `all_non_execution_manifest_assertions_present=true`, `all_non_execution_manifest_assertions_false=true`, `all_non_execution_fixture_assertions_present=true`, `all_non_execution_fixture_assertions_false=true`, `all_shape_fixtures_inert=true`, `all_fail_closed_reasons_covered_once=true`, source files `0`, adapter implementations `0`, skeleton implementations `0`, validators added in the fixture manifest `0`, schemas `0`, CLI surfaces `0`, parsers `0`, runners `0`, hooks `0`, LangChain installs/imports/invocations/integrations/wrappers/callbacks/tools `0`, SQLDatabaseToolkit integrations `0`, SQL execution attempts `0`, DB connections `0`, schema introspection `0`, result readbacks `0`, model API calls `0`, credential accesses `0`, user data accesses `0`, KerniQ runtime calls `0`, E2B handoffs `0`, runtime behaviors `0`, and execution authorizations `0`. The frozen chain adds no code beyond the read-only validator and does not add LangChain support, SQLDatabaseToolkit support, SQL execution, DB access, model APIs, KerniQ/E2B, execution authorization, or runtime behavior. Details: [freeze](docs/dhms_langchain_sql_agent_adapter_skeleton_shape_validation_result_review_and_freeze_v2_6_4.md), [status sync](docs/dhms_readme_current_status_sync_v2_6_4_1.md).

v2.7.0 is the next planning-only milestone for LangChain SQL Agent Adapter Skeleton Source Surface Planning. It is not authorized to add source files, implementation, adapter behavior, skeleton behavior, LangChain integration, SQLDatabaseToolkit usage, SQL execution, DB access, model APIs, KerniQ, E2B, or runtime behavior.

## Public Frozen Claim

DHMS provides a public evidence package for an execution fuse protocol proof
chain covering SQL, File, HTTP, and controlled deterministic mock-agent runtime
interception under documented non-production boundaries.

## Evidence Lines

| Evidence line | Public proof status | Public command |
| --- | --- | --- |
| SQL | Controlled runtime-path SQLite sandbox release proof | `python3 cli.py demo-sql-fuse` |
| File | Constrained synthetic temp-directory proof | `python3 cli.py demo-file-fuse` |
| HTTP | Static inert cases, non-executing benchmark, and constrained local mock HTTP proof | `python3 cli.py demo-http-fuse` |
| Mock agent | Controlled deterministic mock-agent proof over exactly 9 inert SQL/File/HTTP proposals | `python3 cli.py proof-mock-agent-interception` |

The SQL/File/HTTP evidence alignment is documented in
[DHMS SQL/File/HTTP Evidence Alignment v0.9.8](docs/dhms_sql_file_http_evidence_alignment_v0_9_8.md).
The full v1.0 evidence package is documented in
[DHMS Public Evidence Package v1.0](docs/dhms_public_evidence_package_v1_0.md).

## Quickstart

Run the public demo and proof commands:

```bash
python3 cli.py demo-sql-fuse
python3 cli.py demo-file-fuse
python3 cli.py demo-http-fuse
python3 validation/run_dhms_mock_agent_interception_benchmark_v0.py
python3 cli.py bench-mock-agent-interception
python3 validation/run_dhms_controlled_mock_agent_runtime_interception_proof.py
python3 cli.py proof-mock-agent-interception
python3 validation/run_dhms_local_command_proposal_benchmark_v0.py
python3 validation/run_dhms_controlled_mock_agent_local_command_interception_proof.py
python3 validation/run_dhms_runtime_adapter_proposal_benchmark_v0.py
python3 validation/run_dhms_controlled_mock_agent_runtime_adapter_boundary_proof.py
```

Expected verdict markers:

* `SQL_FUSE_DEMO_PASS`
* `DHMS_FILE_FUSE_DEMO_PASS`
* `DHMS_HTTP_FUSE_DEMO_PASS`
* `DHMS_MOCK_AGENT_INTERCEPTION_BENCHMARK_PASS`
* `DHMS_CONTROLLED_MOCK_AGENT_RUNTIME_INTERCEPTION_PROOF_PASS`
* `DHMS_LOCAL_COMMAND_PROPOSAL_BENCHMARK_PASS`
* `DHMS_CONTROLLED_MOCK_AGENT_LOCAL_COMMAND_INTERCEPTION_PROOF_PASS`
* `DHMS_RUNTIME_ADAPTER_PROPOSAL_BENCHMARK_PASS`
* `DHMS_CONTROLLED_MOCK_AGENT_RUNTIME_ADAPTER_BOUNDARY_PROOF_PASS`

Fresh-clone reproduction is documented in [DHMS Fresh Clone Reproduction Check v1.0.1](docs/dhms_fresh_clone_reproduction_check_v1_0_1.md).

## Release Materials

* GitHub release: [`DHMS v1.0 Public Evidence Package`](https://github.com/MkaliezZ/dhms-engine/releases/tag/v1.0.0-public-evidence-package)
* Release notes source: [DHMS v1.0 GitHub Release Notes v1.0.3](docs/dhms_github_release_notes_v1_0_3.md)
* Release preparation: [DHMS v1.0 Tag / Release Preparation v1.0.4](docs/dhms_v1_0_tag_release_preparation_v1_0_4.md)
* Release confirmation: [DHMS Manual GitHub Release Confirmation v1.0.5](docs/dhms_manual_github_release_confirmation_v1_0_5.md)
* README slimming note: [DHMS README Slim Public Landing Page v1.0.6](docs/dhms_readme_slim_public_landing_page_v1_0_6.md)

## Documentation Index

Start with the public package index:
[DHMS AgentFuse Public Protocol Package v0.7.0](docs/dhms_agentfuse_protocol_package_index_v0_7_0.md).

Core documents:

* [DHMS Execution Fuse Protocol v0.6.0](docs/dhms_execution_fuse_protocol_v0_6_0.md)
* [DHMS Public Evidence Package v1.0](docs/dhms_public_evidence_package_v1_0.md)
* [DHMS Fresh Clone Reproduction Check v1.0.1](docs/dhms_fresh_clone_reproduction_check_v1_0_1.md)
* [DHMS README Public Launch Polish v1.0.2](docs/dhms_readme_public_launch_polish_v1_0_2.md)
* [DHMS v1.0 GitHub Release Notes v1.0.3](docs/dhms_github_release_notes_v1_0_3.md)
* [DHMS v1.0 Tag / Release Preparation v1.0.4](docs/dhms_v1_0_tag_release_preparation_v1_0_4.md)
* [DHMS Manual GitHub Release Confirmation v1.0.5](docs/dhms_manual_github_release_confirmation_v1_0_5.md)
* [DHMS README Slim Public Landing Page v1.0.6](docs/dhms_readme_slim_public_landing_page_v1_0_6.md)
* [DHMS Local Command-Agent Interception Planning v1.1.0](docs/dhms_local_command_agent_interception_planning_v1_1_0.md)
* [DHMS Local Command Proposal Static Manifest v1.1.1](docs/dhms_local_command_proposal_static_manifest_v1_1_1.md)
* [DHMS Non-Executing Local Command Proposal Benchmark v1.1.2](docs/dhms_non_executing_local_command_proposal_benchmark_v1_1_2.md)
* [DHMS Local Command Proposal Examples and Trace Plan v1.1.3](docs/dhms_local_command_proposal_examples_and_trace_plan_v1_1_3.md)
* [DHMS Controlled Mock-Agent Local Command Interception Proof v1.1.4](docs/dhms_controlled_mock_agent_local_command_interception_proof_v1_1_4.md)
* [DHMS Local Command Interception Result Review and Freeze v1.1.5](docs/dhms_local_command_interception_result_review_and_freeze_v1_1_5.md)
* [DHMS Runtime Adapter Boundary Planning v1.2.0](docs/dhms_runtime_adapter_boundary_planning_v1_2_0.md)
* [DHMS Runtime Adapter Proposal Static Manifest v1.2.1](docs/dhms_runtime_adapter_proposal_static_manifest_v1_2_1.md)
* [DHMS Non-Executing Runtime Adapter Proposal Benchmark v1.2.2](docs/dhms_non_executing_runtime_adapter_proposal_benchmark_v1_2_2.md)
* [DHMS Runtime Adapter Proposal Examples and Trace Plan v1.2.3](docs/dhms_runtime_adapter_proposal_examples_and_trace_plan_v1_2_3.md)
* [DHMS Controlled Mock-Agent Runtime Adapter Boundary Proof v1.2.4](docs/dhms_controlled_mock_agent_runtime_adapter_boundary_proof_v1_2_4.md)
* [DHMS Runtime Adapter Boundary Result Review and Freeze v1.2.5](docs/dhms_runtime_adapter_boundary_result_review_and_freeze_v1_2_5.md)
* [DHMS Runtime Adapter Boundary Public Evidence Package Planning v1.3.0](docs/dhms_runtime_adapter_boundary_public_evidence_package_planning_v1_3_0.md) / [Assembly v1.3.1](docs/dhms_runtime_adapter_boundary_public_evidence_package_v1_3_1.md) / [Fresh Clone v1.3.2](docs/dhms_runtime_adapter_boundary_fresh_clone_reproduction_check_v1_3_2.md) / [README Polish v1.3.3](docs/dhms_runtime_adapter_boundary_readme_public_launch_polish_v1_3_3.md) / [Release Notes Draft v1.3.4](docs/dhms_runtime_adapter_boundary_github_release_notes_draft_v1_3_4.md) / [Tag Release Prep v1.3.5](docs/dhms_runtime_adapter_boundary_tag_release_preparation_v1_3_5.md) / [Release Confirmation v1.3.6](docs/dhms_runtime_adapter_boundary_manual_github_release_confirmation_v1_3_6.md)
* [DHMS v2.0 Real-Agent-Adjacent Planning Chain](docs/dhms_real_agent_integration_preview_planning_v2_0_0.md) / [Target v2.0.1](docs/dhms_real_agent_target_selection_and_threat_boundary_v2_0_1.md) / [Dry Run v2.0.2](docs/dhms_proposal_only_dry_run_contract_v2_0_2.md) / [Capture v2.0.3](docs/dhms_non_executing_real_agent_proposal_capture_plan_v2_0_3.md) / [Proof Planning v2.0.4](docs/dhms_controlled_real_agent_preview_proof_planning_v2_0_4.md) / [Freeze v2.0.5](docs/dhms_controlled_real_agent_preview_result_review_and_freeze_v2_0_5.md)
* [DHMS README Current Status Sync v2.0.5.1](docs/dhms_readme_current_status_sync_v2_0_5_1.md)
* [DHMS AgentFuse Development Roadmap](docs/dhms_agentfuse_development_roadmap.md)
* [Contribution Guide / Case Format](docs/dhms_contribution_guide_case_format_v0_7_4.md)

Read the README as the landing page, the package index as the map, the v1.0 evidence package as the frozen public claim, and the fresh-clone reproduction check as the external reproducibility record.
Historical milestone details are intentionally kept in the linked docs index.

## Public Non-Claims

DHMS public line does not claim:

* production readiness
* real agent integration / real agent runtime interception / real LLM execution
* LangChain integration / LangChain SQL Agent support / SQLDatabaseToolkit support
* SQL agent implementation / SQL execution support / arbitrary SQL support
* database connection support / schema introspection support / real schema access / real data access
* database mutation safety / database client or ORM support / production DB safety
* model-provider integration / provider SDK integration / agent SDK integration
* runtime behavior / runtime adapter implementation / adapter skeleton implementation / adapter/API-client support
* credential handling / credential safety claim
* user data safety claim / user data safety certification
* real shell execution safety / shell execution / command execution
* local mock-to-real implementation
* universal agent safety
* industry-standard status
* arbitrary tool execution
* arbitrary command execution support
* arbitrary terminal support
* arbitrary file operation support
* arbitrary HTTP/network support
* parser / runner / adapter / agent hook / CLI command support
* MCP integration
* E2B integration
* Codex integration
* Claude integration
* Claude Code integration
* OpenClaw integration
* DeepSeek integration
* file mutation support
* network execution support
* production filesystem safety
* production HTTP/network safety

## Architecture Note

`main` keeps the Product Diagnosis v1.3 public checkpoint for
perturbation-based LLM memory/context stability testing. The `agent-harness-v1`
branch layers Agent Harness preview work on top of DHMS without changing
protected DHMS theory, metrics, binding, or engine semantics.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).

Copyright 2026 Huaxinsheng Zhong.

## Trademark Notice

DHMS, DHMS Engine, DHMS AgentFuse, and DHMS Agent Harness are project names and marks of Huaxinsheng Zhong.

Use of these names is permitted for accurate reference to this project, but does not imply endorsement, sponsorship, or affiliation unless explicitly authorized.

The Apache-2.0 license applies to the source code and documentation in this repository. It does not grant trademark rights.
