"""Packaging contract for historical optional LangChain proof helpers."""

from __future__ import annotations

import builtins
from pathlib import Path

import pytest

from dhms_agentfuse.langchain_agent_loop_boundary import (
    create_dhms_guarded_langchain_agent_loop_harness,
)
from dhms_agentfuse.langchain_guarded_tool_adapter import (
    run_guarded_tool_adapter_scenario,
)
from dhms_agentfuse.langchain_interception import create_dhms_langchain_agent_harness


ROOT = Path(__file__).parents[1]


def test_pyproject_declares_historical_langchain_extra() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text()

    assert '[project.optional-dependencies]\nlangchain = [\n  "langchain>=1.0,<2.0",\n]' in pyproject
    mandatory_dependencies = pyproject.split("dependencies = [", 1)[1].split("]", 1)[0]
    assert "langchain>=1.0,<2.0" not in mandatory_dependencies


def test_missing_optional_langchain_has_clear_intended_behavior(monkeypatch) -> None:
    original_import = builtins.__import__

    def without_langchain(name, *args, **kwargs):
        if name == "langchain" or name.startswith("langchain."):
            raise ImportError("simulated missing optional dependency")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", without_langchain)

    with pytest.raises(ImportError, match=r"dhms-agentfuse\[langchain\]"):
        run_guarded_tool_adapter_scenario({})
    with pytest.raises(ImportError, match=r"dhms-agentfuse\[langchain\]"):
        create_dhms_guarded_langchain_agent_loop_harness({})

    harness = create_dhms_langchain_agent_harness()
    assert harness["langchain_available"] is False
    assert "dhms-agentfuse[langchain]" in harness["dependency_note"]
