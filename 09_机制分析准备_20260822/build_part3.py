#!/usr/bin/env python3
"""Part 3: 生成07_实验过程与方法边界.md 与 08_GPT深度分析输入包.md（全部带来源标记）。"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(r'E:\实验文件整理_按论文逻辑')
SCORE_DIR = ROOT / '07_评分与对比分析' / '48题_正式评分_20260822'
STAT = ROOT / '08_2x2析因统计_48题_20260822'
OUT = ROOT / '09_机制分析准备_20260822'

score = pd.read_csv(SCORE_DIR / '04_formal_scoring_results.csv', keep_default_na=False, na_values=['', 'N/A', 'NA'])
DIMS3 = ['correctness', 'evidence_use', 'actionability']
score['c3'] = score[DIMS3].sum(axis=1)
qle = pd.read_csv(STAT / '02_analysis_dataset' / 'question_level_effects.csv')
het = pd.read_csv(STAT / '07_task_heterogeneity' / 'task_heterogeneity_common3d.csv')
rob = pd.read_csv(STAT / '08_robustness' / 'robustness_three_scales.csv')
dd = pd.read_csv(STAT / '08_robustness' / 'dimension_decomposition.csv')
pw = pd.read_csv(STAT / '06_pairwise' / 'pairwise_holm_common3d.csv')
be = pd.read_csv(STAT / '05_bootstrap' / 'bootstrap_effects_common3d.csv')
desc = pd.read_csv(STAT / '03_descriptive' / '02_descriptive_statistics.csv')
typical = pd.read_csv(OUT / '_tmp_typical.csv')

# ============ 07 方法边界 ============
t7 = """# 实验过程与方法边界（只陈述事实）

> 本文档只记录实验过程事实与方法边界，不含结果解释。所有数字可追溯到来源文件。

## 1. API技术失败发生情况

- 初始执行：160个任务（40题×4条件）中成功119个，技术失败41个【来源：06_ABCD四组实验结果\\新增40题_qwen3.8-max_正式实验_20260820\\正式实验技术失败与样本剔除报告.md】
- 失败类型构成：HTTP503（上游服务饱和，"重试超时，上游负载已饱和"）、HTTP500（i/o timeout）、HTTP200空响应（finish_reason=length导致content为空）【来源：技术失败剔除题清单.csv / 最后错误类型列】
- 补救过程：三轮重跑救援；2026-08-22 00:33中间状态为17题剔除/N=44；02:10-02:53最后一轮恢复6个D组任务，其中4题（PL008_VOCSTotal_Q01、PL009_Coefficient_Q01、PL013_ActivatedCarbon_Q01、PL013_Coefficient_Q01）因此完整恢复，最终13题剔除【来源：final_rerun.log + 01_final_analysis_dataset_v2.xlsx交叉推导】

## 2. 技术失败的分布特征

- 13道最终剔除题中，13/13题的失败group均含D组（LLM+RAG+Skill，prompt最长条件）【来源：技术失败剔除题清单.csv（失败组列）∩ 最终48题集推导】
- 失败group分布：仅D组失败9题；B,D失败3题；B,C,D失败2题（其中1题为PL009_Construction_Q01仅D组）【来源：同上】
- 失败任务类型：SourceStrength 5题、ActivatedCarbon 3题、VOCSTotal 3题、HazardousWaste 2题、Coefficient 2题、Construction 1题、DesignAirflow 1题【来源：技术失败剔除题清单.csv】

## 3. SourceStrength 5/5退出

- SourceStrength（源强核算）题型共5题（PL006/PL007/PL008/PL010/PL013_SourceStrength_Q01），prompt长度58k-63k字符（全部题型中最长），5题全部因技术失败剔除，保留率0%【来源：02_final_dataset_integrity_report.md §三关键发现】
- 该题型在最终48题样本中数量为0【来源：04_formal_scoring_results.csv task_type列实测】

## 4. 13题最终剔除与complete-case规则

