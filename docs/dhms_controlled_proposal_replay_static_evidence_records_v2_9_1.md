# DHMS Controlled Proposal Replay Static Evidence Records v2.9.1

## Title and metadata

Milestone: `v2.9.1 Controlled Proposal Replay Contract + Static Evidence Records`

Status: `contract plus static records only`

Previous milestone: `v2.9.0 Next DHMS Proof Line Planning`

Next milestone: `v2.9.2 Controlled Proposal Replay Validation + Freeze + README Sync`

Reasoning level: `Super High`

## Purpose

v2.9.1 adds static Controlled Proposal Replay Evidence records for the frozen
v2.8 Controlled Agent Proposal Gate fixture validation proof.

The records are inert evidence data only. They do not replay execution, run a
validator, mutate fixtures, or add runtime behavior.

## Manifest path

`benchmarks/dhms_controlled_proposal_replay_evidence_v0/replay_records.json`

## Source evidence

The static records reference:

* source fixture manifest: `benchmarks/dhms_controlled_agent_proposal_gate_v0/proposals.json`
* source validator: `validation/run_dhms_controlled_agent_proposal_gate_fixture_validation_v0.py`
* source freeze: `docs/dhms_controlled_agent_proposal_gate_result_review_and_freeze_v2_8_4.md`
* frozen marker: `DHMS_CONTROLLED_AGENT_PROPOSAL_GATE_FIXTURE_VALIDATION_PASS`

## Record count

The manifest contains `record_count=16` and exactly 16 static records.

## Record families

The records cover:

* 1 `RELEASE_CANDIDATE` inert controlled proposal
* 15 `FAIL_CLOSED` proposal records
* SQL execution, SQL mutation, schema introspection, result readback, DB
  connection, credential scope, user-data scope, unsupported tool, malformed
  proposal, missing boundary, ambiguous handoff, model API, network, subprocess,
  and file mutation boundaries

## Static replay rules

Every record uses:

* `replay_scope=repository_local_read_only_replay_evidence`
* `replay_mode=static_evidence_record_only`
* `expected_replay_status=REPLAY_EVIDENCE_STATIC_ONLY`
* `expected_execution_authorized=false`
* `expected_runtime_behaviors_added=0`
* `expected_real_world_counters_zero=true`
* `expected_non_execution_assertions_preserved=true`

## Counter and runtime boundary

The records preserve the v2.8 counter-zero and non-execution boundary. They do
not execute validators, source code, SQL, DB calls, model APIs, network calls,
subprocesses, env reads, credential reads, user-data reads, KerniQ calls, E2B
handoffs, or production runtime behavior.

## What v2.9.1 adds

v2.9.1 adds:

* a replay evidence contract
* static replay evidence records
* static records documentation
* package index links
* roadmap status updates

## What v2.9.1 does not add

v2.9.1 does not add:

* a validator
* source code
* a CLI
* a schema
* a parser
* a runner
* screenshots
* dependency changes
* proof execution behavior
* runtime behavior
* a release
* a tag

## Public claim boundary

DHMS may claim only:

DHMS has added a repository-local, static, read-only Controlled Proposal Replay
Evidence contract and 16 static replay evidence records referencing the frozen
v2.8 Controlled Agent Proposal Gate fixture validation proof. These records
preserve the frozen validation marker and replay boundaries as inert evidence
data only. v2.9.1 adds no validator, source code, CLI, schema, runtime behavior,
integrations, release, or tag.

## Explicit non-claims

v2.9.1 does not claim:

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
* CLI support
* schema support
* validator support for replay records
* runtime execution
* real execution authorization
* arbitrary real-world agent protection
* external database support
* real tool call support
* release readiness

## Files changed

v2.9.1 changes only:

* `docs/dhms_controlled_proposal_replay_evidence_contract_v2_9_1.md`
* `docs/dhms_controlled_proposal_replay_static_evidence_records_v2_9_1.md`
* `benchmarks/dhms_controlled_proposal_replay_evidence_v0/replay_records.json`
* `docs/dhms_agentfuse_protocol_package_index_v0_7_0.md`
* `docs/dhms_agentfuse_development_roadmap.md`

## Files intentionally not modified

v2.9.1 intentionally does not modify:

* `README.md`
* `docs/dhms_next_proof_line_planning_v2_9_0.md`
* `benchmarks/dhms_controlled_agent_proposal_gate_v0/proposals.json`
* `validation/run_dhms_controlled_agent_proposal_gate_fixture_validation_v0.py`
* v2.8.0-v2.8.4 frozen evidence files
* v2.7 proof documents, scripts, fixtures, or screenshots
* source files
* validation files
* schemas
* CLI files
* dependency files
* release or tag files

## Validation commands

```bash
python3 -m json.tool benchmarks/dhms_controlled_proposal_replay_evidence_v0/replay_records.json >/dev/null
python3 validation/run_dhms_controlled_agent_proposal_gate_fixture_validation_v0.py
python3 -m json.tool benchmarks/dhms_controlled_agent_proposal_gate_v0/proposals.json >/dev/null
python3 validation/run_dhms_pre_execution_fuse_loop_proof_v0.py
python3 validation/run_dhms_pre_execution_fuse_loop_runner_validation_v0.py
git diff --check
git diff --cached --check
```

## Final verdict

`READY_FOR_V2_9_2_CONTROLLED_PROPOSAL_REPLAY_VALIDATION_FREEZE_README_SYNC`
