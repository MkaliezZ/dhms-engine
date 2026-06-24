# DHMS HTTP / Network Request Safety Fuse Selection and Risk Review v0.9.0

## Purpose

v0.9.0 records the selected next DHMS proof line after the completed SQL and
File Fuse work. The selected proof line is:

`HTTP / Network Request Safety Fuse`

This is a planning-only milestone. It defines risk boundaries and future
milestone direction. It does not implement HTTP execution, network adapters,
API clients, MCP integration, provider SDK integration, agent SDK integration,
or arbitrary tool execution.

Audited base commit:

`79ccdb8b5438f68a4f5b08c75a93dcd3d15594a5`

## Completed Proof Lines

DHMS has completed two proof lines:

* `v0.5 SQL Sandbox Execution Fuse`
* `v0.8 File Operation Safety Fuse`

The SQL line proved one exact allowlisted SELECT in a temporary local SQLite
sandbox. The File Fuse line proved an explicitly approved constrained
temp-directory proof with two synthetic operations inside a disposable temp
root while rejected paths remained unopened and unresolved.

## Selected Next Proof Line

The next DHMS proof line is:

`HTTP / Network Request Safety Fuse`

This selection is already made in v0.9.0. v0.9.0 does not run an open-ended
proof-line selection process and does not implement the selected proof line.

## Selection Rationale

HTTP/network request safety is the next logical proof line after SQL and File
because:

* network requests are common agent actions.
* network requests may cause side effects.
* network requests may expose credentials or sensitive data.
* network requests may create data exfiltration risk.
* network requests may create SSRF-style risk.
* network requests may mutate external APIs or trigger irreversible actions.
* HTTP/network intent can first be modeled as inert observable request
  proposals before any real network call is made.
* HTTP is safer to plan before shell execution, MCP tool invocation, or
  arbitrary multi-step tool execution.

## Bounded Claim

v0.9.0 selects HTTP / Network Request Safety Fuse as the next DHMS proof line after the completed SQL Sandbox Execution Fuse and File Operation Safety Fuse lines. It is a planning-only milestone that defines risk boundaries and future milestone direction without implementing HTTP execution, network adapters, API clients, MCP integration, provider SDK integration, agent SDK integration, or arbitrary tool execution.

## HTTP Proof-Line Draft Claim

DHMS may evaluate synthetic HTTP/network request proposals as observable intent objects and classify them into allow, block, hold-for-review, or fail-closed categories without making real network calls.

## Risk Categories

Future HTTP / Network Request Safety Fuse work should consider these risk
categories:

* credential-bearing request proposals
* secret-bearing header or query proposals
* request body data exfiltration
* customer data exfiltration
* production API mutation
* irreversible external API action
* webhook trigger or callback abuse
* SSRF-style internal network target
* localhost or metadata-service target
* unsafe redirect chain
* untrusted domain request
* high-risk HTTP method proposal such as `POST`, `PUT`, `PATCH`, or `DELETE`
* authentication ambiguity
* unknown or malformed URL
* unsupported protocol scheme
* hidden network request embedded in a broader tool proposal

These categories are planning categories only in v0.9.0.

## Explicit Non-Claims

v0.9.0 does not claim:

* real HTTP execution
* real network calls
* web browsing
* API client support
* HTTP adapter support
* credential handling
* production outbound request safety
* SSRF protection
* data exfiltration protection
* external API mutation safety
* webhook safety
* MCP integration
* OpenClaw integration
* DeepSeek/provider integration
* provider SDK integration
* agent SDK integration
* shell execution
* arbitrary tool execution
* production readiness
* industry standard status
* replacement of MCP, guardrails, sandboxes, SDKs, or human approval systems

## Future Milestone Sequence

The recommended v0.9 milestone sequence is:

* `v0.9.0 HTTP / Network Request Safety Fuse Selection and Risk Review`
* `v0.9.1 HTTP / Network Request Safety Fuse Planning`
* `v0.9.2 HTTP Fuse Static Case Manifest`
* `v0.9.3 Non-Executing HTTP Fuse Benchmark`
* `v0.9.4 HTTP Fuse Non-Executing Examples`
* `v0.9.5 HTTP Fuse Result Review / Freeze`
* optional later constrained proof only if separately approved

## Implementation Boundaries

Future v0.9.1+ work must remain bounded until a later phase explicitly
authorizes implementation. v0.9.0 does not authorize:

* HTTP execution
* real network calls
* web browsing
* HTTP adapters
* API clients
* credential handling
* provider SDK integration
* agent SDK integration
* MCP integration
* shell execution
* OpenClaw integration
* DeepSeek/provider integration
* arbitrary tool execution
* production runtime behavior

## Approval Requirement

No HTTP/network implementation may be added merely because the proof line has
been selected. Any future implementation must receive explicit phase approval,
must define allowed and forbidden paths before implementation, and must include
deterministic validation and trace expectations.

## Next Recommended Milestone

`v0.9.1 HTTP / Network Request Safety Fuse Planning`

Final document verdict:

`READY_FOR_V0_9_1_HTTP_NETWORK_REQUEST_SAFETY_FUSE_PLANNING`
