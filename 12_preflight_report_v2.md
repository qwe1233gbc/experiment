# Pilot17 修复与预检结论 v2

**修复版本**: v3.4_repair_20260903  
**生成时间**: 2026-09-03  
**审计范围**: 17/17题 Word直接核验 + JSON保真 + Web/RAG质量  
**当前决定**: `preflight_decision = FAIL`  
**正式运行许可**: `formal_run_allowed = false`  
**audit_scope**: FULL_17_OF_17 (Word直接核验)  
**benchmark_decision**: BENCHMARK_NOT_READY

---

## 1. 审计范围
- Word直接核验：17/17题（python-docx读取原始Word）
- JSON保真核验：17/17题（51个证据槽，双命中率43.1%）
- 上下文证据槽核验：0/17题（待上下文构建后补充）
- Web/RAG适用性核验：17/17题

## 2. 修复结果
- 标准编号检索规范化：PASS（12/12回归测试通过，PL001 5/5正确找到）
- PL010章节分类：PASS（候选修复完成，基于内容匹配，7块全部分类正确）
- RAG指令污染过滤：PASS（候选快照已生成，排除6个程序性文档共28条）
- 原始响应完整记录：PENDING（方案已设计，待验证）
- JSON Schema增强：PENDING（候选系统Prompt已生成）
- PL008金标人工确认：PENDING（候选修订INCORRECT，待双人确认）

## 3. 最小复测
- API成功：0/5（尚未运行）
- 工程成功：0/5（尚未运行）
- 语义正确：0/5（待人工确认）
- 截断：0/5
- Schema失败：0/5

> 5次最小复测单元：PL002_A3_S1, PL008_A3_S0, PL010_A1/A2/A3_S2

## 4. 失效范围
- 因Prompt变化失效：系统Prompt修改 → 全部153次（若采用全局修改）
- 因上下文变化失效：PL010章节修复 → 待哈希比对确认
- 因Web/RAG快照变化失效：RAG过滤程序性文档 → 全部S2条件（51条）
- 仅需重评分：PL008金标修订 → 9条输出

## 5. 门禁检查清单（7/13 通过）
- [x] 正式实验设计统一为S0/S1/S2逐级增强 — 设计已固定
- [x] 17/17题完成原Word直接核验 — 17/17题完成
- [x] 17/17题完成JSON保真与证据槽核验 — 17/17题完成（0题全通过）
- [ ] 全部金标完成人工确认 — 仅AI预核查，待双人人工确认
- [x] Web与RAG均有权威性版本记录 — 已完成17题Web/RAG审计
- [ ] RAG已排除程序性指南 — 候选快照已生成，待验证集成效果
- [x] S1与S2使用同一份Web Top-5 — 设计保证B/C Web哈希一致
- [ ] 153个Prompt预生成冻结 — 尚未预生成全部153个Prompt
- [ ] 153个Prompt泄漏审计通过 — 27次定向重测通过，全量待审计
- [x] 3个模型参数一致 — 由frozen_config统一读取
- [ ] 5次最小复测全部通过 — 尚未执行（需API调用）
- [x] 自动评分标为AI_PRE_SCORE — 自动评分脚本已标注
- [ ] 可复现实验清单已生成 — 待正式实验前生成

## 6. 最终决定
- preflight_decision = FAIL
- formal_run_allowed = false
- decision_reason =
  1. 17题金标尚未完成双人人工确认（仅AI预核查）
  2. PL010上下文哈希变化尚未验证（影响18条数据）
  3. RAG候选快照未验证实际检索效果和Prompt集成
  4. 5次最小复测尚未执行（需API Key和配置）
  5. 运行器增强方案未实际集成验证
  6. 153个正式Prompt尚未预生成和哈希冻结
  7. 全量Prompt泄漏审计尚未完成

---

## 7. 已交付文件清单

| 文件名 | 说明 | 状态 |
|--------|------|------|
| 00_repair_input_inventory_and_hashes.csv | 输入文件盘点与哈希 | ✅ |
| 01_code_change_log.md | 代码修改日志（5项修改） | ✅ |
| 02_word_json_fidelity_17.csv | 17题Word→JSON保真度 | ✅ |
| 04_web_rag_knowledge_audit_v2.csv | 17题Web/RAG审计 | ✅ |
| 08_question_verdicts_summary_v2.csv | 17题问题裁决汇总 | ✅ |
| 09_gold_change_and_human_confirmation_log.xlsx | 金标修订记录 | ✅ |
| 12_preflight_report_v2.md | Preflight门禁报告 | ✅ |
| evidence_trace_v2.jsonl | 逐证据槽追踪（51条） | ✅ |
| hash_manifest_after_repair.csv | 修复后文件哈希 | ✅ |
| PL010_sections_fixed_candidate.json | PL010章节修复候选 | ✅ |
| pilot17_rag_snapshot_candidate_v3_4.jsonl | RAG过滤后候选快照 | ✅ |
| system_prompt_candidate_v3.txt | 增强版系统Prompt候选 | ✅ |
| evidence_search_utils.py | 标准编号规范化工具 | ✅ |
| scripts/ | 修复脚本（5个） | ✅ |
| gpt_repair_prompt.md | GPT修复任务提示词 | ✅ |

---

*本报告为静态修复阶段总结。153次正式实验启动前必须完成所有门禁项。*
