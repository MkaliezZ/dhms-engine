# OpenClaw Evaluation Wrapper Runtime Adaptation Review v0.5.4

## Purpose

v0.5.4 is a static adaptation review for the existing OpenClaw evaluation wrapper path. It documents how OpenClaw support could be adapted into the v0.5 execution runtime layer in a later phase.

This is not runtime integration. No OpenClaw runtime backend is implemented here, OpenClaw is not invoked, DeepSeek is not invoked, and no provider, agent SDK, HTTP adapter, production runner, SQL runtime path, or tool execution is added.

Start HEAD: `225a75f289db420e7094d1e0a44d315c99c977df`

## Files Inspected

- `examples/agents/openclaw_deepseek_v4_wrapper.py`
- `docs/openclaw_deepseek_v4_wrapper.md`
- `validation/run_openclaw_wrapper_extraction_validation.py`
- `docs/agent_harness_real_validation_log.md`
- `engine/agent_harness/command_agent_adapter.py`
- `engine/agent_harness/harness_runner.py`
- `engine/agent_harness/trace_schema.py`
- `engine/agent_harness/trace_normalizer.py`
- `engine/agent_harness/trace_report_enricher.py`
- `engine/agent_harness/agent_suite_runner.py`
- `engine/agent_harness/agent_suite_summary.py`
- `engine/agent_harness/agent_suite_report.py`
- `docs/agent_command_protocol_v1.md`
- `docs/agent_suite_runner_v1.md`
- `docs/execution_runtime_layer_plan_v0_5_0.md`
- `validation/execution_runtime_contract_stub.py`
- `validation/tool_call_interceptor_stub.py`
- `validation/sql_safety_runtime_mount_stub.py`

## Files Added or Modified

- Added `docs/openclaw_evaluation_wrapper_runtime_adaptation_review_v0_5_4.md`

No optional validation script was added. The review is static and documentation-only.

## Current OpenClaw Wrapper Role

The current OpenClaw path is an evaluation-layer, reporting-layer, and trace-extraction support path. `examples/agents/openclaw_deepseek_v4_wrapper.py` implements `dhms-agent-command-v1`, reads a DHMS JSON request from stdin, validates dry-run mode, validates an `OPENCLAW_DHMS_COMMAND` base command, may run OpenClaw with `subprocess.run(..., shell=False)`, captures stdout and stderr, normalizes observable output into DHMS trace evidence, and forces reported tool calls and side effects into blocked dry-run evidence.

The wrapper is valuable for controlled evidence collection and report generation, but it is not yet a runtime execution backend controlled by DHMS. In the current evaluation path, the wrapper can launch OpenClaw after wrapper-level checks. In the future runtime path, OpenClaw must sit behind a DHMS safety decision and must not execute before DHMS approval.

## Evaluation Wrapper vs Runtime Adapter

An evaluation wrapper observes, constrains, and normalizes outputs after or around an agent run. It is primarily used to produce reports, diagnostics, trace evidence, and deterministic validation logs.

A runtime adapter is different. It sits behind DHMS execution approval. It may only execute after a DHMS safety decision, must produce runtime-compatible traces before and after execution, and must not own execution policy.

The v0.5 runtime layer already separates these concerns:

- v0.5.1 defines runtime input requests, tool call proposals, safety decisions, execution decisions, and execution traces.
- v0.5.2 observes raw tool call proposals, normalizes them, classifies risk, and hands proposals to the runtime contract safety decision layer without executing tools.
- v0.5.3 mounts SQL Safety v0.4 into that runtime stub path and keeps SQL execution disabled from the runtime mount.

Future OpenClaw runtime adaptation should follow the same shape rather than reusing the current evaluation wrapper as an execution authority.

## Reusable Pieces

The following concepts from the current OpenClaw evaluation wrapper can be reused later:

- Command invocation boundary: the current wrapper treats `OPENCLAW_DHMS_COMMAND` as a base command and assembles argv with `shell=False`.
- stdout/stderr capture: the wrapper captures observable process output and stderr diagnostics.
- Diagnostic extraction: wrapper diagnostics record raw output presence, detected JSON shape, candidate text fields, truncation, and safe previews.
- Trace normalization concepts: OpenClaw JSON or plain text can be converted into DHMS trace-like evidence.
- Wrapper diagnostics: validation logs can distinguish wrapper failures, nonzero exits, timeouts, and normalization issues.
- Failure reporting: missing command, unsafe command, timeout, nonzero exit, invalid JSON, and incomplete trace shapes already have fail-safe report forms.
- Deterministic validation logs: `validation/run_openclaw_wrapper_extraction_validation.py` provides static local fixture checks for observable extraction, secret-like output rejection, and hidden reasoning avoidance.

These pieces are useful as adapter internals after DHMS approval, not as policy authority.

## Non-Reusable or Risky Pieces

The following must not be directly reused as runtime control:

- Direct agent invocation without a prior DHMS runtime safety decision.
- Any implicit provider or agent SDK ownership of execution policy.
- Any wrapper path that executes before a runtime `ALLOW` or approved `SANDBOX` decision.
- Any trace-only normalization logic mistaken for safety enforcement.
- Any output parsing treated as hidden reasoning inspection.
- Any command base that bypasses runtime interception, proposal classification, or trace IDs.
- Any provider invocation that is not explicitly authorized by the runtime decision.

