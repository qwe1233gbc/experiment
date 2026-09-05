# 环境质量数据引用

- 问题数量：3
- 核心答案依据文件：2个
- 实验Top-5实际检索文件（去重）：6个

## 文件夹说明

- `01_核心答案依据文件`：来自第二阶段冻结评价集 `rag_source_ids`，按52源基础库ID解析后，在70源增强库中复制对应同名文件。
- `02_实验Top5实际检索文件`：来自第三阶段 `rag_contexts_frozen.jsonl`，汇总该类问题实际进入B/D组提示词的Top-5来源。
- `问题与文件映射.csv/json`：逐题记录问题、核心依据、实际Top-5命中来源及Skill。

## 题号

- $(@{question_id=PL001_EnvQuality_Q01; project_id=PL001; question=请根据报告引用的环境质量公报及现状数据，判断大气和地表水环境质量现状数据引用是否准确。; reference_answer=1、大气及地表水环境质量引用数据正确；
2、项目大气环境质量引用《佛山市生态环境局顺德分局关于发布2022年度佛山市顺德区生态环境状况公报的通知（佛环顺函〔2023〕26号）》。环评对大气环境质量分析内容与《2022年度佛山市顺德区生态环境状况公报》中大气环境状况描述一致。经检索，截至审核日该地区最新的环境状况公报为《2024年度佛山市顺德区生态环境状况公报》，可供参考。
项目地表水环境质量引用《佛山市生态环境局顺德分局关于发布2022年度佛山市顺德区生态环境状况公报的通知（佛环顺函〔2023〕26号）》。环评对地表水环境质量分析内容与《2022年度佛山市顺德区生态环境状况公报》中地表水环境状况描述一致。经检索，截至审核日该地区最新的环境状况公报为《2024年度佛山市顺德区生态环境状况公报》，可供参考。; audit_type=环境质量数据引用; report_evidence=System.Object[]; report_support_note=人工参考答案的主体判断可由项目报告原文定位支持。 其中“截至审核日最新公报为《2024年度佛山市顺德区生态环境状况公报》”属于人工核验中的外部检索结论，不能仅由该项目报告原文证明。; rag_source_ids=System.Object[]; rag_knowledge_refs=System.Object[]; skill_id=review-eia-environmental-quality-data; manual_policy_files=System.Object[]; basis_status=sufficient; manual_review_required=False; manual_review_reason=; spatial_verification=; evidence_index_status=部分充分; evidence_index_note=补2022年度公报及佛环顺函〔2023〕26号；否则无法独立验证“与2022公报一致”}.question_id)：请根据报告引用的环境质量公报及现状数据，判断大气和地表水环境质量现状数据引用是否准确。
- $(@{question_id=PL002_EnvQuality_Q01; project_id=PL002; question=请根据报告引用的环境质量公报及现状数据，判断大气和地表水环境质量现状数据引用是否准确。; reference_answer=1、大气及地表水环境质量引用数据正确；
2、项目大气环境质量引用《佛山市生态环境局顺德分局关于发布2022年度佛山市顺德区生态环境状况公报的通知（佛环顺函〔2023〕26号）》。环评对大气环境质量分析内容与《2022年度佛山市顺德区生态环境状况公报》中大气环境状况描述一致。经检索，截至审核日该地区最新的环境状况公报为《2024年度佛山市顺德区生态环境状况公报》，可供参考。
项目地表水环境质量引用《佛山市生态环境局顺德分局关于发布2022年度佛山市顺德区生态环境状况公报的通知（佛环顺函〔2023〕26号）》。环评对地表水环境质量分析内容与《2022年度佛山市顺德区生态环境状况公报》中地表水环境状况描述一致。经检索，截至审核日该地区最新的环境状况公报为《2024年度佛山市顺德区生态环境状况公报》，可供参考。; audit_type=环境质量数据引用; report_evidence=System.Object[]; report_support_note=人工参考答案的主体判断可由项目报告原文定位支持。 其中“截至审核日最新公报为《2024年度佛山市顺德区生态环境状况公报》”属于人工核验中的外部检索结论，不能仅由该项目报告原文证明。; rag_source_ids=System.Object[]; rag_knowledge_refs=System.Object[]; skill_id=review-eia-environmental-quality-data; manual_policy_files=System.Object[]; basis_status=sufficient; manual_review_required=False; manual_review_reason=; spatial_verification=; evidence_index_status=部分充分; evidence_index_note=同PL001环境质量题：缺2022公报和正式通知}.question_id)：请根据报告引用的环境质量公报及现状数据，判断大气和地表水环境质量现状数据引用是否准确。
- $(@{question_id=PL006_EnvQuality_Q01; project_id=PL006; question=请根据报告引用的环境质量公报及现状数据，判断大气和地表水环境质量现状数据引用是否准确。; reference_answer=1、大气及地表水环境质量引用数据正确（报告公报名称及文号存在笔误）；
2、项目大气环境质量引用《佛山市生态环境局顺德分局关于发布2022年度佛山市顺德区生态环境状况公报的通知》（佛环顺函〔2023〕26号）。环评对大气环境质量分析内容与《2022年度佛山市顺德区生态环境状况公报》中大气环境状况描述一致。但报告中公报名称误写为'环境质量状况公报'（正确为'生态环境状况公报'，缺'生态'二字），且多数引用未标注文号，个别处文号误写为'佛顺环函〔2023〕26号'（正确为'佛环顺函〔2023〕26号'），需人工核实更正。经检索，截至审核日该地区最新的环境状况公报为《2024年度佛山市顺德区生态环境状况公报》，可供参考。
项目地表水环境质量引用《佛山市生态环境局顺德分局关于发布2022年度佛山市顺德区生态环境状况公报的通知》（佛环顺函〔2023〕26号）。环评对地表水环境质量分析内容与《2022年度佛山市顺德区生态环境状况公报》中地表水环境状况描述一致。但报告中公报名称及文号存在笔误（详见大气部分说明），需人工核实更正。经检索，截至审核日该地区最新的环境状况公报为《2024年度佛山市顺德区生态环境状况公报》，可供参考。; audit_type=环境质量数据引用; report_evidence=System.Object[]; report_support_note=人工参考答案的主体判断可由项目报告原文定位支持。 其中“截至审核日最新公报为《2024年度佛山市顺德区生态环境状况公报》”属于人工核验中的外部检索结论，不能仅由该项目报告原文证明。 PL006报告原文能够直接定位到“环境质量状况公报”和“佛顺环函〔2023〕26号”等写法；其规范名称/正确文号来自人工核验答案。; rag_source_ids=System.Object[]; rag_knowledge_refs=System.Object[]; skill_id=review-eia-environmental-quality-data; manual_policy_files=System.Object[]; basis_status=sufficient; manual_review_required=False; manual_review_reason=; spatial_verification=; evidence_index_status=部分充分; evidence_index_note=当前RAG不能证明正确名称和正确文号；补2022公报及佛环顺函〔2023〕26号正式通知}.question_id)：请根据报告引用的环境质量公报及现状数据，判断大气和地表水环境质量现状数据引用是否准确。
