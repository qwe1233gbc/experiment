# 论文必读核心文献（12 篇）

> 按重要性排序，建议全部精读

## 1. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

- **作者/年份/会议**：Lewis et al., 2020, NeurIPS
- **DOI/URL**：https://arxiv.org/abs/2005.11401
- **支持的逻辑链**：L2（RAG基础价值）
- **证据等级**：A 级
- **研究问题**：RAG 是否能提升知识密集型 NLP 任务表现？
- **主要结果**：RAG 在多个知识密集型任务上显著优于纯参数模型，且参数效率更高
- **最关键原文**："RAG outperforms pure parametric models on knowledge-intensive tasks"
- **与本文关系**：理论依据（RAG 奠基性论文）
- **它真正能说明**：RAG 是补充模型外部知识的有效范式
- **它不能说明**：RAG 在所有任务上都有效 / 增益与模型能力的关系

## 2. RAG in the Wild: On the (In)effectiveness of LLMs with Mixture-of-Knowledge Retrieval Augmentation

- **作者/年份/会议**：Xu et al., 2026, ACL Findings
- **DOI/URL**：https://aclanthology.org/2026.findings-acl.849.pdf
- **支持的逻辑链**：L3, L5
- **证据等级**：A 级
- **研究问题**：在混合知识来源的真实场景下，RAG 对不同能力模型的效果有何不同？
- **主要结果**：混合知识场景下，检索增益主要局限于较小模型；模型足够强时增益显著下降（事实性 QA 除外）
- **最关键原文**："benefits of retrieval are largely confined to smaller models; gains diminish significantly for powerful models"
- **与本文关系**：核心理论依据（L3 + L5 的最直接证据）
- **它真正能说明**：RAG 增益受模型能力调节，小模型获益更多；知识来源质量影响 RAG 效果
- **它不能说明**：增益单调递减 / 领域知识比通用搜索一定更好

## 3. How Does Knowledge Selection Help Retrieval Augmented Generation?

- **作者/年份/会议**：Li & Ouyang, 2025, EMNLP Findings
- **DOI/URL**：https://aclanthology.org/2025.findings-emnlp.218
- **支持的逻辑链**：L3, L4, L5
- **证据等级**：A 级
- **研究问题**：知识选择（检索精度/召回）如何影响 RAG 表现？与生成器能力有何关系？
- **主要结果**：强模型更受益于召回率（知识量），弱模型更受益于选择精度（知识纯度）；任务复杂度也影响知识选择的作用
- **最关键原文**："generator capability and complexity influence the impact of knowledge selection"
- **与本文关系**：核心理论依据（L3 + L4 + L5 三重支撑）
- **它真正能说明**：模型能力与知识质量存在交互效应；任务复杂度影响 RAG 作用
- **它不能说明**：模型越强 RAG 增益越小（本文发现的是不同维度的调节）

## 4. Less LLM, More Documents: Searching for Improved RAG

- **作者/年份/会议**：Sarfati et al., 2025, arXiv
- **DOI/URL**：https://arxiv.org/pdf/2510.02657
- **支持的逻辑链**：L3（知识替代效应的量化证据）
- **证据等级**：A 级
- **研究问题**：扩大检索语料库能否替代更大的生成模型？
- **主要结果**：存在补偿效应：小模型+大语料可以匹配甚至超过大模型+小语料；4B模型配2倍语料超过8B模型
- **最关键原文**："corpus expansion enables smaller models to match or outperform larger counterparts (compensation effect)"
- **与本文关系**：理论依据（知识替代效应的量化支持）
- **它真正能说明**：外部知识可以部分替代模型规模（补偿效应）
- **它不能说明**：环境领域也有同样的补偿效应 / 强模型完全不需要 RAG

## 5. To Memorize or to Retrieve: Scaling Laws for RAG-Considerate Pretraining

- **作者/年份/会议**：Team OLMo, 2026, arXiv
- **DOI/URL**：https://arxiv.org/pdf/2604.00715
- **支持的逻辑链**：L3（知识替代效应的 scaling law 证据）
- **证据等级**：A 级
- **研究问题**：预训练规模与检索规模之间的最优分配是什么？
- **主要结果**：小模型从检索中获益最多，大模型收益递减且存在过度分配问题；存在 scaling law
- **最关键原文**："smaller models benefit most, while larger models exhibit diminishing returns"
- **与本文关系**：理论依据（scaling law 角度支持知识替代）
- **它真正能说明**：RAG 增益随模型规模递减存在 scaling law
- **它不能说明**：在专业领域也遵循同样的 scaling law

## 6. Benchmarking LLMs for Environmental Review and Permitting (NEPAQuAD)

- **作者/年份/会议**：PNNL, 2025, KDD
- **DOI/URL**：https://arxiv.org/pdf/2407.07321v3
- **支持的逻辑链**：L1, L6
- **证据等级**：A 级
- **研究问题**：LLM 在环境审查与许可任务上的表现如何？
- **主要结果**：所有模型在提供金标段落时表现最好；环境监管推理任务具有挑战性，需要领域知识支持
- **最关键原文**："all models achieve highest performance when provided with gold passage as context"
- **与本文关系**：领域依据（环境领域 LLM 基准的奠基性工作）
- **它真正能说明**：环境审查是知识密集型任务，LLM 需要外部上下文支持
- **它不能说明**：RAG 在环评审核中的具体增益 / 中国环评标准

