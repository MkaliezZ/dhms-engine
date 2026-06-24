# DHMS File Fuse CLI Demo Wrapper v0.8.7

## Purpose

v0.8.7 adds a small DHMS File Fuse CLI demo wrapper so the public quickstart
can use one command for the File Operation Safety Fuse line:

```bash
python3 cli.py demo-file-fuse
```

This phase is wrapper and README polish only. It does not add File Fuse safety
semantics, validation logic, file operation capability, or a file adapter.

## Audited Base

* Audited base commit: `141be0f18c5f15ef8d08e60024d61e86222ddb76`
* Previous milestone: `v0.8.6 File Fuse Quickstart and Evidence Seal`
* Current milestone: `v0.8.7 File Fuse CLI Demo Wrapper`
* Next recommended milestone: `v0.9.0 Next DHMS Proof Line Selection and Risk Review`

## Relationship to v0.8.6 Evidence Seal

v0.8.6 sealed the File Operation Safety Fuse evidence chain and added README
File Fuse Quickstart alignment. v0.8.7 preserves that sealed claim and makes
the File Fuse quickstart symmetrical with the SQL Fuse quickstart:

```bash
python3 cli.py demo-sql-fuse
python3 cli.py demo-file-fuse
```

The wrapper does not replace or modify the underlying File Fuse evidence. It
aggregates the existing deterministic checks and reports one concise summary.

## Wrapped Existing Checks

The `demo-file-fuse` command runs only these fixed local checks:

```bash
python3 validation/run_dhms_file_fuse_static_case_manifest_smoke.py
python3 validation/run_dhms_agentfuse_bench_file_v0.py
python3 validation/run_dhms_file_fuse_non_executing_examples_smoke.py
python3 validation/run_dhms_file_fuse_constrained_temp_directory_proof.py
```

The wrapper does not accept arbitrary script paths, arbitrary commands, or
user-provided file paths.

## Expected CLI Output

Expected success output includes:

```text
DHMS_FILE_FUSE_DEMO_PASS
checks_total=4
checks_passed=4
static_manifest_smoke_passed=true
file_benchmark_passed=true
non_executing_examples_passed=true
constrained_temp_directory_proof_passed=true
actual_file_operations_executed_count=2
approved_constrained_release_cases=2
blocked_or_fail_closed_cases=8
rejected_path_opened_count=0
rejected_path_resolved_count=0
file_adapter_added=false
arbitrary_file_operation_support_added=false
```

If any wrapped check fails, the wrapper prints `DHMS_FILE_FUSE_DEMO_FAIL`,
returns a non-zero exit code, and includes failed check details.

## Bounded Claim

DHMS v0.8.7 adds a public File Fuse CLI demo wrapper that aggregates the
existing deterministic File Operation Safety Fuse checks into one command. It
preserves the v0.8 sealed claim and does not add arbitrary file operation
support, a file adapter, or new runtime file execution behavior.

## Explicit Non-Claims

DHMS v0.8.7 does not claim:

* not arbitrary file operation support
* not direct user file read support
* not direct user file write support
* not file deletion support
* not file adapter support
* not production filesystem safety
* not credential safety
* not customer data safety
* not MCP file tool integration
* not OpenClaw runtime integration
* not DeepSeek/provider integration
* not provider SDK integration
* not agent SDK integration
* not HTTP integration
* not shell integration
* not MCP replacement
* not production-ready
* not universal agent safety
* not an industry standard

## Validation Commands

Run:

```bash
python3 cli.py demo-file-fuse
python3 validation/run_dhms_file_fuse_static_case_manifest_smoke.py
python3 validation/run_dhms_agentfuse_bench_file_v0.py
python3 validation/run_dhms_file_fuse_non_executing_examples_smoke.py
python3 validation/run_dhms_file_fuse_constrained_temp_directory_proof.py
python3 cli.py demo-sql-fuse
python3 validation/run_dhms_agentfuse_bench_sql_v0.py
python3 validation/run_dhms_agentfuse_minimal_api_skeleton_smoke.py
python3 validation/run_dhms_agentfuse_protocol_examples_smoke.py
```

Also run:

```bash
git diff --check
git diff --cached --check
```

## Release Readiness Statement

The v0.8.7 CLI wrapper is ready for GitHub Release only after deterministic
validations and targeted scans pass, the documentation/code commit is pushed,
and the explicit release approval statement is present in the task context.

The release tag for this milestone is:

`v0.8.7-file-fuse-cli-demo-wrapper`

## Next Milestone

Recommended next milestone:

`v0.9.0 Next DHMS Proof Line Selection and Risk Review`

Final document verdict:

`READY_FOR_V0_9_0_NEXT_DHMS_PROOF_LINE_SELECTION_AND_RISK_REVIEW`
