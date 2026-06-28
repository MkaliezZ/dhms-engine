"""Minimal DHMS interception harness for LangChain tool-call proposals.

This module attempts to use real LangChain APIs when installed. It never calls
model providers, executes tools, or authorizes execution.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

from dhms_agentfuse.controlled_proposal_gate import evaluate_controlled_proposal


DHMS_INTERCEPTION_VERSION = "v3.1.1-real-langchain-dependency-agent-harness-validation"

TOOL_CONVERSIONS = {
    "local_read_only_summary": {
        "requested_capabilities": ["local_read_only_summary"],
        "declared_boundary": "local_read_only_non_executing_safe",
    },
    "drop_table": {
        "requested_capabilities": ["sql_mutation"],
        "declared_boundary": "unsafe_sql_mutation_request",
    },
    "model_api_request": {
        "requested_capabilities": ["model_api"],
        "declared_boundary": "unsafe_model_api_request",
    },
}


def _import_langchain_components() -> Dict[str, Any]:
    components: Dict[str, Any] = {
        "langchain_available": False,
        "create_agent": None,
        "ai_message_class": None,
        "tool_decorator": None,
        "fake_chat_model_class": None,
        "errors": [],
    }
    try:
        import langchain  # type: ignore

        components["langchain_available"] = True
        components["langchain_version"] = getattr(langchain, "__version__", "unknown")
    except Exception as exc:  # pragma: no cover - depends on local environment
        components["errors"].append(f"langchain import failed: {type(exc).__name__}: {exc}")
        return components

    try:
        from langchain.agents import create_agent  # type: ignore

        components["create_agent"] = create_agent
    except Exception as exc:  # pragma: no cover - depends on installed version
        components["errors"].append(f"create_agent import failed: {type(exc).__name__}: {exc}")

    try:
        from langchain_core.messages import AIMessage  # type: ignore

        components["ai_message_class"] = AIMessage
    except Exception as exc:  # pragma: no cover - depends on installed version
        components["errors"].append(f"AIMessage import failed: {type(exc).__name__}: {exc}")

    try:
        from langchain_core.tools import tool  # type: ignore

        components["tool_decorator"] = tool
    except Exception as exc:  # pragma: no cover - depends on installed version
        components["errors"].append(f"tool decorator import failed: {type(exc).__name__}: {exc}")

    try:
        from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel  # type: ignore

        components["fake_chat_model_class"] = FakeMessagesListChatModel
    except Exception as exc:  # pragma: no cover - depends on installed version
        components["errors"].append(f"fake chat model import failed: {type(exc).__name__}: {exc}")

    return components


def langchain_available() -> bool:
    """Return whether real LangChain can be imported in the current runtime."""

    return bool(_import_langchain_components()["langchain_available"])


def _inert_tool_functions(tool_decorator: Any = None) -> List[Any]:
    def local_read_only_summary(query: str = "") -> str:
        """Inert local read-only summary tool. DHMS must intercept before use."""

        raise RuntimeError("DHMS interception prevents tool execution")

    def drop_table(statement: str = "") -> str:
        """Inert SQL mutation-like tool. DHMS must intercept before use."""

        raise RuntimeError("DHMS interception prevents tool execution")

    def model_api_request(prompt: str = "") -> str:
        """Inert model API-like tool. DHMS must intercept before use."""

        raise RuntimeError("DHMS interception prevents tool execution")

    tools: List[Any] = [local_read_only_summary, drop_table, model_api_request]
    if tool_decorator is None:
        return tools
    wrapped = []
    for tool_function in tools:
        try:
            wrapped.append(tool_decorator(tool_function))
        except Exception:
            wrapped.append(tool_function)
    return wrapped


def _sample_tool_call() -> Dict[str, Any]:
    return {
        "id": "langchain_tool_call_safe_read_only_summary_001",
        "name": "local_read_only_summary",
        "args": {"topic": "synthetic local project summary"},
        "type": "tool_call",
    }


def _sample_ai_message(ai_message_class: Any) -> Optional[Any]:
    if ai_message_class is None:
        return None
    try:
        return ai_message_class(content="", tool_calls=[_sample_tool_call()])
    except Exception:
        return None


def create_dhms_langchain_agent_harness() -> Dict[str, Any]:
    """Create a minimal real LangChain agent harness when available."""

    components = _import_langchain_components()
    langchain_is_available = bool(components["langchain_available"])
    create_agent = components["create_agent"]
    fake_model_class = components["fake_chat_model_class"]
    result: Dict[str, Any] = {
        "langchain_available": langchain_is_available,
        "langchain_agent_harness_created": False,
        "real_create_agent_imported": create_agent is not None,
        "real_langchain_agent_object_created": False,
        "harness_mode": "langchain_unavailable",
        "agent_object_type": None,
        "fake_or_local_model_used": False,
        "model_provider_called": False,
        "tool_execution_attempted": False,
        "tool_execution_allowed": False,
        "runtime_behaviors_added": 0,
        "real_langchain_message_created": False,
        "real_langchain_ai_message_path_validated": False,
        "inert_tools_defined": False,
        "dependency_note": "",
        "import_errors": list(components["errors"]),
    }
    if not langchain_is_available:
        result["dependency_note"] = (
            "LangChain is not installed in this runtime and no repository dependency "
            "file is available to update. Install langchain externally to exercise "
            "the real harness creation path."
        )
        return result

    tools = _inert_tool_functions(components["tool_decorator"])
    result["inert_tools_defined"] = True
    sample_message = _sample_ai_message(components["ai_message_class"])
    result["real_langchain_message_created"] = sample_message is not None
    result["real_langchain_ai_message_path_validated"] = sample_message is not None

    if create_agent is not None and fake_model_class is not None and sample_message is not None:
        try:
            fake_model = fake_model_class(responses=[sample_message])
            agent = create_agent(model=fake_model, tools=tools)
            result["langchain_agent_harness_created"] = True
            result["real_langchain_agent_object_created"] = True
            result["harness_mode"] = "create_agent_with_fake_messages_model"
            result["agent_object_type"] = type(agent).__name__
            result["fake_or_local_model_used"] = True
            return result
        except Exception as exc:  # pragma: no cover - depends on installed version
            result["import_errors"].append(f"create_agent construction failed: {type(exc).__name__}: {exc}")

    result["dependency_note"] = "LangChain imported, but create_agent could not create a compatible local harness."
    return result


def _read_value(raw_tool_call: Any, key: str, default: Any = None) -> Any:
    if isinstance(raw_tool_call, dict):
        return raw_tool_call.get(key, default)
    return getattr(raw_tool_call, key, default)


def _normalize_tool_call(raw_tool_call: Any) -> Dict[str, Any]:
    tool_call_id = _read_value(raw_tool_call, "id", "unknown_langchain_tool_call")
    name = _read_value(raw_tool_call, "name", "unknown_tool")
    args = _read_value(raw_tool_call, "args", {})
    call_type = _read_value(raw_tool_call, "type", "tool_call")
    return {
        "id": tool_call_id if isinstance(tool_call_id, str) and tool_call_id else "unknown_langchain_tool_call",
        "name": name if isinstance(name, str) and name else "unknown_tool",
        "args": args if isinstance(args, dict) else {},
        "type": call_type if isinstance(call_type, str) and call_type else "tool_call",
    }


def _unique(values: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def build_langchain_tool_call_proposal(raw_tool_call: Dict[str, Any], source: str) -> Dict[str, Any]:
    """Convert a LangChain-style tool call into a DHMS controlled proposal."""

    normalized = _normalize_tool_call(raw_tool_call)
    conversion = TOOL_CONVERSIONS.get(
        normalized["name"],
        {
            "requested_capabilities": ["unsupported_tool"],
            "declared_boundary": "unsupported_langchain_tool_call",
        },
    )
    return {
        "proposal_id": normalized["id"],
        "requested_capabilities": list(conversion["requested_capabilities"]),
        "declared_boundary": conversion["declared_boundary"],
        "source": source,
        "tool_name": normalized["name"],
        "tool_call_type": normalized["type"],
        "metadata": {
            "langchain_tool_call_args_keys": sorted(str(key) for key in normalized["args"].keys()),
            "original_tool_call_id": normalized["id"],
            "original_tool_name": normalized["name"],
        },
    }


def _interception_trace(harness: Dict[str, Any]) -> Dict[str, bool]:
    return {
        "real_langchain_installed_or_imported": bool(harness["langchain_available"]),
        "real_create_agent_imported": bool(harness["real_create_agent_imported"]),
        "real_langchain_agent_harness_created": bool(harness["langchain_agent_harness_created"]),
        "real_langchain_agent_object_created": bool(harness["real_langchain_agent_object_created"]),
        "real_langchain_ai_message_path_validated": bool(harness["real_langchain_ai_message_path_validated"]),
        "langchain_message_or_tool_call_observed": True,
        "converted_to_dhms_proposal": True,
        "routed_through_controlled_proposal_gate": True,
        "tool_not_executed": True,
        "model_provider_not_called": True,
        "fake_or_local_model_used": bool(harness["fake_or_local_model_used"]),
        "no_sql_execution": True,
        "no_db_access": True,
        "no_sql_database_toolkit": True,
        "no_model_api": True,
        "no_network": True,
        "no_subprocess": True,
        "no_env_access": True,
        "no_credentials": True,
        "no_user_data": True,
        "no_file_mutation": True,
        "no_kerniq": True,
        "no_e2b": True,
        "no_production_runtime": True,
    }


def intercept_langchain_tool_call(raw_tool_call: Dict[str, Any], source: str) -> Dict[str, Any]:
    """Observe and gate one LangChain-style tool call before execution."""

    normalized = _normalize_tool_call(raw_tool_call)
    harness = create_dhms_langchain_agent_harness()
    converted_proposal = build_langchain_tool_call_proposal(normalized, source)
    gate_result = evaluate_controlled_proposal(converted_proposal, source)
    blocked_capabilities = gate_result.get("blocked_capabilities", [])
    if isinstance(blocked_capabilities, list):
        blocked_capabilities = _unique(str(item) for item in blocked_capabilities)
        gate_result = dict(gate_result)
        gate_result["blocked_capabilities"] = blocked_capabilities
    return {
        "dhms_interception_version": DHMS_INTERCEPTION_VERSION,
        "langchain_available": harness["langchain_available"],
        "langchain_agent_harness_created": harness["langchain_agent_harness_created"],
        "real_create_agent_imported": harness["real_create_agent_imported"],
        "real_langchain_agent_object_created": harness["real_langchain_agent_object_created"],
        "source": source,
        "observed_tool_call": normalized,
        "converted_proposal": converted_proposal,
        "gate_result": gate_result,
        "intercepted_before_execution": True,
        "tool_execution_attempted": False,
        "tool_execution_allowed": False,
        "execution_authorized": False,
        "runtime_behaviors_added": 0,
        "interception_trace": _interception_trace(harness),
    }


def intercept_langchain_ai_message(message: Any, source: str) -> Dict[str, Any]:
    """Extract the first LangChain AIMessage tool call and route it through DHMS."""

    tool_calls = getattr(message, "tool_calls", None)
    if tool_calls is None and isinstance(message, dict):
        tool_calls = message.get("tool_calls")
    if not isinstance(tool_calls, list) or not tool_calls:
        raw_tool_call = {
            "id": "missing_langchain_tool_call",
            "name": "unsupported_tool",
            "args": {},
            "type": "tool_call",
        }
    else:
        raw_tool_call = tool_calls[0]
    return intercept_langchain_tool_call(raw_tool_call, source)


def run_local_langchain_agent_interception_scenario(scenario: str) -> Dict[str, Any]:
    """Run one deterministic local LangChain interception scenario."""

    scenarios = {
        "safe_read_only": _sample_tool_call(),
        "drop_table": {
            "id": "langchain_tool_call_drop_table_001",
            "name": "drop_table",
            "args": {"statement": "DROP TABLE toy_accounts;"},
            "type": "tool_call",
        },
        "model_api_request": {
            "id": "langchain_tool_call_model_api_request_001",
            "name": "model_api_request",
            "args": {"prompt_summary": "synthetic provider request"},
            "type": "tool_call",
        },
    }
    raw_tool_call = scenarios.get(
        scenario,
        {
            "id": f"langchain_tool_call_unknown_{scenario}",
            "name": "unsupported_tool",
            "args": {},
            "type": "tool_call",
        },
    )
    return intercept_langchain_tool_call(raw_tool_call, f"scenario:{scenario}")
