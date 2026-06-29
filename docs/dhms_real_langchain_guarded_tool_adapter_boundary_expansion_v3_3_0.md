# DHMS Real LangChain Guarded Tool Adapter Boundary Expansion v3.3.0

## 1. Title and Metadata

* Milestone: `v3.3.0 Real LangChain Guarded Tool Adapter Boundary Expansion`
* Status: reusable guarded LangChain tool adapter boundary over multiple local deterministic scenarios
* Previous milestone: `v3.2.2 Real LangChain Agent Loop Boundary Result Review + README Sync`
* Next milestone: `v3.3.1 Real LangChain Guarded Tool Adapter Boundary Validation`
* Reasoning level: Super High

## 2. Purpose

v3.3.0 expands DHMS from one hard-coded guarded LangChain tool boundary into a
reusable guarded LangChain tool adapter boundary. It proves that multiple local
executable payload bodies can be wrapped by a shared adapter that routes real
LangChain agent-loop tool invocations through DHMS before protected payload
execution.

## 3. Why v3.3.0 Is Adapter Expansion, Not Planning

v3.3.0 is not planning-only and not README-only. It adds a reusable local
adapter module, three inert local scenarios, and a validator that invokes a
real LangChain agent loop for each scenario.

## 4. v3.2 Boundary Carried Forward

v3.2 proved that a real LangChain agent loop can reach a guarded tool wrapper,
invoke the DHMS pre-tool guard, fail closed for `sql_mutation`, and keep the
protected payload body unexecuted with `side_effect_sentinel_after=0`.

v3.3.0 carries that boundary forward into a reusable adapter shape.

## 5. Guarded Tool Adapter Design

The adapter exposes:

* `create_guarded_tool_adapter_state`
* `build_controlled_proposal_from_tool_metadata`
* `create_guarded_langchain_tool_adapter`
* `create_deterministic_adapter_driver`
* `run_guarded_tool_adapter_scenario`
* `run_guarded_tool_adapter_scenarios`

For each LangChain tool invocation, the adapter increments adapter/tool wrapper
counters, builds a DHMS controlled proposal from tool metadata, invokes
`evaluate_controlled_proposal`, records gate evidence, and only calls the
protected payload body if DHMS explicitly authorizes execution.

Current gate behavior preserves `execution_authorized=false`, so no protected
payload body executes in v3.3.0.

## 6. Scenario Matrix

| Scenario | Expected decision | Boundary |
| --- | --- | --- |
| `safe_read_only_summary_tool` | `RELEASE_CANDIDATE` | payload not executed, sentinel=0 |
| `dangerous_sql_mutation_tool` | `FAIL_CLOSED` | `sql_mutation` blocked, payload not executed, sentinel=0 |
| `model_api_request_tool` | `FAIL_CLOSED` | `model_api` blocked, payload not executed, sentinel=0 |

## 7. Real LangChain Agent Loop Path

Each scenario:

1. loads a local inert scenario JSON file
2. creates adapter state
3. creates a real LangChain tool through the guarded adapter
4. creates a deterministic fake/local model that emits the target tool call
5. creates a real LangChain agent with `create_agent`
6. invokes the real agent loop with `agent.invoke(...)`
7. routes the tool call through the adapter-created LangChain tool
8. records DHMS guard, gate, and sentinel evidence

## 8. Sentinel and Protected Payload Body Design

Each scenario has a callable protected payload body. If a body were called, it
would increment `protected_payload_body_invocation_count`, increment
`side_effect_sentinel`, and set `protected_tool_body_executed=true`.

v3.3.0 requires every scenario to preserve:

```text
protected_tool_body_executed=false
protected_payload_body_invocation_count=0
side_effect_sentinel_before=0
side_effect_sentinel_after=0
side_effect_sentinel_delta=0
```

## 9. Validation Output

Validation command:

```bash
/usr/local/bin/python3.11 validation/run_dhms_langchain_guarded_tool_adapter_boundary_v0.py
```

Expected pass marker:

```text
DHMS_REAL_LANGCHAIN_GUARDED_TOOL_ADAPTER_BOUNDARY_EXPANSION_PASS
```

Expected summary:

```text
validated_adapter_scenarios=3
release_candidate=1
fail_closed=2
all_tool_boundaries_reached=true
all_guarded_adapters_invoked=true
all_dhms_guards_invoked=true
all_protected_tool_body_executed_false=true
all_side_effect_sentinel_after_zero=true
all_protected_payload_body_invocation_count_zero=true
all_execution_authorized_false=true
all_runtime_behaviors_added_zero=true
sentinel_failure_count=0
protected_payload_body_execution_count=0
runtime_behaviors_added=0
```

## 10. Safety Invariants

v3.3.0 preserves:

* no SQL execution
* no DB access
* no model provider call
* no network behavior
* no subprocess or shell behavior
* no environment access
* no credential access
* no user-data access
* no file mutation
* no protected payload body execution

