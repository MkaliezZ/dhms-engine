# DHMS v2 Cross-Model + Statistical Significance System

DHMS is organized as a strict layered system:

Spec -> Contract -> Binding -> Engine

The engine layer is executable, but it does not redefine DHMS memory, perturbation, regime, or metric semantics. Every run passes through the binding layer before execution.

## Structure

- `spec/`: DHMS Isolation Spec v1. Do not modify from the engine layer.
- `contract/`: DHMS Contract Layer v1. Do not modify from the engine layer.
- `binding/`: DHMS Engine Binding Layer v1. All runs must pass `bind_run()`.
- `engine/v0/`: minimal execution pipeline and JSON formatter.
- `engine/v1/`: measurement aggregation and repeated-trial orchestration.
- `engine/cross_model/`: model registry, routing, and aligned cross-model execution.
- `engine/statistics/`: significance, confidence, and model comparison helpers.
- `engine/v2_cross_model/`: v2 orchestration and CLI entry point.

## Run

Single-model measurement:

```bash
python3 cli.py run --mode B --input "text" --n 5
```

Cross-model measurement:

```bash
python3 cli.py run --mode B --input "text" --models mock,external
```

The CLI also accepts:

```bash
python3 cli.py dhms run --mode C --input "text" --n 3 --models mock,external
```

## Output

The JSON output includes:

- `per_run_results`
- `per_model_results`
- `aggregated_metrics`
- `cross_model_comparison`
- `statistical_significance_summary`
- `effect_size_report`
- `regime_consistency_report`

Metric names remain unchanged: `stability`, `sensitivity`, `specificity`, `isolation_strength`.

## Models

Supported model names:

- `mock`: deterministic local model.
- `external`: OpenAI / DeepSeek-compatible API path when `DHMS_ENABLE_EXTERNAL_API=1` and an API key are available; otherwise deterministic fallback.
- `fallback`: deterministic local fallback model.
