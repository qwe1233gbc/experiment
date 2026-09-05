# 项目智能体规则

本文件适用于 `E:\实验文件整理_按论文逻辑` 及其全部子目录。

## 默认职责

优先由 DSH 完成文件定位、参数提取、目录整理、CSV/JSON 统计、hash/manifest 检查、正式版本核验、论文 3.2—3.5 材料整理及既有脚本的确定性运行。

只有涉及跨脚本复杂修改、版本冲突解释、实验逻辑、复杂调试、核心实验脚本、实验设计、统计方法、正式评价集或科研结论时，才准备 Codex 交接。遵循 `AI_AGENT/TASK_ROUTING.md`。

## 最小读取顺序

1. 先看目录名和文件名。
2. 再看 README、manifest、provenance、validation report 和参数台账。
3. 使用精确关键词搜索。
4. 局部读取目标行、字段、sheet、JSON key 或函数。
5. 仅在任务明确需要时读取完整文件。

默认不读取 `node_modules`、`tmp`、`__pycache__`、历史版本、大量 PDF 原件及无关实验输出。

## Source of Truth

先读 `AI_AGENT/FORMAL_SOURCE_OF_TRUTH.md`。冲突时按以下优先级处理：

1. 冻结清单、实际执行脚本和验收报告；
2. 当前架构说明；
3. 早期试运行文件；
4. 写作提示词和速查表。

无法由权威来源解决的冲突必须标记 `UNRESOLVED`，不得猜测。

## 科研完整性边界

- 未经用户明确授权，不修改正式实验设计、核心实验脚本、统计方法、正式评价集、冻结清单、正式结果或论文结论。
- 不把 LLM 裁判写成人类专家复评；人工专家复评目前尚未完成。
- 不把 52 源基础库与 70 源实验增强快照混为同一口径。
- 不将待审核环评报告 JSON 纳入法规 RAG 知识库。
- Codex 不可用或额度不足时，只继续确定性任务；科研判断停在事实包与 `UNRESOLVED` 状态。

## Codex 交接

使用 `.dsh/skills/codex-handoff/SKILL.md` 和 `AI_AGENT/CODEX_HANDOFF_TEMPLATE.md` 生成最小交接包。默认先向用户展示交接包并获得确认，再调用 Codex；不得直接提交整个项目。

## 项目级 Skills

- `project-navigator`
- `experiment-fact-extractor`
- `paper-material-preparer`
- `experiment-validator`
- `codex-handoff`

项目入口见 `AI_AGENT/PROJECT_INDEX.md`，DSH 使用说明见 `AI_AGENT/DSH_USAGE.md`。
