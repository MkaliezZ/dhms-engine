# DHMS / AgentFuse 中文概览

DHMS / AgentFuse 是 AI agent 工具执行前的政策与授权边界。它验证某次具体
动作是否符合接入产品提供的可信政策与审批上下文，并返回结构化的 allow 或
block decision 及标准化证据。

当前身份：

```text
当前 Python 包：dhms-agentfuse 3.6.0
历史证据里程碑：v3.5.2
证据 Schema：agentfuse-evidence-schema-v0.1
```

当前公共 API：

```text
RuntimeGuardDecision
evaluate()
aevaluate()
invoke()
ainvoke()
```

`evaluate()` 和 `aevaluate()` 只做 decision，不接收 handler，也不执行物理
动作。`invoke()` 和 `ainvoke()` 复用同一公共 decision 路径，并且只有在
decision 允许后才可能调用传入的 handler。

## 责任边界

DHMS 不是危险动作分类器。DHMS 是执行前的政策与授权边界。

风险等级、需要多强的审批，以及业务和组织级安全规则，由接入 DHMS 的产品或
可信策略层决定。DHMS 验证的是：这次具体动作、审批、参数、身份、期限和可信
上下文是否符合已声明政策。

高风险动作在可信政策明确允许、且所有审批条件都满足时，可以得到 allow
decision。表面上无害的动作，如果超出已审批的身份、资源、项目、参数、期限或
政策范围，也可以被 block。

### 接入产品负责

* 可信 capability 和风险分类；
* 审批强度、审批 UI 与审批流程；
* 业务和组织级安全政策；
* physical dispatch；
* 物理执行、outcome 与恢复。

风险分类不能来自 LLM 参数、provider metadata、prompt 文本、command output
或 DHMS 推断。

### DHMS / AgentFuse 负责

* 确定性的政策与授权边界裁决；
* 动作、审批、参数、身份、期限和可信上下文的精确绑定；
* allow 或 block decision evidence；
* 对政策错误和畸形 decision 的 fail-closed 处理。

### DHMS / AgentFuse 不负责

* 动作的内在危险分类；
* 用户意图判断；
* 业务正确性；
* malware 检测；
* 物理执行；
* 对未包装执行路径的通用拦截。

```text
DHMS_IS_A_DANGER_CLASSIFIER=false
DHMS_IS_A_POLICY_AND_AUTHORIZATION_BOUNDARY=true
RISK_CLASSIFICATION_OWNER=INTEGRATING_APPLICATION
PHYSICAL_DISPATCH_OWNER=INTEGRATING_APPLICATION
```

## 当前 Runtime Guard

Runtime Guard 可以根据 allowlist、denylist、default action 和可选自定义 policy
评估 tool call。外部 runtime 拥有 dispatch 时，应调用：

```python
decision = guard.evaluate(tool_call)
```

异步 policy 使用：

```python
decision = await guard.aevaluate(tool_call)
```

完整契约见
[`DHMS AgentFuse Public Decision API 3.6.0`](docs/dhms_agentfuse_public_decision_api_v3_6_0.md)。

Runtime Guard 只控制经过自身 API 或显式 adapter 包装的 handler。直接调用、
其他进程、subprocess、monkey-patching、network traffic 和未包装路径不会被
自动拦截。它不是 process sandbox、network firewall、malware detector 或
通用 production-security 边界。

## 真实 Consumer Integration：KerniQ

[KerniQ](https://github.com/MkaliezZ/qodex) v0.6.0 是 AgentFuse 3.6.0
decision-only 公共 API 的外部 consumer。KerniQ 已合并的
[PR #6](https://github.com/MkaliezZ/qodex/pull/6) 固定使用 AgentFuse source
commit
[`ec4b5842339dccfba0db62df7541920759203bc9`](https://github.com/MkaliezZ/dhms-engine/commit/ec4b5842339dccfba0db62df7541920759203bc9)，
并调用 `RuntimeGuard.evaluate(tool_call)`。

KerniQ 负责：

* 可信风险分类；
* approval；
* durable `ACTION_DECIDED` persistence；
* dispatch 与 `ACTION_STARTED`；
* 物理执行和 settlement；
* restart recovery。

DHMS 负责政策边界裁决和标准化 decision evidence，不拥有 KerniQ 的物理
handler。

已验证的边界包括：

* allow decision 在 dispatch 前独立持久化；
* deny 的 handler invocation 为 0；
* 畸形或过期 identity fail closed；
* settlement persistence 不确定时状态为 `Interrupted`；
* interrupted action 不会自动 replay；
* 安装后的 AgentFuse source 被篡改时 fail closed；
* 可变 installation metadata 不能为被篡改 source 背书。

当前 KerniQ integration 只覆盖一个受限 proof action。Project Command、Patch、
Git、file-write、shell、MCP、browser、Office、provider 和其他 production
action path 尚未声明受 AgentFuse 保护。该集成不证明“AgentFuse 保护 KerniQ
全部动作”，也不证明 KerniQ 已达到通用 production security。

稳定引用：

* [KerniQ repository](https://github.com/MkaliezZ/qodex)
* [KerniQ v0.6.0 merge commit](https://github.com/MkaliezZ/qodex/commit/3d333a30e4507e796aa97ddc0142606ad2e42587)
* [AgentFuse 3.6.0 public decision API](docs/dhms_agentfuse_public_decision_api_v3_6_0.md)

## 历史证据链

历史证据仍然有效，但不再代表当前公共 API 的全部能力：

* v3.4.2：冻结的 multi-tool selective interception result review，是多工具
  拦截证据基础；
* v3.5.2：real `langgraph_bigtool.create_agent()` API wiring demo，是历史
  external-project wiring 入口。

v3.5.2 demo 在真实 `langgraph_bigtool.create_agent()` API 边界前构建
guarded tool registry，并使用确定性的 tool retrieval。它不 compile、invoke
或 stream graph，不调用 provider、network、database、SQL、credential 或
用户数据，也不授权受保护 payload 执行。

历史证据值保持：

```text
protected_payload_body_execution_count = 0
runtime_behaviors_added = 0
execution_authorized_count = 0
```

## 如何运行

安装当前本地包并运行 Runtime Guard demo：

```bash
pip install -e .
python examples/runtime_guard/runtime_guard_mvp_demo.py
python examples/runtime_guard/langgraph_runtime_guard_demo.py
```

运行历史 v3.5.2 wiring demo：

```bash
python examples/external_integrations/langgraph_bigtool/dhms_guarded_tool_registry_demo.py
```

如果系统默认 `python` 版本低于 3.10，可以使用 Python 3.11：

```bash
/usr/local/bin/python3.11 -m pip install -e .
/usr/local/bin/python3.11 examples/runtime_guard/runtime_guard_mvp_demo.py
```

## 适合谁反馈

欢迎正在设计 agent tool 政策、授权、审批、dispatch 和证据边界的开发者反馈。
重点包括：公共 decision-only API 是否清楚、责任边界是否准确、保守 non-claims
是否充分，以及受限 consumer integration 是否容易复现。
