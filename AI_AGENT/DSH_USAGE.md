# DSH 使用说明

## 启动

```powershell
& "E:\dsh-v3\start-dsh-web.ps1"
```

打开 `http://127.0.0.1:3080`，选择工作区 `E:\实验文件整理_按论文逻辑`。

Headless 示例：

```powershell
$env:DSH_HOME = "E:\dsh-v3"
& "E:\npm-global\dsh.ps1" --profile headless "核验正式模型与运行 manifest"
```

API Key 和 Base URL 从当前 Windows 用户环境读取，不写入项目文档。

## 推荐任务写法

- “只根据参数台账和第五阶段 manifest，核验正式模型与参数。”
- “定位论文 3.3 所需的冻结 RAG 事实，只返回路径、字段和值。”
- “核验 A/B/C/D 各组题数、状态和相关哈希，不读取原始回复。”
- “为这个跨脚本问题生成 Codex 最小交接包，先不要调用 Codex。”

## Skills

项目级 Skill 位于 `.dsh/skills/`。新会话应能发现：

- `project-navigator`
- `experiment-fact-extractor`
- `paper-material-preparer`
- `experiment-validator`
- `codex-handoff`

## 使用原则

1. 优先使用 `AI_AGENT/PROJECT_INDEX.md` 定位入口。
2. 正式事实以 `AI_AGENT/FORMAL_SOURCE_OF_TRUTH.md` 为快速索引，并回到列出的 manifest/validation 原件核验。
3. 大文件只读取任务相关字段、sheet、JSON key 或函数。
4. 默认排除 `node_modules`、`tmp`、`__pycache__`、历史版本、大量 PDF 和无关实验输出。
5. 涉及科研判断时按 `AI_AGENT/TASK_ROUTING.md` 升级。

## 故障降级

Codex 不可用时继续 DSH 确定性任务；API 或 DSH 不可用时停止模型任务并保留已确认事实。任何情况下都不得为了完成任务而猜测正式版本或改写科研结论。
