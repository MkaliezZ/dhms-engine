# DHMS HTTP Fuse CLI Demo Wrapper v0.9.7

## Purpose

v0.9.7 adds only a CLI wrapper for the completed HTTP Fuse evidence chain. The
wrapper makes the current HTTP Fuse checks easier to run from the command line
without adding new proof semantics, execution capability, HTTP adapter support,
API client support, credential handling, or production HTTP safety claims.

## CLI Command

```bash
python3 cli.py demo-http-fuse
```

## What the Wrapper Runs

The wrapper runs these existing checks in order:

1. `validation/run_dhms_agentfuse_bench_http_v0.py`
2. `validation/run_dhms_constrained_local_mock_http_proof.py`

The first check is the existing non-executing HTTP benchmark over the static
HTTP Fuse manifest. The second check is the existing constrained local mock
HTTP proof that releases exactly one approved synthetic GET to a disposable
`127.0.0.1` mock target.

## Expected Success Output

```text
final_verdict=DHMS_HTTP_FUSE_DEMO_PASS
checks_total=2
checks_passed=2
non_executing_http_benchmark_passed=true
constrained_local_mock_http_proof_passed=true
actual_http_requests_executed_count=1
approved_mock_get_request_count=1
rejected_http_requests_executed_count=0
external_network_requests_attempted_count=0
dns_resolution_attempted_count=0
credentials_used_count=0
```

## Boundary

v0.9.7 is a CLI wrapper only. It does not modify existing HTTP runners,
manifests, examples, SQL/File runners, proof behavior, or proof semantics. It
does not add new network behavior, general HTTP execution, HTTP adapter
support, API client support, credential handling, SDK integration, MCP
integration, OpenClaw integration, DeepSeek integration, tags, or GitHub
Releases.

## Validation

```bash
python3 cli.py demo-http-fuse
python3 validation/run_dhms_agentfuse_bench_http_v0.py
python3 validation/run_dhms_constrained_local_mock_http_proof.py
python3 cli.py demo-sql-fuse
python3 cli.py demo-file-fuse
git diff --check
git diff --cached --check
```

## Next Milestone

`v0.9.8 SQL/File/HTTP Evidence Alignment`

Final document verdict:

`READY_FOR_V0_9_8_SQL_FILE_HTTP_EVIDENCE_ALIGNMENT`
