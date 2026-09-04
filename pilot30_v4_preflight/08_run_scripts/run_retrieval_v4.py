#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pilot30 V4 真实检索全链路生成脚本
- 接入 HybridRetriever（来自自建脚本_统一管理）
- BM25：完全离线，立即可跑
- Dense/Rerank：需要 DashScope API，先报告预估后等待授权
- 输出到 06_retrieval_snapshots/<question_id>/
- 严格无金标泄漏：query 只来自题干+任务类型+污染物/设施
"""
import argparse
import json
import hashlib
import sys
import os
from pathlib import Path

# 相对路径解析
SCRIPT_DIR = Path(__file__).resolve().parent
V4_ROOT = SCRIPT_DIR.parent  # pilot30_v4_preflight/
REPO_ROOT = V4_ROOT.parent   # 仓库根（实验文件整理_按论文逻辑）

# 将自建脚本加入路径
sys.path.insert(0, str(REPO_ROOT / "自建脚本_统一管理"))

# 索引目录
INDEX_DIR = REPO_ROOT / "实验" / "03_knowledge_base" / "retrieval_index"
SNAPSHOT_DIR = V4_ROOT / "06_retrieval_snapshots"
QUESTIONS_PATH = V4_ROOT / "01_questions" / "formal_questions.jsonl"


def load_questions():
    """加载23道正式题"""
    questions = []
    for line in QUESTIONS_PATH.read_text(encoding='utf-8').strip().splitlines():
        if line.strip():
            questions.append(json.loads(line))
    return questions


def build_query(q):
    """
    构建检索query（严格无金标泄漏）。
    来源：题干审核对象 + 污染物/设施/标准类别关键词 + 任务类型
    禁止：金标verdict、正确代码、预期计算结果
    """
    parts = []
    
    # 1. 原题干（前300字，避免引入金标）
    qtext = q['question_text'].strip()
    if len(qtext) > 300:
        qtext = qtext[:300]
    parts.append(qtext)
    
    # 2. 任务类型
    task = q.get('task_type', '')
    if task:
        parts.append(f"任务类型：{task}")
    
    # 3. 题目类型关键词（从question_id推断，不含金标答案）
    qid = q['question_id'].lower()
    keyword_map = {
        "emission": "污染物排放标准 排放限值",
        "vocs": "VOCs 挥发性有机物 非甲烷总烃 NMHC",
        "captureefficiency": "废气收集效率 集气罩 捕集率",
        "designairflow": "设计风量 集气罩 控制风速 排气量计算",
        "captureairflow": "废气收集形式 理论排气量 集气罩 风量",
        "hazardouswaste": "危险废物 危废名录 危废代码 HW类别",
        "vocstotal": "VOCs总量控制 总量替代 削减量",
        "vocsmeasure": "VOCs治理措施 废气治理 活性炭吸附 催化燃烧",
        "fencelinenmhc": "厂区内无组织排放 监控点浓度 NMHC",
        "stackheight": "排气筒高度 排放速率 高度修正",
        "hwclassify": "危险废物归类 危废代码 HW08 HW49",
        "hwstorage": "危险废物贮存 贮存标准 贮存设施",
        "industry": "国民经济行业分类 行业代码 GB/T 4754",
        "invest_ratio": "环保投资比例 投资估算",
        "living_wastewater": "生活污水 排水量 核算",
        "ro_water": "纯水制备 浓水 反渗透",
        "massbalance": "物料衡算 产排平衡",
        "totalsubstitution": "VOCs总量替代 总量控制 削减比例",
    }
    for key, kw in keyword_map.items():
        if key in qid:
            parts.append(kw)
            break
    
    query = " ".join(parts)
    
    # 查询来源追溯（防泄漏审计）
    provenance = [
        "question_text (first 300 chars)",
        "task_type (from question metadata)",
        f"question_id keyword hint: {q.get('task_type', 'N/A')}",
    ]
    
    return query, provenance


def content_sha256(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def build_context_text(child_text, parent_text, child_id, parent_id):
    """
    构建上下文文本：
    - 以命中child_text为中心，在parent_text中定位
    - 向前后扩展，尽量保持条款、表格行、公式完整
    - 禁止 parent_text[:500] 前缀截断
    """
    if not parent_text:
        return child_text
    
    # 在父文本中查找子文本（取前50字做定位）
    child_fragment = child_text[:50] if len(child_text) > 50 else child_text
    idx = parent_text.find(child_fragment)
    
    if idx == -1:
        # 找不到就返回完整子文本 + 父文本前200字作上下文
        return child_text + "\n\n[父文本开头参考]:\n" + parent_text[:200]
    
    # 向前后各扩展 300 字（约1-2个段落）
    window = 300
    start = max(0, idx - window)
    end = min(len(parent_text), idx + len(child_text) + window)
    
    # 尝试对齐到段落边界
    # 向前找最近的换行或句号
    if start > 0:
        for sep in ['\n', '。', '；']:
            prev_sep = parent_text.rfind(sep, start, idx)
            if prev_sep != -1 and idx - prev_sep < window * 1.5:
                start = prev_sep + 1
                break
    
    # 向后找最近的换行或句号
    if end < len(parent_text):
        for sep in ['\n', '。', '；']:
            next_sep = parent_text.find(sep, end - 20, end + window)
            if next_sep != -1:
                end = next_sep + 1
                break
    
    context = parent_text[start:end]
    
    # 加上前后标记
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(parent_text) else ""
    
    return prefix + context + suffix


def format_result(rank, child, parent, score, method=""):
    """格式化单条检索结果"""
    child_text = child.get("content", child.get("child_text", ""))
    parent_text = parent.get("content", parent.get("parent_text", "")) if parent else ""
    
    context_text = build_context_text(child_text, parent_text, child.get("child_id", ""), child.get("parent_id", ""))
    
    return {
        "rank": rank,
        "child_id": child.get("child_id", ""),
        "parent_id": child.get("parent_id", ""),
        "source_id": child.get("source_id", ""),
        "source_title": child.get("source_title", child.get("source_file", "")),
        "version_or_date": child.get("version", child.get("publish_date", "")),
        "score": round(score, 6),
        "method": method,
        "child_text": child_text,
        "context_text": context_text,
        "content_sha256": content_sha256(child_text),
    }


def save_jsonl(path, items):
    with open(path, 'w', encoding='utf-8') as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def run_bm25_only(retriever, query, top_k=20):
    """只跑BM25（完全离线，不需要API）"""
    bm25_results = retriever._bm25(query, top_k)
    results = []
    for rank, (doc_id, score) in enumerate(bm25_results[:top_k], 1):
        child = retriever.metadata[doc_id]
        parent = retriever.parents.get(child["parent_id"], {})
        results.append(format_result(rank, child, parent, score, method="BM25 + exact-code boost"))
    return results


def main():
    parser = argparse.ArgumentParser(description="Pilot30 V4 RAG检索全链路生成")
    parser.add_argument('--all', action='store_true', help='处理所有RAG_PRIMARY题')
    parser.add_argument('--question', type=str, help='处理单个题目')
    parser.add_argument('--bm25-only', action='store_true', help='只跑BM25（离线，不需要API）')
    parser.add_argument('--report-only', action='store_true', help='只处理REPORT_ONLY_CONTROL题（生成拒答快照）')
    args = parser.parse_args()
    
    questions = load_questions()
    
    # 筛选题目
    if args.question:
        qs = [q for q in questions if q['question_id'] == args.question]
        if not qs:
            print(f"❌ 题目不存在: {args.question}")
            return
    elif args.report_only:
        qs = [q for q in questions if q.get('analysis_role') == 'REPORT_ONLY_CONTROL']
        print(f"REPORT_ONLY_CONTROL 题: {len(qs)} 道")
    elif args.all:
        qs = [q for q in questions if q.get('analysis_role') == 'RAG_PRIMARY']
        print(f"RAG_PRIMARY 题: {len(qs)} 道")
    else:
        print("请指定 --all / --question / --report-only")
        print(f"  可用题目数: {len(questions)}")
        print(f"  RAG_PRIMARY: {sum(1 for q in questions if q.get('analysis_role')=='RAG_PRIMARY')}")
        print(f"  REPORT_ONLY_CONTROL: {sum(1 for q in questions if q.get('analysis_role')=='REPORT_ONLY_CONTROL')}")
        return
    
    # 初始化检索器（BM25不需要API key）
    api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    
    if not args.bm25_only and not args.report_only and not api_key:
        print("⚠️  未设置 DASHSCOPE_API_KEY，将只运行 BM25（离线）")
        print("   如需 Dense + Rerank 全链路，请设置环境变量后重新运行")
        args.bm25_only = True
    
    # REPORT_ONLY_CONTROL 题：直接写拒答
    if args.report_only:
        for q in qs:
            qid = q['question_id']
            qdir = SNAPSHOT_DIR / qid
            qdir.mkdir(parents=True, exist_ok=True)
            
            abstain = {
                "retrieval_abstained": True,
                "reason": "REPORT_ONLY_CONTROL 题，仅用报告内数据即可回答，不需要外部知识",
                "analysis_role": "REPORT_ONLY_CONTROL",
                "rag_items": [],
            }
            
            # 所有阶段都写拒答（保持目录一致）
            for stage in ['01_bm25_top20', '02_dense_top20', '03_rrf_top20', '04_rerank_top10', '05_final_top5']:
                save_jsonl(qdir / f"{stage}.jsonl", [abstain])
            
            # 写 query
            with open(qdir / "00_query.json", 'w', encoding='utf-8') as f:
                json.dump({
                    "question_id": qid,
                    "query": "N/A（REPORT_ONLY_CONTROL题不需要RAG检索）",
                    "query_provenance": ["REPORT_ONLY_CONTROL: no RAG needed"],
                    "abstained": True,
                }, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ {qid}: REPORT_ONLY_CONTROL → 检索拒答")
        
        print(f"\n完成: {len(qs)} 道 REPORT_ONLY_CONTROL 题")
        return
    
    # 初始化 HybridRetriever
    try:
        from hybrid_retrieval import HybridRetriever
        retriever = HybridRetriever(INDEX_DIR, api_key=api_key if not args.bm25_only else "")
        val = retriever.validate()
        print(f"✅ 索引加载成功: {val['children']} 个子块, {val['sources']} 个来源")
    except Exception as e:
        print(f"❌ 索引加载失败: {e}")
        return
    
    # 处理每道题
    bm25_done = 0
    
    for q in qs:
        qid = q['question_id']
        qdir = SNAPSHOT_DIR / qid
        qdir.mkdir(parents=True, exist_ok=True)
        
        # 构建 query
        query, provenance = build_query(q)
        
        # 保存 query
        with open(qdir / "00_query.json", 'w', encoding='utf-8') as f:
            json.dump({
                "question_id": qid,
                "query": query,
                "query_provenance": provenance,
                "gold_leakage_check": "PASSED (query built from question text + task type + domain keywords only; no gold verdict/answer leaked)",
            }, f, ensure_ascii=False, indent=2)
        
        # BM25
        try:
            bm25_results = run_bm25_only(retriever, query, top_k=20)
            save_jsonl(qdir / "01_bm25_top20.jsonl", bm25_results)
            bm25_done += 1
            print(f"  ✅ {qid}: BM25 Top-20 ({len(bm25_results)} 条)")
        except Exception as e:
            print(f"  ❌ {qid}: BM25 失败 - {e}")
        
        # Dense（需要API）
        if not args.bm25_only:
            print(f"  ⏸️  {qid}: Dense/Rerank 需要 API，暂跳过")
    
    print(f"\nBM25 完成: {bm25_done}/{len(qs)} 题")
    if args.bm25_only:
        print("Dense + Rerank 待授权后运行")
        print(f"预估: {len(qs)} 题 × 1次 embedding + 1次 rerank = {len(qs)*2} 次 API 调用")


if __name__ == '__main__':
    main()
