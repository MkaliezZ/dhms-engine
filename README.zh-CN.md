# DHMS / AgentFuse 中文概览

当前 Python package：`dhms-agentfuse 3.7.2`。

当前 RuntimeGuard 公共 API：`RuntimeGuardDecision`、`evaluate()`、`aevaluate()`、`invoke()`、`ainvoke()`。新的 metadata-only integration API 位于 `dhms_agentfuse.integrations`：`IntegrationProfile`、`list_integrations()`、`get_integration()`。

v3.7.2 增加了 bounded、wheel-first 的 LangGraph compatibility matrix。CI 构建一个 `dhms-agentfuse 3.7.2` wheel，并在 Python 3.10/3.11 与 manifest 中列出的精确 LangGraph 版本组合上复用该 wheel，从仓库外运行 public-API probe。测试通过只证明这些精确组合，不代表 `langgraph>=1.2,<2.0` 整个依赖范围都兼容。v3.7.1 的 `langgraph 1.2.11` consumer trial、v3.7.0 的静态 integration profile，以及 v3.6.2 frozen conformance result（52 PASS、4 个有边界理由的 N/A、0 FAIL）保持不变。

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
- [KerniQ v0.6.1 freeze](https://github.com/MkaliezZ/qodex/commit/0486704d613ea203672d75bee455346cceafb225)
- [KerniQ v0.7 freeze](https://github.com/MkaliezZ/qodex/commit/2aa335dd21453ecf5d3ad44c2279b2c9362bef9f)
- [Hermes #53021 external proof](examples/external_integrations/hermes_53021/README.md)
- [Historical v3.5.2 wiring demo](docs/dhms_real_langgraph_bigtool_api_wiring_demo_v3_5_2.md)

## License

Apache License 2.0。详见 [LICENSE](LICENSE)。