- 剔除规则（预设）：任一实验条件(A/B/C/D)下发生持续技术调用失败，按complete-case rule整题剔除【来源：02_final_dataset_integrity_report.md §三】
- 剔除数量：13道question_id；最终N=48（21旧+27新），n=192【来源：同上 §一核心指标】

## 5. 剔除与回答质量无关的证据

- 剔除判定依据仅为API技术可用性（HTTP状态码/空响应/超时），判定发生在评分之前；13道剔除题从未进入评分环节【来源：技术失败剔除题清单.csv（剔除原因列全部为technical execution failure）】
- 剔除决策由预设规则自动执行，无人工按回答内容选择【来源：02_final_dataset_integrity_report.md §三"非选择性删除"】

## 6. 最终48题task_type构成

| task_type | 题数 | task_type | 题数 |
|---|---|---|---|
| Emission_固废 | 5 | Emission_噪声 | 4 |
| V01 | 5 | CaptureEfficiency | 4 |
| Coefficient | 5 | Construction | 4 |
| CaptureAirflow | 5 | DesignAirflow | 3 |
| Emission_水污 | 3 | EnvQuality | 3 |
| ActivatedCarbon | 2 | HazardousWaste | 2 |
| VOCSTotal | 2 | Emission_大气 | 1 |

【来源：04_formal_scoring_results.csv task_type列实测分布】

## 7. 原21题与新增27题任务类型差异

- 原21题（PL001-PL005）：报告核查类任务（Emission_固废/水污/噪声/大气、V01、EnvQuality等6种类型）
- 新增27题（PL006-PL015）：工程参数类任务（Coefficient产污系数、CaptureAirflow捕集风量、DesignAirflow设计风量、CaptureEfficiency捕集效率、ActivatedCarbon活性炭参数、VOCSTotal总量、HazardousWaste危废、Construction建设内容等8种类型）
- 两部分任务类型集合零重叠【来源：04_formal_scoring_results.csv question_source×task_type交叉表】
- Emission_水污3题中含PL002_水污（20260818补实验题，属于旧21题集）【来源：question_source列】

## 8. judge评分方法

- judge模型：qwen3.8-max；temperature=0；max_tokens=1800；enable_thinking=False【来源：judge_execution_manifest.json】
- 评分协议：逐字复用20260812原21题协议（同一prompt模板、五维rubric 0/1/2、N/A规则、JSON解析、retry逻辑）【来源：48题_正式评分_20260822\\01_原21题评分协议复现说明.md】
- 盲评机制：每题A/B/C/D固定映射为R1/R2/R3/R4（A→R1, B→R2, C→R3, D→R4），judge同时盲评同题四个回答【来源：02_blind_mapping.csv】
- judge输入：question + Gold参考答案 + 报告金标证据(前4条) + 四个匿名回答的压缩摘要；不输入RAG Top-5原文、Skill正文、组别真实名称【来源：score_48q_formal.py make_prompt函数】
- 同一judge对同一84条旧题回答（20260812与20260822两轮独立评分）的test-retest信度：common_3d ICC(2,1)=0.786，三维完全一致率94.0-97.6%，无系统漂移【来源：09_评分信度与敏感性检验_20260822\\test_retest_dimension_stats.csv】

## 9. 192/192评分QC

- 192/192完成评分；judge成功48/48题；retry 1次（attempt1违反N/A校验，attempt2成功）；parse failure=0；QC 15/15 PASS【来源：05_scoring_QC_report.md】

## 10. 结构性N/A

- regulatory_basis：A组48条全部N/A（设计性：无RAG无法规依据可评）；C组46/48 N/A（judge裁量：无RAG时多数回答未给出法规依据结论）；B组2条、D组1条N/A（judge裁量）【来源：04_formal_scoring_results.csv实测 + 05_scoring_QC_report.md】
- skill_workflow：A组48条、B组48条全部N/A（设计性：无Skill可评）【来源：同上】
- 主分析口径common_3d_score（correctness+evidence_use+actionability）不受任何N/A影响：三维192/192完整【来源：08_2x2析因统计_48题_20260822\\01_QC\\analysis_QC.md】

