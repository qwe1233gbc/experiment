# 02 Skill 专业审核体系

> 生成日期：2026-08-26
> 数据口径：正式Skill库 = `04_知识库构建/四层架构_正式库/04_Skill检索路由_15个Skill/`（15个专业Skill + 1个总路由器）；40题Skill路由dry-run复验 PASS（2026-08-20）。
> Skill v2（规则内嵌版，`11_15个Skill逐项开发与验证提示词_20260825/`）为在研前沿，不纳入本文。

---

## 主线

```
专家审核经验原本只存在于自然语言提示词中（不可复用、不可验证）
        ↓
Skill = 结构化、可复用的专业审核程序
（"本Skill是环境专业审核程序，不是法规知识副本"——每个Skill第0节的统一声明）
        ↓
15个专业Skill覆盖14类审核任务
        ↓
总路由器按"最小充分集合"选择Skill并确定执行顺序
        ↓
每个Skill：触发条件 → 输入契约 → 分步审核程序 → 降级规则 → 结构化输出
        ↓
C/D组实验中作为"程序约束"因子
```

## 1. Skill 是什么：从提示词到审核程序

科研中的核心命题是：**如何把专家审核经验，从自然语言Prompt转化为结构化、可复用的专业审核程序。**

实现的证据链：

- 每个Skill是一份15节标准结构的 `SKILL.md` 文件，YAML frontmatter声明 `name` 与 `description`（description明确"用于……；不用于……"的正反边界）；
- 每个Skill第0节统一声明定位："本Skill是环境专业审核程序，不是法规知识副本。它负责报告证据抽取、RAG查询构造、适用性比较、内部复算、异常处理和结构化输出。具体标准、条款、限值、版本和固定适用结论必须由运行时`rag_evidence`提供。"——**程序与知识强制分离**，这是Skill区别于"把法规塞进提示词"的关键设计；
- 演变来源可追溯：部分Skill由早期 Dify 工作流改造而来（如行业分类Skill来自 `06_Dify工作流/1-国民经济分类判断.yml`，排放标准Skill来自 `8-污染物排放标准内容判断.yml`），并在文件中注明"旧Dify工作流仅作历史平台实现，不直接作为C/D组Skill输入"。

（来源：`04_知识库构建/四层架构_正式库/04_Skill检索路由_15个Skill/skills/*/SKILL.md`）

## 2. Skill 总量与构成

**15个专业Skill + 1个总路由器**（来源：`AI_AGENT/FORMAL_SOURCE_OF_TRUTH.md` §正式Skill；`router/route-eia-audit-skills/references/routing-catalog.md`）。

按功能分三类（3个calculate + 11个review + 1个router辅助判定）：

| 类型 | Skill | 主要触发对象 | 不负责 |
|---|---|---|---|
| 事实/分类 | review-eia-industry-classification | 行业名称、四位代码、产品和工艺冲突 | 环评分类名录 |
| 事实/分类 | review-eia-three-lines-one-list-consistency | 项目位置、管控单元、准入清单 | 排放与环境质量标准 |
| 完整性 | review-eia-construction-content-completeness | 工程组成、产品、原料、设施、工艺和产污环节 | 标准限值判断 |
| 标准适用 | review-eia-environmental-quality-data | 环境质量公报、年份、原文数据和时效性 | 环境质量标准 |
| 标准适用 | review-eia-environmental-quality-standards | 大气、水、声功能区类别和环境质量限值 | 排放控制标准 |
| 标准适用 | review-eia-pollutant-discharge-standards | 废水、废气、噪声、固废控制标准适用性 | 源强定量核算 |
| 定量计算 | calculate-eia-environmental-investment-ratio | 总投资、环保投资、分项合计和占比 | 治理技术充分性 |
| 定量计算 | calculate-eia-pollutant-source-strength | 产生、收集、处理和排放量计算链 | 外部参数自行认定 |
| 定量计算 | calculate-eia-exhaust-capture-airflow | 收集形式、集气罩、控制风速、理论风量 | 风机设计余量 |
| 定量核查 | review-eia-exhaust-design-airflow | 漏风、同时工作、管网和风机设计风量 | 污染物限值 |
| 定量核查 | review-eia-exhaust-capture-efficiency | 密闭、罩位、负压和收集效率 | 治理去除效率 |
| 定量核查 | review-eia-activated-carbon-parameters | VOCs负荷、炭量、床层和更换周期 | 危废属性认定 |
| 定量核查 | review-eia-pollutant-coefficient-applicability | 产污系数与行业、产品、工艺和规模适配 | 完整源强计算 |
| 危废 | review-eia-hazardous-waste-identification | 废物来源、组成、危害特性、代码和去向 | 排放标准完整性 |
| 总量 | review-eia-vocs-total-control | VOCs产生、排放、削减、替代和总量申请 | 单项源强或标准选择 |

