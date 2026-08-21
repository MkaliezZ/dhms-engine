# AgentFuse Five-Minute Trial

This trial verifies the core AgentFuse pre-dispatch behavior with two local,
synthetic tool calls. It requires Python 3.10 or later and does not require an
LLM provider, API key, network service, database, or real filesystem action.
It is designed as an install-copy-run path that fits within five minutes after
Python is ready; this is a documentation target, not an externally measured
timing result.

## 1. Installation

Create or activate a Python environment, then install the public package:

```bash
pip install dhms-agentfuse
```

## 2. Minimal Example

Save the following as `trial.py`:

```python
from dhms_agentfuse import RuntimeGuard, ToolCallRequest

handler_counts = {"read_project_summary": 0, "delete_file": 0}


def read_project_summary(project: str) -> str:
    handler_counts["read_project_summary"] += 1
    return f"summary:{project}"


def delete_file(path: str) -> str:
    handler_counts["delete_file"] += 1
    return f"synthetic-delete:{path}"


guard = RuntimeGuard(
    allow_tools={"read_project_summary"},
    deny_tools={"delete_file"},
    default_action="block",
)

allowed = guard.invoke(
    tool_call=ToolCallRequest(
        tool_call_id="call-allow-001",
        tool_name="read_project_summary",
        arguments={"project": "demo"},
    ),
    handler=read_project_summary,
)
blocked = guard.invoke(
    tool_call=ToolCallRequest(
        tool_call_id="call-block-001",
        tool_name="delete_file",
        arguments={"path": "synthetic-example.txt"},
    ),
    handler=delete_file,
)

for result in (allowed, blocked):
    print(
        f"{result.tool_name}: decision={result.decision} "
        f"outcome={result.outcome} "
        f"handler_started={str(result.handler_started).lower()}"
    )

print(f"allowed_handler_count={handler_counts['read_project_summary']}")
print(f"blocked_handler_count={handler_counts['delete_file']}")

assert allowed.decision == "allow"
assert allowed.outcome == "executed"
assert handler_counts["read_project_summary"] == 1

assert blocked.decision == "block"
assert blocked.outcome == "not_executed"
assert blocked.handler_started is False
assert handler_counts["delete_file"] == 0
assert blocked.evidence.non_execution is not None
assert blocked.evidence.non_execution.execution == "not_started"
```

Run it:

```bash
python trial.py
```

The handlers only update local in-memory counters. Despite its name, the
synthetic `delete_file` handler performs no file operation, and policy prevents
that handler from starting.

## 3. Expected Evidence

Expected output:

```text
read_project_summary: decision=allow outcome=executed handler_started=true
delete_file: decision=block outcome=not_executed handler_started=false
allowed_handler_count=1
blocked_handler_count=0
```

The output and assertions verify three separate lifecycle facts:

- **Decision:** the read action receives `allow`; the synthetic delete action
  receives `block`.
- **Execution outcome:** the allowed handler returns `executed`; the blocked
  call returns `not_executed`, not an execution failure.
- **Handler execution:** the allowed handler runs once, while the blocked
  handler count remains zero and its non-execution evidence records
  `execution=not_started`.

`RuntimeGuardResult.to_safe_dict()` can serialize the terminal receipt without
including the handler return value. The evidence record retains the tool-call
identity, policy decision, reason code, and safe argument digest.

## 4. Validation Purpose

This trial demonstrates, on the explicit guarded invocation path:

- a policy decision is made before protected handler dispatch;
- the execution boundary prevents a blocked handler from starting; and
- the same control path generates structured decision and non-execution
  evidence.

The trial does not demonstrate production readiness, universal interception,
provider integration, sandboxing, or external adoption. An integrating runtime
still owns trusted inputs, approval, persistence, physical outcomes, retries,
and recovery.

For a real LangGraph `ToolNode` trial, use the existing
[v3.7.1 integration guide](dhms_agentfuse_five_minute_integration_trial_v3_7_1.md).
Developers evaluating their own runtime can continue with the
[Early Validation Program](agentfuse_early_validation_program.md).