## 11. Evidence use天花板效应（数据事实）

- evidence_use维度：四组满分率均为93.8%（45/48题得2分）；48题中仅4题未满分；A/C组各2题得1分，B/D组各1题得1分；该维度方差接近0【来源：02_descriptive_statistics.csv evidence_use行】
- common_3d_score：A组66.7%观测达满分6/6【来源：statistical_report.md §2】
- correctness维度：A组满分率58.3%（28/48），C组满分率37.5%（18/48）【来源：04_formal_scoring_results.csv实测】

## 12. 统计方法实际执行情况

- PRIMARY：题级contrast单样本t检验（df=47）+ question-level paired bootstrap（10,000次，seed=20260822，每次有放回抽48题、整题ABCD带入）【来源：analysis_manifest.json】
- 交叉验证：MixedLM score ~ RAG*Skill + (1|question_id)，效应编码(±0.5)，点估计与方法A完全一致，无收敛警告【来源：04_factorial_analysis\\mixedlm_common3d.csv】
- 多重比较：5个secondary pairwise contrasts做Holm校正；RAG main/Skill main/Interaction三个预设析因效应独立成family【来源：06_pairwise\\pairwise_holm_common3d.csv】
- 三口径稳健性：common_3d_score / common_3d_percent / normalized_100三口径下Interaction均p<0.05【来源：08_robustness\\robustness_three_scales.csv】
- 敏感性：leave-one-category-out 14次剔除后Interaction均>0且p<0.05【来源：09_评分信度与敏感性检验_20260822\\leave_one_category_out_sensitivity.csv】

## 13. 其他已知边界