每个Skill条目均带"不负责"边界列——**防止宽泛关键词误触发**是路由目录的显式设计目标。

## 3. 15节标准结构（用户所需七要素 → 实际文件字段）

15个Skill共用同一15节骨架，与"Applicability / Required evidence / Review procedure / Constraints / Output / Termination"六要素的对应关系如下（以实际文件节名为准）：

| 用户关注要素 | 实际文件节 | 内容 |
|---|---|---|
| Applicability（何时执行） | §2 触发条件 | 3条左右具体条件；**未触发时输出`不适用`，"不得为完成任务而创造项目事实"** |
| Required evidence（需要什么证据） | §3 输入契约 + §4 报告证据字段 | 统一JSON契约；报告证据字段全部"缺失填null并进入missing_evidence"；每个字段绑定 `evidence_id + source_section + source_location + quote`（**可回溯到报告原文位置**） |
| Review procedure（按什么步骤审） | §5 抽取顺序 + §7 审核程序 | 固定抽取顺序（保留冲突证据，"不得只选择支持预设结论的片段"）；分步审核程序 |
| Constraints（什么情况不能判断） | §10 证据不足与降级规则 | `basis_status`三态：available / insufficient / not_required；insufficient时结论降级为"无法判断" |
| Output specification（输出什么） | §12 输出契约 | 统一JSON输出：conclusion、report_evidence_used、rag_basis_used、basis_status、applicability_check、calculation_trace、missing_evidence、risk_hints、manual_review_needed、review_comment |
| Termination（何时终止/转人工） | §13 人工复核规则 | 六种情形触发 `manual_review_needed=true` |
| 程序-知识边界 | §0 Skill定位 + §6 RAG查询构造 | 查询"只使用报告事实和审核类别，不使用外部评判标签、题号、评分或Skill预设结论"；"不得根据模型记忆补充法规、限值、版本或适用结论" |
| 经验知识管控 | §14 非规范经验提示 | 经验阈值、历史修改意见或同类项目惯例"不得冒充法条，不能单独支撑最终判断"，只能进 `risk_hints` |
| 防越界 | §15 与其他Skill边界 | 明确交接对象 |

**结论分级**（15个Skill统一）：`匹配 / 不匹配 / 部分匹配 / 无法判断 / 不适用`——五级结论本身就是审核专业性的表达：允许"无法判断"的存在，比强行给出对错更接近专家行为。

**输入契约的适用性维度按Skill定制**（同一骨架、不同知识维度）：

- 行业分类Skill核对：product、usage、material、process、main_business_activity、valid_time（6维）；
- 排放标准Skill核对：region、industry、process、pollutant、pollution_medium、emission_mode、discharge_destination、valid_time（8维），并规定 `not_applicable`≠缺失（噪声介质 discharge_destination 不适用不算证据缺口）；
- 危废Skill核对：generation_process、composition、physical_state、hazardous_characteristics、waste_code_basis、valid_time（6维）。

每条 rag_evidence 还强制携带 `effective_date`、`validity_status`、`source_sha256`——**证据的版本与哈希可追溯**。

## 4. Skill 路由：总路由器

路由器 `router/route-eia-audit-skills/SKILL.md` 的设计（来源：该文件全文）：

**职责边界**："路由负责选择，专业Skill负责判断，RAG负责提供外部依据"——路由器不替代专业Skill作最终审核判断。

