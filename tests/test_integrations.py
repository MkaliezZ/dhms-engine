"""Public integration-profile and registry contract tests."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

import pytest

from dhms_agentfuse.integrations import (
    IntegrationProfile,
    get_integration,
    list_integrations,
)
from examples.conformance.cross_adapter_v3_6_2.run_conformance import (
    FIXTURE_PATH,
    load_fixture_document,
    run_conformance,
)


EXPECTED_IDS = (
    "python-runtime-guard",
    "provider-neutral-reference",
    "langgraph-tool-node",
    "dsh-tools-pre-execute",
)
FIXTURE_VERSION = "agentfuse-cross-adapter-conformance-v3.6.2"
FIXTURE_DIGEST = "1f66c9e20ff28ebeeae128b8aaf38a5b251582496a753acded9530b819056d7b"


def _serialized_registry() -> str:
    return json.dumps(
        [profile.to_safe_dict() for profile in list_integrations()],
        sort_keys=True,
        separators=(",", ":"),
    )


def _walk(value: Any):
    yield value
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _walk(key)
            yield from _walk(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk(item)


def test_public_surface_is_minimal() -> None:
    import dhms_agentfuse.integrations as integrations

    assert integrations.__all__ == [
        "IntegrationProfile",
        "get_integration",
        "list_integrations",
    ]


def test_profiles_are_frozen_and_collection_fields_are_immutable() -> None:
    profile = get_integration("python-runtime-guard")

    with pytest.raises(FrozenInstanceError):
        profile.runtime_family = "changed"  # type: ignore[misc]
    with pytest.raises(TypeError, match="limitations must be a tuple"):
        replace(profile, limitations=["mutable"])  # type: ignore[arg-type]
    assert isinstance(profile.evidenced_capabilities, tuple)
    assert isinstance(profile.limitations, tuple)


def test_profile_rejects_noncanonical_action_vocabulary() -> None:
    profile = get_integration("python-runtime-guard")

    with pytest.raises(ValueError, match="exactly allow\\|block"):
        replace(profile, canonical_actions=("allow", "block", "ask"))


def test_serialization_is_deterministic_metadata_only() -> None:
    first = _serialized_registry()
    second = _serialized_registry()

    assert first == second
    assert all(not callable(value) for value in _walk(json.loads(first)))
    assert "RuntimeGuard object" not in first


def test_serialization_excludes_sensitive_and_machine_local_values() -> None:
    serialized = _serialized_registry()

    for forbidden in (
        "/Users/",
        "C:\\",
        "RAW_",
        "agentfuse-v3.6.2-synthetic-sentinel",
        "api_key",
        "password",
        "credential_value",
    ):
        assert forbidden not in serialized


def test_registry_order_and_ids_are_stable_and_unique() -> None:
    profiles = list_integrations()
    ids = tuple(profile.integration_id for profile in profiles)

    assert ids == EXPECTED_IDS
    assert len(ids) == len(set(ids))
    assert list_integrations() is profiles


@pytest.mark.parametrize("integration_id", EXPECTED_IDS)
def test_get_known_profile_returns_registered_immutable_value(
    integration_id: str,
) -> None:
    profile = get_integration(integration_id)

    assert isinstance(profile, IntegrationProfile)
    assert profile in list_integrations()
    assert profile.integration_id == integration_id


def test_unknown_profile_raises_key_error() -> None:
    with pytest.raises(KeyError):
        get_integration("unknown-runtime")


def test_canonical_actions_and_fixture_provenance_are_frozen() -> None:
    assert load_fixture_document()["fixture_version"] == FIXTURE_VERSION
    assert hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest() == FIXTURE_DIGEST

    for profile in list_integrations():
        assert profile.canonical_actions == ("allow", "block")
        assert profile.fixture_version == FIXTURE_VERSION
        assert profile.fixture_digest == FIXTURE_DIGEST


def test_runtime_guard_profile_preserves_canonical_boundary() -> None:
    profile = get_integration("python-runtime-guard")

    assert profile.integration_kind == "canonical"
    assert profile.implementation_owner == "dhms"
    assert {"decision_only_sync", "decision_only_async"} <= set(
        profile.evidenced_capabilities
    )
    assert {"guarded_dispatch_sync", "guarded_dispatch_async"} <= set(
        profile.evidenced_capabilities
    )
    assert "interruption_observed" not in profile.evidenced_capabilities
    assert "interruption" in profile.host_owned_facts


def test_reference_profile_is_explicitly_non_production() -> None:
    profile = get_integration("provider-neutral-reference")

    assert profile.integration_kind == "reference"
    assert "interruption_observed" in profile.evidenced_capabilities
    assert "execution_failure_observed" in profile.evidenced_capabilities
    assert "sync_async_parity" in profile.evidenced_capabilities
    assert any("not a production adapter" in item for item in profile.limitations)


def test_langgraph_profile_is_bounded_to_tested_adapter_path() -> None:
    profile = get_integration("langgraph-tool-node")

    assert profile.integration_kind == "internal_adapter"
    assert profile.tested_runtime == "langgraph"
    assert profile.tested_version == "1.2.11"
    assert "interruption_observed" in profile.evidenced_capabilities
    assert {"graph_control_flow", "checkpoint", "resume"} <= set(
        profile.host_owned_facts
    )
    assert any("future LangGraph compatibility" in item for item in profile.limitations)
    assert any("not an official LangGraph certification" in item for item in profile.limitations)


def test_dsh_profile_is_external_pinned_metadata_only() -> None:
    profile = get_integration("dsh-tools-pre-execute")

    assert profile.integration_kind == "external_adapter"
    assert profile.implementation_owner == "external_project"
    assert profile.tested_version == "0.1.0-rc.7"
    assert profile.tested_commit == "99f6f02fecdb7dff40c3fbc9470f5907c29f74ca"
    assert any(
        "366d213f207a833d45669b20551a33117eaeb6e6" in item
        for item in profile.evidence_references
    )
    assert "ask" not in profile.canonical_actions
    assert "sync_async_parity" not in profile.evidenced_capabilities
    assert any("metadata-only" in item for item in profile.limitations)
    assert any("not prove protection of all DSH paths" in item for item in profile.limitations)


def test_python_owned_capability_claims_match_live_frozen_conformance() -> None:
    results = {
        (result.adapter_id, result.case_id): result
        for result in run_conformance(load_fixture_document())
    }

    for integration_id in EXPECTED_IDS[:3]:
        profile = get_integration(integration_id)
        capabilities = set(profile.evidenced_capabilities)
        interrupted = results[(integration_id, "09_ALLOW_THEN_INTERRUPT")]
        failure = results[(integration_id, "08_ALLOW_THEN_HANDLER_FAILURE")]
        parity = results[(integration_id, "13_SYNC_ASYNC_PARITY")]
        settlement = results[(integration_id, "14_ONE_TERMINAL_SETTLEMENT")]

        assert ("interruption_observed" in capabilities) is (
            interrupted.verdict == "PASS" and interrupted.interruption_observed is True
        )
        assert failure.verdict == "PASS"
        assert failure.execution_outcome == "execution_failed"
        assert ("execution_failure_observed" in capabilities) is True
        assert ("sync_async_parity" in capabilities) is (parity.verdict == "PASS")
        assert settlement.verdict == "PASS"
        assert settlement.terminal_settlement_count == 1


def test_frozen_not_applicable_boundaries_are_not_erased() -> None:
    runtime_guard = get_integration("python-runtime-guard")
    dsh = get_integration("dsh-tools-pre-execute")

    assert "interruption_observed" not in runtime_guard.evidenced_capabilities
    assert any("no proved host interruption surface" in item for item in runtime_guard.limitations)
    assert "sync_async_parity" not in dsh.evidenced_capabilities
    assert any("exception and invalid-decision cases" in item for item in dsh.limitations)
    assert any("sync/async parity was not applicable" in item for item in dsh.limitations)


def test_import_has_no_external_adapter_or_process_coupling(tmp_path: Path) -> None:
    code = """
import json
import sys
from dhms_agentfuse.integrations import list_integrations
loaded = sorted(
    name for name in sys.modules
    if name.lower().startswith(("dsh", "deepseek", "@deepseek-ai"))
)
print(json.dumps({"count": len(list_integrations()), "external_modules": loaded}))
"""
    environment = dict(os.environ)
    environment["PYTHONPATH"] = ""
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(completed.stdout) == {"count": 4, "external_modules": []}
    assert completed.stderr == ""
