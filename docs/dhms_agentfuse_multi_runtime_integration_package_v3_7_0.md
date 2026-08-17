# DHMS AgentFuse v3.7.0 Multi-Runtime Integration Package

## Purpose

v3.7.0 packages the independently reviewed v3.6.x integration mappings as a
small importable metadata surface. A consumer can enumerate the mappings,
inspect their tested capabilities and limitations, and trace each profile back
to frozen conformance evidence without importing an adapter implementation.

The package does not execute tools, discover installed runtimes, install
plugins, make network requests, or create a universal runtime abstraction.

## Why Profiles Instead of a Universal Runtime Interface

The reviewed paths have materially different lifecycle semantics:

- Python RuntimeGuard exposes decision-only and guarded sync/async APIs.
- the provider-neutral consumer is reference demonstration code;
- LangGraph owns `GraphInterrupt`, checkpoint, and resume control flow; and
- DSH is an external TypeScript integration whose `ask` vocabulary represents
  host approval deferral.

A shared `evaluate/dispatch/interrupt/settle` protocol would erase those
differences. v3.7.0 therefore publishes integration mappings and evidence
boundaries, while the existing implementations remain authoritative.

## Public API

The public surface is intentionally limited to:

```python
from dhms_agentfuse.integrations import (
    IntegrationProfile,
    get_integration,
    list_integrations,
)
```

`IntegrationProfile` is a frozen dataclass. `list_integrations()` returns the
four immutable profiles in stable package order. `get_integration(id)` returns
the registered profile or raises `KeyError` for an unknown ID. The registry is
static: there is no entry-point discovery, filesystem scan, environment
mutation, dynamic package import, or mutable public registry object.

## Profile Fields

Each profile records:

- stable integration and runtime-family identity;
- `canonical`, `reference`, `internal_adapter`, or `external_adapter` kind;
- implementation ownership and a plain-text implementation reference;
- canonical AgentFuse actions, fixed to `allow | block`;
- the bounded pre-dispatch decision boundary;
- capabilities evidenced in the tested path;
- facts that remain host-owned;
- tested runtime version and, where applicable, commit;
- conformance fixture version and digest;
- evidence scope, references, and explicit limitations.

`to_safe_dict()` deterministically serializes metadata only. It contains no
action arguments, credentials, handlers, mutable runtime objects, or imported
provider objects.

## Capability Semantics

An entry in `evidenced_capabilities` means:

> the named integration mapping has evidence for observing or representing
> this fact in the tested path.

It does not mean AgentFuse owns that lifecycle fact. Approval, dispatch
implementation, physical execution, interruption, retry, recovery, process
completion, and goal achievement remain host-owned where the profile says so.

The model uses an ordered capability vocabulary instead of a generic adapter
protocol so unsupported or N/A dimensions remain visible.

## Packaged Profiles

### `python-runtime-guard`

Kind: `canonical`. Owner: `dhms`.

This profile describes decision-only `evaluate()` / `aevaluate()` and guarded
`invoke()` / `ainvoke()` with sync/async parity. It records execution-failure,
terminal-settlement, identity, deterministic re-evaluation, and safe-output
evidence. It does not claim host interruption observation: case 09 remains N/A
for RuntimeGuard itself. Hosts still own execution consequences, retries,
recovery, process completion, and goal achievement.

### `provider-neutral-reference`

Kind: `reference`. Owner: `dhms`.

This is the v3.6.1 local demonstration mapping around
`RuntimeGuardDecision`. It represents block/no-dispatch, allow/execute,
allow/execution-failure, allow/interruption, and sync/async parity. It is not a
production adapter and carries no deployment or provider-compatibility claim.

### `langgraph-tool-node`

Kind: `internal_adapter`. Owner: `dhms`.

This profile points to the existing explicit `LangGraphRuntimeGuardAdapter`
ToolNode wrapper. AgentFuse owns its bounded pre-dispatch decision; LangGraph
owns graph control flow, `GraphInterrupt`, checkpoint, and resume behavior.
The frozen tested version is `langgraph 1.2.11`. The dependency range is not a
claim that every future 1.x release is compatible. This is neither universal
ToolNode interception nor official LangGraph certification.

### `dsh-tools-pre-execute`

Kind: `external_adapter`. Owner: `external_project`.

