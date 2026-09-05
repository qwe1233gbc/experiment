# 预注册假设 v1.0

> 冻结日期：2026-09-01
> 版本：v1.0（Pilot 前冻结）
> 状态：PREREGISTERED

---

## 核心科学问题

> **在知识密集型环境专业审核中，外部知识增强的效用如何受到模型能力、知识来源与任务知识—推理需求的共同调节？**

---

## 主假设（H1-H4）

### H1：Knowledge Effect（知识效应）

> **领域 RAG（K3）相对于无外部知识（K1）总体提高环境专业审核表现，尤其在 E1 任务中。**

- **检验方式**：知识来源主效应（K3 vs K1），Knowledge × E 交互
- **方向性预期**：K3 > K1，且 E1 类提升幅度大于 E0 类
- **文献依据**：RAG 领域共识（Lewis et al., 2020）+ 环境领域 Zhou et al. (2026) 直接证据 + NEPAQuAD (Meyur et al., 2025)
- **支持强度**：Strong
- **结果指标**：Final Correctness（二元）

### H2：Model Effect（模型效应）

> **经独立校准后，基础能力更高的模型具有更高的审核基线表现。**

- **检验方式**：模型能力主效应（A3 vs A1）
- **方向性预期**：A3 > A2 > A1
- **文献依据**：LLM scaling law 共识
- **支持强度**：Strong
- **操纵检查**：必须通过模型能力操纵检查（独立校准集，K1 条件下验证梯度）
- **结果指标**：Final Correctness（二元），K1 条件下的基线表现

### H3：Model × Knowledge Interaction（模型-知识交互）

> **外部知识的效应因模型基础能力而异。**

- **检验方式**：Model × Knowledge 交互效应（混合效应逻辑回归）
- **这是整篇论文最重要的假设。**
- **不预设严格的 A1增益 > A2 > A3 单调递减**，只检验交互是否存在、形态是什么。
- **文献依据**：
  - 支持递减方向：RAG in the Wild (Xu et al., 2026)、To Memorize or to Retrieve (Singh et al., 2026)、Less LLM More Documents (Ning et al., 2025)
  - 反证/边界：Can Small Language Models Use What They Retrieve? (Pandey, 2026) — 7B 以下模型可能有利用瓶颈
- **支持强度**：Medium-Strong（通用领域有充分证据，环评领域待检验）
- **形态探索**：递减 / 平台 / 倒 U 型，见 EQ1

### H4：Task Boundary（任务边界效应）

> **外部知识效应因任务的外部知识依赖度和推理复杂度而异。**

- **检验方式**：
  - Knowledge × E 交互（知识依赖度的调节作用）
  - Knowledge × P 交互（推理复杂度的调节作用）
- **方向性预期**：
  - Knowledge × E：E1 类知识增益 > E0 类（知识依赖越高，RAG 增益越大）
  - Knowledge × P：方向不确定——P1 类既可能更需要知识，也可能因多跳/干扰导致收益下降
- **文献依据**：任务异质性共识 + Li & Ouyang (2025) 指出任务复杂度影响知识选择
- **支持强度**：Medium

---

## 探索性问题（EQ）

> 以下问题没有足够的文献基础给出方向性预判，将在实验结果中做数据驱动的探索分析。不作为预注册假设。

### EQ1：交互形态

> **Model × Knowledge 的形态是递减、平台还是倒 U 型？**

- 探索内容：
  - 增益曲线：A1增益 vs A2增益 vs A3增益
  - 是否存在"利用瓶颈"：A1 增益是否反而低于 A2（弱模型不会用知识）
  - 是否存在"天花板"：A3 在 E0 类上增益是否接近零
- 分析方法：简单效应分析 + 增益幅度比较
- 注意：Pilot 样本量小，不做结论性判断，仅观察趋势

### EQ2：错误模式与知识利用

> **不同知识来源如何改变错误类型、证据忠实度和知识利用方式？**

- 探索内容：
  - 错误类型迁移：K1 主要是什么错误？K2/K3 后错误类型如何变化？
  - 证据忠实度：K2 vs K3 的证据引用准确率差异
  - 幻觉模式：不同知识条件下幻觉的类型和频率
  - 知识利用方式：不同模型是否"用"了不同的检索内容
- 分析方法：错误类型标注 + 过程指标比较
- 注意：探索性，不预注册方向

---

## Planned Contrasts（预先指定的对比）

### Knowledge Contrasts
- K3 vs K1（领域 RAG vs 无知识）——主对比
- K2 vs K1（搜索 vs 无知识）——次对比
- K3 vs K2（领域 RAG vs 搜索）——知识来源差异

### Model Contrasts
- A3 vs A1（强 vs 弱）——主对比
- A2 vs A1（中 vs 弱）
- A3 vs A2（强 vs 中）

### Strong-model Knowledge Effect
- A3: K3 vs K1（强模型上领域 RAG 是否仍有效）——H5 的检验，检验不可替代性

### EP Stratified Contrasts
- Knowledge effect within E0（E0 类内的知识效应）
- Knowledge effect within E1（E1 类内的知识效应）
- Knowledge effect within P0（P0 类内的知识效应）
- Knowledge effect within P1（P1 类内的知识效应）

---

## Primary Outcome

> **Final Correctness**

- 二元变量：1 = CORRECT, 0 = INCORRECT
- 评分方式：自动结构化评分 + 人工抽样核验
- INSUFFICIENT 处理：归入 INCORRECT（预先规定）

---

## Primary Test

> **Model × Knowledge 交互效应**

这是整篇论文最核心的统计检验。

不是"K3 是否最高"。

---

## 冻结声明

本假设体系于 Pilot 实验前冻结。Pilot 实验仅用于检验操纵有效性和估计效应大小，不用于修改假设方向。

正式实验前，根据 Pilot 结果可能调整的内容：
- ✅ 样本量（效力分析后决定 40/60/80 题）
- ✅ 模型条件命名（如果操纵检查发现梯度不成立）
- ✅ 高阶交互项取舍（根据 Pilot 数据的方差结构）

❌ 不得修改核心假设方向
❌ 不得为了得到显著结果而调整 Gold 或题目
