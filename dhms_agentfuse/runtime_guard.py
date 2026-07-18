"""Experimental in-process pre-dispatch Runtime Guard for agent tool handlers."""

from __future__ import annotations

import hashlib
import inspect
import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping, Sequence

from .evidence_schema import (
    AgentFuseEvidenceRecord,
    LayeredBoundaryDecision,
    NonExecutionEvidence,
    PolicyResolutionEvidence,
    SafeTraceMetadata,
    SCHEMA_VERSION,
)


PolicyCallable = Callable[["ToolCallRequest"], Any]
Handler = Callable[..., Any]

_ACTIONS = {"allow", "block"}
_DEFAULT_ACTIONS = {"allow", "block"}
_NON_EXECUTION_REASONS = {
    "explicit_denylist",
    "not_allowlisted",
    "policy_denied",
    "policy_exception",
    "invalid_policy_decision",
}


def _require_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")


def _stable_arguments_hash(arguments: Mapping[str, Any]) -> str:
    try:
        encoded = json.dumps(
            dict(arguments),
            sort_keys=True,
            separators=(",", ":"),
            default=lambda value: f"<{type(value).__name__}>",
        ).encode("utf-8")
    except (TypeError, ValueError):
        encoded = b"<unserializable-arguments>"
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _policy_hash(policy_id: str) -> str:
    digest = hashlib.sha256(policy_id.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


@dataclass(frozen=True, repr=False)
class ToolCallRequest:
    """Provider-neutral tool request whose default representation redacts arguments."""

    tool_call_id: str
    tool_name: str
    arguments: Mapping[str, Any]
    safe_metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_text(self.tool_call_id, "tool_call_id")
        _require_text(self.tool_name, "tool_name")
        if not isinstance(self.arguments, Mapping):
            raise ValueError("arguments must be a mapping")
        if not isinstance(self.safe_metadata, Mapping):
            raise ValueError("safe_metadata must be a mapping")
        object.__setattr__(self, "arguments", MappingProxyType(dict(self.arguments)))
        object.__setattr__(self, "safe_metadata", MappingProxyType(dict(self.safe_metadata)))

    @property
    def arguments_hash(self) -> str:
        return _stable_arguments_hash(self.arguments)

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "tool_call_id": self.tool_call_id,
            "tool_name": self.tool_name,
            "arguments_hash": self.arguments_hash,
            "safe_metadata_keys": sorted(str(key) for key in self.safe_metadata),
        }

    def __repr__(self) -> str:
        return (
            "ToolCallRequest("
            f"tool_call_id={self.tool_call_id!r}, "
            f"tool_name={self.tool_name!r}, "
            "arguments=<redacted>, "
            f"safe_metadata_keys={sorted(str(key) for key in self.safe_metadata)!r})"
        )


@dataclass(frozen=True)
class RuntimePolicyDecision:
    """Explicit decision returned by an optional custom policy callable."""

    action: str
    reason_code: str
    policy_id: str = "runtime-guard:custom-policy"

    def __post_init__(self) -> None:
        if self.action not in _ACTIONS:
            raise ValueError(f"unsupported policy action: {self.action}")
        _require_text(self.reason_code, "reason_code")
        _require_text(self.policy_id, "policy_id")

    @classmethod
    def allow(
        cls,
        reason_code: str = "allowed",
        policy_id: str = "runtime-guard:custom-policy",
    ) -> "RuntimePolicyDecision":
        return cls(action="allow", reason_code=reason_code, policy_id=policy_id)

    @classmethod
    def block(
        cls,
        reason_code: str = "policy_denied",
        policy_id: str = "runtime-guard:custom-policy",
    ) -> "RuntimePolicyDecision":
        return cls(action="block", reason_code=reason_code, policy_id=policy_id)


@dataclass(frozen=True)
class _ResolvedPolicy:
    action: str
    reason_code: str
    policy_id: str
    resolution_outcome: str = "resolved"
    match_stage: str = "exact"
    match_kind: str = "exact"
    matched_policy_key: str | None = None
    candidate_policy_keys: tuple[str, ...] = ()
    fallback_reason: str | None = None


