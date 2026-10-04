# AgentFuse Attempt-Scoped Lifecycle Evidence v0.3

## External problem source and evidence boundary

On 2026-10-04, GitHub user `impartshadow` [reported a lifecycle mapping
gap](https://github.com/crewAIInc/crewAI/issues/6221#issuecomment-5975614702)
after exercising AgentFuse against a retained crash/recovery artifact from
[crewAIInc/crewAI#5802](https://github.com/crewAIInc/crewAI/issues/5802).
The report describes two attempts sharing a logical action ID. The original
dispatch had unknown execution state and an observed receiver effect; the
same-ID retry was rejected before receiver invocation.

This repository contains a deterministic **external-reported trace fixture**
derived from that public comment. The retained artifact itself has not been
imported or independently replayed. The fixture contains no receiver payload,
receipt, database, authentication material, or invented runtime details.

```text
EXTERNAL_REPORTED_TRACE_FIXTURE=true
REAL_EXTERNAL_TRACE_MAPPING_REPORTED=true
INDEPENDENT_ARTIFACT_REPLAY=false
EXTERNAL_SCHEMA_GAP_IDENTIFIED=true
ATTEMPT_SCOPED_LIFECYCLE_GAP=true
EXTERNAL_VALIDATION_PROVEN=false
ADOPTION_PROVEN=false
```

## Why one denial record cannot represent both attempts

`LifecycleEvidenceRecord` remains a v0.2 denial-like record accepting only
`block` or `escalate`. The original host-dispatched attempt must not acquire
an invented policy denial just to fit that type. Combining both attempts
would also incorrectly transfer the original receiver effect to the blocked
retry, or transfer the retry's strict non-execution claim to the original.

The additive v0.3 shape is:

```text
logical_action_ref = agent-contracts-reality-pilot-001
    |
    +-- attempt_ref = agent-contracts-reality-pilot-001:attempt:1
    |       dispatch=started / execution=unknown / side_effect=observed
    |
    +-- attempt_ref = agent-contracts-reality-pilot-001:attempt:2
            pre_dispatch / not_started / not_executed / proven_none
```

The observed receiver effect belongs only to attempt 1. Attempt 2's
`proven_none` is relative to that attempt; it does not erase the effect of
attempt 1 or claim that the logical action had no effects overall.

## Neutral attempt envelope

`AttemptLifecycleEvidenceRecord` is a frozen data record exported from
`dhms_agentfuse` and defined in `dhms_agentfuse.attempt_lifecycle`:

| Field | Meaning |
| --- | --- |
| `record_id` | Identifier for this evidence record. |
| `schema_version` | `agentfuse-attempt-lifecycle-evidence-schema-v0.3`. |
| `logical_action_ref` | Host-supplied correlation reference grouping attempts. |
| `attempt_ref` | Host-supplied identifier for one distinct attempt. |
| `lifecycle` | Existing validated `ExecutionLifecycleEvidence`, scoped to this attempt. |
| `non_execution` | Optional existing `NonExecutionEvidence`, admissible only with the strict lifecycle below. |

The minimal envelope does not require or manufacture policy metadata. A host
can retain existing decision records separately under its attempt identity.
An allowed or host-dispatched attempt is representable without a denial
decision. The original fixture uses `block_stage=unknown` because no denial
stage was reported; this is not a claim that a block occurred. The v0.2 state
vocabulary is unchanged and no `not_applicable` value is added.

All identity fields must be nonempty strings. `logical_action_ref` groups
attempts; it does not imply identical decisions, execution, outcomes, side
effects or execution success. Different attempts require different
`attempt_ref` values even when the host reuses a tool-call ID.

`correlate_attempt_lifecycle_records(records)` is a pure collection helper.
It returns a dictionary from logical action reference to a tuple of the
original, intact records. It rejects every duplicate `attempt_ref` across
the input, including across logical actions; it never silently overwrites or
deduplicates. Input order is preserved and does not establish chronology.
It performs no evidence aggregation, policy evaluation, retry or dispatch.

```python
from dhms_agentfuse import (
    ATTEMPT_LIFECYCLE_SCHEMA_VERSION,
    AttemptLifecycleEvidenceRecord,
    ExecutionLifecycleEvidence,
    correlate_attempt_lifecycle_records,
)

action = "agent-contracts-reality-pilot-001"
original = AttemptLifecycleEvidenceRecord(
    record_id="example:original",
    schema_version=ATTEMPT_LIFECYCLE_SCHEMA_VERSION,
    logical_action_ref=action,
    attempt_ref=f"{action}:attempt:1",
    lifecycle=ExecutionLifecycleEvidence("unknown", "started", "unknown", "observed"),
)
retry = AttemptLifecycleEvidenceRecord(
    record_id="example:retry",
    schema_version=ATTEMPT_LIFECYCLE_SCHEMA_VERSION,
    logical_action_ref=action,
    attempt_ref=f"{action}:attempt:2",
    lifecycle=ExecutionLifecycleEvidence(
        "pre_dispatch", "not_started", "not_executed", "proven_none"
    ),
)
attempts = correlate_attempt_lifecycle_records((original, retry))[action]
assert attempts[0].lifecycle.side_effect_state == "observed"
assert attempts[1].lifecycle.side_effect_state == "proven_none"
assert attempts[0].lifecycle.execution_state == "unknown"
```

## Strict non-execution and fixture provenance

Attaching `NonExecutionEvidence` requires all four existing strict facts:

```text
block_stage=pre_dispatch
dispatch_state=not_started
execution_state=not_executed
side_effect_state=proven_none
```

It is rejected on the original attempt. The blocked retry may carry it when
the host can supply valid, attempt-scoped v0.1 denial metadata. Unlike the
denial-like v0.2 combined record, a neutral envelope does not require that
metadata merely because strict lifecycle facts are available.

The public report names the host's rejection `ACTION_ALREADY_RECORDED` but
does not supply all v0.1 `NonExecutionEvidence` fields or a canonical v0.1
reason. That host code is not silently remapped to `policy_denied`, and no
approval, tool-call, result or policy identifier is fabricated. Both fact
fixture records therefore have `non_execution=null`. Focused tests separately
attach the existing synthetic denial example to a strict retry to prove schema
support; those synthetic metadata are explicitly not external artifact facts.
Fixture `record_id` values are local labels. The original `block_stage=unknown`
records the absence of a supplied denial stage.

## Host-owned retry and reconciliation

The Consumer Integration Contract continues to assign physical dispatch,
execution outcomes, side effects, retries and recovery to the host.
AgentFuse adds no retry engine or orchestration instruction.

For evidence interpretation, a necessary precondition for a potentially safe
retry is strict non-execution for every relevant prior attempt. Any prior
attempt with `observed`, `possible` or `unknown` side-effect state fails that
condition. Unknown dispatch or execution also cannot establish strict
non-execution. Passing this evidence condition does not itself authorize a
retry; the host still owns policy and reconciliation. The public evaluator's
reported conclusion for #5802 was reconciliation rather than redispatch.

## Compatibility and limits

Existing v0.1 and v0.2 types, factories, validation and serialization remain
unchanged. Existing callers need not migrate. The v0.2 schema-version constant
and package release version are unchanged. Observed side effects do not
convert `execution_state=unknown` into `executed` or `not_executed`.

The envelope preserves supplied facts; it does not authenticate their origin
or prove that a caller labelled an attempt correctly. The correlation helper
never transfers evidence between attempts. It checks uniqueness only within
its input; hosts own durable ID allocation and completeness of prior history.
There is no persistent deduplication ledger, distributed transaction protocol,
receiver authentication, runtime attestation or exactly-once guarantee.

```text
Decision != Outcome
Blocked != Failed
Unknown > fabricated certainty
Projection != Execution Control
```

## Deterministic regression checks

The fact fixture is `tests/fixtures/attempt_lifecycle_v0_3_external_report.json`.
It is read as data, never executed against CrewAI or a receiver.

```bash
python -m pytest tests/test_agentfuse_evidence_lifecycle_v0_2.py -q
python -m pytest tests/test_agentfuse_attempt_lifecycle_v0_3.py -q
python -m pytest -q
python -m compileall -q dhms_agentfuse
git diff --check
```
