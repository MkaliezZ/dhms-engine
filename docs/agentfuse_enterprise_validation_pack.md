# AgentFuse Enterprise Validation Pack

## Purpose

This guide helps an organization evaluate execution-boundary semantics on one
explicit guarded tool path. The core question is narrow: when a policy blocks
an agent action, can the tested path show both the decision and that execution
never started?

The validation keeps four facts separate:

- **decision:** what the policy allowed or blocked;
- **dispatch:** whether the host attempted to cross the execution boundary;
- **execution:** what happened after dispatch, when dispatch was allowed; and
- **evidence:** the safe record available for review.

Use synthetic inputs and an inert or controlled handler. This pack is a
technical validation guide for the experimental public beta. It describes only
the tested path and does not establish behavior outside that path.

## Validation Scenario 1 - Blocked Tool Call

Example request:

```text
delete_customer_record
```

Expected observations on the explicit guarded path:

```text
decision: block
dispatch: false
handler_invoked: false
side_effect: none
```

Here, `side_effect: none` means the tested guarded handler and its side-effect
path were not entered. It does not make a claim about unwrapped code or other
execution paths outside the integration boundary.

An illustrative safe receipt can be as small as:

```json
{
  "tool_call_id": "call-001",
  "decision": "block",
  "execution_status": "not_executed",
  "handler_invoked": false
}
```

The exact host receipt may use different field names. The invariant is that a
policy block is distinguishable from a tool failure after execution began.

## Validation Scenario 2 - Allowed Tool Call

Example request:

```text
read_customer_profile
```

Expected observations:

```text
decision: allow
dispatch: true
handler_invoked: true
execution_status: executed
```

The host runtime remains authoritative for these observations. An `allow`
decision permits host dispatch; it does not by itself prove that a handler
started or completed successfully.

## Validation Scenario 3 - Allowed Action Failed After Dispatch

After an `allow` decision, the host runtime may dispatch the action. That
action can still fail after crossing the execution boundary:

```text
decision: allow
dispatch: true
handler: failed
execution_status: execution_failed
```

This is not a policy denial. The host runtime owns the execution lifecycle and
final outcome. Keeping the policy decision and execution outcome separate lets
an operator distinguish a blocked action from a runtime, handler, or downstream
failure.

## Security / Architecture Review Questions

Use these questions when reviewing one guarded integration path:

- Can the tested path show that blocked actions never reached handler dispatch?
- Can it distinguish a policy denial from an execution failure?
- Does safe evidence avoid exposing sensitive tool arguments by default?
- Can multiple runtimes preserve the same decision, identity, and outcome
  semantics while retaining their own lifecycle behavior?
- Does the host retain authority over approval, retries, persistence, and the
  physical execution outcome?

## Relationship With the Existing Runtime

AgentFuse does not replace:

- runtime execution;
- tool handlers;
- retries; or
- application lifecycle management.

The host runtime remains authoritative for physical dispatch and execution
outcome. AgentFuse evaluates trusted tool-call requests before dispatch and
records the policy decision and associated non-execution evidence for guarded
paths.

## Suggested Validation Path

1. Start with the local [five-minute trial](agentfuse_five_minute_trial.md) or
   the real LangGraph [integration trial](dhms_agentfuse_five_minute_integration_trial_v3_7_1.md).
2. Select one synthetic or controlled tool call with a visible pre-dispatch
   boundary.
3. Run one blocked, one allowed, and one allowed-then-failed case.
4. Confirm that the tool-call identity, policy decision, dispatch observation,
   and execution outcome remain distinguishable in safe evidence.
5. Compare the result with the [consumer integration contract](dhms_agentfuse_consumer_integration_contract_v3_6_1.md)
   and [cross-adapter conformance kit](dhms_agentfuse_cross_adapter_conformance_v3_6_2.md).

For a bounded public-beta integration discussion, see the
[Early Validation Program](agentfuse_early_validation_program.md).
