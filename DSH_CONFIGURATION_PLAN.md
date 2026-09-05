# DSH 基础智能体配置计划

> 项目：`E:\实验文件整理_按论文逻辑`  
> 计划日期：2026-08-14  
> 当前阶段：第一轮检查与方案设计；尚未创建项目级智能体文件或 Skills。

## 1. 配置目标

为本项目建立轻量 DSH 基础智能体：DSH 负责文件定位、事实提取、材料整理、确定性脚本运行与结果核验；涉及核心代码、实验设计、统计方法或科研结论时，DSH 先生成最小上下文包，再交给 Codex。Codex 不可用时，DSH 只能继续确定性任务，不得越权修改科研结论、实验设计或正式结果。

## 2. 已确认的运行环境

- DSH 版本：`0.1.0-rc.6`。
- DSH 启动器：`E:\npm-global\dsh.ps1`。
- DSH Home：`E:\dsh-v3`。
- Web UI：`http://127.0.0.1:3080`，当前可访问。
- Codex CLI：`C:\Users\ylx\AppData\Roaming\npm\codex.ps1`，当前可发现。
- 当前项目尚无 `AGENTS.md`、`AI_AGENT/`、`.dsh/skills/`、`.agents/skills/` 或 `.claude/skills/`。

## 3. 当前版本原生配置能力

本机已安装代码确认：

- `@deepseek-ai/dsh-agent-instructions` 默认读取项目根 `AGENTS.md`，并兼容 `CLAUDE.md`。
- `@deepseek-ai/dsh-skill-filesystem` 原生发现项目级 `.dsh/skills/<skill-name>/SKILL.md`。
- 同一 Skill 提供器也支持 `.agents/skills`、`$DSH_HOME/skills` 等位置；本项目优先使用 `.dsh/skills`，避免污染用户全局配置。
- 不需要开发插件或修改 DSH 源码。

## 4. 最小 Source of Truth 核验

### 4.1 正式模型与实验执行

- 正式推理模型：`qwen3.8-max`。
- 正式执行目录：`06_ABCD四组实验结果/第五阶段_qwen3.8-max_冻结实验_20260812/`。
- `run_manifest.json`：状态 `complete`，A/B/C/D 各 21 题，共 84 个任务，成功 84、失败 0。
- 正式运行参数：`temperature=0`；默认 `max_tokens=8000`；失败重试 `16000`；timeout `300 s`；初始并发 3，单题恢复并发 1。

### 4.2 正式 RAG

- 基础四层知识库：52 知识源、323 父块、2747 子块。
- 正式实验增强快照：在 52 源基础库之外增加 18 项 P0/P1 证据，共 70 源、398 父块、3433 子块。
- 冻结 RAG：21 题各 Top-5，B/D 共用；SHA-256：`fc3cc897cc99d2fb32deb6f68c75cf8a410da7b7a33f57ad0edba4eac02e1dd1`。
- 查询策略明确排除参考答案、`basis_status` 和人工结论。
- 配置文件中必须同时保留“52 源基础库”和“70 源实验增强快照”两个口径，禁止混写。

### 4.3 正式 Skill

- `04_知识库构建/四层架构_正式库/04_Skill检索路由_15个Skill/`记录 15 个专业 Skill 与 1 个总路由器。
- 证据增强版 `skill_bank_manifest.csv` 指向同一组正式 Skill 路径和 SHA-256，未形成另一套 Skill 定义。
- 冻结 C/D 提示词与这份 Skill manifest 是否存在直接、逐文件哈希绑定：`UNRESOLVED`。第二轮只记录该状态，不自行推断或替换正式 Skill。

### 4.4 正式评价集和 A/B/C/D

- 正式评价集：21 题、6 个项目、7 个操作性审核类型；冻结数据集 SHA-256：`37bf435ae24630da5ad4cba41f47a24e8917cd981d153ea0e0c1c96f765047f0`。
- 第四阶段提示词：A/B/C/D 各 21，共 84；因子隔离验收 `PASS`。
- 正式组别：A=LLM；B=LLM+RAG；C=LLM+Skill；D=LLM+RAG+Skill。
- 正式结果以第五阶段冻结实验 manifest、provenance 和 validation report 为准，不以早期组目录或写作速查表覆盖。
- 人工专家复评尚未完成；不得表述为已完成专家验证。

## 5. 第二轮拟创建结构

```text
E:\实验文件整理_按论文逻辑\
├─ AGENTS.md
├─ AI_AGENT\
│  ├─ PROJECT_INDEX.md
│  ├─ FORMAL_SOURCE_OF_TRUTH.md
│  ├─ TASK_ROUTING.md
│  ├─ CODEX_HANDOFF_TEMPLATE.md
│  └─ DSH_USAGE.md
└─ .dsh\skills\
   ├─ project-navigator\SKILL.md
   ├─ experiment-fact-extractor\SKILL.md
   ├─ paper-material-preparer\SKILL.md
   ├─ experiment-validator\SKILL.md
   └─ codex-handoff\SKILL.md
```

