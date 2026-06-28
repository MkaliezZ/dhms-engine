# DHMS Real LangChain Dependency and Agent Harness Validation v3.1.1

## 1. Title and Metadata

* Milestone: `v3.1.1 Real LangChain Dependency Lock + Agent Harness Validation`
* Status: real LangChain dependency and agent harness validation
* Previous milestone: `v3.1.0 Real LangChain Agent Interception Minimal Harness`
* Next milestone: `v3.1.2 Real LangChain Pre-Tool Interception Result Review + README Sync`
* Reasoning level: Super High

## 2. Purpose

v3.1.1 turns the v3.1.0 minimal LangChain interception harness into a stricter
dependency-validated line. It adds a minimal dependency lock, validates that
real LangChain can import, validates that `langchain.agents.create_agent` can
create a local agent harness object, and preserves the DHMS pre-execution
boundary.

This milestone does not add production runtime behavior.

## 3. Why v3.1.1 Removes Fallback Pass

v3.1.0 allowed a minimal path that could still demonstrate inert tool-call
normalization when LangChain was unavailable. v3.1.1 removes that as a passing
condition. The strict validation now requires:

* `langchain_available=true`
* `langchain_agent_harness_created=true`
* `real_create_agent_imported=true`
* `real_langchain_agent_object_created=true`
* `real_langchain_ai_message_path_validated=true`

If any of those are false, the v3.1.1 validation fails.

## 4. Dependency Lock

The dependency lock is intentionally minimal:

```text
langchain>=1.0,<2.0
```

No provider extras, SQL toolkits, database drivers, HTTP clients, E2B packages,
MCP packages, KerniQ packages, or model-provider SDKs are added.

Local note: the default `/usr/bin/python3` runtime was Python 3.9.6 and could
not install LangChain 1.x because LangChain 1.x requires Python 3.10 or newer.
The dependency and validation path was completed with `/usr/local/bin/python3.11`.

## 5. Real LangChain Agent Harness Validation

The v3.1.1 harness creates a real LangChain agent object using:

* real `langchain` import
* real `langchain.agents.create_agent`
* real `langchain_core.messages.AIMessage`
* real `FakeMessagesListChatModel`
* inert local tools that raise if executed

The harness uses a fake/local model only. It does not call a model provider.

## 6. Real create_agent Validation

The validation confirms that `create_agent` imports and produces a local agent
object. The observed local object type is expected to be implementation-specific
to the installed LangChain version; in the validated environment it was a
`CompiledStateGraph`.

The object creation validates wiring shape only. It does not invoke the agent,
run a graph, call a model, or execute a tool.

## 7. Real AIMessage Path Validation

The validation constructs a real `AIMessage` containing a sanitized LangChain
tool-call shape and routes the first tool call through DHMS interception.

Only the LangChain tool-call fields are passed into `AIMessage`:

* `id`
* `name`
* `args`
* `type`

The existing DHMS example expectation fields remain static fixture data and are
not passed into the real LangChain message object.

## 8. Interception Validation Summary

The strict validator covers the three existing LangChain interception examples:

* safe read-only summary tool call: `RELEASE_CANDIDATE`
* `DROP TABLE` tool call: `FAIL_CLOSED`
* model API request tool call: `FAIL_CLOSED`

Validated distribution:

* `validated_interceptions=3`
* `release_candidate=1`
* `fail_closed=2`
* `hold_for_review=0`

## 9. Frozen Pass Output

Expected strict validation command:

```bash
/usr/local/bin/python3.11 validation/run_dhms_langchain_dependency_and_agent_harness_validation_v0.py
```

Expected pass marker:

```text
DHMS_REAL_LANGCHAIN_DEPENDENCY_AND_AGENT_HARNESS_VALIDATION_PASS
```

Expected invariant summary:

```text
langchain_available=true
langchain_agent_harness_created=true
real_create_agent_imported=true
real_langchain_agent_object_created=true
real_langchain_ai_message_path_validated=true
validated_interceptions=3
release_candidate=1
fail_closed=2
hold_for_review=0
all_intercepted_before_execution=true
all_tool_execution_attempted_false=true
all_tool_execution_allowed_false=true
all_execution_authorized_false=true
all_runtime_behaviors_added_zero=true
all_gate_results_execution_authorized_false=true
all_gate_results_runtime_behaviors_added_zero=true
all_interception_trace_keys_present=true
all_interception_trace_assertions_true=true
all_tools_not_executed=true
all_model_providers_not_called=true
runtime_behaviors_added=0
```

## 10. Safety Invariants

v3.1.1 preserves these invariants:

* all tool calls are observed before execution
* no tool execution is attempted
* no tool execution is allowed
* no execution is authorized
* no runtime behavior is added
* no model provider is called
* no SQL is executed
* no database is accessed
* no network request is performed
* no subprocess is invoked
* no environment variables are read
* no credentials are accessed
* no user data is accessed

## 11. What v3.1.1 Adds

v3.1.1 adds:

* `requirements.txt` with minimal LangChain dependency lock
* strict dependency and harness validation
* stricter smoke validation that requires real LangChain availability
* trace fields for real `create_agent`, real agent object creation, real
  `AIMessage` path validation, and fake/local model usage
* documentation for the v3.1.1 validated dependency boundary

## 12. What v3.1.1 Does Not Add

v3.1.1 does not add:

* model provider execution
* SQL execution
* database connection
* schema introspection
* SQLDatabaseToolkit integration
* network calls
* subprocess or shell execution
* file mutation
* KerniQ integration
* E2B integration
* MCP integration
* production runtime behavior

## 13. Public Claim Boundary

v3.1.1 may claim that DHMS can validate a real LangChain dependency and create
a minimal local LangChain agent harness object while intercepting inert
tool-call proposals before execution.

v3.1.1 must not claim production agent runtime interception or production
LangChain agent support.

## 14. Explicit Non-Claims

v3.1.1 does not claim:

* production readiness
* real SQL agent execution
* database safety
* arbitrary SQL safety
* arbitrary tool execution support
* model-provider safety
* user data safety
* credential safety
* network safety
* SQLDatabaseToolkit support
* LangChain production adapter support
* E2B integration
* KerniQ integration
* MCP integration
* universal agent safety

## 15. Files Changed

Expected files for this milestone:

* `requirements.txt`
* `dhms_agentfuse/langchain_interception.py`
* `validation/run_dhms_langchain_interception_smoke_v0.py`
* `validation/run_dhms_langchain_dependency_and_agent_harness_validation_v0.py`
* `docs/dhms_real_langchain_dependency_and_agent_harness_validation_v3_1_1.md`
* `docs/dhms_agentfuse_protocol_package_index_v0_7_0.md`
* `docs/dhms_agentfuse_development_roadmap.md`

## 16. Files Intentionally Not Modified

This milestone intentionally does not modify:

* `README.md`
* `cli.py`
* `dhms_agentfuse/controlled_proposal_gate.py`
* `examples/langchain_interception/*.json`
* v3.0 validators and docs
* v2.7/v2.8/v2.9 frozen evidence
* schemas
* release or tag files

## 17. Validation Commands

Validation commands:

```bash
/usr/local/bin/python3.11 -m pip install --user -r requirements.txt
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

## 18. Next Milestone

Next milestone:

`v3.1.2 Real LangChain Pre-Tool Interception Result Review + README Sync`

## 19. Final Verdict

`READY_FOR_V3_1_2_REAL_LANGCHAIN_PRE_TOOL_INTERCEPTION_RESULT_REVIEW_AND_README_SYNC`
