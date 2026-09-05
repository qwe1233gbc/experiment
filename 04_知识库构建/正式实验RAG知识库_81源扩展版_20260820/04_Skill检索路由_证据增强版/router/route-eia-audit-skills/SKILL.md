---
name: route-eia-audit-skills
description: "在环评报告审核、问答分类、ABCD消融实验或多项审核任务中，根据问题意图、报告证据和所需外部依据，从15个专业EIA Skill中选择最小充分集合，协调RAG证据、执行顺序、跨Skill依赖、证据不足降级和统一结构化输出。用于不确定该调用哪个Skill、一个问题跨越多个审核类别或需要批量路由时；不替代具体专业Skill作出最终审核判断。"
---

# 环评审核 Skill 总路由器

将问题路由到最小充分的专业 Skill 集合。保持“路由负责选择，专业 Skill 负责判断，RAG 负责提供外部依据”的边界。

## 路由流程

1. 从问题和报告证据识别审核对象、污染介质、计算任务及法规需求。
2. 阅读 [routing-catalog.md](references/routing-catalog.md)，形成候选 Skill 集。
3. 排除仅被宽泛关键词命中、但审核对象不在边界内的候选 Skill。
4. 选择能覆盖问题的最小 Skill 集；单一任务不得无理由注入全部 15 个 Skill。
5. 确定执行顺序：事实抽取与分类先于标准匹配，源强先于治理设施和总量闭合。
6. 为每个 Skill 分配同一输入契约中的相关 `report_evidence` 与 `rag_evidence`。
7. 合并输出时保留各 Skill 的 `basis_status`、证据链、计算过程和人工复核标志。

## 优先级和依赖

- 行业分类、建设内容和项目位置属于上游事实，应先于排放标准、产污系数和三线一单适用性判断。
- 产污系数适用性先于源强定量核算。
- 废气收集形式先于设计风量，设计风量和收集效率先于活性炭参数与VOCs总量闭合。
- 环境质量现状数据与环境质量执行标准是两个独立 Skill，不得互相代替。
- 危险废物识别与固废控制标准是两个判断维度；需要时联合调用危险废物识别和污染物排放标准 Skill。

## 路由输出

先输出路由计划，再调用专业 Skill：

```json
{
  "route_status": "matched | ambiguous | not_applicable",
  "selected_skills": [
    {
      "skill_name": "",
      "reason": "",
      "required_report_fields": [],
      "required_rag_domains": [],
      "depends_on": []
    }
  ],
  "execution_order": [],
  "unresolved_scope": [],
  "manual_review_needed": false
}
```

## 证据和降级约束

- 不把题号、金标标签、评分或预设结论写入检索词或 Skill 输入。
- 报告事实与外部法规依据必须分开保存。
- RAG 缺失时仍可路由和执行内部复算，但需要外部常量的 Skill 必须降级为 `basis_status=insufficient`。
- 不把“未检索到依据”解释成“报告错误”。
- 多 Skill 结论冲突时不得投票覆盖，应保留冲突并转人工复核。

## 终止条件

当且仅当已给出最小 Skill 集、执行顺序、所需证据和未解决范围时结束路由。最终专业结论必须由被选中的 Skill 产生。
