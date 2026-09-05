# 40题 Skill 路由 dry-run 最终验收报告（危废Skill正式版本统一后复验）

- 生成时间：2026-08-20T13:30:50.183017+00:00
- 题目数：40
- 正式Skill库：E:\实验文件整理_按论文逻辑\04_知识库构建\四层架构_正式库\04_Skill检索路由_15个Skill
- 冻结RAG：E:\实验文件整理_按论文逻辑\05_QA测试集与样本\40题冻结RAG快照_v3_1_20260820
- 危废Skill正式版本：A版 `ead69b4f…`（四层架构_正式库）；B版 `41fb4b13…` 标记为非正式同步副本

## 自动验收
- 40_questions: True
- unique_question_ids: True
- all_skill_files_exist: True
- all_skill_sha_recorded: True
- nine_skills_used: True
- routing_consistent_all: True
- applicability_all: True
- cd_control_all: True
- pl007_008_all: True
- no_gold_in_prompt: True
- c_has_no_rag: True
- d_uses_frozen_rag: True
- same_skill_same_version: True
- each_skill_used_ge1: True
- hazardous_4_use_A: True
- other_36_unchanged: True
- skill_version_conflict: 0
- kb81_non_formal_sync_copy: {'note': '81源库证据增强版物理副本为B版(41fb4b13)，已标记为非正式同步副本/不用于本轮正式实验；未删除、未修改', 'divergent_skills': ['review-eia-hazardous-waste-identification']}

## 9类Skill实际调用分布
- calculate-eia-exhaust-capture-airflow: 5题
- calculate-eia-pollutant-source-strength: 5题
- review-eia-activated-carbon-parameters: 4题
- review-eia-construction-content-completeness: 5题
- review-eia-exhaust-capture-efficiency: 4题
- review-eia-exhaust-design-airflow: 4题
- review-eia-hazardous-waste-identification: 4题
- review-eia-pollutant-coefficient-applicability: 5题
- review-eia-vocs-total-control: 4题

## 人工抽查建议（12题）
- PL011_Construction_Q01（建设内容完整性 → review-eia-construction-content-completeness）
- PL006_Construction_Q01（建设内容完整性 → review-eia-construction-content-completeness）
- PL009_Construction_Q01（建设内容完整性 → review-eia-construction-content-completeness）
- PL006_SourceStrength_Q01（污染源强定量核算 → calculate-eia-pollutant-source-strength）
- PL009_Coefficient_Q01（产污系数适用性 → review-eia-pollutant-coefficient-applicability）
- PL010_CaptureAirflow_Q01（废气收集形式与理论排气量 → calculate-eia-exhaust-capture-airflow）
- PL007_DesignAirflow_Q01（废气设计风量 → review-eia-exhaust-design-airflow）
- PL006_CaptureEfficiency_Q01（废气收集效率 → review-eia-exhaust-capture-efficiency）
- PL006_ActivatedCarbon_Q01（活性炭治理设施参数 → review-eia-activated-carbon-parameters）
- PL011_HazardousWaste_Q01（危险废物识别 → review-eia-hazardous-waste-identification）
- PL008_VOCSTotal_Q01（VOCs总量控制与一致性 → review-eia-vocs-total-control）
- PL007_SourceStrength_Q01（污染源强定量核算 → calculate-eia-pollutant-source-strength）

## 已知观察项
- 81源库证据增强版物理副本（B版）与正式库A版SHA不一致，已在本次正式版本统一中标记为“非正式同步副本/不用于本轮正式实验”；未删除、未修改该副本。
- 21题C/D prompt曾使用legacy skill路径；本次40题使用当前正式15个Skill库（四层架构_正式库）。
- 本dry-run报告上下文以v3.1证据窗口excerpt构建；正式冻结时报告上下文可按21题build_context机制扩展。

## 结论
**dry-run状态：PASS**
40/40路由成功、危废4题全部切换A版、其他36题零变化、Skill版本冲突=0、C/D控制变量40/40正确；可以进入第四步：冻结A/B/C/D正式输入。
