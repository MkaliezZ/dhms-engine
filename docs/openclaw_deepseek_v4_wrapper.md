# OpenClaw + DeepSeek v4 DHMS Wrapper Template

## Purpose

`examples/agents/openclaw_deepseek_v4_wrapper.py` is a safe local command wrapper template for manually testing a locally deployed OpenClaw agent with DeepSeek v4 through DHMS Agent Harness.

It implements `dhms-agent-command-v1` and is compatible with `python3 cli.py check-agent-adapter`.

## How the wrapper works

The wrapper reads a DHMS JSON request from `stdin`:

```json
{
  "protocol_version": "dhms-agent-command-v1",
  "request": {
    "input_text": "hello",
    "mode": "B",
    "dry_run": true,
    "memory_condition": {},
    "context_condition": {},
    "tool_state_condition": {},
    "metadata": {}
  }
}
```

It writes one valid DHMS JSON response to `stdout` and sends any human-readable logs only to `stderr`.

When `OPENCLAW_DHMS_COMMAND` is set, the wrapper treats it as the base OpenClaw command. It parses the base command with `shlex.split`, appends the DHMS-generated prompt as `["--message", safe_prompt]`, and runs the final argv with `subprocess.run(..., shell=False)`.

Do not include `--message` in `OPENCLAW_DHMS_COMMAND`; the wrapper appends it safely.

If OpenClaw returns JSON, the wrapper extracts `final_answer`, `tool_calls`,
`memory_reads`, `state_transitions`, `side_effects`, and `errors`. If OpenClaw
returns plain text, the wrapper wraps it as safe DHMS trace evidence.

Phase 5.93 also preserves safe observable response text in
`observable_response` and `model_response_preview` when OpenClaw output includes
usable final response content. These fields are redacted/truncated previews for
semantic property checking. They must not contain secrets or hidden
chain-of-thought, and DHMS does not depend on chain-of-thought.

## Safety model

The wrapper is dry-run only.

It does not authorize real tool execution, production API calls, file mutation, emails, purchases, bookings, deletion, shell commands, or other external side effects.

Before execution, the wrapper rejects unsafe OpenClaw base commands containing options or subcommands such as `--deliver`, `--local`, `doctor --fix`, `exec-policy set`, `exec-policy preset`, `approvals set`, `sandbox recreate`, `plugins install`, or scheduled task commands.

The wrapper also fails closed unless `OPENCLAW_DHMS_COMMAND` includes `--profile dhms-pilot`. To permit an unprofiled command for local experimentation, set `OPENCLAW_DHMS_ALLOW_UNPROFILED=1`, but this is not recommended for the first pilot.

The wrapper requires exactly one safe OpenClaw target selector in the base command: `--agent`, `--session-key`, or `--session-id`. It rejects missing, ambiguous, or empty target selectors. Delivery-target routing such as `--to` is forbidden for the DHMS pilot.

Before emitting the DHMS trace, the wrapper forces every tool call and side effect to:

```json
{
  "executed": false,
  "blocked": true,
  "reason": "Blocked by DHMS OpenClaw wrapper dry-run policy."
}
```

If OpenClaw output claims `executed=true`, the wrapper blocks it and records a `claimed_executed_side_effect_blocked` error in the DHMS trace.

The wrapper also redacts suspicious secret-like content before embedding OpenClaw output previews into errors.

## Recommended OpenClaw command after discovery

```bash
export OPENCLAW_DHMS_COMMAND='/Users/macos/.npm-global/bin/openclaw --profile dhms-pilot agent --json --model deepseek/deepseek-v4-flash --agent main'
```

Notes:

* Do not include `--message`; the wrapper appends it safely.
* Do not include `--deliver`.
* Do not include `--local`.
* Do not include `--to`.
* Use `--profile dhms-pilot`.
* Use exactly one safe target selector. Current discovery confirmed `--agent main`.
* This may still call the real DeepSeek model when the user manually runs conformance without preflight mode.

Because OpenClaw exposes no explicit single-turn `--dry-run` / `--no-tools` flag in discovered help output, this pilot must be treated as a constrained real-model dry-run wrapper test, not a full no-tool security guarantee.

## Target selection after discovery

OpenClaw requires a target session or agent for `openclaw agent`. The DHMS wrapper base command must include one safe target selector:

* `--agent <id>`
* `--session-key <key>`
* `--session-id <id>`

Read-only discovery for the `dhms-pilot` profile confirmed:

* `openclaw agent --help` supports `--agent`, `--session-key`, and `--session-id`.
* `openclaw agents list --json` includes the default agent `main`.
* `openclaw sessions list --json` currently has no stored sessions.

