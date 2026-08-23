# AgentFuse Design Partner Trial

## Purpose

This deterministic local trial gives agent framework maintainers, AI teams,
and prospective design partners a five-minute way to inspect AgentFuse's core
execution-assurance distinction. It runs one blocked call, one allowed call,
and one allowed call whose simulated handler fails.

The trial is part of the experimental public beta. It is not a production
deployment tool, a new runtime integration, or a security guarantee.

## What It Proves

On this explicit guarded path, the trial makes these lifecycle facts
observable:

- a blocked action has `decision=block` and `execution_status=not_executed`;
- the blocked handler is never invoked;
- an allowed action can cross the dispatch boundary and complete;
- an allowed action can also fail after dispatch; and
- policy denial remains distinct from runtime failure.

Each result preserves the original tool-call ID and tool name and contains the
existing AgentFuse structured evidence. The scenarios use only synthetic
values and local simulated handlers.

## Run

From the repository root:

```bash
python -m pip install -e .
python examples/design_partner_trial/run_trial.py
```

Expected final output:

```text
AgentFuse distinguishes:

policy denial
!=
runtime failure

AGENTFUSE_DESIGN_PARTNER_TRIAL_PASS
```

No API key, model, database, network service, or external runtime is required.

## Scenarios

The checked-in JSON files describe three synthetic requests:

- `blocked_tool_call.json`: `delete_customer_record` is blocked before dispatch;
- `allowed_tool_call.json`: `read_customer_profile` runs a simulated handler;
- `failed_execution.json`: `update_customer_note` is allowed, starts, and then
  fails inside the simulated handler.

The third case is intentionally an **allowed** action rather than an approval
claim. AgentFuse does not own the host application's approval workflow.

## Relationship to AgentFuse

AgentFuse evaluates a trusted tool-call request before dispatch. Its guarded
invocation path can show that a blocked handler was not entered and can produce
safe decision and non-execution evidence.

The host runtime remains authoritative for:

- physical dispatch;
- handler invocation outside this guarded example;
- retries and recovery; and
- the final physical execution outcome.

This trial uses `RuntimeGuard.invoke()` as a small local stand-in for that host
boundary. It does not replace the existing examples or integrations. For the
broader evaluation questions and limits, see the
[Enterprise Validation Pack](../../docs/agentfuse_enterprise_validation_pack.md).

## Tests

```bash
python -m pytest examples/design_partner_trial/tests -q
```
