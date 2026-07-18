"""Real LangGraph ToolNode integration for AgentFuse Runtime Guard."""

from __future__ import annotations

import json
from threading import Lock
from typing import Any, Callable, Sequence

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool
from langgraph.errors import GraphInterrupt
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt.tool_node import (
    ToolCallRequest as LangGraphToolCallRequest,
    ToolInvocationError,
)

from .runtime_guard import RuntimeGuard, RuntimeGuardResult, ToolCallRequest


class LangGraphRuntimeGuardAdapter:
    """Create a real ToolNode whose dispatch is mediated by a RuntimeGuard."""

    def __init__(self, guard: RuntimeGuard) -> None:
        self.guard = guard
        self._receipts: list[RuntimeGuardResult] = []
        self._receipt_lock = Lock()

    @property
    def receipts(self) -> tuple[RuntimeGuardResult, ...]:
        with self._receipt_lock:
            return tuple(self._receipts)

    def receipt_for(self, tool_call_id: str) -> RuntimeGuardResult:
        matches = [receipt for receipt in self.receipts if receipt.tool_call_id == tool_call_id]
        if len(matches) != 1:
            raise KeyError(f"expected one receipt for tool_call_id={tool_call_id!r}")
        return matches[0]

    def clear_receipts(self) -> None:
        with self._receipt_lock:
            self._receipts.clear()

    def create_tool_node(
        self,
        tools: Sequence[BaseTool | Callable[..., Any]],
        *,
        name: str = "tools",
    ) -> ToolNode:
        """Return an installed LangGraph ToolNode with guarded sync/async dispatch."""

        return ToolNode(
            tools,
            name=name,
            handle_tool_errors=False,
            wrap_tool_call=self._wrap_tool_call,
            awrap_tool_call=self._awrap_tool_call,
        )

    def _runtime_request(self, request: LangGraphToolCallRequest) -> ToolCallRequest:
        call = request.tool_call
        return ToolCallRequest(
            tool_call_id=str(call["id"]),
            tool_name=str(call["name"]),
            arguments=dict(call.get("args") or {}),
            safe_metadata={"adapter": "langgraph-tool-node"},
        )

    def _store(self, receipt: RuntimeGuardResult) -> None:
        with self._receipt_lock:
            self._receipts.append(receipt)

    @staticmethod
    def _terminal_message(receipt: RuntimeGuardResult) -> ToolMessage:
        content = json.dumps(
            {
                "decision": receipt.decision,
                "outcome": receipt.outcome,
                "reason_code": receipt.reason_code,
                "tool_name": receipt.tool_name,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return ToolMessage(
            content=content,
            tool_call_id=receipt.tool_call_id,
            name=receipt.tool_name,
            status="error",
            artifact={"agentfuse_receipt": receipt.to_safe_dict()},
        )

    def _wrap_tool_call(
        self,
        request: LangGraphToolCallRequest,
        execute: Callable[[LangGraphToolCallRequest], Any],
    ) -> Any:
        tool_call = self._runtime_request(request)
        resolved = self.guard._resolve_policy_sync(tool_call)
        if resolved.action == "block":
            receipt = self.guard._blocked_result(tool_call, resolved)
            self._store(receipt)
            return self._terminal_message(receipt)
        if request.tool is None:
            receipt = self.guard._failure_result(
                tool_call,
                resolved,
                dispatch_occurred=False,
                handler_started=False,
                failure_category="unregistered_tool",
                side_effect_occurred=False,
            )
            self._store(receipt)
            return self._terminal_message(receipt)
        try:
            result = execute(request)
        except GraphInterrupt:
            receipt = self.guard._interrupted_result(tool_call, resolved)
            self._store(receipt)
            raise
        except ToolInvocationError:
            receipt = self.guard._failure_result(
                tool_call,
                resolved,
                dispatch_occurred=False,
                handler_started=False,
                failure_category="tool_input_error",
                side_effect_occurred=False,
            )
            self._store(receipt)
            return self._terminal_message(receipt)
        except Exception:
            receipt = self.guard._failure_result(
                tool_call,
                resolved,
                dispatch_occurred=True,
                handler_started=True,
                failure_category="handler_exception",
                side_effect_occurred=None,
            )
            self._store(receipt)
            return self._terminal_message(receipt)
        if isinstance(result, ToolMessage) and result.status == "error":
            receipt = self.guard._failure_result(
                tool_call,
                resolved,
                dispatch_occurred=True,
                handler_started=True,
                failure_category="handler_exception",
                side_effect_occurred=None,
            )
        else:
            return_value = result.content if isinstance(result, ToolMessage) else None
            receipt = self.guard._success_result(tool_call, resolved, return_value)
        self._store(receipt)
        return result

    async def _awrap_tool_call(
        self,
        request: LangGraphToolCallRequest,
        execute: Callable[[LangGraphToolCallRequest], Any],
    ) -> Any:
        tool_call = self._runtime_request(request)
        resolved = await self.guard._resolve_policy_async(tool_call)
        if resolved.action == "block":
            receipt = self.guard._blocked_result(tool_call, resolved)
            self._store(receipt)
            return self._terminal_message(receipt)
        if request.tool is None:
            receipt = self.guard._failure_result(
                tool_call,
                resolved,
                dispatch_occurred=False,
                handler_started=False,
                failure_category="unregistered_tool",
                side_effect_occurred=False,
            )
            self._store(receipt)
            return self._terminal_message(receipt)
        try:
            result = await execute(request)
        except GraphInterrupt:
            receipt = self.guard._interrupted_result(tool_call, resolved)
            self._store(receipt)
            raise
        except ToolInvocationError:
            receipt = self.guard._failure_result(
                tool_call,
                resolved,
                dispatch_occurred=False,
                handler_started=False,
                failure_category="tool_input_error",
                side_effect_occurred=False,
            )
            self._store(receipt)
            return self._terminal_message(receipt)
        except Exception:
            receipt = self.guard._failure_result(
                tool_call,
                resolved,
                dispatch_occurred=True,
                handler_started=True,
                failure_category="handler_exception",
                side_effect_occurred=None,
            )
            self._store(receipt)
            return self._terminal_message(receipt)
        if isinstance(result, ToolMessage) and result.status == "error":
            receipt = self.guard._failure_result(
                tool_call,
                resolved,
                dispatch_occurred=True,
                handler_started=True,
                failure_category="handler_exception",
                side_effect_occurred=None,
            )
        else:
            return_value = result.content if isinstance(result, ToolMessage) else None
            receipt = self.guard._success_result(tool_call, resolved, return_value)
        self._store(receipt)
        return result


__all__ = ["LangGraphRuntimeGuardAdapter"]
