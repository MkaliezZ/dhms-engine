# DHMS Agent Suite Runner v1

## Purpose

Agent Suite Runner v1 runs a directory of dry-run agent cases through the Agent Harness and produces per-case plus aggregate diagnosis reports.

It supports:

* `MockAgentAdapter`
* `CommandAgentAdapter` using the existing `dhms-agent-command-v1` local JSON protocol

It does not enable real tool execution, remote agents, HTTP adapters, or real provider API calls from DHMS.

## Agent Case Format

Each case is a plain `.txt` file with lightweight fields:

```text
title:
scenario:
user_input:
memory_context:
context:
tool_state:
expected_agent_property:
risk_focus:
```

If fields are missing, DHMS runs the full file text as the input and marks unavailable metadata as `not_available`.

## Mock Suite Example

```bash
python3 cli.py test-agent-suite --suite cases/agent_core --mock-agent --n 1 --report --output reports/agent_harness_phase4/mock_suite
```

## Command Suite Example

```bash
python3 cli.py test-agent-suite --suite cases/agent_core --agent-command "python3 examples/agents/sample_json_agent.py" --n 1 --report --output reports/agent_harness_phase4/command_suite
```

## Report Outputs

Suite runs write:

* `per_case/<case_id>/agent_harness_report.json`
* `per_case/<case_id>/agent_harness_report.md`
* `suite_agent_report.json`
* `suite_agent_report.md`

The aggregate report includes diagnosis distribution, expected-property summary, side-effect safety summary, command adapter failure summary, top actionable cases, per-case report paths, and reproduction commands.

## Dry-Run Safety Policy

Agent Suite Runner v1 is dry-run only. Tool calls and side effects may be recorded as attempted trace evidence, but DHMS does not execute them. Any trace with `executed=true` side effects is treated as a Critical safety failure and should block release.

If all attempted side effects are blocked, the suite summary reports that the dry-run guard is working.

## Caveats

* Phase 4 suite runner does not enable real tool execution.
* Command adapter is local BYOA dry-run only.
* HTTP adapter is not implemented.
* `n=1` is preliminary.
* Sample agents are not production agents.

## Not Implemented

* HTTP adapter
* Real tool execution
* Production agent certification
