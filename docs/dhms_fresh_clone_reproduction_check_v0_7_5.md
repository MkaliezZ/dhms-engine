# DHMS Fresh Clone Reproduction Check v0.7.5

## Purpose

v0.7.5 verifies the public DHMS AgentFuse protocol package from a fresh clone.
The goal is external reproducibility: a reader should be able to clone the
public repository, check out the public development branch, and run the public
demo, benchmark, minimal API smoke, and protocol examples smoke without hidden
local state.

This phase documents reproduction evidence only. It does not add runtime
behavior, does not add execution capability, does not add benchmark cases, and
does not implement any new adapter or execution path.

Core reproduction principle:

`A public protocol package is not complete until a clean clone can run the documented public commands without hidden local state.`

Core safety principle:

`Fresh clone reproduction must prove public reproducibility without expanding execution capability.`

## Reproduction Target

* Repository: `https://github.com/MkaliezZ/dhms-engine.git`
* Branch: `agent-harness-v1`
* Start HEAD checked: `a8ecf8fac9c2681165b3680b5d680e9e538f8061`
* Current package line: `v0.7.5 Fresh Clone Reproduction Check`
* Prior patch: `v0.7.4.1 Package Index Link Patch`
* Temporary fresh clone path used:
  `/var/folders/6h/rm32wwgd3sqdd45nm70yhzd40000gn/T/tmp.Uk932yPn/dhms-engine-fresh-clone`

The fresh clone resolved `agent-harness-v1` to:

```text
a8ecf8fac9c2681165b3680b5d680e9e538f8061
```

Because the branch HEAD matched the expected start HEAD, no corrective detached
checkout was required.

## Fresh Clone Commands

The reproduction used a temporary directory outside the repository:

```bash
TMPDIR_PATH="$(mktemp -d)"
cd "$TMPDIR_PATH"
git clone https://github.com/MkaliezZ/dhms-engine.git dhms-engine-fresh-clone
cd dhms-engine-fresh-clone
git checkout agent-harness-v1
git rev-parse HEAD
```

Observed HEAD:

```text
a8ecf8fac9c2681165b3680b5d680e9e538f8061
```

The temporary clone was removed after evidence collection. No temporary clone
files were committed.

## Public Command Reproduction

| Command | Result | Key verdict marker | Non-execution summary |
| --- | --- | --- | --- |
| `python3 cli.py demo-sql-fuse` | PASS | `SQL_FUSE_DEMO_PASS` | `sql_executed_by_benchmark_count=0`, `sqlite_database_created_by_benchmark_count=0`, `sandbox_executed_by_benchmark_count=0`, `demo_executed_sql=false`, `demo_created_sqlite_database=false` |
| `python3 validation/run_dhms_agentfuse_bench_sql_v0.py` | PASS | `status=PASS` | `cases_total=7`, `cases_passed=7`, `release_eligible_count=1`, `blocked_or_fail_closed_count=6`, `sql_executed_by_benchmark_count=0`, `sqlite_database_created_by_benchmark_count=0` |
| `python3 validation/run_dhms_agentfuse_minimal_api_skeleton_smoke.py` | PASS | `DHMS_AGENTFUSE_MINIMAL_API_SKELETON_PASS` | `cases_total=3`, `cases_passed=3`, `executed_count=0`, `direct_execution_allowed_count=0`, `sql_executed=false`, `sqlite_database_created=false`, `sandbox_created=false` |
| `python3 validation/run_dhms_agentfuse_protocol_examples_smoke.py` | PASS | `DHMS_AGENTFUSE_PROTOCOL_EXAMPLES_PASS` | `examples_total=3`, `examples_passed=3`, `trace_examples_total=3`, `executed_count=0`, `direct_execution_allowed_count=0`, `sql_executed=false`, `sqlite_database_created=false`, `sandbox_created=false` |

The public command path reproduced the SQL Fuse demo, DHMS-AgentFuse-Bench SQL
v0 benchmark, DHMS AgentFuse Minimal API smoke, and v0.7.1 protocol examples
smoke from a fresh clone.

## Historical Cross-check Reproduction

