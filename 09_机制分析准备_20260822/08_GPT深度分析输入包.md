# GPT深度分析输入包：环评LLM RAG×Skill 2×2正式实验

> 用途：供GPT基于以下真实数据完成科研分析（机制判断、Results/Discussion建议）。
> 约束：本文档只提供数据与事实，所有"为什么"由GPT分析；每个关键数字带【来源】标记。
> 配套文件：01-05 xlsx（结构化数据）、06典型题对照（原文摘要）、07方法边界（事实清单）。

# 1 实验设计

- 2×2析因：A=LLM(基线)，B=LLM+RAG，C=LLM+Skill，D=LLM+RAG+Skill；RAG∈{0,1}，Skill∈{0,1}【来源：01_final_analysis_dataset_v2.xlsx / RAG/Skill列】
- RAG=冻结Top-5证据注入（73源知识库混合检索，B/D共用同一Top-5快照）；Skill=路由的单一主任务审核程序（15个Skill模块库）【来源：新增40题_正式输入冻结_20260820\input_freeze_manifest.json】
- 模型qwen3.8-max，temperature=0；48个question_id为配对/区组单位（同一题A/B/C/D为重复测量）【来源：02_final_dataset_integrity_report.md §五】
- 评分五维各0/1/2分；主分析结局common_3d_score=correctness+evidence_use+actionability（0-6分），四组共同适用无N/A【来源：01_原21题评分协议复现说明.md】

# 2 样本形成过程

- 61候选（21旧+40新）→ 13题技术失败剔除（complete-case规则，与质量无关）→ 48题 → 48×4=192条【来源：02_final_dataset_integrity_report.md §一/§二】
- 13剔除题：SourceStrength 5/5全退出（prompt最长58k-63k字符）；13/13题失败group含D组（最长prompt条件）【来源：技术失败剔除题清单.csv + 推导】
- 旧21题=报告核查类6种task_type；新27题=工程参数类8种task_type；两类集合零重叠【来源：04_formal_scoring_results.csv / question_source×task_type】

# 3 A/B/C/D总体结果

| outcome | A | B | C | D |
|---|---|---|---|---|
| correctness | 1.67±0.52 | 1.62±0.49 | 1.42±0.54 | 1.56±0.54 |
| evidence_use | 1.96±0.20 | 1.98±0.14 | 1.96±0.20 | 1.98±0.14 |
| actionability | 1.96±0.20 | 1.90±0.37 | 1.79±0.46 | 1.94±0.24 |
| common_3d_score | 5.58±0.68 | 5.50±0.71 | 5.17±0.88 | 5.48±0.65 |
| common_3d_percent | 93.06±11.32 | 91.67±11.91 | 86.11±14.72 | 91.32±10.87 |
| normalized_100 | 93.06±11.32 | 91.75±10.82 | 89.01±12.67 | 93.33±7.53 |
【来源：02_descriptive_statistics.csv（mean±SD，n=48/组）】

- A组common_3d满分(6/6)比例66.7%；四组evidence_use满分率均93.8%（48题仅4题未满分）【来源：statistical_report.md §2 / 02_descriptive_statistics.csv】
- 四组中A最高(93.06%)、C最低(86.11%)、D回升至91.32%（未回到A水平）【来源：02_descriptive_statistics.csv / common_3d_percent行】

# 4 RAG main effect

- common_3d_score：+0.115分（t-CI [-0.110, 0.339]；bootstrap-CI [-0.104, 0.344]；p=0.3100；dz=0.148）【来源：robustness_three_scales.csv / common_3d_score (0-6) / rag_main】
- common_3d_percent：+1.910pp（t-CI [-1.834, 5.653]；bootstrap-CI [-1.736, 5.729]；p=0.3100；dz=0.148）【来源：robustness_three_scales.csv / common_3d_percent (0-100) / rag_main】
- normalized_100：+1.511pp（t-CI [-2.184, 5.205]；bootstrap-CI [-1.901, 5.183]；p=0.4148；dz=0.119）【来源：robustness_three_scales.csv / normalized_100 (0-100) / rag_main】
- 简单效应分解：B-A=-0.083（p=0.522，不显著）；D-C=+0.313（p=0.015，Holm p=0.059）【来源：pairwise_holm_common3d.csv / B-A、D-C】
- MixedLM交叉验证：RAG主效应p=0.206【来源：mixedlm_common3d.csv】

