# 最终数据集完整性报告

**生成时间**: 2026-08-22
**数据集版本**: final_frozen_v1
**状态**: 评分前冻结，不再修改实验结果

---

## 一、核心指标

| 指标 | 值 | 验证状态 |
|------|-----|---------|
| questions (N) | **48** | ✓ PASS |
| responses (n) | **192** | ✓ PASS |
| A组(LLM baseline, RAG=0,Skill=0) | 48 | ✓ PASS |
| B组(LLM+RAG, RAG=1,Skill=0) | 48 | ✓ PASS |
| C组(LLM+Skill, RAG=0,Skill=1) | 48 | ✓ PASS |
| D组(LLM+RAG+Skill, RAG=1,Skill=1) | 48 | ✓ PASS |
| complete_ABCD_pairs | **48** | ✓ PASS |
| SourceStrength题数 | **0** | ✓ PASS (已全部剔除) |

---

## 二、样本构成

### 2.1 题源构成

| 来源 | question_id数 |
|------|--------------|
| 原21题（第一阶段种子QA） | 21 |
| 新增40题中保留 | 27 |
| 新增40题中剔除（技术失败） | 13 |
| **合计** | **48** |

### 2.2 任务类型分布

| 任务类型 | question_id数 |
|---------|--------------|
| ActivatedCarbon | 2 |
| CaptureAirflow | 5 |
| CaptureEfficiency | 4 |
| Coefficient | 5 |
| Construction | 4 |
| DesignAirflow | 3 |
| Emission_噪声 | 4 |
| Emission_固废 | 5 |
| Emission_大气 | 1 |
| Emission_水污 | 3 |
| EnvQuality | 3 |
| HazardousWaste | 2 |
| V01 | 5 |
| VOCSTotal | 2 |

---

## 三、剔除规则执行

- **剔除依据**: 任一实验条件(A/B/C/D)下发生持续技术调用失败（HTTP503上游饱和、连接中断、length截断导致空响应等），按预设complete-case rule整题剔除
- **剔除数量**: 13道question_id
- **关键发现**: SourceStrength（源强核算）题型因prompt最长（58k-63k字符），全部5道题均因技术失败剔除，保留率0%。此为实验限制，需在论文Limitations中披露。
- **非选择性删除**: 剔除完全基于API技术可用性，与模型回答质量/正确性无关。

---

## 四、文件完整性验证

| 验证项 | 结果 |
|--------|------|
| 总行数=192 (48×4) | ✓ PASS |
| question_id唯一值=48 | ✓ PASS |
| 每个question_id恰好4条(A/B/C/D) | ✓ PASS |
| A/B/C/D各48条 | ✓ PASS |
| 无SourceStrength题 | ✓ PASS |
| 无13道剔除题 | ✓ PASS |
| 所有192条raw_response存在 | ✓ PASS |
| 所有192条parsed_output存在 | ✓ PASS |
| 所有192条content非空 | ✓ PASS |
| Gold答案可关联 | 192/192 (48 questions) |

---

## 五、实验参数冻结确认

| 参数 | 值 | 冻结状态 |
|------|-----|---------|
| model | qwen3.8-max | ✓ 冻结 |
| temperature | 0 | ✓ 冻结 |
| max_tokens | 8000 | ✓ 冻结（B类题有length截断风险，不调整） |
| system_prompt | 与正式实验一致 | ✓ 冻结 |
| RAG知识库 | 正式实验冻结版 | ✓ 冻结 |
| Skill package | 正式实验冻结版 | ✓ 冻结 |
| Prompt | input_snapshots冻结版（逐字节一致） | ✓ 冻结 |

---

## 六、结论

**数据集通过完整性验证，可进入评分阶段。**

- N=48 questions, n=192 model responses
- 2×2析因设计完整，每道题均有A/B/C/D四个条件
- SourceStrength题型已全部排除，结论不外推至该类任务
- 所有原始raw/parsed文件均存在且SHA256已记录在主表中
- **后续统计分析统一使用N=48, n=192**，不得再使用N=61, N=40, N=44等旧数字

---

*本报告由自动化脚本生成，不调用任何LLM API，不评分。*
