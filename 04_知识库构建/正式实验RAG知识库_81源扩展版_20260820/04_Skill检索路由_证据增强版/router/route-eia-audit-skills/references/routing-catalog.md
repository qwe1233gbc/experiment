# 15 个专业 Skill 路由目录

| Skill | 主要触发对象 | 不负责 |
|---|---|---|
| `review-eia-industry-classification` | 行业名称、四位代码、产品和工艺冲突 | 环评分类名录 |
| `calculate-eia-environmental-investment-ratio` | 总投资、环保投资、分项合计和占比 | 治理技术充分性 |
| `review-eia-three-lines-one-list-consistency` | 项目位置、管控单元、准入清单 | 排放与环境质量标准 |
| `review-eia-construction-content-completeness` | 工程组成、产品、原料、设施、工艺和产污环节 | 标准限值判断 |
| `review-eia-environmental-quality-data` | 环境质量公报、年份、原文数据和时效性 | 环境质量标准 |
| `review-eia-environmental-quality-standards` | 大气、水、声功能区类别和环境质量限值 | 排放控制标准 |
| `review-eia-pollutant-discharge-standards` | 废水、废气、噪声、固废控制标准适用性 | 源强定量核算 |
| `review-eia-pollutant-coefficient-applicability` | 产污系数与行业、产品、工艺和规模适配 | 完整源强计算 |
| `calculate-eia-pollutant-source-strength` | 产生、收集、处理和排放量计算链 | 外部参数自行认定 |
| `calculate-eia-exhaust-capture-airflow` | 收集形式、集气罩、控制风速、理论风量 | 风机设计余量 |
| `review-eia-exhaust-design-airflow` | 漏风、同时工作、管网和风机设计风量 | 污染物限值 |
| `review-eia-exhaust-capture-efficiency` | 密闭、罩位、负压和收集效率 | 治理去除效率 |
| `review-eia-activated-carbon-parameters` | VOCs负荷、炭量、床层和更换周期 | 危废属性认定 |
| `review-eia-hazardous-waste-identification` | 废物来源、组成、危害特性、代码和去向 | 排放标准完整性 |
| `review-eia-vocs-total-control` | VOCs产生、排放、削减、替代和总量申请 | 单项源强或标准选择 |

## 常见联合调用

- 塑料项目排放标准：行业分类 → 建设内容 → 污染物排放标准。
- VOCs 全链条：产污系数适用性 → 源强定量 → 收集形式 → 设计风量 → 收集效率 → 活性炭参数 → VOCs总量。
- 固废审核：建设内容 → 危险废物识别 → 污染物排放标准。
- 环境质量章节：环境质量现状数据 + 环境质量执行标准，分别出结论。
