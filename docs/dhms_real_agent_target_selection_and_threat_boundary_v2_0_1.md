# DHMS Real Agent Target Selection and Threat Boundary v2.0.1

## Purpose

v2.0.1 chooses one narrow future real-agent integration preview target and
defines its threat boundary before any implementation begins.

DHMS v2.0.1 selects and defines the threat boundary for a future real-agent
integration preview target in planning form only, without adding real agent
integration, SDK integration, runtime integration, adapter code, schema files,
parsers, runners, CLI commands, execution behavior, or production runtime
claims.

This milestone may select a future target as a planning target only. It does
not integrate that target, run that target, import its SDK, call its API, or
add adapter code.

## Selected Future Target

Selected target:

`local mock-to-real agent boundary`

This is the first v2.x target because it is the lowest-risk future preview
boundary:

* it can remain local
* it can remain proposal-only
* it can remain non-production
* it can remain non-credentialed
* it is closest to the existing DHMS mock-agent evidence line
* it does not require OpenClaw, Codex, Claude Code, MCP, E2B, DeepSeek,
  provider SDK, or agent SDK integration
* it gives DHMS a narrow path to study proposal interception before discussing
  any real runtime handoff

Selecting this target does not authorize implementation. It only identifies
the first future boundary to plan around.

## Target-Selection Criteria Applied

The selected target is evaluated against the following v2.0.1 criteria:

* observable proposal before execution
* proposal-only / dry-run feasibility
* execution disabled by default
* ability to preserve DHMS `RELEASE`, `HOLD`, `BLOCK`, and `FAIL_CLOSED`
* evidence continuity
* trace continuity
* fail-closed behavior on missing or invalid DHMS decision
* local or controlled non-production environment
* no production credentials required
* no user data required
* no uncontrolled shell, tool, or network execution required
* rollback simplicity
* implementation complexity
* public claim risk

## Candidate Comparison Matrix

| candidate target | proposal observability | dry-run feasibility | execution risk | credential/user-data risk | rollback simplicity | public-claim risk | selected now? | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| local mock-to-real agent boundary | high: closest to existing mock-agent proposal evidence | high: can stay proposal-only and local | low if execution remains disabled | low if synthetic data and no credentials are used | high: local planning boundary can be reverted without external dependency | lower: clearly framed as future planning | yes | lowest-risk first target; local, proposal-only, non-production, non-credentialed, and aligned with existing DHMS mock-agent evidence |
| OpenClaw-style local orchestrator boundary | possible, but would require careful runtime boundary definition | medium, only if kept as proposal-only planning | higher because orchestrators imply real action surfaces | medium unless credentials and user data are explicitly excluded | medium | higher because readers may infer OpenClaw support | no | deferred; not selected for the first target because no OpenClaw integration is being added or claimed |
| Codex-style coding agent proposal boundary | possible in concept, but runtime proposal boundaries must be defined first | medium, only if kept as inert proposal examples | higher because coding agents can affect files, commands, and repositories | medium to high in real workspaces | medium | high because readers may infer Codex integration | no | deferred; candidate for later planning after a local mock-to-real boundary is defined |
| Claude Code-style coding agent proposal boundary | possible in concept, but runtime proposal boundaries must be defined first | medium, only if kept as inert proposal examples | higher because coding agents can affect files, commands, and repositories | medium to high in real workspaces | medium | high because readers may infer Claude Code integration | no | deferred; candidate for later planning after proposal-only boundaries mature |
| MCP tool-call proposal boundary | possible where tool proposals are observable | medium, but requires MCP-specific boundary planning | medium to high because tool surfaces vary widely | medium to high depending on connected tools | medium | high because readers may infer MCP integration or replacement | no | deferred; not selected for the first target because DHMS does not implement MCP integration |
| E2B-style substrate handoff boundary | possible at a future substrate handoff layer | lower until handoff contracts are more concrete | medium: substrate execution is still execution | medium depending on mounted data and credentials | medium | high because readers may infer E2B integration or sandbox support | no | deferred; candidate for later substrate planning, not selected for the first target |

## Why This Target Was Selected First

The local mock-to-real agent boundary provides the cleanest bridge from the
existing controlled DHMS mock-agent evidence line toward a future real-agent
preview. It can preserve the same core discipline:

