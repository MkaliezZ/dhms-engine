# DHMS README Public Landing Page Polish v2.7.4.2

## Title and Metadata

* Milestone: `v2.7.4.2 README Public Landing Page Polish`
* Status: `README landing-page polish only`
* Previous milestone: `v2.7.4.1 README Current Status Sync`
* Next milestone: `v2.8.0 Controlled Agent Proposal Gate Planning`
* Reasoning level: `High`

## Purpose

v2.7.4.2 improves README readability and public landing-page structure after
the v2.7.4 freeze and v2.7.4.1 status sync.

This milestone is documentation-only and README-polish-only.

## Current Status

The README now prioritizes:

* what DHMS is
* the current strongest proof
* what was proven
* how to reproduce it
* where the screenshot evidence is
* what DHMS does not claim yet
* where the full evidence chain lives

## Relationship to v2.7.4

v2.7.4 froze the repository-local, stdlib-only Minimal Pre-Execution Fuse Loop
proof. v2.7.4.2 preserves that frozen boundary and does not change proof
behavior.

## Relationship to v2.7.4.1

v2.7.4.1 synchronized README public status with the v2.7.4 freeze. v2.7.4.2
keeps that status and reshapes the README into a clearer public landing page.

## README Landing-Page Changes Made

The README now opens with a concise DHMS identity statement and the current
proof summary. It moves the v2.7 proof target, proof table, reproduction
command, proof output, screenshot evidence, evidence-chain links, claim
boundary, and non-claims above the historical evidence sections.

## Current Proof Summary Reflected in README

The README now includes a concise current proof table covering:

* proof target
* gate result
* fail-closed reason
* executor handoff
* execution authorization
* mock executor receipt
* mock executor invocations
* SQL execution attempts
* DB connections
* schema introspection
* result readbacks

## Screenshot Presentation

The README presents screenshot evidence in a collapsible details block:

```markdown
<details>
<summary>View v2.7.3 proof screenshot</summary>

![v2.7.3 pre-execution interception proof](docs/development/screenshots/v2_7_3_pre_execution_interception_proof/v2_7_3_pre_execution_interception_proof_terminal.png)

</details>
```

The screenshot path remains:

`docs/development/screenshots/v2_7_3_pre_execution_interception_proof/v2_7_3_pre_execution_interception_proof_terminal.png`

The README states that the screenshot captures the v2.7.3 proof command output:

```bash
python3 validation/run_dhms_pre_execution_fuse_loop_proof_v0.py
```

It also states that the screenshot is not a screenshot of:

```bash
python3 cli.py gate-proposal examples/proposals/drop_table.json
```

## Historical Evidence Compression

Long historical milestone paragraphs were compressed into short evidence-line
summaries with links. The README keeps historical evidence visible but moves it
below the current v2.7 proof.

## Public Claim Boundary

README polish does not expand claims beyond the v2.7.4 freeze.

The README may claim only:

DHMS has a repository-local, stdlib-only Minimal Pre-Execution Fuse Loop proof
showing that one inert LangChain-SQL-agent-like DROP TABLE proposal is observed
before execution, fail-closed by the DHMS gate before executor handoff, not
received by the inert mock executor, and recorded with zero SQL execution
attempts, zero DB connections, zero schema introspection, and zero result
readbacks.

## Explicit Non-Claims

v2.7.4.2 does not claim:

* production readiness
* real LangChain integration
* SQLDatabaseToolkit support
* real SQL Agent support
* real SQL execution support
* real DB protection
* schema introspection protection for real DBs
* model-provider integration
* credential safety
* user-data safety
* KerniQ integration
* E2B integration
* CLI support for the v2.7 proof
* parser support
* hook support
* schema support
* real execution authorization
* production runtime behavior
* protection against arbitrary real-world agents
* support for external databases
* support for real tool calls
* `python3 cli.py gate-proposal` support
* `examples/proposals/drop_table.json` support

## Files Changed

* `README.md`
* `docs/dhms_readme_public_landing_page_polish_v2_7_4_2.md`
* `docs/dhms_agentfuse_protocol_package_index_v0_7_0.md`
* `docs/dhms_agentfuse_development_roadmap.md`