Therefore the preferred target for the next single smoke is:

```bash
--agent main
```

Use agent/session selectors for the DHMS pilot, not delivery-target routing. The wrapper rejects `--to`, missing targets, ambiguous targets, and empty target selector values.

## Required environment variable

`OPENCLAW_DHMS_COMMAND`

This must point to the local OpenClaw command the user wants to test manually.

## Optional environment variable

`OPENCLAW_DHMS_TIMEOUT_SECONDS`

Default: `8`

`OPENCLAW_DHMS_PREFLIGHT_ONLY`

Set to `1` to run static wrapper checks without launching OpenClaw or calling DeepSeek.

`OPENCLAW_DHMS_ALLOW_UNPROFILED`

Set to `1` only if you intentionally want to bypass the default `--profile dhms-pilot` requirement.

## Example setup

```bash
export OPENCLAW_DHMS_COMMAND='/Users/macos/.npm-global/bin/openclaw --profile dhms-pilot agent --json --model deepseek/deepseek-v4-flash --agent main'
```

Use a dedicated pilot profile and avoid production credentials or production tools.

## Safe local validation without running OpenClaw

Do not set `OPENCLAW_DHMS_COMMAND` for this check:

```bash
printf '{"protocol_version":"dhms-agent-command-v1","request":{"input_text":"hello","mode":"B","dry_run":true,"memory_condition":{},"context_condition":{},"tool_state_condition":{},"metadata":{}}}' | python3 examples/agents/openclaw_deepseek_v4_wrapper.py
```

Expected:

* valid DHMS JSON
* `missing_openclaw_command` error
* `dry_run=true`
* no `executed=true`


## Timeout and Liveness Pattern

Real OpenClaw model calls can exceed the default adapter probe timeout. Keep the wrapper timeout shorter than the parent conformance timeout so the wrapper can return structured DHMS JSON instead of being killed by the parent process.

Recommended pattern for a real OpenClaw conformance retry:

```bash
OPENCLAW_DHMS_TIMEOUT_SECONDS=<N> \
OPENCLAW_DHMS_COMMAND='/Users/macos/.npm-global/bin/openclaw --profile dhms-pilot agent --json --model deepseek/deepseek-v4-flash --agent main' \
python3 cli.py check-agent-adapter \
  --agent-command "python3 examples/agents/openclaw_deepseek_v4_wrapper.py" \
  --timeout-seconds <N+delta> \
  --report \
  --output reports/adapter_conformance/openclaw_deepseek_v4
```

Use a small delta that is long enough for wrapper cleanup and JSON emission. Never put tokens, passwords, or API keys inside `OPENCLAW_DHMS_COMMAND`. Do not run `test-agent-suite` until adapter conformance passes.

On wrapper-level timeout, the wrapper returns `protocol_version=dhms-agent-command-v1`, `trace.adapter_name=openclaw_deepseek_v4`, `trace.dry_run=true`, empty `tool_calls` / `side_effects`, and a safe `openclaw_timeout` error with redacted diagnostics.

## Manual Phase 5 conformance command

First run static preflight:

```bash
export OPENCLAW_DHMS_PREFLIGHT_ONLY=1
python3 cli.py check-agent-adapter \
  --agent-command "python3 examples/agents/openclaw_deepseek_v4_wrapper.py" \
  --report \
  --output reports/adapter_conformance/openclaw_deepseek_v4_preflight
```

Then, only if the user accepts real model-call risk:

```bash
unset OPENCLAW_DHMS_PREFLIGHT_ONLY
```

```bash
python3 cli.py check-agent-adapter \
  --agent-command "python3 examples/agents/openclaw_deepseek_v4_wrapper.py" \
  --report \
  --output reports/adapter_conformance/openclaw_deepseek_v4
```

If `OPENCLAW_DHMS_COMMAND` is not set, this should fail safely and still generate JSON / Markdown / static HTML conformance reports.

## Manual suite command

```bash
python3 cli.py test-agent-suite \
  --suite cases/agent_core \
  --agent-command "python3 examples/agents/openclaw_deepseek_v4_wrapper.py" \
  --n 3 \
  --report \
  --output reports/openclaw_deepseek_v4/agent_core_n3
```

Run this only after local OpenClaw dry-run behavior has passed adapter conformance.

## Optional read-only human checks

The user may manually inspect local OpenClaw safety state before a real pilot:

```bash
/Users/macos/.npm-global/bin/openclaw --profile dhms-pilot exec-policy show
/Users/macos/.npm-global/bin/openclaw --profile dhms-pilot sandbox explain
```

Do not run `exec-policy set`, `exec-policy preset`, `doctor --fix`, or `sandbox recreate` as part of this wrapper pilot.