# 5 Skill main effect

- common_3d_score：-0.219分（t-CI [-0.406, -0.032]；bootstrap-CI [-0.406, -0.042]；p=0.0227；dz=-0.340）【来源：robustness_three_scales.csv / common_3d_score (0-6) / skill_main】
- common_3d_percent：-3.646pp（t-CI [-6.759, -0.532]；bootstrap-CI [-6.771, -0.694]；p=0.0227；dz=-0.340）【来源：robustness_three_scales.csv / common_3d_percent (0-100) / skill_main】
- normalized_100：-1.232pp（t-CI [-3.715, 1.250]；bootstrap-CI [-3.646, 1.137]；p=0.3231；dz=-0.144）【来源：robustness_three_scales.csv / normalized_100 (0-100) / skill_main】
- 简单效应分解：C-A=-0.417（p=0.00005，Holm p=0.00025，显著）；D-B=-0.021（p=0.868，不显著）【来源：pairwise_holm_common3d.csv / C-A、D-B】
- MixedLM交叉验证：Skill主效应p=0.016【来源：mixedlm_common3d.csv】

# 6 Interaction（D-B-C+A）

- common_3d_score：+0.396分（t-CI [0.158, 0.633]；bootstrap-CI [0.167, 0.625]；p=0.0016；dz=0.484）【来源：robustness_three_scales.csv / common_3d_score (0-6) / interaction】
- common_3d_percent：+6.597pp（t-CI [2.637, 10.558]；bootstrap-CI [2.778, 10.417]；p=0.0016；dz=0.484）【来源：robustness_three_scales.csv / common_3d_percent (0-100) / interaction】
- normalized_100：+5.624pp（t-CI [2.183, 9.065]；bootstrap-CI [2.429, 9.096]；p=0.0019；dz=0.475）【来源：robustness_three_scales.csv / normalized_100 (0-100) / interaction】
- 三口径下Interaction均p<0.05（p=0.0016/0.0016/0.0019），方向一致【来源：robustness_three_scales.csv】
- MixedLM交叉验证：Interaction p=0.029【来源：mixedlm_common3d.csv】
- leave-one-category-out：剔除任一task_type后Interaction均>0且p<0.05（14/14次；最保守=剔除Coefficient后+0.326, p=0.0116）【来源：leave_one_category_out_sensitivity.csv】
- 关键背景数值：D-A=-0.104（p=0.452，不显著；D未超越A）【来源：pairwise_holm_common3d.csv / D-A】

# 7 简单效应（5个配对比较，Holm校正family=5）

- B - A：-0.083分（CI [-0.343, 0.177]；p=0.5221；Holm p=1.0000；dz=-0.093；Holm后不显著）【来源：pairwise_holm_common3d.csv / B - A】
- C - A：-0.417分（CI [-0.605, -0.229]；p=0.0001；Holm p=0.0003；dz=-0.644；Holm后显著）【来源：pairwise_holm_common3d.csv / C - A】
- D - A：-0.104分（CI [-0.380, 0.172]；p=0.4516；Holm p=1.0000；dz=-0.110；Holm后不显著）【来源：pairwise_holm_common3d.csv / D - A】
- D - B：-0.021分（CI [-0.271, 0.230]；p=0.8678；Holm p=1.0000；dz=-0.024；Holm后不显著）【来源：pairwise_holm_common3d.csv / D - B】
- D - C：+0.312分（CI [0.064, 0.561]；p=0.0147；Holm p=0.0587；dz=0.366；Holm后不显著）【来源：pairwise_holm_common3d.csv / D - C】

# 8 三维分解

