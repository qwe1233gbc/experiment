# 环评审核 LLM 实验 — 3×3 析因设计

> 研究问题：外部知识对 LLM 环评审核能力的增益是否因模型规格、知识来源质量、任务类型不同而变化？

## 快速开始

### 1. 配置 API Key

```bash
# 所有 key 已经在 config/.env 中配置好了
# 如果需要修改，编辑 config/.env
```

需要的 Key：
- `COMPANY_API_KEY` — 主实验（公司 API）
- `DASHSCOPE_API_KEY` — RAG 检索（embedding + rerank）
- `SERPER_API_KEY` — K2 联网搜索（待实现）

### 2. 运行 Pilot 实验

```bash
# K1 + K3 条件，3模型 × 16题 = 96 次调用
python 05_scripts/run_pilot16.py

# 自动评分
python 05_scripts/score_pilot16.py
```

结果输出到 `07_results/` 目录。

### 3. 重新生成 RAG 快照（可选）

```bash
# 如果题库有更新，重新跑检索
python 05_scripts/run_rag_retrieval.py
```

## 当前状态

| 条件 | 状态 | 说明 |
|------|------|------|
| K1（无知识） | ✅ 可运行 | 脚本就绪 |
| K2（联网搜索） | 🚧 待实现 | Serper key 已配置，脚本待写 |
| K3（领域 RAG） | ✅ 可运行 | 快照已生成，脚本就绪 |

## 实验设计

### 三因素设计

| 因素 | 水平 | 说明 |
|------|------|------|
| **模型规格 (M)** | M1: qwen3.8-flash | 轻量快速模型 |
| | M2: qwen3.7-max | 上一代旗舰 |
| | M3: qwen3.8-max | 当前旗舰 |
| **知识来源 (K)** | K1: 无知识 | 闭卷，仅报告上下文 |
| | K2: 联网搜索 | Serper API 搜索结果 |
| | K3: 领域 RAG | 环评法规标准知识库 |
| **任务类型 (T)** | E0P0 | 低知识依赖 × 低推理复杂度 |
| | E0P1 | 低知识依赖 × 高推理复杂度 |
| | E1P0 | 高知识依赖 × 低推理复杂度 |
| | E1P1 | 高知识依赖 × 高推理复杂度 |

### Pilot：16 题 × 3 模型 × 3 知识 = 144 次调用

## 快速开始

### 1. 配置 API

```bash
cp config/.env.example config/.env
# 编辑 config/.env，填入 COMPANY_API_KEY
```

### 2. 查看实验设计

- `01_experiment_design/实验设计文档_v2.0.md` — 完整实验设计
- `01_experiment_design/预注册假设_v1.md` — 预注册假设
- `01_experiment_design/统计分析计划_v1.md` — 统计分析方案

### 3. 运行 Pilot 实验

```bash
cd 05_scripts
cp run_experiment.py.template run_pilot.py
# 修改 run_pilot.py 中的模型和题目配置
python run_pilot.py
```

### 4. 评分与分析

```bash
cp score_results.py.template score_pilot.py
# 修改 score_pilot.py 配置
python score_pilot.py
```

## 目录结构

```
实验/
├── README.md                    # 本文件
├── .gitignore                   # Git忽略配置
├── config/                      # API配置、模型清单
│   ├── .env.example
│   └── models_available.md
├── 01_experiment_design/        # 实验设计文档
│   ├── 实验设计文档_v2.0.md
│   ├── 预注册假设_v1.md
│   ├── 统计分析计划_v1.md
│   ├── EP分类协议_v1.md
│   └── Pilot准备总览.md
├── 02_evaluation_set/           # 评价集 + Gold
│   ├── pilot16_questions.xlsx
│   ├── pilot16_gold_review_template.xlsx
│   ├── pilot16_EP_labeling_audit.xlsx
│   └── scoring_rules_v1.md
├── 03_knowledge_base/           # RAG知识库
│   ├── README.md
│   ├── rag_snapshot_v3.jsonl
│   ├── rag_manifest_v3.json
│   ├── report_context_v3.jsonl
│   └── standard_cards.json
├── 04_prompts/                  # Prompt模板
│   ├── prompt_template_FROZEN_v1.md
│   └── knowledge_condition_spec.md
├── 05_scripts/                  # 运行脚本
│   ├── README.md
│   ├── run_experiment.py.template
│   └── score_results.py.template
├── 06_calibration/              # 模型校准结果
│   ├── calibration_findings_v2.md
│   ├── calibration_questions_hard15.md
│   ├── calibration_hard15_questions.xlsx
│   └── calibration_hard15_scored.xlsx
├── 07_results/                  # 实验结果（运行后生成）
├── 08_reference/                # 参考资料
│   ├── 文献支持审计总览.md
│   ├── research_gap_audit.md
│   └── 核心文献推荐.md
└── 09_input_reports/            # 输入报告（原始JSON）
    ├── README.md
    └── PL001~PL015 共11份环评报告.json
```

## 重要说明

### 模型梯度问题

**⚠️ 模型能力操纵检查未通过**：Qwen 3.x 系列（flash/max）在环境工程基础题和一般推理上天花板效应严重，无法建立弱-中-强能力梯度。

**当前设计**：将"模型能力"改为"模型规格/代际差异"：
- M1 (qwen3.8-flash) — 轻量版
- M2 (qwen3.7-max) — 上一代旗舰
- M3 (qwen3.8-max) — 当前旗舰

详见 `06_calibration/calibration_findings_v2.md`。

### 安全提醒

- **不要将 API Key 提交到公开 GitHub 仓库**
- `.env` 文件应加入 `.gitignore`
- 只使用 `.env.example` 作为模板

## 相关文档

- 文献审计：`08_reference/文献支持审计总览.md`
- 研究 Gap：`08_reference/research_gap_audit.md`
- 核心文献：`08_reference/核心文献推荐.md`