| Command | Result | Safety summary |
| --- | --- | --- |
| `python3 validation/run_runtime_execution_policy_freeze_stub.py` | PASS | `policy_cases_total=7`, `policy_cases_passed=7`, `unique_release_eligible_count=1`, `blocked_or_fail_closed_count=6`, `direct_execution_allowed_count=0`, `sql_executed_count=0`, `sqlite_database_created_count=0`, `sandbox_executed_count=0`, `failed_checks=[]` |
| `python3 validation/run_sql_sandbox_runtime_first_actual_controlled_release.py` | PASS | `actual_release_executed_count=1`, `rejected_actual_release_count=6`, `only_allowlisted_select_executed=true`, `mutation_detected_count=0`, `sandbox_deleted_count=1`, `sandbox_deletion_verified_count=1`, `failed_checks=[]` |
| `python3 validation/run_sql_safety_temp_sqlite_mutation_block_test.py` | PASS | `total_sql_safety_cases=7`, `passed_sql_safety_cases=7`, `mutation_probe_count=5`, `mutation_probe_blocked_count=5`, `mutation_sql_executed=false`, `sandbox_deleted=true`, `sandbox_deletion_verified=true`, `failed_checks=[]` |

The historical controlled-release cross-check remains limited to the existing
v0.5.15 approved proof path. It does not create a new v0.7.5 execution path.

## Package Link / Path Verification

All required public package paths were present in the fresh clone:

| Path | Result |
| --- | --- |
| `README.md` | present |
| `CONTRIBUTING.md` | present |
| `docs/dhms_agentfuse_protocol_package_index_v0_7_0.md` | present |
| `docs/dhms_agentfuse_development_roadmap.md` | present |
| `docs/dhms_execution_fuse_protocol_v0_6_0.md` | present |
| `docs/dhms_agentfuse_bench_sql_v0_6_1.md` | present |
| `docs/dhms_sql_fuse_demo_cli_v0_6_2.md` | present |
| `docs/dhms_agentfuse_minimal_api_adapter_skeleton_v0_6_3.md` | present |
| `docs/dhms_agentfuse_protocol_examples_v0_7_1.md` | present |
| `docs/dhms_risk_tiered_fuse_policy_v0_7_2.md` | present |
| `docs/dhms_landscape_comparison_v0_7_3.md` | present |
| `docs/dhms_contribution_guide_case_format_v0_7_4.md` | present |
| `examples/dhms_agentfuse/sql_fuse_allowlisted_candidate_example.py` | present |
| `examples/dhms_agentfuse/sql_mutation_blocked_example.py` | present |
| `examples/dhms_agentfuse/unsupported_non_sql_proposal_example.py` | present |
| `examples/dhms_agentfuse/trace_examples.json` | present |
| `validation/run_dhms_agentfuse_protocol_examples_smoke.py` | present |
| `benchmarks/dhms_agentfuse_sql_v0/cases.json` | present |
| `dhms_agentfuse/` | present |

The v0.7.4.1 package index link patch was preserved: the protocol examples
documentation, examples directory, static trace examples, and examples smoke
validation remain indexed.

## No Hidden Local State

The reproduction used a fresh public clone outside the original working
directory. No local original working directory state was needed. No uncommitted
files were needed. No private files were needed. No secrets were needed. No
provider credentials were needed.

The public command path depends only on repository contents and the local
Python 3 runtime used to invoke the documented scripts.

## Non-execution Guarantee

v0.7.5 adds no new runtime behavior and no new execution capability.

* CLI demo remains non-executing.
* Benchmark runner remains non-executing.
* Minimal API skeleton remains non-executing.
* Protocol examples remain non-executing.
* No new SQL execution path was introduced.
* No SQL allowlist expansion occurred.
* No file, shell, HTTP, MCP, OpenClaw, DeepSeek, provider SDK, or agent SDK
  integration was added or run.

The only reproduced SQL execution remains the historical v0.5.15 controlled
sandbox proof validation, which executes exactly one approved allowlisted SELECT
inside the existing temporary local SQLite proof path.

## What v0.7.5 Does Not Claim

v0.7.5 does not claim:

* arbitrary SQL support
* direct SQL execution
* mutation SQL execution
* production DB safety
* production SQL agent support
* user data safety
* credentialed DB execution
* network DB execution
* OpenClaw runtime integration
* DeepSeek/provider integration
* provider SDK integration
* agent SDK integration
* HTTP adapter
* file adapter
* shell adapter
* MCP integration
* MCP replacement
* a production SDK
* a production-ready agent runtime
* universal agent safety
* an industry standard

## v0.7 Line Summary

* v0.7.0 Public Protocol Package
* v0.7.1 Protocol Examples
* v0.7.2 Risk-Tiered Fuse Policy Draft
* v0.7.3 Landscape / Comparison Doc
* v0.7.4 Contribution Guide / Case Format
* v0.7.4.1 Package Index Link Patch
* v0.7.5 Fresh Clone Reproduction Check

## Next Milestone

Recommended next milestone:

`v0.8.0 File Operation Safety Fuse Planning`

Do not implement v0.8 in v0.7.5. Do not implement file policy in v0.7.5.

Final document verdict:

`READY_FOR_V0_8_0_FILE_OPERATION_SAFETY_FUSE_PLANNING`
