# DHMS External LangChain/LangGraph Integration Example v3.5.1

## Purpose

v3.5.1 adds a minimal external integration example showing how DHMS AgentFuse can
be placed around a real LangChain/LangGraph-style agent tool registry with a
small code change.

This is an example milestone only. It does not add production runtime behavior,
authorization policy, provider SDK integration, SQL execution, database access,
network access, credential access, user-data access, package release, tag, or
PyPI publication.

## External Project Chosen

Project: `langchain-ai/langgraph-bigtool`

URL: https://github.com/langchain-ai/langgraph-bigtool

Observed stars: `545`

Reason chosen: `langgraph-bigtool` is a focused LangGraph project for agents
that retrieve and call tools from a tool registry. It is small and
understandable compared with a full framework repository, and its public README
shows a clear tool-registry boundary that DHMS can guard.

## Integration Boundary

The external project pattern is:

```python
tool_registry = {
    tool_id: tool
    for tool_id, tool in discovered_tools.items()
}
```

The DHMS example keeps the integration at that registry boundary.

Minimal integration diff:

```python
from dhms_agentfuse.controlled_proposal_gate import evaluate_controlled_proposal

tool_registry = {
    tool_name: dhms_guard_tool(tool_name, tool)
    for tool_name, tool in tool_registry.items()
}
```

Approximate integration line count: `7`

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

`DHMS_EXTERNAL_LANGGRAPH_BIGTOOL_INTEGRATION_EXAMPLE_PASS`

## Preserved Boundaries

v3.5.1 preserves the v3.4.x proof boundary:

* no production runtime
* no authorization policy
* no provider SDK
* no SQLDatabaseToolkit
* no PythonREPLTool
* no network calls during validation
* no SQL execution
* no database access
* no environment access
* no credential access
* no user-data access
* no protected payload body execution
* no real model API behavior
* no tag or release

## Next Milestone

`v3.5.2 Public post / external feedback trigger`

Final document verdict:

`READY_FOR_V3_5_2_PUBLIC_POST_AND_EXTERNAL_FEEDBACK_TRIGGER`
