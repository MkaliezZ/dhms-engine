# DHMS Mock Agent Runtime Interception Proof Planning v0.10.0

## Purpose

v0.10.0 plans the Mock Agent Runtime Interception Proof line.

The goal is to define how DHMS can prove deterministic mock-agent runtime
interception for existing SQL, File, and HTTP tool-call proposals without
connecting to a real agent runtime or adding new execution capability.

This milestone is planning-only. It does not add a runner, manifest, examples,
trace examples, CLI command, source code, execution behavior, real LLM
integration, Codex integration, Claude integration, OpenClaw integration,
DeepSeek integration, MCP integration, E2B integration, real agent runtime,
real user data, or production runtime claim.

## Core Claim to Plan

A deterministic mock agent generates SQL/File/HTTP tool-call proposals. DHMS
intercepts those proposals, assigns safety decisions, applies execution gates,
returns agent runtime results, prevents rejected actions from executing, and
allows approved candidates only through existing constrained proof paths.

This is the planned v0.10 proof claim. v0.10.0 does not implement it.

## Deterministic Mock Agent Boundary

The mock agent must be deterministic, local, synthetic, and data-only.

The mock agent boundary for future v0.10 proof phases should include:

* fixed mock-agent identity
* fixed run IDs
* fixed proposal IDs
* fixed SQL/File/HTTP proposal sequence
* no model call
* no hidden reasoning dependency
* no external agent runtime
* no provider SDK
* no agent SDK
* no network dependency
* no production resource
* no user data
* no credentials

The mock agent must not execute tools. It only emits inert tool-call proposal
objects that DHMS can intercept.

## Mock Agent Tool-Call Proposal Schema

Future v0.10.1 manifest work should define proposal objects with fields such as:

* `mock_agent_run_id`
* `mock_agent_id`
* `proposal_id`
* `proposal_sequence_index`
* `proposal_type`
* `tool_name`
* `tool_family`
* `intent_summary`
* `payload`
* `expected_safety_decision`
* `expected_gate_state`
* `expected_agent_runtime_result`
* `expected_executed`
* `expected_direct_execution_allowed`
* `expected_constrained_proof_path`
* `expected_trace_fields`
* `not_claimed_scope`

Allowed `proposal_type` values for v0.10 planning are only:

* `SQL`
* `File`
* `HTTP`

No other proposal type is in scope for v0.10.

## SQL/File/HTTP-Only Scope

v0.10 planning may reference only the existing proof-line families:

* SQL proposals mapped to the SQL Sandbox Execution Fuse evidence line.
* File proposals mapped to the File Operation Safety Fuse evidence line.
* HTTP proposals mapped to the HTTP / Network Request Safety Fuse evidence line.

The planned mock agent must not introduce a new proof family. It should only
show how DHMS intercepts already-understood proposal families at an agent
runtime boundary.

## Forbidden Proposal Types

The following proposal types are explicitly out of scope:

* Shell
* Browser
* Email
* Git
* Docker
* E2B
* MCP
* Cloud
* API client
* Real database adapter
* Real agent SDK
* Arbitrary tool execution

Any future appearance of these categories in a v0.10 manifest should be treated
as unsupported, blocked, or fail-closed unless a later explicit phase changes
scope.

## DHMS Interception Lifecycle

The planned interception lifecycle is:

1. A deterministic mock agent emits an inert SQL/File/HTTP tool-call proposal.
2. DHMS captures the proposal before any tool execution.
3. DHMS normalizes the proposal into an observable proposal record.
4. DHMS assigns a safety decision.
5. DHMS applies an execution gate.
6. DHMS returns an agent runtime result to the mock agent.
7. Rejected proposals return blocked or fail-closed runtime results and do not
   execute.
8. Approved candidates may proceed only through existing constrained proof
   paths.
9. DHMS records trace evidence for every proposal.

The lifecycle must prove interception before execution, not after-the-fact
logging.

## Mapping to DHMS Execution Fuse Protocol v0.6.0

The v0.10 mock-agent planning line maps to the v0.6.0 protocol objects:

| v0.6.0 protocol object | v0.10 planned mock-agent mapping |
| --- | --- |
| `RuntimeRequest` | Mock agent run event and proposal emission context |
| `ToolCallProposal` | Deterministic SQL/File/HTTP proposal object |
| `SafetyDecision` | DHMS decision for the intercepted proposal |
| `ExecutionGateDecision` | Gate result before tool execution |
| `BridgeDecision` / `ReleaseReview` | Existing constrained proof path when a candidate is eligible |
| `ReleaseAuthorization` | Existing explicit constrained authorization where applicable |
| `SandboxExecutionResult` / proof result | Existing SQL/File/HTTP constrained proof result only |
| `ExternalStateVerification` | Existing verification evidence for approved constrained proofs |
| `ExecutionTrace` | End-to-end mock-agent interception trace |

v0.10 must not redefine the DHMS Execution Fuse Protocol. It should show how
the existing protocol applies at a mock agent runtime boundary.

