# 3×3 实验文献充分性审计报告

> 审计日期：2026-09-01
> 研究问题：外部知识对 LLM 环评专业审核能力的增益，是否因模型能力、知识来源质量、任务类型不同而变化？

## 🟡 YELLOW（修正表述后可以做）

**总体判断**：大方向成立，核心理论基础充分，但部分假设证据不足，需要调整表述。

### 为什么是 YELLOW 不是 GREEN

1. **H4（强模型对知识质量更敏感）**缺乏直接证据，应降级为探索性问题
2. **H6（E1P0 > E1P1 > E0P1 > E0P0 死排序）**没有文献支持，应改成更宽泛的表述
3. **E×P 框架**是本文提出的操作性分类，不是成熟理论，需要如实说明
4. 小模型端可能存在"检索利用瓶颈"（7B以下模型可能不会有效利用检索结果），可能影响 H3 的单调性

### 为什么不是 RED

1. 研究问题有价值：环境领域 Model × Knowledge × Task 三维交互是空白的
2. 核心理论基础扎实：RAG 价值、知识替代效应、任务异质性都有文献支撑
3. 方法合理：3×3 析因设计是标准的多因素研究方法
4. 环境领域有充分证据说明专业性和研究必要性

---

## 1. 我现在到底研究什么？

研究**外部知识、模型能力、任务类型**三者如何交互影响 LLM 环评审核表现。具体来说：
- RAG 在环评审核中有用吗？
- 不同能力的模型，从 RAG 中获益一样吗？
- 不同质量的知识来源（无知识/搜索/领域RAG），效果差多少？
- 什么类型的审核题 RAG 帮助最大？

## 2. 为什么这个问题值得研究？

- **理论意义**：检验通用领域发现的知识替代效应是否适用于专业法规领域
- **实践意义**：为环评 AI 系统选型（用什么模型、配什么知识）提供实证依据
- **领域价值**：环评审核专业性强、错误后果严重，AI 辅助有迫切需求但研究不足

## 3. 已经有哪些人做过类似研究？

- **通用 RAG 领域**：Lewis et al. (2020) 奠基；RAG in the Wild (2026)、Li & Ouyang (2025) 等研究了模型能力和知识质量的交互
- **环境领域**：NEPAQuAD (PNNL 2025) 是首个环境审查 LLM 基准；Zhou et al. (2026, JEM) 做了污染控制指南 RAG
- **任务异质性**：多跳推理 RAG、领域 RAG 等研究都涉及任务差异，但没有统一的分类框架

## 4. 他们做到哪里了？

- 通用领域：已经知道"小模型从 RAG 获益更多"，也知道"知识质量很重要"
- 环境领域：知道"LLM 可以辅助环评"，也知道"RAG 在环境领域有价值"
- 但没有人：在专业法规领域，系统研究 Model × Knowledge × Task 的三维交互

## 5. 哪一部分还没人回答清楚？

- 专业法规领域的知识替代效应是什么形态？（强模型还需要 RAG 吗？）
- 领域知识库相比通用搜索，增量价值到底有多大？
- 不同类型的审核任务，RAG 增益的差异有什么规律？

## 6. 为什么要比较三个模型？

因为 RAG 增益不是固定的，它取决于模型本身有多少知识。只有比较不同能力的模型，才能揭示"知识替代效应"的形态——是线性递减？还是倒 U 型？还是到某个点就不降了？这是论文的核心理论贡献。

## 7. 为什么要比较无知识/搜索/领域RAG？

因为我们想知道 RAG 的价值到底是"有知识就行"还是"必须是专业高质量知识"。如果搜索和领域 RAG 效果差不多，那说明知识"量"更重要；如果领域 RAG 好很多，说明知识"质"更重要。这直接关系到实践中怎么建 RAG 系统。

## 8. E×P 是别人提出的还是我们提出的？

**本文提出的操作性分类框架**。E 维度（知识依赖度）和 P 维度（推理复杂度）各自有文献基础（closed-book vs open-book、single-hop vs multi-hop），但把它们组合成 2×2 框架来系统分析 RAG 增益，是本文的工作。
论文里要如实说明，不要说是成熟理论。

