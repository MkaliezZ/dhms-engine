# DHMS Real langgraph-bigtool API Wiring Demo v3.5.2

## Purpose

v3.5.2 upgrades the prior registry-pattern demo into a real
`langgraph-bigtool` API wiring demo. It imports and uses:

```python
from langgraph_bigtool import create_agent
```

The demo builds a DHMS-guarded `tool_registry`, passes it into
`create_agent()`, and supplies a deterministic `retrieve_tools_function`. This
is real `create_agent` wiring, not a full live production agent run.

## External Project Chosen

Project: `langchain-ai/langgraph-bigtool`

URL: https://github.com/langchain-ai/langgraph-bigtool

Observed stars: `545`

Reason chosen: `langgraph-bigtool` is a focused LangGraph project for agents
that retrieve and call tools from a tool registry. It is small and
understandable compared with a full framework repository, and its public README
shows a clear tool-registry boundary that DHMS can guard.

## Wiring Boundary

The external project pattern is:

```python
tool_registry = {
    tool_id: tool
    for tool_id, tool in discovered_tools.items()
}
```

The DHMS demo keeps the guard at that registry boundary before calling
`create_agent()`.

Minimal guard diff:

```python
from dhms_agentfuse.controlled_proposal_gate import evaluate_controlled_proposal
from langgraph_bigtool import create_agent

guarded_tool_registry = {
    tool_name: dhms_guard_tool(tool_name, tool)
    for tool_name, tool in tool_registry.items()
}

builder = create_agent(
    fake_model,
    guarded_tool_registry,
    retrieve_tools_function=retrieve_tools,
)
```

The demo reuses the existing DHMS bindable fake model path via
`create_deterministic_adapter_driver()`.

## Before / After

Before:

* the agent/tool path can reach every registered tool
* `safe_read_only_summary_tool` is reachable
* `dangerous_sql_mutation_tool` is reachable
* `model_api_request_tool` is reachable

After:

* DHMS observes each tool proposal before protected payload execution
* `safe_read_only_summary_tool` returns `RELEASE_CANDIDATE`
* `dangerous_sql_mutation_tool` returns `FAIL_CLOSED` with blocked category `sql_mutation`
* `model_api_request_tool` returns `FAIL_CLOSED` with blocked category `model_api`
* `imports_or_runs_langgraph_bigtool=true`
* `uses_create_agent=true`
* `passes_guarded_tool_registry_to_create_agent=true`
* `uses_deterministic_retrieve_tools_function=true`
* `agent_compiled=false`
* `agent_invoked=false`
* `agent_streamed=false`
* protected payload bodies are not executed
* `execution_authorized_count=0`
* `runtime_behaviors_added=0`

## Example Files

* [`examples/external_integrations/langgraph_bigtool/README.md`](../examples/external_integrations/langgraph_bigtool/README.md)
* [`examples/external_integrations/langgraph_bigtool/dhms_guarded_tool_registry_demo.py`](../examples/external_integrations/langgraph_bigtool/dhms_guarded_tool_registry_demo.py)

## Run

```bash
/usr/local/bin/python3.11 examples/external_integrations/langgraph_bigtool/dhms_guarded_tool_registry_demo.py
```

Expected final verdict:

`DHMS_REAL_LANGGRAPH_BIGTOOL_API_WIRING_DEMO_PASS`

## Preserved Boundaries

v3.5.2 preserves the v3.4.x proof boundary:

* no production runtime
* no authorization policy
* no provider SDK
* no SQLDatabaseToolkit
* no PythonREPLTool
* no agent graph compile/invoke/stream
* no semantic search, embeddings, or LangGraph Store
* no network calls during validation
* no SQL execution
* no database access
* no environment access
* no credential access
* no user-data access
* no protected payload body execution
* no real model API behavior
* no tag or release

## Next Direction

Public post / external feedback trigger.

Final document verdict:

`V3_5_2_PUSHED_READY_FOR_PUBLIC_POST_AND_EXTERNAL_FEEDBACK`
