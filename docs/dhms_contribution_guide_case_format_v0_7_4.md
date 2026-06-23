# DHMS Contribution Guide / Case Format v0.7.4

## Purpose

v0.7.4 defines contribution and case-format guidance for DHMS AgentFuse.

The purpose is to make DHMS safer to extend. Contributors must define expected
behavior before implementation. A case is a safety contract, not a shortcut to
new execution capability.

This phase is documentation-only. It does not add runtime behavior, execution
capability, benchmark cases, adapters, or new SQL execution paths.

## Contribution Principles

Every new DHMS case must specify expected decision behavior, expected execution
behavior, expected trace evidence, and not-claimed boundaries before
implementation.

Adding a case is not permission to add an execution path.

Core principles:

* fail closed by default
* no new execution path without explicit phase approval
* adding a case does not authorize execution
* every case must specify expected decision behavior
* every case must specify expected execution behavior
* every case must specify trace expectations
* every case must specify not-claimed boundaries
* unsupported categories remain blocked or fail-closed
* design-only docs must be clearly marked as design-only
* README License and Trademark Notice should not be modified casually

## Case Categories

DHMS contribution cases should use one of these categories:

* Protocol case: documents protocol object or lifecycle expectations.
* Benchmark case: adds or proposes deterministic benchmark inputs and expected
  outcomes.
* Trace expectation case: defines required trace fields and expected values.
* Risk-tier policy case: maps a proposal to the DHMS Risk-Tiered Fuse Policy.
* Future fuse-line proposal: describes a future proof line before
  implementation.
* Design-only comparison/policy case: clarifies positioning or policy without
  executable behavior.
* Runtime implementation case: proposes executable behavior.

Runtime implementation cases require explicit phase approval and must not be
introduced casually.

## DHMS Case Format

Suggested case object format:

```json
{
  "case_id": "string",
  "case_version": "string",
  "title": "string",
  "category": "protocol_case | benchmark_case | trace_expectation_case | risk_tier_policy_case | future_fuse_line_proposal | design_only_comparison_policy_case | runtime_implementation_case",
  "risk_domain": "string",
  "risk_tier": "L0 | L1 | L2 | L3 | L4 | not_applicable",
  "proposal_class": "string",
  "input_summary": "string",
  "payload_kind": "string",
  "expected_safety_decision": "string",
  "expected_gate_state": "string",
  "expected_release_eligible": false,
  "expected_direct_execution_allowed": false,
  "expected_executed": false,
  "expected_trace_fields": ["string"],
  "expected_not_claimed_scope": ["string"],
  "linked_proof_or_reference": "string",
  "implementation_status": "documented_only",
  "notes": "string"
}
```

`expected_executed` must default to `false` unless a phase explicitly
authorizes controlled release. `expected_direct_execution_allowed` must default
to `false`.

Allowed `implementation_status` values:

* `documented_only`
* `benchmark_only`
* `example_only`
* `minimal_api_shape`
* `controlled_release_proof`
* `future_not_implemented`

## Benchmark Case Format

DHMS-AgentFuse-Bench cases should be deterministic and evidence-bounded.

Benchmark cases should include:

* deterministic inputs
* deterministic expected decisions
* no secrets
* no customer data
* no production resources
* no real tool invocation
* no hidden execution path
* explicit expected counts
* explicit failed check behavior
* linked proof when relevant

Benchmark runners should be non-executing unless a phase explicitly authorizes
a controlled-release proof.

## Trace Expectation Format

Trace expectations should cover these DHMS AgentFuse protocol objects:

* `RuntimeRequest`
* `ToolCallProposal`
* `SafetyDecision`
* `ExecutionGateDecision`
* `AgentFuseTrace`

Required defaults:

* `executed=false` by default
* `execution_result=null` by default
* `direct_execution_allowed=false` by default
* `execution_allowed=false` unless explicitly authorized
* trace must include protocol version or protocol reference
* trace must avoid secrets, credentials, customer data, and production data

Trace expectations should describe both required fields and values that must
remain false for non-executing paths.

## Risk-Tier Expectation Format

Risk-tier expectations should use the v0.7.2 DHMS Risk-Tiered Fuse Policy
model:

* L0 Observed / No Gate
* L1 Fast Pass
* L2 Constrained Read / Constrained Action
* L3 Hold / Sandbox / Review
* L4 Block / Fail-Closed

Read-only is not automatically safe. Low-risk fast path is still a DHMS
decision, not a bypass of DHMS. Unknown or unsupported actions fail closed by
default.

Risk-tier expectations should state:

* proposed tier
* reason for the tier
* expected fuse behavior
* expected trace evidence
* current implementation status

## Future Fuse-Line Proposal Format

A future fuse line should be proposed before implementation.

Required fields:

```json
{
  "fuse_line_name": "string",
  "risk_category": "string",
  "threat_model_summary": "string",
  "expected_allowed_path": "string",
  "expected_blocked_path": "string",
  "expected_trace_contract": "string",
  "expected_verification_method": "string",
  "sandbox_or_simulation_boundary": "string",
  "non_execution_guarantees": ["string"],
  "not_claimed_scope": ["string"],
  "required_validation": ["string"],
  "rollback_or_freeze_plan": "string"
}
```

The v0.8 preferred future fuse line remains File Operation Safety Fuse. A
future fuse-line proposal does not authorize implementation by itself.

## Contribution Checklist

Before proposing or merging a DHMS contribution, answer:

* Does this change add execution capability?
* Does this change add or expand an execution path?
* Does this change modify SQL allowlist behavior?
* Does this change import `sqlite3`?
* Does this change add OpenClaw/DeepSeek/provider SDK/agent SDK/HTTP/file/shell/MCP integration?
* Does this change touch production checker/runner/schema/taxonomy?
* Does this change alter v0.6.1 benchmark semantics?
* Does this change alter v0.6.2 CLI demo semantics?
* Does this change alter v0.6.3 minimal API semantics?
* Does this change alter v0.7.1 examples semantics?
* Does this change alter v0.7.2 risk-tiered policy semantics?
* Does this change alter v0.7.3 landscape comparison semantics?
* Does this change modify License or Trademark Notice?
* Are new claims bounded by evidence?
* Are not-claimed boundaries preserved?
* Are validation commands listed?

## Safe Contribution Examples

Examples of safer contributions:

* fixing typos
* adding docs links
* adding non-executing examples
* adding static trace examples
* adding design-only policy discussion
* improving README clarity
* adding benchmark case proposals without implementation

## High-Risk Contribution Examples

Examples of high-risk contributions:

* adding `execute` functions
* adding real adapters
* adding SQL execution paths
* importing `sqlite3` outside an approved proof path
* adding file/shell/HTTP/MCP integration
* adding provider SDK integration
* claiming production readiness
* modifying License or Trademark Notice
* adding customer data or secrets
* expanding allowlists without approval

## Not Claimed

v0.7.4 does not claim:

* arbitrary SQL support
* direct SQL execution
* mutation SQL execution
* production DB safety
* production SQL agent support
* user data safety
* credentialed DB execution
* network DB execution
* OpenClaw runtime integration
* DeepSeek/provider integration
* provider SDK integration
* agent SDK integration
* HTTP adapter
* file adapter
* shell adapter
* MCP integration
* MCP replacement
* a production SDK
* a production-ready agent runtime
* universal agent safety
* an industry standard

## Next Milestone

Recommended next milestone:

`v0.7.5 Fresh Clone Reproduction Check`

Final document verdict:

`READY_FOR_V0_7_5_FRESH_CLONE_REPRODUCTION_CHECK`
