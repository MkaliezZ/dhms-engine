# DHMS AgentFuse Development Roadmap

## Current Status

* Current branch: `agent-harness-v1`
* Current line: `DHMS Execution Fuse Protocol`
* Current package milestone: `v0.9.7 HTTP Fuse CLI Demo Wrapper`
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

`v0.9.3 Non-Executing HTTP Fuse Benchmark`

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
* current/completed non-executing file fuse benchmark milestone in v0.8.2

### v0.8.3 Non-Executing File Fuse Examples

* add public examples for file fuse proposals, decisions, gates, and traces
* keep examples non-executing
* do not add a file adapter
* current/completed non-executing file fuse examples milestone in v0.8.3

### v0.8.4 Constrained Temp-Directory Proof Planning

* define the safety envelope for a possible constrained temp-directory proof
* require explicit approval before any implementation
* plan temp root constraints, future proof cases, metrics, trace fields, failure conditions, and cleanup requirements
* do not create temp directories, fixtures, synthetic reports, cleanup verification, file policy, or file operation capability
* current/completed constrained temp-directory proof planning milestone in v0.8.4

### v0.8.4.1 Constrained Temp-Directory Proof Implementation

* implemented only after explicit approval
* performs two synthetic file operations inside a disposable temp root
* verifies temp root cleanup and deletion
* keeps rejected paths unopened and unresolved
* does not add arbitrary file operation support or a file adapter
* current/completed constrained temp-directory proof implementation milestone in v0.8.4.1

### v0.8.5 Result Review and Freeze

* review the v0.8 File Operation Safety Fuse evidence chain
* freeze claims and not-claimed boundaries
* preserve no uncontrolled real-world side effects principle
* current/completed File Operation Safety Fuse result review and freeze milestone in v0.8.5

### v0.8.6 File Fuse Quickstart and Evidence Seal

* add README File Fuse Quickstart directly below the SQL Fuse Demo quickstart
* seal the v0.8 File Operation Safety Fuse evidence chain
* preserve the v0.8.5 freeze semantics
* add no execution capability, file adapter, or arbitrary file operation support
* current/completed File Fuse Quickstart and Evidence Seal milestone in v0.8.6

### v0.8.7 File Fuse CLI Demo Wrapper

* add `python3 cli.py demo-file-fuse`
* aggregate the existing deterministic File Fuse public checks into one command
* preserve the v0.8.6 evidence seal
* add no file operation capability, file adapter, or arbitrary file operation support
* current/completed File Fuse CLI Demo Wrapper milestone in v0.8.7

### v0.8.8 DHMS AgentFuse Naming and Trademark Notice Alignment

* align the public DHMS AgentFuse naming hierarchy
* update README Trademark Notice to include current DHMS AgentFuse project marks
* do not rename the repository or branches
* do not claim formal trademark registration or provide legal advice
* current/completed naming and Trademark Notice alignment milestone in v0.8.8

### v0.8.9 DHMS README Public Surface Polish

* clarify the README public landing page
* keep SQL Fuse and File Fuse demos as primary quickstarts
* preserve historical Agent Harness reproduction commands as legacy material
* simplify README Trademark Notice wording without changing naming hierarchy docs
* documentation-only; no code or runtime behavior changes
* current/completed README public surface polish milestone in v0.8.9

### v0.8.10 DHMS README Milestone Heading Normalization

* normalize README peer milestone headings from v0.6.2 through v0.8.9
* keep true README subsections at their existing heading level
* preserve wording, proof claims, non-claims, links, quickstarts, License, and Trademark Notice
* documentation-only; no code or runtime behavior changes
* current/completed README milestone heading normalization patch in v0.8.10

## v0.9 HTTP / Network Request Safety Fuse Plan

### v0.9.0 HTTP / Network Request Safety Fuse Selection and Risk Review

* select `HTTP / Network Request Safety Fuse` as the next DHMS proof line
* record that SQL Sandbox Execution Fuse and File Operation Safety Fuse are the completed proof lines
* define HTTP/network risk categories and explicit non-claims
* planning-only; no HTTP execution, network adapter, API client, MCP integration, provider SDK integration, agent SDK integration, or arbitrary tool execution
* current/completed selection and risk review milestone in v0.9.0

### v0.9.1 HTTP / Network Request Safety Fuse Planning

