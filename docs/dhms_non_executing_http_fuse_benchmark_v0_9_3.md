# DHMS Non-Executing HTTP Fuse Benchmark v0.9.3

## Audited Base Commit

`019808b7a8805ae1c5180a2ba28d04277481ffc1`

## Purpose

v0.9.3 adds a deterministic non-executing benchmark runner for the HTTP /
Network Request Safety Fuse line.

The benchmark evaluates the static inert v0.9.2 HTTP case manifest in memory
and produces deterministic metrics. It does not implement HTTP execution,
perform network calls, create HTTP clients, handle credentials, add HTTP
adapters, add examples, add CLI wrapper commands, or authorize real network
activity.

## Relationship to v0.9.0, v0.9.1, and v0.9.2

v0.9.0 selected `HTTP / Network Request Safety Fuse` as the next DHMS proof
line.

v0.9.1 planned inert HTTP/network request proposal shapes, risk categories,
decision boundaries, trace expectations, future metrics, and fail-closed
requirements.

v0.9.2 added the static inert HTTP case manifest with exactly 16 synthetic
HTTP/network request proposal cases.

v0.9.3 adds the non-executing benchmark step over that manifest. It keeps the
same staged strategy used by the File Fuse line: planning, static inert cases,
non-executing benchmark, examples, and freeze.

## Bounded Claim

v0.9.3 adds a deterministic non-executing HTTP Fuse benchmark runner over the
static inert v0.9.2 HTTP case manifest. The runner validates synthetic
HTTP/network request proposal cases as data-only safety contracts in memory and
produces deterministic metrics without performing HTTP execution, network calls,
URL fetching, socket operations, API client creation, HTTP adapter behavior,
credential handling, MCP/provider/agent SDK integration, or arbitrary tool
execution.

## Runner Path

`validation/run_dhms_agentfuse_bench_http_v0.py`

## Manifest Path

`benchmarks/dhms_agentfuse_http_v0/cases.json`

The runner reads this committed static manifest only. It treats every URL,
method, header, body, host, path, credential indicator, and risk field as inert
data.

## Benchmark Behavior

The runner:

* loads the static v0.9.2 manifest;
* validates top-level manifest fields;
* validates exactly 16 expected case IDs;
* validates required case fields;
* validates allowed decision classes;
* validates allowed gate values;
* validates decision-to-gate mappings;
* validates aggregate counts;
* validates the non-execution invariant;
* prints deterministic key-value metrics and a JSON summary;
* exits non-zero if any check fails.

The runner does not parse URLs into executable request objects, create HTTP
clients, resolve DNS, open URLs, create sockets, call browsers, call shell
commands, handle credentials, or invoke external tools.

## Expected Metrics

Expected deterministic metrics:

* `cases_total=16`
* `cases_passed=16`
* `allow_inert_count=1`
* `hold_for_review_count=1`
* `blocked_count=10`
* `fail_closed_count=4`
* `network_calls_executed_count=0`
* `http_clients_created_count=0`
* `credentials_used_count=0`
* `external_mutation_attempted_count=0`
* `manifest_case_count_matches=true`
* `schema_valid=true`
* `decisions_valid=true`
* `gates_valid=true`
* `non_execution_invariant_satisfied=true`

## Pass Verdict

`DHMS_AGENTFUSE_BENCH_HTTP_V0_PASS`

## Fail Verdict

`DHMS_AGENTFUSE_BENCH_HTTP_V0_FAIL`

On failure, the runner prints a deterministic `failure_reason` before returning
a non-zero exit code.

## Non-Execution Invariant

The benchmark invariant is:

`network_calls_executed_count == 0`

The runner must also keep:

* `http_clients_created_count=0`
* `credentials_used_count=0`
* `external_mutation_attempted_count=0`

The manifest read itself is not HTTP Fuse runtime behavior. It is only the
allowed read of the committed static benchmark manifest.

## Explicit Non-Claims

v0.9.3 does not claim:

* real HTTP execution;
* real network calls;
* web browsing;
* HTTP adapter support;
* API client support;
* credential handling;
* SSRF protection;
* production outbound request safety;
* data exfiltration protection;
* external API mutation safety;
* webhook safety;
* redirect safety;
* MCP integration;
* OpenClaw integration;
* DeepSeek/provider integration;
* provider SDK integration;
* agent SDK integration;
* shell execution;
* arbitrary tool execution;
* production readiness;
* industry standard status;
* replacement of MCP, guardrails, sandboxes, SDKs, or human approval systems.

## Implementation Boundaries

v0.9.3 does not add HTTP examples, does not add a CLI wrapper command, does not
change the HTTP static manifest, does not change existing SQL or File Fuse
proof semantics, and does not create or move release tags.

The runner must not import or use `requests`, `httpx`, `urllib`, `aiohttp`,
`http.client`, `socket`, `subprocess`, browser tools, network clients, provider
SDKs, agent SDKs, MCP tools, OpenClaw, or DeepSeek.

## Validation Command

```bash
python3 validation/run_dhms_agentfuse_bench_http_v0.py
```

Optional continuity checks:

```bash
python3 -m json.tool benchmarks/dhms_agentfuse_http_v0/cases.json >/tmp/dhms_http_cases_v0_9_3.json
python3 cli.py demo-sql-fuse
python3 cli.py demo-file-fuse
```

## Next Recommended Milestone

`v0.9.4 HTTP Fuse Non-Executing Examples`

Final document verdict:

`READY_FOR_V0_9_4_HTTP_FUSE_NON_EXECUTING_EXAMPLES`
