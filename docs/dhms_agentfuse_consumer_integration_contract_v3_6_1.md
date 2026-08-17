# DHMS AgentFuse Consumer Integration Contract 3.6.1

Package identity: `dhms-agentfuse 3.6.1`.

## Problem

An agent runtime can make a pre-dispatch policy decision without owning the
rest of an application's lifecycle. Treating that decision as approval,
handler execution, process completion, or goal achievement loses the facts
needed to debug a blocked, interrupted, or failed call safely.

This contract describes the minimum relationship between AgentFuse's immutable
`RuntimeGuardDecision` and a host that owns its own lifecycle. It is
provider-neutral and local-only.

## Consumer Contract

Use `RuntimeGuard.evaluate()` or `RuntimeGuard.aevaluate()` to obtain a
`RuntimeGuardDecision` before host dispatch.

* When `action="block"`, the host MUST NOT dispatch the protected handler for
  that decision. The host records a non-execution outcome such as
  `not_executed`; the handler has not started.
* When `action="allow"`, the host MAY begin its own dispatch stage after its
  own approval, identity, and business-policy checks. `allow` does not prove
  handler start, handler success, side-effect absence or presence, process
  success, or goal achievement.
* A host interruption or pause is distinct from an execution failure. A handler
  failure is distinct from a policy block.
* Policy exceptions and malformed policy results fail closed through the
  existing `policy_exception` and `invalid_policy_decision` reason codes.

The same semantic rules apply to `evaluate()` and `aevaluate()`. A synchronous
consumer must not attempt to run an async-only policy through `evaluate()`;
that path fails closed.

## Ownership Boundary

AgentFuse owns deterministic `ToolCallRequest` policy evaluation, the
canonical `allow|block` decision, canonical decision evidence, and fail-closed
handling of policy exceptions or malformed policy values.

The host owns approval, trusted action identity, durable lifecycle persistence,
dispatch, retries, recovery, process completion, and goal completion. AgentFuse
does not decide whether a process or agent run failed merely because one call
was blocked.

The lifecycle facts are separate:

```text
policy decision
!= approval
!= dispatch
!= execution outcome
!= process completion
!= goal achievement
```

## Reference Consumer Proof

`examples/runtime_guard/consumer_integration_contract_demo.py` is a local,
provider-neutral reference consumer. It uses `RuntimeGuardDecision` directly;
it does not create another public decision type or a new AgentFuse executor.

The proof covers four deterministic cases:

1. A blocked call is not dispatched and its handler count remains zero.
2. An allowed call can be dispatched and its local handler executes once.
3. An allowed call can be interrupted by the host before its handler starts;
   that remains `interrupted`, not a policy denial or tool failure.
4. An allowed call whose handler raises becomes `execution_failed`; it remains
   distinct from policy denial.

The reference receipt deliberately leaves `approval_state`, process completion,
and goal achievement as host-owned facts. It does not make a claim about a
real task, process, or external side effect.

## Privacy and Safe Evidence

`ToolCallRequest` retains arguments for local policy evaluation but its default
safe representations expose an arguments hash, not raw arguments. The
reference consumer carries only `RuntimeGuardDecision.to_safe_dict()` into its
safe receipt. Its tests assert that protected fixture values do not appear in
default serialized output.

## External Semantic Mappings

These are conceptual comparisons, not integration claims.

* **LangGraph:** `GraphInterrupt` is control-flow pause semantics, not an
  ordinary tool failure. LangGraph owns pause and resume behavior. This
  milestone does not change or certify a LangGraph integration.
* **Claude Code headless permission denial:** a permission denial can coexist
  with successful process completion. The denial is a separate lifecycle fact.
  This milestone adds no Claude Code adapter or integration claim.
* **DSH:** DSH remains an external consumer/plugin integration and is not a
  dependency of this repository. Future conformance fixtures may be reused by
  the independent `dsh-agentfuse-plugin` repository.

## Non-Claims

This contract does not add production runtime enforcement, a universal
interceptor, approval UI, retry or workflow engine, policy loader, trust store,
provider/model integration, Claude Code adapter, DSH dependency, MCP gateway,
or shell, filesystem, browser, email, Git, Docker, cloud, database, or network
execution capability. It is not a security, compliance, certification, or
interoperability standard.

## Validation

```bash
python -m pytest tests/test_consumer_integration_contract.py -q
python examples/runtime_guard/consumer_integration_contract_demo.py
python -m pytest
python -m compileall -q dhms_agentfuse
```

Expected demo verdict:

```text
AGENTFUSE_CONSUMER_INTEGRATION_CONTRACT_DEMO_PASS
```
