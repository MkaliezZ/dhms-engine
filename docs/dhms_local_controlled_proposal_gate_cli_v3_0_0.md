# DHMS Local Controlled Proposal Gate CLI v3.0.0

## Title and metadata

Milestone: `v3.0.0 Local Controlled Proposal Gate CLI`

Status: `local deterministic CLI implementation`

Previous milestone: `v2.9.2 Controlled Proposal Replay Validation + Freeze + README Sync`

Next milestone: `v3.0.1 CLI Evidence Trace Validation`

Mandatory post-v3.0 milestone: `v3.1.0 Real LangChain Agent Interception Minimal Harness`

Reasoning level: `Super High`

## Purpose

v3.0.0 adds the first local dynamic DHMS tool after the frozen v2.9 replay
evidence line: a deterministic, stdlib-only, non-executing controlled proposal
gate CLI.

The CLI reads one local proposal JSON file, evaluates it before execution, and
prints a structured gate result. It does not execute proposals.

## Locked v3.0 sequence

* `v3.0.0 Local Controlled Proposal Gate CLI`
* `v3.0.1 CLI Evidence Trace Validation`
* `v3.0.2 CLI Result Review + README Sync`

v3.0 must not expand into a planning, contract, fixtures, runner, proof, freeze,
and sync sequence.

## Mandatory v3.1 transition

After v3.0.2, the required next line is:

`v3.1.0 Real LangChain Agent Interception Minimal Harness`

v3.0.0 does not add LangChain, SQLDatabaseToolkit, real agent interception, model
API calls, DB access, or production runtime behavior.

## CLI command

```bash
python3 cli.py gate-proposal <proposal_json_path>
```

The command exits `0` for successful evaluation, including `FAIL_CLOSED`
decisions. It exits nonzero for missing files, invalid JSON, or unsupported CLI
usage.

## Gate evaluator behavior

The evaluator is implemented in:

`dhms_agentfuse/controlled_proposal_gate.py`

It uses deterministic local rules:

* `RELEASE_CANDIDATE` only for local, read-only, non-executing proposals that
  explicitly declare the safe boundary
* `FAIL_CLOSED` for dangerous or unsupported requested capabilities
* `HOLD_FOR_REVIEW` for ambiguous proposals without explicit dangerous
  capability and without a complete safe boundary

## Example proposals

* `examples/proposals/safe_read_only_summary.json` -> `RELEASE_CANDIDATE`
* `examples/proposals/drop_table.json` -> `FAIL_CLOSED` with `sql_mutation`
* `examples/proposals/model_api_request.json` -> `FAIL_CLOSED` with `model_api`

## Output contract

Each result includes:

* `dhms_gate_version`
* `proposal_id`
* `decision`
* `reason`
* `blocked_capabilities`
* `execution_authorized`
* `runtime_behaviors_added`
* `evidence_trace`

## Safety invariants

Every v3.0.0 CLI result must keep:

* `execution_authorized=false`
* `runtime_behaviors_added=0`
* `observed_before_execution=true`
* `deterministic=true`
* `stdlib_only=true`
* no SQL execution
* no DB access
* no model API
* no network
* no subprocess
* no env access
* no credentials
* no user data
* no file mutation
* no LangChain
* no KerniQ
* no E2B
* no production runtime

## What v3.0.0 adds

v3.0.0 adds:

* local `gate-proposal` CLI command
* deterministic local gate evaluator
* three local proposal examples
* concise CLI documentation
* package index and roadmap links

## What v3.0.0 does not add

v3.0.0 does not add:

* proposal execution
* real tool calls
* SQL execution
* DB access
* model API calls
* network calls
* subprocess calls
* env access
* credential access
* user-data access outside the supplied proposal JSON file
* file mutation
* LangChain integration
* SQLDatabaseToolkit support
* KerniQ integration
* E2B integration
* production runtime
* release or tag

## Public claim boundary

DHMS may claim only:

DHMS has a local deterministic controlled proposal gate CLI that reads a local
proposal JSON file, evaluates it before execution, and emits a structured gate
result with `execution_authorized=false` and `runtime_behaviors_added=0`. It
does not execute proposals, call tools, access SQL/DB/model
APIs/network/subprocess/env/credentials/user data, integrate LangChain,
integrate SQLDatabaseToolkit, integrate KerniQ, integrate E2B, or claim
production readiness.

## Explicit non-claims

v3.0.0 does not claim:

* production readiness
* real agent integration
* real LangChain integration
* SQLDatabaseToolkit support
* SQL execution support
* DB protection
* model-provider integration
* credential safety
* user-data safety
* KerniQ integration
* E2B integration
* runtime execution
* real execution authorization
* arbitrary real-world agent protection
* external database support
* real tool call support
* release readiness

## Files changed

v3.0.0 changes only:

* `cli.py`
* `dhms_agentfuse/controlled_proposal_gate.py`
* `examples/proposals/safe_read_only_summary.json`
* `examples/proposals/drop_table.json`
* `examples/proposals/model_api_request.json`
* `docs/dhms_local_controlled_proposal_gate_cli_v3_0_0.md`
* `docs/dhms_agentfuse_protocol_package_index_v0_7_0.md`
* `docs/dhms_agentfuse_development_roadmap.md`

## Files intentionally not modified

v3.0.0 intentionally does not modify:

* `README.md`
* v2.9 replay records
* v2.9 validators and freeze docs
* v2.8 fixtures and validators
* v2.7 proof documents, scripts, fixtures, or screenshots
* dependency files
* release or tag files

## Manual smoke commands

```bash
python3 cli.py gate-proposal examples/proposals/safe_read_only_summary.json
python3 cli.py gate-proposal examples/proposals/drop_table.json
python3 cli.py gate-proposal examples/proposals/model_api_request.json
python3 validation/run_dhms_controlled_proposal_replay_evidence_validation_v0.py
python3 validation/run_dhms_controlled_agent_proposal_gate_fixture_validation_v0.py
git diff --check
git diff --cached --check
```

## Final verdict

`READY_FOR_V3_0_1_CLI_EVIDENCE_TRACE_VALIDATION`
