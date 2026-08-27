# DHMS AgentFuse v3.7.1 Five-Minute Integration Trial

## Purpose

v3.7.1 exercises the reviewed public AgentFuse LangGraph mapping as a small,
reproducible consumer trial. It uses the installed LangGraph `ToolNode` path
without a model, provider API, credential, or runtime network service.

LangGraph is the selected consumer because it is independently maintained, its
reviewed ToolNode mapping already exists, and the frozen tested version is
known: `langgraph 1.2.11`.

## Bounded Consumer Workflow

The trial is designed as an approximately-five-minute integration path:

1. Install `dhms-agentfuse 3.7.1` with `langgraph==1.2.11`.
2. Select `langgraph-tool-node` through the public integration registry.
3. Copy and run the small consumer example.

The consumer code is in
[`examples/integration_trial/five_minute_v3_7_1/`](../examples/integration_trial/five_minute_v3_7_1/).
It imports AgentFuse only through public exports:

```python
from dhms_agentfuse import LangGraphRuntimeGuardAdapter, RuntimeGuard
from dhms_agentfuse.integrations import get_integration
```

It does not import implementation modules, registry internals, tests,
conformance helpers, or DSH code.

## Trial Cases

The allow case calls a trusted synthetic summary tool. The policy decision is
`allow`, an external in-memory counter observes one selected handler start, and
the terminal receipt records `executed`. Starting with AgentFuse 3.7.4, the
LangGraph receipt itself leaves `handler_started` unknown because the adapter
only observes the opaque host continuation. This is a selected successful host
outcome, not a claim that `allow` always means successful physical execution.

The block case calls a registered synthetic mutation tool through the same
wrapped `ToolNode`. The policy decision is `block`, the receipt records
`not_executed`, dispatch is not observed, and the protected handler counter is
exactly zero. The terminal ToolMessage and receipt retain the original call ID.

## Run

```bash
pip install -e . "langgraph==1.2.11"
python examples/integration_trial/five_minute_v3_7_1/run_trial.py
python examples/integration_trial/five_minute_v3_7_1/run_trial.py --json-only
```

The normal command emits an indented result followed by:

```text
AGENTFUSE_FIVE_MINUTE_INTEGRATION_TRIAL_V3_7_1_PASS
```

`--json-only` emits exactly one deterministic JSON document. It has a trial
version, integration ID, expected and observed runtime version, local-runtime
requirements, two case records, and an overall verdict. It does not include the
raw synthetic protected argument.

## Clean-Wheel Proof

The acceptance path builds `dhms_agentfuse-3.7.1-py3-none-any.whl`, installs it
into a fresh temporary virtual environment, installs `langgraph==1.2.11`, and
copies only the consumer trial files into a separate temporary directory. The
runner executes with a non-repository `PYTHONPATH`; the imported package origin
is checked to be the installed wheel rather than the source checkout.

## Ownership and Boundaries

AgentFuse provides the bounded pre-dispatch policy decision through the existing
RuntimeGuard and wrapped adapter. LangGraph owns ToolNode and graph execution
semantics, including interruption, checkpoint, and resume behavior where used.
The `IntegrationProfile` only identifies the reviewed mapping; it does not
enforce policy.

For the LangGraph adapter, `dispatch_occurred=true` means AgentFuse called the
host-provided execution continuation. Physical handler entry is not inferred
from that call; the receipt uses `null` when LangGraph does not expose stronger
evidence at the wrapper boundary.

The trial requires no API key, LLM provider, model call, or runtime network
service. Its handlers only increment local in-memory counters; no filesystem,
database, or external action occurs.

## What Five-Minute Means

"Five-Minute Integration Trial" is a design and documentation target for the
small bounded workflow above. Automated execution time is not human setup time.
This milestone does not claim that an external human completed the integration
in five minutes, external adoption, product validation, or product-market fit.

## Supported Claims

- A clean consumer environment can install the v3.7.1 wheel and run the public
  AgentFuse LangGraph mapping at the tested `1.2.11` version.
- The tested local path produces one allowed handler start and zero blocked
  handler starts.
- The consumer uses public AgentFuse imports and serializes no raw synthetic
  protected argument in its canonical result.

## Explicit Non-Claims

This trial does not claim production readiness, production security, universal
LangGraph interception, compatibility with every LangGraph version, official
LangGraph certification, universal runtime integration, DSH trial validation,
provider compatibility, exactly-once physical execution, sandboxing, DLP,
malware prevention, external human timing, external adoption, or that metadata
profiles enforce policy by themselves.

## Validation

```bash
python3.11 -m pytest tests/test_five_minute_integration_trial_v3_7_1.py -q
python3.11 -m pytest
python3.11 -m compileall -q dhms_agentfuse
python3.11 examples/conformance/cross_adapter_v3_6_2/run_conformance.py
python3.11 examples/conformance/cross_adapter_v3_6_2/run_conformance.py --json-only
python3.11 examples/integration_trial/five_minute_v3_7_1/run_trial.py
python3.11 examples/integration_trial/five_minute_v3_7_1/run_trial.py --json-only
```

## Known Limitations and Next Milestone

The trial covers only the reviewed explicit ToolNode wrapper at LangGraph
`1.2.11`; it is not a compatibility matrix. v3.7.2 Compatibility Matrix and
CI is next and is not started by this milestone. The v3.8.x external-consumer /
real-trial condition and v4.0 external-use / compatibility-stability condition
remain unchanged.
