# DHMS Runtime Adapter Proposal Examples v0

These examples are inert documentation/data only.

They are not runtime adapter tutorials, SDK integration examples, network
recipes, shell instructions, terminal usage guides, or operational tool
invocation recipes.

Runtime adapter proposals are treated as data. DHMS observes the proposal,
normalizes adapter intent, classifies the runtime target and requested
capability, assigns a policy decision, plans trace evidence, and confirms that
execution is not performed.

For v1.2.3, allowed policy decisions remain:

* `HOLD`
* `BLOCK`
* `FAIL_CLOSED`

`RELEASE` is not used in v1.2.3.

The examples in `inert_examples.json` are compact reader aids linked to the
static runtime adapter proposal manifest:

`benchmarks/dhms_runtime_adapter_proposals_v0/cases.json`

The complete non-executing trace plan is:

`trace_examples/dhms_runtime_adapter_proposals_v0/trace_plan.json`

These examples do not implement runtime adapters, call SDKs, invoke tools, make
network calls, execute shell/subprocess/terminal behavior, access credentials,
access user data, touch production runtimes, add benchmark runners, add proof
runners, add CLI commands, or add schemas.
