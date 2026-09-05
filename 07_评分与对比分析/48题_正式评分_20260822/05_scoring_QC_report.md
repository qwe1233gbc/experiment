# 48题正式评分QC报告（20260822）

- 生成时间: 2026-08-22 14:14:57
- 评分对象: 01_final_analysis_dataset_v2.xlsx（48题×4条件=192条冻结回答）
- 评分协议: 逐字复用20260812原21题评分协议（judge=qwen3.8-max, temperature=0, max_tokens=1800, enable_thinking=False, timeout=240s, 每题≤2次尝试）
- 盲化: 固定映射A→R1 B→R2 C→R3 D→R4（与原21题一致），仅向裁判披露RAG/Skill可用性用于N/A规则

## 一、15项QC检查结果

| # | 检查项 | 结果 | 说明 |
|---|---|---|---|
| 1 | 总评分记录=192 | **PASS** | 实际 192 |
| 2 | unique question_id=48 | **PASS** | 实际 48 |
| 3 | 每题恰好4个condition | **PASS** | 48题, 异常题 无 |
| 4 | A/B/C/D各48条 | **PASS** | A=48 B=48 C=48 D=48 |
| 5 | 无13道已剔除题 | **PASS** | 剔除清单13题核对=13, 评分集中泄漏=0 |
| 6 | SourceStrength=0 | **PASS** | question_id含SourceStrength=0, task_type含=0 |
| 7 | Gold匹配=192/192(48题金标全部来自冻结Gold) | **PASS** | 48/48题Gold与冻结源逐字一致, 每题金标被4个condition共用→192/192 |
| 8 | model response匹配=192/192(哈希一致) | **PASS** | 192/192 parsed文件SHA256与冻结集v2一致 |
| 9 | judge成功=192/192 | **PASS** | judge_raw成功文件=48/48, judge_parsed=48/48 |
| 10 | score均处于合法范围(0/1/2或N/A) | **PASS** | 非法值 无 |
| 11 | N/A仅出现在原rubric允许的位置(强制规则) | **PASS** | 非法N/A 无; 强制N/A缺失 无; 分布: A.regulatory=48, A.skill=48, B.regulatory=2, B.skill=48, C.regulatory=46, D.regulatory=1 |
| 12 | normalized_100计算正确(适用维度/适用满分×100) | **PASS** | 错误 无 |
| 13 | 无重复评分(question×condition唯一) | **PASS** | 重复 无 |
| 14 | 无缺失评分(48×4全覆盖) | **PASS** | 缺失 无 |
| 15 | blind mapping可逆且无错误(A→R1 B→R2 C→R3 D→R4) | **PASS** | 映射错误 无, 192对(question,blind_id)全部双射 |

## 二、执行过程统计

- judge调用: 48题（每题一次比较式盲评R1-R4），共49次API调用（含1次失败重试）
- 技术失败/重试: 1题attempt1失败后attempt2成功（PL002_EnvQuality_Q01: ValueError: R1法规依据必须为null）
- JSON parse failure: 0次
- 评分校验失败重试: 1次（judge违反N/A规则→按原协议retry逻辑重试后成功）
- 最终失败: 0题

## 三、N/A分布（与原21题协议一致）

| 位置 | 本次48题 | 原21题 |
|---|---|---|
| A.regulatory_basis | 48 | 21/21 |
| A.skill_workflow | 48 | 21/21 |
| B.skill_workflow | 48 | 21/21 |
| C.regulatory_basis | 46 | 20/21 |
| C.skill_workflow | 0 | 0/21 |

N/A总数: 193格（A法规48+A技能48+B技能48+C法规裁量N/A）

### 裁判裁量N/A说明（3处，均位于regulatory_basis维度）

- PL004_Emission_水污.B, PL011_Construction_Q01.B, PL011_Construction_Q01.D
- 性质: judge输出JSON schema对regulatory_basis允许null（"0|1|2|null"），原协议validate_scores仅强制A组法规与A/B组技能为null，不拒绝B/C/D组法规维度null，故此3处属协议内裁判裁量，非技术失败，不触发重试。
- PL011_Construction_Q01为该题4组全部N/A：裁判判定施工期 completeness 审核题不涉及法规依据维度（题级对称裁量，不偏袒任何组）。
- PL004_Emission_水污.B为单组裁量N/A（B组适用满分6，C/D组适用满分10；归一化按各自适用满分计算）。
- 与原21题差异: 原运行中B/D法规维度均21/21被评分（无裁量N/A）；C法规维度原为20/21 N/A，本次46/48 N/A，比例相近（95.2% vs 95.8%）。
- 对下一阶段影响: 原21题析因分析口径为"四组共同适用前三维"（correctness/evidence_use/actionability），此3处裁量N/A均不在共同三维内，不影响2×2析因统计。

## 四、总体结论

**全部PASS**: 15/15项通过。

> 本阶段仅完成192条正式评分与QC，未进行2×2统计分析、效应计算或结果解释。