仅创建上述最少文件；不创建全量索引，不复制 15 个专业 EIA Skill，不修改正式实验文件，不修改 DSH 源码。

## 6. 文件职责

### `AGENTS.md`

- 声明 DSH/Codex 权限边界和禁止事项。
- 固化最小读取顺序及排除目录。
- 指向 `AI_AGENT/` 内的索引、正式口径与路由规则。
- 对正式结果、实验设计和科研结论实行只读默认策略。

### `AI_AGENT/PROJECT_INDEX.md`

- 只记录 01—09 主目录职责和权威入口文件。
- 不建立逐文件全量索引。

### `AI_AGENT/FORMAL_SOURCE_OF_TRUTH.md`

- 记录正式模型、RAG、Skill、评价集和 A/B/C/D 目录。
- 记录 SHA-256、验收状态和权威来源优先级。
- 冲突或缺少直接证据的项目明确标记 `UNRESOLVED`。

### `AI_AGENT/TASK_ROUTING.md`

- 定义 DSH 直接处理、DSH 整理后交 Codex、Codex 优先三类任务。
- 给出升级条件和禁止自动修改事项。

### `AI_AGENT/CODEX_HANDOFF_TEMPLATE.md`

固定只传递：任务、已确认事实、相关路径、关键片段、冲突点、需 Codex 判断的问题。默认不附整个目录、全文或无关输出。

### `AI_AGENT/DSH_USAGE.md`

- 提供启动、工作区选择、Skills 检查和最小读取示例。
- 说明 Codex 不可用时的降级策略。

### 5 个轻量 Skills

- `project-navigator`：按目录名/文件名→README/manifest→搜索→局部读取定位材料。
- `experiment-fact-extractor`：从参数台账、manifest、provenance、validation report 提取可溯源事实。
- `paper-material-preparer`：按论文 3.2—3.5 组织已确认材料，不生成未经证实的科研结论。
- `experiment-validator`：执行 hash/manifest/数量/状态/正式版本一致性检查。
- `codex-handoff`：生成最小上下文包；仅在复杂代码、实验逻辑或科研判断触发时调用 Codex。

## 7. DSH/Codex 路由方案

| 任务 | 默认执行者 | 升级条件 |
|---|---|---|
| 文件定位、参数提取、目录整理、CSV/JSON 统计、hash/manifest 检查 | DSH | 出现跨来源冲突且无法由权威优先级解决 |
| 正式版本核验、按论文 3.2—3.5 整理材料、已有脚本确定性运行 | DSH | 需要改变正式方法或解释冲突的科研含义 |
| 跨多个脚本的复杂问题、版本冲突、复杂调试、实验逻辑核验 | DSH 先压缩，Codex 后处理 | 上下文包满足模板后再调用 |
| 修改核心实验脚本、实验设计、统计方法、正式评价集或科研结论 | Codex 优先 | 未获得明确授权时保持只读并报告 |

Codex 不可用或额度不足时：DSH 可继续定位、提取、统计、核验和运行既有确定性脚本；涉及设计、方法或正式结论的任务停止在“事实包 + `UNRESOLVED`”状态。

## 8. Token 与读取控制

默认读取顺序：

1. 目录名和文件名；
2. README、manifest、provenance、validation report、参数台账；
3. 精确关键词搜索；
4. 局部读取目标行、字段、sheet、JSON key 或函数；
5. 仅在任务必要时读取完整文件。

默认排除：`node_modules`、`tmp`、`__pycache__`、历史版本、大量 PDF 原件和无关实验输出。

## 9. 预计影响

- 新增少量 Markdown 配置与 5 个轻量 Skill 定义。
- 不修改现有实验数据、脚本、冻结清单、结果或论文结论。
- 不重跑实验，不生成大型索引，不复制大文件。
- DSH 每次任务会先读取简短项目规则，增加少量固定上下文，但显著减少无关文件读取和交给 Codex 的上下文量。

## 10. 第二轮验收建议

1. DSH 新会话能加载项目根 `AGENTS.md`。
2. DSH 能发现且仅新增上述 5 个项目级轻量 Skill。
3. `project-navigator` 能在不扫描排除目录的情况下定位指定权威文件。
4. `experiment-fact-extractor` 输出包含事实、来源路径和冲突状态。
5. `experiment-validator` 能复核冻结 RAG、评价集、提示词及正式运行 manifest 的核心哈希/数量。
6. `codex-handoff` 生成的包只含模板规定的六类信息。
7. 不对任何正式实验文件产生修改。

## 11. 待确认事项

1. 是否批准进入第二轮并创建第 5 节列出的文件。
2. `codex-handoff` 是默认只生成交接包并等待人工确认，还是允许在满足升级条件后自动调用本机 Codex CLI。建议先采用“生成交接包 + 人工确认”。
3. 冻结 C/D 提示词与正式 Skill manifest 的直接哈希绑定目前标记为 `UNRESOLVED`；是否需要第二轮追加一次只读溯源核验。

