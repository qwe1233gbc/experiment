# SEARCH_PLAN - 3×3 实验文献充分性审计

> 生成日期：2026-09-01
> 研究问题：外部知识对 LLM 环评专业审核能力的增益，是否因模型能力、知识来源质量、任务类型不同而变化？

## 0. 已有资产盘点

### 本地已有
- 130 篇文献证据矩阵（旧 2×2 口径）
- RAG 证据包：57 篇
- 环境领域 LLM 证据包：37 篇
- 反面证据包：已初步整理
- 文献综述大纲：旧版（Skill+RAG 口径）

### 已有文献中可用的
- **L1（环境专业性）**：16 篇环境领域 LLM 研究 → 基本充足
- **L2（RAG 基础价值）**：46 篇 RAG 相关 → 充足
- **L6（环境领域 RAG 有价值）**：有 Zhou et al. 2026 (JEM) 等 → 基本有

### 需要重点补充的
- **L3（模型能力 × RAG 交互）**：几乎空白，只有 2 篇不相关的 → **最高优先级**
- **L4（任务复杂度 × RAG）**：有一些但不够系统 → **高优先级**
- **L5（知识来源/质量）**：有 RAG in the Wild 等，但不够 → **中优先级**
- **L7（E×P 框架基础）**：需要分别找 E 和 P 的理论依据 → **中优先级**
- **反面证据**：需要主动找 RAG 失败、强模型不需要 RAG 等文献 → **中优先级**

---

## 1. 检索维度与优先级

### P0：必须核查的核心论文（最高优先级）

| 编号 | 论文 | 验证什么 | 对应 L |
|------|------|---------|-------|
| 1 | Lewis et al. 2020, RAG for Knowledge-Intensive NLP Tasks | RAG 基础 | L2 |
| 2 | Li & Ouyang 2025, How Does Knowledge Selection Help RAG? (EMNLP Findings) | 模型能力×知识选择 | L3, L4, L5 |
| 3 | Xu et al. 2026, RAG in the Wild (ACL Findings) | 混合知识来源×模型大小 | L3, L5 |
| 4 | NEPAQuAD / PNNL 环境审查基准 | 环境领域 LLM 基准 | L1, L6 |
| 5 | Zhou et al. 2026, Integrating fine-tuning and RAG for pollution control guidelines (JEM) | 环境领域 RAG | L6 |

### P1：L3 模型能力 × RAG（重点补充）

检索关键词：
- "retrieval augmented generation model size"
- "RAG weaker models benefit more"
- "generator capability knowledge selection"
- "model scale RAG performance"
- "small vs large language models retrieval augmentation"

预期找到：
- 不同模型大小下 RAG 增益的比较研究
- 知识替代效应的直接/间接证据
- 强模型是否也需要 RAG 的证据

### P2：L4 任务异质性 × RAG

检索关键词：
- "RAG task complexity"
- "retrieval augmentation reasoning tasks"
- "multi-hop RAG benchmark"
- "knowledge intensive task RAG"
- "task dependent retrieval benefit"

预期找到：
- 不同任务类型 RAG 收益不同的证据
- 任务分类维度（推理复杂度、知识依赖度）
- 能否支撑 E×P 框架

### P3：L5 知识来源/质量

检索关键词：
- "retrieval source quality RAG"
- "noisy retrieval RAG"
- "domain-specific vs general knowledge RAG"
- "web search RAG vs curated corpus"
- "imperfect retrieval language models"

预期找到：
- 知识质量影响 RAG 效果的证据
- 不同知识来源对比的研究
- K2/K3 作为不同知识供给机制的合理性

### P4：L7 E×P 框架理论基础

分别检索：
- E 维度："closed-book vs open-book QA", "knowledge-intensive NLP tasks", "external knowledge dependency"
- P 维度："multi-hop reasoning RAG", "reasoning complexity NLP", "compositional retrieval"

### P5：反面证据

检索关键词：
- "RAG fails strong models"
- "retrieval hurts performance"
- "long context vs RAG"
- "distractor knowledge RAG"
- "retrieval no benefit large models"

---

## 2. 执行顺序

1. **P0 核心论文核查**：先验证 5 篇核心论文的关键结论（最优先）
2. **L3 + L5 并行检索**：模型能力×知识来源（理论核心）
3. **L4 + L7 并行检索**：任务异质性 + EP框架
4. **L1 + L6 盘点**：环境领域（已有较多，只需补新的）
5. **反面证据检索**：确保不片面
6. **假设检查 + Gap 分析**：综合判断
7. **生成交付物**

---

## 3. 文献等级标准

- **A 级（直接证据）**：做了与 claim 非常接近的实验（如比较不同模型下 RAG 增益）
- **B 级（间接证据）**：没直接做，但结果可以合理支持
- **C 级（背景证据）**：只说明研究场景重要
- **D 级（不能用）**：标题党、博客、无关

---

## 4. 输出文件清单

```
literature_support_audit_3x3/
├── 01_scientific_question_evidence_map.xlsx
├── 02_core_paper_cards.xlsx
├── 03_hypothesis_support_audit.xlsx
├── 04_contradictory_evidence.xlsx
├── 05_research_gap_audit.md
├── 06_EP_framework_evidence.md
├── 07_missing_literature_search_log.xlsx
├── 08_recommended_core_literature.md
└── README.md
```
