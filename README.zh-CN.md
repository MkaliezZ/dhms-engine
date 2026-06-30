# DHMS / AgentFuse 中文概览

DHMS 是面向 AI agent 的执行熔断协议。AgentFuse 是围绕 DHMS 协议构建的证据线、示例、验证脚本和本地演示集合，用来展示 agent tool call 在进入真实副作用之前如何被观察、分类、拦截和 fail-closed。

DHMS / AgentFuse 不是 LangChain 的附庸。LangChain、LangGraph 和其他 agent 框架可以是 DHMS 的集成对象，但 DHMS 自身关注的是执行边界：一个 side-effect-capable agent tool 是否应该被释放、阻断、持有，或 fail closed，以及这个决定需要什么证据。

## 解决什么风险

越来越多 AI agent 会调用可能产生副作用的工具，例如 SQL、文件、API、代码、业务系统或模型调用。风险不只来自模型输出文本，也来自工具 payload 真正执行前的边界判断。

DHMS 的目标是成为 side-effect-capable AI agent tools 的 automatic fail-closed execution fuse：安全只读候选可以成为 `RELEASE_CANDIDATE`，危险 SQL mutation 和 model API 请求会 `FAIL_CLOSED`，受保护的 payload body 不会执行。

## v3.5.2 当前证明了什么

当前最新外部集成示例是 LangGraph / `langgraph-bigtool` 的真实 API wiring demo。示例位于：

```bash
examples/external_integrations/langgraph_bigtool/
```

DHMS 目前证明的是在真实 `langgraph_bigtool.create_agent()` API 边界前构建 guarded tool registry，并在已知风险工具进入受保护 payload 前 fail closed。这个 demo 使用真实的 `langgraph_bigtool.create_agent` API，把 DHMS guard 包装后的 tool registry 传入 `create_agent()`，并使用确定性的 tool retrieval 函数。

当前证据：

* `protected_payload_body_execution_count = 0`
* `runtime_behaviors_added = 0`
* `execution_authorized_count = 0`

这证明的是安全 wiring 和 pre-tool interception，不是完整 live production agent run。

## 当前没有证明什么

当前边界：

* 不是 production runtime
* 不 compile / invoke / stream graph
* 不调用 provider 或真实模型 API
* 不发起 network 请求
* 不访问 DB
* 不执行 SQL
* 不读取环境变量、凭证或用户数据
* 不授权受保护 payload body 执行
* 不声明 DHMS 是完成版 SDK、企业安全产品或 production security system
* 不声明 LangChain / LangGraph 缺少自己的安全机制

## 如何运行 demo

本地安装：

```bash
pip install -e .
```

运行最新 demo：

```bash
python examples/external_integrations/langgraph_bigtool/dhms_guarded_tool_registry_demo.py
```

预期结果：

```text
DHMS_REAL_LANGGRAPH_BIGTOOL_API_WIRING_DEMO_PASS
```

如果系统默认 `python` 版本过旧，可以使用 Python 3.11：

```bash
/usr/local/bin/python3.11 -m pip install -e .
/usr/local/bin/python3.11 examples/external_integrations/langgraph_bigtool/dhms_guarded_tool_registry_demo.py
```

## 适合谁反馈

欢迎这些方向的反馈：

* 正在设计 agent tool 安全边界的人
* 使用 LangChain、LangGraph 或其他 agent 框架的人
* 关心 SQL、文件、API、模型调用等 side-effect-capable tools 的人
* 想评估 fail-closed execution fuse 是否适合自己 agent 架构的人

反馈重点可以放在：guarded tool registry 是否容易理解、v3.5.2 demo 的边界是否清楚、non-claims 是否足够保守、以及哪些真实 agent tool 风险类别最值得优先覆盖。