@dataclass(frozen=True, repr=False)
class RuntimeGuardResult:
    """Structured terminal receipt for one guarded tool-call dispatch."""

    tool_call_id: str
    tool_name: str
    decision: str
    reason_code: str
    dispatch_occurred: bool
    handler_started: bool
    outcome: str
    tool_failure: bool
    side_effect_occurred: bool | None
    evidence: AgentFuseEvidenceRecord
    return_value: Any = field(default=None, repr=False)
    failure_category: str | None = None

    @property
    def handler_invoked(self) -> bool:
        return self.handler_started

    @property
    def execution(self) -> str:
        return "not_started" if self.outcome == "not_executed" else "started"

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "tool_call_id": self.tool_call_id,
            "tool_name": self.tool_name,
            "decision": self.decision,
            "reason_code": self.reason_code,
            "dispatch_occurred": self.dispatch_occurred,
            "handler_started": self.handler_started,
            "handler_invoked": self.handler_invoked,
            "execution": self.execution,
            "outcome": self.outcome,
            "tool_failure": self.tool_failure,
            "side_effect_occurred": self.side_effect_occurred,
            "failure_category": self.failure_category,
            "return_value_in_safe_output": False,
            "evidence": self.evidence.to_dict(),
        }

    def __repr__(self) -> str:
        return f"RuntimeGuardResult({self.to_safe_dict()!r})"


@dataclass(frozen=True)
class GuardedInvocation:
    tool_call: ToolCallRequest
    handler: Handler


