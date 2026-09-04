# PRE_FLIGHT_REPORT

> 版本：V4.0 | 日期：2026-09-04 | 状态：FAIL

## 门禁状态

**preflight_decision = FAIL**

通过门禁：4/10

| 门禁项 | 状态 | 说明 |
|---|---|---|
| ✅ question_complete | PASS | 23题全部完整 |
| ❌ human_gold_confirmed | FAIL | 0/23 题已人工确认金标 — 未确认: ['NEW_PL001_invest_ratio', 'NEW_PL006_invest_ratio', 'NEW_P |
| ✅ original_report_registered | PASS | 11/11 个项目有解析文件登记 |
| ❌ word_parsed_fidelity_pass | FAIL | 0/11 个项目完整保真度核验通过；11 个项目JSON解析正常但缺原始Word无法核验 |
| ❌ required_report_evidence_in_prompt | FAIL | 逐题证据包: 0/23（待生成最小充分证据包） |
| ❌ required_external_clause_in_topk | FAIL | 0/23 题外部知识覆盖已确认；其余为 PARTIAL/MISSING，需审计是否包含决定性条款 |
| ❌ K2_web_hash_equals_K3_web_hash | FAIL | 尚未生成统一Web/RAG快照；K3必须复用K2的同一Web证据 |
| ✅ prompt_gold_leakage_zero | PASS | 结论枚举值作为JSON Schema示例出现属正常现象；未发现具体题目的金标答案泄漏 |
| ✅ unresolved_pending_audit_zero | PASS | 剩余 PENDING_AUDIT: 0 处（需逐题审计完成） |
| ❌ runnable_from_clean_checkout | FAIL | frozen_config存在: True; 脚本数: 0; 硬编码路径: 0 |

## 失败门禁详情

### ❌ human_gold_confirmed

0/23 题已人工确认金标 — 未确认: ['NEW_PL001_invest_ratio', 'NEW_PL006_invest_ratio', 'NEW_PL010_invest_ratio', 'NEW_PL015_invest_ratio', 'PL001_Emission_固体']...

### ❌ word_parsed_fidelity_pass

0/11 个项目完整保真度核验通过；11 个项目JSON解析正常但缺原始Word无法核验

### ❌ required_report_evidence_in_prompt

逐题证据包: 0/23（待生成最小充分证据包）

### ❌ required_external_clause_in_topk

0/23 题外部知识覆盖已确认；其余为 PARTIAL/MISSING，需审计是否包含决定性条款

### ❌ K2_web_hash_equals_K3_web_hash

尚未生成统一Web/RAG快照；K3必须复用K2的同一Web证据

### ❌ runnable_from_clean_checkout

frozen_config存在: True; 脚本数: 0; 硬编码路径: 0

## 额外检查项

- ✅ BM25索引哈希一致: 5/5 索引文件哈希与登记一致
- ✅ Prompt去锚定: system prompt中conclusion示例已改为空占位符
- ✅ 金标枚举完整: CORRECT/INCORRECT/PARTIALLY_CORRECT/INSUFFICIENT 四值完整
- ✅ run_matrix生成: 主实验 69 条 run matrix 已生成（23题×3条件）
- ✅ 标准来源登记: 38 个标准来源已登记（可追溯性等级: CARD_EXISTS）
- ✅ 索引完整性: 5/5 索引文件存在且哈希一致

## 待整改项（按优先级）

1. **human_gold_confirmed**: 0/23 题已人工确认金标 — 未确认: ['NEW_PL001_invest_ratio', 'NEW_PL006_invest_ratio', 'NEW_PL010_invest_ratio', 'NEW_PL015_invest_ratio', 'PL001_Emission_固体']...

2. **word_parsed_fidelity_pass**: 0/11 个项目完整保真度核验通过；11 个项目JSON解析正常但缺原始Word无法核验

3. **required_report_evidence_in_prompt**: 逐题证据包: 0/23（待生成最小充分证据包）

4. **required_external_clause_in_topk**: 0/23 题外部知识覆盖已确认；其余为 PARTIAL/MISSING，需审计是否包含决定性条款

5. **K2_web_hash_equals_K3_web_hash**: 尚未生成统一Web/RAG快照；K3必须复用K2的同一Web证据

6. **runnable_from_clean_checkout**: frozen_config存在: True; 脚本数: 0; 硬编码路径: 0

## 当前可用资产

- 23 道正式题目（16 历史 + 7 heldout）
- 11 个项目解析 JSON（已登记）
- RAG 索引完整（5/5 哈希一致）
- 38 个标准知识卡（已登记来源）
- v3.4 RAG/Web 快照（覆盖 15-16/23 题）
- 去锚定 Prompt（conclusion 空占位符）
- frozen_config + run_matrix（69 条主实验）
- 验证脚本（相对路径，可跨环境运行）

---

preflight_decision=FAIL
