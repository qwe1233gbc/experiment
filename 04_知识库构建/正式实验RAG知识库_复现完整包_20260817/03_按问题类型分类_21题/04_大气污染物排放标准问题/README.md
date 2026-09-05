# 大气污染物排放标准

- 问题数量：1
- 核心答案依据文件：3个
- 实验Top-5实际检索文件（去重）：5个

## 文件夹说明

- `01_核心答案依据文件`：来自第二阶段冻结评价集 `rag_source_ids`，按52源基础库ID解析后，在70源增强库中复制对应同名文件。
- `02_实验Top5实际检索文件`：来自第三阶段 `rag_contexts_frozen.jsonl`，汇总该类问题实际进入B/D组提示词的Top-5来源。
- `问题与文件映射.csv/json`：逐题记录问题、核心依据、实际Top-5命中来源及Skill。

## 题号

- $(@{question_id=PL002_Emission_大气; project_id=PL002; question=请根据项目行业类别、生产工艺和污染因子，判断大气污染物排放标准选取是否合理。要求分析：污染源覆盖是否完整（列出所有大气污染源及对应标准），是否存在缺漏的污染源或标准。; reference_answer=1、大气污染物排放标准判定结论：无误（污染源分析内容完整）；
2、具体分析：混料、破碎工序颗粒物执行GB31572-2015表9企业边界大气污染物浓度限值，符合合成树脂工业标准适用范围。挤出、抽检工序非甲烷总烃执行GB31572-2015表5大气污染物特别排放限值及表9企业边界浓度限值，顺德区属珠三角重点区域，执行特别排放限值合理。臭气浓度执行GB14554-93表2和表1二级新扩改建标准，合理。厂区内VOCs无组织排放执行DB44/2367-2022表3，合理。各污染因子标准选取完整、适用。; audit_type=大气污染物排放标准; report_evidence=System.Object[]; report_support_note=人工参考答案的主体判断可由项目报告原文定位支持。; rag_source_ids=System.Object[]; rag_knowledge_refs=System.Object[]; skill_id=review-eia-pollutant-discharge-standards; manual_policy_files=System.Object[]; basis_status=sufficient; manual_review_required=False; manual_review_reason=; spatial_verification=; evidence_index_status=充分; evidence_index_note=需分别核验颗粒物、NMHC、臭气和厂区内VOCs；不得把四项合成一次模糊检索}.question_id)：请根据项目行业类别、生产工艺和污染因子，判断大气污染物排放标准选取是否合理。要求分析：污染源覆盖是否完整（列出所有大气污染源及对应标准），是否存在缺漏的污染源或标准。