- LLM-as-judge为单裁判（qwen3.8-max），无人工专家盲评交叉验证（专家盲评尚未执行）【来源：项目状态】
- normalized_100口径下各组applicable_max不同（8分93条、6分50条、10分49条），横向比较需注明【来源：04_formal_scoring_results.csv applicable_max列】
- 14类task_type中9类n≤3，任务级效应估计精度有限【来源：task_heterogeneity_common3d.csv n_questions列】
"""
(OUT / '07_实验过程与方法边界.md').write_text(t7, encoding='utf-8')

# ============ 08 GPT深度分析输入包 ============
def g(eff, outcome='common_3d_score (0-6)'):
    r = rob[(rob.outcome == outcome) & (rob.effect == eff)].iloc[0]
    return r

def fmt_eff(eff, outcome, unit='分'):
    r = g(eff, outcome)
    src = 'robustness_three_scales.csv' if 'common' in outcome or 'norm' in outcome else 'dimension_decomposition.csv'
    return (f"{r.estimate:+.3f}{unit}（t-CI [{r.CI95_low:.3f}, {r.CI95_high:.3f}]；"
            f"bootstrap-CI [{r.boot_CI95_low:.3f}, {r.boot_CI95_high:.3f}]；p={r.p_value:.4f}；dz={r.cohen_dz:.3f}）"
            f"【来源：{src} / {outcome} / {eff}】")

def dim_eff(eff, dim):
    r = dd[(dd.outcome == f'{dim} (0-2)') & (dd.effect == eff)].iloc[0]
    return (f"{r.estimate:+.3f}分（bootstrap-CI [{r.boot_CI95_low:.3f}, {r.boot_CI95_high:.3f}]；"
            f"p={r.p_value:.4f}；dz={r.cohen_dz:.3f}）【来源：dimension_decomposition.csv / {dim} / {eff}】")

# 典型题10题（去重，按优先级）
seen, t10 = set(), []
for _, r in typical.iterrows():
    if r.question_id not in seen:
        seen.add(r.question_id)
        t10.append(r)
    if len(t10) >= 10:
        break

t10_lines = []
pivot = score.pivot_table(index='question_id', columns='condition', values='c3')
for r in t10:
    q = qle[qle.question_id == r.question_id].iloc[0]
    a4 = pivot.loc[r.question_id]
    t10_lines.append(f"- {r.question_id}（{r.task_type}，{r.category}={r.value}）："
                     f"四组c3得分 A={a4['A']:.0f}/B={a4['B']:.0f}/C={a4['C']:.0f}/D={a4['D']:.0f}；"
                     f"Interaction={q.c3_interaction}；C-A={q.c3_C_minus_A}；D-C={q.c3_D_minus_C}；D-B={q.c3_D_minus_B}"
                     f"【来源：question_level_effects.csv + 04_formal_scoring_results.csv / {r.question_id}】")

# 任务异质性表
het_sorted = het.sort_values('interaction', ascending=False)
het_tbl = ['| task_type | n | A% | B% | C% | D% | RAG_main | Skill_main | Interaction | interaction_boot_CI |',
           '|---|---|---|---|---|---|---|---|---|---|']
for _, r in het_sorted.iterrows():
    het_tbl.append(f"| {r.task_type} | {r.n_questions} | {r.A_mean_pct:.1f} | {r.B_mean_pct:.1f} | {r.C_mean_pct:.1f} | {r.D_mean_pct:.1f} | "
                   f"{r.rag_main:+.2f} | {r.skill_main:+.2f} | {r.interaction:+.2f} | {r.interaction_boot_CI95} |")
het_tbl.append('【来源：task_heterogeneity_common3d.csv 全表（common_3d_score尺度，%列为common_3d_percent）】')

# 描述统计表
desc_tbl = ['| outcome | A | B | C | D |', '|---|---|---|---|---|']
for oc in DIMS3 + ['common_3d_score', 'common_3d_percent', 'normalized_100']:
    row = [oc]
    for c in ['A (LLM)', 'B (LLM+RAG)', 'C (LLM+Skill)', 'D (LLM+RAG+Skill)']:
        r = desc[(desc.outcome == oc) & (desc.condition == c)].iloc[0]
        row.append(f"{r['mean']:.2f}±{r.SD:.2f}")
    desc_tbl.append('| ' + ' | '.join(row) + ' |')
desc_tbl.append('【来源：02_descriptive_statistics.csv（mean±SD，n=48/组）】')

pw_lines = []
for _, r in pw.iterrows():
    pw_lines.append(f"- {r['effect']}：{r.estimate:+.3f}分（CI [{r.CI95_low:.3f}, {r.CI95_high:.3f}]；p={r.p_value:.4f}；"
                    f"Holm p={r.p_holm:.4f}；dz={r.cohen_dz:.3f}；Holm后{'显著' if r['reject_holm_0.05'] else '不显著'}）"
                    f"【来源：pairwise_holm_common3d.csv / {r['effect']}】")

typical_detail = []
for r in t10:
    typical_detail.append(f"- {r.question_id}（{r.task_type}，{r.category}={r.value}）")

t8 = f"""# GPT深度分析输入包：环评LLM RAG×Skill 2×2正式实验

> 用途：供GPT基于以下真实数据完成科研分析（机制判断、Results/Discussion建议）。
> 约束：本文档只提供数据与事实，所有"为什么"由GPT分析；每个关键数字带【来源】标记。
> 配套文件：01-05 xlsx（结构化数据）、06典型题对照（原文摘要）、07方法边界（事实清单）。

# 1 实验设计

- 2×2析因：A=LLM(基线)，B=LLM+RAG，C=LLM+Skill，D=LLM+RAG+Skill；RAG∈{{0,1}}，Skill∈{{0,1}}【来源：01_final_analysis_dataset_v2.xlsx / RAG/Skill列】
- RAG=冻结Top-5证据注入（73源知识库混合检索，B/D共用同一Top-5快照）；Skill=路由的单一主任务审核程序（15个Skill模块库）【来源：新增40题_正式输入冻结_20260820\\input_freeze_manifest.json】
- 模型qwen3.8-max，temperature=0；48个question_id为配对/区组单位（同一题A/B/C/D为重复测量）【来源：02_final_dataset_integrity_report.md §五】
- 评分五维各0/1/2分；主分析结局common_3d_score=correctness+evidence_use+actionability（0-6分），四组共同适用无N/A【来源：01_原21题评分协议复现说明.md】

