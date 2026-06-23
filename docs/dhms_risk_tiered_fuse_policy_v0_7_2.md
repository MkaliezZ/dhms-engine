# DHMS Risk-Tiered Fuse Policy Draft v0.7.2

## Purpose

v0.7.2 defines the first DHMS Risk-Tiered Fuse Policy draft. The policy draft
explains how DHMS can classify observable agent actions into different risk
tiers and route them through different fuse behavior.

The goal is performance-aware safety: not all actions require heavy review,
sandbox, or controlled release, but all observable actions should be classified
or recorded.

This is a design document only. v0.7.2 does not implement new runtime behavior,
does not add execution capability, and does not add file, shell, HTTP, MCP, or
provider integration.

## Relationship to DHMS Execution Fuse Protocol

The v0.6.0 DHMS Execution Fuse Protocol defines the fuse lifecycle: observable
runtime request, tool-call proposal, safety decision, execution gate,
controlled release where applicable, state verification, and trace.

v0.6.1, v0.6.2, and v0.6.3 provide the benchmark, CLI demo, and minimal API
shape. v0.7.2 adds the policy concept for routing different observable actions
through different fuse levels.

Risk-tiered fuse policy does not replace fail-closed behavior. It refines how
actions are classified before gate decisions.

## Core Principle

* Every observable agent action should be classified or recorded.
* Not every action should use the same heavy gate.
* Low-risk actions may use a fast path.
* High-risk actions require hold, review, sandbox, or block.
* Unknown or unsupported actions fail closed by default.
* Read-only does not mean risk-free.
* Fast pass is still a DHMS decision, not a bypass of DHMS.
* The policy owner remains DHMS.

## Tier Model

### L0 Observed / No Gate

For actions that are observed and recorded but do not require active gating.

Examples:

* reading public project documentation
* reading explicitly allowlisted static examples

Requirements:

* must still be traceable in lightweight form
* not for secrets, credentials, customer data, production data, or private paths

### L1 Fast Pass

For low-risk actions that pass a lightweight deterministic check.

Examples:

* reading README
* reading docs
* reading public examples
* reading benchmark fixtures
* reading harmless metadata in an allowlisted project path

Requirements:

* decision should still be recorded
* fast pass must not imply production readiness or universal safety

### L2 Constrained Read / Constrained Action

For actions that may be allowed only under constraints.

Examples:

* reading within allowlisted directories
* bounded file size
* safe extension
* no secret markers
* no hidden credential paths
* writing deterministic local reports under an allowlisted reports directory

Required constraints may include:

* path allowlist
* size limit
* extension allowlist
* sensitive-pattern checks

No arbitrary file adapter is implemented in v0.7.2.

### L3 Hold / Sandbox / Review

For high-risk or ambiguous actions.

Examples:

* proposed SQL SELECT candidate requiring sandbox bridge
* sensitive file reads
* writes to source code
* external tool proposal
* network action proposal
* shell-like proposal

Expected behavior:

* hold
* review
* sandbox
* controlled release

The current proven L3 example is the v0.5.15 SQL sandbox controlled release
path.

### L4 Block / Fail-Closed

For destructive, mutation, credentialed, unsupported, unknown, or clearly
unsafe actions.

Examples:

* SQL DELETE/UPDATE
* production DB access
* credential access
* secret exfiltration
* unauthorized shell command
* network exfiltration
* unsupported real runtime execution

Default for unknown unsupported actions. No execution.

## Action Category Examples

| Action category | Likely tier | Reason | Expected fuse behavior | Current implementation support |
| --- | --- | --- | --- | --- |
| Public documentation read | L0 or L1 | Public, low mutation risk | observe or fast pass with trace | Design-only tiering; ordinary repo reads are not a DHMS runtime adapter |
| Project fixture read | L1 | Allowlisted project fixture, low sensitivity | deterministic fast pass | Design-only tiering |
| Hidden file read | L2 or L3 | Hidden path may indicate sensitive state | constrained read or hold/review | Design-only; no file adapter implemented |
| `.env` read | L4 | Likely credentials/secrets | block or fail closed | Design-only; no file adapter implemented |
| API key / credential read | L4 | Secret exfiltration risk | block or fail closed | Design-only; no file adapter implemented |
| Customer data read | L3 or L4 | Confidentiality and compliance risk | hold/review or fail closed | Design-only; no production data support |
| Synthetic benchmark case read | L0 or L1 | Synthetic, allowlisted fixture | observe or fast pass | Benchmark runner reads its fixture; no runtime file policy |
| Deterministic local report write | L2 | Bounded write under allowlisted report path | constrained write with trace | Design-only for future file fuse |
| Source code write | L3 | Can change behavior and safety boundary | hold/review | Design-only; no file adapter implemented |
| SQL allowlisted SELECT candidate | L3 | Read-like but requires sandbox proof | hold, sandbox, controlled release | Proven only through v0.5.15 SQL sandbox path |
| SQL mutation | L4 | Destructive mutation risk | block or fail closed | Proven blocked in SQL safety validation |
| Shell command proposal | L4 by default | High system side-effect risk | block/fail closed until planned | Design-only; no shell adapter implemented |
| HTTP/network proposal | L3 or L4 | External effect and exfiltration risk | hold/review or block | Design-only; no HTTP adapter implemented |
| MCP tool proposal | L3 or L4 | Tool-specific external effects | hold/review or block | Design-only; no MCP integration implemented |
| OpenClaw runtime proposal | L3 or L4 | Real runtime/backend execution risk | hold/review or block | Design-only; no OpenClaw runtime integration |
| Provider SDK proposal | L3 or L4 | Provider execution and data exposure risk | hold/review or block | Design-only; no provider SDK integration |
| Production database proposal | L4 | Credentialed production data and mutation risk | block/fail closed | Not supported |

Unsupported future categories are design-only / not implemented.

## Read-only Is Not Automatically Safe

Read has low mutation risk but may have high confidentiality risk. Safe read
requires evaluating path, data class, sensitivity, context, and policy
constraints.

Safer reads may include:

* README
* docs
* examples
* benchmarks
* synthetic fixtures

Unsafe reads may include:

* `.env`
* private keys
* API tokens
* customer data
* production database dumps
* secrets
* private contracts
* browser cookies
* SSH keys
* hidden credential directories

Read-only actions can still disclose sensitive information. DHMS should not
treat read-only as automatically safe.

## Performance Model

* L0/L1 should be low overhead.
* L2 adds constraint checks.
* L3 may add review, sandbox, or controlled release overhead.
* L4 blocks or fails closed quickly.
* DHMS should avoid forcing every action through heavy sandbox or human review.
* The performance goal is tiered routing, not uniform heavy gating.

This section uses qualitative language only. v0.7.2 does not claim measured
performance results.

## Relationship to v0.8 File Operation Safety Fuse

v0.7.2 is design-only. The preferred v0.8 second proof line is File Operation
Safety Fuse.

v0.8 may turn some L1/L2/L3 file operation concepts into controlled
deterministic validation. v0.7.2 does not implement file policy.

## Non-execution Guarantee

v0.7.2 adds:

* no file adapter
* no shell adapter
* no HTTP adapter
* no MCP adapter
* no provider SDK integration
* no OpenClaw runtime integration
* no DeepSeek integration
* no new SQL execution path
* no new sandbox execution
* no production runtime support

## Not Claimed

v0.7.2 does not claim:

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

`v0.7.3 Landscape / Comparison Doc`

Final document verdict:

`READY_FOR_V0_7_3_LANDSCAPE_COMPARISON_DOC`
