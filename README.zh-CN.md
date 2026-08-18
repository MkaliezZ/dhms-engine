# DHMS / AgentFuse 中文概览

当前 Python package：`dhms-agentfuse 3.7.3`。

**当前状态：Experimental Public Beta。**

AgentFuse 是面向有副作用 Agent 工具的 fail-closed pre-dispatch execution
boundary。只有 trusted policy boundary 明确返回 `allow`，受保护调用才可以
进入 handler。当前公开支持路径是 `RuntimeGuard`、显式 LangGraph `ToolNode`
integration，以及只读 integration metadata。

## 安装

当前没有宣称 PyPI 发布。请从 v3.7.3 GitHub tag 安装：

```bash
python -m pip install \
  "dhms-agentfuse @ git+https://github.com/MkaliezZ/dhms-engine.git@v3.7.3"
```

## 五分钟 Beta Trial

Canonical trial 不需要 LLM provider、API key 或 runtime external service：

```bash
git clone --branch v3.7.3 --depth 1 \
  https://github.com/MkaliezZ/dhms-engine.git agentfuse-beta
cd agentfuse-beta
python -m pip install -e . "langgraph==1.2.11"
python examples/integration_trial/five_minute_v3_7_1/run_trial.py
```

这个 bounded trial 验证 allow handler 恰好执行 1 次，block handler 执行 0
次。详细说明见
[v3.7.1 five-minute trial](docs/dhms_agentfuse_five_minute_integration_trial_v3_7_1.md)。

## Public Beta Integration Request

如果你维护 Agent runtime，或项目里有带副作用的工具，请提交
[Beta Integration Request](https://github.com/MkaliezZ/dhms-engine/issues/new?template=agentfuse-beta-integration.yml)，
只需提供 repository、runtime/framework 和一个 protected tool。该入口用于讨论
第一个 bounded integration，不承诺无限期的免费工程支持。

当前 RuntimeGuard 公共 API：`RuntimeGuardDecision`、`evaluate()`、`aevaluate()`、`invoke()`、`ainvoke()`。新的 metadata-only integration API 位于 `dhms_agentfuse.integrations`：`IntegrationProfile`、`list_integrations()`、`get_integration()`。

v3.7.3 没有新增 runtime capability。它冻结 v3.7.2 的 bounded、wheel-first
LangGraph compatibility evidence，并发布简洁的
[release seal](docs/dhms_agentfuse_integration_release_seal_v3_7_3.md)。精确测试组合是
Python 3.10 / LangGraph 1.2.11、Python 3.11 / LangGraph 1.2.0，以及 Python
3.11 / LangGraph 1.2.11。测试通过只证明这些精确组合，不代表
`langgraph>=1.2,<2.0` 整个依赖范围都兼容。

完整且最新的项目说明、责任边界、non-claims、KerniQ 证据引用与 external proof 请以英文主 README 为准：

[README.md](README.md)

AgentFuse 仍是 experimental pre-dispatch policy and authorization boundary。接入产品仍然负责自己的 action/approval identity、risk classification、durable lifecycle、physical execution 与 recovery；只有经过独立集成、审查和 proof 的路径可以作相应保护声明。

## 关键引用

- [AgentFuse Public Decision API 3.6.0](docs/dhms_agentfuse_public_decision_api_v3_6_0.md)
- [AgentFuse Consumer Integration Contract 3.6.1](docs/dhms_agentfuse_consumer_integration_contract_v3_6_1.md)
- [AgentFuse Cross-Adapter Conformance Kit 3.6.2](docs/dhms_agentfuse_cross_adapter_conformance_v3_6_2.md)
- [AgentFuse Integration Result Review and Freeze 3.6.3](docs/dhms_agentfuse_integration_result_review_and_freeze_v3_6_3.md)
- [AgentFuse Multi-Runtime Integration Package 3.7.0](docs/dhms_agentfuse_multi_runtime_integration_package_v3_7_0.md)
- [AgentFuse Five-Minute Integration Trial 3.7.1](docs/dhms_agentfuse_five_minute_integration_trial_v3_7_1.md)
- [AgentFuse Compatibility Matrix and CI 3.7.2](docs/dhms_agentfuse_compatibility_matrix_and_ci_v3_7_2.md)
- [AgentFuse Integration Release Seal 3.7.3](docs/dhms_agentfuse_integration_release_seal_v3_7_3.md)
- [KerniQ v0.6.1 freeze](https://github.com/MkaliezZ/qodex/commit/0486704d613ea203672d75bee455346cceafb225)
- [KerniQ v0.7 freeze](https://github.com/MkaliezZ/qodex/commit/2aa335dd21453ecf5d3ad44c2279b2c9362bef9f)
- [Hermes #53021 external proof](examples/external_integrations/hermes_53021/README.md)
- [Historical v3.5.2 wiring demo](docs/dhms_real_langgraph_bigtool_api_wiring_demo_v3_5_2.md)

## License

Apache License 2.0。详见 [LICENSE](LICENSE)。
