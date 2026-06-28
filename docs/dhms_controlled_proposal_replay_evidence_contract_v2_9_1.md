# DHMS Controlled Proposal Replay Evidence Contract v2.9.1

## Title and metadata

Milestone: `v2.9.1 Controlled Proposal Replay Contract + Static Evidence Records`

Status: `contract plus static records only`

Previous milestone: `v2.9.0 Next DHMS Proof Line Planning`

Next milestone: `v2.9.2 Controlled Proposal Replay Validation + Freeze + README Sync`

Reasoning level: `Super High`

## Purpose

v2.9.1 defines the Controlled Proposal Replay Evidence contract and adds static
replay evidence records for the frozen v2.8 Controlled Agent Proposal Gate
fixtures.

This milestone adds no validator, source code, CLI, schema, parser, runner, or
runtime behavior.

## Compressed v2.9 sequence

* `v2.9.0 Next DHMS Proof Line Planning`
* `v2.9.1 Controlled Proposal Replay Contract + Static Evidence Records`
* `v2.9.2 Controlled Proposal Replay Validation + Freeze + README Sync`

## Replay evidence definition

Controlled Proposal Replay Evidence is repository-local, static, read-only
evidence data that references already frozen inert proposal fixtures and
validator outcomes. It preserves the source proposal id, frozen decision,
fail-closed reason where applicable, validation marker, and non-execution
boundary as evidence records.

## Replay evidence non-definition

Replay evidence is not execution replay. It is not a validator, schema, CLI,
runtime, parser, runner, adapter, model call, SQL call, DB access, network call,
subprocess call, env read, credential read, user-data read, KerniQ invocation,
E2B handoff, release, or tag.

## Record manifest contract

The v2.9.1 manifest is:

`benchmarks/dhms_controlled_proposal_replay_evidence_v0/replay_records.json`

It references:

* `benchmarks/dhms_controlled_agent_proposal_gate_v0/proposals.json`
* `validation/run_dhms_controlled_agent_proposal_gate_fixture_validation_v0.py`
* `docs/dhms_controlled_agent_proposal_gate_result_review_and_freeze_v2_8_4.md`

The manifest must contain `record_count=16` and exactly one record for each
frozen v2.8.2 fixture id.

## Required record fields

Each replay record must include:

* `replay_record_id`
* `source_proposal_id`
* `source_decision`
* `source_fail_closed_reason` when `source_decision=FAIL_CLOSED`
* `replay_scope`
* `replay_mode`
* `source_fixture_manifest`
* `source_validator`
* `frozen_validation_marker`
* `expected_replay_status`
* `expected_execution_authorized`
* `expected_runtime_behaviors_added`
* `expected_real_world_counters_zero`
* `expected_non_execution_assertions_preserved`
* `replay_assertions`

## Replay assertions

Every replay record must assert:

* `static_record_only=true`
* `no_fixture_mutation=true`
* `no_validator_execution=true`
* `no_source_runtime_code=true`
* `no_cli=true`
* `no_schema=true`
* `no_sql_execution=true`
* `no_db_access=true`
* `no_model_api=true`
* `no_network=true`
* `no_subprocess=true`
* `no_env_access=true`
* `no_credentials=true`
* `no_user_data=true`
* `no_kerniq=true`
* `no_e2b=true`
* `no_production_runtime=true`

## Scope boundary

v2.9.1 may add only this contract document, the static records document, the
static replay records manifest, package index links, and roadmap status updates.

## Non-scope boundary

v2.9.1 must not add validators, source code, CLI, schemas, parsers, runners,
screenshots, dependency changes, proof execution behavior, runtime behavior,
releases, tags, LangChain, SQLDatabaseToolkit, SQL execution, DB access, model
APIs, network, subprocess, env access, credentials, user data, KerniQ, E2B, or
production runtime behavior.

## What v2.9.1 adds

v2.9.1 adds:

* replay evidence contract documentation
* static replay evidence records documentation
* 16 static replay evidence records
* package index links
* roadmap status for the compressed v2.9 sequence

## What v2.9.1 does not add

v2.9.1 does not add:

* validator support for replay records
* source code
* CLI support
* schema support
* runtime behavior
* proof execution behavior
* release or tag readiness

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
