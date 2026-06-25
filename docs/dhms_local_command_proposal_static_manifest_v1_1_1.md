# DHMS Local Command Proposal Static Manifest v1.1.1

## Purpose

v1.1.1 creates the first static inert manifest for local command proposals
under the v1.1 Local Command-Agent Interception line.

This milestone defines data cases for future non-executing validation. It does
not implement command execution, shell execution, subprocess execution, a
command runner, a benchmark runner, a CLI command, terminal integration,
source code changes, execution behavior, or proof semantics.

## Manifest Path

```text
benchmarks/dhms_local_command_proposals_v0/cases.json
```

## Manifest Structure

The manifest is a JSON top-level object with:

* `manifest_id`
* `version`
* `purpose`
* `execution_boundary`
* `cases`

Each case includes:

* `case_id`
* `category`
* `command_string`
* `argv`
* `working_directory_intent`
* `environment_intent`
* `stdin_intent`
* `file_redirection_intent`
* `network_or_process_side_effect_intent`
* `destructive_operation_indicators`
* `credential_or_user_data_risk_indicators`
* `expected_output_description`
* `proposed_policy_decision`
* `decision_rationale`
* `trace_evidence_reference`

The manifest execution boundary states:

`This manifest contains inert local command proposals only. No command in this file is intended to be executed by DHMS, by tests, by CI, or by a human operator.`

## Case Coverage Summary

The manifest contains 14 inert local command proposal cases covering:

* apparently read-only local listing proposal
* apparently read-only metadata proposal
* destructive filesystem proposal
* recursive delete proposal
* credential/secret access proposal
* environment variable leakage proposal
* hidden file access proposal
* file redirection overwrite proposal
* command chaining proposal
* shell metacharacter ambiguity proposal
* process spawning proposal
* network side-effect proposal
* privilege escalation proposal
* malformed or empty command proposal

All paths, names, and targets are synthetic placeholders such as
`/tmp/dhms_synthetic_workspace`, `/tmp/dhms_synthetic_output.txt`,
`EXAMPLE_SECRET_NAME`, `example.invalid`, and `synthetic-user-data.txt`.

## Allowed Policy Decisions

v1.1.1 uses only:

* `HOLD`
* `BLOCK`
* `FAIL_CLOSED`

## Why RELEASE Is Not Used Yet

`RELEASE` is not used in v1.1.1 because this phase is static-manifest-only.
There is no command execution proof, no runner, no shell execution, no
subprocess execution, no command adapter, and no controlled local command proof
path.

Any future release-like behavior would require an explicitly approved later
phase with constrained, deterministic, synthetic, non-production boundaries.

## Fail-Closed Default Rule

Unknown, malformed, unsupported, credential-seeking, destructive, ambiguous, or
side-effectful local command proposals fail closed unless a later phase defines
a constrained proof path.

Read-like command proposals are not automatically safe. They are held or
blocked until future policy can classify path, data class, side effects,
environment intent, stdin intent, and trace expectations.

## Safety Invariants

* Every command string in the manifest is inert proposal text.
* No command in the manifest is intended to be copied and run.
* The manifest does not authorize execution.
* `RELEASE` is not an allowed v1.1.1 decision.
* Unknown or malformed proposals fail closed.
* Credential, secret, and user-data risk proposals are blocked or fail closed.
* Destructive and network side-effect proposals are blocked or fail closed.
* Future validation must treat command strings as data, not instructions.

## Validation Expectations

v1.1.1 validation checks JSON syntax and preserves existing evidence commands:

```bash
python3 -m json.tool benchmarks/dhms_local_command_proposals_v0/cases.json > /tmp/dhms_local_command_cases_v0_normalized.json
python3 cli.py demo-sql-fuse
python3 cli.py demo-file-fuse
python3 cli.py demo-http-fuse
python3 validation/run_dhms_mock_agent_interception_benchmark_v0.py
python3 cli.py bench-mock-agent-interception
python3 validation/run_dhms_controlled_mock_agent_runtime_interception_proof.py
python3 cli.py proof-mock-agent-interception
```

Expected existing verdict markers:

* `SQL_FUSE_DEMO_PASS`
* `DHMS_FILE_FUSE_DEMO_PASS`
* `DHMS_HTTP_FUSE_DEMO_PASS`
* `DHMS_MOCK_AGENT_INTERCEPTION_BENCHMARK_PASS`
* `DHMS_CONTROLLED_MOCK_AGENT_RUNTIME_INTERCEPTION_PROOF_PASS`

## Public Claim Boundaries

The v1.0 public frozen claim remains:

`DHMS provides a public evidence package for an execution fuse protocol proof chain covering SQL, File, HTTP, and controlled deterministic mock-agent runtime interception under documented non-production boundaries.`

v1.1.1 adds only this planning/data claim:

`DHMS v1.1 defines a static inert manifest for future local command-agent interception evidence under fail-closed, non-production boundaries.`

## Public Non-Claims

DHMS v1.1.1 does not claim:

* production readiness
* real agent runtime interception
* real LLM execution
* real shell execution safety
* arbitrary command execution support
* arbitrary terminal support
* arbitrary tool execution
* credential handling
* user data safety certification
* production filesystem safety
* production process safety
* production network safety
* MCP integration
* E2B integration
* Codex integration
* Claude integration
* OpenClaw integration
* DeepSeek integration
* provider SDK integration
* agent SDK integration

## Documentation/Data-Only Confirmation

v1.1.1 creates only a static inert local command proposal manifest.

It does not add command execution, shell execution, subprocess execution, a
command runner, a benchmark runner, a CLI command, terminal integration,
MCP/E2B/Codex/Claude/OpenClaw/DeepSeek/provider SDK/agent SDK integration,
credential handling, user data handling, source code, schema changes,
execution behavior, proof semantic changes, executable examples, trace
examples, or a new SQL/File/HTTP execution path.

## Repository Safety Confirmation

No files were deleted, renamed, or moved for v1.1.1. No directories were
removed. No GitHub release was created, edited, or deleted. No tag was created,
modified, deleted, or pushed.

## Next Milestone

Recommended next milestone:

`v1.1.2 Non-Executing Local Command Proposal Benchmark`

## Final Verdict

`READY_FOR_V1_1_2_NON_EXECUTING_LOCAL_COMMAND_PROPOSAL_BENCHMARK`
