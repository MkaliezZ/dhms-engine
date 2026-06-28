# DHMS Controlled Agent Proposal Static Fixtures v2.8.2

## Title and metadata

Milestone: `v2.8.2 Controlled Agent Proposal Static Fixtures`

Status: `static inert fixtures only`

Previous milestone: `v2.8.1 Controlled Agent Proposal Gate Contract + README Non-Claims Compression`

Next milestone: `v2.8.3 Controlled Agent Proposal Gate Non-Executing Validation`

Reasoning level: `Super High`

## Purpose

v2.8.2 adds static inert controlled-agent proposal fixtures for the v2.8
Controlled Agent Proposal Gate line.

The fixtures are data-only. They do not add a validator, runner, schema, CLI,
source code, parser, runtime behavior, or execution behavior.

## Relationship to v2.8.1

v2.8.1 defined the prose-only Controlled Agent Proposal Gate Contract. v2.8.2
adds the first fixture manifest that follows that contract.

The v2.8.1 contract remains unchanged. v2.8.2 does not reinterpret or weaken
the contract.

## Fixture manifest path

The fixture manifest is:

`benchmarks/dhms_controlled_agent_proposal_gate_v0/proposals.json`

## Fixture count

The manifest contains exactly 16 fixtures:

* 1 `RELEASE_CANDIDATE`
* 15 `FAIL_CLOSED`
* 0 `HOLD_FOR_REVIEW`

## Fixture families

The fixture families are:

* safe inert controlled proposal
* SQL execution request
* SQL mutation request
* schema introspection request
* result readback request
* database connection request
* credential scope request
* user data scope request
* unsupported tool request
* malformed proposal
* missing declared boundary
* ambiguous executor handoff
* model API request
* network request
* subprocess request
* file mutation request

## Required fields

Every fixture includes:

* `proposal_id`
* `agent_family`
* `controlled_agent_profile`
* `proposed_tool`
* `proposed_action`
* `tool_input_summary`
* `declared_boundary`
* `observed_before_execution`
* `expected_dhms_decision`
* `expected_executor_handoff_allowed`
* `expected_execution_authorized`
* `expected_mock_executor_received`
* `expected_mock_executor_invocations`
* `expected_sql_execution_attempts`
* `expected_db_connections`
* `expected_schema_introspection`
* `expected_result_readbacks`
* `expected_model_api_calls`
* `expected_network_calls`
* `expected_subprocess_calls`
* `expected_credential_accesses`
* `expected_user_data_accesses`
* `expected_file_mutation_attempts`
* `expected_executor_handoffs`
* `non_execution_assertions`

Every `FAIL_CLOSED` fixture also includes `expected_fail_closed_reason`.

## Counter rules

All real-world counters are 0 for every fixture:

* SQL execution attempts: 0
* DB connections: 0
* schema introspection: 0
* result readbacks: 0
* model API calls: 0
* network calls: 0
* subprocess calls: 0
* credential accesses: 0
* user data accesses: 0
* file mutation attempts: 0
* executor handoffs: 0

The one `RELEASE_CANDIDATE` fixture sets
`expected_executor_handoff_allowed=true` only as future bounded mock handoff
eligibility. It still sets `expected_execution_authorized=false` and all
real-world counters to 0.

## Inertness rules

The fixtures are inert data. They do not contain:

* executable code
* secrets
* credentials
* real user data
* live URLs
* database connection strings
* API keys
* tokens
* runnable shell commands
* runnable SQL intended for execution

## What v2.8.2 adds

v2.8.2 adds:

* one static inert fixture manifest with exactly 16 fixtures
* this documentation file
* package index links
* roadmap status updates

## What v2.8.2 does not add

v2.8.2 does not add:

* validator
* runner
* schema
* CLI command
* parser
* source code
* screenshot
* dependency change
* LangChain import or integration
* SQLDatabaseToolkit support
* SQL execution
* DB connection
* model API call
* network call
* subprocess call
* environment access
* credential handling
* real user data handling
* KerniQ integration
* E2B integration
* production runtime behavior
* release
* tag

## Public claim boundary

DHMS has added 16 repository-local, static inert controlled-agent proposal
fixtures following the v2.8.1 prose-only contract. These fixtures are data-only
and do not add validators, schemas, CLI, source code, runtime behavior,
LangChain integration, SQLDatabaseToolkit support, SQL execution, DB access,
model APIs, network/subprocess behavior, credential/user-data behavior, KerniQ,
E2B, production runtime, release, or tag.

## Explicit non-claims

v2.8.2 does not claim:

* production readiness
* real agent integration
* real LangChain integration
* SQLDatabaseToolkit support
* real SQL Agent support
* SQL execution support
* DB protection
* model-provider integration
* credential safety
* user-data safety
* KerniQ integration
* E2B integration
* CLI support
* schema support
* validator support
* runtime execution
* real execution authorization
* production runtime behavior

## Files changed

v2.8.2 changes only:

* `benchmarks/dhms_controlled_agent_proposal_gate_v0/proposals.json`
* `docs/dhms_controlled_agent_proposal_static_fixtures_v2_8_2.md`
* `docs/dhms_agentfuse_protocol_package_index_v0_7_0.md`
* `docs/dhms_agentfuse_development_roadmap.md`

## Files intentionally not modified

v2.8.2 intentionally does not modify:

* `README.md`
* `docs/dhms_controlled_agent_proposal_gate_contract_v2_8_1.md`
* `docs/dhms_controlled_agent_proposal_gate_planning_v2_8_0.md`
* v2.7 proof documents
* v2.7 proof scripts
* v2.7 fixtures
* v2.7 screenshots
* source files
* validation files
* CLI files
* schema files
* dependency files
* release or tag files

## Validation commands

Expected validation commands:

```bash
python3 -m json.tool benchmarks/dhms_controlled_agent_proposal_gate_v0/proposals.json >/dev/null
python3 validation/run_dhms_pre_execution_fuse_loop_proof_v0.py
python3 validation/run_dhms_pre_execution_fuse_loop_runner_validation_v0.py
python3 -m json.tool benchmarks/dhms_pre_execution_fuse_loop_v0/proposals.json >/dev/null
git diff --check
git diff --cached --check
```

## Targeted scan summary

Targeted scans should confirm:

* only allowed files changed
* exactly 16 fixtures exist
* no schema file was added
* no validator was added
* no CLI command was added
* no source file was changed
* no executable code exists in fixtures
* no secrets, credentials, user data, live URLs, API keys, tokens, or DB
  connection strings exist in fixtures
* all real-world counters are 0
* no production-ready claim was added
* no real LangChain, SQLDatabaseToolkit, SQL, DB, model, KerniQ, or E2B claim
  was added

## Acceptance checklist

* Manifest path exists
* Manifest JSON is valid
* `fixture_count=16`
* exactly 16 fixtures are present
* exactly 1 `RELEASE_CANDIDATE`
* exactly 15 `FAIL_CLOSED`
* all fixtures are observed before execution
* all fixtures deny execution authorization
* only the `RELEASE_CANDIDATE` fixture allows future bounded mock handoff
  eligibility
* all mock executor receipt fields remain false
* all mock executor invocation counts remain 0
* all real-world counters remain 0
* all `FAIL_CLOSED` fixtures include expected fail-closed reasons
* no validator, runner, schema, CLI, parser, source code, screenshot,
  dependency, release, or tag is added

## Final verdict

`READY_FOR_V2_8_3_CONTROLLED_AGENT_PROPOSAL_GATE_NON_EXECUTING_VALIDATION`
