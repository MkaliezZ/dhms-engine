# Contributing to DHMS AgentFuse

DHMS is an execution fuse protocol for AI agents. DHMS AgentFuse is the
benchmark, demo, API, and adapter-skeleton tool family around that protocol.

This repository is intentionally cautious about execution. A contribution that
adds a case, example, benchmark, or design note does not authorize a new
execution path.

## Safety Principles

* Fail closed by default.
* Do not add execution capability without explicit phase approval.
* Do not add or expand SQL execution paths casually.
* Do not expand the SQL allowlist without explicit phase approval.
* Do not add OpenClaw, DeepSeek, provider SDK, agent SDK, HTTP, file, shell,
  MCP, or production database integration without explicit phase approval.
* Keep design-only work clearly marked as design-only.
* Preserve README License and Trademark Notice text unless a phase explicitly
  authorizes legal/trademark edits.

## Proposing a Case

Every new DHMS case must specify expected decision behavior, expected execution
behavior, expected trace evidence, and not-claimed boundaries before
implementation.

Use the detailed case format in:

[`docs/dhms_contribution_guide_case_format_v0_7_4.md`](docs/dhms_contribution_guide_case_format_v0_7_4.md)

At minimum, include:

* case ID and category
* risk domain and expected risk tier
* proposal class and input summary
* expected safety decision and gate state
* expected release eligibility
* expected direct execution allowed value
* expected executed value
* trace expectations
* not-claimed scope
* linked proof or reference

Defaults matter: `expected_executed=false` and
`expected_direct_execution_allowed=false` unless a phase explicitly authorizes
controlled release.

## Proposing a Future Fuse Line

A future fuse-line proposal should describe the risk category, threat model,
expected allowed path, expected blocked path, trace contract, verification
method, sandbox or simulation boundary, non-execution guarantees, validation,
and rollback/freeze plan.

A future fuse-line proposal does not authorize implementation by itself.

## Validation Expectations

List targeted validation commands with each contribution. Common current
checks include:

```bash
python3 cli.py demo-sql-fuse
python3 validation/run_dhms_agentfuse_bench_sql_v0.py
python3 validation/run_dhms_agentfuse_minimal_api_skeleton_smoke.py
python3 validation/run_dhms_agentfuse_protocol_examples_smoke.py
python3 validation/run_runtime_execution_policy_freeze_stub.py
python3 validation/run_sql_sandbox_runtime_first_actual_controlled_release.py
python3 validation/run_sql_safety_temp_sqlite_mutation_block_test.py
git diff --check
```

## Not-Claimed Reminder

DHMS AgentFuse currently does not claim arbitrary SQL support, direct SQL
execution, mutation SQL execution, production DB safety, production SQL agent
support, user data safety, credentialed DB execution, network DB execution,
OpenClaw runtime integration, DeepSeek/provider integration, provider SDK
integration, agent SDK integration, HTTP adapter, file adapter, shell adapter,
MCP integration, MCP replacement, production SDK status, production-ready
agent runtime status, universal agent safety, or industry-standard status.
