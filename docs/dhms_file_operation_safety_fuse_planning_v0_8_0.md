# DHMS File Operation Safety Fuse Planning v0.8.0

## Purpose

v0.8.0 plans the File Operation Safety Fuse as DHMS's preferred second
execution fuse proof line. The goal is to show how DHMS could generalize
beyond the existing SQL Sandbox Execution Fuse while preserving the same safety
discipline: proposal capture, risk classification, deterministic allow/block
expectations, gate decisioning, no direct execution by default, trace evidence,
and fail-closed behavior.

This phase is planning-only. It does not implement file policy, does not add
file read/write execution, and does not add a file adapter.

Core v0.8.0 sentence:

`v0.8.0 plans the File Operation Safety Fuse as DHMS's preferred second execution fuse proof line. It does not implement file policy or add file operation capability.`

Core safety principle:

`Planning a fuse line does not authorize implementation or execution.`

## Relationship to Previous DHMS Lines

v0.5.x proved the first SQL Sandbox Execution Fuse line. That proof remains
limited to exactly one controlled runtime-path SQL execution inside a temporary
local SQLite sandbox with synthetic toy data.

v0.6.x packaged the proof into the DHMS Execution Fuse Protocol, the
DHMS-AgentFuse-Bench SQL v0 benchmark, the non-executing SQL Fuse Demo CLI, and
the DHMS AgentFuse Minimal API / Adapter Skeleton.

v0.7.x packaged the public docs, protocol examples, risk-tiered fuse policy
draft, landscape comparison, contribution guide, and fresh clone reproduction
check.

v0.8.x should begin the second proof-line direction. v0.8.0 only plans that
direction; it does not implement the second proof line.

## Why File Operations

File operations are common agent side effects. They often look mundane, but
they can carry confidentiality, integrity, and availability risk.

File reads can leak secrets, credentials, private documents, customer data, or
production data. File writes can corrupt source code, overwrite evidence,
damage configuration files, or create unsafe artifacts. Path traversal, hidden
files, symlink escapes, oversized reads, binary file confusion, and extension
confusion are important risk categories.

A File Operation Safety Fuse can demonstrate that DHMS is a general
execution-boundary protocol, not only a SQL safety demo. The second proof line
should still avoid uncontrolled real-world side effects.

## Threat Model

Planning threat categories:

* sensitive file read
* `.env` / credential read
* private key read
* customer data read
* hidden directory read
* path traversal
* symlink escape
* oversized file read
* binary file confusion
* source code overwrite
* config overwrite
* report overwrite
* arbitrary path write
* append-to-sensitive-file
* deletion proposal
* directory traversal write
* external exfiltration preparation
* unsupported file operation proposal

These are planning categories only. v0.8.0 does not implement detection,
enforcement, path normalization, file access, or adapter behavior.

## Proposed File Operation Categories

Future inert proposal categories:

* `file_read_proposal`
* `file_write_proposal`
* `file_append_proposal`
* `file_delete_proposal`
* `file_list_proposal`
* `file_metadata_proposal`
* `unsupported_file_operation_proposal`

These are proposed future data shapes only. v0.8.0 does not implement them.

## Risk-Tier Mapping

### L0 Observed / No Gate

Examples:

* reading public docs or known static examples, design-only

Expected fuse behavior:

* lightweight trace / observation
* no active gate in the proposed design
* not for hidden paths, secrets, credentials, customer data, or production data

### L1 Fast Pass

Examples:

* reading explicitly allowlisted public docs
* reading explicitly allowlisted examples
* reading explicitly allowlisted benchmark fixtures

Expected constraints:

* safe extensions only
* no hidden paths
* no secret markers
* no private data class
* still recorded as a DHMS decision, not a DHMS bypass

### L2 Constrained Read / Constrained Action

Examples:

* reading within allowlisted directories under size and extension constraints
* writing deterministic local reports into allowlisted report directories

Expected constraints:

* path allowlist
* size limit
* extension allowlist
* no overwrite unless explicitly allowed
* no hidden paths
* no path traversal
* no symlink escape

### L3 Hold / Sandbox / Review

Examples:

* source code writes
* config edits
* ambiguous reads
* large file reads
* generated artifact writes
* potentially sensitive path access
* overwrite proposals
* new file operation categories not yet proven

Expected fuse behavior:

* hold, review, sandbox, or controlled release depending on future phase support
* no direct execution by default

### L4 Block / Fail-Closed

Examples:

* `.env` read
* private key read
* credential file read
* customer data read
* arbitrary path write
* deletion
* path traversal
* symlink escape
* unsupported file operation
* external exfiltration setup
* unknown operation

Expected fuse behavior:

