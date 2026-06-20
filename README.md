# DHMS Product Diagnosis v1.3

DHMS is a perturbation-based LLM memory/context stability tester with diagnosis-driven reports.

> Branch note: `agent-harness-v1` is a development preview branch. The stable public checkpoint remains `main` at Product Diagnosis v1.3. This branch contains Agent Harness v1 Phase 1–4.5 work in progress.

## Agent Harness MVP Quickstart

`agent-harness-v1` is a dry-run MVP preview branch. It currently supports mock agents and local command agents that follow `dhms-agent-command-v1`; `main` remains the Product Diagnosis v1.3 stable checkpoint.

What works now:

* mock agent single-case test
* command agent single-case test
* mock suite
* command suite
* diagnosis-enriched reports
* dry-run side-effect safety checks

Mock suite:

```bash
python3 cli.py test-agent-suite --suite cases/agent_core --mock-agent --n 1 --report --output reports/agent_harness_preview/mock_suite
```

Command suite:

```bash
python3 cli.py test-agent-suite --suite cases/agent_core --agent-command "python3 examples/agents/sample_json_agent.py" --n 1 --report --output reports/agent_harness_preview/command_suite
```

Bad-agent dry-run violation demo:

```bash
python3 cli.py test-agent --agent-command "python3 examples/agents/bad_dry_run_false_agent.py" --input "Check the refund policy and issue a refund if eligible." --n 1 --report --output reports/agent_harness_preview/bad_dry_run_false
```

Smoke validation:

```bash
python3 validation/run_agent_harness_mvp_smoke.py
```

Outputs:

* per-case reports under `reports/.../per_case/`
* aggregate suite reports: `suite_agent_report.json` and `suite_agent_report.md`
* validation reports: `validation/outputs/agent_harness_mvp_smoke_report.json` and `validation/outputs/agent_harness_mvp_smoke_report.md`

## What DHMS Tests

DHMS runs controlled memory and context perturbations, then reports product-facing diagnosis signals:

* memory perturbation
* context perturbation
* mock-vs-real divergence
* regime behavior drift
* expected-property violations
* style/format drift

## Current Status

* `main` remains the Product Diagnosis v1.3 stable checkpoint.
* DeepSeek `deepseek:flash` is live-verified.
* OpenAI, Claude, Qwen, Kimi, Gemini, and Mistral are adapter-ready via BYOK.
* This branch is the Agent Harness v1 development branch.
* Phase 1 completed: mock dry-run skeleton and trace contract.
* Phase 2 completed: trace diagnosis layer.
* Phase 3 completed: command adapter / BYOA local agent JSON protocol.
* Phase 4 completed: agent suite runner and aggregate agent diagnosis reports.
* Phase 4.5 completed: MVP demo guide, conformance checklist, bad-agent examples, and smoke validation.
* HTTP adapter is not implemented.
* Real tool execution is not enabled.
* Real provider API calls are not run by DHMS.
* Agent Harness remains dry-run safe.
* GitHub checkpoint tag: `v0.1.3-product-diagnosis`.

## Quickstart

Mock demo:

```bash
python3 cli.py test --input "Does this agent stay consistent?" --models mock --n 1 --report --output reports/demo_mock_single
```

DeepSeek demo, if `DEEPSEEK_API_KEY` is configured:

```bash
python3 cli.py test --input-file examples/agent_memory_case.txt --models mock,deepseek:flash --n 1 --report --output reports/public_demo_deepseek_flash
```

LLM core suite:

```bash
python3 cli.py test-suite --suite cases/llm_core --models mock --n 1 --report --output reports/public_demo_llm_core_mock
```

## Diagnosis Caveats

* High drift is not automatically provider failure.
* Expected-property violation is stronger evidence than mock-real divergence alone.
* `n=1` is preliminary and cannot establish general stochastic stability.
* Recommendations are rule-based and evidence-backed, not LLM-generated.

## Documentation

* [Product README](README_PRODUCT.md)
* [Public demo package](docs/public_demo_package.md)
* [Diagnosis layer v1.3](docs/diagnosis_layer_v1_3.md)
* [Top critical case explanations](docs/top_critical_case_explanations.md)
* [Release checkpoint devlog](docs/devlog/2026-06-20-dhms-product-diagnosis-v1-3.md)
* [Agent Harness v1 plan](docs/agent_harness_v1_plan.md)
* [Agent command protocol v1](docs/agent_command_protocol_v1.md)
* [Agent Harness MVP demo guide](docs/agent_harness_mvp_demo_guide.md)
* [Agent suite runner v1](docs/agent_suite_runner_v1.md)
* [Agent adapter conformance checklist](docs/agent_adapter_conformance_checklist.md)
* [Agent Harness preview branch status](docs/agent_harness_preview_branch_status.md)

## Architecture / Historical Engine Layer

DHMS is organized as a strict layered system:

```text
spec -> contract -> binding -> engine -> product diagnosis
```

* `spec/`, `contract/`, and `binding/` define the protected semantic boundary.
* V1 handles measurement aggregation and repeated-trial orchestration.
* V2 adds cross-model execution and statistical comparison.
* V2.5 adds the real-provider bridge and provider:model routing without overriding V2 metrics.
* Product Diagnosis v1.3 adds taxonomy, expected-property checks, rule-based recommendations, and public reports.
* Agent Harness v1 is being developed on `agent-harness-v1` as a dry-run layer for mock and local command-agent traces.

Metric names remain unchanged: `stability`, `sensitivity`, `specificity`, and `isolation_strength`.
