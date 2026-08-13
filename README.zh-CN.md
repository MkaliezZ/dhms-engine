# DHMS / AgentFuse 中文概览

当前 Python package：`dhms-agentfuse 3.6.0`。

当前公共 API：`RuntimeGuardDecision`、`evaluate()`、`aevaluate()`、`invoke()`、`ainvoke()`。

当前真实 consumer 状态：KerniQ 已完成并冻结两条独立 bounded integration：v0.6.1 Project Command 与 v0.7 Coding Pack Export。最新 external proof 为 Hermes #53021 的受限 session policy proof。历史 evidence milestone `v3.5.2` 仍保留，但不代表当前 package version。

完整且最新的项目说明、责任边界、non-claims、KerniQ 证据引用与 external proof 请以英文主 README 为准：

[README.md](README.md)

AgentFuse 仍是 experimental pre-dispatch policy and authorization boundary。接入产品仍然负责自己的 action/approval identity、risk classification、durable lifecycle、physical execution 与 recovery；只有经过独立集成、审查和 proof 的路径可以作相应保护声明。

## 关键引用

- [AgentFuse Public Decision API 3.6.0](docs/dhms_agentfuse_public_decision_api_v3_6_0.md)
- [KerniQ v0.6.1 freeze](https://github.com/MkaliezZ/qodex/commit/0486704d613ea203672d75bee455346cceafb225)
- [KerniQ v0.7 freeze](https://github.com/MkaliezZ/qodex/commit/2aa335dd21453ecf5d3ad44c2279b2c9362bef9f)
- [Hermes #53021 external proof](examples/external_integrations/hermes_53021/README.md)
- [Historical v3.5.2 wiring demo](docs/dhms_real_langgraph_bigtool_api_wiring_demo_v3_5_2.md)

## License

Apache License 2.0。详见 [LICENSE](LICENSE)。
