# RAG 知识库说明

## 知识库概况

- **来源数量**：81 个正式来源
- **父块数量**：409 个
- **子块数量**：3459 个
- **向量维度**：1024
- **Embedding 模型**：text-embedding-v4（阿里云 DashScope）
- **检索方式**：Dense + BM25 RRF 融合 → gte-rerank-v2 重排序 → 来源去重

## 数据来源白名单

法律法规正式文本、GB国家标准、HJ行业标准、DB44地方标准、官方国民经济行业分类、官方生态环境状况公报、官方声环境功能区划、官方三线一单文件、正式技术规范和指南、佛山市塑胶行业正式技术参考指南。

## 文件说明

### 检索索引
- `retrieval_index/` — 混合检索索引目录
  - `retrieval_registry.json` — 索引元数据
  - `child_cosine_flat.index` — FAISS 向量索引（dense retrieval）
  - `bm25_index.json` — BM25 索引（sparse retrieval）
  - `child_metadata.jsonl` — 子块元数据
  - `parent_contexts.jsonl` — 父块全文
  - `child_embeddings_l2_normalized.npy` — 子块向量备份

### 检索快照（实验用）
- `pilot16_rag_snapshot.jsonl` — Pilot 16 题的 RAG 检索结果（冻结）
  - 共 80 条记录（16题 × Top-5）
  - 每题 5 个不重复来源
  - 包含父块全文作为证据文本
- `pilot16_rag_manifest.json` — 快照元数据

### 旧版快照（仅供参考）
- `rag_snapshot_v3.jsonl` — 旧 heldout16 的 8 题检索结果（不用于本实验）
- `rag_manifest_v3.json` — 旧版 manifest

### 其他
- `report_context_v3.jsonl` — 报告上下文快照（旧版）
- `standard_cards.json` — 38 张法规标准卡片
- `README.md` — 本文件

## 如何重新生成检索快照

如果题库有更新，重新跑 RAG 检索：

```bash
# 确保设置了 DASHSCOPE_API_KEY
export DASHSCOPE_API_KEY=your_key

# 运行检索脚本
python 05_scripts/run_rag_retrieval.py
```

输出：
- `03_knowledge_base/pilot16_rag_snapshot.jsonl` — 新的检索快照
- `03_knowledge_base/pilot16_rag_manifest.json` — 元数据

## 快照字段说明

每条记录包含：
- `question_id` — 题目ID
- `ep_category` — EP分类
- `rank` — 检索排名（1-5）
- `parent_id` / `child_id` — 知识库块ID
- `source_id` / `source_file` — 来源文件
- `retrieval_score` / `rerank_score` — 检索分数
- `text` — 父块全文（用于 Prompt 上下文）
- `child_text` — 子块文本（精确匹配段）
- `retrieval_method` — 检索方法说明
- `retrieval_query_sha256` — 检索 query 哈希
- `snapshot_hash` — 记录哈希
