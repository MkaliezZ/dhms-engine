# DHMS Agent Harness v1 Preview

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

DHMS is an execution fuse protocol for AI agents. It records reproducible
evidence for release, block, hold, and fail-closed decisions under documented non-production boundaries.

DHMS began as memory/context/tool-state perturbation testing. The current
`agent-harness-v1` branch is the public DHMS AgentFuse evidence line for the DHMS Execution Fuse Protocol.

## Current Status

* Current branch: `agent-harness-v1`.
* Current milestone: `v1.3.6 Runtime Adapter Boundary Manual GitHub Release Confirmation`.
* Previous milestone: `v1.3.5 Runtime Adapter Boundary Tag / Release Preparation`.
* Public release: [`DHMS v1.3 Runtime Adapter Boundary Public Evidence Package`](https://github.com/MkaliezZ/dhms-engine/releases/tag/v1.3.0-runtime-adapter-boundary-public-evidence-package).
* Release tag: `v1.3.0-runtime-adapter-boundary-public-evidence-package`.
* Confirmed tag target commit: `23311e7484e1a603c56a479189463a9d18f97741`.
* Prior public release: [`DHMS v1.0 Public Evidence Package`](https://github.com/MkaliezZ/dhms-engine/releases/tag/v1.0.0-public-evidence-package), tag `v1.0.0-public-evidence-package`, target `24319dfa3db0f272b13b220201e6f4528c62a6f2`.

v1.1 adds Local Command-Agent Interception planning, a static inert manifest,
a non-executing benchmark, inert examples / trace planning, and a controlled
non-executing mock-agent local command proof, now reviewed and frozen:
[planning](docs/dhms_local_command_agent_interception_planning_v1_1_0.md),
[manifest doc](docs/dhms_local_command_proposal_static_manifest_v1_1_1.md),
[benchmark doc](docs/dhms_non_executing_local_command_proposal_benchmark_v1_1_2.md),
[examples doc](docs/dhms_local_command_proposal_examples_and_trace_plan_v1_1_3.md),
[proof doc](docs/dhms_controlled_mock_agent_local_command_interception_proof_v1_1_4.md),
[freeze doc](docs/dhms_local_command_interception_result_review_and_freeze_v1_1_5.md),
[cases](benchmarks/dhms_local_command_proposals_v0/cases.json),
[runner](validation/run_dhms_local_command_proposal_benchmark_v0.py),
[proof runner](validation/run_dhms_controlled_mock_agent_local_command_interception_proof.py),
[examples README](examples/dhms_local_command_proposals_v0/README.md),
[examples JSON](examples/dhms_local_command_proposals_v0/inert_examples.json),
and [trace plan](trace_examples/dhms_local_command_proposals_v0/trace_plan.json).
It does not add command execution, shell execution, subprocess execution,
terminal integration, CLI commands, schemas, tags, or GitHub releases.

v1.2 adds runtime adapter boundary planning, a static inert manifest,
non-executing benchmark, inert examples / trace plan, and controlled
mock-agent boundary proof:
[planning](docs/dhms_runtime_adapter_boundary_planning_v1_2_0.md),
[manifest](docs/dhms_runtime_adapter_proposal_static_manifest_v1_2_1.md),
[cases](benchmarks/dhms_runtime_adapter_proposals_v0/cases.json),
[benchmark](docs/dhms_non_executing_runtime_adapter_proposal_benchmark_v1_2_2.md),
[runner](validation/run_dhms_runtime_adapter_proposal_benchmark_v0.py),
[examples](examples/dhms_runtime_adapter_proposals_v0/inert_examples.json),
[trace plan](trace_examples/dhms_runtime_adapter_proposals_v0/trace_plan.json),
[examples doc](docs/dhms_runtime_adapter_proposal_examples_and_trace_plan_v1_2_3.md),
[proof doc](docs/dhms_controlled_mock_agent_runtime_adapter_boundary_proof_v1_2_4.md), [proof runner](validation/run_dhms_controlled_mock_agent_runtime_adapter_boundary_proof.py),
and [freeze doc](docs/dhms_runtime_adapter_boundary_result_review_and_freeze_v1_2_5.md).
v1.3 packages the frozen v1.2 Runtime Adapter Boundary line for public reading: [planning](docs/dhms_runtime_adapter_boundary_public_evidence_package_planning_v1_3_0.md), [assembly](docs/dhms_runtime_adapter_boundary_public_evidence_package_v1_3_1.md), [fresh-clone reproduction](docs/dhms_runtime_adapter_boundary_fresh_clone_reproduction_check_v1_3_2.md), [README polish](docs/dhms_runtime_adapter_boundary_readme_public_launch_polish_v1_3_3.md), [release notes draft](docs/dhms_runtime_adapter_boundary_github_release_notes_draft_v1_3_4.md), [tag/release preparation](docs/dhms_runtime_adapter_boundary_tag_release_preparation_v1_3_5.md), and [manual release confirmation](docs/dhms_runtime_adapter_boundary_manual_github_release_confirmation_v1_3_6.md).
It does not add runtime adapter implementation, SDK integration, CLI commands, schemas, or runtime execution behavior.

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
* [DHMS AgentFuse Development Roadmap](docs/dhms_agentfuse_development_roadmap.md)
* [Contribution Guide / Case Format](docs/dhms_contribution_guide_case_format_v0_7_4.md)

Read the README as the landing page, the package index as the map, the v1.0 evidence package as the frozen public claim, and the fresh-clone reproduction check as the external reproducibility record.
Historical milestone details are intentionally kept in the linked docs index.

## Public Non-Claims

DHMS public line does not claim:

* production readiness
* real agent runtime interception
* real LLM execution
* real shell execution safety
* universal agent safety
* industry-standard status
* arbitrary tool execution
* arbitrary command execution support
* arbitrary terminal support
* arbitrary SQL support
* arbitrary file operation support
* arbitrary HTTP/network support
* adapter/API-client support
* MCP integration
* E2B integration
* Codex integration
* Claude integration
* OpenClaw integration
* DeepSeek integration
* provider SDK integration
* agent SDK integration
* credential handling
* user data safety certification
* production DB safety
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
