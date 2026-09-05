# Pilot 3×3 准备工作 v1.0

> **状态**：🟡 **BLOCKED_BY_MODEL_GRADIENT**（5 项阻塞，3 项警告，2 项通过）
> **版本**：v1.0
> **日期**：2026-09-01

---

## 快速回答 20 问

### 1. 科学问题最终版本是什么？
在知识密集型环境专业审核中，外部知识增强的效用如何受到模型能力、知识来源与任务知识—推理需求的共同调节？

### 2. H1-H4 是什么？
- H1（Knowledge Effect）：领域 RAG（K3）相对于无知识（K1）提高审核表现，尤其在 E1 任务中
- H2（Model Effect）：经独立校准后，基础能力更高的模型基线表现更高
- H3（Model × Knowledge）：外部知识的效应因模型能力而异（核心假设）
- H4（Task Boundary）：外部知识效应因知识依赖度和推理复杂度而异

### 3. EQ1-EQ2 是什么？
- EQ1：Model × Knowledge 的形态是递减、平台还是倒 U 型？
- EQ2：不同知识来源如何改变错误类型、证据忠实度和知识利用方式？

### 4. 三模型梯度是否成立？
**尚未验证**。校准集（20 题）已准备，待运行 K1 条件下的三个模型。

### 5. 如果不严格成立，怎么命名模型条件？
改称 "three models with empirically differentiated baseline capability"（A1/A2/A3）。

### 6. Pilot16 是否 4×4 平衡？
题目数量平衡（EP 四类各 4 题），但 CORRECT/INCORRECT 不平衡。

### 7. correct/incorrect 是否平衡？
**不平衡**。12 CORRECT / 4 INCORRECT（3:1）。
- E0P0：4/0（天花板风险）
- E1P0：4/0（天花板风险）
- E0P1：3/1
- E1P1：2/2

正式实验需扩充 INCORRECT 题。

### 8. Gold 是否 16/16 可靠？
初标全部为 A/B 级，但完整人工复核**待完成**。目标：16/16 deterministic。

### 9. E×P 是否定义清楚？
定义清楚。判定规则、流程图、常见误区都已写入 `03_EP_labeling_protocol.md`。

### 10. 是否准备双人标签一致性？
Reviewer 1（DSH）已完成初标，**Reviewer 2 待安排**。目标 Cohen's κ ≥ 0.80。

### 11. K1/K2/K3 最终如何命名？
Knowledge Condition（知识来源条件），三个水平为 K1（无外部知识）/ K2（联网搜索）/ K3（领域 RAG）。
**禁止**写成 low/medium/high quality。

### 12. K2/K3 evidence schema 是否一致？
规范已写好，但**实际转换尚未完成**。统一为 Evidence 1-5 + Source/Title/Date/Content 格式。

### 13. token budget 是否可比？
**尚未估计**。目标：K2/K3 evidence token budget 尽量处于同一范围。

### 14. K2/K3 manipulation check 是否完成？
**未完成**。待 K2/K3 检索结果出来后人工标注 answer-bearing recall、authoritative-source rate、applicability rate、noise rate。

### 15. temperature=0 稳定性如何？
**未检验**。计划抽 10 题 × 1 模型 × 1 条件，重复 3 次，目标 conclusion agreement ≥ 95%。

### 16. Prompt 是否 144/144 冻结？
Manifest 结构已生成（144 条），但 hash 和 token 估计为 PENDING，**待实际生成 prompt 后填充**。

### 17. GLMM 计划是否冻结？
**已冻结**。主模型：Correct ~ Model*Knowledge + E + P + Knowledge:E + Knowledge:P + (1|Question) + (1|Project)。

### 18. 当前唯一阻塞项是什么？
**模型梯度未验证**（最核心阻塞项）。此外还有 EP 双盲审核、知识操纵检查、prompt 泄露审计等 4 项阻塞。

### 19. 是否达到 READY_FOR_PILOT144_API_RUN？
**否**。当前状态：BLOCKED_BY_MODEL_GRADIENT。

### 20. 下一步唯一动作是什么？
运行模型能力操纵检查（20 题校准集 × 3 模型 × K1），验证梯度是否成立。

---

## 目录结构

