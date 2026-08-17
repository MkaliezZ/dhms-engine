# DHMS AgentFuse v3.6.3 Integration Result Review and Freeze

## Purpose

v3.6.3 freezes only what the reviewed v3.6.0-v3.6.2 integration line has
actually demonstrated. It adds no runtime, policy, evidence-schema, adapter,
approval, recovery, or execution capability.

## Reviewed Source State

| Item | Reviewed state |
|---|---|
| v3.6.1 merge | `96984766db2495d66959a189134391bd5cf7a8b5` |
| DHMS v3.6.2 merge | `028b592526c77c0806b447da7462b5d10713baf3` |
| DSH v0.1.1 conformance merge | `366d213f207a833d45669b20551a33117eaeb6e6` |
| RuntimeGuard core change in v3.6.2 | no |
| Evidence Schema change in v3.6.2 | no |
| LangGraph adapter change in v3.6.2 | no |

## Frozen v3.6.x Result

### v3.6.0 Public Decision API

`RuntimeGuardDecision` remains an immutable public pre-dispatch value with
`tool_call_id`, `tool_name`, `action`, `reason_code`, `policy_id`, and
evidence. Its canonical action is only `allow | block`.

`evaluate()` and `aevaluate()` accept a `ToolCallRequest`, not a protected
handler. `invoke()` and `ainvoke()` first reuse the same canonical decision
path, then may dispatch a supplied handler only after allow.

### v3.6.1 Consumer Integration Contract

The reviewed contract keeps these host lifecycle facts separate:

```text
policy decision
!= approval
!= dispatch
!= execution outcome
!= process completion
!= goal achievement
```

For a block, the reviewed host paths do not dispatch the protected action. An
allow permits host-owned progression only; it is not proof of handler start,
execution success, side effects, process completion, or goal achievement.

### v3.6.2 Cross-Adapter Conformance

The canonical fixture version is
`agentfuse-cross-adapter-conformance-v3.6.2`. It contains 14 deterministic,
provider-neutral cases and only the canonical actions `allow | block`.

| Case | Python RuntimeGuard | Reference consumer | LangGraph ToolNode | DSH pre-execute |
|---|---:|---:|---:|---:|
| 01 STATIC_ALLOW | PASS | PASS | PASS | PASS |
| 02 STATIC_BLOCK | PASS | PASS | PASS | PASS |
| 03 EXPLICIT_DENY_WINS | PASS | PASS | PASS | PASS |
| 04 NOT_ALLOWLISTED | PASS | PASS | PASS | PASS |
| 05 POLICY_EXCEPTION_FAIL_CLOSED | PASS | PASS | PASS | N/A |
| 06 INVALID_POLICY_DECISION_FAIL_CLOSED | PASS | PASS | PASS | N/A |
| 07 ALLOW_THEN_EXECUTE | PASS | PASS | PASS | PASS |
| 08 ALLOW_THEN_HANDLER_FAILURE | PASS | PASS | PASS | PASS |
| 09 ALLOW_THEN_INTERRUPT | N/A | PASS | PASS | PASS |
| 10 SAFE_RECEIPT | PASS | PASS | PASS | PASS |
| 11 DETERMINISTIC_REEVALUATION | PASS | PASS | PASS | PASS |
| 12 TOOL_CALL_IDENTITY | PASS | PASS | PASS | PASS |
| 13 SYNC_ASYNC_PARITY | PASS | PASS | PASS | N/A |
| 14 ONE_TERMINAL_SETTLEMENT | PASS | PASS | PASS | PASS |

Counts: Python-owned paths 41 PASS, 1 N/A, 0 FAIL. The independently rerun
DSH path is 11 PASS, 3 N/A, 0 FAIL. Combined result: 52 PASS, 4 justified N/A,
0 FAIL.

## Fixture Provenance and Tested Runtimes

- Canonical fixture source commit:
  `3ed2ccd0aadfcc61ad48ac5a49a54632f7911a91`
- Fixture SHA-256:
  `1f66c9e20ff28ebeeae128b8aaf38a5b251582496a753acded9530b819056d7b`
- DHMS CI runtime: Python 3.11.15, `langgraph 1.2.11`
- DSH proof runtime: Node 24, pnpm 11.7.0, DeepSeek Harness `0.1.0-rc.7`
  at `99f6f02fecdb7dff40c3fbc9470f5907c29f74ca`