- correctness：RAG main +0.052分（bootstrap-CI [-0.094, 0.208]；p=0.4980；dz=0.099）【来源：dimension_decomposition.csv / correctness / rag_main】；Skill main -0.156分（bootstrap-CI [-0.281, -0.042]；p=0.0175；dz=-0.356）【来源：dimension_decomposition.csv / correctness / skill_main】；Interaction +0.188分（bootstrap-CI [0.042, 0.333]；p=0.0110；dz=0.382）【来源：dimension_decomposition.csv / correctness / interaction】
- evidence_use：RAG main +0.021分（bootstrap-CI [0.000, 0.062]；p=0.3224；dz=0.144）【来源：dimension_decomposition.csv / evidence_use / rag_main】；Skill main +0.000分（bootstrap-CI [0.000, 0.000]；p=nan；dz=nan）【来源：dimension_decomposition.csv / evidence_use / skill_main】；Interaction +0.000分（bootstrap-CI [0.000, 0.000]；p=nan；dz=nan）【来源：dimension_decomposition.csv / evidence_use / interaction】（该维度四组满分率93.8%，方差接近0，skill_main与interaction估计值为0）
- actionability：RAG main +0.042分（bootstrap-CI [-0.062, 0.146]；p=0.4386；dz=0.113）【来源：dimension_decomposition.csv / actionability / rag_main】；Skill main -0.062分（bootstrap-CI [-0.146, 0.021]；p=0.1595；dz=-0.206）【来源：dimension_decomposition.csv / actionability / skill_main】；Interaction +0.208分（bootstrap-CI [0.083, 0.354]；p=0.0062；dz=0.414）【来源：dimension_decomposition.csv / actionability / interaction】
- 维度均值（A/B/C/D）：correctness 1.67/1.63/1.42/1.56；evidence_use 1.96/1.98/1.96/1.98；actionability 1.96/1.90/1.79/1.94【来源：02_descriptive_statistics.csv】

# 9 task-type异质性（common_3d_score尺度，按Interaction降序）

| task_type | n | A% | B% | C% | D% | RAG_main | Skill_main | Interaction | interaction_boot_CI |
|---|---|---|---|---|---|---|---|---|---|
| Coefficient | 5 | 93.3 | 93.3 | 76.7 | 93.3 | +0.50 | -0.50 | +1.00 | [0.40, 1.60] |
| EnvQuality | 3 | 77.8 | 83.3 | 77.8 | 100.0 | +0.83 | +0.50 | +1.00 | [0.00, 3.00] |
| Emission_固废 | 5 | 96.7 | 83.3 | 93.3 | 93.3 | -0.40 | +0.20 | +0.80 | [0.20, 1.40] |
| Construction | 4 | 100.0 | 87.5 | 91.7 | 91.7 | -0.38 | -0.12 | +0.75 | [0.00, 1.50] |
| CaptureAirflow | 5 | 93.3 | 86.7 | 83.3 | 86.7 | -0.10 | -0.30 | +0.60 | [0.00, 1.40] |
| VOCSTotal | 2 | 100.0 | 91.7 | 100.0 | 100.0 | -0.25 | +0.25 | +0.50 | n<3, CI not computed |
| DesignAirflow | 3 | 77.8 | 88.9 | 66.7 | 83.3 | +0.83 | -0.50 | +0.33 | [0.00, 1.00] |
| CaptureEfficiency | 4 | 95.8 | 100.0 | 79.2 | 87.5 | +0.38 | -0.88 | +0.25 | [0.00, 0.75] |
| Emission_水污 | 3 | 77.8 | 94.4 | 77.8 | 94.4 | +1.00 | +0.00 | +0.00 | [0.00, 0.00] |
| Emission_噪声 | 4 | 100.0 | 100.0 | 87.5 | 87.5 | +0.00 | -0.75 | +0.00 | [0.00, 0.00] |
| HazardousWaste | 2 | 100.0 | 100.0 | 100.0 | 100.0 | +0.00 | +0.00 | +0.00 | n<3, CI not computed |
| ActivatedCarbon | 2 | 91.7 | 91.7 | 91.7 | 91.7 | +0.00 | +0.00 | +0.00 | n<3, CI not computed |
| Emission_大气 | 1 | 100.0 | 100.0 | 100.0 | 100.0 | +0.00 | +0.00 | +0.00 | n<3, CI not computed |
| V01 | 5 | 96.7 | 93.3 | 96.7 | 86.7 | -0.40 | -0.20 | -0.40 | [-1.20, 0.00] |
【来源：task_heterogeneity_common3d.csv 全表（common_3d_score尺度，%列为common_3d_percent）】

