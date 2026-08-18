# AgentFuse v3.7.3 Integration Release Seal

## Release

AgentFuse v3.7.3 is the **Experimental Public Beta** release of the existing
fail-closed pre-dispatch boundary for side-effect-capable AI agent tools. It
packages and exposes the already-reviewed RuntimeGuard, LangGraph ToolNode
integration, integration metadata, compatibility evidence, and five-minute
consumer trial. It adds no runtime capability or policy semantics.

The machine-readable seal is
[`release/agentfuse_v3_7_3_release_seal.json`](../release/agentfuse_v3_7_3_release_seal.json).
Its `canonical_source_commit` is the frozen v3.7.2 runtime-source baseline
inherited by this release. The v3.7.3 tag separately identifies the final
release commit.

## Proven Runtime Behavior

Within the explicit guarded paths:

- a trusted policy `allow` can reach the supplied handler;
- a trusted policy `block` returns before dispatch;
- the tested allow path starts its handler exactly once;
- the tested block path starts its protected handler zero times;
- policy exceptions and malformed policy results fail closed; and
- tool-call identity and safe evidence remain available at the boundary.

This evidence does not cover direct or unwrapped execution paths.

## Evidenced Integrations

The public metadata registry exposes four bounded profiles:

- `python-runtime-guard`
- `provider-neutral-reference`
- `langgraph-tool-node`
- `dsh-tools-pre-execute`

Profiles describe reviewed mappings. They do not discover runtimes, execute
tools, or make different host lifecycles equivalent.

## Compatibility Evidence

Both PR review CI and post-merge CI passed these exact cells:

| Python | LangGraph | Allow handler | Block handler | Block dispatch |
| --- | --- | ---: | ---: | --- |
| 3.10 | 1.2.11 | 1 | 0 | false |
| 3.11 | 1.2.0 | 1 | 0 | false |
| 3.11 | 1.2.11 | 1 | 0 | false |

PR #11 reviewed head `bbc4bf8bf9d66c347c05939385ff0b82a3949df0`
with CI run `32051700104`. Post-merge CI run `32095927125` validated
merge `ae3d75287415d8c80a1726a73dbee1ef3deb6421`.

The review wheel SHA-256 was
`317bf6967b4ce881754b9c1c313c0bfe8abbc014e1e98bfe852cd8c49f3903b4`.
The post-merge wheel SHA-256 was
`cc6e95a10ea529e6cd29bc279c3ecf2c621351ef31563ab0d6affd6acffecce0`.
These were separately built artifacts that passed the same bounded
invariants. Their differing hashes are not a byte-identical reproducible-build
claim. The observed `langchain-core` version moved from 1.5.5 to 1.5.6 while
the exact cells remained green; this does not prove compatibility with
arbitrary future transitive versions.

Artifact IDs and exact matrix-result references are recorded in the JSON seal.

## Install

PyPI publication is not assumed. The truthful source installation for the
tagged release is:

```bash
python -m pip install \
  "dhms-agentfuse @ git+https://github.com/MkaliezZ/dhms-engine.git@v3.7.3"
```

The GitHub Release also carries a wheel and source distribution.

## Five-Minute Trial

To run the canonical bounded consumer trial from source:

```bash
git clone --branch v3.7.3 --depth 1 \
  https://github.com/MkaliezZ/dhms-engine.git agentfuse-beta
cd agentfuse-beta
python -m pip install -e . "langgraph==1.2.11"
python examples/integration_trial/five_minute_v3_7_1/run_trial.py
```

Expected evidence includes one allow handler invocation and zero protected
block handler invocations. No LLM provider, API key, or runtime external
service is required. See the
[full trial guide](dhms_agentfuse_five_minute_integration_trial_v3_7_1.md).

## Public Beta Integration Request

If you maintain an agent runtime or an agent with side-effect-capable tools,
[open a Beta Integration Request](https://github.com/MkaliezZ/dhms-engine/issues/new?template=agentfuse-beta-integration.yml)
with the repository, runtime/framework, and one protected tool or action. This
is an invitation to map the first bounded integration, not a guarantee of
indefinite engineering support.

## Boundaries

AgentFuse v3.7.3 does not claim production readiness, production security,
universal interception, a sandbox, malware detection, DLP, exactly-once
physical execution, global replay protection, compliance certification,
official LangGraph or DSH certification, enterprise readiness, or external
adoption. Evidence applies only to the explicit versions and guarded paths
recorded in the seal.

## Next Milestone

Public beta feedback now controls product architecture. No v3.8 milestone
starts merely because it is numerically next. A future change must respond to
concrete integration friction such as provenance, approval identity, replay
boundaries, API simplicity, another runtime mapping, deployment, installation,
or observability.
