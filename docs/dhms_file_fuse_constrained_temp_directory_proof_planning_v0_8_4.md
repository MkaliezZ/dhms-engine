# DHMS File Fuse Constrained Temp-Directory Proof Planning v0.8.4

## Purpose

v0.8.4 plans a future constrained temp-directory proof for the DHMS File
Operation Safety Fuse line.

Core v0.8.4 sentence:

`v0.8.4 plans a constrained temp-directory proof for the DHMS File Operation Safety Fuse. It does not implement the proof and does not add file operation capability.`

Core safety principle:

`A constrained proof must be designed before it is implemented, and implementation requires explicit approval.`

This phase is planning-only. It does not implement the proof, does not add file
operation capability, does not add a file adapter, and does not authorize
implementation. A future constrained proof requires explicit approval before
any implementation work may begin.

## Relationship to v0.8.0-v0.8.3

v0.8.0 planned the File Operation Safety Fuse as DHMS's preferred second
execution fuse proof line. v0.8.1 added static, inert manifest cases. v0.8.2
added a non-executing benchmark over that manifest. v0.8.3 added
non-executing examples and static trace examples.

v0.8.4 defines the safety envelope for a possible future constrained
temp-directory proof. It does not change v0.8.0 planning semantics, v0.8.1
manifest semantics, v0.8.2 benchmark semantics, or v0.8.3 example semantics.

## Why a Constrained Temp-Directory Proof

The v0.5 SQL proof used a tightly controlled temporary SQLite sandbox. The
File Operation Safety Fuse needs an equivalent proof shape before DHMS can make
broader claims about controlled file-operation release behavior.

A constrained temp-directory proof can demonstrate controlled side effects
without touching repository files, user files, credentials, source files,
configuration files, home directories, production data, or persistent
resources. Any future proof must show that approved side effects occur only
inside a disposable temp root and that rejected paths remain unopened,
unresolved, and non-executing.

## Proof Authorization Gate

No constrained temp-directory proof may be implemented without the following
exact future approval statement:

`I explicitly approve implementing the v0.8.4 constrained temp-directory proof under the planning boundaries in docs/dhms_file_fuse_constrained_temp_directory_proof_planning_v0_8_4.md.`

Without this exact approval, no implementation may occur. Planning a fuse line
does not authorize implementation or execution.

## Planned Proof Scope

Allowed future proof scope, only after explicit approval:

* create one temp directory outside the repository
* create a small synthetic allowlisted fixture inside that temp directory
* read only that synthetic allowlisted fixture
* write only one deterministic synthetic report inside an allowlisted
  subdirectory of that temp directory
* block `.env`, private key, path traversal, symlink escape, source overwrite,
  arbitrary path write, delete, and unsupported operation proposals
* record trace summary
* verify cleanup
* delete temp directory
* verify deletion

These are future proof boundaries only. v0.8.4 does not implement them.

## Planned Proof Non-Scope

Forbidden future proof behavior:

* no repository file writes
* no source file writes
* no source file reads as proof target
* no `.env` reads
* no private key reads
* no home directory access
* no customer data access
* no production data access
* no path traversal
* no symlink escape
* no arbitrary external path writes
* no delete outside temp root
* no shell execution
* no HTTP/network
* no MCP
* no OpenClaw
* no DeepSeek/provider/agent SDK
* no production DB
* no persistent sandbox
* no hidden local state
* no real user files

## Planned Temp Root Constraints

Future temp root constraints:

* temp root must be created by runtime using safe temp API
* temp root must be outside repo
* temp root path must be recorded
* temp root must contain only synthetic fixture files
* temp root must be deleted at the end
* deletion must be verified
* if cleanup fails, final verdict must fail
* no symlinks allowed
* no hidden files allowed
* no parent path traversal allowed
* no absolute path targets except the generated temp root itself
* no writes outside allowlisted report subdirectory
* no source tree paths allowed

These constraints are planning requirements for a future phase. v0.8.4 does
not implement temp root creation, cleanup, or verification.

## Planned Future Proof Cases

