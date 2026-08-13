# Hermes #53021 Proof Receipt Fields

The proof emits only safe receipt data produced by AgentFuse. The important
fields are the decision, outcome, handler-start state, policy identity, reason
code, and canonical arguments digest.

The original command string is intentionally not copied into the receipt.

For a blocked call the expected invariant is:

```text
decision=block
outcome=not_executed
dispatch_occurred=false
handler_started=false
side_effect_occurred=false
```

The exact same blocked action, when re-evaluated with a new call id, keeps the
same arguments digest and remains blocked.
