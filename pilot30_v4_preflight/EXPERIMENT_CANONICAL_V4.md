# EXPERIMENT_CANONICAL_V4

> 唯一权威实验设计文档。其他 README、脚本说明只链接本文。
> 版本：V4.0 | 日期：2026-09-04 | 状态：PREFLIGHT_REPAIR

---

## 1. 研究问题

**逐步增加外部知识后，环评审核问答质量是否改善？该改善趋势能否在另一模型上复现？**

具体分解：
- H1（主）：K3 > K2 > K1（逐层知识增益）
- H2（区分度）：难题的知识增益幅度 > 简单题
- H3（跨模型）：知识增益方向在 Kimi 和 Qwen 上一致

---

## 2. 实验设计

### 2.1 模型

| 角色 | 模型 ID | 供应商 | 代际/规格 | thinking 模式 |
|---|---|---|---|---|
| 主模型 | qwen3.8-max | 阿里/火山 | 3.8 代旗舰 | 关闭 |
| 验证模型 | kimi-k2.6 | 月之暗面 | K2.6 标准版 | 关闭 |

- 主实验只用 qwen3.8-max
- Kimi 仅用于预注册的代表性子集验证（不参与主结果排名）

### 2.2 知识条件（逐层叠加）

```
K1 = 报告上下文（最小充分证据包）
K2 = K1 + 冻结 Web 搜索 Top-K（同一份 Web 证据）
K3 = K2 同一 Web 证据 + 冻结领域 RAG Top-K（REPORT_ONLY_CONTROL题允许rag_items=[]并记录retrieval_abstained=true）
```

- K3 **必须复用** K2 的完全相同的 Web 证据（同一快照、同一顺序）
- 对比解释：
  - K2 − K1 = Web 搜索带来的增益
  - K3 − K2 = 领域 RAG 在 Web 基础上的额外增益
  - K3 − K1 = 外部知识总增益

### 2.3 题集

- **正式题数：23 题**（H04、H05 暂缓）
- **分析角色**：RAG_PRIMARY × 14（需要外部知识的主效应题），REPORT_ONLY_CONTROL × 9（纯报告内计算/核查题，RAG 应拒答）
- EP 分布：E0P0 × 4，E0P1 × 5，E1P0 × 6，E1P1 × 8
- 金标分布：CORRECT × 8，PARTIALLY_CORRECT × 7，INCORRECT × 8
- 难度结构目标：易 30% / 中 40% / 难 30%（待实验后实际校准）

暂缓题：
- H04_PL004_MultiStandardApp（缺裁决材料：报告日期/完整标准适用范围）
- H05_PL002_LivingWastewaterCalc（题干仍为占位符，缺人数定额天数）

### 2.4 参数

| 参数 | 值 | 说明 |
|---|---|---|
| temperature | 0 | 确定性输出 |
| max_completion_tokens | 1200 | 短 JSON 任务上限；冒烟验证后可调整 |
| response_format | json_object | 所有模型统一；如某模型不支持先在冒烟阶段解决 |
| seed | 42 | 固定随机种子 |
| top_p | 1.0 | 默认 |

### 2.5 评分维度

| 维度 | 权重 | 说明 |
|---|---|---|
| conclusion 正确性 | 40% | 结论标签与金标匹配 |
| evidence 证据质量 | 20% | 真实性、充分性、准确性 |
| reasoning 推理严谨性 | 25% | 逻辑链条、计算、周全性 |
| knowledge 知识利用 | 15% | 外部知识整合深度（K1 不计入此维度） |

所有评分由独立 GPT 盲评完成，标记 PRECHECK 不视为正式结果。

---

## 3. 运行流程

```
静态门禁全部PASS → 9次冒烟测试（主模型×3条件×3分层题） → 冒烟PASS → 冻结commit → 主实验全量 → 盲评打分 → Kimi子集验证
```

### 3.1 静态门禁（10 项硬门禁）

1. question_complete = 100%
2. human_gold_confirmed = 100%
3. original_report_registered = 100%
4. word_parsed_fidelity_pass = 100%
5. required_report_evidence_in_prompt = 100%
6. required_external_clause_in_topk = 100%
7. K2_web_hash_equals_K3_web_hash = 100%
8. prompt_gold_leakage = 0
9. unresolved_pending_audit = 0
10. runnable_from_clean_checkout = PASS

### 3.2 冒烟测试
- 3 道分层代表题（易/中/难各 1）× K1/K2/K3 = 9 次
- 只跑主模型
- 验证：JSON 可解析、无截断、K2/K3 Web 哈希一致、输入合规

---

## 4. 版本与冻结

- 本文件（EXPERIMENT_CANONICAL_V4.md）是唯一权威设计
- 任何改动必须先更新本文件，再改脚本/配置
- 冒烟通过后冻结 commit SHA，全量实验从该 SHA 出发

---

## 5. 禁止事项

1. 不得为了得到 K3>K2>K1 而修改题目、证据或金标
2. 不得在实验过程中换题、换模型、换检索参数
3. 不得把 PRECHECK 分数当作正式结果
4. 不得在主实验完成前进行 Kimi 全量测试
5. 不得混用不同版本的快照、Prompt、金标
