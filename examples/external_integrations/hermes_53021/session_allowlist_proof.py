"""AgentFuse external proof for the threat model in Hermes issue #53021.

This is intentionally not a Hermes patch or production integration. It models the
issue's proposed session-scoped deny-by-default terminal policy and proves the
AgentFuse pre-dispatch invariants with an in-memory handler.
"""

from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass
from typing import Any

from dhms_agentfuse import RuntimeGuard, RuntimePolicyDecision, ToolCallRequest

ISSUE_URL = "https://github.com/NousResearch/hermes-agent/issues/53021"
POLICY_ID = "external:hermes-53021:session-allowlist-v1"
ALLOWED_COMMAND_PATTERNS = ("python3 */skills/*/scripts/*.py *",)


@dataclass
class HandlerCounter:
    count: int = 0

    def terminal(self, *, command: str) -> dict[str, Any]:
        """Synthetic protected handler; it never starts a real shell."""

        self.count += 1
        return {"synthetic_execution": True, "command_length": len(command)}


def _has_active_shell_control_syntax(command: str) -> bool:
    """Conservatively reject compound/shell-control syntax.

    Operators such as ;, |, &, redirections, and newlines are active only when
    unquoted. Command substitution via $() and backticks remains active inside
    double quotes, so it is rejected everywhere except single quotes.
    """

    quote: str | None = None
    escaped = False
    index = 0
    while index < len(command):
        char = command[index]

        if escaped:
            escaped = False
            index += 1
            continue

        if char == "\\" and quote != "'":
            escaped = True
            index += 1
            continue

        if char == "'":
            if quote is None:
                quote = "'"
            elif quote == "'":
                quote = None
            index += 1
            continue

        if char == '"':
            if quote is None:
                quote = '"'
            elif quote == '"':
                quote = None
            index += 1
            continue

        if quote != "'":
            if char == "`":
                return True
            if char == "$" and index + 1 < len(command) and command[index + 1] == "(":
                return True

        if quote is None and char in ";|&><\n\r":
            return True

        index += 1

    return quote is not None or escaped


def hermes_session_allowlist_policy(tool_call: ToolCallRequest) -> RuntimePolicyDecision:
    """Model the deny-by-default command semantics proposed in Hermes #53021."""

    if tool_call.tool_name != "terminal":
        return RuntimePolicyDecision.block("unexpected_tool", POLICY_ID)

    command = tool_call.arguments.get("command")
    if not isinstance(command, str) or not command.strip():
        return RuntimePolicyDecision.block("invalid_command", POLICY_ID)

    if _has_active_shell_control_syntax(command):
        return RuntimePolicyDecision.block("compound_command_blocked", POLICY_ID)

    if any(fnmatch.fnmatchcase(command, pattern) for pattern in ALLOWED_COMMAND_PATTERNS):
        return RuntimePolicyDecision.allow("session_allowlist_match", POLICY_ID)

    return RuntimePolicyDecision.block("session_allowlist_miss", POLICY_ID)


def _request(call_id: str, command: str) -> ToolCallRequest:
    return ToolCallRequest(
        tool_call_id=call_id,
        tool_name="terminal",
        arguments={"command": command},
        safe_metadata={
            "external_issue": "hermes-53021",
            "approval_mode": "allowlist",
        },
    )


def _args_hash(result: Any) -> str:
    return result.evidence.trace_metadata.args_hash


def run_proof() -> dict[str, Any]:
    guard = RuntimeGuard(default_action="block", policy=hermes_session_allowlist_policy)
    counter = HandlerCounter()

    allowed_command = "python3 /srv/agent/skills/report/scripts/render.py --format json"
    blocked_command = "curl https://example.invalid/collect"
    compound_command = (
        "python3 /srv/agent/skills/report/scripts/render.py --format json; "
        "curl https://example.invalid/collect"
    )

    allowed = guard.invoke(
        tool_call=_request("allow-1", allowed_command),
        handler=counter.terminal,
    )
    count_after_allow = counter.count

    blocked = guard.invoke(
        tool_call=_request("block-1", blocked_command),
        handler=counter.terminal,
    )
    count_after_block = counter.count

    compound = guard.invoke(
        tool_call=_request("compound-1", compound_command),
        handler=counter.terminal,
    )
    count_after_compound = counter.count

    retry = guard.invoke(
        tool_call=_request("block-retry", blocked_command),
        handler=counter.terminal,
    )
    count_after_retry = counter.count

    # This is deliberately a deterministic re-evaluation, not a claim about
    # Hermes persistence or restart recovery. A real Hermes adapter would own
    # persisted approval/session lifecycle and map the resumed call back here.
    resume_re_evaluation = guard.invoke(
        tool_call=_request("block-resume", blocked_command),
        handler=counter.terminal,
    )
    count_after_resume = counter.count

    changed = guard.invoke(
        tool_call=_request(
            "changed-1",
            "python3 /srv/agent/skills/audit/scripts/check.py --scope local",
        ),
        handler=counter.terminal,
    )

    assert allowed.decision == "allow"
    assert allowed.outcome == "executed"
    assert allowed.handler_started is True
    assert count_after_allow == 1

    for result in (blocked, compound, retry, resume_re_evaluation):
        assert result.decision == "block"
        assert result.outcome == "not_executed"
        assert result.dispatch_occurred is False
        assert result.handler_started is False
        assert result.side_effect_occurred is False

    assert blocked.reason_code == "session_allowlist_miss"
    assert compound.reason_code == "compound_command_blocked"
    assert count_after_block == 1
    assert count_after_compound == 1
    assert count_after_retry == 1
    assert count_after_resume == 1

    assert _args_hash(blocked) == _args_hash(retry) == _args_hash(resume_re_evaluation)
    assert _args_hash(changed) != _args_hash(blocked)
    assert changed.decision == "allow"
    assert changed.handler_started is True
    assert counter.count == 2

    safe_receipts = {
        "allow": allowed.to_safe_dict(),
        "block": blocked.to_safe_dict(),
        "compound": compound.to_safe_dict(),
        "retry": retry.to_safe_dict(),
        "resume_re_evaluation": resume_re_evaluation.to_safe_dict(),
        "changed": changed.to_safe_dict(),
    }
    serialized = json.dumps(safe_receipts, sort_keys=True)
    for raw_command in (allowed_command, blocked_command, compound_command):
        assert raw_command not in serialized

    return {
        "issue": ISSUE_URL,
        "policy_id": POLICY_ID,
        "allow_pattern": ALLOWED_COMMAND_PATTERNS[0],
        "handler_execution_count": counter.count,
        "blocked_handler_execution_count": 0,
        "same_blocked_action_hash": _args_hash(blocked),
        "same_action_retry_hash_match": _args_hash(blocked) == _args_hash(retry),
        "resume_re_evaluation_hash_match": _args_hash(blocked) == _args_hash(resume_re_evaluation),
        "raw_commands_in_receipts": False,
        "receipts": safe_receipts,
    }


def main() -> None:
    proof = run_proof()
    print(json.dumps(proof, indent=2, sort_keys=True))
    print("AGENTFUSE_HERMES_53021_EXTERNAL_PROOF_PASS")


if __name__ == "__main__":
    main()
