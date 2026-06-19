# DHMS Product Diagnosis v1.3: LLM Memory Stability Tester

DHMS helps developers test whether an LLM or agent remains stable when memory or context conditions are perturbed.

## Who Should Use It

Use DHMS if you build AI agents, RAG apps, memory-enabled assistants, workflow copilots, or LLM systems where context drift can affect user-facing behavior.

## 5-Minute Quickstart

1. Run a local mock demo:

```bash
python3 cli.py test --input "Does this agent stay consistent?" --models mock --n 3 --report
```

2. Open the HTML report:

```bash
open reports/latest/dhms_product_report.html
```

3. Try a packaged example:

```bash
python3 cli.py test --input-file examples/agent_memory_case.txt --models mock --n 3 --report --output reports/demo_agent_memory
```

## Public Demo

Live verified:

* DeepSeek `deepseek:flash`

Adapter-ready / BYOK:

* OpenAI
* Anthropic / Claude
* Qwen / DashScope
* Kimi / Moonshot
* Gemini
* Mistral

DeepSeek live-verified demo, if `DEEPSEEK_API_KEY` is configured:

```bash
python3 cli.py test --input-file examples/agent_memory_case.txt --models mock,deepseek:flash --n 1 --report --output reports/public_demo_deepseek_flash
```

DeepSeek live-verified LLM Core suite demo, if `DEEPSEEK_API_KEY` is configured:

```bash
python3 cli.py test-suite --suite cases/llm_core --models mock,deepseek:flash --n 1 --report --output reports/public_demo_llm_core_deepseek
```

Mock-only fallback demo:

```bash
python3 cli.py test-suite --suite cases/llm_core --models mock --n 1 --report --output reports/public_demo_llm_core_mock
```

The demo is local-first and does not store API keys. Reports show whether a specific run used a real API or a fallback.

## Baseline vs Current Run

DeepSeek validation baseline means the previously generated smoke-test result under `validation/deepseek_smoke/outputs/`. It tells you whether the DeepSeek bridge has been validated before.

Current run means this specific product report. A mock-only run will show:

* Current run real API: No
* Current real API models: none
* Drift score: not_applicable_mock_only

A real DeepSeek run will show:

* Current run real API: Yes
* Current real API models: deepseek:flash
* Fallback used: true or false
* Drift score: the current run value

## Scores In Product Language

* Stability Score: how consistently the system behaves across repeated trials.
* Sensitivity Score: how much behavior shifts when memory/context is perturbed.
* Isolation Strength: how cleanly the observed shift remains tied to the controlled perturbation conditions.
* Drift Risk: product-level risk estimate derived from DHMS outputs and real API calibration when available.

These scores are product interpretations of existing DHMS metrics. DHMS metric semantics are not changed.

## Diagnosis Layer

DHMS Product Diagnosis v1.3 adds diagnosis-driven fields in addition to raw product scores. The diagnosis layer explains why a case is risky and separates:

* `mock_real_divergence`: real-provider output differs from the mock baseline. This is not automatically provider failure.
* `regime_behavior_drift`: behavior changes across DHMS-A/B/C regimes.
* `expected_property_violation`: the case's expected stability property appears violated.
* `style_or_format_drift`: wording, markdown, verbosity, or structure changed while core behavior may be preserved.

High drift is a debugging signal, not a final provider-failure label. Mock-real divergence means real provider output differs from the mock baseline. Expected-property violation is stronger evidence of behavioral failure than mock-real divergence alone.

`n=1` reports are preliminary. They are useful for smoke diagnosis and schema validation, but they cannot prove general stochastic stability. Recommendations are rule-based and evidence-backed, not LLM-generated.

Recommendations name an action, reason, evidence, priority, confidence, and affected layer such as `memory_policy`, `retrieval_policy`, `prompt_contract`, `output_schema`, `safety_policy`, `provider_config`, `test_design`, or `metric_integrity`.

## Optional Stronger Confidence Rerun

For top actionable cases, rerun with `n>=3` before making stronger stability claims:

```bash
python3 cli.py test --input-file cases/llm_core/agent_memory/conflicting_memory.txt --models mock,deepseek:flash --n 3 --report --output reports/rerun_conflicting_memory_n3
```

Approximate real API calls:

```text
one case x one real provider x n=3 x DHMS A/B/C ~= 9 calls
```

