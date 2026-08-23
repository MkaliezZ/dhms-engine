# AgentFuse Execution Assurance Model

## Purpose

AgentFuse is a runtime execution assurance layer for AI agents. It evaluates a
trusted tool-call request before dispatch, preserves the original tool-call
identity, and produces structured evidence about the decision and the guarded
execution boundary.

The central question is:

> Did this action cross the runtime execution boundary?

AgentFuse applies only to tool paths that pass through an explicit integration
point, such as a pre-tool hook, middleware boundary, decision API, or guarded
invocation. It does not make claims about unguarded code or execution paths
outside that boundary.

## Responsibility Boundary

### AgentFuse is

- a pre-dispatch `allow` or `block` decision point for trusted requests;
- an enforcement boundary for handlers invoked through its guarded APIs;
- a way to preserve tool-call identity across a policy decision;
- a source of structured decision and non-execution evidence; and
- an integration surface that keeps policy decisions separate from runtime
  outcomes.

### AgentFuse is not

- an authority or delegation system;
- an identity provider or identity registry;
- an approval workflow, review queue, or resume coordinator;
- an operating-system, process, container, filesystem, or network sandbox;
- a general-purpose policy language or policy-management platform; or
- a replacement for the host runtime's executor, retries, persistence, or
  physical outcome recording.

AgentFuse includes bounded deterministic policy evaluation for trusted
tool-call requests. The integrating application remains responsible for
establishing trusted identity, authority, approval, capability, risk, and
business-policy context.

## Lifecycle Model

The conceptual lifecycle is:

```text
authority decision       external or host-owned
        |
        v
policy decision          allow or block
        |
        v
dispatch boundary        guarded before handler invocation
        |
        v
execution                host-runtime owned
        |
        v
evidence                 decision plus observable runtime facts
```

An authority decision may come from the host application or a separate
authority system. AgentFuse does not require a particular authority system and
does not create authority by itself.

At the policy stage, AgentFuse evaluates the trusted request. With the
decision-only APIs, the host enforces that result at its own dispatch boundary.
With guarded invocation APIs, AgentFuse calls the supplied handler only after
an `allow` decision.

After dispatch, the host runtime remains authoritative for handler execution,
retries, downstream effects, and the final physical outcome.

## Decision and Outcome Are Different Facts

A decision describes what policy concluded before execution. An outcome
describes what happened at or after the execution boundary.

```text
decision != outcome
```

The same `allow` decision can lead to different runtime outcomes:

| Decision | Dispatch | Example outcome | Meaning |
| --- | --- | --- | --- |
| `allow` | started | `executed` | The handler completed on the observed path. |
| `allow` | started | `execution_failed` | The handler started and later failed. |
| `block` | not started | `not_executed` | Policy stopped the call before dispatch. |

An `allow` decision does not prove that execution started or succeeded. The
runtime must record those later facts.

### Blocked is not failed

A blocked call is a completed policy decision, not a failed tool execution:

```text
blocked != failed
```

For a block on an explicit guarded path, the expected invariant is:

```text
decision: block
dispatch: false
handler_invoked: false
execution_status: not_executed
```

### `not_executed` is not a tool error

`not_executed` means the protected handler was not entered. A tool error means
execution began and the handler or a downstream dependency reported a failure.

```text
not_executed != tool_error
```

Keeping these states separate prevents a denied request from being reported as
though a side-effect-capable tool had run and failed.

## Evidence Ownership

AgentFuse evidence can retain safe boundary facts such as:

- the original tool-call ID and tool name;
- the policy decision and machine-readable reason;
- policy and argument digests;
- whether dispatch or handler invocation occurred on a guarded path; and
- a non-execution or execution outcome where the integrated path can observe
  it.

Raw arguments, credentials, request bodies, environment values, and protected
paths are excluded from default evidence output. A digest supports correlation
without making the evidence record a copy of the original payload.

The runtime remains the source of truth for physical execution facts. AgentFuse
must not infer a successful execution, failure, or side effect from an `allow`
decision alone.

## Interoperability

AgentFuse can compose with authority, approval, policy, and evidence systems
without absorbing their schemas or responsibilities.

An integration may carry opaque references such as:

```text
action_ref
tool_call_id
authority_receipt_ref
policy_decision_ref
execution_evidence_ref
```

These references link separately owned lifecycle records:

- an authority system may provide an action or authority receipt reference;
- the host runtime supplies the canonical tool-call identity;
- AgentFuse records the policy decision enforced at the guarded boundary; and
- the runtime supplies final execution facts and may link them to the AgentFuse
  evidence record.

A reference does not prove that its issuer is trusted or that the referenced
decision is current. The integrating application remains responsible for
validation, freshness, expiry, and authorization semantics.

This model is an AgentFuse integration boundary, not a protocol standard. Host
runtimes may use different field names and result shapes as long as they
preserve the lifecycle distinctions and ownership rules described here.

## Integration Invariant

A conforming guarded integration should be able to demonstrate all of the
following for its tested path:

- the original tool-call identity remains available;
- a policy decision occurs before handler dispatch;
- a blocked call does not invoke the protected handler;
- `not_executed` remains distinct from post-dispatch failure;
- an allowed call's final outcome comes from the host runtime; and
- default evidence does not copy protected tool arguments.

These observations describe the integrated path only. They are not a security,
compliance, production-deployment, or universal runtime guarantee.