# 2 样本形成过程

- 61候选（21旧+40新）→ 13题技术失败剔除（complete-case规则，与质量无关）→ 48题 → 48×4=192条【来源：02_final_dataset_integrity_report.md §一/§二】
- 13剔除题：SourceStrength 5/5全退出（prompt最长58k-63k字符）；13/13题失败group含D组（最长prompt条件）【来源：技术失败剔除题清单.csv + 推导】
- 旧21题=报告核查类6种task_type；新27题=工程参数类8种task_type；两类集合零重叠【来源：04_formal_scoring_results.csv / question_source×task_type】

# 3 A/B/C/D总体结果

{chr(10).join(desc_tbl)}

- A组common_3d满分(6/6)比例66.7%；四组evidence_use满分率均93.8%（48题仅4题未满分）【来源：statistical_report.md §2 / 02_descriptive_statistics.csv】
- 四组中A最高(93.06%)、C最低(86.11%)、D回升至91.32%（未回到A水平）【来源：02_descriptive_statistics.csv / common_3d_percent行】

# 4 RAG main effect

- common_3d_score：{fmt_eff('rag_main', 'common_3d_score (0-6)')}
- common_3d_percent：{fmt_eff('rag_main', 'common_3d_percent (0-100)', 'pp')}
- normalized_100：{fmt_eff('rag_main', 'normalized_100 (0-100)', 'pp')}
- 简单效应分解：B-A=-0.083（p=0.522，不显著）；D-C=+0.313（p=0.015，Holm p=0.059）【来源：pairwise_holm_common3d.csv / B-A、D-C】
- MixedLM交叉验证：RAG主效应p=0.206【来源：mixedlm_common3d.csv】

# 5 Skill main effect

- common_3d_score：{fmt_eff('skill_main', 'common_3d_score (0-6)')}
- common_3d_percent：{fmt_eff('skill_main', 'common_3d_percent (0-100)', 'pp')}
- normalized_100：{fmt_eff('skill_main', 'normalized_100 (0-100)', 'pp')}
- 简单效应分解：C-A=-0.417（p=0.00005，Holm p=0.00025，显著）；D-B=-0.021（p=0.868，不显著）【来源：pairwise_holm_common3d.csv / C-A、D-B】
- MixedLM交叉验证：Skill主效应p=0.016【来源：mixedlm_common3d.csv】

# 6 Interaction（D-B-C+A）

- common_3d_score：{fmt_eff('interaction', 'common_3d_score (0-6)')}
- common_3d_percent：{fmt_eff('interaction', 'common_3d_percent (0-100)', 'pp')}
- normalized_100：{fmt_eff('interaction', 'normalized_100 (0-100)', 'pp')}
- 三口径下Interaction均p<0.05（p=0.0016/0.0016/0.0019），方向一致【来源：robustness_three_scales.csv】
- MixedLM交叉验证：Interaction p=0.029【来源：mixedlm_common3d.csv】
- leave-one-category-out：剔除任一task_type后Interaction均>0且p<0.05（14/14次；最保守=剔除Coefficient后+0.326, p=0.0116）【来源：leave_one_category_out_sensitivity.csv】
- 关键背景数值：D-A=-0.104（p=0.452，不显著；D未超越A）【来源：pairwise_holm_common3d.csv / D-A】

# 7 简单效应（5个配对比较，Holm校正family=5）

{chr(10).join(pw_lines)}

# 8 三维分解

- correctness：RAG main {dim_eff('rag_main', 'correctness')}；Skill main {dim_eff('skill_main', 'correctness')}；Interaction {dim_eff('interaction', 'correctness')}
- evidence_use：RAG main {dim_eff('rag_main', 'evidence_use')}；Skill main {dim_eff('skill_main', 'evidence_use')}；Interaction {dim_eff('interaction', 'evidence_use')}（该维度四组满分率93.8%，方差接近0，skill_main与interaction估计值为0）
- actionability：RAG main {dim_eff('rag_main', 'actionability')}；Skill main {dim_eff('skill_main', 'actionability')}；Interaction {dim_eff('interaction', 'actionability')}
- 维度均值（A/B/C/D）：correctness 1.67/1.63/1.42/1.56；evidence_use 1.96/1.98/1.96/1.98；actionability 1.96/1.90/1.79/1.94【来源：02_descriptive_statistics.csv】

