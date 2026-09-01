# 环评审核 LLM 实验 — ChatGPT 协作提示词

> 复制以下内容发给 ChatGPT，让它基于 GitHub 仓库协助你做实验

---

## 发给 ChatGPT 的提示词（复制下面全部内容）

```
我有一个环评审核 LLM 实验的 GitHub 仓库，需要你帮我做实验和分析。请先通读以下信息，然后回答我的问题或执行我要求的操作。

## 仓库地址
https://github.com/qwe1233gbc/experiment

## 项目背景
研究问题：外部知识对 LLM 环评审核能力的增益是否因模型规格、知识来源质量、任务类型不同而变化？

这是一个 3×3 析因设计实验：
- 模型规格 (M)：M1=qwen3.8-flash（轻量）、M2=qwen3.7-max（上一代旗舰）、M3=qwen3.8-max（当前旗舰）
- 知识来源 (K)：K1=无知识（闭卷）、K2=联网搜索（待实现）、K3=领域RAG（环评法规知识库）
- 任务类型 (T)：按EP分类，E0P0（低知识低推理）、E0P1（低知识高推理）、E1P0（高知识低推理）、E1P1（高知识高推理）

Pilot 阶段：16 题 × 3 模型 × 2 知识条件(K1+K3) = 96 次 API 调用

## 仓库结构（重点文件）

实验/
├── 01_experiment_design/        # 实验设计文档
│   ├── 实验设计文档_v2.0.md     # 完整设计
│   ├── 预注册假设_v1.md         # 假设清单
│   ├── 统计分析计划_v1.md       # 统计方案
│   ├── EP分类协议_v1.md         # EP分类规则
│   └── Pilot准备总览.md
├── 02_evaluation_set/           # 评价集
│   ├── pilot16_questions.xlsx   # 16道题（含题干、Gold答案、EP标签）
│   └── scoring_rules_v1.md      # 评分规则
├── 03_knowledge_base/           # RAG知识库
│   ├── pilot16_rag_snapshot.jsonl   # Pilot16题的检索快照（Top-5）
│   └── retrieval_index/         # 检索索引文件
├── 04_prompts/                  # Prompt模板
│   ├── prompt_template_FROZEN_v1.md
│   └── knowledge_condition_spec.md
├── 05_scripts/                  # 运行脚本
│   ├── run_pilot16.py           # 主实验脚本（K1+K3）
│   ├── score_pilot16.py         # 自动评分脚本
│   └── run_rag_retrieval.py     # RAG检索快照生成
├── 06_calibration/              # 模型校准结果
│   └── calibration_findings_v2.md
├── 07_results/                  # 实验结果（运行后生成）
├── 09_input_reports/            # 11份环评报告JSON
├── config/
│   ├── .env.example             # API Key模板（真实key不在仓库中）
│   └── models_available.md
├── AUDIT_REPORT.md              # 实验包审计报告
└── README.md

## 当前状态
- K1（无知识）+ K3（领域RAG）条件可运行，共 96 次调用
- K2（联网搜索）条件待实现，Serper API Key 已配置
- RAG 检索快照已预先生成（pilot16_rag_snapshot.jsonl，80条记录）
- 实验脚本已通过冒烟测试

## 如何运行实验

### 前置依赖
```bash
pip install openpyxl faiss-cpu numpy requests python-dotenv
```

### 配置 API Key
从 config/.env.example 复制为 config/.env，填入：
- COMPANY_API_KEY — 主实验API
- DASHSCOPE_API_KEY — RAG检索（embedding+rerank）
- SERPER_API_KEY — K2联网搜索

### 运行主实验（K1+K3）
```bash
cd 实验
python 05_scripts/run_pilot16.py
```
输出：07_results/pilot16_raw_results.jsonl + 运行日志
支持断点续跑，失败自动重试3次

### 自动评分
```bash
python 05_scripts/score_pilot16.py
```
输出：07_results/pilot16_scored.xlsx + pilot16_score_summary.md

评分方式：
- 判断题：立场匹配
- 选择题：选项提取比对
- 计算题：数值提取，允许10%相对误差
- 综合题：关键词匹配率
- 无法判断的标记为 UNKNOWN

### 重新生成RAG快照（如修改了题库或知识库）
```bash
python 05_scripts/run_rag_retrieval.py
```

## 结果格式（JSONL）
每条记录字段：
- run_id: 唯一标识（question_id__model__knowledge）
- question_id, ep_category, model_condition, knowledge_condition
- prompt_hash, evidence_hash, report_context_hash（哈希校验）
- gold_answer, raw_answer
- input_tokens, output_tokens, latency
- status: OK / ERROR / TRUNCATED

## 评分结果格式（XLSX）
两个 sheet：
1. detail — 逐题评分详情（score, score_method, explanation）
2. summary — 按模型×知识条件汇总的正确率、平均分

## 我需要你帮我做的事

请根据以下优先级协助我：

### 高优先级
1. 帮我理解实验设计和统计分析方案
2. 实验完成后，帮我分析 pilot16_scored.xlsx 的结果
3. 帮我写 K2 联网搜索条件的实现代码（Serper API）
4. 帮我写统计分析脚本（GLMM、交互效应检验、可视化）

### 中优先级
5. 帮我检查 Prompt 模板是否有问题
6. 帮我优化自动评分逻辑
7. 帮我写结果报告的初稿

### 低优先级
8. 帮我扩展评价集（设计新题目）
9. 帮我整理论文相关图表

每次请你做具体操作时，我会提供相关文件内容。现在请你先确认理解了整个实验框架，然后我们可以开始具体工作。
```

---

## 使用建议

### 第一次对话
- 把上面的完整提示词发给 ChatGPT
- 让它先确认理解了实验框架
- 可以问它对实验设计有什么疑问或建议

### 要分析结果时
- 把 `07_results/pilot16_scored.xlsx` 的内容（或关键数据）粘贴给它
- 或者把 `pilot16_score_summary.md` 的内容发过去

### 要写代码时
- 把相关的现有脚本内容发过去（让它先读代码再修改）
- 明确需求和约束条件

### 推荐模型
- **代码/分析类**：GPT-4o 或 Claude 3.5 Sonnet
- **统计分析**：GPT-4o（带 Code Interpreter 更好）
- **文档写作**：GPT-4o 或 Claude

---

## 快速提问模板

### 分析结果
```
这是 pilot16_score_summary.md 的内容：
[粘贴内容]

请帮我分析：
1. 各模型×知识条件的正确率对比
2. 知识增益（K3-K1）在各模型上的差异
3. EP分类对结果的影响
4. 有什么意外发现或值得注意的地方
```

### 实现 K2
```
我需要实现 K2 联网搜索条件。现有文件：
- run_pilot16.py 的内容：[粘贴]
- knowledge_condition_spec.md 的内容：[粘贴]
- .env 中有 SERPER_API_KEY

请帮我：
1. 设计搜索 query 构造逻辑
2. 设计搜索结果格式化和截断策略
3. 修改主实验脚本支持 K2 条件
4. 给出完整的实现代码
```

### 统计分析
```
这是评分结果的 summary sheet 数据：
[粘贴数据]

请帮我做统计分析：
1. 描述性统计（各条件下的均值、标准差）
2. 双因素方差分析（模型×知识）
3. 简单效应分析（如果有交互效应）
4. 生成可视化建议
请给出 Python 代码（用 scipy/statsmodels）
```
