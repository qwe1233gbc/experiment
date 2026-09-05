# 国民经济行业分类

- 问题数量：4
- 核心答案依据文件：2个
- 实验Top-5实际检索文件（去重）：9个

## 文件夹说明

- `01_核心答案依据文件`：来自第二阶段冻结评价集 `rag_source_ids`，按52源基础库ID解析后，在70源增强库中复制对应同名文件。
- `02_实验Top5实际检索文件`：来自第三阶段 `rag_contexts_frozen.jsonl`，汇总该类问题实际进入B/D组提示词的Top-5来源。
- `问题与文件映射.csv/json`：逐题记录问题、核心依据、实际Top-5命中来源及Skill。

## 题号

- $(@{question_id=PL001_V01_Q01; project_id=PL001; question=请结合项目产品、原辅材料和生产工艺，判断该报告行业类别是否基本合理。; reference_answer=1、国民经济行业类型判定结论：正确；
2、具体分析：根据项目概况，本项目主要通过调胶、涂布、复合熟化、印刷和收卷等生产工艺，生产保护纸和保护膜。经识别，国民经济行业类别为C2223加工纸制造、C2921塑料薄膜制造，与项目填报的国民经济行业类别C2223加工纸制造、C2921塑料薄膜制造一致。; audit_type=国民经济行业分类; report_evidence=System.Object[]; report_support_note=人工参考答案的主体判断可由项目报告原文定位支持。; rag_source_ids=System.Object[]; rag_knowledge_refs=System.Object[]; skill_id=review-eia-industry-classification; manual_policy_files=System.Object[]; basis_status=sufficient; manual_review_required=False; manual_review_reason=; spatial_verification=; evidence_index_status=充分; evidence_index_note=需同时使用产品、涂布/复合工艺，不能只按报告已填代码返回结论}.question_id)：请结合项目产品、原辅材料和生产工艺，判断该报告行业类别是否基本合理。
- $(@{question_id=PL002_V01_Q01; project_id=PL002; question=请结合项目产品、原辅材料和生产工艺，判断该报告是否适合作为塑胶行业种子问答样本，并判断行业类别是否基本合理。; reference_answer=1、国民经济行业类型判定结论：正确；
2、具体分析：根据项目概况，本项目主要通过配料、混料、双螺杆熔融挤出、冷却和切粒等生产工艺，生产改性塑料粒。经识别，国民经济行业类别为C2929塑料零件及其他塑料制品制造，与项目填报的国民经济行业类别C2929塑料零件及其他塑料制品制造一致。; audit_type=国民经济行业分类; report_evidence=System.Object[]; report_support_note=人工参考答案的主体判断可由项目报告原文定位支持。; rag_source_ids=System.Object[]; rag_knowledge_refs=System.Object[]; skill_id=review-eia-industry-classification; manual_policy_files=System.Object[]; basis_status=sufficient; manual_review_required=False; manual_review_reason=; spatial_verification=; evidence_index_status=充分; evidence_index_note=以改性塑料粒、熔融挤出和切粒活动构造查询}.question_id)：请结合项目产品、原辅材料和生产工艺，判断该报告是否适合作为塑胶行业种子问答样本，并判断行业类别是否基本合理。
- $(@{question_id=PL003_V01_Q01; project_id=PL003; question=请结合项目产品、原辅材料和生产工艺，判断该报告行业类别是否基本合理。; reference_answer=1、国民经济行业类型判定结论：正确；
2、具体分析：根据项目概况，本项目主要通过混料、吹膜、涂布、烘干、分切、复卷和检验等生产工艺，生产塑料薄膜。经识别，国民经济行业类别为C2921塑料薄膜制造，与项目填报的国民经济行业类别C2921塑料薄膜制造一致。; audit_type=国民经济行业分类; report_evidence=System.Object[]; report_support_note=人工参考答案的主体判断可由项目报告原文定位支持。; rag_source_ids=System.Object[]; rag_knowledge_refs=System.Object[]; skill_id=review-eia-industry-classification; manual_policy_files=System.Object[]; basis_status=sufficient; manual_review_required=False; manual_review_reason=; spatial_verification=; evidence_index_status=充分; evidence_index_note=以塑料薄膜、吹膜、涂布、分切为事实链}.question_id)：请结合项目产品、原辅材料和生产工艺，判断该报告行业类别是否基本合理。
- $(@{question_id=PL004_V01_Q01; project_id=PL004; question=请结合项目产品、原辅材料和生产工艺，判断该报告行业类别是否基本合理。; reference_answer=1、国民经济行业类型判定结论：正确；
2、具体分析：根据项目概况，本项目主要通过投料、混料、双螺杆熔融挤出、水下切粒和筛选等生产工艺，生产改性SEBS塑料粒。经识别，国民经济行业类别为C2929塑料零件及其他塑料制品制造，与项目填报的国民经济行业类别C2929塑料零件及其他塑料制品制造一致。; audit_type=国民经济行业分类; report_evidence=System.Object[]; report_support_note=人工参考答案的主体判断可由项目报告原文定位支持。; rag_source_ids=System.Object[]; rag_knowledge_refs=System.Object[]; skill_id=review-eia-industry-classification; manual_policy_files=System.Object[]; basis_status=sufficient; manual_review_required=False; manual_review_reason=; spatial_verification=; evidence_index_status=充分; evidence_index_note=以改性SEBS塑料粒、熔融挤出、水下切粒为事实链}.question_id)：请结合项目产品、原辅材料和生产工艺，判断该报告行业类别是否基本合理。
