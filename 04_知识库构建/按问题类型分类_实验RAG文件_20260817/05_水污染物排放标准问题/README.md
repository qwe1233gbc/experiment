# 水污染物排放标准

- 问题数量：3
- 核心答案依据文件：3个
- 实验Top-5实际检索文件（去重）：9个

## 文件夹说明

- `01_核心答案依据文件`：来自第二阶段冻结评价集 `rag_source_ids`，按52源基础库ID解析后，在70源增强库中复制对应同名文件。
- `02_实验Top5实际检索文件`：来自第三阶段 `rag_contexts_frozen.jsonl`，汇总该类问题实际进入B/D组提示词的Top-5来源。
- `问题与文件映射.csv/json`：逐题记录问题、核心依据、实际Top-5命中来源及Skill。

## 题号

- $(@{question_id=PL003_Emission_水污; project_id=PL003; question=请根据报告中的废水类型、预处理方式、排放去向、企业排口标准、污水处理厂名称、尾水排放河道和尾水执行标准，判断水污染物排放标准选取是否合理。要求对比：生活污水排放标准+排入污水处理厂名称+尾水排放河道+尾水排放执行标准，报告与知识库是否一致。; reference_answer=1、水污染物排放标准中生活污水排放执行标准：无误；
2、具体分析：生活废水经三级化粪池处理执行DB44/26-2001第二时段三级标准，后排入杏坛镇吉祐村红砖厂农村生活污水处理站，尾水执行GB18918-2002一级B标准。标准层次清晰，预处理标准与污水处理厂尾水标准分别引用，选取合理。; audit_type=水污染物排放标准; report_evidence=System.Object[]; report_support_note=人工参考答案的主体判断可由项目报告原文定位支持。; rag_source_ids=System.Object[]; rag_knowledge_refs=System.Object[]; skill_id=review-eia-pollutant-discharge-standards; manual_policy_files=System.Object[]; basis_status=sufficient; manual_review_required=False; manual_review_reason=; spatial_verification=; evidence_index_status=充分（人工镇级规则）; evidence_index_note=Excel未单列吉祐村污水站；按人工确认的镇级回退规则，以杏坛镇代表污水处理厂标准执行，不再以该站独立批复/许可作为本题前置条件}.question_id)：请根据报告中的废水类型、预处理方式、排放去向、企业排口标准、污水处理厂名称、尾水排放河道和尾水执行标准，判断水污染物排放标准选取是否合理。要求对比：生活污水排放标准+排入污水处理厂名称+尾水排放河道+尾水排放执行标准，报告与知识库是否一致。
- $(@{question_id=PL004_Emission_水污; project_id=PL004; question=请根据报告中的废水类型、预处理方式、排放去向、企业排口标准、污水处理厂名称、尾水排放河道和尾水执行标准，判断水污染物排放标准选取是否合理。要求对比：生活污水排放标准+排入污水处理厂名称+尾水排放河道+尾水排放执行标准，报告与知识库是否一致。; reference_answer=1、水污染物排放标准中生活污水排放执行标准：无误；
2、具体分析：生活污水经三级化粪池处理执行DB44/26-2001第二时段三级标准，通过市政管网排至杏坛镇生活污水处理厂，尾水执行GB18918-2002一级A标准及DB44/26-2001第二时段一级标准的较严值。冷却水经沉淀池处理达到GB/T18920-2020后回用于冲厕，再经化粪池排入污水处理厂。标准层次清晰，选取合理。; audit_type=水污染物排放标准; report_evidence=System.Object[]; report_support_note=人工参考答案的主体判断可由项目报告原文定位支持。; rag_source_ids=System.Object[]; rag_knowledge_refs=System.Object[]; skill_id=review-eia-pollutant-discharge-standards; manual_policy_files=System.Object[]; basis_status=sufficient; manual_review_required=False; manual_review_reason=; spatial_verification=; evidence_index_status=部分充分; evidence_index_note=设施映射和回用标准已有；补GB18918-2002全文以核验一级A条款和版本}.question_id)：请根据报告中的废水类型、预处理方式、排放去向、企业排口标准、污水处理厂名称、尾水排放河道和尾水执行标准，判断水污染物排放标准选取是否合理。要求对比：生活污水排放标准+排入污水处理厂名称+尾水排放河道+尾水排放执行标准，报告与知识库是否一致。
- $(@{question_id=PL005_Emission_水污; project_id=PL005; question=请根据报告中的废水类型、预处理方式、排放去向、企业排口标准、污水处理厂名称、尾水排放河道和尾水执行标准，判断水污染物排放标准选取是否合理。要求对比：生活污水排放标准+排入污水处理厂名称+尾水排放河道+尾水排放执行标准，报告与知识库是否一致。; reference_answer=1、水污染物排放标准中生活污水排放执行标准：无误；
2、具体分析：生活污水经三级化粪池处理执行DB44/26-2001第二时段三级标准，经市政管网排至杏坛污水处理厂，尾水执行GB18918-2002一级A标准及DB44/26-2001第二时段一级标准的较严值。冷却水经静置沉淀处理达到GB/T18920-2020后回用于冲厕。标准层次清晰，选取合理。; audit_type=水污染物排放标准; report_evidence=System.Object[]; report_support_note=人工参考答案的主体判断可由项目报告原文定位支持。; rag_source_ids=System.Object[]; rag_knowledge_refs=System.Object[]; skill_id=review-eia-pollutant-discharge-standards; manual_policy_files=System.Object[]; basis_status=sufficient; manual_review_required=False; manual_review_reason=; spatial_verification=; evidence_index_status=部分充分; evidence_index_note=补GB18918-2002全文；同时保留污水厂名称差异的实体归一化记录}.question_id)：请根据报告中的废水类型、预处理方式、排放去向、企业排口标准、污水处理厂名称、尾水排放河道和尾水执行标准，判断水污染物排放标准选取是否合理。要求对比：生活污水排放标准+排入污水处理厂名称+尾水排放河道+尾水排放执行标准，报告与知识库是否一致。
