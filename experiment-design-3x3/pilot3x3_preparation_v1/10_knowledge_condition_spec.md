# 知识来源条件规范 v1.0

> 冻结日期：2026-09-01（Pilot 前）
> 版本：v1.0
> 变量名：**Knowledge Condition**（或 **Knowledge Source Condition**）
> ⚠️ 禁止写成 "low / medium / high quality knowledge"

---

## 一、三个水平

### K1：No External Knowledge（无外部知识）

**定义**：模型只能看到问题和报告上下文，没有任何外部检索知识。

**输入构成**：
```
系统提示词
├─ 任务说明
└─ 输出格式要求

用户消息
├─ 报告上下文（Report Context）
└─ 问题（Question）
```

**作用**：基线条件，测量模型的内置参数知识能力。

---

### K2：Open-web Search（联网搜索）

**定义**：通过 Serper.dev API 检索互联网，取 Top-5 搜索结果作为外部知识。

**实现方式**：
- 搜索引擎：Serper.dev（Google 搜索结果 API）
- 检索数量：Top-5
- 检索查询：自动构造（以题目关键词 + "环评" + "标准" 等限定词）
- 结果格式：转换为统一 Evidence Schema（见下文）

**特点**：
- 开放式知识来源，覆盖面广
- 时效性强（能搜到最新信息）
- 质量参差不齐（可能有博客、论坛、非权威来源）
- 可能包含噪声和无关信息

**作用**：模拟"审核人员用搜索引擎查资料"的场景，代表通用外部知识。

---

### K3：Curated Domain RAG（领域 RAG）

**定义**：从 81 源环评专业知识库中检索，取 Top-5 作为外部知识。

**实现方式**：
- 知识库：81 源环评专业知识库（国家标准、行业标准、技术导则、地方标准等）
- 检索方式：BM25 + 稠密向量混合检索
- 检索数量：Top-5（父块）
- 结果格式：转换为统一 Evidence Schema（见下文）

**特点**：
- 权威性高（官方标准、导则）
- 结构化（标准卡片格式）
- 覆盖范围有限（只有入库的 81 个来源）
- 时效性取决于知识库更新频率

**作用**：模拟"审核人员查专业法规手册"的场景，代表权威领域知识。

---

## 二、统一 Evidence Schema

K2 和 K3 的检索结果必须转换为相同的结构。

```
Evidence [n]
Source: [来源名称/URL/标准编号]
Title: [标题/主题]
Date: [发布日期/更新日期，如无则标"未知"]
Content:
[证据正文内容]
```

共 Top-5 条，编号为 Evidence 1 ~ Evidence 5。

### 格式统一要求

| 要求 | K2 | K3 |
|------|-----|-----|
| Evidence 编号 | Evidence 1-5 | Evidence 1-5 |
| Source 字段 | 有（网页标题+URL） | 有（标准编号/标准名称） |
| Title 字段 | 有 | 有 |
| Date 字段 | 有（搜索结果日期，无则标"未知"） | 有（标准发布/实施日期） |
| Content 字段 | 有（搜索结果摘要） | 有（标准卡片内容） |
| 额外人工解释 | ❌ 禁止 | ❌ 禁止 |
| Gold 提示 | ❌ 禁止 | ❌ 禁止 |
| 元数据不对称 | 正常包含 URL | 包含标准编号作为元数据对等物 |

### 禁止事项

- ❌ K2 和 K3 使用不同的字段结构
- ❌ K3 额外带人工解释或审核指导
- ❌ K3 的证据中隐含 Gold 答案提示
- ❌ K2 有完整 URL 元数据而 K3 完全没有 source metadata（必须有对等物）

---

## 三、Token Budget 控制

### 为什么需要控制

K1 只有报告内容，K2/K3 额外增加了检索结果，输入长度不同。上下文长度是重要的混淆变量：
- 长上下文可能导致注意力稀释
- 长上下文本身可能改变模型的推理行为
- 如果 K2 和 K3 输入长度差异大，效果差异可能来自长度而非知识质量

### 控制措施

1. **尽量控制 Top-N 证据总 token 数接近**
   - 目标范围：K2/K3 evidence token budget 处于同一范围（如 2500-3500 tokens）
   - 具体范围根据 Pilot 检索结果分布确定

2. **记录并报告**
   - evidence_count（证据条数）
   - evidence_tokens（证据总 token 数）
   - total_input_tokens（总输入 token 数）

3. **分析中考虑**
   - 将 input tokens 作为协变量纳入敏感性分析
   - 报告 K2/K3 的 token 数差异

### 不做什么

- ❌ 不增加 K1 + 等长度无意义文本的 R0 对照组（会人为引入注意力干扰）
- ❌ 不为了等长而截断决定性法规条款（知识完整性优先）

---

## 四、知识操纵检查指标

每道 E1 题分别评价 K2 和 K3 的检索质量：

| 指标 | 定义 | 评价方式 |
|------|------|---------|
| **Answer-bearing Recall** | Top-5 中是否存在支持 Gold 的关键证据 | 人工标注：是/否/部分 |
| **Authoritative-source Rate** | 官方政府、国家/地方标准、正式规范的比例 | 人工统计：5条中权威来源有几条 |
| **Applicability Rate** | 证据真正适用于当前项目/行业/污染物/时点的比例 | 人工评价：适用/部分适用/不适用 |
| **Noise Rate** | Top-5 中无关或误导内容的比例 | 人工统计：5条中噪声有几条 |

### 注意事项

- **不要预设 K3 必然优于 K2**
- 某些题上 K2 可能更好（比如时效性强的问题）
- 操纵检查是为了解释结果，不是为了证明 K3 更好
- 如果 K2/K3 知识质量差异很小，那本身就是有效发现

---

## 五、命名规范

### 变量名

推荐使用：
- **Knowledge Condition**（知识来源条件）
- **Knowledge Source Condition**（知识来源条件）

### 三个水平

- K1 = No external knowledge / Baseline
- K2 = Open-web search / Web search
- K3 = Curated domain RAG / Domain RAG

### 禁止的表述

- ❌ "low quality / medium quality / high quality knowledge"
- ❌ "knowledge quality"（作为自变量等级）
- ❌ "K3 is better than K2"（实验前预设）

### 允许的表述

- ✅ "different knowledge source conditions"
- ✅ "knowledge quality"（作为操纵检查指标，不是自变量）
- ✅ "authoritative knowledge"（描述 K3 的属性，不是等级标签）