The implementation remains in
`https://github.com/MkaliezZ/dsh-agentfuse-plugin`. The Python package contains
metadata and provenance only; it adds no DSH, Node.js, TypeScript, or
`@deepseek-ai` dependency. The reviewed mapping is bounded to DeepSeek Harness
`0.1.0-rc.7` at commit
`99f6f02fecdb7dff40c3fbc9470f5907c29f74ca` and the tested integrated
`Context` / `SystemPrompt` / `ToolRuntime` path.

The external plugin evidence reference is its merged commit
`366d213f207a833d45669b20551a33117eaeb6e6`; the `tested_commit` field records
the independently pinned upstream Harness commit, not the plugin commit.

DSH `ask` is host approval-deferral vocabulary, not a third canonical
AgentFuse action. Cases 05, 06, and 13 retain their frozen N/A boundaries; the
profile does not claim custom-policy callback behavior, separate sync/async
parity, or protection of all DSH paths.

## Conformance Provenance

- fixture version: `agentfuse-cross-adapter-conformance-v3.6.2`
- canonical fixture:
  `examples/conformance/cross_adapter_v3_6_2/fixtures.json`
- fixture SHA-256:
  `1f66c9e20ff28ebeeae128b8aaf38a5b251582496a753acded9530b819056d7b`
- frozen combined result: 52 PASS, 4 justified N/A, 0 FAIL
- LangGraph frozen tested version: `1.2.11`
- DSH frozen tested version: `0.1.0-rc.7`
- DSH frozen tested commit:
  `99f6f02fecdb7dff40c3fbc9470f5907c29f74ca`

The profiles reference this canonical fixture rather than duplicating it as a
second package data source.

## Import and Dependency Boundary

Importing `dhms_agentfuse.integrations` constructs only frozen Python metadata.
The registry does not import the DSH implementation, call Node.js, spawn a
subprocess, scan installed packages, access the network, or inspect arbitrary
files. Plain import/documentation references are strings, not live classes or
handlers.

The existing top-level package dependency on LangGraph is unchanged. The
registry itself does not dynamically import LangGraph merely to describe its
profile.

## Example

```python
from dhms_agentfuse.integrations import get_integration, list_integrations

for profile in list_integrations():
    print(profile.integration_id, profile.integration_kind, profile.tested_version)

dsh = get_integration("dsh-tools-pre-execute")
assert dsh.canonical_actions == ("allow", "block")
assert dsh.implementation_owner == "external_project"
```

## Supported Claims

- AgentFuse exposes immutable metadata for four reviewed integration mappings.
- Consumers can enumerate and retrieve the profiles deterministically.
- The profiles preserve canonical, reference, internal-adapter, and
  external-adapter distinctions.
- Capability metadata is bounded to frozen conformance evidence and tested
  versions.
- DSH metadata is bounded to the pinned external proof and adds no Python DSH
  dependency.
- Registry import performs no runtime discovery or protected-action execution.

## Explicit Non-Claims

v3.7.0 does not claim production readiness or production security; a universal
runtime abstraction; universal interception; automatic integration discovery
or plugin installation; official LangGraph or DeepSeek certification;
compatibility with every version in dependency ranges; exactly-once physical
execution; global no-replay; sandboxing; complete DLP; malware protection;
intrinsic action-danger classification; runtime enforcement by metadata
profiles; inclusion of external DSH code in the Python package; external
product adoption or validation; or product-market fit.

## Validation

```bash
python3.11 -m pytest tests/test_integrations.py -q
python3.11 -m pytest
python3.11 -m compileall -q dhms_agentfuse
python3.11 examples/conformance/cross_adapter_v3_6_2/run_conformance.py
python3.11 examples/conformance/cross_adapter_v3_6_2/run_conformance.py --json-only
python3.11 -m pip wheel . --no-deps --wheel-dir <temporary-directory>
git diff --check
```

The packaging check installs the built wheel into a clean temporary virtual
environment, imports the three public integration symbols, lists all profiles,
looks each one up, and safely serializes it without relying on repository-root
imports.

## Next Milestone

v3.7.1 Five-Minute Integration Trial is next and is not started by v3.7.0. The
external-consumer / real-trial conditional gate remains on v3.8.x, while v4.0
remains gated on real external use and compatibility stability.
