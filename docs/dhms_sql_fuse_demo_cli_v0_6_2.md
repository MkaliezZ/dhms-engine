# DHMS SQL Fuse Demo CLI v0.6.2

## Purpose

v0.6.2 adds a minimal CLI demo for the SQL Fuse benchmark.

The goal is demonstrability, not new capability. The CLI makes the
non-executing DHMS-AgentFuse-Bench SQL v0 result easy to run from the command
line while preserving the existing safety boundaries.

## Relationship to v0.6.1

v0.6.1 created the non-executing SQL benchmark layer:
`DHMS-AgentFuse-Bench SQL v0`.

v0.6.2 exposes that benchmark through a simple CLI demo. The demo delegates to
the existing benchmark runner and does not add SQL execution.

## CLI Command

Run:

```bash
python3 cli.py demo-sql-fuse
```

The command writes or refreshes:

- `reports/dhms_agentfuse_bench_sql_v0/summary.json`
- `reports/dhms_agentfuse_bench_sql_v0/summary.md`

## Expected Output

Expected output includes:

```text
DHMS SQL Fuse Demo
benchmark_name=DHMS-AgentFuse-Bench SQL v0
cases_total=7
cases_passed=7
release_eligible_count=1
blocked_or_fail_closed_count=6
direct_execution_allowed_count=0
sql_executed_by_benchmark_count=0
sqlite_database_created_by_benchmark_count=0
sandbox_executed_by_benchmark_count=0
mutation_sql_executed_count=0
rejected_input_executed_count=0
failed_checks=[]
linked_actual_release_proof=v0.5.15 existing controlled release validation
final_verdict=SQL_FUSE_DEMO_PASS
```

## Safety Boundaries

The CLI demo:

- does not execute SQL
- does not create SQLite databases
- does not import `sqlite3` in new demo code
- does not create sandbox files
- does not expand the SQL allowlist
- does not invoke OpenClaw
- does not invoke DeepSeek
- does not use provider SDKs
- does not use agent SDKs
- does not use HTTP/network clients
- does not implement file/shell/MCP policy
- does not implement production runtime support

## Relationship to v0.5.15 Proof

The actual controlled SQL sandbox release proof remains v0.5.15.

v0.6.2 only demonstrates the benchmark and linked proof status. It does not
reimplement the v0.5.15 temporary SQLite execution path and does not create a
second SQL executor.

## Not Claimed

v0.6.2 does not claim:

- arbitrary SQL support
- mutation SQL execution
- production DB safety
- production SQL agent support
- user data safety
- credentialed DB execution
- network DB execution
- OpenClaw runtime integration
- DeepSeek/provider integration
- provider SDK integration
- agent SDK integration
- HTTP adapter
- file/shell/MCP policy
- API implementation
- adapter implementation
- production-ready agent runtime

## Next Milestone

Recommended next milestone:

`v0.6.3 Minimal API / Adapter Skeleton`

## Final Verdict

`READY_FOR_V0_6_3_MINIMAL_API_ADAPTER_SKELETON`
