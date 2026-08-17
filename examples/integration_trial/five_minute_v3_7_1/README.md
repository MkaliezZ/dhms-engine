# AgentFuse v3.7.1 LangGraph Consumer Trial

This small consumer example uses the public AgentFuse API with a real local
LangGraph `ToolNode`. It is designed as an approximately five-minute
integration path, not evidence that an external human completed it in five
minutes.

## Prerequisites

- Python 3.10+
- `dhms-agentfuse 3.7.1`
- `langgraph==1.2.11`

No API key, model call, or runtime network service is required.

## Run

```bash
pip install -e . "langgraph==1.2.11"
python examples/integration_trial/five_minute_v3_7_1/run_trial.py
python examples/integration_trial/five_minute_v3_7_1/run_trial.py --json-only
```

The consumer performs three visible integration steps:

1. Look up `langgraph-tool-node` using `get_integration()`.
2. Create a public `RuntimeGuard` and public `LangGraphRuntimeGuardAdapter`.
3. Run one allow and one block call through an explicit LangGraph `ToolNode`.

The allow case invokes its synthetic in-memory handler exactly once. The block
case still reaches the guarded ToolNode boundary but has zero protected handler
starts and zero dispatch. Both terminal messages retain their original tool-call
identity.

`--json-only` writes one deterministic JSON document to stdout. It contains
only decisions, outcomes, counters, identities, and runtime metadata; the raw
synthetic argument is not serialized.

## Consumer Boundary

[`consumer.py`](consumer.py) imports AgentFuse only through:

```python
from dhms_agentfuse import LangGraphRuntimeGuardAdapter, RuntimeGuard
from dhms_agentfuse.integrations import get_integration
```

It does not import AgentFuse implementation modules, tests, conformance
helpers, DSH, or registry internals. The profile is metadata only; the existing
RuntimeGuard and wrapped ToolNode own the tested decision and dispatch path.

## Non-Claims

This is a bounded local consumer trial. It does not establish external
adoption, external human timing, production readiness, universal LangGraph
interception, compatibility beyond LangGraph 1.2.11, provider compatibility,
or physical side-effect guarantees.
