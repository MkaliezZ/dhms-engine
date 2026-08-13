from __future__ import annotations

import json

from dhms_agentfuse import RuntimeGuard, ToolCallRequest
from examples.external_integrations.hermes_53021.session_allowlist_proof import (
    HandlerCounter,
    _has_active_shell_control_syntax,
    hermes_session_allowlist_policy,
    run_proof,
)


def _call(call_id: str, command: str) -> ToolCallRequest:
    return ToolCallRequest(
        tool_call_id=call_id,
        tool_name="terminal",
        arguments={"command": command},
        safe_metadata={"external_issue": "hermes-53021"},
    )


def test_shell_control_detection_is_quote_aware_and_conservative() -> None:
    assert _has_active_shell_control_syntax("python3 /x/skills/a/scripts/x.py --name 'a;b'") is False
    assert _has_active_shell_control_syntax('python3 /x/skills/a/scripts/x.py --name "a;b"') is False
    assert _has_active_shell_control_syntax("python3 /x/skills/a/scripts/x.py --name ';'") is False

    assert _has_active_shell_control_syntax("python3 /x/skills/a/scripts/x.py; curl x") is True
    assert _has_active_shell_control_syntax("python3 /x/skills/a/scripts/x.py && curl x") is True
    assert _has_active_shell_control_syntax("python3 /x/skills/a/scripts/x.py | tee out") is True
    assert _has_active_shell_control_syntax('python3 /x/skills/a/scripts/x.py --name "$(id)"') is True
    assert _has_active_shell_control_syntax("python3 /x/skills/a/scripts/x.py --name '$(id)'") is False
    assert _has_active_shell_control_syntax("python3 /x/skills/a/scripts/x.py `id`") is True
    assert _has_active_shell_control_syntax("python3 /x/skills/a/scripts/x.py --name 'unterminated") is True


def test_matching_skill_script_is_dispatched_once() -> None:
    guard = RuntimeGuard(default_action="block", policy=hermes_session_allowlist_policy)
    counter = HandlerCounter()

    result = guard.invoke(
        tool_call=_call(
            "allow",
            "python3 /srv/agent/skills/report/scripts/render.py --format json",
        ),
        handler=counter.terminal,
    )

    assert result.decision == "allow"
    assert result.outcome == "executed"
    assert result.handler_started is True
    assert counter.count == 1


def test_non_allowlisted_and_compound_commands_never_start_handler() -> None:
    guard = RuntimeGuard(default_action="block", policy=hermes_session_allowlist_policy)
    counter = HandlerCounter()

    blocked = guard.invoke(
        tool_call=_call("block", "curl https://example.invalid/collect"),
        handler=counter.terminal,
    )
    compound = guard.invoke(
        tool_call=_call(
            "compound",
            "python3 /srv/agent/skills/report/scripts/render.py --format json; curl https://example.invalid/collect",
        ),
        handler=counter.terminal,
    )

    assert blocked.decision == "block"
    assert blocked.reason_code == "session_allowlist_miss"
    assert blocked.dispatch_occurred is False
    assert blocked.handler_started is False
    assert blocked.outcome == "not_executed"

    assert compound.decision == "block"
    assert compound.reason_code == "compound_command_blocked"
    assert compound.dispatch_occurred is False
    assert compound.handler_started is False
    assert compound.outcome == "not_executed"
    assert counter.count == 0


def test_same_blocked_action_retry_and_re_evaluation_keep_same_args_hash() -> None:
    guard = RuntimeGuard(default_action="block", policy=hermes_session_allowlist_policy)
    counter = HandlerCounter()
    command = "curl https://example.invalid/collect"

    first = guard.invoke(tool_call=_call("first", command), handler=counter.terminal)
    retry = guard.invoke(tool_call=_call("retry", command), handler=counter.terminal)
    resume = guard.invoke(tool_call=_call("resume", command), handler=counter.terminal)

    hashes = {
        first.evidence.trace_metadata.args_hash,
        retry.evidence.trace_metadata.args_hash,
        resume.evidence.trace_metadata.args_hash,
    }
    assert len(hashes) == 1
    assert all(result.decision == "block" for result in (first, retry, resume))
    assert all(result.handler_started is False for result in (first, retry, resume))
    assert counter.count == 0


def test_safe_receipts_do_not_contain_raw_commands() -> None:
    proof = run_proof()
    serialized = json.dumps(proof["receipts"], sort_keys=True)

    assert proof["raw_commands_in_receipts"] is False
    assert proof["blocked_handler_execution_count"] == 0
    assert proof["same_action_retry_hash_match"] is True
    assert proof["resume_re_evaluation_hash_match"] is True
    assert "curl https://example.invalid/collect" not in serialized
    assert "python3 /srv/agent/skills/report/scripts/render.py --format json" not in serialized