- 正Interaction最大类别：Coefficient(+1.00)、EnvQuality(+1.00)、Emission_固废(+0.80)、Construction(+0.75)【来源：task_heterogeneity_common3d.csv / interaction列】
- 唯一负Interaction类别：V01(-0.40)【来源：同上】
- 9/14类别n≤3，类别级估计精度有限【来源：同上 / n_questions列】

# 10 interaction极端案例（10题，客观记录见06_典型题ABCD对照.md）

- PL006_EnvQuality_Q01（EnvQuality，A. Interaction最高的5题=3）：四组c3得分 A=4/B=3/C=4/D=6；Interaction=3；C-A=0；D-C=2；D-B=3【来源：question_level_effects.csv + 04_formal_scoring_results.csv / PL006_EnvQuality_Q01】
- PL010_Coefficient_Q01（Coefficient，A. Interaction最高的5题=2）：四组c3得分 A=6/B=6/C=4/D=6；Interaction=2；C-A=-2；D-C=2；D-B=0【来源：question_level_effects.csv + 04_formal_scoring_results.csv / PL010_Coefficient_Q01】
- PL005_Emission_固体（Emission_固废，A. Interaction最高的5题=2）：四组c3得分 A=6/B=4/C=6/D=6；Interaction=2；C-A=0；D-C=0；D-B=2【来源：question_level_effects.csv + 04_formal_scoring_results.csv / PL005_Emission_固体】
- PL011_Construction_Q01（Construction，A. Interaction最高的5题=2）：四组c3得分 A=6/B=4/C=6/D=6；Interaction=2；C-A=0；D-C=0；D-B=2【来源：question_level_effects.csv + 04_formal_scoring_results.csv / PL011_Construction_Q01】
- PL014_CaptureAirflow_Q01（CaptureAirflow，A. Interaction最高的5题=2）：四组c3得分 A=6/B=4/C=4/D=4；Interaction=2；C-A=-2；D-C=0；D-B=0【来源：question_level_effects.csv + 04_formal_scoring_results.csv / PL014_CaptureAirflow_Q01】
- PL004_V01_Q01（V01，B. Interaction最低的5题=-2）：四组c3得分 A=6/B=6/C=6/D=4；Interaction=-2；C-A=0；D-C=-2；D-B=-2【来源：question_level_effects.csv + 04_formal_scoring_results.csv / PL004_V01_Q01】
- PL001_EnvQuality_Q01（EnvQuality，B. Interaction最低的5题=0）：四组c3得分 A=5/B=6/C=5/D=6；Interaction=0；C-A=0；D-C=1；D-B=0【来源：question_level_effects.csv + 04_formal_scoring_results.csv / PL001_EnvQuality_Q01】
- PL002_Emission_噪声（Emission_噪声，B. Interaction最低的5题=0）：四组c3得分 A=6/B=6/C=6/D=6；Interaction=0；C-A=0；D-C=0；D-B=0【来源：question_level_effects.csv + 04_formal_scoring_results.csv / PL002_Emission_噪声】
- PL001_V01_Q01（V01，B. Interaction最低的5题=0）：四组c3得分 A=6/B=6/C=6/D=6；Interaction=0；C-A=0；D-C=0；D-B=0【来源：question_level_effects.csv + 04_formal_scoring_results.csv / PL001_V01_Q01】
- PL002_EnvQuality_Q01（EnvQuality，B. Interaction最低的5题=0）：四组c3得分 A=5/B=6/C=5/D=6；Interaction=0；C-A=0；D-C=1；D-B=0【来源：question_level_effects.csv + 04_formal_scoring_results.csv / PL002_EnvQuality_Q01】

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
