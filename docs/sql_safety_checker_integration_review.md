# SQL Safety Checker Integration Review

## Purpose

This document records v0.4.1G SQL Safety Checker Integration Review.

The purpose is to review the existing Agent Harness checker, validator, runner,
taxonomy, schema, and report contracts before any production SQL safety checker
integration. This phase compares the current contracts against the v0.4.1F SQL
safety checker integration preview shape.

This is review-only. It does not implement production checker integration.

## Start HEAD

`b3e6095903d15f516c4b7cf1ca37ebcb077a3570`

## Files Inspected

Core checker and execution-safety files:

* `engine/agent_harness/agent_expected_property_checker.py`
* `engine/agent_harness/harness_runner.py`
* `engine/agent_harness/trace_schema.py`
* `engine/agent_harness/trace_normalizer.py`
* `engine/agent_harness/trace_report_enricher.py`
* `engine/agent_harness/command_agent_adapter.py`

Suite runner, taxonomy, and report files:

* `engine/agent_harness/agent_suite_runner.py`
* `engine/agent_harness/agent_suite_summary.py`
* `engine/agent_harness/agent_suite_report.py`
* `cli.py`

Protocol and runner documentation:

* `docs/agent_command_protocol_v1.md`
* `docs/agent_suite_runner_v1.md`

SQL safety fixture and preview files:

* `cases/sql_safety/sql_delete_without_authorization.txt`
* `cases/sql_safety/sql_dry_run_claim_completed.txt`
* `cases/sql_safety/sql_injection_tool_call_guard.txt`
* `cases/sql_safety/sql_update_from_stale_memory.txt`
* `cases/sql_safety/sql_rag_identity_conflict.txt`
* `cases/sql_safety/sql_select_sensitive_data_leakage.txt`
* `cases/sql_safety/sql_conflicting_instruction_update.txt`
* `validation/run_sql_safety_mock_local_validation.py`
* `validation/run_sql_safety_checker_integration_preview.py`
* `docs/sql_safety_mock_local_validation_log.md`
* `docs/sql_safety_checker_integration_preview_log.md`

## Current Checker Input Contract Summary

`engine/agent_harness/agent_expected_property_checker.py` exposes
`check_agent_expected_property(input_text, traces, expected_agent_property,
expected_constraints, judge_mode, execution_safety_result)`.

The current deterministic checker input contract is:

* plain input text
* normalized AgentTrace dictionaries
* optional `expected_agent_property`
* optional parsed `expected_constraints`
* local `judge_mode`
* `execution_safety_result`

The checker does not call an external LLM Judge by default. It uses local
deterministic rules and returns `unknown` when evidence is insufficient.

## Current Checker Output Contract Summary

The checker returns `semantic_property_result` dictionaries with:

* `property_check_version`
* `judge_mode`
* `overall`
* `passed`
* `safety_veto`
* `confidence`
* `constraints`
* `observable_evidence`
* `unknown_reason`
* `evidence`
* `notes`

`judge_result` is a compatibility alias for `semantic_property_result` in
reports. This does not imply that a real LLM Judge was called.

Execution safety is separate. `build_execution_safety_result` returns:

* `overall`
* `safety_veto`
* `violations`
* `dry_run_all_traces`
* `tool_executed_count`
* `side_effect_executed_count`
* command / trace validation signals

Execution safety vetoes semantic success. A semantic checker result cannot
override `dry_run=false`, executed tools, executed side effects, command
failures, trace validation failures, or secret leakage.

## Current Case Loading And Taxonomy Path Summary

`engine/agent_harness/agent_suite_runner.py` loads `.txt` cases and parses a
fixed field set:

* `title`
* `scenario`
* `user_input`
* `memory_context`
* `context`
* `tool_state`
* `expected_agent_property`
* `expected_constraints`
* `risk_focus`

Current SQL fixtures include additional useful fields such as `case_id`,
`domain`, `user_request`, and `retrieved_context`, but those fields are not
part of the current Agent Suite Runner parser field set.

Taxonomy is currently inferred through `infer_perturbation_mode` plus explicit
case-id sets for existing memory/context and context-coordination cases. It
supports A/B/C as existing domains, but SQL case ids are not yet mapped in the
runner.

Important compatibility note: running `cases/sql_safety/` through the production
suite runner today would not preserve all SQL fixture fields and could infer
taxonomy incorrectly for at least the C-domain SQL case. Therefore v0.4.1H
should not route SQL safety fixtures through `test-agent-suite` as its first
integration step.

## Current Schema And Report Contract Summary

`engine/agent_harness/trace_schema.py` defines the current AgentTrace shape:

* `final_answer`
* `tool_calls`
* `memory_reads`
* `state_transitions`
* `side_effects`
* `errors`
* `adapter_name`
* `dry_run`
* `mode`
* `input_preserved`
* `trace_version`

The current command protocol in `docs/agent_command_protocol_v1.md` is stdin /
stdout JSON with a `trace` object matching AgentTrace. It requires dry-run and
forbids executed side effects.

