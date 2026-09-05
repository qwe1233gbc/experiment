# 40题 RAG Top-5 v3.1 正式重跑与冻结 验收报告

> 日期：2026-08-20
> 任务：40题 RAG Top-5 v3.1 正式重跑与冻结
> 输入：`40题_query_plan_v3_1.json`（已通过v3.1落地验收）
> 知识库：`正式实验RAG知识库_81源扩展版_20260820`（冻结，未修改）
> 唯一变更：报告事实query由旧版切换为v3.1；其余检索参数、知识库、Gold、Skill均未改动。

## 1. 检索配置（严格复用原21题/旧40题正式参数）

| 参数 | 值 |
|---|---|
| embedding | text-embedding-v4（1024维） |
| dense_top_k | 40 |
| sparse_top_k | 100 |
| candidate_top_k | 30 |
| final_top_k | 5 |
| RRF k | 60 |
| rerank | gte-rerank-v2（精确来源加成+1.0） |
| 候选池单源上限 | 3 |
| BM25精确代码加权 | 250 / 文件名500 |
| source去重 + parent扩展 | 是 |
| query构造 | v3.1（question + key_facts + evidence_windows + missing_slots），未调用旧build_retrieval_query |

## 2. 自动验收结果（13项）

总判定：**PASS**

| 检查项 | 结果 |
|---|---|
| 10. Gold leakage = 0 | ✅ 通过 |
| 11. Skill leakage = 0 | ✅ 通过 |
| 12. embedding/BM25/rerank/Top-K等参数完全未变 | ✅ 通过 |
| 13. 81源知识库索引未修改（registry hash与旧40题一致） | ✅ 通过 |
| 1. 40/40题均成功检索 | ✅ 通过 |
| 2. 每题恰好5个最终hit | ✅ 通过 |
| 3. question_id无重复、无遗漏 | ✅ 通过 |
| 4. query_sha256与v3.1完全一致（含query字节级一致） | ✅ 通过 |
| 5. rag_context SHA256一致 | ✅ 通过 |
| 6. source_id均属于81源manifest | ✅ 通过 |
| 7. child/parent可回溯 | ✅ 通过 |
| 8. rag_context与Top-5内容一致 | ✅ 通过 |
| 9. PL007全部008版 | ✅ 通过 |

## 3. Top-5 召回质量重新评级（实际Top-5）

- A（充分）：**37** 题
- B（部分充分）：**2** 题
- C（不足）：**1** 题

B级：['PL006_Construction_Q01', 'PL009_Construction_Q01']
C级：['PL011_Construction_Q01']

## 4. 新旧结果对比（旧24A/11B/5C → 新37A/2B/1C）

| 转移 | 题数 |
|---|---|
| A → A | 24 |
| B → A | 10 |
| B → B | 1 |
| C → A | 3 |
| C → B | 1 |
| C → C | 1 |

### 4.1 原5道C级题变化

| question_id | 旧 | 新 |
|---|---|---|
| PL006_ActivatedCarbon_Q01 | C | A |
| PL008_Construction_Q01 | C | A |
| PL009_Construction_Q01 | C | B |
| PL011_Construction_Q01 | C | C |
| PL012_CaptureAirflow_Q01 | C | A |

### 4.2 原15道未命中设计源 → 现仅1道

- 旧版0命中设计源题数：15
- 新版0命中设计源题数：1（仅 ['PL011_Construction_Q01']）
- 恢复：14/15 题

### 4.3 原A题退化检查

- 原A题退化：无

### 4.4 PL009 4-hit 问题

- v3.1修正query后，PL009_Construction_Q01 候选池自然恢复 **5个unique source（5-hit）**，无新增fallback逻辑。
- 结论：旧4-hit由query前处理偏差导致（旧query证据窗口被“三线一单”内容主导，候选池12个child全部来自4个三线一单源）。
- 新版Top-5来源：SRC015、SRC055、SRC060、SRC061、SRC056。

## 5. 版本路由与时点边界（未做任何调整）

- 未调整#28中15%（广东2023版本属性）、20%（不作通用规范值）。
- 未调整#30中HJ2026 120%设计风量（规范依据）、Q=K×P×H×V×3600（工程设计参考）、12次/h与60次/h（不作通用阈值）。
- PL007全部4题使用PL007_008版JSON；query/context中无007版数值（1.123/0.491/1.614）。

## 6. 防泄漏确认

- query仅由v3.1 plan的question + key_facts + evidence_windows + missing_slots构成；Gold/Skill正文未进入query。
- Gold泄漏检查（query≥20字、context≥40字滑窗）通过；Skill泄漏检查通过。
- rag_context全部来自81源知识库parent内容。

## 7. 人工抽查建议（12题）

优先纳入：仍为B/C的题、原5道C级题、改善幅度最大的题、每类Skill至少1题、版本边界题。

1. PL011_Construction_Q01（C级，建设内容完整性）
2. PL006_SourceStrength_Q01（A级，污染源强定量核算）
3. PL006_CaptureEfficiency_Q01（A级，废气收集效率）
4. PL006_ActivatedCarbon_Q01（A级，活性炭治理设施参数）
5. PL007_DesignAirflow_Q01（A级，废气设计风量）
6. PL008_VOCSTotal_Q01（A级，VOCs总量控制与一致性）
7. PL009_Coefficient_Q01（A级，产污系数适用性）
8. PL010_CaptureAirflow_Q01（A级，废气收集形式与理论排气量）
9. PL011_HazardousWaste_Q01（A级，危险废物识别）
10. PL007_SourceStrength_Q01（A级，污染源强定量核算）
11. PL011_ActivatedCarbon_Q01（A级，活性炭治理设施参数）
12. PL012_ActivatedCarbon_Q01（A级，活性炭治理设施参数）

“人工确认”“人工备注”在`Top5人工抽查表.xlsx`中留空。

## 8. Known Issue（仅记录，不判失败）

- PL008_SourceStrength_Q01、PL008_VOCSTotal_Q01 窗口正文仍存在HTML表格数字粘连（如528176.480%、06243.1295%等），属表格解析层td/th列边界问题；本次未根据Gold拆数、未改原始JSON、未改解析器。

## 9. 结论

- 40/40检索成功、每题恰好5-hit；13项自动验收全部通过。
- 召回质量：37A/2B/1C（旧24A/11B/5C）；原A题无退化；原5道C级中4道升A/B；原15道未命中设计源仅剩1道（PL011_Construction_Q01）。
- PL009_Construction_Q01 4-hit自然恢复为5-hit，确认旧问题由query前处理偏差导致。
- 未运行A/B/C/D；未进入Skill dry-run。

