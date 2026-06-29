# DHMS Guard Demo Based on the langgraph-bigtool Tool Registry Pattern

This example shows how DHMS AgentFuse can guard a `langgraph-bigtool`-style
tool registry shape with a small code change.

This example mirrors the `langgraph-bigtool` tool registry shape; it does not
import or run `langgraph_bigtool` itself.

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

`DHMS_LANGGRAPH_BIGTOOL_REGISTRY_PATTERN_DEMO_PASS`

This example does not import `langgraph_bigtool`, call model providers, perform
network requests, execute SQL, access a database, read environment variables,
read credentials, read user data, or authorize protected payload execution.