* observe proposal before execution
* validate proposal completeness
* assign `RELEASE`, `HOLD`, `BLOCK`, or `FAIL_CLOSED`
* keep execution disabled by default
* require evidence and trace continuity
* fail closed on missing, stale, or invalid decisions
* avoid production credentials, user data, uncontrolled shell execution,
  uncontrolled tool execution, and uncontrolled network execution

The target is intentionally local and narrow. It is not a commitment to real
agent runtime integration.

## Non-Selected Targets

### OpenClaw-style Local Orchestrator Boundary

Deferred. It is not selected for the first target because an
OpenClaw-style boundary could be misread as current OpenClaw integration.
v2.0.1 does not connect to OpenClaw, import OpenClaw code, run OpenClaw, or
claim OpenClaw support.

### Codex-style Coding Agent Proposal Boundary

Deferred. It is a candidate for later planning, but it is not selected for the
first target because coding-agent proposal boundaries can touch repository,
file, command, and tool surfaces. v2.0.1 does not integrate Codex or claim
Codex support.

### Claude Code-style Coding Agent Proposal Boundary

Deferred. It is a candidate for later planning, but it is not selected for the
first target because it would require careful proposal-only boundaries before
any discussion of runtime behavior. v2.0.1 does not integrate Claude or
Claude Code and does not claim Claude Code support.

### MCP Tool-Call Proposal Boundary

Deferred. It is a candidate for later planning because MCP-style systems can
expose tool-call proposals, but DHMS does not implement MCP integration and is
not an MCP replacement. v2.0.1 does not connect to MCP servers or tools.

### E2B-style Substrate Handoff Boundary

Deferred. It is a candidate for later substrate planning, but it is not
selected for the first target because substrate handoff raises execution,
sandbox, data-mount, and public-claim risks. v2.0.1 does not integrate E2B or
claim E2B support.

### Any Other Candidate

Any target not selected in this document remains a candidate for later planning
only. It is not supported, integrated, or authorized by v2.0.1.

## Selected Target Threat Boundary

### Inside the Boundary

The selected future boundary may include, in planning form only:

* an inert proposal emitted by a local mock-to-real target
* a DHMS proposal envelope received before execution
* completeness checks over the proposal envelope
* assignment of `RELEASE`, `HOLD`, `BLOCK`, or `FAIL_CLOSED`
* evidence and trace expectations
* refusal semantics for all non-`RELEASE` decisions
* a requirement that any future bounded proof must be explicitly approved in a
  later milestone

### Outside the Boundary

The selected target boundary excludes:

* real agent runtime integration
* real LLM execution
* OpenClaw integration
* Codex integration
* Claude or Claude Code integration
* DeepSeek integration
* MCP integration
* E2B integration
* provider SDK integration
* agent SDK integration
* runtime adapter implementation
* controlled adapter implementation
* schema implementation
* proposal parser implementation
* handoff parser implementation
* adapter parser implementation
* adapter executor implementation
* shell execution
* command execution
* file mutation support
* network execution support
* arbitrary tool execution
* credential handling
* user data handling
* production runtime behavior

### What Must Remain Inert

The selected target must keep these items inert until a later explicit
implementation phase:

* proposal payloads
* payload references
* tool names
* target identifiers
* runtime names
* trace references
* evidence references
* candidate target labels

### What Must Remain Non-Executing

The selected target must remain non-executing in v2.0.1:

* no proposal execution
* no direct tool call
* no shell or command execution
* no file mutation
* no network request
* no SDK call
* no MCP call
* no E2B handoff
* no OpenClaw, Codex, Claude Code, DeepSeek, provider SDK, or agent SDK call

### Evidence Required Before Future Implementation

Before any later implementation may begin, a future phase must define:

* exact proposal-only dry-run contract
* accepted proposal types
* explicit unsupported proposal types
* required proposal envelope fields
* decision semantics for `RELEASE`, `HOLD`, `BLOCK`, and `FAIL_CLOSED`
* fail-closed behavior for missing, malformed, stale, or unsupported inputs
* trace fields and trace continuity requirements
* proof boundary for any constrained release path
* rollback and freeze plan
* public non-claims

