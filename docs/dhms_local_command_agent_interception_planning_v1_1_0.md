# DHMS Local Command-Agent Interception Planning v1.1.0

## Purpose

v1.1.0 opens the planning line for Local Command-Agent Interception.

The purpose is to define how DHMS could treat a local command proposal as an
intercepted agent action before execution. DHMS would capture the proposal,
classify risk, apply fail-closed policy, and produce trace evidence before any
future controlled release path is considered.

This milestone is documentation-only planning. It does not implement command
execution, shell execution, subprocess execution, a command runner, terminal
integration, MCP integration, agent SDK integration, source code changes, or
production runtime behavior.

## Scope

v1.1.0 is limited to planning how DHMS should reason about inert local command
proposals under non-production boundaries.

The planning scope includes:

* command-agent interception as a future DHMS evidence line
* local command proposal capture before execution
* risk classification for command strings and argv-like proposals
* fail-closed behavior for unknown or unsupported proposals
* block/hold/fail-closed decision expectations
* trace evidence expectations
* future controlled-proof boundaries

## Non-Scope

v1.1.0 does not add:

* command execution
* shell execution
* subprocess execution
* command runner behavior
* terminal integration
* MCP integration
* E2B integration
* Codex integration
* Claude integration
* OpenClaw integration
* DeepSeek integration
* provider SDK integration
* agent SDK integration
* credential handling
* user data handling
* production runtime behavior
* arbitrary command support

## Threat Model

Local command proposals can carry high risk even when represented as short text.
The v1.1 threat model includes:

* destructive filesystem operations
* credential or secret access
* user-data access
* environment-variable leakage
* hidden file access
* process spawning
* network side effects
* file redirection and overwrite behavior
* stdin-driven destructive behavior
* command chaining
* shell metacharacter ambiguity
* privilege escalation intent
* production resource access
* unknown or malformed command proposals

v1.1.0 does not implement detection or enforcement for these categories. It
only defines the planning boundary for future inert cases and proofs.

## Local Command Proposal Concept

A local command proposal is an observable intent for an agent to run a local
command. In DHMS planning, the proposal is data first. DHMS should observe and
classify it before any execution boundary is crossed.

The future proposal should be treated as inert unless a later phase explicitly
approves a constrained proof path.

## Proposed Command Proposal Fields

Future local command proposal cases may describe, in prose or inert manifest
data:

* command string
* argv list
* working directory
* environment intent
* stdin intent
* file redirection intent
* network/process side-effect intent
* destructive-operation indicators
* credential/user-data risk indicators
* expected output description
* proposed policy decision
* trace evidence reference

These fields are planning concepts only. v1.1.0 does not create a schema file,
JSON manifest, executable example, runner, or command adapter.

## Fail-Closed Default Rule

Unknown, malformed, unsupported, credential-seeking, destructive, ambiguous, or
side-effectful local command proposals should fail closed unless a later phase
defines a constrained proof path.

Fast paths must still be DHMS decisions. A local command proposal must not
bypass DHMS merely because it appears read-only or simple.

## Allowed Future Evidence Line

DHMS v1.1 may develop a future evidence line for inert local command proposals:

`DHMS v1.1 plans a local command-agent interception evidence line for inert local command proposals under fail-closed, non-production boundaries.`

Future phases may define static manifests, non-executing benchmarks, inert
examples, trace plans, and a constrained mock-agent proof if explicitly
approved later.

## Forbidden Current Behavior

v1.1.0 does not allow:

* executing a local command proposal
* invoking a shell
* invoking subprocess execution
* starting a terminal session
* adding a command runner
* adding a terminal adapter
* adding MCP, E2B, Codex, Claude, OpenClaw, DeepSeek, provider SDK, or agent SDK integration
* adding credential handling
* handling user data
* claiming production readiness
* claiming production shell safety
* claiming arbitrary command support

## Planned v1.1 Milestone Sequence

* `v1.1.0 Local Command-Agent Interception Planning`
* `v1.1.1 Local Command Proposal Static Manifest`
* `v1.1.2 Non-Executing Local Command Proposal Benchmark`
* `v1.1.3 Local Command Proposal Examples and Trace Plan`
* `v1.1.4 Controlled Mock-Agent Local Command Interception Proof`
* `v1.1.5 Local Command Interception Result Review and Freeze`

## Safety Invariants

* DHMS owns the policy decision before any command execution boundary.
* Local command proposals are inert data until explicitly approved by a later controlled-proof phase.
* Unknown proposals fail closed.
* Malformed proposals fail closed.
* Credential-seeking proposals fail closed.
* Destructive proposals are blocked or fail closed.
* Command-agent interception must produce trace evidence.
* A future controlled proof must be constrained, deterministic, synthetic, and non-production.
* v1.1.0 does not expand SQL/File/HTTP proof semantics.
* v1.1.0 does not add a new execution path.

## Validation Expectations

v1.1.0 keeps existing public evidence validation intact:

```bash
python3 cli.py demo-sql-fuse
python3 cli.py demo-file-fuse
python3 cli.py demo-http-fuse
python3 validation/run_dhms_mock_agent_interception_benchmark_v0.py
python3 cli.py bench-mock-agent-interception
python3 validation/run_dhms_controlled_mock_agent_runtime_interception_proof.py
python3 cli.py proof-mock-agent-interception
```

Future v1.1 validations should begin with static, inert proposal checks before
any controlled proof path is considered.

## Public Claim Boundaries

The v1.0 public frozen claim remains:

`DHMS provides a public evidence package for an execution fuse protocol proof chain covering SQL, File, HTTP, and controlled deterministic mock-agent runtime interception under documented non-production boundaries.`

v1.1.0 adds only this future planning claim:

`DHMS v1.1 plans a local command-agent interception evidence line for inert local command proposals under fail-closed, non-production boundaries.`

## Public Non-Claims

DHMS v1.1 planning does not claim:

* production readiness
* real agent runtime interception
* real LLM execution
* real shell execution safety
* arbitrary command execution support
* arbitrary terminal support
* arbitrary tool execution
* credential handling
* user data safety certification
* production filesystem safety
* production process safety
* production network safety
* MCP integration
* E2B integration
* Codex integration
* Claude integration
* OpenClaw integration
* DeepSeek integration
* provider SDK integration
* agent SDK integration

## Documentation-Only Confirmation

v1.1.0 is documentation-only and planning-only.

It does not add command execution, shell execution, subprocess execution,
terminal integration, a command runner, a benchmark runner, CLI command,
manifest file, examples file, trace examples file, schema change, source code
change, execution behavior, proof semantic change, proposal type
implementation, SQL/File/HTTP execution path, real agent runtime, real LLM,
MCP integration, E2B integration, Codex integration, Claude integration,
OpenClaw integration, DeepSeek integration, provider SDK integration, agent SDK
integration, credentials, user data, or production runtime behavior.

## Final Verdict

`READY_FOR_V1_1_1_LOCAL_COMMAND_PROPOSAL_STATIC_MANIFEST`