**七步路由流程**：识别审核对象/介质/计算任务/法规需求 → 查routing-catalog形成候选集 → 排除仅被宽泛关键词命中的候选 → 选最小充分Skill集（"单一任务不得无理由注入全部15个Skill"） → 确定执行顺序 → 为每个Skill分配report_evidence与rag_evidence → 合并输出保留各自basis_status/证据链/计算过程/人工复核标志。

**领域依赖顺序**（专家工序逻辑的程序化）：
1. 行业分类、建设内容、项目位置属上游事实，先于排放标准、产污系数、三线一单适用性；
2. 产污系数适用性先于源强定量核算；
3. 废气收集形式先于设计风量，设计风量和收集效率先于活性炭参数与VOCs总量闭合；
4. 环境质量现状数据与环境质量执行标准是两个独立Skill，不得互相代替；
5. 危废识别与固废控制标准是两个判断维度，需要时联合调用。

**典型联合调用**（routing-catalog.md）：
- 塑料项目排放标准：行业分类 → 建设内容 → 污染物排放标准；
- VOCs全链条：产污系数适用性 → 源强定量 → 收集形式 → 设计风量 → 收集效率 → 活性炭参数 → VOCs总量（**7个Skill成链**）；
- 固废审核：建设内容 → 危险废物识别 → 污染物排放标准。

**防作弊约束**（路由器明文）："不把题号、金标标签、评分或预设结论写入检索词或Skill输入"；"不把'未检索到依据'解释成'报告错误'"；"多Skill结论冲突时不得投票覆盖，应保留冲突并转人工复核"。

## 5. dry-run 验证（40题，2026-08-20）

（来源：`05_QA测试集与样本/40题Skill_dryrun_正式版复验_20260820/Skill_dryrun最终验收报告.md`）

**结论：PASS。** 关键验收项：

| 验收项 | 结果 |
|---|---|
| 40题全部路由成功、question_id唯一 | True |
| 实际调用Skill类数 | 9类（每类≥1题） |
| 路由一致性 / 适用性 / C/D控制变量（C组无RAG、D组用冻结RAG） | 40/40 通过 |
| 提示词无Gold泄漏（no_gold_in_prompt） | True |
| 同题同Skill同版本（same_skill_same_version） | True |
| Skill版本冲突 | 0 |
| 危废Skill版本统一 | 4题全部切换正式库A版（`ead69b4f…`），81源库内B版副本标记"非正式同步副本/不用于正式实验" |

9类Skill调用分布（40题）：源强定量5题、收集风量5题、产污系数适用性5题、建设内容完整性5题、活性炭参数4题、收集效率4题、设计风量4题、危废识别4题、VOCs总量4题。

**实验调用方式**：C/D组正式输入在冻结前先经dry-run复验路由正确性，路由结果（选中Skill+版本SHA）与四组正式提示词一起冻结，保证C/D两组"同Skill同版本"、D组与B组"同RAG快照"。

## 6. 三个典型Skill深读（六问六答）

### 6.1 行业分类审核（review-eia-industry-classification）

| 问 | 答（均出自该SKILL.md） |
|---|---|
| 什么时候执行 | 报告填报行业名称或代码；产品或工艺可能跨多个行业小类；名称、代码、产品、工艺出现冲突。未触发输出`不适用` |
| 需要什么证据 | 7个报告字段：填报行业名称/代码、产品与产能、主要原辅材料、工艺流程、主要经营活动、产污环节；每字段带quote与位置 |
| 按什么步骤审 | ①判断项目事实是否足以描述主要活动 ②以产品为主、工艺为辅构造分类查询 ③比较报告代码与RAG分类定义及包含/不包含范围 ④多行业并存时区分主导与兼营活动 ⑤仅在RAG依据可追溯时判断外部匹配 |
| 什么情况不能判断 | 任一必要适用性维度（product/usage/material/process/main_business_activity/valid_time）未知时不得输出确定的外部依据结论；RAG缺失→`basis_status=insufficient`→"无法判断" |
| 输出什么 | 统一JSON契约；conclusion五级；review_comment必须写明"报告事实—外部依据—比较过程—建议修改" |
| 什么时候终止 | 关键证据缺失/前后冲突/RAG版本不明/结论为不匹配或部分匹配或无法判断/参数缺来源/经验与正式依据冲突 → `manual_review_needed=true` |