The DSH repository consumes a byte-identical fixture snapshot plus source
commit and digest provenance. DHMS has no DSH runtime dependency, and the DSH
plugin has no Python runtime dependency.

## N/A Boundaries

- Python RuntimeGuard case 09: `invoke()` has no host interruption surface;
  interruption is proved by the reference consumer and LangGraph paths.
- DSH cases 05 and 06: the pinned TypeScript core has static policy
  configuration, not a call-level custom-policy callback surface.
- DSH case 13: the pinned `ToolRuntime` has one asynchronous execution path,
  not independent sync and async public paths.

These are absent capabilities, not skipped applicable failures.

## What the Review Proves

- In every applicable tested block path, protected handler/body invocation is
  zero before dispatch.
- `allow + execute` remains allow with an executed host outcome.
- `allow + handler failure` remains allow with `execution_failed`.
- `allow + interruption` remains allow with an interrupted host outcome.
- LangGraph interruption uses its installed real interrupt control flow;
  LangGraph owns pause, checkpoint, and resume semantics.
- Tested identities remain associated with their originating `tool_call_id`,
  and identical input/policy pairs retain deterministic digest and decision
  semantics.
- Safe decision/result/receipt/event/report serialization excludes the
  synthetic protected value, including sanitized failure reasons.
- One terminal settlement means one terminal result in the named tested path;
  it does not mean exactly-once physical execution or global no-replay.

## Authority Boundary

AgentFuse owns deterministic policy evaluation, canonical `allow | block`
decision evidence, and guarded dispatch only when the caller routes a handler
through that API. Hosts retain approval, action identity, risk and business
policy, physical execution, outcome recording, retries, recovery, process
completion, and goal completion.

DSH `ask` is host approval-deferral vocabulary. It is not a third canonical
AgentFuse action. The DSH result is bounded to the pinned integrated
`Context`/`SystemPrompt`/`ToolRuntime`/`tools/pre-execute`/`tools/execute`/
`tools/result` path; it does not cover all DSH paths.

## Supported Claims

- AgentFuse exposes an immutable, provider-neutral pre-dispatch `allow | block`
  decision contract.
- The four reviewed paths preserve canonical policy meaning separately from
  applicable later execution outcomes.
- The reviewed fixture set produced 52 PASS, 4 justified N/A, and 0 FAIL.
- Safe reviewed serialization surfaces exclude the synthetic protected value.
- DSH conformance is limited to its pinned tested harness commit/version.
- LangGraph conformance is limited to `langgraph 1.2.11`, the version resolved
  in the reviewed CI environment.

## Explicit Non-Claims and Known Limitations

v3.6.x does not prove production readiness or production security; universal
interception; arbitrary unwrapped-path protection; official LangGraph or
DeepSeek certification; future upstream compatibility; exactly-once physical
execution; global no-replay; distributed transaction safety; complete DLP or
secret detection; process sandboxing; malware prevention; intrinsic action
danger classification; arbitrary action correctness; external product
adoption; external product validation; or product-market fit.

The LangGraph dependency range is not a future compatibility promise. DSH
claims are only for the pinned upstream integration path. External stars,
issues, comments, and technical alignment remain interest evidence, not
deployment or product validation.

## Validation

```bash
python3.11 -m pytest tests/test_cross_adapter_conformance_v3_6_2.py -q
python3.11 -m pytest
python3.11 -m compileall -q dhms_agentfuse
python3.11 examples/conformance/cross_adapter_v3_6_2/run_conformance.py
python3.11 examples/conformance/cross_adapter_v3_6_2/run_conformance.py --json-only
python3.11 -m pip wheel . --no-deps --wheel-dir /tmp/dhms-agentfuse-wheel
git diff --check
```

The independent DSH proof is reproduced by its merged conformance workflow:
frozen-lockfile install, pinned upstream checkout, TypeScript build, core and
adapter/conformance tests, then the DSH matrix renderer.

## Freeze Verdict and Next Milestone

`READY_FOR_V3_6_3_REVIEW`

v3.6.x integration evidence is frozen. The next planned milestone is v3.7.0
Multi-Runtime Integration Package. It remains gated on actual consumer need and
external integration evidence, and is not started by this freeze.
