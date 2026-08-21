# AgentFuse

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](pyproject.toml)
[![AgentFuse](https://img.shields.io/badge/AgentFuse-3.7.3-green.svg)](pyproject.toml)
[![Status](https://img.shields.io/badge/status-experimental%20public%20beta-orange.svg)](docs/dhms_agentfuse_integration_release_seal_v3_7_3.md)

**AgentFuse is the vendor-neutral execution policy layer for AI agents: keep your existing runtime, evaluate tool calls before dispatch, preserve tool-call identity, and produce structured execution evidence.**

AgentFuse 3.7.3 is an **Experimental Public Beta**.

```bash
python -m pip install dhms-agentfuse==3.7.3
```

Chinese technical overview: [README.zh-CN.md](README.zh-CN.md)

## The Problem

Agents increasingly use tools that read data, write files, call APIs, send
messages, or trigger other external actions. The policy for those actions often
ends up fragmented across prompts, workflow branches, provider callbacks, and
framework-specific middleware.

That fragmentation makes a few basic questions harder to answer consistently:

- Was the tool call allowed or blocked before execution?
- Did the handler start, or was the call only denied by policy?
- Does the terminal result still refer to the original tool-call identity?
- Can the runtime record safe evidence without copying protected arguments?

Prompt instructions alone do not create an execution boundary. A generic tool
error also cannot reliably distinguish a pre-dispatch block from a handler that
started and failed.

## The Solution

AgentFuse sits at an explicit integration point immediately before tool
dispatch:

```text
existing agent runtime
        |
        v
trusted ToolCallRequest
        |
        v
AgentFuse allow | block
        |
        +---- block -> terminal non-execution evidence
        |
        +---- allow -> host-owned dispatch and outcome
```

You keep your existing agents and runtime. There is no runtime migration:
AgentFuse plugs into a runtime's existing pre-tool hook, middleware boundary,
or explicit guarded invocation path instead of replacing its graph, model,
approval flow, persistence, or executor.

AgentFuse provides:

- deterministic pre-dispatch `allow` or `block` policy decisions;
- fail-closed behavior for policy exceptions and malformed policy results;
- preservation of the original tool-call ID and tool name;
- structured decision and non-execution evidence with safe argument digests;
- sync and async decision APIs; and
- cross-runtime integration surfaces that preserve each host's lifecycle model.

The integrating application still owns trusted action identity, approval,
business policy, physical dispatch, execution outcomes, retries, and recovery.
AgentFuse does not infer whether an action is intrinsically dangerous from
prompt text or model arguments.

## Current Integrations

The table separates packaged adapters from external samples and proofs. These
entries are verified integration surfaces, not claims of endorsement,
certification, production deployment, or upstream framework adoption.

| Runtime or ecosystem | Verified surface | Public beta status |
| --- | --- | --- |
| [LangGraph](docs/dhms_agentfuse_five_minute_integration_trial_v3_7_1.md) | Packaged `LangGraphRuntimeGuardAdapter` for an explicit `ToolNode` path, with identity-preserving terminal results and tested allow/block behavior at recorded versions. | Built-in public-beta adapter; not universal LangGraph interception. |
| [Microsoft Agent Framework sample](https://github.com/microsoft/agent-framework/pull/7719) | Optional `FunctionMiddleware` sample and focused contract tests for pre-dispatch block, guard failure, cancellation, and host-owned handler failure. | Experimental external sample; not part of the upstream package. |
| [PraisonAI](https://github.com/MervinPraison/PraisonAI/pull/4023) | Generic `tool_call_id` middleware plumbing is upstream; an [optional AgentFuse plugin](https://github.com/MervinPraison/PraisonAI-Plugins/pull/18) maps decisions to host-native `ToolResponse` results. | Experimental plugin contribution under review; no adoption claim. |
| [Pydantic ecosystem](https://github.com/pydantic/pydantic-ai-harness/issues/642) | A validated fork proof maps `RuntimeGuard` to the existing `ToolGuardrail` boundary while preserving host-native block semantics and sibling continuation. | Experimental fork proof; not an upstream integration. |
| [DSH](docs/dhms_agentfuse_multi_runtime_integration_package_v3_7_0.md#dsh-tools-pre-execute) | Separate TypeScript [pre-execute plugin](https://github.com/MkaliezZ/dsh-agentfuse-plugin) for one pinned DeepSeek Harness path, with conformance provenance exposed as package metadata. | Reviewed experimental external adapter; not official DeepSeek certification. |

The public package also includes a provider-neutral reference consumer and an
immutable integration metadata registry:

```python
from dhms_agentfuse.integrations import get_integration, list_integrations

profiles = list_integrations()
langgraph = get_integration("langgraph-tool-node")
```

Integration profiles describe reviewed mappings. They do not discover
runtimes, install plugins, or make different host lifecycles equivalent.

## Five-Minute Trial

Run one allowed and one blocked call through a real LangGraph `ToolNode`. The
trial requires no LLM provider, API key, or runtime external service.

```bash
python -m pip install dhms-agentfuse==3.7.3 "langgraph==1.2.11"
git clone --branch v3.7.3 --depth 1 \
  https://github.com/MkaliezZ/dhms-engine.git agentfuse-beta
cd agentfuse-beta
python examples/integration_trial/five_minute_v3_7_1/run_trial.py
```

Expected behavior:

```text
allowed handler execution count = 1
blocked handler execution count = 0
AGENTFUSE_FIVE_MINUTE_INTEGRATION_TRIAL_V3_7_1_PASS
```

Read the [five-minute trial guide](docs/dhms_agentfuse_five_minute_integration_trial_v3_7_1.md)
for the exact contract and boundaries. Provider-neutral denial fixtures are
also available in
[`examples/trial/denial_lifecycle_regression_fixtures/`](examples/trial/denial_lifecycle_regression_fixtures/).

## Early Validation Program

### Free technical validation for early adopters

If you maintain an agent runtime or an agent with side-effect-capable tools,
AgentFuse can be evaluated against one bounded tool path in your existing
architecture. The goal is to check whether the current request, policy,
identity, and evidence contracts map cleanly to your runtime without requiring
a runtime migration.

Read the [Early Validation Program](docs/agentfuse_early_validation_program.md),
then [open a Beta Integration Request](https://github.com/MkaliezZ/dhms-engine/issues/new?template=agentfuse-beta-integration.yml)
with your repository, runtime or framework, and one protected tool or action.
This is a bounded public-beta technical validation, not a promise of custom
development or indefinite engineering support.

## Public API

Use `evaluate()` when your runtime owns dispatch and physical outcome
recording:

```python
from dhms_agentfuse import RuntimeGuard, ToolCallRequest

guard = RuntimeGuard(
    allow_tools={"read_project_summary"},
    deny_tools={"delete_file"},
    default_action="block",
)

request = ToolCallRequest(
    tool_call_id="call-001",
    tool_name="delete_file",
    arguments={"path": "example.txt"},
)
decision = guard.evaluate(request)

assert decision.action == "block"
assert decision.tool_call_id == "call-001"
assert decision.evidence.non_execution.status == "not_executed"
```

`evaluate()` and `aevaluate()` do not accept a handler and perform no protected
side effect. `invoke()` and `ainvoke()` use the same decision path and can call
a supplied handler only after an `allow` decision.

For the complete lifecycle split, see the
[Consumer Integration Contract](docs/dhms_agentfuse_consumer_integration_contract_v3_6_1.md).

## Execution Evidence

AgentFuse keeps policy decisions separate from execution outcomes. A blocked
call is represented as a completed policy decision with a `not_executed`
outcome, not as a failed physical tool execution.

Safe evidence can retain:

- tool-call ID and tool name;
- policy decision and machine-readable reason;
- policy and argument digests;
- whether dispatch or handler invocation occurred on guarded paths; and
- non-execution or execution outcome where that path can observe it.

Raw arguments, filesystem paths, environment variables, credentials, and
request bodies are excluded from default evidence output. When another runtime
owns dispatch, that runtime remains responsible for recording the physical
outcome.

## Responsibility Boundary

### The integrating application owns

- action proposals, approvals, expiry, and identity validation;
- trusted capability, risk, and business-policy context;
- dispatch, persistence, retries, recovery, and physical outcomes; and
- every execution path that does not pass through an integrated guard.

### The adapter owns

- mapping trusted host context into `ToolCallRequest`;
- preserving request and response identity; and
- translating the canonical decision into host-native lifecycle results.

### AgentFuse owns

- deterministic policy evaluation for trusted requests;
- canonical `allow` or `block` decision evidence;
- fail-closed handling of policy errors; and
- pre-dispatch enforcement for handlers routed through guarded invocation APIs.

## Public Beta Boundaries

AgentFuse 3.7.3 does not claim:

- production readiness or universal side-effect prevention;
- a process sandbox, network firewall, malware detector, or DLP system;
- automatic protection for direct or unwrapped execution paths;
- intrinsic action-danger classification or business correctness;
- exactly-once physical execution or global replay protection;
- official certification by any listed runtime or framework; or
- external adoption merely because an integration sample, proof, issue, or pull request exists.

See the [v3.7.3 release seal](docs/dhms_agentfuse_integration_release_seal_v3_7_3.md)
and [machine-readable record](release/agentfuse_v3_7_3_release_seal.json) for
the exact reviewed evidence and compatibility cells.

## Documentation

- [RuntimeGuard decision API](docs/dhms_agentfuse_public_decision_api_v3_6_0.md)
- [Consumer integration contract](docs/dhms_agentfuse_consumer_integration_contract_v3_6_1.md)
- [Multi-runtime integration package](docs/dhms_agentfuse_multi_runtime_integration_package_v3_7_0.md)
- [Five-minute integration trial](docs/dhms_agentfuse_five_minute_integration_trial_v3_7_1.md)
- [Compatibility matrix and CI](docs/dhms_agentfuse_compatibility_matrix_and_ci_v3_7_2.md)
- [v3.7.3 release seal](docs/dhms_agentfuse_integration_release_seal_v3_7_3.md)
- [Historical evidence archive](docs/)

## Maintainer Checks

```bash
python -m pip install -e .
python examples/runtime_guard/runtime_guard_mvp_demo.py
python examples/runtime_guard/langgraph_runtime_guard_demo.py
python examples/conformance/cross_adapter_v3_6_2/run_conformance.py
```

These checks are deterministic local evidence. They do not invoke a model,
provider, real shell, database, or external side-effect service.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).

Copyright 2026 Huaxinsheng Zhong.

## Trademark Notice

DHMS, DHMS Engine, DHMS AgentFuse, and DHMS Agent Harness are project names and
marks of Huaxinsheng Zhong. Accurate reference does not imply endorsement,
sponsorship, or affiliation. The Apache-2.0 license applies to the source code
and documentation; it does not grant trademark rights.
