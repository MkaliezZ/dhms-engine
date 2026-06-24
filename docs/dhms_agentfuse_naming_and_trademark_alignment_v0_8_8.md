# DHMS AgentFuse Naming and Trademark Notice Alignment v0.8.8

## Purpose

v0.8.8 aligns the public DHMS AgentFuse naming surface and README Trademark
Notice after the v0.8 File Operation Safety Fuse quickstart and CLI wrapper
milestones.

This phase is documentation and public-surface cleanup only. It does not rename
the GitHub repository, rename branches, modify code, add execution behavior, or
change existing proof semantics.

## Audited Base

* Audited base commit: `aa7850d5d5f05b4b2ca1cdda61033bc52e33a221`
* Branch: `agent-harness-v1`
* Repository: `MkaliezZ/dhms-engine`
* Current milestone: `v0.8.8 DHMS AgentFuse Naming and Trademark Notice Alignment`
* Previous milestone: `v0.8.7 File Fuse CLI Demo Wrapper`
* Next recommended milestone: `v0.9.0 Next DHMS Proof Line Selection and Risk Review`

## Current Naming Issue

The README Trademark Notice previously listed:

`DHMS, DHMS Engine, and DHMS Agent Harness`

The current public surface also uses DHMS AgentFuse naming for the benchmark,
demo, API, and adapter-skeleton tool family. v0.8.8 updates the Trademark
Notice to include the current DHMS AgentFuse project-mark surface while avoiding
formal registration overclaims.

## Approved Public Naming Hierarchy

Use this naming hierarchy consistently:

* Main brand: `DHMS`
* Protocol name: `DHMS Execution Fuse Protocol`
* Formal long name: `DHMS Agent Execution Fuse Protocol`
* Tool family: `DHMS AgentFuse`
* Benchmark family: `DHMS-AgentFuse-Bench`
* CLI family: `DHMS AgentFuse CLI`
* API name: `DHMS AgentFuse Minimal API`
* Adapter name: `DHMS AgentFuse Adapter Skeleton`
* Policy draft name: `DHMS Risk-Tiered Fuse Policy`
* SQL proof line: `DHMS SQL Sandbox Execution Fuse`
* File proof line: `DHMS File Operation Safety Fuse`

Avoid public-facing shorthand such as standalone `AgentFuse`, `Agent Fuse`,
`Agent-Fuse`, `Agentfuse`, or `DHMSAEFP`.

## Updated Trademark Notice Wording

The README Trademark Notice now uses:

`DHMS, DHMS Engine, DHMS Agent Harness, DHMS Execution Fuse Protocol, DHMS AgentFuse, DHMS AgentFuse CLI, DHMS AgentFuse Minimal API, DHMS AgentFuse Adapter Skeleton, and DHMS-AgentFuse-Bench are claimed as trademarks or project marks of Huaxinsheng Zhong.`

The existing permission and license boundary wording remains:

`Use of these names is permitted for accurate reference to this project, but does not imply endorsement, sponsorship, or affiliation unless explicitly authorized.`

`The Apache-2.0 license applies to the source code and documentation in this repository. It does not grant trademark rights.`

The phrase `trademarks or project marks` is used to avoid overstating formal
registration status.

## Non-Rename Decision

v0.8.8 does not rename:

* the GitHub repository `dhms-engine`
* the `main` branch
* the `agent-harness-v1` branch
* package directories
* validation scripts
* benchmark manifests
* examples

The change is naming and notice alignment only.

## Explicit Non-Claims

v0.8.8 does not claim:

* formal trademark registration
* legal advice
* production readiness
* industry-standard status
* MCP replacement
* guardrail replacement
* agent SDK replacement
* arbitrary SQL support
* arbitrary file operation support
* arbitrary tool execution support
* new execution behavior
* HTTP execution
* shell execution
* MCP integration
* OpenClaw integration
* DeepSeek/provider integration
* provider SDK integration
* agent SDK integration

## Validation and Scans

Run:

```bash
python3 cli.py demo-sql-fuse
python3 cli.py demo-file-fuse
python3 validation/run_dhms_agentfuse_bench_sql_v0.py
python3 validation/run_dhms_file_fuse_static_case_manifest_smoke.py
python3 validation/run_dhms_agentfuse_bench_file_v0.py
git diff --check
git diff --cached --check
```

Targeted scans should check:

* standalone public-facing `AgentFuse` usage without `DHMS`
* inconsistent forms such as `Agent Fuse`, `Agent-Fuse`, and `Agentfuse`
* missing `DHMS AgentFuse` in the README Trademark Notice
* formal trademark registration overclaims
* production-ready overclaims
* MCP replacement claims
* arbitrary SQL, file, or tool execution claims
* accidental source code, validation runner, manifest, benchmark, example, schema, production checker, or production runner changes
* accidental README License section changes
* accidental branch or repository rename instructions
* secret/API key/private key patterns

## Next Milestone

Recommended next milestone:

`v0.9.0 Next DHMS Proof Line Selection and Risk Review`

Final document verdict:

`READY_FOR_V0_9_0_NEXT_DHMS_PROOF_LINE_SELECTION_AND_RISK_REVIEW`