## Expected v0.10.1 Manifest Scope

v0.10.1 should add a static mock agent tool-call proposal manifest.

Expected scope:

* SQL/File/HTTP proposal objects only
* deterministic mock-agent run metadata
* expected DHMS decisions
* expected gate states
* expected mock-agent runtime results
* expected execution flags
* expected trace fields
* no source code behavior
* no runner
* no examples
* no CLI command
* no real agent runtime

## Expected v0.10.2 Non-Executing Benchmark Scope

v0.10.2 should add a non-executing benchmark over the static v0.10.1 manifest.

Expected scope:

* load the committed static manifest
* validate SQL/File/HTTP-only proposal scope
* validate expected decisions and gate states
* validate rejected proposals remain non-executing
* validate approved candidates are only linked to existing constrained proof
  paths
* validate deterministic mock-agent runtime result expectations
* produce deterministic metrics
* no execution behavior
* no real agent runtime
* no new proof behavior

## Expected v0.10.3 Examples and Trace Scope

v0.10.3 should add non-executing examples and trace examples.

Expected scope:

* static SQL/File/HTTP interception examples
* mock-agent proposal examples
* safety decision examples
* gate decision examples
* mock-agent runtime result examples
* trace examples
* no real agent runtime
* no model invocation
* no tool execution
* no new CLI command unless explicitly approved in a later phase

## Expected v0.10.4 Controlled Proof Scope

v0.10.4 may implement a controlled proof only if explicitly approved in that
future phase.

Expected scope:

* deterministic mock-agent run only
* SQL/File/HTTP proposals only
* interception before execution
* rejected proposals do not execute
* approved candidates use only existing constrained proof paths
* no new SQL execution path
* no arbitrary file operation path
* no arbitrary HTTP/network path
* no real LLM
* no real agent SDK
* no MCP/E2B/OpenClaw/DeepSeek integration
* no production data
* no credential handling

## Success Metrics for v0.10.4

Future v0.10.4 success metrics should include:

* `mock_agent_runs_total`
* `tool_call_proposals_total`
* `sql_proposals_total`
* `file_proposals_total`
* `http_proposals_total`
* `unsupported_proposal_type_count`
* `intercepted_before_execution_count`
* `safety_decisions_total`
* `gate_decisions_total`
* `blocked_or_fail_closed_count`
* `approved_constrained_candidates_count`
* `rejected_actions_executed_count`
* `direct_execution_allowed_count`
* `real_agent_runtime_used_count`
* `real_llm_used_count`
* `mcp_integration_used_count`
* `e2b_integration_used_count`
* `openclaw_invoked_count`
* `deepseek_invoked_count`
* `provider_sdk_invoked_count`
* `agent_sdk_invoked_count`
* `credentials_used_count`
* `production_resource_touched_count`
* `trace_records_created_count`
* `failed_checks`

Expected successful values should include:

* `unsupported_proposal_type_count=0`
* `intercepted_before_execution_count=tool_call_proposals_total`
* `rejected_actions_executed_count=0`
* `direct_execution_allowed_count=0`
* `real_agent_runtime_used_count=0`
* `real_llm_used_count=0`
* `mcp_integration_used_count=0`
* `e2b_integration_used_count=0`
* `openclaw_invoked_count=0`
* `deepseek_invoked_count=0`
* `provider_sdk_invoked_count=0`
* `agent_sdk_invoked_count=0`
* `credentials_used_count=0`
* `production_resource_touched_count=0`
* `failed_checks=[]`

## Expected v0.10.5 Freeze Scope

v0.10.5 should review and freeze the v0.10 evidence chain.

Expected scope:

* review v0.10.1 manifest
* review v0.10.2 benchmark
* review v0.10.3 examples and trace examples
* review v0.10.4 controlled proof if explicitly implemented
* confirm SQL/File/HTTP-only proposal scope
* confirm no new proposal family was introduced
* confirm no rejected proposal executed
* confirm no production runtime claim
* freeze non-claims and next-step boundaries

## Frozen Non-Claims

v0.10.0 does not claim:

* production readiness
* real agent runtime interception
* real LLM execution
* Codex integration
* Claude integration
* OpenClaw integration
* DeepSeek integration
* MCP integration
* E2B integration
* provider SDK integration
* agent SDK integration
* shell execution
* browser execution
* email execution
* Git execution
* Docker execution
* cloud execution
* API client execution
* real database adapter support
* arbitrary tool execution
* arbitrary SQL support
* arbitrary file operation support
* arbitrary HTTP/network request support
* production DB safety
* production filesystem safety
* production HTTP safety
* credential handling
* user data safety certification
* universal agent safety
* industry-standard status

## Next Milestone

Recommended next milestone:

`v0.10.1 Static Mock Agent Tool-Call Proposal Manifest`

Final document verdict:

`READY_FOR_V0_10_1_STATIC_MOCK_AGENT_TOOL_CALL_PROPOSAL_MANIFEST`
