# DHMS DeepSeek Smoke Validation

This folder contains a bounded smoke test for the DHMS V2.5 Real API Bridge Layer.

Run from the project root:

```bash
python3 validation/deepseek_smoke/run_deepseek_smoke.py --n 1 --models mock,deepseek --max-real-api-calls 9
```

The script never prints or stores API keys. It reports only whether `DEEPSEEK_API_KEY` is present.

Outputs are written to `validation/deepseek_smoke/outputs/`.