## Files Intentionally Not Modified

* `docs/dhms_readme_current_status_sync_v2_7_4_1.md`
* `docs/dhms_pre_execution_fuse_loop_result_review_and_freeze_v2_7_4.md`
* `docs/development/screenshots/v2_7_3_pre_execution_interception_proof/v2_7_3_pre_execution_interception_proof_terminal.png`
* `validation/run_dhms_pre_execution_fuse_loop_proof_v0.py`
* `docs/dhms_pre_execution_interception_proof_v2_7_3.md`
* `dhms_agentfuse/pre_execution_gate.py`
* `dhms_agentfuse/inert_mock_executor.py`
* `validation/run_dhms_pre_execution_fuse_loop_runner_validation_v0.py`
* `docs/dhms_gate_runner_and_mock_executor_v2_7_2.md`
* `docs/dhms_proposal_gate_contract_and_fixtures_v2_7_1.md`
* `benchmarks/dhms_pre_execution_fuse_loop_v0/proposals.json`
* `docs/dhms_minimal_pre_execution_fuse_loop_planning_v2_7_0.md`
* `docs/dhms_pre_execution_fuse_roadmap_correction_v2_6_4_2.md`
* existing validators, fixtures, examples, source files, schemas, CLI files,
  dependency/package files, release docs, and frozen artifacts

No source files, proof scripts, runners, mock executors, fixtures, screenshots,
validators, CLI files, schemas, dependencies, releases, or tags were modified.

## Validation Commands

```bash
python3 validation/run_dhms_pre_execution_fuse_loop_proof_v0.py
python3 validation/run_dhms_pre_execution_fuse_loop_runner_validation_v0.py
python3 -m json.tool benchmarks/dhms_pre_execution_fuse_loop_v0/proposals.json >/dev/null
python3 validation/run_dhms_langchain_sql_agent_adapter_skeleton_shape_fixture_validation_v0.py
python3 validation/run_dhms_langchain_sql_agent_emit_only_adapter_fixture_validation_v0.py
python3 validation/run_dhms_third_party_sql_agent_threat_fixture_validation_v0.py
python3 validation/run_dhms_sql_agent_local_emit_only_fixture_validation_v0.py
python3 validation/run_dhms_bounded_local_mock_to_real_fixture_validation_v0.py
python3 validation/run_dhms_bounded_local_proposal_emitter_candidate_fixture_validation_v0.py
python3 -m json.tool benchmarks/dhms_langchain_sql_agent_adapter_skeleton_shape_v0/shape_fixtures.json >/dev/null
python3 -m json.tool benchmarks/dhms_langchain_sql_agent_emit_only_adapter_v0/adapter_boundary_fixtures.json >/dev/null
git diff --check
git diff --cached --check
```

## Targeted Scan Summary

Targeted scans should show only allowed hits: explicit non-claims, future
milestone labels, required proof marker text, runner validation marker
references, screenshot path references, prohibited-boundary references,
validation command text, inert dangerous-intent examples such as `DROP TABLE
customers`, `execution_authorized=false`, `mock_executor_received=false`, and
collapsed screenshot markdown.

No source code, proof behavior, runner behavior, fixtures, screenshot
artifacts, validators, CLI, schemas, dependencies, release, or tag changes are
part of v2.7.4.2.

## Acceptance Checklist

* [x] README opens with a clearer DHMS identity statement.
* [x] README prioritizes the current v2.7 proof.
* [x] README includes the current proof table.
* [x] README includes the proof command and expected proof output.
* [x] README includes screenshot evidence inside a collapsible details block.
* [x] README states the screenshot path.
* [x] README states the screenshot is not a gate-proposal CLI screenshot.
* [x] README compresses historical evidence lower on the page.
* [x] README keeps claims bounded to the v2.7.4 freeze.
* [x] No source, proof, runner, fixture, screenshot, validator, CLI, schema,
  dependency, release, or tag changes are included.

## Final Verdict

`READY_FOR_V2_8_0_CONTROLLED_AGENT_PROPOSAL_GATE_PLANNING`