亮点：审核程序第4步"区分主导活动与兼营活动"是典型的专家判断知识——通用LLM不会自发想到。

### 6.2 污染物排放标准审核（review-eia-pollutant-discharge-standards）

| 问 | 答 |
|---|---|
| 什么时候执行 | 报告列示污染物排放或固废控制标准；污染源—污染因子—排放形式需要匹配；纳管、回用、外排、有组织/无组织边界需要判断 |
| 需要什么证据 | 11个报告字段：污染源、工艺、污染因子、介质、排放形式、去向、治理设施、报告标准、报告限值、排口参数、报告日期 |
| 按什么步骤审 | ①建立工序—污染物—治理—排放形式清单 ②按介质和去向分别查RAG ③按适用范围、例外和版本筛选候选标准 ④逐项比较报告标准、条款和限值 ⑤核对污染源覆盖完整性 ⑥固废危废只用RAG返回的法律、名录、鉴别和贮存条款判断 |
| 什么情况不能判断 | 8个适用性维度按介质解释（废气核对污染物/排放形式/排口厂界；废水核对去向/纳管外排回用；噪声核对厂界/功能区/时段；固废核对类别/贮存/去向/版本），真正必要维度未知才降级；`metadata_only_source_ids`（只有标准名无正文）不得支撑匹配结论 |
| 输出什么 | 统一JSON契约；换算时记录参数来源；不得预置具体标准号、类别限值或固定适用结论 |
| 什么时候终止 | 同六情形触发人工复核；版本或适用性不明是本Skill最常见的触发点 |

亮点：`not_applicable`≠缺失的规则（如噪声介质的discharge_destination），防止把"本来就不适用"误判为"证据不足"——这是从实际审核错误中沉淀的约束。

### 6.3 危险废物识别审核（review-eia-hazardous-waste-identification）

| 问 | 答 |
|---|---|
| 什么时候执行 | 项目产生固废、副产品或废包装物；产生废活性炭、废溶剂、废油墨、污泥等候选危废；报告引用名录、鉴别或贮存依据 |
| 需要什么证据 | 10个报告字段：废物名称、来源工序、组成、物理状态、危害特性、危废代码、识别依据、产生量、贮存方式、处置去向 |
| 按什么步骤审 | ①建立物料—工艺—废物清单 ②区分产品、副产品和废物 ③查RAG名录、鉴别和贮存条款 ④核对代码与危害特性证据 ⑤**按报告编制时点选择当时有效的名录、鉴别和贮存版本，不得把现行版本倒用于历史报告** ⑥检查遗漏类别、混存和版本问题 ⑦RAG不足时不得凭废物名称、行业惯例或相似项目直接认定危险属性 |
| 什么情况不能判断 | 6个适用性维度任一未知；RAG不足时危险属性、代码和贮存要求一律不得凭名称/惯例认定 |
| 输出什么 | 统一JSON契约；可按物料衡算复核产生量（内部算术），但危险属性结论必须来自RAG或正式鉴别证据 |
| 什么时候终止 | 同六情形触发人工复核 |

亮点：第7.5条"版本时点规则"与第7.7条"禁止名称认定"是危废审核最常见的两类真实错误（用2021版名录审2023报告、凭"废活性炭"名字直接定HW49）的直接程序化封堵。该Skill无独立Dify前身，是从建设内容、源强、治理设施和固废章节的交叉抽取经验新建的——说明Skill体系不是平台迁移，而是专家经验的新沉淀。

## 7. 面向展览的Skill一句话表达

> Skill把"怎么审环评"从专家脑中的隐性流程写成15份可执行审核程序：每份程序规定触发条件、证据字段、分步步骤、降级规则、五级结论与人工复核触发点，并由总路由器按"最小充分集合+领域依赖顺序"调度——模型在C/D组中执行的不是一段自然语言提示，而是一套带输入输出契约的专业审核流程。
