# DHMS AgentFuse Public Decision API v3.5.1

## Purpose

`RuntimeGuard.evaluate()` and `RuntimeGuard.aevaluate()` expose AgentFuse's
canonical pre-dispatch policy decision to runtimes that own their own approval,
dispatch, and physical-outcome lifecycle.

## Contract

Both methods return an immutable `RuntimeGuardDecision` containing:

- the original tool-call ID and tool name
- an `allow` or `block` action
- the canonical reason code and policy ID
- the canonical `AgentFuseEvidenceRecord`

They accept no handler, perform no dispatch, and cannot execute the protected
payload.

```python
from dhms_agentfuse import RuntimeGuard, ToolCallRequest

guard = RuntimeGuard(allow_tools={"read_file"})
decision = guard.evaluate(
    ToolCallRequest(
        tool_call_id="call-001",
        tool_name="read_file",
        arguments={"path": "synthetic-example.txt"},
    )
)
```

Use `aevaluate()` for an async policy. Passing an async-only policy to the
synchronous `evaluate()` API fails closed with
`reason_code="invalid_policy_decision"`.

## Relationship to Invocation

`invoke()` and `ainvoke()` call the same public decision path:

```text
resolve policy once
→ create RuntimeGuardDecision and canonical evidence
→ block, or dispatch only when the decision allows
```

Policy exceptions and invalid policy results fail closed. Argument values stay
out of safe decision serialization; only their stable digest is included in
canonical evidence.