## 7. Integrating Fine-tuning and Retrieval-Augmented Generation to Address Application Challenges of Pollution Control Guidelines

- **作者/年份/会议**：Zhou et al., 2026, Journal of Environmental Management
- **DOI/URL**：10.1016/j.jenvman.2026.125280
- **支持的逻辑链**：L6（环境领域 RAG 有效性的直接证据）
- **证据等级**：A 级
- **研究问题**：RAG 和微调能否提升污染控制指南的理解与应用？
- **主要结果**：RAG 和微调整合系统在污染控制指南问答上显著优于基线；领域 RAG 对环境专业知识任务有效
- **最关键原文**："RAG effectively enhances LLMs in pollution control guideline applications"
- **与本文关系**：领域依据（环境领域 RAG 的直接证据）
- **它真正能说明**：环境领域（污染控制指南）RAG 有效；专业法规知识需要外部补充
- **它不能说明**：不同模型能力下 RAG 效果不同 / 知识质量梯度

## 8. Toward Robust RALMs: Revealing the Impact of Imperfect Retrieval on Retrieval-Augmented Language Models

- **作者/年份/会议**：Kim et al., 2024, arXiv
- **DOI/URL**：https://arxiv.org/html/2410.15107
- **支持的逻辑链**：L5（知识质量影响 RAG 效果）
- **证据等级**：A 级
- **研究问题**：不完美检索如何影响 RAG 系统的鲁棒性？
- **主要结果**：RALM 对外部信息质量敏感；检索器不完美或知识源受污染会显著降低鲁棒性
- **最关键原文**："RALMs are sensitive to the quality of external information"
- **与本文关系**：理论依据（知识质量的重要性）
- **它真正能说明**：知识/检索质量显著影响 RAG 效果，质量是值得操纵的变量
- **它不能说明**：领域知识库一定比搜索好

## 9. Can Small Language Models Use What They Retrieve? An Empirical Study of Retrieval Utilization Across Model Scale

- **作者/年份/会议**：, 2026, arXiv
- **DOI/URL**：https://arxiv.org/html/2603.11513v1
- **支持的逻辑链**：L3（模型能力维度的另一面：小模型利用检索能力弱）
- **证据等级**：B 级
- **研究问题**：小模型能否有效利用检索到的知识？
- **主要结果**：7B 以下模型即使有 oracle 检索也有 85-100% 的时候提取不出正确答案，存在"利用瓶颈"
- **最关键原文**："models ≤7B fail to extract correct answer 85-100% of time even with oracle retrieval"
- **与本文关系**：对立/补充证据（提示小模型端可能有地板效应）
- **它真正能说明**：小模型存在检索利用瓶颈，不是给了知识就能用
- **它不能说明**：所有小模型都有这个问题 / 环评领域也一样

## 10. How Faithful are RAG Models? Quantifying the Tug-of-War between RAG and LLMs' Internal Prior

- **作者/年份/会议**：Zhang et al., 2024, arXiv
- **DOI/URL**：https://arxiv.org/pdf/2404.10198v1.pdf
- **支持的逻辑链**：L3, L5
- **证据等级**：B 级
- **研究问题**：RAG 模型的忠实度如何？模型内置知识与检索内容如何竞争？
- **主要结果**：LLM 与检索内容之间存在"拉锯战"；模型越强，越倾向于依赖内置知识而忽略检索内容（当二者冲突时）
- **最关键原文**："tug-of-war between RAG and LLMs internal prior; stronger LLMs revert to priors more"
- **与本文关系**：机制证据（知识替代的微观机制）
- **它真正能说明**：强模型更依赖内置知识，检索内容的影响力相对减弱
- **它不能说明**：强模型在环评标准上也有足够的内置知识

## 11. Artificial Intelligence in Impact Assessment: The State of the Art

- **作者/年份/会议**：Sullivan & Staz, 2025, Impact Assessment and Project Appraisal
- **DOI/URL**：10.1080/14615517.2025.2594274
- **支持的逻辑链**：L1, L6
- **证据等级**：C 级
- **研究问题**：AI 在环境影响评价领域的应用现状如何？
- **主要结果**：AI/LLM 在环评中有广阔应用前景，但专业知识和监管合规性是核心挑战
- **最关键原文**："domain expertise and regulatory compliance remain core challenges"
- **与本文关系**：背景证据（领域重要性）
- **它真正能说明**：环评领域 AI 应用需要专业知识支持
- **它不能说明**：RAG 具体增益多少

## 12. Large Language Model-assisted EIA Screening

- **作者/年份/会议**：Booth et al., 2025, Impact Assessment and Project Appraisal
- **DOI/URL**：10.1080/14615517.2025.2523628
- **支持的逻辑链**：L1, L6
- **证据等级**：B 级
- **研究问题**：LLM 能否辅助 EIA 筛选？
- **主要结果**：LLM 可以辅助 EIA 筛选，但在专业法规判断上仍有局限，需要领域知识增强
- **最关键原文**："LLMs can assist EIA screening but need domain knowledge enhancement for regulatory judgments"
- **与本文关系**：领域依据（EIA 领域 LLM 局限）
- **它真正能说明**：EIA 任务需要领域知识，纯 LLM 有局限
- **它不能说明**：RAG 具体提升多少

