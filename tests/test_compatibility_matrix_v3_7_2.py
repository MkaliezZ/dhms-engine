"""Contract tests for the AgentFuse v3.7.2 compatibility matrix."""

from __future__ import annotations

import ast
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).parents[1]
COMPATIBILITY_DIR = ROOT / "validation/compatibility_v3_7_2"
MANIFEST_PATH = COMPATIBILITY_DIR / "compatibility_matrix.json"
PROBE_PATH = COMPATIBILITY_DIR / "probe.py"
WORKFLOW_PATH = ROOT / ".github/workflows/agentfuse-ci.yml"
EXPECTED_CELLS = [
    {
        "python": "3.10",
        "langgraph": "1.2.11",
        "roles": ["python-floor", "frozen-runtime-baseline"],
    },
    {
        "python": "3.11",
        "langgraph": "1.2.0",
        "roles": ["declared-runtime-floor"],
    },
    {
        "python": "3.11",
        "langgraph": "1.2.11",
        "roles": ["frozen-baseline", "current-stable"],
    },
]


def _manifest() -> dict[str, object]:
    return json.loads(MANIFEST_PATH.read_text())


def _probe_module():
    spec = importlib.util.spec_from_file_location("compatibility_probe_v3_7_2", PROBE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manifest_has_exact_deterministic_cells_and_roles() -> None:
    manifest = _manifest()
    assert manifest["matrix_version"] == "agentfuse-compatibility-matrix-v3.7.2"
    assert manifest["integration_id"] == "langgraph-tool-node"
    assert manifest["profile_frozen_tested_version"] == "1.2.11"
    assert manifest["cells"] == EXPECTED_CELLS
    assert len({(cell["python"], cell["langgraph"]) for cell in manifest["cells"]}) == 3
    assert json.dumps(manifest, indent=2) + "\n" == MANIFEST_PATH.read_text()


def test_manifest_versions_are_exact_reviewed_non_yanked_releases() -> None:
    manifest = _manifest()
    version_pattern = re.compile(r"^[0-9]+\.[0-9]+(?:\.[0-9]+)?$")
    assert manifest["declared_dependency_range"] == "langgraph>=1.2,<2.0"
    assert manifest["discovery"] == {
        "source": "https://pypi.org/pypi/langgraph/json",
        "checked_on": "2026-08-18",
        "current_stable_version": "1.2.11",
        "prereleases_excluded": True,
        "yanked_releases_excluded": True,
    }
    assert set(manifest["release_metadata"]) == {"1.2.0", "1.2.11"}
    for cell in manifest["cells"]:
        assert version_pattern.fullmatch(cell["python"])
        assert version_pattern.fullmatch(cell["langgraph"])
        assert manifest["release_metadata"][cell["langgraph"]] == {
            "prerelease": False,
            "yanked": False,
        }
    assert "latest" not in MANIFEST_PATH.read_text().lower()


def test_probe_runs_real_allow_and_block_path_deterministically() -> None:
    probe = _probe_module()
    observed_langgraph = importlib.metadata.version("langgraph")
    expected_python = f"{sys.version_info.major}.{sys.version_info.minor}"
    first = probe.run_probe(
        expected_python_version=expected_python,
        expected_langgraph_version=observed_langgraph,
        expected_package_version="3.7.4",
    )
    second = probe.run_probe(
        expected_python_version=expected_python,
        expected_langgraph_version=observed_langgraph,
        expected_package_version="3.7.4",
    )
    assert first == second
    assert first["profile_frozen_tested_version"] == "1.2.11"
    assert first["cases"]["allow"] == {
        "decision": "allow",
        "execution_outcome": "host_completed",
        "handler_started": None,
        "handler_count": 1,
        "tool_call_identity_preserved": True,
    }
    assert first["cases"]["block"] == {
        "decision": "block",
        "execution_outcome": "not_executed",
        "dispatch_observed": False,
        "handler_started": False,
        "handler_count": 0,
        "tool_call_identity_preserved": True,
    }
    assert "synthetic-protected-value-v3-7-2" not in json.dumps(first, sort_keys=True)


def test_probe_json_only_is_one_document_and_uses_explicit_runtime_validation() -> None:
    observed_langgraph = importlib.metadata.version("langgraph")
    expected_python = f"{sys.version_info.major}.{sys.version_info.minor}"
    completed = subprocess.run(
        [
            sys.executable,
            str(PROBE_PATH),
            "--expected-python-version",
            expected_python,
            "--expected-langgraph-version",
            observed_langgraph,
            "--expected-package-version",
            "3.7.4",
            "--json-only",
        ],
        cwd=COMPATIBILITY_DIR,
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stderr == ""
    assert completed.stdout.count("\n") == 1
    assert json.loads(completed.stdout)["verdict"] == "PASS"

    tree = ast.parse(PROBE_PATH.read_text())
    assert not [node for node in ast.walk(tree) if isinstance(node, ast.Assert)]
    imports = [node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    agentfuse_modules = {
        node.module
        for node in imports
        if node.module and node.module.startswith("dhms_agentfuse")
    }
    assert agentfuse_modules == {"dhms_agentfuse", "dhms_agentfuse.integrations"}
    source = PROBE_PATH.read_text().lower()
    assert "tests" not in source
    assert "examples.conformance" not in source
    assert "dsh" not in source


def test_workflow_uses_one_manifest_driven_wheel_matrix() -> None:
    workflow = WORKFLOW_PATH.read_text()
    assert "permissions:\n  contents: read" in workflow
    assert "fail-fast: false" in workflow
    assert "fromJSON(needs.build-wheel.outputs.matrix)" in workflow
    assert "validation/compatibility_v3_7_2/compatibility_matrix.json" in workflow
    assert workflow.count("python -m pip install -e .") == 1
    assert workflow.count("python -m pip wheel --no-deps") == 1
    assert "actions/upload-artifact@v4" in workflow
    assert "actions/download-artifact@v4" in workflow
    assert "--forbid-import-root \"$GITHUB_WORKSPACE\"" in workflow
    assert 'COMPAT_LANGGRAPH: ${{ matrix.langgraph }}' in workflow
    assert 'COMPAT_PYTHON: ${{ matrix.python }}' in workflow
    assert '"langgraph==${{ matrix.langgraph }}"' not in workflow
    assert workflow.count("agentfuse-wheel-v3-7-4") == 2
    assert workflow.count("dhms_agentfuse-3.7.4-py3-none-any.whl") == 4
    assert "fetch-depth: 0" in workflow