### Trace Continuity Required

The future selected boundary must preserve trace continuity from:

* target proposal observation
* DHMS proposal envelope receipt
* proposal completeness validation
* safety decision assignment
* execution gate decision
* agent-visible runtime result
* rejected-action non-execution
* evidence reference
* trace verdict

### What Must Fail Closed

The selected target must fail closed when:

* proposal envelope is absent
* proposal envelope is malformed
* `proposal_id` is missing
* payload reference is missing
* proposal type is unsupported
* DHMS decision is missing
* DHMS decision is unknown
* evidence is stale
* trace reference is missing
* requested capability is outside the selected boundary
* execution is attempted before a documented `RELEASE` boundary

### What Must Never Be Interpreted as RELEASE

These states must never be interpreted as `RELEASE`:

* missing decision
* unknown decision
* malformed decision
* stale decision
* `HOLD`
* `BLOCK`
* `FAIL_CLOSED`
* missing trace
* stale trace
* incomplete evidence
* unsupported proposal type
* capability outside boundary

### What Must Not Be Connected Yet

v2.0.1 must not connect:

* real agents
* real LLMs
* OpenClaw
* Codex
* Claude
* Claude Code
* DeepSeek
* MCP
* E2B
* provider SDKs
* agent SDKs
* runtime adapters
* controlled adapters
* shell, command, file, or network execution paths

## Selected Target Conceptual Flow

```text
selected target emits inert proposal
DHMS receives proposal envelope
DHMS validates proposal completeness
DHMS assigns RELEASE / HOLD / BLOCK / FAIL_CLOSED
DHMS records evidence and trace expectations
future preview refuses all non-RELEASE decisions
future preview remains non-executing unless a later phase explicitly implements a bounded proof
```

This is a conceptual flow only. v2.0.1 does not implement it.

## Selected Target Failure Cases

| failure case | required behavior |
| --- | --- |
| no proposal envelope | `FAIL_CLOSED`; no execution |
| malformed proposal envelope | `FAIL_CLOSED`; no execution |
| missing `proposal_id` | `FAIL_CLOSED`; no execution |
| missing payload reference | `FAIL_CLOSED`; no execution |
| unsupported proposal type | `FAIL_CLOSED` or `BLOCK`; no execution |
| missing DHMS decision | `FAIL_CLOSED`; no execution |
| unknown DHMS decision | `FAIL_CLOSED`; no execution |
| `HOLD` decision | hold remains non-executing; not interpreted as `RELEASE` |
| `BLOCK` decision | block remains non-executing; not interpreted as `RELEASE` |
| `FAIL_CLOSED` decision | fail closed; no execution |
| stale evidence | `FAIL_CLOSED`; no execution |
| missing trace reference | `FAIL_CLOSED`; no execution |
| requested capability outside target boundary | `BLOCK` or `FAIL_CLOSED`; no execution |
| attempt to execute before documented `RELEASE` boundary | `FAIL_CLOSED`; no execution |

## Why v2.0.1 Still Does Not Implement

Target selection is not integration.

Threat boundary definition is not execution.

Candidate comparison is not a support claim.

Selecting a future target does not authorize implementation.

Implementation requires a later explicit milestone with allowed files,
forbidden paths, validation commands, trace expectations, and bounded proof
criteria.

## Public Non-Claims

DHMS v2.0.1 does not claim:

* production readiness
* real agent integration
* real agent runtime interception
* real LLM execution
* OpenClaw integration
* Codex integration
* Claude integration
* Claude Code integration
* DeepSeek integration
* MCP integration
* E2B integration
* provider SDK integration
* agent SDK integration
* runtime adapter implementation
* controlled adapter implementation
* sandbox implementation
* shell execution
* command execution
* file mutation support
* network execution support
* arbitrary tool execution
* schema implementation
* proposal parser
* handoff parser
* adapter parser
* adapter executor
* production runtime behavior
* credential handling
* user data handling
* universal agent safety
* industry standard status

## Next Milestone

Recommended next milestone:

`v2.0.2 Proposal-Only Dry-Run Contract`

## Final Verdict

`READY_FOR_V2_0_2_PROPOSAL_ONLY_DRY_RUN_CONTRACT`