This rerun is optional and should only be used when the real provider key is intentionally configured.

## Failure Modes Shown In Reports

Reports are designed to expose:

* missing API key
* fallback used
* timeout
* rate limit
* response format mismatch
* adapter routing issue

## Mock Mode

Mock mode is deterministic and does not require API keys. It is useful for local demos, CI checks, and report-generation validation.

```bash
python3 cli.py test --input "demo" --models mock --n 3 --report
```

## Real API Mode

Real API mode uses the existing V2.5 bridge when the requested model and API key are available. The Product Layer does not override V2 metrics with real API metrics.

```bash
python3 cli.py test --input "demo" --models mock,deepseek:flash --n 1 --report
```

## Safety Note

DHMS measures behavioral stability under controlled perturbation. It does not prove causal internal memory mechanisms.

## Roadmap

* CLI
* SDK
* API
* Dashboard

## Provider Expansion

DHMS supports provider:model syntax so users can test specific model families, not only providers.

```bash
python3 cli.py test --input-file examples/agent_memory_case.txt --models mock,deepseek:flash --n 1 --report
python3 cli.py test --input-file examples/agent_memory_case.txt --models mock,deepseek:pro --n 1 --report
python3 cli.py test --input-file examples/agent_memory_case.txt --models mock,openai:gpt-5.5 --n 1 --report
python3 cli.py test --input-file examples/agent_memory_case.txt --models mock,anthropic:sonnet --n 1 --report
python3 cli.py test --input-file examples/agent_memory_case.txt --models mock,qwen:plus --n 1 --report
python3 cli.py test --input-file examples/agent_memory_case.txt --models mock,kimi:k2 --n 1 --report
python3 cli.py test --input-file examples/agent_memory_case.txt --models mock,gemini:flash --n 1 --report
python3 cli.py test --input-file examples/agent_memory_case.txt --models mock,mistral:small --n 1 --report
```

### Supported Providers

| Provider | Aliases | Example | Key env var |
|---|---|---|---|
| deepseek | deepseek | `deepseek:flash` | `DEEPSEEK_API_KEY` |
| openai | openai | `openai:gpt-5.5` | `OPENAI_API_KEY` |
| anthropic | claude | `anthropic:sonnet` | `ANTHROPIC_API_KEY` |
| qwen | dashscope | `qwen:plus` | `DASHSCOPE_API_KEY` |
| kimi | moonshot | `kimi:k2` | `KIMI_API_KEY` or `MOONSHOT_API_KEY` |
| gemini | gemini | `gemini:flash` | `GEMINI_API_KEY` |
| mistral | mistral | `mistral:small` | `MISTRAL_API_KEY` |

### Model Alias Resolution

Explicit `provider:model` wins over env vars. For aliases, provider-specific env vars can override configured defaults, for example `DEEPSEEK_FLASH_MODEL`, `ANTHROPIC_SONNET_MODEL`, `QWEN_PLUS_MODEL`, `GEMINI_FLASH_MODEL`, or `MISTRAL_SMALL_MODEL`.

Direct model ID passthrough is allowed. For example, `openai:gpt-5.5` asks OpenAI for `gpt-5.5` directly.

Missing keys produce skipped or unavailable provider status, not real validation. Fallback/unavailable status is shown in reports and is not counted as successful real API behavior.

### Cost Warning

Real calls scale roughly as:

```text
3 * n * provider_count * case_count
```

Use `n=1` for live provider smoke tests and demos.

## LLM Core Suite Demo

Run the bundled LLM case library:

```bash
python3 cli.py test-suite --suite cases/llm_core --models mock --n 1 --report --output reports/llm_core_mock_smoke
```

DeepSeek live-verified suite demo, if `DEEPSEEK_API_KEY` is configured:

```bash
python3 cli.py test-suite --suite cases/llm_core --models mock,deepseek:flash --n 1 --report --output reports/public_demo_llm_core_deepseek
```

## Doctor / Provider Status

```bash
python3 cli.py doctor
python3 cli.py providers
python3 cli.py providers models
python3 cli.py providers models deepseek
```

## More Documentation

Detailed taxonomy and caveats are documented in `docs/diagnosis_layer_v1_3.md`.
Human-readable interpretation examples are documented in `docs/top_critical_case_explanations.md`.
