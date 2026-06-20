# OpenClaw Wrapper Template Validation

- Status: PASS
- Branch: agent-harness-v1
- Wrapper: examples/agents/openclaw_deepseek_v4_wrapper.py
- Docs: docs/openclaw_deepseek_v4_wrapper.md
- Py compile: PASS
- Missing-command stdin test: PASS
- Missing-command conformance status: FAIL
- Preflight stdin test: PASS
- Missing target rejection: PASS
- Unsafe command rejection: PASS
- Forbidden --to rejection: PASS
- Missing profile rejection: PASS
- Preflight conformance status: PASS
- Sample conformance: PASS
- Preview tag unchanged: PASS
- Protected core layers unchanged: PASS
- Secret scan: PASS

## Safety

- Real OpenClaw was not run.
- DeepSeek API was not called.
- Real external tools were not executed.
- `OPENCLAW_DHMS_COMMAND` was intentionally unset during missing-command validation.