## 9. 7个假设哪些有文献支撑？

| 假设 | 支持强度 | 说明 |
|------|---------|------|
| H1 RAG有效 | ⭐⭐⭐ Strong | 文献共识 |
| H2 模型有差异 | ⭐⭐⭐ Strong | scaling law 共识 |
| H3 知识替代效应 | ⭐⭐ Medium-Strong | 通用领域有充分证据，环评领域待检验 |
| H4 知识质量×强模型更敏感 | ⭐ Weak-Medium | 质量影响有证据，"强模型更敏感"证据不足 |
| H5 强模型E1仍有增益 | ⭐⭐ Medium | 方向合理，但需实证检验 |
| H6 E×P死排序 | ⭐ Weak | 方向性有道理，但具体排序无文献支持 |
| H7 过程质量提升 | ⭐⭐ Medium | 有相关证据，环评领域待验证 |

## 10. 哪些应该改成探索性问题？

- **H4**：把"强模型对知识质量更敏感"改成探索性研究问题
- **H6**：把死排序改成"RAG 增益随知识依赖度和推理复杂度而异"，排序在结果中报告
- **H3 的单调性**：保留假设但表述为"可能递减"，不预设严格单调

## 11. 环境/EIA为什么不是随便换一个应用场景？

因为环评有独特的边界条件：法规标准权威性、地方规则多样性、时效性、专业术语体系、多文件证据要求、可追溯性要求、错误判断的监管后果。这些使得环评领域的 RAG 研究不仅仅是"换个数据集"，而是在一个具有强约束的场景下检验和发展 RAG 理论。

## 12. 最终 GREEN/YELLOW/RED？

**🟡 YELLOW（修正表述后可以做）**

核心方向没问题，基础扎实。但需要：
1. 把 H4 降级为探索性问题
2. 把 H6 的死排序改成宽泛表述
3. 明确说明 E×P 是操作性分类而非成熟理论
4. 讨论小模型端可能的"利用瓶颈"效应

## 13. 如果只能保留一个最核心科学问题，应该是什么？

> **在环评审核这个专业法规场景下，RAG 增益是否随模型能力增强而递减？知识替代效应的领域边界在哪里？**

这是最有理论价值也最有实践意义的问题。其他问题（知识质量、任务异质性）都是围绕这个核心的深化和细化。

## 14. 哪 12 篇文献是论文必须精读的？

1. Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks... (NeurIPS)
2. Xu et al. (2026). RAG in the Wild: On the (In)effectiveness of LLMs with Mixture-of-Know... (ACL Findings)
3. Li & Ouyang (2025). How Does Knowledge Selection Help Retrieval Augmented Generation?... (EMNLP Findings)
4. Sarfati et al. (2025). Less LLM, More Documents: Searching for Improved RAG... (arXiv)
5. Team OLMo (2026). To Memorize or to Retrieve: Scaling Laws for RAG-Considerate Pretraini... (arXiv)
6. PNNL (2025). Benchmarking LLMs for Environmental Review and Permitting (NEPAQuAD)... (KDD)
7. Zhou et al. (2026). Integrating Fine-tuning and Retrieval-Augmented Generation to Address ... (Journal of Environmental Management)
8. Kim et al. (2024). Toward Robust RALMs: Revealing the Impact of Imperfect Retrieval on Re... (arXiv)
9.  (2026). Can Small Language Models Use What They Retrieve? An Empirical Study o... (arXiv)
10. Zhang et al. (2024). How Faithful are RAG Models? Quantifying the Tug-of-War between RAG an... (arXiv)
11. Sullivan & Staz (2025). Artificial Intelligence in Impact Assessment: The State of the Art... (Impact Assessment and Project Appraisal)
12. Booth et al. (2025). Large Language Model-assisted EIA Screening... (Impact Assessment and Project Appraisal)

（详细内容见 08_recommended_core_literature.md）
