# PRE_FLIGHT_REPORT

> 版本：V4.2 | 日期：2026-09-04 | 状态：FAIL（BM25已就绪，待Dense/Rerank+人工确认）

## 总体判断

**preflight_decision = FAIL**

5/10 硬门禁通过。BM25 检索已全部就绪，但 Dense+Rerank 需 API 授权、gold passage 需人工确认、金标需人工确认。

**距离可以开始实验还差**：
1. Dense + Rerank 检索（需 API 授权，28 次调用）
2. 14 题 gold passage 人工确认（确认 Top-5 中哪条是决定性证据）
3. 金标人工确认（至少 RAG_PRIMARY 的 14 题）
4. Web 快照统一化（K2/K3 复用同一 Web 证据）
5. 逐题报告证据包生成（最小充分证据）

---

## 10 项硬门禁

| 门禁项 | 状态 | 当前情况 |
|---|---|---|
| ✅ question_complete | PASS | 23 题题干全部完整 |
| ❌ human_gold_confirmed | FAIL | 0/23 题人工确认金标（全部 PROVISIONAL） |
| ✅ original_report_registered | PASS | 11/11 个项目有解析 JSON 登记 |
| ❌ word_parsed_fidelity_pass | FAIL | 0/11 完整保真度（缺原始 Word，JSON 解析正常） |
| ❌ required_report_evidence_in_prompt | FAIL | 0/23 逐题最小充分证据包（待生成） |
| ❌ required_external_clause_in_topk | FAIL | 0/14 题 gold passage 人工确认（0/70 候选待审） |
| ❌ K2_web_hash_equals_K3_web_hash | FAIL | 尚未生成统一 Web 快照（K3 必须复用 K2 的同一 Web 证据） |
| ✅ prompt_gold_leakage_zero | PASS | Prompt 已去锚定；Query 金标泄漏 0 处 |
| ✅ unresolved_pending_audit_zero | PASS | 状态字段完整，pending 计数为 0 |
| ✅ runnable_from_clean_checkout | PASS | frozen_config 存在；检索脚本可运行；无硬编码路径 |

---

## RAG 检索进度

| 阶段 | 完成数 | 总数 | 状态 |
|---|---:|---:|---|
| BM25 Top-20 | 14 | 14 | ✅ 全部完成（离线） |
| Dense Top-20 | 0 | 14 | ⏸️ 待 API 授权（DashScope embedding） |
| RRF 融合 | 0 | 14 | 待 Dense 完成后自动执行 |
| Rerank Top-10 | 0 | 14 | ⏸️ 待 API 授权（gte-rerank-v2） |
| Final Top-5 | 0 | 14 | 待 Rerank 完成后自动执行 |
| REPORT_ONLY_CONTROL 拒答 | 9 | 9 | ✅ 全部完成 |
| **占位符文件** | **0** | **23** | **✅ 0 个占位符** |
| **金标泄漏检查** | **0 处** | **23 题** | **✅ 全通过** |

### API 预估（Dense + Rerank）

- 14 题 × 1 次 embedding + 1 次 rerank = **28 次 API 调用**
- 模型：DashScope text-embedding-v3 + gte-rerank-v2
- 预计费用：约 0.1-0.3 元（极便宜）

---

## Gold Passage 状态

- 候选总数：70 条（14 题 × BM25 Top-5）
- 人工确认：0/14 题
- 旧候选已归档：legacy_candidates_not_for_review.jsonl
- 新候选来源：真实 BM25 检索结果（非旧快照）

---

## 题目分层

| 分析角色 | 题数 | EP 分布 |
|---|---:|---|
| RAG_PRIMARY（需外部知识） | 14 | E1P0 × 9, E1P1 × 5 |
| REPORT_ONLY_CONTROL（纯报告内） | 9 | E0P0 × 4, E0P1 × 5 |

---

## 可以先做的事（不需要等全部门禁）

1. **BM25 检索已完成** → 可以开始人工确认 gold passage
2. **Dense + Rerank** → 授权后 2-3 分钟跑完
3. **金标人工确认** → 跟 gold passage 确认可以并行
4. **逐题报告证据包** → 可以开始生成（不依赖 API）

---

## 启动正式实验的最低门槛

| 项 | 是否必须 | 说明 |
|---|---|---|
| BM25 完成 | ✅ 已完成 | |
| Dense+Rerank 完成 | ⚠️ 建议 | 没有 rerank 的 Top-5 质量可能不够 |
| Gold passage 确认 | ⚠️ 核心 | 不知道证据对不对，实验结果无法解释 |
| 金标确认 | ⚠️ 核心 | 金标不对，打分全错 |
| Web 快照统一 | ✅ 可用旧的 | v3.4 快照可先用，后续再替换 |
| 报告证据包 | ⚠️ 建议 | 没有最小充分证据，K1 基线不可靠 |
| 保真度核验 | ⚠️ 长期风险 | 不影响跑实验，但影响论文可信度 |

**诚实建议**：等 gold passage 和金标确认完再跑实验。不然跑出来的数据不知道"模型答错是因为不会，还是因为证据没搜到"，结果无法解释。

---

preflight_decision=FAIL