```
pilot3x3_preparation_v1/
├── 01_experiment_inventory.xlsx          实验资产清单
├── 02_preregistered_hypotheses_v1.md      预注册假设（H1-H4, EQ1-EQ2）
├── 03_EP_labeling_protocol.md            E×P 标签协议
├── 04_pilot16_EP_labeling_audit.xlsx     Pilot16 EP 标签审计（含双盲模板）
├── 05_model_calibration_set.xlsx          模型能力校准集（20 题）
├── 06_model_capability_manipulation_check.xlsx  模型操纵检查结果模板
├── 07_model_calibration_findings.md       模型校准发现（待运行后填写）
├── 08_pilot16_gold_review.xlsx           Pilot16 Gold 复核模板
├── 09_pilot16_label_balance_audit.xlsx   标签平衡审计
├── 10_knowledge_condition_spec.md        知识来源条件规范
├── 11_pilot16_knowledge_manipulation_check.xlsx  知识操纵检查模板
├── 12_prompt_template_FROZEN.md          Prompt 模板（冻结版）
├── 13_determinism_stability_check.xlsx   稳定性检查模板
├── 14_pilot144_prompt_manifest_FROZEN.jsonl  144 条 Prompt Manifest（结构模板）
├── 15_prompt_leakage_audit.xlsx          Prompt 泄露审计模板
├── 16_statistical_analysis_plan_v1.md    统计分析计划（预注册）
├── 17_power_simulation_template.py       效力模拟模板
├── 18_pilot144_preflight_report.json     Preflight 报告
├── README.md                             本文件
└── issues.md                             问题清单与风险
```

---

## Preflight 检查清单

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 题目数量（16题，4×4） | ✅ PASS | EP四类各4题 |
| 标签平衡（接近1:1） | ⚠️ WARN | 12/4，E0P0和E1P0全correct |
| Gold确定性（16/16） | ⏳ TBD | 待人工完整复核 |
| 模型梯度操纵检查 | ❌ FAIL | 校准集已备，待运行 |
| 知识条件定义 | ⚠️ WARN | 规范已写，schema和token待实际对齐 |
| Prompt模板冻结 | ⚠️ WARN | 模板已备，泄露审计待做 |
| 模型参数统一 | ✅ PASS | temperature=0, max_tokens=8192 |
| Prompt manifest | ⚠️ WARN | 144条结构已生成，hash待填 |
| EP标签一致性 | ❌ FAIL | 仅1人标注，缺第二审核人 |
| 统计分析计划 | ✅ PASS | 已冻结 |
| 稳定性检查 | ❌ FAIL | 待运行 |

**总计**：✅ 2 · ⚠️ 3 · ❌ 5

---

## 下一步行动清单

### 第 1 步：模型能力操纵检查（最优先）
- 运行 20 题校准集 × 3 模型 × K1 条件
- 验证 A3 > A2 > A1 是否成立
- 输出 `07_model_calibration_findings.md`

### 第 2 步：EP 标签双盲审核
- 安排第二审核人独立标注
- 计算 Cohen's κ
- 如果 κ ≥ 0.80，确认 final label
- 如果不够，修订判定规则

### 第 3 步：Gold 人工复核
- 逐题核验 16 题的 Gold 答案
- 确认 16/16 deterministic
- 有争议的题替换

### 第 4 步：K2/K3 检索准备
- 运行 16 题的 Serper 搜索（K2）
- 运行 16 题的领域 RAG 检索（K3）
- 统一转换为 Evidence Schema
- 估计 token budget

### 第 5 步：知识操纵检查
- 人工标注 E1 题的 4 项知识质量指标
- 记录 K2/K3 的实际差异

### 第 6 步：Prompt 冻结与泄露审计
- 实际生成 144 条完整 prompt
- 填充 manifest 的 hash 和 token 字段
- 完成 prompt leakage audit
- 确认只有 knowledge block 不同

### 第 7 步：稳定性检查
- 抽 10 题 × 1 模型 × 1 条件，重复 3 次
- 验证 conclusion agreement ≥ 95%

### 第 8 步：最终 Preflight
- 更新 `18_pilot144_preflight_report.json`
- 如果全部通过，状态更新为 `READY_FOR_PILOT144_API_RUN`
- **不自动运行 Pilot**，等下一轮单独执行

---

## 研究诚信边界

本轮绝不能为了得到 K3>K1、A3>A1、知识替代递减等预期结果而：
- 换 Gold
- 换题
- 改评分
- 调搜索结果
- 调 RAG 参数直到趋势满足
- 删除不利结果

**可以修的**：实验操纵是否有效、资产是否公平、变量定义是否清楚。
**不能修的**：结果方向。