The evaluation wrapper's dry-run blocking is evidence support; it is not a substitute for the v0.5 execution control contract.

## Runtime Adaptation Contract

A future OpenClaw runtime adapter should fit the v0.5 flow as follows:

1. Runtime input request is observed.
2. Raw OpenClaw tool call event is captured before execution.
3. v0.5 interceptor normalizes the proposal.
4. Proposal is classified as `OPENCLAW`.
5. Risk signals are attached, including external-effect risk and provider/backend invocation risk.
6. Runtime safety decision is made by DHMS.
7. Execution decision is derived from the safety decision.
8. OpenClaw runtime adapter may run only if the DHMS decision is `ALLOW` or a specific approved `SANDBOX`.
9. Adapter emits execution trace fields before and after execution.
10. Adapter captures post-execution observable result, stdout, stderr, exit code, and external mutation evidence where applicable.

DHMS owns the final execution decision. OpenClaw may be a backend only after approval; it must not own policy.

## Proposed Future Runtime Adapter Fields

A future OpenClaw runtime adapter should emit fields such as:

- `adapter_id`
- `request_id`
- `proposal_id`
- `decision_id`
- `adapter_type="OPENCLAW_RUNTIME_BACKEND"`
- `dhms_approved`
- `execution_allowed`
- `execution_started`
- `execution_completed`
- `stdout_captured`
- `stderr_captured`
- `exit_code`
- `external_mutation_detected`
- `provider_invoked`
- `agent_sdk_invoked`
- `black_box_validated`

These fields should supplement runtime-compatible traces without changing the current production output schema in this review phase.

## Required Fail-Closed Behavior

Future OpenClaw runtime adaptation must fail closed if:

- no DHMS decision exists
- the decision is `BLOCK`
- the decision is `REWRITE` but the rewrite has not completed
- the decision is `SANDBOX` but the sandbox boundary is missing
- the OpenClaw command is unknown
- command arguments are unsafe
- required trace IDs are missing
- provider or agent SDK invocation is not explicitly allowed
- external mutation cannot be observed
- stdout, stderr, or process output cannot be normalized
- adapter output cannot be mapped into runtime-compatible trace evidence

Fail-closed behavior means no backend execution occurs and the runtime trace records the blocked reason.

## No SDK / SDK-Agnostic Boundary

DHMS does not depend on OpenClaw as policy owner. OpenClaw may become an execution backend only after DHMS approval. DHMS remains the execution control plane.

No provider SDK, agent SDK, external service SDK, HTTP adapter, production runner integration, OpenClaw runtime integration, or DeepSeek invocation is added in v0.5.4.

## Black-Box Validation Boundary

Future OpenClaw runtime adaptation must preserve black-box validation:

- do not inspect hidden reasoning
- check only observable input
- check normalized proposal
- check DHMS decision
- check execution trace
- check stdout and stderr
- check exit code
- check external state where applicable

The existing evaluation wrapper already avoids depending on hidden chain-of-thought and preserves redacted observable response previews. Runtime adaptation should keep that boundary.

## Relationship to SQL Safety v0.4 and v0.5.3

SQL Safety v0.4 is already the first proven execution safety module. It completed dry-fire validation, temporary local SQLite SELECT-only target validation, mutation-block validation, and v0.4 freeze documentation.

v0.5.3 mounts SQL Safety v0.4 into the runtime stub path by routing intercepted SQL proposals to deterministic `BLOCK` or `SANDBOX` decisions while keeping runtime-path SQL execution disabled.

OpenClaw is not yet mounted as a runtime execution backend. v0.5.4 only prepares the static review needed before future runtime adaptation.

## Proposed Next Phase

Expected next phase:

`v0.5.5 First Runtime Dry-Run Loop`

That phase should combine:

- runtime input
- tool-call interception
- runtime safety decision
- SQL safety mount decision
- execution trace

It should still avoid real OpenClaw execution unless explicitly authorized in a later phase.

## Commands Run

- `python3 validation/run_execution_runtime_contract_stub.py`
- `python3 validation/run_tool_call_interceptor_stub.py`
- `python3 validation/run_sql_safety_runtime_mount_stub.py`
- `python3 validation/run_sql_safety_temp_sqlite_select_only_first_real_run.py`
- `python3 validation/run_sql_safety_temp_sqlite_mutation_block_test.py`
- `git diff --check`
- targeted grep checks
- import-only disallowed SDK/client scan
- secret scan

## Non-Execution Confirmation

No OpenClaw runtime integration was implemented. OpenClaw was not invoked. DeepSeek was not invoked. No provider SDK, agent SDK, external service SDK, HTTP adapter, production runner, SQL runtime execution, SQL sandbox execution from runtime path, real LLM Judge, real-provider test, full suite validation, or tool execution was added or run.

Production checker logic, production runner logic, schema, output schema, A/B/C taxonomy, SQL safety cases, and non-SQL cases were not modified.

## Final Verdict

READY_FOR_V0_5_5_FIRST_RUNTIME_DRY_RUN_LOOP
