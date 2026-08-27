"""Contract tests for the public LangGraph five-minute integration trial."""

from __future__ import annotations

import ast
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

from dhms_agentfuse.integrations import get_integration


TRIAL_DIR = Path(__file__).parents[1] / "examples/integration_trial/five_minute_v3_7_1"
CONSUMER_PATH = TRIAL_DIR / "consumer.py"
RUNNER_PATH = TRIAL_DIR / "run_trial.py"


def _consumer_module():
    spec = importlib.util.spec_from_file_location("v3_7_1_consumer", CONSUMER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _result() -> dict[str, object]:
    return _consumer_module().run_trial()


def _case(result: dict[str, object], case_id: str) -> dict[str, object]:
    return next(case for case in result["cases"] if case["case_id"] == case_id)


def test_allow_and_block_use_real_public_langgraph_path() -> None:
    result = _result()
    allow = _case(result, "allow")
    block = _case(result, "block")

    assert result["integration_id"] == "langgraph-tool-node"
    assert get_integration("langgraph-tool-node").canonical_actions == (
        "allow",
        "block",
    )
    assert importlib.metadata.version("langgraph") == "1.2.11"
    assert allow["policy_decision"] == "allow"
    assert allow["execution_outcome"] == "host_completed"
    assert allow["protected_handler_count"] == 1
    assert allow["tool_call_identity_preserved"] is True
    assert block["policy_decision"] == "block"
    assert block["execution_outcome"] == "not_executed"
    assert block["dispatch_observed"] is False
    assert block["protected_handler_count"] == 0
    assert block["tool_call_identity_preserved"] is True


def test_safe_result_is_deterministic_and_excludes_raw_argument() -> None:
    first = _result()
    second = _result()
    serialized = json.dumps(first, sort_keys=True, separators=(",", ":"))

    assert serialized == json.dumps(second, sort_keys=True, separators=(",", ":"))
    assert "synthetic-protected-value-v3-7-1" not in serialized
    assert first["requirements"] == {
        "api_key_required": False,
        "network_required_at_runtime": False,
        "model_call_required": False,
    }


def test_json_only_stdout_is_one_json_document() -> None:
    completed = subprocess.run(
        [sys.executable, str(RUNNER_PATH), "--json-only"],
        cwd=TRIAL_DIR,
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stderr == ""
    result = json.loads(completed.stdout)
    assert result["verdict"] == "PASS"
    assert completed.stdout.count("\n") == 1


def test_consumer_uses_only_public_agentfuse_imports() -> None:
    tree = ast.parse(CONSUMER_PATH.read_text())
    imports = [node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    agentfuse_modules = {node.module for node in imports if node.module and node.module.startswith("dhms_agentfuse")}

    assert agentfuse_modules == {"dhms_agentfuse", "dhms_agentfuse.integrations"}
    assert "tests" not in CONSUMER_PATH.read_text()
    assert "examples.conformance" not in CONSUMER_PATH.read_text()
    assert "dsh" not in CONSUMER_PATH.read_text().lower()
