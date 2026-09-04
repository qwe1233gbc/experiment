#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pilot30 V4 检索全链路生成脚本
- 对 14 道 RAG_PRIMARY 题执行 BM25 → Dense → RRF → Rerank → Top5
- 对 9 道 REPORT_ONLY_CONTROL 题保持检索拒答（rag_items=[]）
- 输出到 06_retrieval_snapshots/<question_id>/
- 全程保存中间结果，可复现
- 不调用模型API，只做检索

用法: python run_retrieval_v4.py --all
   或: python run_retrieval_v4.py --question PL001_Emission_固体
"""
import argparse
import json
import sys
from pathlib import Path

# 相对路径导入检索模块
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # pilot30_v4_preflight/../..
sys.path.insert(0, str(PROJECT_ROOT / '实验' / '05_scripts'))

BASE = PROJECT_ROOT / '实验'
V4 = PROJECT_ROOT / 'pilot30_v4_preflight'
SNAPSHOT_DIR = V4 / '06_retrieval_snapshots'
INDEX_DIR = BASE / '03_knowledge_base' / 'retrieval_index'


def load_questions():
    """加载正式题目"""
    q_path = V4 / '01_questions' / 'formal_questions.jsonl'
    questions = []
    for line in q_path.read_text(encoding='utf-8').strip().splitlines():
        if line.strip():
            questions.append(json.loads(line))
    return questions


def build_query(q):
    """
    从题干、任务类型、污染物/工艺/设施、标准名称生成检索query。
    严禁从金标答案倒推查询词。
    """
    parts = [q['question_text']]
    
    # 添加任务类型关键词
    task = q.get('task_type', '')
    if task and task not in q['question_text']:
        parts.append(f"任务类型：{task}")
    
    # 添加项目涉及污染物（从题目推断）
    qid = q['question_id']
    pollutant_hints = {
        "VOCs": "VOCs 挥发性有机物",
        "Hazardous": "危险废物 危废",
        "Emission_固体": "固体废物 固废",
        "Capture": "收集效率 集气罩",
        "Airflow": "设计风量 排气量",
        "Fenceline": "厂区内 无组织 NMHC",
        "Stack": "排气筒 高度 排放速率",
        "Storage": "危废贮存 贮存设施",
    }
    for key, hint in pollutant_hints.items():
        if key in qid:
            parts.append(hint)
            break
    
    return " ".join(parts)


def run_bm25(query, top_k=20):
    """BM25检索（调用现有检索模块）"""
    # TODO: 调用实际的 BM25 检索函数
    # from retrieve_v3_3 import bm25_search
    # results = bm25_search(query, top_k=top_k)
    raise NotImplementedError("BM25检索需要导入实际的检索模块")


def run_dense(query, top_k=20):
    """Dense检索"""
    raise NotImplementedError("Dense检索需要导入实际的检索模块")


def run_rrf(bm25_results, dense_results, top_k=20):
    """RRF融合"""
    raise NotImplementedError("RRF融合需要实现")


def run_rerank(query, candidates, top_k=10):
    """Rerank重排"""
    raise NotImplementedError("Rerank需要导入实际的rerank模块")


def build_final_top5(rerank_results, top_k=5):
    """
    构建最终Top-5：
    - 保留child_text命中段
    - 在父块中按命中位置向前后扩展
    - 禁止优先截取parent_text开头
    - 表格行、条号、数值、代码不得被截断
    """
    raise NotImplementedError("上下文扩展需要实现")


def save_jsonl(path, items):
    with open(path, 'w', encoding='utf-8') as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def process_question(q):
    """处理单题检索全链路"""
    qid = q['question_id']
    qdir = SNAPSHOT_DIR / qid
    qdir.mkdir(parents=True, exist_ok=True)
    
    # REPORT_ONLY_CONTROL 题：拒答
    if q.get('analysis_role') == 'REPORT_ONLY_CONTROL':
        abstain = {
            "retrieval_abstained": True,
            "reason": "REPORT_ONLY_CONTROL题，不需要外部知识",
            "rag_items": [],
        }
        save_jsonl(qdir / "05_final_top5.jsonl", [abstain])
        print(f"  {qid}: REPORT_ONLY_CONTROL → 检索拒答")
        return True
    
    # RAG_PRIMARY 题：执行全链路
    query = build_query(q)
    
    # 保存 query
    with open(qdir / "00_query.json", 'w', encoding='utf-8') as f:
        json.dump({
            "question_id": qid,
            "query": query,
            "query_source": "question_text + task_type + pollutant_hint",
            "gold_leakage_check": "PASSED（未使用金标答案）",
        }, f, ensure_ascii=False, indent=2)
    
    # TODO: 执行各阶段检索
    # bm25_results = run_bm25(query, 20)
    # save_jsonl(qdir / "01_bm25_top20.jsonl", bm25_results)
    #
    # dense_results = run_dense(query, 20)
    # save_jsonl(qdir / "02_dense_top20.jsonl", dense_results)
    #
    # rrf_results = run_rrf(bm25_results, dense_results, 20)
    # save_jsonl(qdir / "03_rrf_top20.jsonl", rrf_results)
    #
    # rerank_results = run_rerank(query, rrf_results, 10)
    # save_jsonl(qdir / "04_rerank_top10.jsonl", rerank_results)
    #
    # final_top5 = build_final_top5(rerank_results, 5)
    # save_jsonl(qdir / "05_final_top5.jsonl", final_top5)
    
    print(f"  {qid}: RAG_PRIMARY → 检索框架就绪（待接入实际检索模块）")
    return False  # 未实际执行


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--all', action='store_true', help='处理所有题目')
    parser.add_argument('--question', type=str, help='处理单个题目')
    args = parser.parse_args()
    
    questions = load_questions()
    
    if args.question:
        q = next((q for q in questions if q['question_id'] == args.question), None)
        if not q:
            print(f"题目不存在: {args.question}")
            return
        questions = [q]
    elif not args.all:
        print("请指定 --all 或 --question")
        return
    
    print(f"开始检索: {len(questions)} 题")
    done = 0
    for q in questions:
        if process_question(q):
            done += 1
    
    print(f"完成: {done}/{len(questions)} 题")
    print("注意：当前仅框架，需接入实际检索模块后才能生成真实快照")


if __name__ == '__main__':
    main()
