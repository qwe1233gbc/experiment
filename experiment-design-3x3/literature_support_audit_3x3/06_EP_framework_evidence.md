# E×P 分类框架的文献基础审计

> 结论：AUTHOR_PROPOSED_OPERATIONAL_FRAMEWORK

> E 和 P 两个维度分别有理论基础，但 E×P 二维组合框架是本文提出的操作性分类。

---

## E 维度（知识依赖度 External Knowledge Dependency）

### 文献基础

- **Closed-book vs Open-book QA** 是问答领域的经典分类范式
  - Closed-book QA：模型只靠参数知识回答（Chen et al. 2017, 等）
  - Open-book QA / Open-domain QA：模型可以检索外部文档（Lewis et al. 2020, 等）
- **Knowledge-intensive NLP tasks** 是 RAG 研究的标准术语（Lewis et al. 2020）
- **Domain-specific vs General knowledge** 是领域 RAG 的基本区分（DomainRAG, KAG, 等）

### 在本文中的操作化定义

- **E0**：答案所需信息全部在环评报告内部，不需要外部法规标准知识
- **E1**：需要查阅外部标准、导则、名录等法规知识才能做出正确判断

### 文献支持强度：STRONG

E 维度的区分是 QA/RAG 领域的基础共识，有大量文献支撑。

---

## P 维度（推理复杂度 Reasoning/Processing Complexity）

### 文献基础

- **Single-hop vs Multi-hop reasoning** 是 RAG/QA 领域的常见任务分类
  - Single-hop：一次检索即可找到答案
  - Multi-hop：需要多步推理、多个证据综合
- **Reasoning complexity** 是 NLP 任务分类的常用维度
- **Direct lookup vs Comprehension/Reasoning** 是阅读理解的经典区分
- Li & Ouyang (2025) 明确指出任务复杂度影响知识选择对 RAG 的作用
- PIKE-RAG (2026) 指出不同 RAG 场景的挑战不同，特别是规则型 vs 计算型任务

### 在本文中的操作化定义

- **P0**：直接提取/查找型，答案就是标准原文或报告中的数据，不需要复杂推理
- **P1**：需要计算、比较、综合判断，涉及多步骤推理

### 文献支持强度：MEDIUM

"推理复杂度影响任务难度"是共识，但具体怎么分、分几类，没有统一标准。本文的 P0/P1 二分法是简化的操作性定义。

---

## E×P 二维框架

### 是否有文献提出完全相同的 2×2 分类？

**没有。**

### 正确的学术表述

不要写：
> "E×P 是一个成熟的理论框架。"

应该写：
> "Following prior work distinguishing knowledge-intensive tasks (Lewis et al., 2020) and reasoning complexity (Li & Ouyang, 2025), we propose an operational taxonomy with two dimensions: external knowledge dependency (E0/E1) and reasoning complexity (P0/P1)."

### 框架的价值

E×P 的价值不在于"理论创新"，而在于：

1. **实用价值**：为环评审核任务的难度分层和系统设计提供参考
2. **分析价值**：可以定位 RAG 增益的来源（是补了知识缺口，还是帮了推理？）
3. **可迁移性**：可以迁移到其他专业审核领域（法律合规、医疗质控等）

---

## 最终判定

**AUTHOR_PROPOSED_OPERATIONAL_FRAMEWORK**

两个维度各有文献基础，但 E×P 组合是本文提出的。应如实说明，不要伪造理论来源。