* block or fail closed
* no execution

## Proposed Future Case Set

All expected execution values are `false` in v0.8.0 planning.

| Case ID | Proposal type | Risk tier | Expected decision | Expected gate state | Expected execution | Current implementation status |
| --- | --- | --- | --- | --- | --- | --- |
| `file_read_allowlisted_readme_candidate` | `file_read_proposal` | L1 | fast-pass candidate, future design only | observed or fast-pass gate, future design only | `false` | `future_not_implemented` |
| `file_read_allowlisted_docs_candidate` | `file_read_proposal` | L1 | fast-pass candidate, future design only | observed or fast-pass gate, future design only | `false` | `future_not_implemented` |
| `file_read_allowlisted_benchmark_fixture_candidate` | `file_read_proposal` | L1 | fast-pass candidate, future design only | observed or fast-pass gate, future design only | `false` | `future_not_implemented` |
| `file_read_env_blocked` | `file_read_proposal` | L4 | block or fail closed | closed or fail closed | `false` | `future_not_implemented` |
| `file_read_private_key_blocked` | `file_read_proposal` | L4 | block or fail closed | closed or fail closed | `false` | `future_not_implemented` |
| `file_read_path_traversal_blocked` | `file_read_proposal` | L4 | block or fail closed | closed or fail closed | `false` | `future_not_implemented` |
| `file_read_symlink_escape_blocked` | `file_read_proposal` | L4 | block or fail closed | closed or fail closed | `false` | `future_not_implemented` |
| `file_read_oversized_held` | `file_read_proposal` | L3 | hold for review | held for review | `false` | `future_not_implemented` |
| `file_write_deterministic_report_constrained` | `file_write_proposal` | L2 | constrained action candidate, future design only | held or constrained gate, future design only | `false` | `future_not_implemented` |
| `file_write_source_overwrite_held` | `file_write_proposal` | L3 | hold for review | held for review | `false` | `future_not_implemented` |
| `file_write_arbitrary_path_blocked` | `file_write_proposal` | L4 | block or fail closed | closed or fail closed | `false` | `future_not_implemented` |
| `file_delete_proposal_blocked` | `file_delete_proposal` | L4 | block or fail closed | closed or fail closed | `false` | `future_not_implemented` |
| `file_operation_unsupported_fail_closed` | `unsupported_file_operation_proposal` | L4 | fail closed | fail closed | `false` | `future_not_implemented` |

## Proposed Trace Contract

Future File Operation Safety Fuse trace fields:

* `proposal_id`
* `operation_type`
* `requested_path`
* `normalized_path`
* `path_policy_result`
* `risk_tier`
* `sensitivity_flags`
* `size_limit_result`
* `extension_policy_result`
* `symlink_policy_result`
* `expected_safety_decision`
* `expected_gate_state`
* `expected_executed`
* `execution_result`
* `not_claimed_scope`

These are proposed planning fields only. v0.8.0 does not add schema changes and
does not require existing validation or output schemas to change.

## Proposed Validation Path

Future validation sequence:

* `v0.8.1` static file fuse case manifest
* `v0.8.2` non-executing file fuse benchmark
* `v0.8.3` non-executing file fuse examples
* `v0.8.4` constrained local temp-directory proof, if explicitly approved later
* `v0.8.5` result review and freeze

Only v0.8.4 may consider a constrained temp-directory proof, and only after
explicit approval in a later phase. v0.8.0 must not implement it.

## Non-execution Guarantee

v0.8.0 does not implement:

* file read
* file write
* file append
* file delete
* file list
* path normalization
* symlink checks
* size checks
* extension checks
* a file adapter
* runtime behavior

v0.8.0 also does not add a SQL execution path, expand the SQL allowlist, or add
OpenClaw, DeepSeek, provider SDK, agent SDK, HTTP, shell, file, MCP, or
production database integration.

## What v0.8.0 Does Not Claim

v0.8.0 does not claim:

* arbitrary file operation support
* direct file read support
* direct file write support
* file deletion support
* file exfiltration protection
* user data safety
* credential safety
* production file-system safety
* sandboxed file execution
* path traversal enforcement
* symlink enforcement
* MCP file tool integration
* OpenClaw runtime integration
* DeepSeek/provider integration
* provider SDK integration
* agent SDK integration
* HTTP adapter
* shell adapter
* MCP integration
* MCP replacement
* a production SDK
* a production-ready agent runtime
* universal agent safety
* an industry standard

## Next Milestone

Recommended next milestone:

`v0.8.1 File Fuse Static Case Manifest`

Final document verdict:

`READY_FOR_V0_8_1_FILE_FUSE_STATIC_CASE_MANIFEST`
