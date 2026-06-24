# DHMS Mock Agent Interception Examples and Trace Examples v0.10.3

## Purpose

v0.10.3 adds static mock-agent interception examples and trace examples for the
v0.10 proof line.

The examples show how the v0.10.1 static SQL/File/HTTP tool-call proposals map
into DHMS interception lifecycle records:

1. mock agent emits inert proposal
2. DHMS observes proposal before execution
3. DHMS assigns safety decision
4. DHMS applies execution gate
5. mock agent receives runtime result
6. rejected proposal does not execute
7. constrained candidate is held for existing constrained proof path
8. trace record is produced

This milestone is static examples only. It does not add a runner, benchmark
runner, CLI command, source code, execution behavior, real agent runtime,
real LLM integration, SDK integration, adapters, API clients, credentials, or
production runtime behavior.

## Input References

The examples are derived from:

* `benchmarks/dhms_mock_agent_runtime_interception_v0/proposals.json`
* `validation/run_dhms_mock_agent_interception_benchmark_v0.py`

The input proposal set contains exactly 9 proposals:

* 3 SQL proposals
* 3 File proposals
* 3 HTTP proposals

No other proposal type is represented.

## Static Example Files

v0.10.3 adds:

* `examples/dhms_mock_agent_runtime_interception_v0/interception_examples.json`
* `examples/dhms_mock_agent_runtime_interception_v0/trace_examples.json`

Both files are static data only. They do not execute SQL, open file paths,
perform HTTP requests, start mock servers, invoke real agents, invoke LLMs,
call SDKs, or connect to external systems.

## Covered Proposal States

The static examples cover the required states:

| State | Count | Meaning |
| --- | ---: | --- |
| `CONSTRAINED_RELEASE_CANDIDATE` | 3 | SQL/File/HTTP candidates are held for existing constrained proof paths. |
| `BLOCK` | 4 | Destructive or unsafe proposals are blocked before execution. |
| `FAIL_CLOSED` | 2 | Malformed or hidden/unknown proposals fail closed before execution. |

## Proposal Coverage

| Proposal type | Count | Coverage |
| --- | ---: | --- |
| SQL | 3 | allowlisted SELECT candidate, DROP TABLE blocked, malformed SQL fail-closed |
| File | 3 | synthetic temp fixture candidate, `.env` read blocked, path traversal blocked |
| HTTP | 3 | synthetic local mock GET candidate, external POST blocked, hidden network fail-closed |

## Trace Fields

Each trace example includes:

* `mock_agent_run_id`
* `mock_agent_id`
* `proposal_id`
* `proposal_sequence_index`
* `proposal_type`
* `tool_name`
* `intent_summary`
* `observed_before_execution`
* `safety_decision`
* `execution_gate_state`
* `agent_runtime_result`
* `expected_executed`
* `actual_executed`
* `direct_execution_allowed`
* `constrained_proof_path`
* `trace_verdict`
* `not_claimed_scope`

Required successful values are frozen as:

* `observed_before_execution=true`
* `expected_executed=false`
* `actual_executed=false`
* `direct_execution_allowed=false`
* rejected actions use `constrained_proof_path=null`
* constrained candidates point only to existing SQL/File/HTTP constrained proof paths

## Existing Constrained Proof Paths

Constrained candidates remain held for existing proof paths only:

* SQL: `v0.5.15 SQL Sandbox Execution Fuse controlled SQLite sandbox release proof`
* File: `v0.8.4.1 File Operation Safety Fuse constrained synthetic temp-directory proof`
* HTTP: `v0.9.5.1 HTTP / Network Request Safety Fuse constrained local mock HTTP proof`

v0.10.3 does not create a new constrained proof path.

## Validation

Validate the static JSON files and existing benchmark:

```bash
python3 -m json.tool examples/dhms_mock_agent_runtime_interception_v0/interception_examples.json >/dev/null
python3 -m json.tool examples/dhms_mock_agent_runtime_interception_v0/trace_examples.json >/dev/null
python3 validation/run_dhms_mock_agent_interception_benchmark_v0.py
python3 cli.py bench-mock-agent-interception
```

Existing public demos should continue to pass:

```bash
python3 cli.py demo-sql-fuse
python3 cli.py demo-file-fuse
python3 cli.py demo-http-fuse
```

## Non-Execution Guarantee

v0.10.3 does not:

* execute SQL
* read or write proposal file paths
* perform HTTP requests
* start a mock HTTP server
* invoke a real agent runtime
* invoke a real LLM
* invoke Codex, Claude, OpenClaw, or DeepSeek
* invoke MCP or E2B
* invoke provider SDKs or agent SDKs
* add adapters
* add API clients
* add credential handling
* add production runtime behavior
* add new proposal types

The examples and trace examples are static records only.

## Not Claimed

v0.10.3 does not claim:

* production readiness
* real agent runtime interception
* real LLM execution
* Codex integration
* Claude integration
* OpenClaw integration
* DeepSeek integration
* MCP integration
* E2B integration
* provider SDK integration
* agent SDK integration
* arbitrary tool execution
* arbitrary SQL support
* arbitrary file operation support
* arbitrary HTTP/network support
* production DB safety
* production filesystem safety
* production HTTP safety
* credential handling
* user data safety certification
* universal agent safety
* industry-standard status

## Next Milestone

Recommended next milestone:

`v0.10.4 Controlled Mock Agent Runtime Interception Proof`

Final document verdict:

`READY_FOR_V0_10_4_CONTROLLED_MOCK_AGENT_RUNTIME_INTERCEPTION_PROOF`
