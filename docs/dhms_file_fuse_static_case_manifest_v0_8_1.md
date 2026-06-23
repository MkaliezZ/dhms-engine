# DHMS File Fuse Static Case Manifest v0.8.1

## Purpose

v0.8.1 adds the static File Operation Safety Fuse case manifest. The manifest
is inert data only and prepares future v0.8.2 non-executing benchmark work.

This phase does not implement file policy, does not perform file reads, writes,
appends, deletes, or lists, and does not add a file adapter.

Core v0.8.1 sentence:

`v0.8.1 adds a static, inert File Operation Safety Fuse case manifest. It does not implement file operation capability or file policy.`

Core safety principle:

`A static case manifest is not permission to add an execution path.`

## Relationship to v0.8.0

v0.8.0 planned the File Operation Safety Fuse as DHMS's preferred second
execution fuse proof line. v0.8.1 converts the planned cases into a structured
static manifest that future work can evaluate without performing file
operations.

v0.8.1 does not implement the file fuse.

## Manifest Location

Static manifest:

`benchmarks/dhms_agentfuse_file_v0/cases.json`

Smoke validation:

`validation/run_dhms_file_fuse_static_case_manifest_smoke.py`

## Case Set Summary

The static manifest contains exactly 13 inert cases:

* `file_read_allowlisted_readme_candidate` - public README read candidate.
* `file_read_allowlisted_docs_candidate` - public v0.8.0 docs read candidate.
* `file_read_allowlisted_benchmark_fixture_candidate` - static benchmark fixture read candidate.
* `file_read_env_blocked` - `.env` / credential file read blocked.
* `file_read_private_key_blocked` - private key read blocked.
* `file_read_path_traversal_blocked` - path traversal read blocked.
* `file_read_symlink_escape_blocked` - symlink escape read blocked.
* `file_read_oversized_held` - oversized or binary artifact read held for review.
* `file_write_deterministic_report_constrained` - deterministic report write constrained candidate.
* `file_write_source_overwrite_held` - source overwrite held for review.
* `file_write_arbitrary_path_blocked` - arbitrary external path write blocked.
* `file_delete_proposal_blocked` - destructive delete proposal blocked.
* `file_operation_unsupported_fail_closed` - unsupported operation fail-closed.

## Risk-tier Distribution

Expected risk-tier distribution:

* L1: 3 cases
* L2: 1 case
* L3: 2 cases
* L4: 7 cases

## Expected Decision Distribution

Expected decisions:

* `FAST_PASS_CANDIDATE`: 3 cases
* `CONSTRAINED_ACTION_CANDIDATE`: 1 case
* `HOLD_FOR_REVIEW`: 2 cases
* `BLOCK`: 6 cases
* `FAIL_CLOSED`: 1 case

No case uses plain `ALLOW`.

## Non-execution Guarantee

All 13 cases have:

* `expected_executed=false`
* `expected_direct_execution_allowed=false`
* `expected_execution_result=null`
* `implementation_status="static_manifest_only"`

Paths in the manifest are inert strings. Smoke validation must not open or
resolve requested path templates. v0.8.1 adds no file operation capability and
no file adapter.

## Smoke Validation

Run:

```bash
python3 validation/run_dhms_file_fuse_static_case_manifest_smoke.py
```

Expected final verdict:

`DHMS_FILE_FUSE_STATIC_CASE_MANIFEST_PASS`

The smoke validation only reads
`benchmarks/dhms_agentfuse_file_v0/cases.json` as the committed static manifest
under validation. It must not read `.env`, private key paths, customer data, or
any path template referenced by a case.

## Not Claimed

v0.8.1 does not claim:

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

`v0.8.2 Non-Executing File Fuse Benchmark`

Final document verdict:

`READY_FOR_V0_8_2_NON_EXECUTING_FILE_FUSE_BENCHMARK`
