# DHMS Product Diagnosis v1.3

DHMS is a perturbation-based LLM memory/context stability tester with diagnosis-driven reports.

## What DHMS Tests

DHMS runs controlled memory and context perturbations, then reports product-facing diagnosis signals:

* memory perturbation
* context perturbation
* mock-vs-real divergence
* regime behavior drift
* expected-property violations
* style/format drift

## Current Status

* Product Diagnosis v1.3 is sealed.
* DeepSeek `deepseek:flash` is live-verified.
* OpenAI, Claude, Qwen, Kimi, Gemini, and Mistral are adapter-ready via BYOK.
* Agent Harness v1 is active on the `agent-harness-v1` preview branch.
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

## Agent Harness Preview

Agent Harness v1 is active on the `agent-harness-v1` branch. `main` remains the Product Diagnosis v1.3 stable checkpoint.

The preview branch contains dry-run local command-agent testing, adapter conformance, execution-safety reports, an expected-property signal layer, and limited OpenClaw + DeepSeek pilot evidence. It is preview-only and is not production certification, full-suite validation, system-level sandbox proof, or a claim that real LLM Judge is active.

## Documentation

* [Product README](README_PRODUCT.md)
* [Public demo package](docs/public_demo_package.md)
* [Diagnosis layer v1.3](docs/diagnosis_layer_v1_3.md)
* [Top critical case explanations](docs/top_critical_case_explanations.md)
* [Release checkpoint devlog](docs/devlog/2026-06-20-dhms-product-diagnosis-v1-3.md)

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
* Agent Harness v1 preview work lives on `agent-harness-v1` and is not merged into this stable checkpoint.

Metric names remain unchanged: `stability`, `sensitivity`, `specificity`, and `isolation_strength`.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).
