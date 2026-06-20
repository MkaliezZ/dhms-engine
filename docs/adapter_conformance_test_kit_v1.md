# Adapter Conformance Test Kit v1

## Purpose

The Adapter Conformance Test Kit checks whether a local BYOA command-agent wrapper is protocol-safe and ready to use with DHMS Agent Harness suite tests.

It is intended to run before full reliability or case-suite evaluation.

## What Conformance Means

Conformance means the local wrapper can launch, read a DHMS stdin JSON request, return valid `dhms-agent-command-v1` JSON on stdout, include a valid trace object, preserve dry-run safety, and generate JSON / Markdown / static HTML conformance reports.

## What Conformance Does Not Mean

Conformance is not production certification. It does not prove real-agent reliability, grant tool execution permission, certify safety in production, or test remote / HTTP agents.

## Command

```bash
python3 cli.py check-agent-adapter \
  --agent-command "python3 examples/agents/sample_json_agent.py" \
  --report \
  --output reports/adapter_conformance/sample_json_agent
```

## Local Command Wrapper Expectations

* Read one JSON object from stdin.
* Return one JSON object to stdout.
* Use `protocol_version = "dhms-agent-command-v1"`.
* Return a top-level `trace` object.
* Include required AgentTrace fields.
* Set `dry_run=true`.
* Treat tool calls as trace evidence only.
* Record side effects as blocked trace evidence.
* Never mark side effects as `executed=true`.
* Keep stderr free of secrets.
* Return before the configured timeout.

## Conformance Checks

The test kit checks:

* process launch
* valid stdout JSON
* protocol version
* trace presence
* required trace fields
* `dry_run=true`
* no executed side effects
* attempted side effects are blocked
* tool calls are not executed
* stderr secret safety
* timeout enforcement
* JSON / Markdown / HTML reportability

## Readiness Score

The readiness score starts at 100 and subtracts penalties for failed checks:

* Critical fail: -40
* High fail: -25
* Medium fail: -10
* Low fail: -5

Scores are clamped to 0-100.

## PASS / WARN / FAIL

* `PASS`: required checks passed and the adapter is suite-ready.
* `WARN`: no blocking failures, but medium/low caveats should be reviewed.
* `FAIL`: one or more blocking failures must be fixed before suite testing.

## Blocking Failures

Blocking failures include:

* invalid JSON
* wrong protocol
* missing trace
* missing required trace fields
* `dry_run=false`
* executed side effect
* timeout
* nonzero exit with no valid trace


## Timeout Diagnostics

`check-agent-adapter` accepts `--timeout-seconds` and the alias `--case-timeout-seconds` for the parent probe timeout. Reports include timeout diagnostics for failed probes: case id, timeout source, timeout seconds, duration when available, and redacted stdout/stderr previews.

For wrappers that call real local agents, prefer wrapper-level timeout first and parent timeout second. For example, set `OPENCLAW_DHMS_TIMEOUT_SECONDS=N` in the wrapper environment and run `check-agent-adapter --timeout-seconds N+delta`. This lets the wrapper return structured DHMS JSON with `tool_calls=[]`, `side_effects=[]`, and no `executed=true` if the real agent is slow.

Never put tokens, passwords, or API keys in `--agent-command` or wrapper environment command strings. Do not run suite tests until conformance passes.

## Reports

With `--report`, the command writes:

* `adapter_conformance_report.json`
* `adapter_conformance_report.md`
* `adapter_conformance_report.html`

JSON is for machine review, Markdown is for GitHub review, and static HTML is for demos, screenshots, and non-technical inspection.

## Good Adapter Example

```bash
python3 cli.py check-agent-adapter \
  --agent-command "python3 examples/agents/sample_json_agent.py" \
  --report \
  --output reports/adapter_conformance/sample_json_agent
```

## Bad-Agent Examples

```bash
python3 cli.py check-agent-adapter --agent-command "python3 examples/agents/bad_invalid_json_agent.py" --report --output reports/adapter_conformance/bad_invalid_json
python3 cli.py check-agent-adapter --agent-command "python3 examples/agents/bad_wrong_protocol_agent.py" --report --output reports/adapter_conformance/bad_wrong_protocol
python3 cli.py check-agent-adapter --agent-command "python3 examples/agents/bad_dry_run_false_agent.py" --report --output reports/adapter_conformance/bad_dry_run_false
python3 cli.py check-agent-adapter --agent-command "python3 examples/agents/bad_executed_side_effect_agent.py" --report --output reports/adapter_conformance/bad_executed_side_effect
python3 cli.py check-agent-adapter --agent-command "python3 examples/agents/bad_missing_trace_agent.py" --report --output reports/adapter_conformance/bad_missing_trace
python3 cli.py check-agent-adapter --agent-command "python3 examples/agents/bad_timeout_agent.py" --timeout-seconds 1 --report --output reports/adapter_conformance/bad_timeout
```

These samples intentionally demonstrate safe failure handling.

## Caveats

* dry-run only
* local BYOA command only
* no production certification
* HTTP adapter not implemented
* DHMS cannot stop malicious user-owned process internals
* users should run dry-run / sandbox wrappers during testing
