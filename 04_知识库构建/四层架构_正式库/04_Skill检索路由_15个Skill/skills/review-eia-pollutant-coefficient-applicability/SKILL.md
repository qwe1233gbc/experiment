---
name: review-eia-pollutant-coefficient-applicability
description: "分步核验产排污系数的活动水平口径、行业、产品、原料、工艺、污染物及适用边界；不负责完成全部源强计算。"
---

# TASK

审核报告选用的产污系数、排污系数、类比系数或经验系数是否适用于本项目。未引用这类系数时输出`不适用`。

# GOAL

将每个系数条目作为独立对象：先核活动水平口径，再核行业/产品/原料/工艺/污染物匹配，最后核适用边界与时点。必须区分“活动水平口径错误”与“系数选择错误”。

# CORE RULES

1. 审核目标是判断报告是否满足既定要求，而不是尽可能发现问题。若Mandatory条件均满足且无直接反证，应判定Match并停止，不得为了展示审核深度扩大问题范围。
2. 项目事实只能来自报告证据；具体系数值、手册版本、条文和外部适用结论只能来自可追溯RAG，不得凭记忆补充。
3. 每个工序独立判定。某工艺的回用、惯例或口径说明，不能证明另一工艺的系数适用。
4. 只有`DECISION_REQUIRED`证据缺失才能使相应子判定Cannot determine；`VALIDATION_ONLY`或`SUPPORTING`缺失不得降级。
5. 引用跨行业或参照条目时，工艺同名仅是线索，不是适用证明。必须分别核对活动目的、物料来源与状态、企业在该活动中的角色，以及RAG是否明确覆盖该场景；自产工序物料的厂内处理与以废物加工利用为目的的生产活动不得默认互换。
6. RAG若明确说明项目场景与条目适用场景不同、不等同或不在其范围，这是直接边界反证，对该条目必须判Mismatch。“没有更合适系数”、“物料相似”、“结果偏保守”或“数值可追溯”都不能消除适用边界反证；只能转化为寻找替代依据、采用其他核算方法或补充论证的修改建议。

# REQUIRED REPORT FACTS

逐条抽取并绑定原文位置：系数来源/版本、数值/单位、污染物、核算工序、活动水平数值/口径，以及相关的行业、产品、原料和工艺事实。交叉核对产能表、原辅料表、工艺描述和核算表。

# EVIDENCE REQUIREMENTS

- `DECISION_REQUIRED`：报告的系数条目、单位、活动水平口径；需外部核验时，RAG中相应条目的适用对象和边界。
- `VALIDATION_ONLY`：产能表、物料衡算和其他章节的同一工序数据，只用于交叉核对。
- `SUPPORTING`：规模、末端治理、类案和经验提示；仅当外部条目明示要求时升为`DECISION_REQUIRED`。

# REVIEW PROCEDURE

## STEP 1 — 建立条目台账
Action: 按污染物和工序拆分条目，抽取报告值、单位、来源和项目事实。
Required input: `DECISION_REQUIRED`报告证据。
Decision: 条目能否唯一识别；冲突原文全部保留。
Output: `result + explanation`及缺失字段。

## STEP 2 — 核对活动水平
Action: 比较系数单位要求的基准与报告代入量，再用产能、原辅料、回用量或物料衡算交叉核对。
Required input: 系数单位、活动水平值/口径；单位要求需RAG确认时列为`DECISION_REQUIRED`。
Decision: `MATCH | MISMATCH | CANNOT_DETERMINE`。“原料用量之和”不得仅按字面判错，必须判断实际口径。
Output: `result + explanation`；仅形成口径子结论，不延伸为系数选择结论。

## STEP 3 — 核对系数匹配
Action: 将报告的行业、产品、原料、工艺和污染物逐项与同一条RAG条目比较；跨行业参照还必须比较活动目的、物料来源/状态和企业角色。
Required input: 项目事实和可追溯RAG适用证据。
Decision: 只检查RAG明示的适用维度；不相关维度不是强制门槛；一个条目匹配不能代替其他工序判定。对跨行业条目，若RAG未明确覆盖项目的活动目的、物料来源/状态和企业角色，不得判Match；有直接边界反证时判Mismatch，否则Cannot determine并给出补证动作。
Output: `result + explanation`及逐维比较。

## STEP 4 — 核对适用边界
Action: 核对产污/排污系数性质、跨行业或参照条件、规模/治理条件和有效时点。
Required input: 报告条目与RAG对应边界；仅RAG明示条件为Mandatory。
Decision: `MATCH | MISMATCH | CANNOT_DETERMINE`。“常见做法”只对其明示对象有效，不得扩展到其他工序或来源。
Output: `result + explanation`及RAG定位。

## STEP 5 — 归纳结论
Action: 保留每个条目的子结论，再形成总结论和修改意见。
Required input: Steps 1–4。
Decision: `匹配 | 不匹配 | 部分匹配 | 无法判断 | 不适用`。已证实的实质不匹配不得被其他匹配项抵消；不确定子项不得冒充问题。
Output: `result + explanation`和可执行审核意见。

# DECISION LOGIC

- Match：Mandatory报告事实和所需外部证据齐备，口径、条目匹配和边界无直接反证。
- Mismatch：报告事实明确，且内部复核或适用RAG显示实质冲突。
- 对跨行业/参照条目，RAG明示“项目场景与条目场景不等同”即执行Mismatch，不得再以缺乏更优条目改判Match。
- Cannot determine：仅限当前子判定的`DECISION_REQUIRED`证据缺失；其他已可判定子项继续完成。
- 无RAG时仍完成证据抽取、口径识别、算术复核和交叉核对，但不给出未提供的系数、版本或外部结论。

# COMMON ERRORS TO AVOID

- 未核单位/活动水平就判系数值；混淆口径错误与系数选择错误。
- 因一个工序的回用或惯例成立，就放行另一工序的跨行业系数。
- 因辅助证据缺失直接判错，或为审核而找错。
- 把RAG中不适用的条目当作“报告无问题”的证明。

# SCOPE DISCIPLINE

仅处理本Skill对应audit_category。其他审核类别的线索只允许写入`scope_note`，不展开判断，不得影响本题等级。完整源强计算由相应计算Skill处理。

# TERMINATION CONDITION

所有Mandatory步骤完成、决定性证据已获得或本题不需要外部证据、且不存在直接反证时立即停止。

# OUTPUT

遵循运行时统一Schema，至少输出：总结论；每个条目的活动水平、条目匹配和边界子结论；报告与RAG证据位置；缺失的`DECISION_REQUIRED`证据；可执行修改或核验动作。输出合法JSON，不编造事实或外部数值。

# FINAL CHECK

确认：已先核活动水平；每个工序/条目独立判定；未将回用或惯例跨步骤泛化；具体系数和手册结论均有RAG来源；仅`DECISION_REQUIRED`缺失导致Cannot determine；Mandatory条件均满足且无反证时已判Match并停止。
