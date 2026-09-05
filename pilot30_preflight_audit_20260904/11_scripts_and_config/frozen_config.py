#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
冻结参数配置 — CANONICAL v3.0
唯一权威来源：EXPERIMENT_CANONICAL.md

所有运行脚本必须从本文件读取参数，不得各自定义。
修改本文件后需重新生成所有 Prompt 并重新审计。
"""
from pathlib import Path

# ====== 实验版本 ======
VERSION = "v3.3_abc_canonical"
CONTEXT_VERSION = "v3.3"
CANONICAL_VERSION = "v3.0"

# ====== 模型规格（Model Ability）======
# 代码用 A1/A2/A3，论文展示用弱/中/强
MODELS = [
    {
        "model_id": "A1",
        "model_name": "qwen3.8-flash",
        "model_tier": "weak",
        "model_desc": "弱模型（轻量快速）",
    },
    {
        "model_id": "A2",
        "model_name": "qwen3.7-max",
        "model_tier": "medium",
        "model_desc": "中模型（上一代旗舰）",
    },
    {
        "model_id": "A3",
        "model_name": "qwen3.8-max",
        "model_tier": "strong",
        "model_desc": "强模型（当前旗舰）",
    },
]

# ====== 支持配置（Support Configuration）======
# 代码用 S0/S1/S2，论文展示用 A/B/C
SUPPORT_CONFIGS = [
    {
        "config_code": "S0",
        "config_label": "A",
        "config_name": "LLM",
        "config_desc": "纯模型基线（问题 + 环评报告上下文）",
        "has_web": False,
        "has_rag": False,
    },
    {
        "config_code": "S1",
        "config_label": "B",
        "config_name": "Web-augmented",
        "config_desc": "联网增强（A + 冻结联网搜索 Top-5）",
        "has_web": True,
        "has_rag": False,
    },
    {
        "config_code": "S2",
        "config_label": "C",
        "config_name": "Web+RAG",
        "config_desc": "联合增强（B 的同一联网证据 + 冻结领域 RAG Top-5）",
        "has_web": True,
        "has_rag": True,
    },
]

# ====== 模型参数（所有条件共享）======
TEMPERATURE = 0.0
MAX_COMPLETION_TOKENS = 8192
SEED = 42
TOP_P = 1.0

# ====== 上下文构建 ======
CONTEXT_CHAR_LIMIT = 15000
CONTEXT_BUILDER = "v3.3"  # 证据槽驱动 + 双通道召回 + 回溯补充

# ====== 检索参数 ======
WEB_TOP_K = 5
RAG_TOP_K = 5
WEB_SEARCH_ENGINE = "serper"

# ====== 评分规则 ======
SCORING_DIMENSIONS = [
    ("judgement_correctness", "判断正确性", 5),
    ("evidence_usage", "证据使用", 5),
    ("actionability", "审核意见可执行性", 5),
]
SCORING_WEIGHTS = [1/3, 1/3, 1/3]  # 等权重
AUTO_SCORING_LABEL = "PRE_SCORING_ONLY"  # 明确标记为仅预检

# ====== 文件路径 ======
def get_paths(project_root):
    """返回所有关键文件路径"""
    root = Path(project_root)
    return {
        "questions": root / "02_evaluation_set" / "pilot16_questions_v2.xlsx",
        "gold_review": root / "02_evaluation_set" / "pilot16_gold_review_v2.xlsx",
        "web_snapshot": root / "03_knowledge_base" / "pilot16_web_snapshot_v3_3.jsonl",
        "rag_snapshot": root / "03_knowledge_base" / "pilot16_rag_snapshot_v3_3.jsonl",
        "prompt_template": root / "04_prompts" / "prompt_template_FROZEN_v2.md",
        "system_prompt_file": root / "04_prompts" / "system_prompt_FROZEN_v2.txt",
        "output_dir": root / "07_results_v2" / "v3.3_abc_experiment",
        "prompt_dir": root / "07_results_v2" / "v3.3_abc_experiment" / "prompts",
        "result_file": root / "07_results_v2" / "v3.3_abc_experiment" / "pilot17_v3_3_abc_raw_results.jsonl",
        "pre_scoring_file": root / "07_results_v2" / "v3.3_abc_experiment" / "auto_pre_scoring_only.jsonl",
    }


def model_info(model_id):
    """按 model_id 获取模型信息"""
    for m in MODELS:
        if m["model_id"] == model_id:
            return m
    return None


def config_info(config_code):
    """按 config_code 获取配置信息"""
    for c in SUPPORT_CONFIGS:
        if c["config_code"] == config_code:
            return c
    return None


def total_runs(num_questions):
    """计算总运行次数"""
    return num_questions * len(MODELS) * len(SUPPORT_CONFIGS)
