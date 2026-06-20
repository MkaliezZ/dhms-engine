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

If OpenClaw returns JSON, the wrapper extracts `final_answer`, `tool_calls`, `memory_reads`, `state_transitions`, `side_effects`, and `errors`. If OpenClaw returns plain text, the wrapper wraps it as safe DHMS trace evidence.

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

Default: `60`

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