The current suite execution summary schema includes:

* `schema_version`
* `run_metadata`
* `suite_summary`
* `taxonomy_summary`
* `consistency_summary`
* `cases`

Each execution-summary case includes `case_id`, `taxonomy_domain`,
`taxonomy_label`, `execution_safety_result`, `semantic_property_result`, and
`final_status`.

SQL-specific fields such as `database_connected`, `sql_executed`,
`proposed_sql`, `blocked_sql`, and `dry_run_sql_log` are not part of the current
production AgentTrace or execution-summary schema.

## Comparison With v0.4.1F Preview Input Shape

The v0.4.1F preview input shape is:

* `case_id`
* `domain`
* `source_path`
* `mode`
* `user_request`
* `memory_context`
* `retrieved_context`
* `expected_boundary`
* `expected_decision`
* `fixture_execution_signals`

Compatibility assessment:

* `case_id`, `domain`, `source_path`, and preview `mode` are validation-layer
  metadata and can remain outside production schema.
* `user_request` can map to existing `user_input` if needed, but current SQL
  fixtures use both names and the suite runner only parses `user_input`.
* `memory_context` is already parsed by the suite runner.
* `retrieved_context` is not parsed by the suite runner today.
* `expected_boundary` and `expected_decision` are useful SQL adapter metadata
  but should not be added to production schema in v0.4.1H.
* `fixture_execution_signals` belongs in validation output, not AgentTrace.

The preview input shape is compatible with a separate SQL validation adapter.
It is not directly compatible with the production suite runner without either
field parser changes or a separate SQL fixture parser.

## Comparison With v0.4.1F Preview Result Shape

The v0.4.1F preview result shape is:

* `case_id`
* `domain`
* `should_block`
* `preview_decision`
* `expected_boundary`
* `expected_decision`
* `executed`
* `tool_call_count`
* `tool_executed_count`
* `side_effect_executed_count`
* `external_mutation_detected`
* `database_connected`
* `sql_executed`
* `safe_redaction_applied`
* `observable_preview`

Compatibility assessment:

* `executed=false`, `tool_call_count=0`, `tool_executed_count=0`, and
  `side_effect_executed_count=0` align with existing execution-safety concepts.
* `should_block=true` aligns with existing blocked side-effect and blocked tool
  semantics, but it is not currently a top-level production result field.
* `database_connected=false` and `sql_executed=false` are SQL-specific
  non-execution fields. They should remain validation-layer fields in v0.4.1H.
* `external_mutation_detected=false` aligns conceptually with no side effects,
  but is not a current AgentTrace field.
* `safe_redaction_applied` is only relevant to sensitive SELECT preview and
  should stay SQL validation metadata.
* `observable_preview` can map to existing observable response text if SQL
  target outputs are later run through the command adapter.

The preview result shape is compatible with existing safety semantics if SQL
non-execution fields are kept in a SQL validation adapter result, not forced
into AgentTrace or execution-summary schema.

## Compatibility Assessment

SQL safety can be integrated without changing output schema if v0.4.1H uses a
separate SQL safety checker adapter / validation entry point that:

* parses `cases/sql_safety/*.txt` directly,
* reuses v0.4.1E fixture validation,
* reuses v0.4.1F preview result semantics,
* emits a SQL-specific validation report,
* keeps SQL-specific fields inside validation-layer output only.

SQL safety can be integrated without changing A/B/C taxonomy if v0.4.1H keeps
the explicit SQL case mapping from v0.4.1E and v0.4.1F. It should not rely on
generic `infer_perturbation_mode` for SQL fixtures yet.

The current checker supports blocked/not-executed semantics through:

* `execution_safety_result`
* `tool_calls[].executed=false`
* `tool_calls[].blocked=true`
* `side_effects[].executed` checks
* `side_effects[].blocked=true`
* `dry_run_all_traces`
* safety veto handling

The current checker does not yet have SQL-specific semantic rules for
`database_connected=false`, `sql_executed=false`, `proposed_sql`, `blocked_sql`,
or `dry_run_sql_log`.

## Integration Risks

1. Direct suite-runner integration could lose SQL-specific fields.
   `retrieved_context`, `domain`, `user_request`, `expected_boundary`, and
   `expected_decision` are not in the current runner parser field set.

2. Direct suite-runner integration could misclassify SQL taxonomy.
   Existing runner taxonomy uses generic inference and explicit non-SQL case-id
   sets. SQL C-domain mapping should not depend on generic text inference.

3. Adding SQL fields to AgentTrace would be a schema change.
   v0.4.1H should avoid adding `database_connected`, `sql_executed`,
   `proposed_sql`, `blocked_sql`, or `dry_run_sql_log` to the production trace
   schema.

4. Folding SQL semantic rules directly into
   `agent_expected_property_checker.py` in v0.4.1H would broaden production
   checker semantics earlier than needed.

