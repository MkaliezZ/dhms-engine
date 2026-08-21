# AgentFuse Early Validation Program

AgentFuse 3.7.3 is an Experimental Public Beta. The Early Validation Program
helps developers evaluate one bounded tool-execution path in an existing agent
without migrating to a new runtime.

## Who This Is For

This program is intended for:

- developers building AI agents that call tools or external services;
- teams using multiple agent runtimes or framework-specific middleware;
- teams operating tool-execution workflows with pre-dispatch decisions;
- teams that need execution evidence or explicit approval boundaries; and
- runtime and framework maintainers evaluating a vendor-neutral policy layer.

The best starting point is one concrete tool or action whose dispatch boundary
is already identifiable in code.

## What Problem We Explore

Agent actions are increasingly connected to files, APIs, databases, messages,
and other external tools. As those paths grow, execution policy often becomes
fragmented across prompts, workflow branches, approval code, and middleware.

The validation focuses on whether one existing workflow can keep these facts
separate and observable:

- what the trusted policy allowed or blocked before dispatch;
- whether the protected handler started;
- whether the terminal result preserved the original tool-call identity; and
- what the host runtime recorded as the physical execution outcome.

AgentFuse owns the pre-dispatch policy decision and its evidence. The host
runtime continues to own approval, physical execution, persistence, retries,
recovery, and outcomes that occur after an allow decision.

## What Participants Receive

Participants receive bounded technical help for one validation path:

- technical setup guidance for `RuntimeGuard` or an existing reviewed adapter;
- five-minute trial support using the repository's deterministic LangGraph
  trial;
- a runtime integration discussion focused on one pre-tool hook, middleware
  boundary, or guarded invocation path; and
- feedback review covering request mapping, tool-call identity, decision
  evidence, and integration friction.

This is technical validation of the current public beta. It is not a commitment
to custom development, long-term support, or a production deployment.

## What We Ask From Participants

Participants should be willing to:

- try AgentFuse with one existing agent and tool workflow;
- provide concrete technical feedback on the decision and evidence contract;
- share integration friction, unclear lifecycle ownership, or missing adapter
  information; and
- report the smallest reproducible mismatch when the current approach does not
  fit the host runtime.

Please do not provide:

- confidential information;
- production credentials or API keys;
- private customer, user, or business data;
- protected prompts, tool payloads, filesystem paths, or database contents; or
- access to a production environment.

Use synthetic inputs and a local, staging, or otherwise controlled workflow.

## Current Scope

AgentFuse 3.7.3 is an Experimental Public Beta with a vendor-neutral,
runtime-neutral approach. It evaluates trusted `ToolCallRequest` objects and
returns canonical `allow` or `block` decisions before dispatch.

Current validation is limited to explicit guarded paths. AgentFuse does not
automatically intercept unwrapped execution, replace host approval or runtime
semantics, infer danger from prompt text, or guarantee production deployment.
Evidence applies only to the versions and paths identified during a bounded
trial.

## How To Start

1. Run the
   [five-minute integration trial](dhms_agentfuse_five_minute_integration_trial_v3_7_1.md)
   with synthetic inputs.
2. Choose one existing tool whose pre-dispatch boundary is visible and can be
   exercised without production access.
3. [Open an AgentFuse Beta Integration Request](https://github.com/MkaliezZ/dhms-engine/issues/new?template=agentfuse-beta-integration.yml)
   with a public repository link, the runtime or framework, and the protected
   tool or action.
4. Use the issue to discuss the smallest request mapping, expected decision,
   host-owned outcome, and any integration friction.

For documentation problems or reproducible public-beta defects that do not fit
the integration form, use the repository's
[general issue entry](https://github.com/MkaliezZ/dhms-engine/issues/new/choose).

Keep all shared examples public-safe and synthetic. A private repository,
credential, production trace, or confidential payload is not required to
participate.
