# DHMS AgentFuse v3.7.2 Compatibility Matrix and CI

## Purpose and Relationship to v3.7.1

v3.7.2 turns the bounded v3.7.1 clean-wheel LangGraph consumer trial into a
small, repeatable GitHub Actions compatibility matrix. It records only exact
tested combinations and does not add a new adapter, execution engine, or policy
semantic.

The matrix covers the maintained `langgraph-tool-node` mapping. The
`python-runtime-guard` path remains covered by ordinary local/core CI, the
`provider-neutral-reference` profile remains a reference mapping, and
`dsh-tools-pre-execute` remains external-evidence-only in its independently
owned project.

## Exact Matrix Philosophy

The checked-in manifest is
[`validation/compatibility_v3_7_2/compatibility_matrix.json`](../validation/compatibility_v3_7_2/compatibility_matrix.json).
It defines these exact cells:

| Roles | Python | LangGraph |
| --- | --- | --- |
| Python floor, frozen runtime baseline | `3.10` | `1.2.11` |
| Declared runtime floor | `3.11` | `1.2.0` |
| Frozen baseline, current stable | `3.11` | `1.2.11` |

The matrix is intentionally not a full Cartesian product. Python `3.12` and
newer are not claimed by this milestone. Each cell uses exact pins; no cell
contains a range, wildcard, prerelease, yanked release, or mutable `latest`
value.

## Version Discovery

The package declares `langgraph>=1.2,<2.0`, so `1.2.0` is the conceptual
declared floor. The frozen v3.6.x/v3.7.1 profile provenance remains `1.2.11`.
On 2026-08-18, the authoritative PyPI JSON metadata at
`https://pypi.org/pypi/langgraph/json` reported `1.2.11` as the current stable
release. PyPI metadata also showed `1.2.0` and `1.2.11` as non-yanked stable
releases. The current-stable candidate therefore deduplicates with the frozen
baseline cell.

The declared dependency range is resolver eligibility, not compatibility
evidence for every release in that range. Only successful cells from the real
GitHub Actions run support compatibility claims.

## Frozen Profile Provenance

`get_integration("langgraph-tool-node").tested_version` remains `1.2.11`. That
field identifies frozen reviewed profile evidence; it is not rewritten to the
newest matrix candidate. The manifest and probe record both the frozen profile
version and the candidate runtime version as separate facts.

## Build-Once Wheel CI

The workflow keeps the existing Python 3.11 editable-install full regression
job. A separate `build-wheel` job builds exactly one
`dhms_agentfuse-3.7.2-py3-none-any.whl` and uploads it as
`agentfuse-wheel-v3-7-2`. The same job converts the reviewed manifest into the
GitHub Actions matrix output.

Every compatibility cell downloads that same wheel artifact. Cells do not
rebuild AgentFuse and do not use `pip install -e .`.

## Clean-Wheel External Execution

Each compatibility cell checks out the repository only to read the reviewed
manifest and copy the probe. It then:

1. installs the shared AgentFuse wheel and exact LangGraph pin;
2. copies only `probe.py` into a `RUNNER_TEMP` directory;
3. executes from that directory with `PYTHONPATH` removed;
4. rejects an AgentFuse import whose resolved origin is under
   `GITHUB_WORKSPACE`; and
5. uploads one safe JSON compatibility result.

This establishes source-fallback protection for the tested CI cell. It is not a
general package isolation or sandbox guarantee.

## Compatibility Probe and Invariants

The public-API probe imports `RuntimeGuard`,
`LangGraphRuntimeGuardAdapter`, and `get_integration`. It builds a real
`StateGraph(MessagesState)`, creates the existing wrapped `ToolNode`, and
invokes one synthetic allow call and one synthetic block call.

For a passing cell:

- allow records `decision=allow`, starts the selected handler, preserves the
  tool-call identity, and increments the allow counter exactly once;
- block records `decision=block` and `outcome=not_executed`, observes no
  dispatch, preserves identity, and leaves the protected counter at zero; and
- decision and execution outcome remain separate facts. A selected successful
  allow case does not make `allow` a universal success guarantee.

The probe uses explicit `RuntimeError` validation rather than optimization-
removable assertions. The synthetic protected argument is excluded from JSON
output and CI result artifacts.

## Machine-Readable Artifacts

Each cell uploads one artifact named from its exact Python and LangGraph
versions. The JSON records the matrix version, package and runtime versions,
observed `langchain-core` version, frozen profile provenance, source-isolation
result, allow/block observations, local-runtime requirements, and verdict. It
contains no wheel, virtual environment, cache, credential, or raw protected
argument.

## CI Architecture and Safety

The workflow has three functional layers:

1. `test`: editable-install full pytest and compileall regression coverage;
2. `build-wheel`: one wheel plus the manifest-derived matrix output; and
3. `compatibility`: `fail-fast: false` exact-version cells consuming the same
   wheel.

Workflow permissions are read-only. It uses no secret, provider API key, model
call, runtime network service, PR title/body evaluation, DSH runtime, or write
permission. Package installation may use the package index; the probe itself
performs only in-memory local tool calls.

## Failure Classification

A red cell must be investigated rather than removed. Useful classifications
are `UPSTREAM_COMBINATION_UNAVAILABLE`, `DEPENDENCY_RESOLUTION_FAILURE`,
`AGENTFUSE_IMPORT_INCOMPATIBILITY`, `LANGGRAPH_ADAPTER_INCOMPATIBILITY`,
`TRIAL_SEMANTIC_FAILURE`, and `INFRASTRUCTURE_FAILURE`. A reproducible failure
inside the declared resolver range is compatibility evidence and may require a
separately justified range narrowing or adapter correction.

## Supported Claims

After the corresponding GitHub Actions run is green, AgentFuse may claim that
the exact listed combinations installed the same v3.7.2 wheel outside the
source tree and passed the bounded allow-once/block-zero-dispatch probe. The
machine-readable artifacts may be cited for their exact observed package,
Python, LangGraph, and `langchain-core` versions.

## Explicit Non-Claims

v3.7.2 does not claim compatibility with every release in
`langgraph>=1.2,<2.0`, all LangGraph 1.x versions, future LangGraph releases,
every Python version at or above 3.10, official LangGraph certification,
universal runtime compatibility, DSH runtime CI coverage in this repository,
production readiness, production security, external adoption, product
validation, product-market fit, exactly-once physical execution, global
no-replay, sandboxing, DLP, malware prevention, or arbitrary application
correctness from a green cell.

## Local Validation

```bash
python3.11 -m pip install -e . "langgraph==1.2.11"
python3.11 -m pytest tests/test_compatibility_matrix_v3_7_2.py -q
python3.11 validation/compatibility_v3_7_2/probe.py \
  --expected-python-version 3.11 \
  --expected-langgraph-version 1.2.11 \
  --expected-package-version 3.7.2 \
  --json-only
python3.11 -m pytest
python3.11 -m compileall -q dhms_agentfuse validation/compatibility_v3_7_2
```

Local validation does not substitute for the real Python 3.10 and wheel-based
GitHub Actions cells.

## Known Limitations and Next Milestone

The matrix covers one reviewed explicit LangGraph ToolNode wrapper and three
exact Python/runtime cells. It does not cover every eligible dependency
version, every Python version, unwrapped LangGraph execution, provider/model
behavior, or the external DSH runtime.

v3.7.3 Integration Release Seal is the next milestone and is not started by
v3.7.2. The v3.8.x external-consumer/real-trial gate and v4.0 real external
use/compatibility-stability gate remain unchanged.
