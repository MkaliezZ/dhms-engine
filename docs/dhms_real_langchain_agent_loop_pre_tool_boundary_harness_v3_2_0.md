# DHMS Real LangChain Agent Loop Pre-Tool Boundary Harness v3.2.0

## 1. Title and Metadata

* Milestone: `v3.2.0 Real LangChain Agent Loop Pre-Tool Boundary Harness`
* Status: real LangChain agent loop reaches guarded pre-tool boundary
* Previous milestone: `v3.1.2 Real LangChain Pre-Tool Interception Result Review + README Sync`
* Next milestone: `v3.2.1 Real LangChain Agent Loop Boundary Validation`
* Reasoning level: Super High

## 2. Purpose

v3.2.0 implements the first DHMS real LangChain agent-loop pre-tool boundary
harness. It proves that a real LangChain agent loop can be invoked, can reach a
real LangChain tool invocation boundary, and can run a DHMS guard before the
protected tool payload body.

## 3. Why v3.2.0 Is Not Planning-Only

v3.2.0 is not planning-only. It invokes a real LangChain `create_agent` loop
using a deterministic local fake model and a real LangChain tool wrapper. The
proof is not merely object construction, not only `AIMessage` parsing, and not
only inert fixture evaluation.

## 4. What Real Agent Loop Boundary Means

For v3.2.0, real agent loop boundary means:

* a real LangChain agent object is created with `create_agent`
* the agent loop is invoked through the LangChain graph
* the local fake model emits a tool call
* LangChain routes that tool call into the registered tool wrapper
* the wrapper calls DHMS before the protected payload body
* the protected payload body remains unexecuted

## 5. Deterministic Fake Model Role

The fake/local model is used only as a deterministic driver. It emits one tool
call to `dangerous_sql_mutation_tool` and then returns a final local response.
It does not call a model provider.

## 6. Guarded Tool Wrapper Design

The guarded tool wrapper:

* increments `guarded_tool_wrapper_invocation_count`
* marks the LangChain tool invocation boundary as reached
* constructs a DHMS controlled proposal for `sql_mutation`
* invokes `evaluate_controlled_proposal`
* records `gate_decision=FAIL_CLOSED`
* records `blocked_capabilities=["sql_mutation"]`
* returns a deterministic blocked result to LangChain
* does not call the protected payload body when execution is not authorized

## 7. Protected Payload Body and Side-Effect Sentinel

The protected payload body is callable and executable in principle. If it ever
ran, it would increment:

* `protected_payload_body_invocation_count`
* `side_effect_sentinel`

The v3.2.0 critical invariant is:

```text
side_effect_sentinel_before=0
side_effect_sentinel_after=0
side_effect_sentinel_delta=0
protected_payload_body_invocation_count=0
protected_tool_body_executed=false
```

## 8. Agent Loop Execution Path

Execution path:

1. Create boundary state.
2. Create guarded LangChain tool wrapper.
3. Create deterministic local fake message model.
4. Create real LangChain agent through `create_agent`.
5. Invoke the real LangChain agent loop.
6. LangChain routes the model tool call to the guarded wrapper.
7. DHMS guard evaluates the proposal before protected payload execution.
8. Gate fails closed for `sql_mutation`.
9. Protected payload body is not called.

## 9. Validation Output

Primary validation command:

```bash
/usr/local/bin/python3.11 validation/run_dhms_langchain_agent_loop_pre_tool_boundary_harness_v0.py
```

Expected pass marker:

```text
DHMS_REAL_LANGCHAIN_AGENT_LOOP_PRE_TOOL_BOUNDARY_HARNESS_PASS
```

Expected critical output:

```text
agent_loop_invoked=true
langchain_tool_invocation_boundary_reached=true
langchain_tool_wrapper_invoked=true
dhms_pre_tool_guard_invoked=true
protected_tool_was_executable=true
protected_tool_body_executed=false
side_effect_sentinel_before=0
side_effect_sentinel_after=0
side_effect_sentinel_delta=0
guarded_tool_wrapper_invocation_count=1
dhms_guard_invocation_count=1
protected_payload_body_invocation_count=0
gate_decision=FAIL_CLOSED
blocked_capabilities=sql_mutation
execution_authorized=false
runtime_behaviors_added=0
```

## 10. Safety Invariants

v3.2.0 preserves:

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

## 11. What v3.2.0 Adds

v3.2.0 adds:

* a real LangChain agent-loop boundary harness
* a guarded LangChain tool wrapper
* a protected payload body behind the DHMS guard
* a side-effect sentinel proof
* a deterministic local validation script
* one local example fixture for the dangerous SQL mutation tool call

## 12. What v3.2.0 Does Not Add

v3.2.0 does not add:

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

v3.2.0 may claim only:

DHMS has a local deterministic real LangChain agent loop harness where a real
LangChain agent loop is invoked, a fake/local model deterministically emits a
tool call, the loop reaches a real LangChain tool invocation boundary, a DHMS
pre-tool guard runs before the protected payload body, the gate fails closed
for a dangerous `sql_mutation` proposal, and the protected payload body does
not execute as proven by `side_effect_sentinel_after=0`.

## 14. Explicit Non-Claims

v3.2.0 does not claim:

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

Expected files:

* `dhms_agentfuse/langchain_agent_loop_boundary.py`
* `validation/run_dhms_langchain_agent_loop_pre_tool_boundary_harness_v0.py`
* `examples/langchain_agent_loop/dangerous_sql_mutation_tool_call.json`
* `docs/dhms_real_langchain_agent_loop_pre_tool_boundary_harness_v3_2_0.md`
* `docs/dhms_agentfuse_protocol_package_index_v0_7_0.md`
* `docs/dhms_agentfuse_development_roadmap.md`

## 16. Files Intentionally Not Modified

v3.2.0 intentionally does not modify:

* `README.md`
* `requirements.txt`
* `dhms_agentfuse/langchain_interception.py`
* `dhms_agentfuse/controlled_proposal_gate.py`
* existing v3.1 validators
* `cli.py`
* existing LangChain interception examples
* proposal examples
* v3.1 result review docs
* v3.0 docs
* v2.7/v2.8/v2.9 frozen evidence
* schemas
* release or tag files

## 17. Validation Commands

Validation commands:

```bash
/usr/local/bin/python3.11 -m pip install --user -r requirements.txt
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

v3.2 must stay to exactly this three-step line unless a correction is strictly
necessary:

1. `v3.2.0 Real LangChain Agent Loop Pre-Tool Boundary Harness`
2. `v3.2.1 Real LangChain Agent Loop Boundary Validation`
3. `v3.2.2 Real LangChain Agent Loop Boundary Result Review + README Sync`

Next required milestone:

`v3.2.1 Real LangChain Agent Loop Boundary Validation`

## 19. Final Verdict

`READY_FOR_V3_2_1_REAL_LANGCHAIN_AGENT_LOOP_BOUNDARY_VALIDATION`
