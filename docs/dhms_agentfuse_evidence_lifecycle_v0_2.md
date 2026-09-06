# AgentFuse Evidence Lifecycle Schema v0.2

## Purpose

External technical feedback identified an evidence-modeling gap in Evidence
Schema v0.1. This document records the bounded, additive schema work that
answers it. DHMS / AgentFuse remains an SDK-free Agent Runtime Governance
Layer; this milestone models evidence only and changes no runtime behavior.

## External-feedback trigger

Two concrete inputs triggered this work:

1. LangChain Forum external feedback observed that
   `side_effect_occurred=false` is only provable when the block happened
   before dispatch. Once dispatch has started, side-effect reality may be
   unknown, so it should not be modeled as one boolean state.
2. An independent real-world counterexample pattern (Anthropic Claude Code
   issue #77185) reported a case where a policy/classifier returned a denial,
   Bash execution had already occurred, and real external side effects had
   already been applied. Reporting that lifecycle as simply `not_executed`
   would contradict reality.

No adoption, validation, or endorsement by any external project is claimed.
This schema is an AgentFuse-side modeling response to publicly observable
feedback patterns.

## Policy decision vs execution reality

v0.1 already separates a policy decision from an execution outcome. v0.2
makes the remaining lifecycle facts explicit and individually observable:

```text
model intent
!= policy decision
!= dispatch reality
!= execution reality
!= side-effect reality
```

A denial states what policy concluded. It does not, by itself, state what the
host runtime physically did. A denial that races with dispatch can coexist
with a started dispatch, an executed handler, and observed side effects.

## Why v0.1 NonExecutionEvidence remains strict

`NonExecutionEvidence` continues to mean exactly what it meant in v0.1: a
call for which non-execution is affirmatively established. Its fields keep
their existing meaning and types:

```text
execution = not_started
payload_executed = false
side_effect_occurred = false
```

These fields were not converted into tri-state values. Post-dispatch denial
cases are not forced into this strict type; they are represented by the new
additive v0.2 types below. The v0.1 module `evidence_schema.py` is unchanged
by this milestone.

## Block stage

`ExecutionLifecycleEvidence.block_stage` records when the denial was
established relative to dispatch:

| State | Meaning |
| --- | --- |
| `pre_dispatch` | The block was proven before dispatch started. Implies strict non-execution (see invariants). |
| `post_dispatch` | The denial was established after dispatch had already started. |
| `unknown` | The stage could not be determined from available evidence. |

## Dispatch, execution, and side-effect states

| Field | Canonical states |
| --- | --- |
| `dispatch_state` | `not_started`, `started`, `unknown` |
| `execution_state` | `not_executed`, `executed`, `partially_executed`, `unknown` |
| `side_effect_state` | `proven_none`, `observed`, `possible`, `unknown` |

Side-effect reality is intentionally not a boolean. `proven_none` is an
affirmative proof of no side effect, `observed` means a side effect was
applied, `possible` means a side effect may have occurred without proof either
way, and `unknown` means the fact is missing or ambiguous.

## Claude Code #77185 as a counterexample pattern

The issue describes a denial race: policy said block, but execution had
already happened with real external side effects. The v0.2 representation of
that pattern is:

```text
boundary_decision.decision = block
lifecycle.block_stage       = post_dispatch
lifecycle.dispatch_state    = started
lifecycle.execution_state   = executed
lifecycle.side_effect_state = observed
non_execution               = None
```

This record is valid v0.2 evidence. Attaching strict `NonExecutionEvidence`
to it is rejected, because `side_effect_occurred=false` would contradict the
observed reality. This schema models such evidence; it does not solve or
claim to solve the underlying race in any runtime.

## Required invariants

`ExecutionLifecycleEvidence` rejects internally contradictory combinations:

- A proven `pre_dispatch` block must imply `dispatch_state=not_started`,
  `execution_state=not_executed`, and `side_effect_state=proven_none`. This
  is the strict case that corresponds to `NonExecutionEvidence`.
- A `started` dispatch cannot carry `block_stage=pre_dispatch` (contrapositive
  of the above).
- `executed` or `partially_executed` execution cannot coexist with
  `dispatch_state=not_started`.
- An `observed` side effect cannot claim strict pre-dispatch non-execution.
- Missing or ambiguous facts remain `unknown`; the schema provides no path
  that converts missing evidence into proof of non-execution.

`LifecycleEvidenceRecord` additionally requires that `non_execution` evidence
appear only on strict pre-dispatch records, that strict pre-dispatch blocked
or escalated records include it, and that allowed records omit it.

## Compatibility guarantees

- Evidence Schema v0.1 remains valid and semantically unchanged; the v0.1
  module is untouched.
- Existing v0.1 imports, factories, and `to_dict()` serialization shapes are
  unchanged.
- v0.2 reuses the v0.1 building blocks (`PolicyResolutionEvidence`,
  `LayeredBoundaryDecision`, `SafeTraceMetadata`, `NonExecutionEvidence`)
  rather than duplicating them.
- The v0.2 schema version string is
  `agentfuse-evidence-lifecycle-schema-v0.2`.

## Non-goals

- No runtime behavior change: no change to dispatch, policy evaluation,
  approval, tool execution, adapters, or guarded invocation semantics.
- No side-effect detection, rollback, dry-run execution, sandboxing, or
  tracing infrastructure.
- No attempt to solve or mitigate the Claude Code #77185 race itself; only
  its truthful evidence representation is modeled.
- No v3.8.x product-line start, no package version bump for this schema work
  alone, and no change to the 3.7.3 public decision API.
- No claim of external adoption, external trial, or validation by any
  external project.
