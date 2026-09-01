# 实验脚本

## 脚本列表

| 脚本 | 用途 | 依赖 |
|------|------|------|
| `run_pilot16.py` | 主实验运行脚本（K1+K3） | COMPANY_API_KEY |
| `score_pilot16.py` | 自动评分脚本 | openpyxl |
| `run_rag_retrieval.py` | RAG 检索快照生成 | DASHSCOPE_API_KEY, faiss |

## 使用方法

### 0. 配置环境变量

```bash
# 复制模板
cp config/.env.example config/.env

# 编辑 config/.env，填入各个 API Key
```

### 1. 生成 RAG 检索快照（如需要）

如果 `03_knowledge_base/pilot16_rag_snapshot.jsonl` 已经存在，跳过此步。

```bash
python 05_scripts/run_rag_retrieval.py
```

输出：
- `03_knowledge_base/pilot16_rag_snapshot.jsonl` — 检索快照

### 2. 运行主实验

```bash
python 05_scripts/run_pilot16.py
```

输出：
- `07_results/pilot16_raw_results.jsonl` — 原始结果（JSONL 格式）
- `07_results/logs/run_pilot16.log` — 运行日志

**特点**：
- 支持断点续跑（已完成的 run_id 会跳过）
- 自动重试（失败最多重试 3 次）
- 3 模型 × 2 知识条件 × 16 题 = 96 次调用

### 3. 自动评分

```bash
python 05_scripts/score_pilot16.py
```

输出：
- `07_results/pilot16_scored.xlsx` — 逐题评分表 + 汇总统计
- `07_results/pilot16_score_summary.md` — Markdown 汇总报告

**评分方式**：
- 判断题：判断立场是否一致（正确/错误、符合/不符合）
- 选择题：提取选项字母比对
- 计算题：提取关键数值，允许 10% 相对误差
- 综合题：关键词匹配率
- 无法自动判断的标记为 UNKNOWN，需人工复核

### 4. 人工复核

自动评分后，建议对 PARTIAL 和 UNKNOWN 的题目进行人工复核。

## 依赖安装

```bash
pip install openpyxl faiss-cpu numpy requests
```

faiss 只在运行 RAG 检索时需要，运行主实验和评分不需要。

## 实验设计

- **模型**：M1 (qwen3.8-flash)、M2 (qwen3.7-max)、M3 (qwen3.8-max)
- **知识条件**：K1（无知识）、K3（领域 RAG）——K2 待补充
- **题目**：16 题（E0P0/E0P1/E1P0/E1P1 各 4 题）
- **总调用数**：3 × 2 × 16 = 96 次

## 结果格式（JSONL）

每条记录字段：
- `run_id` — 唯一标识（question_id__model__knowledge）
- `question_id` — 题目ID
- `ep_category` — EP 分类
- `model_condition` / `model_name` — 模型
- `knowledge_condition` — 知识条件
- `prompt_hash` / `evidence_hash` / `report_context_hash` — 哈希校验
- `gold_answer` — Gold 答案
- `raw_answer` — 模型原始回答
- `input_tokens` / `output_tokens` / `latency` — 用量统计
- `status` — OK / ERROR / TRUNCATED
