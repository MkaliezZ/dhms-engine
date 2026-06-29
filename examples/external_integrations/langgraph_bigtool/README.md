# DHMS Real langgraph-bigtool API Wiring Demo

This example shows how DHMS AgentFuse can guard a `langgraph-bigtool` tool
registry with a small code change while using the real `langgraph_bigtool`
`create_agent` API.

This is real `create_agent` wiring, not a full live production agent run. The
demo builds a DHMS-guarded `tool_registry`, passes it into
`langgraph_bigtool.create_agent()`, supplies a deterministic
`retrieve_tools_function`, and does not compile, invoke, or stream the agent
graph.

External project:

* Project: `langchain-ai/langgraph-bigtool`
* URL: https://github.com/langchain-ai/langgraph-bigtool
* Observed stars: `545`
* Reason chosen: it is a small, understandable LangGraph project focused on
  agent access to many tools through a tool registry, not a huge framework repo.

## Before / After

Before:

```python
tool_registry = {
    "safe_read_only_summary_tool": safe_read_only_summary_tool,
    "dangerous_sql_mutation_tool": dangerous_sql_mutation_tool,
    "model_api_request_tool": model_api_request_tool,
}
```

The agent/tool path can reach every registered tool, including dangerous tools.

After:

```python
from dhms_agentfuse.controlled_proposal_gate import evaluate_controlled_proposal

tool_registry = {
    tool_name: dhms_guard_tool(tool_name, tool)
    for tool_name, tool in tool_registry.items()
}
```

The guard point is the tool registry boundary. DHMS observes each tool proposal
before protected payload execution, returns `RELEASE_CANDIDATE` for the safe
read-only tool, returns `FAIL_CLOSED` for dangerous SQL mutation and model API
tools, and keeps all protected payload bodies unexecuted.

Run the deterministic local demo:

```bash
/usr/local/bin/python3.11 examples/external_integrations/langgraph_bigtool/dhms_guarded_tool_registry_demo.py
```

Expected final verdict:

`DHMS_REAL_LANGGRAPH_BIGTOOL_API_WIRING_DEMO_PASS`

This example does not call model providers, perform network requests, execute
SQL, access a database, use semantic search, use embeddings, use LangGraph
Store, read environment variables, read credentials, read user data, or
authorize protected payload execution.
