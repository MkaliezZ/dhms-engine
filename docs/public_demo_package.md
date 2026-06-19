# DHMS Public Demo Package

DHMS helps developers test whether an LLM or agent remains stable when memory or context conditions are perturbed.

## Live Verified

* DeepSeek `deepseek:flash`

## Adapter-Ready / BYOK

* OpenAI
* Anthropic / Claude
* Qwen / DashScope
* Kimi / Moonshot
* Gemini
* Mistral

## DeepSeek Live-Verified Demo

Use this bounded demo only when `DEEPSEEK_API_KEY` is intentionally configured:

```bash
python3 cli.py test --input-file examples/agent_memory_case.txt --models mock,deepseek:flash --n 1 --report --output reports/public_demo_deepseek_flash
```

## DeepSeek Live-Verified Suite Demo

```bash
python3 cli.py test-suite --suite cases/llm_core --models mock,deepseek:flash --n 1 --report --output reports/public_demo_llm_core_deepseek
```

## Mock-Only Fallback Demo

```bash
python3 cli.py test-suite --suite cases/llm_core --models mock --n 1 --report --output reports/public_demo_llm_core_mock
```

## Diagnosis Layer

DHMS Product Diagnosis v1.3 adds diagnosis fields to the public demo reports:

* High drift does not automatically mean provider failure.
* Mock-real divergence means real provider output differs from the mock baseline.
* Expected-property violation is stronger evidence than mock-real divergence alone.
* `n=1` is preliminary and cannot prove general stochastic stability.
* Recommendations are rule-based and evidence-backed, not LLM-generated.

## Optional Stronger Confidence Rerun

For top actionable cases, rerun with `n>=3` before making stronger claims:

```bash
python3 cli.py test --input-file cases/llm_core/agent_memory/conflicting_memory.txt --models mock,deepseek:flash --n 3 --report --output reports/rerun_conflicting_memory_n3
```

Approximate real API calls:

```text
one case x one real provider x n=3 x DHMS A/B/C ~= 9 calls
```

This rerun is optional. Do not run it by default in CI or public demo smoke checks.

## Cost Warning

Real API calls scale roughly as `3 * n * provider_count * case_count`.

## Not Agent Harness

This package tests LLM behavior under controlled prompt/memory/context perturbation. It is not yet a real tool-executing Agent Harness.