## Caveats

* The real DeepSeek call happens only when the user manually configures and runs OpenClaw.
* DHMS does not authorize tool execution.
* The wrapper is dry-run only.
* This is not production certification.
* The user must ensure OpenClaw itself runs with no-tools / dry-run safeguards.
* The discovered OpenClaw CLI did not expose explicit single-turn `--dry-run`, `--no-tools`, `--no-shell`, `--no-exec`, or `--no-deliver` flags.
* DHMS cannot prevent a malicious local process from acting internally.
* Do not use production credentials or production tools in the first pilot.

## Limited Agent Suite Pattern

After adapter conformance passes, use a bounded suite run before any broad evaluation:

```bash
OPENCLAW_DHMS_TIMEOUT_SECONDS=45 \
OPENCLAW_DHMS_COMMAND='/Users/macos/.npm-global/bin/openclaw --profile dhms-pilot agent --json --model deepseek/deepseek-v4-flash --agent main' \
python3 cli.py test-agent-suite \
  --suite cases/agent_core \
  --agent-command "python3 examples/agents/openclaw_deepseek_v4_wrapper.py" \
  --n 1 \
  --max-cases 1 \
  --case-timeout-seconds 60 \
  --report \
  --output reports/agent_suite/openclaw_deepseek_v4_limited_phase59
```

Keep `--max-cases` small for the first real-agent gate, and never include tokens or passwords in `OPENCLAW_DHMS_COMMAND`.

## Real Validation Evidence

Post-preview real OpenClaw + DeepSeek validation evidence is recorded in
[Agent Harness Real Validation Log](agent_harness_real_validation_log.md). The
preview tag remains frozen; that log is branch evidence only.

The Phase 5.92 two-case limited real suite recorded
`openclaw_output_wrapped` notices for both selected cases. Those notices mean
the wrapper normalized OpenClaw output into DHMS trace evidence; they are not
execution-safety failures when required safety fields are preserved and no tool
or side effect is executed.

Phase 5.93 adds observable response preservation so future limited runs can
reduce `expected_property_check=unknown` when OpenClaw provides safe visible
response text. This does not enable real tools, real OpenClaw turns by itself,
or any external LLM Judge.

Phase 5.94 ran one real semantic probe for `delete_account_guard`. Execution
safety passed, but the semantic result stayed `unknown` because OpenClaw output
was normalized to a generic final answer without preserved
`observable_response` / `model_response_preview`. This is not a safety failure
and not a production certification.

## Phase 5.94R Extraction Notes

`openclaw_output_wrapped` is emitted when the wrapper cannot see a complete DHMS
trace shape from OpenClaw output. Phase 5.94 reports included the wrapper's
DHMS JSON stdout preview, but not the original OpenClaw stdout shape, so a
future exactly-one real extraction probe is needed to confirm the live envelope.

Local fixtures now validate extraction from sanitized fake shapes:

* top-level `final_answer`
* nested `trace`
* nested `result` / `response` / `output` / `data`
* string `message`
* `message.content`
* `choices[0].message.content`

The wrapper still rejects secret-like output before preserving previews and
does not use hidden reasoning or chain-of-thought fields.

## Phase 5.95R Raw Output Diagnostics

The wrapper now emits `wrapper_diagnostics` when it has to normalize OpenClaw
output instead of accepting a complete DHMS trace. These diagnostics are
pre-normalization facts for debugging the OpenClaw envelope shape. They do not
affect pass/fail, safety veto, trace validation, or semantic recommendations.

Fields:

* `diagnostics_version`
* `raw_stdout_present`
* `raw_stderr_present`
* `raw_stdout_preview`
* `raw_stderr_preview`
* `detected_json_shape`
* `normalization_reason`
* `candidate_text_fields_found`

Safety rules:

* stdout/stderr previews are truncated
* secret-like content is replaced with a redacted placeholder
* hidden reasoning / chain-of-thought fields are omitted from parseable JSON
  previews
* candidate text detection records field paths only
* diagnostics are local evidence for the next single-case probe, not proof that
  real semantic extraction is fixed

## Phase 5.97 Payload Text Extraction

Phase 5.96 identified the live OpenClaw visible text candidate path
`result.payloads[0].text`. Phase 5.97 adds a narrow local extraction fix for
visible payload fields:

* `payload.text`
* `payload.content`
* string `payload.message`
* `payload.message.content`

The extraction result is still redacted/truncated through the wrapper's safe
message path. Hidden reasoning / chain-of-thought fields are ignored, dry-run
safety behavior is unchanged, and extraction does not affect execution-safety
pass/fail. Real OpenClaw confirmation remains a future exactly-one probe.
