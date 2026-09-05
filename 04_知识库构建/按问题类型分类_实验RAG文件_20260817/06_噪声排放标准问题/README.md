# 噪声排放标准

- 问题数量：4
- 核心答案依据文件：2个
- 实验Top-5实际检索文件（去重）：10个

## 文件夹说明

- `01_核心答案依据文件`：来自第二阶段冻结评价集 `rag_source_ids`，按52源基础库ID解析后，在70源增强库中复制对应同名文件。
- `02_实验Top5实际检索文件`：来自第三阶段 `rag_contexts_frozen.jsonl`，汇总该类问题实际进入B/D组提示词的Top-5来源。
- `问题与文件映射.csv/json`：逐题记录问题、核心依据、实际Top-5命中来源及Skill。

## 题号

- $(@{question_id=PL002_Emission_噪声; project_id=PL002; question=请根据项目所属声环境功能区类别，判断噪声排放标准选取是否合理。要求总结声功能区类型、厂界执行标准（GB12348-2008）及昼夜限值，并与环评编制内容进行一致性分析。; reference_answer=1、噪声排放标准中执行标准与排放限值内容：无误；
2、具体分析：项目厂界执行GB12348-2008中3类标准（昼间≤65dB(A)、夜间≤55dB(A)），与项目所在的工业区声功能区划相符。; audit_type=噪声排放标准; report_evidence=System.Object[]; report_support_note=人工参考答案的主体判断可由项目报告原文定位支持。; rag_source_ids=System.Object[]; rag_knowledge_refs=System.Object[]; skill_id=review-eia-pollutant-discharge-standards; manual_policy_files=System.Object[]; basis_status=sufficient; manual_review_required=False; manual_review_reason=; spatial_verification=; evidence_index_status=部分充分; evidence_index_note=GB12348限值充分；项目确属3类区仍缺佛山声功能区划外部依据}.question_id)：请根据项目所属声环境功能区类别，判断噪声排放标准选取是否合理。要求总结声功能区类型、厂界执行标准（GB12348-2008）及昼夜限值，并与环评编制内容进行一致性分析。
- $(@{question_id=PL003_Emission_噪声; project_id=PL003; question=请根据项目所属声环境功能区类别，判断噪声排放标准选取是否合理。要求总结声功能区类型、厂界执行标准（GB12348-2008）及昼夜限值，并与环评编制内容进行一致性分析。; reference_answer=1、噪声排放标准中执行标准与排放限值内容：无误；
2、具体分析：项目边界噪声执行GB12348-2008中3类区标准，与工业区声功能区划相符。; audit_type=噪声排放标准; report_evidence=System.Object[]; report_support_note=人工参考答案的主体判断可由项目报告原文定位支持。; rag_source_ids=System.Object[]; rag_knowledge_refs=System.Object[]; skill_id=review-eia-pollutant-discharge-standards; manual_policy_files=System.Object[]; basis_status=sufficient; manual_review_required=False; manual_review_reason=; spatial_verification=; evidence_index_status=部分充分; evidence_index_note=标准限值可核验，3类功能区归属仍需佛山声功能区划}.question_id)：请根据项目所属声环境功能区类别，判断噪声排放标准选取是否合理。要求总结声功能区类型、厂界执行标准（GB12348-2008）及昼夜限值，并与环评编制内容进行一致性分析。
- $(@{question_id=PL004_Emission_噪声; project_id=PL004; question=请根据项目所属声环境功能区类别，判断噪声排放标准选取是否合理。要求总结声功能区类型、厂界执行标准（GB12348-2008）及昼夜限值，并与环评编制内容进行一致性分析。; reference_answer=1、噪声排放标准中执行标准与排放限值内容：无误；
2、具体分析：报告引用了《佛山市声环境功能区划》（佛环[2024]1号），明确项目位置属于3321杏坛东部工业区片区，厂界执行GB12348-2008中3类标准（昼间≤65dB(A)、夜间≤55dB(A)），声功能区划依据充分，标准选取准确。; audit_type=噪声排放标准; report_evidence=System.Object[]; report_support_note=人工参考答案的主体判断可由项目报告原文定位支持。; rag_source_ids=System.Object[]; rag_knowledge_refs=System.Object[]; skill_id=review-eia-pollutant-discharge-standards; manual_policy_files=System.Object[]; basis_status=sufficient; manual_review_required=False; manual_review_reason=; spatial_verification=; evidence_index_status=部分充分; evidence_index_note=补佛环〔2024〕1号正文及3321片区图层，才能外部验证3类区归属}.question_id)：请根据项目所属声环境功能区类别，判断噪声排放标准选取是否合理。要求总结声功能区类型、厂界执行标准（GB12348-2008）及昼夜限值，并与环评编制内容进行一致性分析。
- $(@{question_id=PL005_Emission_噪声; project_id=PL005; question=请根据项目所属声环境功能区类别，判断噪声排放标准选取是否合理。要求总结声功能区类型、厂界执行标准（GB12348-2008）及昼夜限值，并与环评编制内容进行一致性分析。; reference_answer=1、噪声排放标准中执行标准与排放限值内容：无误；
2、具体分析：项目厂界执行GB12348-2008中3类标准（昼间≤65dB(A)、夜间≤55dB(A)），与项目所在的工业区声功能区划相符。; audit_type=噪声排放标准; report_evidence=System.Object[]; report_support_note=人工参考答案的主体判断可由项目报告原文定位支持。; rag_source_ids=System.Object[]; rag_knowledge_refs=System.Object[]; skill_id=review-eia-pollutant-discharge-standards; manual_policy_files=System.Object[]; basis_status=sufficient; manual_review_required=False; manual_review_reason=; spatial_verification=; evidence_index_status=部分充分; evidence_index_note=补佛山声功能区划，验证项目位置与3类区对应关系}.question_id)：请根据项目所属声环境功能区类别，判断噪声排放标准选取是否合理。要求总结声功能区类型、厂界执行标准（GB12348-2008）及昼夜限值，并与环评编制内容进行一致性分析。
