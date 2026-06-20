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

When `OPENCLAW_DHMS_COMMAND` is set, the wrapper parses it with `shlex.split` and runs it with `subprocess.run(..., shell=False)`. The OpenClaw process receives a JSON payload containing the original DHMS request plus a strict dry-run safety instruction.

If OpenClaw returns JSON, the wrapper extracts `final_answer`, `tool_calls`, `memory_reads`, `state_transitions`, `side_effects`, and `errors`. If OpenClaw returns plain text, the wrapper wraps it as safe DHMS trace evidence.

## Safety model

The wrapper is dry-run only.

It does not authorize real tool execution, production API calls, file mutation, emails, purchases, bookings, deletion, shell commands, or other external side effects.

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

## Required environment variable

`OPENCLAW_DHMS_COMMAND`

This must point to the local OpenClaw command the user wants to test manually.

## Optional environment variable

`OPENCLAW_DHMS_TIMEOUT_SECONDS`

Default: `60`

## Example setup

```bash
export OPENCLAW_DHMS_COMMAND='python3 /path/to/openclaw_cli.py --model deepseek-v4 --dry-run --no-tools'
```

Use placeholder paths until your local OpenClaw dry-run command is ready.

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

## Manual Phase 5 conformance command

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

## Caveats

* The real DeepSeek call happens only when the user manually configures and runs OpenClaw.
* DHMS does not authorize tool execution.
* The wrapper is dry-run only.
* This is not production certification.
* The user must ensure OpenClaw itself runs with no-tools / dry-run safeguards.
* DHMS cannot prevent a malicious local process from acting internally.
* Do not use production credentials or production tools in the first pilot.