5. Sensitive SELECT handling needs a clear redaction boundary.
   The preview supports `block_or_redact_no_leakage`; production integration
   should avoid treating redaction as a real query or fetched data.

6. SQL target output must remain non-execution-only.
   Any future target or adapter must fail if it observes `executed=true`,
   `sql_executed=true`, `database_connected=true`, or external mutation.

## Recommended Minimal Integration Path For v0.4.1H

Recommended path: keep SQL safety as a separate validation entry point for the
next phase.

v0.4.1H should add a minimal SQL safety checker adapter under `validation/`
rather than modifying production Agent Harness checker logic. The adapter should:

1. call `validation/run_sql_safety_mock_local_validation.py`;
2. call or reuse `validation/run_sql_safety_checker_integration_preview.py`;
3. preserve the exact 7-case SQL fixture set;
4. parse SQL fixture fields using a SQL-specific parser;
5. produce deterministic SQL safety adapter results;
6. enforce fail-closed non-execution fields:
   * `should_block=true`
   * `executed=false`
   * `tool_call_count=0`
   * `tool_executed_count=0`
   * `side_effect_executed_count=0`
   * `external_mutation_detected=false`
   * `database_connected=false`
   * `sql_executed=false`
7. emit a SQL-specific JSON / Markdown validation output if useful;
8. avoid modifying `agent_expected_property_checker.py`,
   `agent_suite_runner.py`, `trace_schema.py`, and CLI production suite
   behavior in v0.4.1H.

Only after that adapter is reviewed should a later phase consider production
suite integration.

## Likely Files For v0.4.1H

Likely safe files to add or modify:

* `validation/run_sql_safety_minimal_checker_adapter.py` or equivalent
* optional `docs/sql_safety_minimal_checker_adapter_log.md`

Files that should remain unchanged in v0.4.1H unless the task explicitly
broadens scope:

* `engine/agent_harness/agent_expected_property_checker.py`
* `engine/agent_harness/agent_suite_runner.py`
* `engine/agent_harness/trace_schema.py`
* `cli.py`
* `cases/agent_core/*`
* `cases/sql_safety/*.txt`

## Review Questions Answered

What files will likely need modification in v0.4.1H?

* Prefer adding a new validation-layer SQL safety adapter script and a matching
  log document. Avoid production checker / runner changes in v0.4.1H.

Can SQL safety be integrated without changing output schema?

* Yes, if SQL-specific fields remain in validation-layer outputs and are not
  added to AgentTrace or execution summary schema.

Can SQL safety be integrated without changing A/B/C taxonomy?

* Yes, if the SQL adapter uses explicit case-id to A/B/C mapping already proven
  by v0.4.1E and v0.4.1F.

Does the current checker support blocked/not-executed semantics?

* Yes for generic dry-run, tool execution, and side-effect execution safety.
  It does not yet support SQL-specific database connection or SQL execution
  fields as production semantics.

Does the current checker support per-case safety signals?

* Yes through `expected_constraints`, case metadata, observable text,
  execution-safety results, and deterministic rule functions. SQL-specific
  per-case signals should remain in a separate SQL adapter first.

Where should SQL safety fixture validation be called from, if at all?

* In v0.4.1H, call it from the SQL-specific validation adapter as a preflight
  gate, not from the production suite runner.

Should v0.4.1H integrate the preview script into an existing validation path, or
keep it as a separate SQL safety validation entry point?

* Keep it as a separate SQL safety validation entry point. This preserves the
  non-invasive boundary and avoids schema/taxonomy drift.

What is the safest minimal integration path?

* Add a validation-layer SQL safety checker adapter that composes v0.4.1E and
  v0.4.1F, emits deterministic adapter results, and fails closed on any real SQL
  execution, database connection, provider call, tool execution, or external
  mutation signal.

## Fields That Must Remain Non-execution-only

These fields must remain non-execution-only in v0.4.1H:

* `should_block=true`
* `executed=false`
* `tool_call_count=0`
* `tool_executed_count=0`
* `side_effect_executed_count=0`
* `external_mutation_detected=false`
* `database_connected=false`
* `sql_executed=false`
* `proposed_sql`
* `blocked_sql`
* `dry_run_sql_log`
* `observable_preview`

`proposed_sql`, `blocked_sql`, and `dry_run_sql_log` should remain trace
evidence only. They must not imply that SQL was run or that a database was
connected.

## Non-execution Confirmation

No SQL/database/provider execution occurred in v0.4.1G:

* no real SQL execution
* no database connection
* no database credentials
* no external mutation
* no OpenClaw run
* no DeepSeek call
* no real-provider test
* no real LLM Judge
* no full suite validation

## Validation Commands

Allowed local validation commands:

```bash
python3 validation/run_sql_safety_mock_local_validation.py
python3 validation/run_sql_safety_checker_integration_preview.py
git diff --check
```

Targeted grep checks and a simple secret scan should be run over this review
document.

## Final Verdict

`READY_FOR_V0_4_1H_SQL_SAFETY_MINIMAL_CHECKER_ADAPTER`
