"""Release-only drift checks for the AgentFuse v3.7.3 public beta."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from dhms_agentfuse.evidence_schema import SCHEMA_VERSION


ROOT = Path(__file__).parents[1]
SEAL_PATH = ROOT / "release/agentfuse_v3_7_3_release_seal.json"
ISSUE_FORM_PATH = ROOT / ".github/ISSUE_TEMPLATE/agentfuse-beta-integration.yml"


def _seal() -> dict[str, object]:
    return json.loads(SEAL_PATH.read_text())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_release_seal_records_exact_frozen_evidence() -> None:
    seal = _seal()
    pyproject = (ROOT / "pyproject.toml").read_text()

    assert seal["release_version"] == "3.7.3"
    assert seal["package_version"] == "3.7.3"
    assert re.search(r'^version = "3\.7\.3"$', pyproject, re.MULTILINE)
    assert seal["evidence_schema_version"] == SCHEMA_VERSION
    assert seal["canonical_source_commit"] == (
        "ae3d75287415d8c80a1726a73dbee1ef3deb6421"
    )
    assert seal["review_evidence"] == {
        "pull_request": 11,
        "reviewed_head": "bbc4bf8bf9d66c347c05939385ff0b82a3949df0",
        "ci_run": 32051700104,
        "wheel_artifact": 9294922822,
        "wheel_sha256": (
            "317bf6967b4ce881754b9c1c313c0bfe8abbc014e1e98bfe852cd8c49f3903b4"
        ),
        "observed_dependencies": {"langchain-core": "1.5.5"},
        "matrix": [
            {
                "python": "3.10",
                "langgraph": "1.2.11",
                "result_artifact": 9294931622,
                "verdict": "PASS",
            },
            {
                "python": "3.11",
                "langgraph": "1.2.0",
                "result_artifact": 9294932517,
                "verdict": "PASS",
            },
            {
                "python": "3.11",
                "langgraph": "1.2.11",
                "result_artifact": 9294930572,
                "verdict": "PASS",
            },
        ],
    }
    assert seal["post_merge_evidence"] == {
        "merge_commit": "ae3d75287415d8c80a1726a73dbee1ef3deb6421",
        "ci_run": 32095927125,
        "wheel_artifact": 9309921770,
        "wheel_sha256": (
            "cc6e95a10ea529e6cd29bc279c3ecf2c621351ef31563ab0d6affd6acffecce0"
        ),
        "observed_dependencies": {"langchain-core": "1.5.6"},
        "matrix": [
            {
                "python": "3.10",
                "langgraph": "1.2.11",
                "result_artifact": 9309929120,
                "verdict": "PASS",
            },
            {
                "python": "3.11",
                "langgraph": "1.2.0",
                "result_artifact": 9309929013,
                "verdict": "PASS",
            },
            {
                "python": "3.11",
                "langgraph": "1.2.11",
                "result_artifact": 9309928624,
                "verdict": "PASS",
            },
        ],
    }
    assert seal["integration_profiles"] == [
        "python-runtime-guard",
        "provider-neutral-reference",
        "langgraph-tool-node",
        "dsh-tools-pre-execute",
    ]
    assert seal["next_mode"] == "public_beta"
    assert seal["external_signal_required_for_next_product_architecture"] is True
    assert json.dumps(seal, indent=2) + "\n" == SEAL_PATH.read_text()


def test_release_seal_protects_runtime_core_and_compatibility_manifest() -> None:
    seal = _seal()

    for relative_path, expected_digest in seal["protected_runtime_files"].items():
        assert _sha256(ROOT / relative_path) == expected_digest

    manifest = seal["compatibility_manifest"]
    assert _sha256(ROOT / manifest["path"]) == manifest["sha256"]
    assert seal["artifact_interpretation"] == {
        "separate_builds_passed_same_bounded_invariants": True,
        "byte_identical_reproducible_build_claim": False,
        "arbitrary_future_transitive_compatibility_claim": False,
    }


def test_public_beta_issue_form_has_minimal_required_inputs() -> None:
    form = ISSUE_FORM_PATH.read_text()

    assert "name: AgentFuse Beta Integration Request" in form
    assert 'title: "[AgentFuse Beta] "' in form
    assert form.count("required: true") == 4
    for field_id in (
        "repository_url",
        "runtime_framework",
        "protected_tool",
        "desired_boundary",
        "notes",
    ):
        assert f"id: {field_id}" in form
    assert "Share your agent repo and one protected tool." in form
