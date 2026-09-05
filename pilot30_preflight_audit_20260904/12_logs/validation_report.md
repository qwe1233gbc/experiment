# 审计包验证报告

- **验证状态**: PASS
- **总检查项**: 19
- **通过**: 19
- **失败**: 0

## 全部检查项

- ✅ 25个唯一question_id: 实际25个
- ✅ 16+7+2状态数量正确: 已实验16, heldout7, 暂缓2
- ✅ SHA256可复算: pilot17_rag_snapshot_v3_4.jsonl: 73e9f6b963e13104...
- ✅ SHA256可复算: pilot17_v3_5_full_results_144.jsonl: d6e948c00676012c...
- ✅ 项目-报告映射完整: 题目项目11个, 登记项目11个, 缺0个: set()
- ✅ 运行记录数: 实际144条
- ✅ 排除记录数≤2: 实际1条
- ✅ 3模型×3知识条件: 模型3个: {'A3', 'A1', 'A2'}, 知识条件3个: {'K3', 'K1', 'K2'}
- ✅ JSON可解析: kb_snapshot_manifest.json: 
- ✅ JSON可解析: scoring_status.json: 
- ✅ JSON可解析: missing_materials.json: 
- ✅ JSONL可解析: pilot17_rag_snapshot_v3_4.jsonl: 
- ✅ JSONL可解析: pilot17_v3_5_full_results_144.jsonl: 
- ✅ KB覆盖表覆盖全部题目: 表中25题, 题目清单25题, 差异set()
- ✅ CSV字段齐全: 01_questions/current_25_questions.csv: 25行
- ✅ CSV字段齐全: 10_audit_tables/question_root_cause_matrix.csv: 25行
- ✅ CSV字段齐全: 09_scoring_and_gold/gold_version_lineage.csv: 25行
- ✅ README_FOR_GPT.md存在: size: 6037
- ✅ 缺失清单存在: 已生成

---

**重要说明**：验证通过仅代表审计包结构完整、文件可解析、数量匹配。**不代表题目证据充分或实验可运行**。
具体证据质量和根因判定需由 GPT 结合原文逐题审计。
