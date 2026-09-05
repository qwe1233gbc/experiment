# RAG-QA 对齐整改报告

> 版本：V4.0 | 日期：2026-09-04 | 状态：CANDIDATE_AWAITING_HUMAN_REVIEW

## 总体结论

**preflight_rag_status = FAIL**（候选已生成，待人工确认）

- 23 题中 14 道为 RAG_PRIMARY（需要外部知识），9 道为 REPORT_ONLY_CONTROL（纯报告内题）
- 38 个标准来源已登记，全部为 DERIVED_CARD（二手知识卡，需核对官方原文）
- 14 道 RAG 主效应题中：8 题有 RAG 快照候选，6 题无快照（含 1 题完全缺失、4 题二手卡、1 题条件性）
- Gold passage 候选已从现有快照提取，**全部待人工确认**
- 检索全链路目录结构已就绪，**待接入实际检索模块后生成真实快照**

## 题目分层

| 分析角色 | 题数 | 说明 |
|---|---:|---|
| RAG_PRIMARY | 14 题 | 需要外部知识的主效应题（E1P0×9, E1P1×5） |
| REPORT_ONLY_CONTROL | 9 题 | 纯报告内计算/核查题（RAG 应拒答） |

REPORT_ONLY_CONTROL 题清单：
- invest_ratio × 4（PL001/006/010/015）
- 生活污水、纯水浓水、VOCs 总量、VOCs 监测、VOCs 产排平衡

## 知识库内容充分性

| 内容状态 | 题数 | 说明 | 下一步 |
|---|---:|---|---|
| PRESENT_RAW_TEXT | 6 题 | 库内有原文片段 | 优先修检索（召回完整条款） |
| PRESENT_STRUCTURED | 2 题 | 有结构化条目但不完整 | 去噪并召回完整定义 |
| DERIVED_CARD_ONLY | 4 题 | 只有二手知识卡，无官方原文 | 补官方全文并核对 |
| MISSING | 1 题 | 知识库完全没有 | 确认适用后补库 |
| PRESENT_RAW_TEXT_CONDITIONAL | 1 题 | 有原文但适用性待确认 | 先确认报告执行标准 |

## 来源可追溯性

- 38 个标准来源全部标记为 DERIVED_CANDIDATE_NEEDS_HUMAN_VERIFY
- 缺少：官方 URL、发布/实施日期、适用范围、原始文件哈希
- **需人工逐项核对官方原文后升级为 HUMAN_VERIFIED**

## Gold Passage 候选

- 从 v3.4 RAG 快照中为 8 道题提取了 23 条候选（每题最多 3 条）
- 6 道题无快照（H01/H03/H06/H07/H09/H10）
- **全部候选待人工确认哪条（或是否有）是 gold passage**

## 检索全链路

目录结构已就绪：
```
06_retrieval_snapshots/
  <question_id>/
    00_query.json          检索query（含金标泄漏检查）
    01_bm25_top20.jsonl    BM25 Top-20
    02_dense_top20.jsonl   Dense Top-20
    03_rrf_top20.jsonl     RRF融合 Top-20
    04_rerank_top10.jsonl  Rerank重排 Top-10
    05_final_top5.jsonl    最终 Top-5（含父块上下文）
```

当前状态：框架就绪，待接入实际检索模块后生成真实快照。

## 人工确认任务清单

共 **13 项** 人工任务，详见 `09_validation/human_review_tasks_rag.csv`：

| 任务类型 | 数量 | 说明 |
|---|---:|---|
| GOLD_PASSAGE_VERIFY | 8 题 | 从候选中确认 gold passage |
| SOURCE_VERIFY_AND_ADD | 4 题 | 核对官方原文并更新来源登记 |
| KB_CONTENT_ADD | 1 题 | 补充缺失的 VOCs 总量替代政策 |

## 门禁状态

| 门禁 | 状态 | 说明 |
|---|---|---|
| required_external_clause_in_topk | ❌ FAIL | 14 题 gold passage 均未人工确认 |
| K2_web_hash_equals_K3_web_hash | ❌ FAIL | 新快照未生成 |
| prompt_gold_leakage_zero | ✅ PASS | Query 生成规则禁止金标倒推 |

## 下一步

1. 人工确认 8 题的 gold passage
2. 人工核对 4 道二手卡题的官方原文
3. 确认 H06 VOCs 总量替代的适用政策并补库
4. 接入实际检索模块，生成 14 题全链路快照
5. 计算 context_recall@5、decisive_clause_hit@5 等指标
6. 确认全部 14 题 recall=1 后，更新门禁状态
