# Denial Lifecycle Regression Fixtures

These provider-neutral fixtures cover denied agent tool-call lifecycles. They
help catch bugs where a denied request has no terminal result, is reported as
an execution failure, aborts a separate allowed request, loses its original
tool-call identity, or leaks protected input into trace output.

## Protected Invariants

* Policy decision and execution outcome are separate facts.
* `block` does not mean execution failure.
* A denied handler never starts.
* Every requested call has exactly one terminal record.
* The original `tool_call_id` and `tool_name` remain bound to that record.
* An allowed call can continue after a denied call in the same batch.
* Default trace metadata remains sanitized.

## Reuse

Copy `fixtures.json`, translate its expectations into your own test framework,
and compare the terminal lifecycle output from your runtime. Importing
AgentFuse is not required to copy these assertions. Installing AgentFuse is
only needed to run the bundled Python demo and tests.

The JSON is canonical for this fixture pack's expected outputs. It is
illustrative for external frameworks, not a protocol or interoperability
standard.

## Reference Demo

```bash
python examples/trial/per_call_denial_lifecycle_demo.py
```

Expected verdict:

```text
AGENTFUSE_PER_CALL_DENIAL_TRIAL_DEMO_PASS
```

## Boundaries

These fixtures do not provide production runtime enforcement, provider or
model integration, SQL/network/filesystem execution, an MCP gateway, a policy
evaluator, a security or compliance guarantee, or a universal transcript
standard.