* plan inert HTTP/network request proposal shapes
* define future risk-tier mapping and trace expectations
* keep all HTTP/network proposals non-executing until separately approved
* document planned fields, risk categories, decision classes, future metrics, and fail-closed planning rules
* current/completed HTTP/network planning milestone in v0.9.1

### v0.9.2 HTTP Fuse Static Case Manifest

* define static HTTP/network request safety cases
* treat URLs, headers, bodies, methods, and credentials as inert data
* do not perform network calls
* add exactly 16 synthetic HTTP/network request proposal cases
* current/completed static inert HTTP case manifest milestone in v0.9.2

### v0.9.3 Non-Executing HTTP Fuse Benchmark

* evaluate static HTTP/network cases in memory
* produce deterministic metrics
* do not implement HTTP execution or API clients
* current/completed non-executing HTTP Fuse benchmark milestone in v0.9.3

### v0.9.3.1 DHMS Proof-Line Protocol Lifecycle Mapping Clarification

* map SQL, File, and HTTP proof-line evidence back to the v0.6 DHMS Execution Fuse Protocol lifecycle
* clarify that SQL has a controlled runtime-path sandbox release, File has a constrained synthetic temp-directory proof, and HTTP currently has static inert cases plus a non-executing benchmark
* documentation-only; do not modify runners, manifests, examples, CLI commands, adapters, proof semantics, or runtime behavior
* current/completed lifecycle mapping clarification milestone in v0.9.3.1
* next recommended milestone: `v0.9.4 HTTP Fuse Non-Executing Examples`

### v0.9.4 HTTP Fuse Non-Executing Examples

* add examples for request proposals, decisions, gates, and traces
* keep examples non-executing
* current/completed HTTP Fuse non-executing examples milestone in v0.9.4
* next recommended milestone: `v0.9.5 Constrained Local Mock HTTP Proof Planning`

### v0.9.5 Constrained Local Mock HTTP Proof Planning

* plan a future constrained local mock HTTP proof
* distinguish weak simulated target evidence from a future strong constrained mock proof
* define mock-only, local-only, loopback-only, synthetic-only proof envelope
* require explicit approval before any v0.9.5.1 implementation
* do not implement mock server, socket creation, HTTP client, network request, proof runner, validation runner, adapter, API client, or CLI command
* current/completed constrained local mock HTTP proof planning milestone in v0.9.5
* next recommended milestone: `v0.9.5.1 Constrained Local Mock HTTP Proof Implementation, after explicit approval`

### v0.9.5.1 Constrained Local Mock HTTP Proof Implementation, after explicit approval

* implement only if the task context explicitly approves implementation
* release exactly one synthetic GET to a disposable local mock target
* keep blocked and fail-closed HTTP/network proposal classes non-executing
* verify teardown and non-claim boundaries
* current/completed constrained local mock HTTP proof implementation milestone in v0.9.5.1
* next recommended milestone: `v0.9.6 HTTP Fuse Result Review and Freeze`

### v0.9.6 HTTP Fuse Result Review and Freeze

* review and freeze the HTTP / Network Request Safety Fuse evidence chain
* include v0.9.0 selection, v0.9.1 planning, v0.9.2 static cases, v0.9.3 benchmark, v0.9.3.1 lifecycle mapping, v0.9.4 examples, v0.9.5 planning, and v0.9.5.1 constrained local mock proof
* documentation-only; do not modify runners, manifests, examples, CLI commands, adapters, proof semantics, or runtime behavior
* current/completed HTTP Fuse result review and freeze milestone in v0.9.6
* next recommended milestone: `v0.9.7 HTTP Fuse CLI Demo Wrapper`

### v0.9.7 HTTP Fuse CLI Demo Wrapper

* add `python3 cli.py demo-http-fuse`
* run the existing non-executing HTTP benchmark and constrained local mock HTTP proof in order
* do not modify existing HTTP runners, manifests, examples, SQL/File runners, proof behavior, adapters, API clients, or credential handling
* current/completed HTTP Fuse CLI demo wrapper milestone in v0.9.7
* next recommended milestone: `v0.9.8 SQL/File/HTTP Evidence Alignment`

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
* no HTTP/network request capability without explicit phase approval
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

`READY_FOR_NEXT_DHMS_PROOF_LINE_PLANNING`
