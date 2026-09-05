# 环评投资概算

- 问题数量：1
- 核心答案依据文件：1个
- 实验Top-5实际检索文件（去重）：5个

## 文件夹说明

- `01_核心答案依据文件`：来自第二阶段冻结评价集 `rag_source_ids`，按52源基础库ID解析后，在70源增强库中复制对应同名文件。
- `02_实验Top5实际检索文件`：来自第三阶段 `rag_contexts_frozen.jsonl`，汇总该类问题实际进入B/D组提示词的Top-5来源。
- `问题与文件映射.csv/json`：逐题记录问题、核心依据、实际Top-5命中来源及Skill。

## 题号

- $(@{question_id=PL003_V01_Q03; project_id=PL003; question=请根据报告中的总投资、环保投资和环保工程投资明细，判断环保投资核算是否前后一致、比例是否正确。; reference_answer=1、环保投资占比（%）核算正确；
2、具体分析：项目填报的项目总投资金额为100万元、环保投资金额为15万元、环保投资占比为15%。按“环保投资÷总投资×100%”复算为15.00%，与报告填报值一致；表2-9 项目环保工程措施投资一览表中的分项投资合计为15万元，与环保投资一致。因此，环保投资金额、分项合计及占比前后一致，核算正确。; audit_type=环评投资概算; report_evidence=System.Object[]; report_support_note=人工参考答案的主体判断可由项目报告原文定位支持。; rag_source_ids=System.Object[]; rag_knowledge_refs=System.Object[]; skill_id=calculate-eia-environmental-investment-ratio; manual_policy_files=System.Object[]; basis_status=sufficient; manual_review_required=False; manual_review_reason=; spatial_verification=; evidence_index_status=充分; evidence_index_note=该题核心为报告内部复算，外部RAG不是必要条件；不要用5%经验阈值替代算术核验}.question_id)：请根据报告中的总投资、环保投资和环保工程投资明细，判断环保投资核算是否前后一致、比例是否正确。