## 11. What v3.3.0 Adds

v3.3.0 adds:

* a reusable guarded LangChain tool adapter boundary
* DHMS proposal construction from local tool metadata
* three local deterministic adapter scenarios
* a validator for real LangChain agent-loop adapter routing
* package index and roadmap updates for v3.3.0

## 12. What v3.3.0 Does Not Add

v3.3.0 does not add:

* README sync
* dependency changes
* provider SDKs
* SQLDatabaseToolkit
* PythonREPLTool
* requests tool
* network tool
* database driver
* real SQL execution
* DB connection
* schema introspection
* result readback from DB/tool runtime
* subprocess or shell behavior
* environment access
* credential access
* user-data access
* file mutation
* KerniQ integration
* E2B integration
* MCP integration
* release or tag

## 13. Public Claim Boundary

v3.3.0 may claim only:

DHMS now has a reusable local deterministic real LangChain guarded tool adapter
boundary that wraps multiple executable local payload bodies, routes real
LangChain agent-loop tool invocations through DHMS before protected payload
execution, preserves `execution_authorized=false` and
`runtime_behaviors_added=0`, fails closed for dangerous `sql_mutation` and
`model_api` proposals, returns release-candidate for a safe read-only proposal
without executing payload, and proves all protected payload bodies remain
unexecuted by sentinel/count assertions.

## 14. Explicit Non-Claims

v3.3.0 does not claim:

* production readiness
* arbitrary production LangChain agent protection
* arbitrary real-world agent protection
* real SQLDatabaseToolkit protection
* real SQL execution safety
* real DB protection
* model provider safety
* credential safety
* user-data safety
* network safety
* general tool execution support
* release readiness
* industry standardization

## 15. Files Changed

v3.3.0 changes:

* `dhms_agentfuse/langchain_guarded_tool_adapter.py`
* `validation/run_dhms_langchain_guarded_tool_adapter_boundary_v0.py`
* `examples/langchain_guarded_tool_adapter/safe_read_only_summary_tool_call.json`
* `examples/langchain_guarded_tool_adapter/dangerous_sql_mutation_tool_call.json`
* `examples/langchain_guarded_tool_adapter/model_api_request_tool_call.json`
* `docs/dhms_real_langchain_guarded_tool_adapter_boundary_expansion_v3_3_0.md`
* `docs/dhms_agentfuse_protocol_package_index_v0_7_0.md`
* `docs/dhms_agentfuse_development_roadmap.md`

## 16. Files Intentionally Not Modified

v3.3.0 intentionally does not modify:

* `README.md`
* `requirements.txt`
* v3.2 harness module
* v3.2 validators
* v3.1 validators
* `cli.py`
* `dhms_agentfuse/controlled_proposal_gate.py`
* existing examples
* frozen evidence docs
* schemas
* release or tag files

## 17. Validation Commands

```bash
/usr/local/bin/python3.11 -m pip install --user -r requirements.txt
/usr/local/bin/python3.11 validation/run_dhms_langchain_guarded_tool_adapter_boundary_v0.py
/usr/local/bin/python3.11 validation/run_dhms_langchain_agent_loop_boundary_validation_v0.py
/usr/local/bin/python3.11 validation/run_dhms_langchain_agent_loop_pre_tool_boundary_harness_v0.py
/usr/local/bin/python3.11 validation/run_dhms_langchain_dependency_and_agent_harness_validation_v0.py
/usr/local/bin/python3.11 validation/run_dhms_langchain_interception_smoke_v0.py
/usr/local/bin/python3.11 validation/run_dhms_local_controlled_proposal_gate_cli_trace_validation_v0.py
/usr/local/bin/python3.11 cli.py gate-proposal examples/proposals/safe_read_only_summary.json
/usr/local/bin/python3.11 cli.py gate-proposal examples/proposals/drop_table.json
/usr/local/bin/python3.11 cli.py gate-proposal examples/proposals/model_api_request.json
/usr/local/bin/python3.11 validation/run_dhms_controlled_proposal_replay_evidence_validation_v0.py
/usr/local/bin/python3.11 validation/run_dhms_controlled_agent_proposal_gate_fixture_validation_v0.py
git diff --check
git diff --cached --check
```

## 18. Next Milestones

v3.3 must stay to exactly this three-step line unless a correction is strictly
necessary:

1. `v3.3.0 Real LangChain Guarded Tool Adapter Boundary Expansion`
2. `v3.3.1 Real LangChain Guarded Tool Adapter Boundary Validation`
3. `v3.3.2 Real LangChain Guarded Tool Adapter Boundary Result Review + README Sync`

## 19. Final Verdict

`READY_FOR_V3_3_1_REAL_LANGCHAIN_GUARDED_TOOL_ADAPTER_BOUNDARY_VALIDATION`
