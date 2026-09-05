# 统计分析计划 v1.0

> 冻结日期：2026-09-01（Pilot 前）
> 版本：v1.0
> 状态：PREREGISTERED

---

## 一、分析框架

### 主要因变量

**Final Correctness**（二元）
- 1 = CORRECT
- 0 = INCORRECT / INSUFFICIENT（预先规定 INSUFFICIENT 归入 INCORRECT）

### 核心自变量

- **Model**（3 水平）：A1 / A2 / A3（经操纵检查验证的模型能力梯度）
- **Knowledge**（3 水平）：K1 / K2 / K3（知识来源条件）

### 调节变量

- **E**（2 水平）：E0 / E1（外部知识依赖度）
- **P**（2 水平）：P0 / P1（推理复杂度）

### 随机效应

- **Question**：题目随机截距（同一题在 9 个条件下重复，不独立）
- **Project**：报告/项目随机截距（如果多道题来自同一报告）

> 选择原则：如果题目完全嵌套在项目内（16题来自16个不同项目则无嵌套），用 `(1 | Question) + (1 | Project)`；如果每项目只有 1 题，Project 随机效应的方差可能估计为 0，此时可去掉。Pilot 后根据数据结构确定。

---

## 二、主分析模型

### 2.1 主模型（Model × Knowledge）

```
Correct ~ Model * Knowledge
        + (1 | Question)
        + (1 | Project)
```

**核心检验**：Model × Knowledge 交互效应（LRT 或 Wald 检验）

**如果交互效应显著**，进行简单效应分析：
- 各 Model 水平上的 Knowledge 效应（K3 vs K1, K2 vs K1, K3 vs K2）
- 各 Knowledge 水平上的 Model 效应

### 2.2 扩展模型（加入 E 和 P）

```
Correct ~ Model * Knowledge
        + E + P
        + Knowledge:E
        + Knowledge:P
        + (1 | Question)
        + (1 | Project)
```

**检验内容**：
- Knowledge × E 交互（H4a：知识依赖度调节知识效应）
- Knowledge × P 交互（H4b：推理复杂度调节知识效应）

> 高阶交互（如 Model × Knowledge × E）不预注册主分析。仅在样本量足够（≥60题）且有理论理由时作为探索性分析。

---

## 三、估计与推断方法

### 模型类型

- **主分析**：广义线性混合模型（GLMM），二项分布，logit 连接
- **连续过程指标**：线性混合模型（LMM），高斯分布

### 估计方法

- 最大似然估计（ML）用于模型比较
- 限制性最大似然估计（REML）用于最终参数估计
- 工具：R 包 lme4 / glmmTMB，或 Python 的 statsmodels / pymer4

### 推断方法

- 固定效应：Wald 检验 + 95% CI
- 模型比较：似然比检验（LRT）
- 事后对比：emmeans（或等价工具），Tukey 多重比较校正
- 效应量报告：
  - 主要效应：OR（比值比）+ 95% CI
  - 组间差异：风险差（Risk Difference）+ 95% CI
  - 不只用 p 值，重点报告效应大小

---

## 四、Planned Contrasts

### Knowledge Contrasts
- K3 vs K1 — 主对比（领域 RAG 是否有效）
- K2 vs K1 — 次对比（搜索是否有效）
- K3 vs K2 — 知识来源差异

### Model Contrasts
- A3 vs A1 — 主对比（强 vs 弱）
- A2 vs A1
- A3 vs A2

### Key Simple Effects
- A3: K3 vs K1 — 强模型上领域 RAG 效应（检验不可替代性，H5）
- A1: K3 vs K1 — 弱模型上领域 RAG 效应

### EP Stratified
- Knowledge effect within E0
- Knowledge effect within E1
- Knowledge effect within P0
- Knowledge effect within P1

---

## 五、次要分析

### 5.1 过程指标分析

按 EP 分类分别分析过程指标：
- E0P0：章节定位准确率、数据提取准确率
- E1P0：标准引用准确率、数值准确率
- E0P1：参数提取准确率、公式正确率、计算结果准确率
- E1P1：场景识别准确率、知识引用准确率、推理完整性、最终判断准确率

分析方法：二元指标用 GLMM，连续指标用 LMM。

### 5.2 错误类型分析

- 假阳性率 vs 假阴性率（按条件比较）
- 错误环节分布（提取错误 / 计算错误 / 知识错误 / 推理错误 / 方法错误）
- 幻觉类型分析（编造标准 / 编造数据 / 编造章节）

### 5.3 知识操纵检查分析

- K2/K3 的 answer-bearing recall 对比
- K2/K3 的 authoritative-source rate 对比
- 知识质量指标与正确率的相关性
- 知识质量是否中介了 Knowledge condition 的效应

### 5.4 敏感性分析

- 是否纳入 INSUFFICIENT（主分析归入 INCORRECT，敏感性分析中排除或单独报告）
- 控制 input tokens 作为协变量
- 排除极端题目（正确率异常高或低的题）
- 不同随机效应结构的模型比较

---

## 六、Pilot 分析的边界

Pilot 16 题**只回答以下问题**：

1. 模型梯度是否成立？（操纵检查）
2. K2/K3 操纵是否真实不同？（知识操纵检查）
3. E/P 是否能稳定分类？（标签一致性）
4. Gold 是否可靠？（确定性检查）
5. 是否有 ceiling/floor 效应？
6. Scoring 能否运行？
7. API 成本/延迟？
8. GLMM 脚本是否可运行？

**Pilot 不能用来**：
- ❌ 正式检验 H1-H4
- ❌ 宣称发现知识替代效应
- ❌ 用单个 Pilot 效应量直接写论文结论
- ❌ 调整假设方向

---

## 七、效力分析计划

### 时机

Pilot 完成后，基于 Pilot 数据做 **simulation-based power analysis**。

### 输入参数（从 Pilot 估计）

- plausible baseline range（基线正确率范围）
- plausible OR（知识效应和模型效应的比值比）
- ICC（组内相关系数）
- question/project variance（随机效应方差）

### 模拟条件

- 40 题
- 60 题
- 80 题

### 目标效力

> **Power ≥ 0.80**（针对 Model × Knowledge 交互效应）

### 决策规则

| 效力结果 | 正式实验题量 | 调整策略 |
|---------|-------------|---------|
| 60 题 power ≥ 0.80 | 60 题 | 正常进行 |
| 80 题 power ≥ 0.80 | 80 题 | 扩充题目 |
| 40 题 power ≥ 0.80 | 40 题 | 最少可行样本量 |
| 80 题 power < 0.80 | 重新设计 | 缩减模型：保留 Model, Knowledge, Model×Knowledge, E；弱化 P 和高阶分层 |

---

## 八、Pilot 后可能的调整

### ✅ 允许调整的内容

- 样本量（根据效力分析）
- 模型条件命名（如果操纵检查发现梯度不成立）
- 随机效应结构（根据数据结构）
- 高阶交互项取舍（根据 Pilot 方差结构）
- 过程指标的具体定义（如果某些指标不可靠）

### ❌ 不允许调整的内容

- 核心科学问题
- H1-H4 的方向
- 自变量的基本定义（3 个模型、3 个知识条件）
- 主要因变量（Final Correctness）
- 核心检验（Model × Knowledge 交互）
- Gold 答案和题目选择（为了让结果"好看"而换题）