class RuntimeGuard:
    """Evaluate policy, own handler dispatch, and emit evidence from that path."""

    def __init__(
        self,
        *,
        allow_tools: Iterable[str] | None = None,
        deny_tools: Iterable[str] | None = None,
        default_action: str = "block",
        policy: PolicyCallable | None = None,
    ) -> None:
        if default_action not in _DEFAULT_ACTIONS:
            raise ValueError("default_action must be 'allow' or 'block'")
        self._allowlist_configured = allow_tools is not None
        self.allow_tools = frozenset(allow_tools or ())
        self.deny_tools = frozenset(deny_tools or ())
        if not all(isinstance(name, str) and name for name in self.allow_tools | self.deny_tools):
            raise ValueError("tool policy names must be non-empty strings")
        self.default_action = default_action
        self.policy = policy

    def invoke(self, *, tool_call: ToolCallRequest, handler: Handler) -> RuntimeGuardResult:
        resolved = self._resolve_policy_sync(tool_call)
        if resolved.action == "block":
            return self._blocked_result(tool_call, resolved)
        if inspect.iscoroutinefunction(handler):
            return self._failure_result(
                tool_call,
                resolved,
                dispatch_occurred=False,
                handler_started=False,
                failure_category="async_handler_requires_ainvoke",
                side_effect_occurred=False,
            )
        try:
            value = handler(**dict(tool_call.arguments))
            if inspect.isawaitable(value):
                if inspect.iscoroutine(value):
                    value.close()
                return self._failure_result(
                    tool_call,
                    resolved,
                    dispatch_occurred=True,
                    handler_started=True,
                    failure_category="async_handler_requires_ainvoke",
                    side_effect_occurred=None,
                )
        except Exception:
            return self._failure_result(
                tool_call,
                resolved,
                dispatch_occurred=True,
                handler_started=True,
                failure_category="handler_exception",
                side_effect_occurred=None,
            )
        return self._success_result(tool_call, resolved, value)

    async def ainvoke(self, *, tool_call: ToolCallRequest, handler: Handler) -> RuntimeGuardResult:
        resolved = await self._resolve_policy_async(tool_call)
        if resolved.action == "block":
            return self._blocked_result(tool_call, resolved)
        try:
            value = handler(**dict(tool_call.arguments))
            if inspect.isawaitable(value):
                value = await value
        except Exception:
            return self._failure_result(
                tool_call,
                resolved,
                dispatch_occurred=True,
                handler_started=True,
                failure_category="handler_exception",
                side_effect_occurred=None,
            )
        return self._success_result(tool_call, resolved, value)

    def invoke_batch(self, *, invocations: Sequence[GuardedInvocation]) -> list[RuntimeGuardResult]:
        return [
            self.invoke(tool_call=invocation.tool_call, handler=invocation.handler)
            for invocation in invocations
        ]

    async def ainvoke_batch(
        self,
        *,
        invocations: Sequence[GuardedInvocation],
    ) -> list[RuntimeGuardResult]:
        results: list[RuntimeGuardResult] = []
        for invocation in invocations:
            results.append(
                await self.ainvoke(
                    tool_call=invocation.tool_call,
                    handler=invocation.handler,
                )
            )
        return results

    def _resolve_static_policy(self, tool_call: ToolCallRequest) -> _ResolvedPolicy | None:
        if tool_call.tool_name in self.deny_tools:
            return _ResolvedPolicy(
                action="block",
                reason_code="explicit_denylist",
                policy_id="runtime-guard:denylist",
                matched_policy_key=f"deny:{tool_call.tool_name}",
                candidate_policy_keys=(f"deny:{tool_call.tool_name}",),
            )
        if self._allowlist_configured and tool_call.tool_name not in self.allow_tools:
            return _ResolvedPolicy(
                action="block",
                reason_code="not_allowlisted",
                policy_id="runtime-guard:allowlist",
                matched_policy_key="allowlist:configured",
                candidate_policy_keys=tuple(f"allow:{name}" for name in sorted(self.allow_tools)),
            )
        return None

    def _resolve_policy_sync(self, tool_call: ToolCallRequest) -> _ResolvedPolicy:
        static = self._resolve_static_policy(tool_call)
        if static is not None:
            return static
        if self.policy is not None:
            if inspect.iscoroutinefunction(self.policy):
                return self._invalid_policy_result()
            try:
                raw_decision = self.policy(tool_call)
                if inspect.isawaitable(raw_decision):
                    if inspect.iscoroutine(raw_decision):
                        raw_decision.close()
                    return self._invalid_policy_result()
            except Exception:
                return self._policy_exception_result()
            return self._coerce_custom_policy(raw_decision)
        if self._allowlist_configured:
            return _ResolvedPolicy(
                action="allow",
                reason_code="allowed",
                policy_id="runtime-guard:allowlist",
                matched_policy_key=f"allow:{tool_call.tool_name}",
                candidate_policy_keys=(f"allow:{tool_call.tool_name}",),
            )
        return self._default_policy_result()

    async def _resolve_policy_async(self, tool_call: ToolCallRequest) -> _ResolvedPolicy:
        static = self._resolve_static_policy(tool_call)
        if static is not None:
            return static
        if self.policy is not None:
            try:
                raw_decision = self.policy(tool_call)
                if inspect.isawaitable(raw_decision):
                    raw_decision = await raw_decision
            except Exception:
                return self._policy_exception_result()
            return self._coerce_custom_policy(raw_decision)
        if self._allowlist_configured:
            return _ResolvedPolicy(
                action="allow",
                reason_code="allowed",
                policy_id="runtime-guard:allowlist",
                matched_policy_key=f"allow:{tool_call.tool_name}",
                candidate_policy_keys=(f"allow:{tool_call.tool_name}",),
            )
        return self._default_policy_result()

    def _coerce_custom_policy(self, raw_decision: Any) -> _ResolvedPolicy:
        if isinstance(raw_decision, RuntimePolicyDecision):
            decision = raw_decision
        elif isinstance(raw_decision, str) and raw_decision in _ACTIONS:
            decision = RuntimePolicyDecision(
                action=raw_decision,
                reason_code="allowed" if raw_decision == "allow" else "policy_denied",
            )
        else:
            return self._invalid_policy_result()
        return _ResolvedPolicy(
            action=decision.action,
            reason_code=decision.reason_code,
            policy_id=decision.policy_id,
            matched_policy_key=decision.policy_id,
            candidate_policy_keys=(decision.policy_id,),
        )

    def _default_policy_result(self) -> _ResolvedPolicy:
        return _ResolvedPolicy(
            action=self.default_action,
            reason_code="allowed" if self.default_action == "allow" else "policy_denied",
            policy_id=f"runtime-guard:default:{self.default_action}",
            match_stage="fallback",
            match_kind="none",
            matched_policy_key=f"default:{self.default_action}",
            candidate_policy_keys=(),
        )

    @staticmethod
    def _policy_exception_result() -> _ResolvedPolicy:
        return _ResolvedPolicy(
            action="block",
            reason_code="policy_exception",
            policy_id="runtime-guard:custom-policy",
            resolution_outcome="no_match",
            match_stage="fallback",
            match_kind="none",
            fallback_reason="policy_exception",
        )

    @staticmethod
    def _invalid_policy_result() -> _ResolvedPolicy:
        return _ResolvedPolicy(
            action="block",
            reason_code="invalid_policy_decision",
            policy_id="runtime-guard:custom-policy",
            resolution_outcome="no_match",
            match_stage="fallback",
            match_kind="none",
            fallback_reason="invalid_policy_decision",
        )

    def _evidence(
        self,
        tool_call: ToolCallRequest,
        resolved: _ResolvedPolicy,
    ) -> AgentFuseEvidenceRecord:
        policy = PolicyResolutionEvidence(
            policy_resolution_outcome=resolved.resolution_outcome,
            match_stage=resolved.match_stage,
            matched_policy_key=resolved.matched_policy_key,
            match_kind=resolved.match_kind,
            priority=100 if resolved.resolution_outcome == "resolved" else None,
            candidate_policy_keys=list(resolved.candidate_policy_keys),
            fallback_reason=resolved.fallback_reason,
        )
        policy_hash = _policy_hash(resolved.policy_id)
        evidence_ref = f"evidence:runtime-guard:{tool_call.tool_call_id}"
        boundary = LayeredBoundaryDecision(
            boundary_type="call",
            decision=resolved.action,
            policy_id=resolved.policy_id,
            policy_hash=policy_hash,
            reason_code=resolved.reason_code,
            decisive_gate=True,
        )
        trace = SafeTraceMetadata(
            tool_name=tool_call.tool_name,
            decision=resolved.action,
            policy_id=resolved.policy_id,
            policy_hash=policy_hash,
            reason_code=resolved.reason_code,
            boundary_type="call",
            args_hash=tool_call.arguments_hash,
            evidence_ref=evidence_ref,
        )
        non_execution = None
        if resolved.action == "block":
            reason = (
                resolved.reason_code
                if resolved.reason_code in _NON_EXECUTION_REASONS
                else "policy_denied"
            )
            non_execution = NonExecutionEvidence(
                status="not_executed",
                reason=reason,
                execution="not_started",
                payload_executed=False,
                tool_failure=False,
                side_effect_occurred=False,
                approval_id=f"runtime-policy:{tool_call.tool_call_id}",
                call_id=tool_call.tool_call_id,
                result_ref=f"result:not_executed:{tool_call.tool_call_id}",
            )
        return AgentFuseEvidenceRecord(
            record_id=f"runtime-guard-evidence:{tool_call.tool_call_id}",
            schema_version=SCHEMA_VERSION,
            policy_resolution=policy,
            boundary_decision=boundary,
            trace_metadata=trace,
            non_execution=non_execution,
        )

    def _blocked_result(
        self,
        tool_call: ToolCallRequest,
        resolved: _ResolvedPolicy,
    ) -> RuntimeGuardResult:
        return RuntimeGuardResult(
            tool_call_id=tool_call.tool_call_id,
            tool_name=tool_call.tool_name,
            decision="block",
            reason_code=resolved.reason_code,
            dispatch_occurred=False,
            handler_started=False,
            outcome="not_executed",
            tool_failure=False,
            side_effect_occurred=False,
            evidence=self._evidence(tool_call, resolved),
        )

    def _success_result(
        self,
        tool_call: ToolCallRequest,
        resolved: _ResolvedPolicy,
        return_value: Any,
    ) -> RuntimeGuardResult:
        return RuntimeGuardResult(
            tool_call_id=tool_call.tool_call_id,
            tool_name=tool_call.tool_name,
            decision="allow",
            reason_code=resolved.reason_code,
            dispatch_occurred=True,
            handler_started=True,
            outcome="executed",
            tool_failure=False,
            side_effect_occurred=None,
            evidence=self._evidence(tool_call, resolved),
            return_value=return_value,
        )

    def _failure_result(
        self,
        tool_call: ToolCallRequest,
        resolved: _ResolvedPolicy,
        *,
        dispatch_occurred: bool,
        handler_started: bool,
        failure_category: str,
        side_effect_occurred: bool | None,
    ) -> RuntimeGuardResult:
        return RuntimeGuardResult(
            tool_call_id=tool_call.tool_call_id,
            tool_name=tool_call.tool_name,
            decision="allow",
            reason_code=resolved.reason_code,
            dispatch_occurred=dispatch_occurred,
            handler_started=handler_started,
            outcome="execution_failed",
            tool_failure=True,
            side_effect_occurred=side_effect_occurred,
            evidence=self._evidence(tool_call, resolved),
            failure_category=failure_category,
        )


__all__ = [
    "GuardedInvocation",
    "RuntimeGuard",
    "RuntimeGuardResult",
    "RuntimePolicyDecision",
    "ToolCallRequest",
]
