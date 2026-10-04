# AgentFuse Attempt-Scoped Lifecycle Evidence v0.3

## External problem source and evidence boundary

On 2026-10-04, GitHub user `impartshadow` [reported a lifecycle mapping
gap](https://github.com/crewAIInc/crewAI/issues/6221#issuecomment-5975614702)
after exercising AgentFuse against a retained crash/recovery artifact from
[crewAIInc/crewAI#5802](https://github.com/crewAIInc/crewAI/issues/5802).
The report describes two attempts sharing a logical action ID. The original
dispatch had unknown execution state and an observed receiver effect; the
same-ID retry was rejected before receiver invocation.

The initial milestone added a deterministic **external-reported trace fixture**
derived from that public comment. At that stage, the retained artifact had not
been imported or independently replayed. That comment-derived fixture contains
no receiver payload, receipt, database, authentication material, or invented
runtime details. The following flags describe that initial fixture; the exact
redacted issue #15 replay is documented separately below.

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

## Exact External Issue #15 Replay

On 2026-10-05, the sole JSON artifact in
[MkaliezZ/dhms-engine#15](https://github.com/MkaliezZ/dhms-engine/issues/15),
authored by `impartshadow` on 2026-10-04, was fetched directly from the issue
body and preserved as
`tests/fixtures/attempt_lifecycle_v0_3_external_issue_15.json`. No source fields
or values were changed. The fixture is 1,495 bytes with a final newline;
its SHA-256 is
`7fd524dd3910c77da89f1376f40b1b89d7f5d2e96980512b5621ded25386dd41`.
That digest pins the fetched redacted snapshot, not artifact authenticity.

A test-local pure mapper parses the external `shadow.redacted-attempt-trace.v1`
artifact and creates two existing `AttemptLifecycleEvidenceRecord` values.
Their logical action reference and distinct attempt references are preserved.
Output `record_id` values are local fixture labels, not claimed external IDs.
No production schema, public API or runtime behavior was changed.

The allowed original attempt's external `block_stage=none` maps conservatively
to AgentFuse `unknown`: no AgentFuse denial stage is asserted, and this does
not mean a block occurred. Its lifecycle remains `started / unknown / observed`.
The blocked retry retains `pre_dispatch / not_started / not_executed / proven_none`
and passes `is_strict_pre_dispatch`.

Both mapped records have `non_execution=None`. The host-native
`ACTION_ALREADY_RECORDED` metadata do not supply the complete v0.1 metadata;
no approval ID, call ID, result reference or canonical reason is fabricated.
The existing separate synthetic test still proves that valid AgentFuse
`NonExecutionEvidence` can be attached when all required metadata exist.

Receiver evidence stays under attempt 1 in the exact external fixture and
supports its `observed` state. Runtime evidence, redactions, retry-native
non-execution evidence and `derived_host_policy` remain unchanged source data.
They are not added to AgentFuse records. Correlation retains both intact
attempts: retry `proven_none` neither erases the original effect nor inherits it.
The host's `reconcile_do_not_redispatch` conclusion remains host-owned; the
original unknown completion and observed effect do not establish safe automatic
redispatch. AgentFuse supplies no retry or reconciliation operation.

Here, independent artifact replay means parsing and mapping the exact external
**redacted** artifact through existing types and checking attempt/lifecycle
invariants. It does not mean executing CrewAI, SQLite or the receiver, physically
reproducing #5802, proving authenticity, or establishing adoption.

```text
ISSUE15_ARTIFACT_IMPORTED=true
EXACT_REDACTED_FIXTURE_PRESERVED=true
REDACTED_EXTERNAL_ARTIFACT_REPLAY=true
RAW_EXTERNAL_ARTIFACT_REPLAY=false
ORIGINAL_RUNTIME_REPLAYED=false
ARTIFACT_AUTHENTICITY_PROVEN=false
RUNTIME_ATTESTATION_PROVEN=false
EXTERNAL_SCHEMA_VALIDATION_PROVEN=true
EXTERNAL_VALIDATION_PROVEN=false
ADOPTION_PROVEN=false
```

`EXTERNAL_SCHEMA_VALIDATION_PROVEN` means only that a real external user's
redacted crash/recovery artifact was independently mapped against AgentFuse
attempt-scoped lifecycle schema v0.3 and the required attempt/lifecycle
invariants passed. It carries no broader external validation claim.

Validation uses Python 3.11 with the current package installed in a separate
virtual environment. The commands above cover the unchanged 29 v0.2 tests,
the unchanged 36 v0.3 cases plus 14 exact-artifact cases (50 total), the full
230-test suite, compileall and diff checks. All passed.

## External Operator Rerun: Issue #15 Freeze

Evidence classification: `EXTERNAL_OPERATOR_RERUN`.
Status: frozen for this reported path and merged shape only.

Sources in [issue #15](https://github.com/MkaliezZ/dhms-engine/issues/15):

- [`impartshadow` rerun report, comment 5983874570](https://github.com/MkaliezZ/dhms-engine/issues/15#issuecomment-5983874570),
  posted 2026-10-04 at 20:04:13 UTC.
- [Maintainer confirmation, comment 5984122387](https://github.com/MkaliezZ/dhms-engine/issues/15#issuecomment-5984122387),
  posted by `MkaliezZ` at 20:34:01 UTC that day.

The operator explicitly reports a new run against merged commit
`4f8c0facfa7ff23a1f5df2e2c1dfc3fdc0a3eef9`, using the actual Reality Layer
`4213c479` plus agent-contracts crash/recovery pilot in an isolated checkout
with a fresh SQLite receiver. Fresh outcomes were then projected through
`AttemptLifecycleEvidenceRecord` and `correlate_attempt_lifecycle_records`.
This is a new external operator rerun of the merged attempt-scoped shape,
distinct from reading the schema or our earlier replay of the redacted JSON.

The reported results are:

| Boundary | Operator-reported outcome |
| --- | --- |
| Commit-before-ack crash | Receiver observed exactly one effect. |
| Recovered original attempt | Runtime status remained `UNKNOWN`; reconciliation remained `REQUIRED`. Projection: `unknown / started / unknown / observed`. |
| Same-action retry | Host rejected `ACTION_ALREADY_RECORDED`; no second effect. Separate attempt projection: `pre_dispatch / not_started / not_executed / proven_none`. |
| Correlation | One logical action retained two distinct attempt references; neither record borrowed nor fabricated v0.1 non-execution metadata. |
| Focused checks | Operator reported 79 passing merged v0.2/v0.3 focused cases; this is the operator's result, not a new local test run in this documentation task. |

Receiver evidence stays scoped to the original attempt. The retry's strict
non-execution evidence cannot be borrowed to label the original attempt as
unexecuted or effect-free; the original's observed effect cannot be attributed
to the retry. The operator also reports that the September 30 retained ledger
and receiver were left untouched, still at `UNKNOWN`/`REQUIRED` with one effect.
The fresh rerun and that retained evidence are distinct.

The mapping limitation remains explicit: the host-native trace knows that no
denial applied (`block_stage=none`), while the neutral projection uses
`block_stage=unknown`. A neutral lifecycle projection is not a lossless
replacement for the host-native trace. The original host trace and receiver
evidence must remain alongside it to preserve that distinction. No source-native
rejection metadata are turned into fabricated AgentFuse `NonExecutionEvidence`.

The maintainer's subsequent reply acknowledges the rerun and these same
boundaries. It is confirmation of the recorded interpretation, not another
independent runtime test or certification. The source evidence for this entry
is the operator's public report; this documentation task did not independently
execute the fresh crash/recovery setup.

This evidence does **not** prove independent AgentFuse certification,
production integration, general runtime enforcement, runtime retry permission,
or that every agent, runtime or framework satisfies the reported property.
Retry and reconciliation remain host-owned. No new proof claim is introduced:
the earlier bounded schema/artifact-mapping claim is unchanged, and
`EXTERNAL_VALIDATION_PROVEN=false` and `ADOPTION_PROVEN=false` remain unchanged.

This validation line is frozen at the cited operator report and maintainer
confirmation. The freeze records those facts and limits only; it authorizes
no new schema, implementation, adapter, release or subsequent milestone.