The future constrained proof case set should include at least:

| Case ID | Operation | Expected decision | Expected execution | Target / constraint |
| --- | --- | --- | --- | --- |
| `file_temp_read_allowlisted_fixture_released` | read | constrained release candidate | true only in future approved proof | synthetic fixture inside temp root; cleanup required |
| `file_temp_write_allowlisted_report_released` | write | constrained release candidate | true only in future approved proof | synthetic report inside temp root allowlisted report dir; cleanup required |
| `file_temp_read_env_blocked` | read | block | false | `.env` must not be opened |
| `file_temp_read_private_key_blocked` | read | block | false | private key path must not be opened |
| `file_temp_path_traversal_blocked` | read/write | block/fail-closed | false | traversal path must not be resolved against filesystem |
| `file_temp_symlink_escape_blocked` | read | block/fail-closed | false | symlink must not be followed |
| `file_temp_source_overwrite_blocked` | write | block or hold | false | source path must not be opened |
| `file_temp_arbitrary_external_write_blocked` | write | block/fail-closed | false | external path must not be touched |
| `file_temp_delete_blocked` | delete | block/fail-closed | false | delete operation must not execute |
| `file_temp_unsupported_operation_fail_closed` | unsupported | fail-closed | false | unsupported operation must not execute |

This is a planned future case set only. It is not added to a runnable manifest
in v0.8.4 and no runner logic is implemented.

## Planned Future Metrics

Future metrics may include:

* `total_planned_cases`
* `approved_constrained_release_cases`
* `blocked_or_fail_closed_cases`
* `actual_file_operations_executed_count`
* `synthetic_fixture_read_count`
* `synthetic_report_write_count`
* `rejected_path_opened_count`
* `rejected_path_resolved_count`
* `source_tree_touched_count`
* `external_path_touched_count`
* `symlink_followed_count`
* `temp_root_created_count`
* `temp_root_deleted_count`
* `temp_root_deletion_verified_count`
* `cleanup_failed_count`
* `failed_checks`

These metrics are planning fields only. v0.8.4 does not implement metric
collection.

## Planned Future Trace Fields

Future trace fields may include:

* `trace_id`
* `case_id`
* `operation_type`
* `temp_root`
* `requested_path_template`
* `normalized_candidate_path`
* `path_scope`
* `path_policy_result`
* `risk_tier`
* `expected_safety_decision`
* `actual_safety_decision`
* `expected_gate_state`
* `actual_gate_state`
* `expected_executed`
* `actual_executed`
* `execution_scope`
* `cleanup_required`
* `cleanup_verified`
* `rejected_path_opened`
* `rejected_path_resolved`
* `source_tree_touched`
* `external_path_touched`
* `symlink_followed`
* `final_verdict`

These are future planning fields only. v0.8.4 does not change schemas.

## Failure Conditions

A future constrained proof must fail if:

* temp root is inside repo
* temp root is not deleted
* deletion cannot be verified
* rejected path is opened
* rejected path is resolved when it should remain inert
* source tree is touched
* `.env` is opened
* private key path is opened
* symlink is followed
* path traversal escapes temp root
* external path is written
* delete operation executes
* unsupported operation executes
* shell/network/MCP/provider SDK is invoked
* any unapproved file operation occurs
* expected trace fields are missing
* final cleanup is incomplete

## Non-execution Guarantee for v0.8.4

v0.8.4 does not:

* create temp roots
* create fixtures
* read synthetic fixtures
* write synthetic reports
* delete temp roots
* perform cleanup verification
* implement file policy
* add a file adapter
* add runtime behavior
* authorize implementation without explicit approval

## What v0.8.4 Does Not Claim

v0.8.4 does not claim:

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
* size enforcement
* extension enforcement
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

`v0.8.4.1 Constrained Temp-Directory Proof Implementation — requires explicit approval`

Final document verdict:

`READY_FOR_EXPLICIT_APPROVAL_BEFORE_V0_8_4_1_CONSTRAINED_TEMP_DIRECTORY_PROOF_IMPLEMENTATION`
