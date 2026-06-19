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
* Agent Harness v1 has not started yet.
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
* Future Agent Harness v1 will be a later layer and is not part of this checkpoint.

Metric names remain unchanged: `stability`, `sensitivity`, `specificity`, and `isolation_strength`.
