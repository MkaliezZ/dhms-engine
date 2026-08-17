"""Static registry of reviewed AgentFuse integration mappings."""

from __future__ import annotations

from types import MappingProxyType

from .model import IntegrationProfile


_FIXTURE_VERSION = "agentfuse-cross-adapter-conformance-v3.6.2"
_FIXTURE_DIGEST = "1f66c9e20ff28ebeeae128b8aaf38a5b251582496a753acded9530b819056d7b"
_FIXTURE_REFERENCE = "examples/conformance/cross_adapter_v3_6_2/fixtures.json"
_FREEZE_REFERENCE = (
    "docs/dhms_agentfuse_integration_result_review_and_freeze_v3_6_3.md"
)
_COMMON_HOST_FACTS = (
    "approval",
    "physical_execution",
    "retry",
    "recovery",
    "process_completion",
    "goal_achievement",
)


_PROFILES = (
    IntegrationProfile(
        integration_id="python-runtime-guard",
        runtime_family="Python RuntimeGuard",
        integration_kind="canonical",
        implementation_owner="dhms",
        implementation_reference="dhms_agentfuse.runtime_guard:RuntimeGuard",
        canonical_actions=("allow", "block"),
        decision_boundary="canonical pre-dispatch policy evaluation and guarded invocation",
        evidenced_capabilities=(
            "decision_only_sync",
            "decision_only_async",
            "guarded_dispatch_sync",
            "guarded_dispatch_async",
            "sync_async_parity",
            "execution_failure_observed",
            "terminal_settlement_observed",
            "deterministic_reevaluation",
            "tool_call_identity_preserved",
            "safe_serialization",
        ),
        host_owned_facts=_COMMON_HOST_FACTS + ("interruption",),
        tested_runtime="dhms-agentfuse",
        tested_version="3.6.3",
        tested_commit="8bd894065a5892b7c795699db745bf180b9b2376",
        fixture_version=_FIXTURE_VERSION,
        fixture_digest=_FIXTURE_DIGEST,
        evidence_scope="canonical RuntimeGuard decision and guarded invocation path",
        evidence_references=(
            _FIXTURE_REFERENCE,
            "docs/dhms_agentfuse_public_decision_api_v3_6_0.md",
            _FREEZE_REFERENCE,
        ),
        limitations=(
            "RuntimeGuard.invoke has no proved host interruption surface",
            "allow is not proof of physical execution or goal achievement",
            "unwrapped execution paths are outside this mapping",
        ),
    ),
    IntegrationProfile(
        integration_id="provider-neutral-reference",
        runtime_family="Provider-neutral reference consumer",
        integration_kind="reference",
        implementation_owner="dhms",
        implementation_reference=(
            "examples/runtime_guard/consumer_integration_contract_demo.py"
        ),
        canonical_actions=("allow", "block"),
        decision_boundary="reference host mapping around RuntimeGuardDecision",
        evidenced_capabilities=(
            "guarded_dispatch_sync",
            "guarded_dispatch_async",
            "sync_async_parity",
            "interruption_observed",
            "execution_failure_observed",
            "terminal_settlement_observed",
            "tool_call_identity_preserved",
            "safe_serialization",
        ),
        host_owned_facts=_COMMON_HOST_FACTS + ("interruption",),
        tested_runtime="provider-neutral reference consumer",
        tested_version="3.6.1",
        tested_commit="96984766db2495d66959a189134391bd5cf7a8b5",
        fixture_version=_FIXTURE_VERSION,
        fixture_digest=_FIXTURE_DIGEST,
        evidence_scope="local demonstration mapping for host-owned lifecycle outcomes",
        evidence_references=(
            _FIXTURE_REFERENCE,
            "docs/dhms_agentfuse_consumer_integration_contract_v3_6_1.md",
            _FREEZE_REFERENCE,
        ),
        limitations=(
            "reference-only demonstration mapping, not a production adapter",
            "host outcomes are modeled locally rather than delegated to a provider",
            "no deployment or runtime compatibility claim",
        ),
    ),
    IntegrationProfile(
        integration_id="langgraph-tool-node",
        runtime_family="LangGraph ToolNode",
        integration_kind="internal_adapter",
        implementation_owner="dhms",
        implementation_reference=(
            "dhms_agentfuse.langgraph_runtime_guard:LangGraphRuntimeGuardAdapter"
        ),
        canonical_actions=("allow", "block"),
        decision_boundary="AgentFuse pre-dispatch decision inside an explicit ToolNode wrapper",
        evidenced_capabilities=(
            "guarded_dispatch_sync",
            "guarded_dispatch_async",
            "sync_async_parity",
            "interruption_observed",
            "execution_failure_observed",
            "terminal_settlement_observed",
            "tool_call_identity_preserved",
            "safe_serialization",
        ),
        host_owned_facts=_COMMON_HOST_FACTS
        + ("graph_control_flow", "checkpoint", "resume", "interruption"),
        tested_runtime="langgraph",
        tested_version="1.2.11",
        tested_commit=None,
        fixture_version=_FIXTURE_VERSION,
        fixture_digest=_FIXTURE_DIGEST,
        evidence_scope="installed LangGraph ToolNode wrapper and GraphInterrupt path",
        evidence_references=(
            _FIXTURE_REFERENCE,
            "dhms_agentfuse/langgraph_runtime_guard.py",
            _FREEZE_REFERENCE,
        ),
        limitations=(
            "LangGraph owns GraphInterrupt, checkpoint, and resume semantics",
            "only the explicit reviewed ToolNode adapter path is described",
            "dependency range does not prove future LangGraph compatibility",
            "not an official LangGraph certification",
        ),
    ),
    IntegrationProfile(
        integration_id="dsh-tools-pre-execute",
        runtime_family="DeepSeek Harness ToolRuntime",
        integration_kind="external_adapter",
        implementation_owner="external_project",
        implementation_reference="https://github.com/MkaliezZ/dsh-agentfuse-plugin",
        canonical_actions=("allow", "block"),
        decision_boundary="external tools/pre-execute mapping before tested ToolRuntime execution",
        evidenced_capabilities=(
            "guarded_dispatch_async",
            "interruption_observed",
            "execution_failure_observed",
            "terminal_settlement_observed",
            "deterministic_reevaluation",
            "tool_call_identity_preserved",
            "safe_serialization",
        ),
        host_owned_facts=_COMMON_HOST_FACTS
        + ("ask_approval_deferral", "interruption"),
        tested_runtime="DeepSeek Harness",
        tested_version="0.1.0-rc.7",
        tested_commit="99f6f02fecdb7dff40c3fbc9470f5907c29f74ca",
        fixture_version=_FIXTURE_VERSION,
        fixture_digest=_FIXTURE_DIGEST,
        evidence_scope="pinned external Context/SystemPrompt/ToolRuntime execution path",
        evidence_references=(
            _FIXTURE_REFERENCE,
            "https://github.com/MkaliezZ/dsh-agentfuse-plugin",
            "https://github.com/MkaliezZ/dsh-agentfuse-plugin/commit/366d213f207a833d45669b20551a33117eaeb6e6",
            _FREEZE_REFERENCE,
        ),
        limitations=(
            "metadata-only; the external TypeScript adapter is not in this package",
            "DSH ask is host approval deferral, not a canonical AgentFuse action",
            "custom policy exception and invalid-decision cases were not applicable",
            "sync/async parity was not applicable to the single async ToolRuntime path",
            "the tested path does not prove protection of all DSH paths",
            "not an official DeepSeek certification",
        ),
    ),
)

_PROFILES_BY_ID = MappingProxyType(
    {profile.integration_id: profile for profile in _PROFILES}
)
if len(_PROFILES_BY_ID) != len(_PROFILES):
    raise RuntimeError("integration profile IDs must be unique")


def list_integrations() -> tuple[IntegrationProfile, ...]:
    """Return reviewed profiles in stable package order."""

    return _PROFILES


def get_integration(integration_id: str) -> IntegrationProfile:
    """Return one reviewed profile or raise ``KeyError`` for an unknown ID."""

    return _PROFILES_BY_ID[integration_id]


__all__ = ["get_integration", "list_integrations"]
