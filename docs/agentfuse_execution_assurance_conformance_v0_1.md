# AgentFuse Execution Assurance Conformance v0.1

## Purpose

This document defines a framework-neutral validation contract for execution
assurance at an explicit runtime dispatch boundary. It gives runtimes and
adapters a small set of observable lifecycle invariants without requiring an
AgentFuse API, receipt format, transport, or framework-specific result type.

Conformance applies only to the guarded path under test. It does not establish
behavior for unwrapped handlers, alternate dispatch paths, or the runtime as a
whole.

## 1. Scope

AgentFuse execution assurance checks whether a policy decision governed the
actual dispatch boundary and whether the protected handler was invoked.

The contract separates:

- the decision made before dispatch;
- whether dispatch started;
- whether the protected handler was invoked; and
- the execution disposition observed by the host runtime.

This contract does not define:

- identity providers or identity registries;
- delegation or authority systems;
- authorization providers;
- approval workflows, review queues, or resume behavior;
- operating-system, process, container, filesystem, or network sandboxing;
- a general-purpose policy language; or
- the host runtime's retry, persistence, recovery, or result model.

The integrating runtime remains responsible for trusted request identity,
authority and approval context, physical execution, and final outcome
recording.

## 2. Lifecycle Model

The lifecycle under test is:

```text
authority context        external or host-owned
        |
        v
policy decision          allow or block
        |
        v
dispatch boundary        protected transition into execution
        |
        v
handler invocation       runtime-owned callable
        |
        v
execution outcome        runtime-observed disposition
        |
        v
evidence                 safe lifecycle facts
```

Authority context may be present, but this contract does not evaluate or
validate it. The conformance target begins with a trusted tool-call request and
a policy decision that is enforced before the handler starts.

A policy decision and an execution outcome describe different facts:

```text
decision != execution_status
```

A block is complete when the runtime can show that dispatch and handler
invocation did not occur. It is not an execution failure:

```text
block -> not_executed
allow -> executed | failed
```

## 3. Required Conformance Scenarios

A conforming implementation MUST exercise all three scenarios against the same
documented dispatch path. The policy rules and handlers MAY be synthetic, but
the dispatch and handler observations MUST come from the path under test.

### Scenario A - Blocked Before Dispatch

The policy blocks the request before the runtime invokes the protected
handler.

Required observations:

```text
decision=block
dispatch_started=false
handler_invoked=false
execution_status=not_executed
```

The test MUST use a handler invocation counter, sentinel, or equivalent runtime
observation to prove that the protected handler was not entered. Reporting a
generic tool error without proving non-dispatch does not satisfy this scenario.

### Scenario B - Allowed Execution

The policy allows the request, the runtime crosses the dispatch boundary, and
the protected handler completes.

Required observations:

```text
decision=allow
dispatch_started=true
handler_invoked=true
execution_status=executed
```

The `allow` decision alone is not sufficient. The host runtime MUST provide the
dispatch, handler, and execution observations.

### Scenario C - Allowed but Failed

The policy allows the request, the runtime crosses the dispatch boundary, and
the protected handler or a downstream dependency fails after invocation.

Required observations:

```text
decision=allow
dispatch_started=true
handler_invoked=true
execution_status=failed
```

The earlier policy decision MUST remain `allow`. The runtime MUST NOT rewrite
the decision to `block` or report the failure as `not_executed`.

A runtime MAY use a native value such as `execution_failed`. Its conformance
test must document the unambiguous mapping from that native value to the v0.1
`failed` disposition.

## 4. Evidence Requirements

Each scenario MUST produce or expose enough structured data for a test to
evaluate this minimum logical record:

```json
{
  "tool_call_id": "call-001",
  "decision": "block",
  "dispatch_started": false,
  "handler_invoked": false,
  "execution_status": "not_executed",
  "safe_metadata": {}
}
```

The record defines logical fields, not a required wire format. A runtime MAY
use different names or distribute these facts across native events and result
objects if its conformance test shows how they map to the contract.

Required evidence semantics:

- `tool_call_id`: preserves the original runtime tool-call identity;
- `decision`: records the pre-dispatch `allow` or `block` result;
- `dispatch_started`: records whether the protected dispatch boundary was
  crossed;
- `handler_invoked`: records whether the protected handler was entered;
- `execution_status`: records `not_executed`, `executed`, or `failed`; and
- `safe_metadata`: carries only non-sensitive correlation or decision data.

These logical facts may be assembled from more than one observation source.
For example, an adapter receipt may prove host-continuation dispatch while a
runtime-owned counter proves handler entry. If a particular record cannot
observe handler entry, it must represent that field as unknown rather than
coercing it to `true` or `false`; a conformance claim still needs separate host
evidence for the required scenario.

Safe metadata MAY include:

- tool name;
- machine-readable reason code;
- policy identifier or digest;
- arguments digest; and
- an opaque evidence or authority receipt reference.

The conformance record MUST NOT require or copy:

- raw tool arguments;
- credentials, tokens, or environment values;
- request bodies or protected filesystem paths; or
- embedded authority, identity, or approval data.

An opaque reference MAY be retained, but this contract does not establish the
reference's issuer, trust, freshness, or authorization meaning.

## 5. Framework Integration Guidance

Frameworks do not need to adopt an AgentFuse API or a shared receipt class.
They need an enforceable pre-handler boundary and testable lifecycle
observations.

### MCP

An MCP host, gateway, client integration, or server wrapper can evaluate policy
before forwarding a `tools/call` request to the handler. Its test should retain
the original tool-call identity, prove that a block was not forwarded, and map
the terminal host result to the conformance dispositions.

Tool schemas and annotations do not by themselves demonstrate conformance. The
test must exercise the component that can prevent dispatch.

### LangGraph

A LangGraph integration can enforce the decision at a `ToolNode`, middleware,
or other explicit pre-tool boundary. It may return a host-native tool message
or state update, provided the original tool-call identity remains available
and the test can distinguish a policy block from a handler failure.

Calling LangGraph's host-provided continuation proves adapter dispatch, not
physical handler entry. A wrapper that cannot observe the host's internal
handler boundary should report that field as unknown and use separate runtime
instrumentation when making a conformance claim.

Conformance applies only to the integrated node or middleware path. It does not
imply interception of every tool path in a graph.

### Custom Runtimes

A custom runtime can place a policy check immediately before its callable,
executor, job submission, or external-action adapter. A counter or sentinel can
prove handler invocation, while the runtime's native result or event model can
provide the final execution disposition.

The runtime remains free to own scheduling, retries, cancellation, persistence,
and terminal result delivery.

## 6. Conformance Report

A published conformance result SHOULD identify:

- the runtime and tested version or commit;
- the exact dispatch path under test;
- the mapping from native fields to the v0.1 logical fields;
- the result of Scenarios A, B, and C; and
- any lifecycle capability that the tested path cannot observe.

`PASS` means the tested path preserved every required invariant. It does not
mean that every path in the runtime is guarded.

## 7. Non-Goals and Non-Claims

This document does not define or claim:

- a security guarantee;
- a compliance control or certification;
- production readiness;
- universal interception of agent actions;
- a universal receipt or audit standard;
- a protocol extension for MCP, LangGraph, or another framework;
- exactly-once execution or side-effect prevention outside the tested path; or
- official framework endorsement, adoption, or certification.

AgentFuse execution assurance conformance is a bounded validation contract for
observable behavior at one explicit runtime dispatch boundary.
