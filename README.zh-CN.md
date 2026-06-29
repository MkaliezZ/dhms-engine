# DHMS / AgentFuse 中文概览

DHMS 是面向 AI agent 的执行熔断协议。AgentFuse 是围绕 DHMS 协议构建的证据线、示例、验证脚本和本地演示集合，用来展示 agent tool call 在进入真实副作用之前如何被观察、分类、拦截和 fail-closed。

DHMS / AgentFuse 不是 LangChain 的附庸。LangChain、LangGraph 和其他 agent 框架可以是 DHMS 的集成对象，但 DHMS 自身关注的是执行边界：一个 side-effect-capable agent tool 是否应该被释放、阻断、持有，或 fail closed，以及这个决定需要什么证据。

当前最新外部集成示例是 LangGraph / `langgraph-bigtool` 的真实 API wiring demo。示例位于：

```bash
examples/external_integrations/langgraph_bigtool/
```

这个 demo 使用真实的 `langgraph_bigtool.create_agent` API，把 DHMS guard 包装后的 tool registry 传入 `create_agent()`，并使用确定性的 tool retrieval 函数。它证明的是安全 wiring 和 pre-tool interception，不是完整 live production agent run。

DHMS 的目标是成为 side-effect-capable agent tools 的 automatic fail-closed execution fuse：安全只读候选可以成为 `RELEASE_CANDIDATE`，危险 SQL mutation 和 model API 请求会 `FAIL_CLOSED`，受保护的 payload body 不会执行。

当前边界：

* 不是 production runtime
* 不 compile / invoke / stream graph
* 不调用 provider 或真实模型 API
* 不发起 network 请求
* 不访问 DB
* 不执行 SQL
* 不读取环境变量、凭证或用户数据
* 不授权受保护 payload body 执行

本地 Quickstart：

```bash
/usr/local/bin/python3.11 -m pip install -e .
```

运行最新 demo：

```bash
/usr/local/bin/python3.11 examples/external_integrations/langgraph_bigtool/dhms_guarded_tool_registry_demo.py
```

预期结果：

```text
DHMS_REAL_LANGGRAPH_BIGTOOL_API_WIRING_DEMO_PASS
```
