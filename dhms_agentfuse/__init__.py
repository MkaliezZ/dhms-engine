"""Safe public exports for the DHMS AgentFuse Minimal API skeleton."""

from typing import TYPE_CHECKING, Any

from .adapter_skeleton import AgentFuseAdapterSkeleton
from .api import (
    ALLOWLISTED_SQL,
    apply_execution_gate,
    build_agentfuse_trace,
    create_runtime_request,
    create_tool_call_proposal,
    evaluate_proposal,
    run_non_executing_agentfuse_flow,
)
from .evidence_schema import (
    AgentFuseEvidenceRecord,
    LayeredBoundaryDecision,
    NonExecutionEvidence,
    PolicyResolutionEvidence,
    SafeTraceMetadata,
    ambiguous_pattern_overlap_evidence,
    example_evidence_records,
    mcp_file_network_boundary_evidence,
    safe_read_only_summary_evidence,
    sql_mutation_block_evidence,
)
from .models import AgentFuseTrace, ExecutionGateDecision, RuntimeRequest, SafetyDecision, ToolCallProposal
from .runtime_guard import (
    GuardedInvocation,
    RuntimeGuard,
    RuntimeGuardDecision,
    RuntimeGuardResult,
    RuntimePolicyDecision,
    ToolCallRequest,
)

if TYPE_CHECKING:
    from .langgraph_runtime_guard import LangGraphRuntimeGuardAdapter


def __getattr__(name: str) -> Any:
    """Load the optional runtime-specific export only when requested."""

    if name == "LangGraphRuntimeGuardAdapter":
        from .langgraph_runtime_guard import LangGraphRuntimeGuardAdapter

        return LangGraphRuntimeGuardAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "ALLOWLISTED_SQL",
    "AgentFuseAdapterSkeleton",
    "AgentFuseEvidenceRecord",
    "AgentFuseTrace",
    "ExecutionGateDecision",
    "GuardedInvocation",
    "LayeredBoundaryDecision",
    "LangGraphRuntimeGuardAdapter",
    "NonExecutionEvidence",
    "PolicyResolutionEvidence",
    "RuntimeRequest",
    "RuntimeGuard",
    "RuntimeGuardDecision",
    "RuntimeGuardResult",
    "RuntimePolicyDecision",
    "SafeTraceMetadata",
    "SafetyDecision",
    "ToolCallProposal",
    "ToolCallRequest",
    "ambiguous_pattern_overlap_evidence",
    "apply_execution_gate",
    "build_agentfuse_trace",
    "create_runtime_request",
    "create_tool_call_proposal",
    "example_evidence_records",
    "evaluate_proposal",
    "mcp_file_network_boundary_evidence",
    "run_non_executing_agentfuse_flow",
    "safe_read_only_summary_evidence",
    "sql_mutation_block_evidence",
]
