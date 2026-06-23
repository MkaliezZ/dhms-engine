# DHMS AgentFuse Development Roadmap

## Current Status

* Current branch: `agent-harness-v1`
* Current line: `DHMS Execution Fuse Protocol`
* Current package milestone: `v0.8.1 File Fuse Static Case Manifest`
* Completed v0.6 line:
  * v0.6.0 protocol spec
  * v0.6.1 benchmark
  * v0.6.2 CLI demo
  * v0.6.3 minimal API / adapter skeleton

## Naming Strategy

* Main brand: `DHMS`
* Protocol name: `DHMS Execution Fuse Protocol`
* Formal long name: `DHMS Agent Execution Fuse Protocol`
* Tool family: `DHMS AgentFuse`
* Benchmark family: `DHMS-AgentFuse-Bench`
* CLI family: `DHMS AgentFuse CLI`
* API name: `DHMS AgentFuse Minimal API`
* Adapter name: `DHMS AgentFuse Adapter Skeleton`

DHMS AgentFuse is the benchmark, demo, API, and adapter-skeleton tool family
around the DHMS Execution Fuse Protocol.

Avoid public-facing shorthand such as `DHMSAEFP`, standalone `AgentFuse`,
`Agent Fuse`, `Agent-Fuse`, or `Agentfuse`.

## v0.6 Completed Line

The v0.6 line packages the first proven execution fuse path without expanding
execution capability:

* v0.5.x SQL Sandbox Execution Fuse proof
* v0.6.0 protocol spec
* v0.6.1 benchmark
* v0.6.2 CLI demo
* v0.6.3 minimal API / adapter skeleton

The current actual controlled-release proof remains v0.5.15 existing
controlled runtime-path SQL sandbox release validation, limited to the exact
allowlisted SQL:

```sql
SELECT id, label, status FROM toy_accounts ORDER BY id;
```

## v0.7 Public Protocol Package Plan

### v0.7.0 Public Protocol Package

* establish protocol package index
* unify DHMS / DHMS AgentFuse naming
* summarize v0.6.0 protocol, v0.6.1 benchmark, v0.6.2 CLI, v0.6.3 API skeleton
* clarify reproducible paths

### v0.7.1 Protocol Examples

* SQL Fuse example
* unsupported non-SQL proposal example
* trace example
* no-execution examples

### v0.7.2 Risk-Tiered Fuse Policy Draft

* introduce tiered fuse concept
* L0 Observed / No Gate
* L1 Fast Pass
* L2 Constrained Read / Constrained Action
* L3 Hold / Sandbox / Review
* L4 Block / Fail-Closed
* design document only; no real file/shell/MCP implementation
* current/completed draft in v0.7.2

### v0.7.3 Landscape / Comparison Doc

* MCP connects tools; DHMS controls execution boundaries
* guardrails vs execution fuse
* agent SDK vs policy owner
* sandbox vs controlled release
* define boundaries without attacking competitors
* current/completed conceptual comparison in v0.7.3

### v0.7.4 Contribution Guide / Case Format

* how to write DHMS cases
* how to write benchmark cases
* how to write trace expectations
* how to extend future fuse lines
* contribution rule: do not casually add execution paths
* current/completed contribution and case-format guidance in v0.7.4

### v0.7.5 Fresh Clone Reproduction Check

* clean clone reproduction
* run Quickstart
* run demo
* run benchmark
* document minimum external reproduction path
* current/completed fresh clone reproduction check in v0.7.5

## v0.8 Second Fuse Line Direction

`v0.8.0 = File Operation Safety Fuse Planning`

Preferred direction:

`File Operation Safety Fuse`

v0.8.0 should plan how DHMS can demonstrate that it is not only a SQL
benchmark, but a general execution fuse protocol with a second proof line. It
should still avoid uncontrolled real-world side effects.

Next direction:

`v0.8.2 Non-Executing File Fuse Benchmark`

## v0.8 File Operation Safety Fuse Plan

### v0.8.0 File Operation Safety Fuse Planning

* plan the second DHMS execution fuse proof line
* define file operation threat categories
* map file operation examples to L0-L4 risk tiers
* propose future case categories and trace fields
* planning-only; no file policy, file adapter, or file operation capability
* current/completed planning milestone in v0.8.0

### v0.8.1 File Fuse Static Case Manifest

* define a static file fuse case manifest
* keep cases inert and non-executing
* preserve fail-closed defaults and no direct execution by default
* current/completed static manifest milestone in v0.8.1

### v0.8.2 Non-Executing File Fuse Benchmark

* evaluate planned file fuse cases in memory
* produce deterministic summary metrics
* do not perform file reads, writes, appends, deletes, or lists

### v0.8.3 Non-Executing File Fuse Examples

* add public examples for file fuse proposals, decisions, gates, and traces
* keep examples non-executing
* do not add a file adapter

### v0.8.4 Constrained Temp-Directory Proof

* possible only if explicitly approved later
* may consider a tightly constrained local temp-directory proof
* must not be implemented by v0.8.0, v0.8.1, v0.8.2, or v0.8.3

### v0.8.5 Result Review and Freeze

* review any explicitly approved future proof result
* freeze claims and not-claimed boundaries
* preserve no uncontrolled real-world side effects principle

## Development Prompt Pattern

Standard DHMS development prompts should include:

* Goal
* Context
* Naming / Positioning
* Allowed files
* Required outputs
* Hard boundaries
* Validation
* Targeted scans
* Final report
* Commit message
* Final verdict

DHMS development prompts should behave like an execution fuse: first define
goals, allowed paths, forbidden paths, validation, and final evidence before
allowing an agent to act.

## Hard Boundaries

Persistent boundaries:

* fail-closed by default
* no new execution path without explicit phase approval
* no arbitrary SQL support unless explicitly planned
* no mutation SQL execution
* no production DB support
* no credentialed DB support
* no OpenClaw runtime integration without explicit phase approval
* no provider SDK integration without explicit phase approval
* no agent SDK integration without explicit phase approval
* no HTTP/file/shell/MCP adapter without explicit phase approval
* no file operation capability without explicit phase approval
* no production-ready claims before proof
* do not alter License / Trademark Notice casually

## Not-claimed Scope

DHMS AgentFuse currently does not claim:

* universal agent safety
* MCP replacement
* production runtime
* production DB safety
* arbitrary tool execution
* arbitrary file operation support
* autonomous execution authorization
* a standard adopted by industry yet

## Final Roadmap Verdict

`READY_FOR_V0_8_2_NON_EXECUTING_FILE_FUSE_BENCHMARK`
