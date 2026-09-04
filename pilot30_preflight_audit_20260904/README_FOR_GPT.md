# Pilot30 预飞审计包 - README_FOR_GPT

> **重要声明**：本包用于判断 25 道环评问答能否获得原始报告与 RAG 知识证据，以及实验失败发生在解析、切分、检索、Prompt、模型还是评分阶段。**本包不授权修改金标、补库或重跑 API。**
>
> 所有候选根因标记仅为 Trae 初步填写，**非最终审判**。最终结论由 GPT 结合原文审计后得出。

---

## 1. 基线 commit 与目录说明

**基线分支**：origin/main
**基线 commit**：03d2a55178cdde4f394afb890db649a07ebe60a9
**审计分支**：pilot30-preflight-audit-20260904

审计包位于 `pilot30_preflight_audit_20260904/` 目录，共 13 个子目录：

| 目录 | 内容 | 状态 |
|---|---|---|
| `00_inventory/` | 文件清单与哈希 | ✅ 完整 |
| `01_questions/` | 25 题清单 + 元数据 | ✅ 完整 |
| `02_original_reports/` | 原始 Word 报告登记 | ⚠️ 11项目均无原始Word（需补充） |
| `03_parsed_reports/` | 解析文本登记 | ⚠️ 仅有索引，缺逐项目解析文件 |
| `04_report_chunks/` | chunk 登记 | ⚠️ 仅有统计，缺逐题 chunk |
| `05_rag_knowledge_base/` | RAG 知识库快照 + 清单 | ✅ 完整（v3.4 快照） |
| `06_retrieval_snapshots/` | 检索快照 | ✅ 最终Top-K快照有；中间过程未记录 |
| `07_actual_prompts/` | Prompt 模板 | ✅ system prompt + user template |
| `08_model_outputs/` | 模型输出（144 条） | ✅ 完整（143 OK + 1 EXCLUDED_HARD） |
| `09_scoring_and_gold/` | 金标世代表 + 评分状态 | ⚠️ 仅结构化预检，正式打分待做 |
| `10_audit_tables/` | 5 张审计表 | ⚠️ 候选状态，待 GPT 终审 |
| `11_scripts_and_config/` | 关键脚本 + 配置 | ✅ 4 个核心脚本 |
| `12_logs/` | 验证报告 + 缺失清单 + 隐私扫描 | ✅ 完整 |

---

## 2. 25 题状态总览

| 类别 | 题数 | 说明 |
|---|---:|---|
| 已完成实验 | 16 题 | pilot17 v3.5，3模型×3条件=144条 |
| heldout 难题（待实验） | 7 题 | H01-H03, H06-H07, H09-H10 |
| 证据不足暂缓 | 2 题 | H04（多标准适用）、H05（生活污水核算） |
| **合计** | **25 题** | |

详细清单见 `01_questions/current_25_questions.csv`。

---

## 3. 原始 Word 与解析文本映射

- **原始报告**：11 个项目均未在审计包内找到原始 Word 文件（`report_registry.csv` 中均标记 MISSING）。需由研究者补充。
- **解析文本**：解析结果嵌入在 chunk 和上下文快照中，无独立的逐项目解析文件。
- **保真度**：因缺原始 Word，Word-to-parsed 保真度审计暂无法进行（`word_to_parsed_fidelity.csv` 均为 NOT_CHECKED / ORIGINAL_MISSING）。

---

## 4. RAG 快照与检索配置

- **RAG 版本**：v3.4
- **Top-K**：5
- **快照文件**：`pilot17_rag_snapshot_v3_4.jsonl`（57 条检索结果，覆盖 16 题）
- **Web 快照**：`pilot17_web_snapshot_v3_4.jsonl`
- **检索方法**：BM25 + Dense + RRF 融合 + Rerank（具体配置见 `kb_snapshot_manifest.json`）
- **⚠️ 限制**：BM25 候选、Dense 候选、Rerank 前后排名等中间过程未持久化（NOT_LOGGED），无法做全链路检索归因

---

## 5. 实际 Prompt 和回答的位置

- **System Prompt**：`07_actual_prompts/system_prompt_FROZEN_v2.txt`
- **User Prompt 模板**：`07_actual_prompts/prompt_template_FROZEN_v1.md`
- **逐题 Prompt**：v3.4 实验有 153 个 prompt 文件（在原实验目录），v3.5 增量实验的 prompt 嵌入在结果 JSONL 的 prompt 字段中
- **模型输出**：`08_model_outputs/pilot17_v3_5_full_results_144.jsonl`（144 条，含 raw_answer、reasoning_content、review_opinion 等）

---

## 6. 已知缺失文件

详见 `12_logs/missing_materials.json`，共 9 大类：

1. 11 个项目的原始 Word 报告
2. BM25 候选列表
3. Dense retrieval 候选列表
4. Rerank 前/后排名对比
5. 原始检索 query
6. 正式多维度 GPT 打分
7. 7 道疑点题人工盲评结果
8. 7 道 heldout 新题人工金标确认
9. H04/H05 暂缓题补充材料

---

## 7. 公开仓库未上传的私有文件

见 `PRIVATE_FILES_NOT_PUSHED.md`。

主要包括：
- 原始 Word 报告（含企业敏感信息）
- API Key、密钥
- 内部配置文件

---

## 8. 建议 GPT 阅读顺序

```
00_inventory → 01_questions → 02/03原文与解析 → 04分块 → 05知识库 → 06检索 → 07实际Prompt → 08回答 → 09金标评分 → 10审计表
```

建议重点关注：
1. **10_audit_tables/question_root_cause_matrix.csv** — 从这里开始，逐题追踪
2. **08_model_outputs/** — 看模型实际回答了什么
3. **05_rag_knowledge_base/pilot17_rag_snapshot_v3_4.jsonl** — 看 RAG 检索到了什么
4. **09_scoring_and_gold/gold_version_lineage.csv** — 金标变更历史

---

## 9. 所有表格字段字典

### question_root_cause_matrix.csv
- `question_id`：题目编号
- `report_evidence_available`：报告证据是否可得
- `external_evidence_required`：是否需要外部知识
- `kb_support_status`：知识库支持状态
- `parsed_fidelity_status`：解析保真度
- `chunk_support_status`：chunk 支持状态
- `retrieval_support_status`：检索支持状态
- `prompt_support_status`：Prompt 支持状态
- `answer_used_decisive_evidence`：回答是否使用了关键证据
- `gold_status`：金标状态
- `scoring_status`：评分状态
- `candidate_root_cause`：候选根因（Trae 填写，非最终）
- `supporting_file_paths`：支持文件路径
- `missing_materials`：缺失材料
- `trae_comment`：Trae 备注

### 其他审计表字段
详见各 CSV 表头 + `README_FOR_GPT.md` 中的说明。

---

## 10. 声明

**所有结论仅为 Trae 候选标记，非最终审判。** 本审计包的目的是提供完整的证据链材料，供独立审计者（GPT）进行全链路问题定位。不得将本包中的候选状态视为最终结论。
