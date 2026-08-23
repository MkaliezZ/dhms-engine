# AgentFuse Design Partner Evaluation Guide

## Purpose

This guide helps an external runtime maintainer or enterprise AI engineer
evaluate AgentFuse against one explicit tool-execution path. The evaluation is
structured around observable runtime behavior rather than product adoption or
a broad architecture review.

Use synthetic inputs and a local, staging, or otherwise controlled handler. A
production environment is not required.

## 1. Who Should Evaluate AgentFuse

AgentFuse is most relevant to people who can identify and observe the boundary
immediately before a runtime invokes a tool handler.

Potential evaluators include:

- MCP host, gateway, client, or server-runtime maintainers;
- agent framework developers responsible for tool middleware or execution;
- enterprise AI platform teams operating side-effect-capable agent workflows;
- custom agent runtime owners with an explicit dispatcher or executor; and
- infrastructure engineers responsible for tool-call lifecycle evidence.

The best evaluation target is one bounded tool path with:

- a stable tool-call identity;
- a visible pre-handler policy or middleware hook;
- an observable handler invocation; and
- synthetic or controlled execution behavior.

## 2. Evaluation Goal

The goal is not security certification, compliance validation, penetration
testing, or proof that every runtime path is protected.

The goal is to verify whether one tested path can demonstrate these execution
assurance invariants:

- a blocked tool call does not cross the dispatch boundary;
- a blocked handler is not invoked;
- an allowed tool call can cross the boundary and execute;
- an allowed call that fails after dispatch remains distinct from a policy
  denial;
- the original tool-call identity remains available; and
- safe evidence preserves the decision and observable execution facts without
  copying protected inputs.

The host runtime remains authoritative for physical dispatch, handler
execution, retries, downstream effects, and final outcomes.

## 3. Fifteen-Minute Evaluation Flow

### Step 1 - Understand the Lifecycle Model (3 minutes)

Read the [Execution Assurance Model](execution_assurance_model.md). Confirm the
separation between:

```text
authority context
        |
        v
policy decision
        |
        v
dispatch boundary
        |
        v
handler invocation
        |
        v
execution outcome
        |
        v
evidence
```

The key distinction is:

```text
decision != outcome
blocked != failed
not_executed != tool_error
```

For the framework-neutral test contract, see
[Execution Assurance Conformance v0.1](agentfuse_execution_assurance_conformance_v0_1.md).

### Step 2 - Run the Design Partner Trial (5 minutes)

From the repository root:

```bash
python -m pip install -e .
python examples/design_partner_trial/run_trial.py
```

The deterministic [Design Partner Trial](../examples/design_partner_trial/)
runs three synthetic scenarios:

1. blocked before dispatch;
2. allowed and executed; and
3. allowed, dispatched, and failed inside the simulated handler.

The expected final verdict is:

```text
AGENTFUSE_DESIGN_PARTNER_TRIAL_PASS
```

This verdict applies to the local trial only. It is not evidence that an
external runtime has already integrated AgentFuse.

### Step 3 - Inspect the Evidence (3 minutes)

For each trial scenario, inspect:

- `tool_call_id` and tool name;
- policy `decision`;
- whether dispatch started;
- whether the handler was invoked;
- execution status; and
- safe decision or correlation metadata.

Confirm the three lifecycle shapes:

| Scenario | Decision | Dispatch | Handler | Outcome |
| --- | --- | --- | --- | --- |
| Blocked | `block` | not started | not invoked | `not_executed` |
| Allowed | `allow` | started | invoked | executed |
| Allowed but failed | `allow` | started | invoked | failed after dispatch |

Also confirm that an `allow` decision does not by itself claim execution
success and that the evidence does not require raw arguments or credentials.

### Step 4 - Map the Contract to an Existing Runtime (4 minutes)

Choose one existing tool path and locate:

1. where the runtime creates or receives the canonical tool-call identity;
2. where policy can run before dispatch;
3. which component can prevent handler invocation;
4. which events or result objects show dispatch and handler state; and
5. where the runtime records the final execution outcome.

The mapping does not need to adopt an AgentFuse-specific result class. Native
events and result objects are sufficient if they preserve the same lifecycle
distinctions.

At the end of this step, record whether the integration point is:

- directly available;
- available with a small adapter;
- missing a required lifecycle observation; or
- unsuitable because AgentFuse cannot govern the actual dispatch path.

## 4. Information Requested From the Evaluator

Useful evaluation context includes:

- runtime or framework name and tested version or commit;
- the specific tool-invocation path under review;
- the pre-handler hook, middleware, wrapper, or dispatcher location;
- available execution lifecycle events or result types;
- how the runtime preserves tool-call identity;
- which execution facts the runtime can observe; and
- the decision or execution evidence the team would like to retain.

Use public-safe and synthetic descriptions. Do not provide:

- secrets, API keys, tokens, or private credentials;
- raw production tool payloads or prompts;
- customer, employee, or other private data;
- protected filesystem paths, request bodies, or database contents; or
- access to a private or production environment.

An arguments digest, synthetic payload, redacted event shape, or minimal public
reproduction is sufficient.

## 5. Feedback Template

Copy this template into an
[AgentFuse Beta Integration Request](https://github.com/MkaliezZ/dhms-engine/issues/new?template=agentfuse-beta-integration.yml)
or another agreed public review thread:

```markdown
## Runtime tested

- Runtime/framework:
- Version or commit:
- Tested tool path:

## Scenarios tested

- [ ] Blocked before dispatch
- [ ] Allowed and executed
- [ ] Allowed but failed after dispatch

## Integration point

- Tool-call identity source:
- Pre-handler hook or boundary:
- Dispatch observation:
- Handler invocation observation:
- Final outcome owner:

## Evidence reviewed

- Decision fields available:
- Execution fields available:
- Safe metadata available:

## Missing information or friction

- Missing lifecycle observation:
- Unclear ownership or mapping:
- Documentation gap:

## Desired improvements

- Smallest change that would make evaluation easier:
- Framework-specific guidance that would help:
```

Do not attach secrets, credentials, raw private payloads, or production traces
to the feedback.

## 6. Boundaries

AgentFuse does not replace:

- authorization systems or authority providers;
- identity providers or identity registries;
- approval workflows, review queues, or resume coordination;
- operating-system, process, container, filesystem, or network sandboxing;
- host-runtime scheduling, retries, persistence, or recovery; or
- the runtime's final physical execution record.

An AgentFuse evaluation covers only the explicitly tested guarded path. It does
not establish universal interception, production readiness, a security
guarantee, a compliance control, or a framework certification.

The evaluation result should report what was observed, what could not be
observed, and which component owned each lifecycle fact.