# 9 task-type异质性（common_3d_score尺度，按Interaction降序）

{chr(10).join(het_tbl)}

- 正Interaction最大类别：Coefficient(+1.00)、EnvQuality(+1.00)、Emission_固废(+0.80)、Construction(+0.75)【来源：task_heterogeneity_common3d.csv / interaction列】
- 唯一负Interaction类别：V01(-0.40)【来源：同上】
- 9/14类别n≤3，类别级估计精度有限【来源：同上 / n_questions列】

# 10 interaction极端案例（10题，客观记录见06_典型题ABCD对照.md）

{chr(10).join(t10_lines)}

每题完整对照（Gold摘要+A/B/C/D回答摘要+三维评分+judge理由+引用证据条数）见：06_典型题ABCD对照.md【来源：parsed_outputs冻结文件 + 04_formal_scoring_results.csv】

# 11 技术失败与样本边界

- 160任务初始成功119；41失败（HTTP503/500/空响应）；三轮救援后最终13题剔除【来源：正式实验技术失败与样本剔除报告.md】
- SourceStrength 5/5退出（保留率0%）；13/13剔除题失败group含D组【来源：技术失败剔除题清单.csv】
- 剔除与回答质量无关（判定发生在评分前，依据为API技术可用性）【来源：02_final_dataset_integrity_report.md §三】

# 12 评分与统计方法

- judge=qwen3.8-max（temp=0/max_tokens=1800/enable_thinking=False），逐字复用20260812协议；A/B/C/D→R1-R4固定盲化【来源：judge_execution_manifest.json / 01_原21题评分协议复现说明.md】
- judge输入含Gold参考答案与报告金标证据，不含RAG Top-5原文/Skill正文/真实组名【来源：score_48q_formal.py】
- 统计：题级t检验(df=47)+question-level paired bootstrap(10,000次/seed=20260822/整题ABCD带入)；MixedLM交叉验证（效应编码）；Holm仅用于5个pairwise【来源：analysis_manifest.json】
- judge test-retest信度（同一84条旧题回答两轮独立评分）：common_3d ICC=0.786；三维一致率94.0-97.6%；无系统漂移【来源：test_retest_dimension_stats.csv】

# 13 当前所有已知限制（事实清单）

1. SourceStrength题型0%保留，结论不外推至源强核算类任务【来源：02_final_dataset_integrity_report.md】
2. 旧21题与新27题task_type集合零重叠（batch构成差异）【来源：04_formal_scoring_results.csv】
3. 9/14 task_type类别n≤3【来源：task_heterogeneity_common3d.csv】
4. LLM单裁判评分，无人工专家盲评交叉验证【来源：项目状态】
5. evidence_use维度天花板（四组满分率93.8%，方差近0）【来源：02_descriptive_statistics.csv】
6. common_3d强天花板（A组66.7%满分）压缩效应幅度【来源：statistical_report.md §2】
7. normalized_100口径各组applicable_max不同（8分93条/6分50条/10分49条）【来源：04_formal_scoring_results.csv】
8. 3处judge裁量N/A位于B/D组法规维度（PL004_水污.B、PL011_Construction.B/D）【来源：05_scoring_QC_report.md】
9. N/A在regulatory_basis/skill_workflow维度结构性存在（A组法规48N/A、A/B组技能各48N/A），主分析已规避但两维度不能四组并列【来源：05_scoring_QC_report.md】
"""
(OUT / '08_GPT深度分析输入包.md').write_text(t8, encoding='utf-8')
print('07/08 完成')
print('08长度:', len(t8), '字符')
