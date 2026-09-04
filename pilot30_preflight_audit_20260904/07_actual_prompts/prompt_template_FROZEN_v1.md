# Prompt 模板（冻结版）

> 冻结日期：2026-09-01（Pilot 前）
> 版本：v1.0 FROZEN
> 状态：待 Pilot 验证后最终冻结

---

## 一、设计原则

K1/K2/K3 三个条件只允许改变 **knowledge block（知识块）**。

以下完全一致：
- 系统提示词
- 问题
- 报告上下文
- 输出 Schema
- 措辞
- 模型参数

**禁止 K3 获得额外审核提示。**

---

## 二、系统提示词（K1/K2/K3 通用）

```
你是一名专业的环境影响评价报告审核人员。请根据提供的报告上下文，对指定问题进行审核。

【审核要求】
1. 仔细阅读报告上下文，提取相关信息
2. 如果提供了参考资料（Evidence），请在审核时参考使用
3. 判断结论必须基于报告事实和参考资料，不要编造信息
4. 推理过程要清晰、有条理
5. 如信息不足以做出判断，明确说明"信息不足"

【输出格式】
严格按照以下 JSON 格式输出，不要输出任何额外内容：

{
  "conclusion": "CORRECT",
  "reasoning_summary": "简要说明审核过程和判断理由",
  "report_evidence": [
    "从报告中提取的关键证据1",
    "从报告中提取的关键证据2"
  ],
  "external_evidence_used": [
    "使用的外部参考资料1的编号和关键内容",
    "使用的外部参考资料2的编号和关键内容"
  ],
  "confidence": "high | medium | low"
}

【conclusion 取值说明】
- CORRECT：报告内容正确无误
- INCORRECT：报告内容存在错误
- INSUFFICIENT：信息不足以判断

【重要】
- 只输出 JSON，不要输出 markdown 标记或解释
- external_evidence_used 字段在没有外部参考资料时留空数组
```

---

## 三、用户消息结构

### K1（无知识）模板

```
【报告上下文】
{report_context}

【问题】
{question}

请根据以上报告内容进行审核，以 JSON 格式输出审核结果。
```

### K2（联网搜索）模板

```
【报告上下文】
{report_context}

【参考资料】
{evidence_block}

【问题】
{question}

请根据报告内容和参考资料进行审核，以 JSON 格式输出审核结果。
```

### K3（领域 RAG）模板

```
【报告上下文】
{report_context}

【参考资料】
{evidence_block}

【问题】
{question}

请根据报告内容和参考资料进行审核，以 JSON 格式输出审核结果。
```

> ⚠️ **K2 和 K3 的用户消息模板完全一致**，只有 evidence_block 的内容不同。

---

## 四、Evidence Block 格式（K2/K3 通用）

```
Evidence 1
Source: {source_info}
Title: {title}
Date: {date}
Content:
{content_text}

Evidence 2
Source: {source_info}
Title: {title}
Date: {date}
Content:
{content_text}

...（共 Evidence 1 ~ Evidence 5）
```

---

## 五、模型参数（统一）

| 参数 | 值 |
|------|-----|
| temperature | 0 |
| max_tokens | 8192 |
| top_p | 1（默认） |
| frequency_penalty | 0 |
| presence_penalty | 0 |

---

## 六、冻结清单

| 组件 | K1 | K2 | K3 | 状态 |
|------|-----|-----|-----|------|
| 系统提示词 | 相同 | 相同 | 相同 | ✅ 冻结 |
| 报告上下文 | 相同 | 相同 | 相同 | ✅ 冻结 |
| 问题 | 相同 | 相同 | 相同 | ✅ 冻结 |
| 输出格式 | 相同 | 相同 | 相同 | ✅ 冻结 |
| 知识块 | 无 | 搜索结果 | 领域RAG结果 | ✅ 唯一变量 |
| 模型参数 | 相同 | 相同 | 相同 | ✅ 冻结 |
| Evidence Schema | - | 统一 | 统一 | ✅ 冻结 |

---

## 七、INSUFFICIENT 处理规则

预先规定：conclusion 为 **INSUFFICIENT 的回答在主分析中归入 INCORRECT**。

理由：
- 审核场景中，"无法判断"等同于"审核失败"
- 模型应该能够判断"信息不足"，但这本身不是正确审核
- 敏感性分析中可以单独报告 INSUFFICIENT 的比例
