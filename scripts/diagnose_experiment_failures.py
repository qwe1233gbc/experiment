#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pilot17 实验失败原因排查工具
=================================
对 3x3 实验 153 条唯一记录逐条诊断失败原因（多标签），
按题目聚合生成重跑裁决：哪些题不用再做 / 哪些要重跑 / 重跑前必须先修什么。

原因分类体系（结合本项目已知问题整理）:
  [运行层]  E1_API_ERROR          API调用失败
            E2_TRUNC_EMPTY        截断且答案为空（reasoning耗尽token）
            E3_TRUNC_PARTIAL      截断但有部分输出
            E4_FORMAT_NOT_JSON    OK但输出为Markdown非JSON（输出协议缺陷）
  [输入层]  I1_NO_REPORT          error_no_report，报告上下文未加载
            I2_CTX_SECTION_DEFECT PL010章节点识别失效（上下文质量缺陷）
            I3_WEB_EMPTY          K2条件Web搜索0结果（知识操纵失效）
            I4_RAG_INSTRUCTION    K3条件RAG证据含指令型文档（格式污染）
            I5_WEB_SNAPSHOT_DRIFT 运行时Web快照与当前快照哈希不一致（复现性缺陷）
  [协议层]  P1_PROMPT_CHANGED     系统Prompt将v2→v3，旧结果与新结果不可混用
  [评分层]  S1_GOLD_UNCONFIRMED   金标未人工确认（评分阻断）
            S2_GOLD_SUSPECT       PL008金标存疑
"""
import json
import csv
import hashlib
from pathlib import Path
from collections import Counter, defaultdict

BASE = Path(r"E:\实验文件整理_按论文逻辑\实验")
REPAIR_DIR = BASE / "07_results_v2" / "pilot17_repair_20260903"

RESULTS_3X3 = BASE / "07_results_v2/v3.3_3x3_experiment/pilot16_v3_3_3x3_raw_results.jsonl"
WEB_SNAPSHOT = BASE / "03_knowledge_base/pilot16_web_snapshot_v3_3.jsonl"
RAG_V33 = BASE / "03_knowledge_base/pilot16_rag_snapshot_v3_3.jsonl"
RAG_V34 = REPAIR_DIR / "pilot17_rag_snapshot_candidate_v3_4.jsonl"
VALIDATION_5 = REPAIR_DIR / "validation_5_runs.jsonl"

# 已知静态缺陷表（来自全链路审计，人工核验）
KNOWN_CTX_DEFECT_QUESTIONS = {"PL010_VOCSTotal_Q01"}          # 章节误判（NEW_PL010待查input_status）
KNOWN_GOLD_SUSPECT = {"PL008_VOCSMeasure_Q01"}                # INSUFFICIENT存疑
INSTRUCTION_DOC_KEYWORDS = ("审核指南", "核算指南", "审查要点", "工作指引", "审核要点", "检查表")


def load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def parse_json_answer(text):
    if not text or not str(text).strip():
        return False
    t = str(text).strip()
    if t.startswith("```"):
        t = t.strip("`").lstrip("json").strip()
    try:
        json.loads(t)
        return True
    except Exception:
        return False


def main():
    # ---------- 数据加载 ----------
    raw = load_jsonl(RESULTS_3X3)
    rows = {}
    for r in raw:                      # 去重：同run_id取最后一条
        rows[r["run_id"]] = r
    runs = list(rows.values())
    print(f"3x3原始行数 {len(raw)} → 唯一run {len(runs)}")

    # Web快照（当前磁盘版本）
    web_snap = {r["question_id"]: r for r in load_jsonl(WEB_SNAPSHOT)}
    # RAG v3_3原始快照（扁平结构：每行一条证据，按题聚合）
    rag33 = defaultdict(list)
    for r in load_jsonl(RAG_V33):
        rag33[r["question_id"]].append(r)
    # RAG v3_4候选（指令型证据已被移除的版本）
    rag34 = defaultdict(list)
    for r in load_jsonl(RAG_V34):
        rag34[r["question_id"]].append(r)
    print(f"RAG快照: v3_3共{sum(len(v) for v in rag33.values())}条证据, "
          f"v3_4候选共{sum(len(v) for v in rag34.values())}条 "
          f"(移除{sum(len(v) for v in rag33.values()) - sum(len(v) for v in rag34.values())}条指令型)")

    # ---------- 逐run诊断 ----------
    per_run = []
    for r in runs:
        causes = []
        status = (r.get("status") or "").upper()
        ans = str(r.get("raw_answer") or "")
        qid = r["question_id"]
        kc = r.get("knowledge_condition", "")

        # 运行层
        if "ERROR" in status:
            causes.append("E1_API_ERROR")
        if "TRUNC" in status:
            causes.append("E2_TRUNC_EMPTY" if not ans.strip() else "E3_TRUNC_PARTIAL")
        elif status == "OK" and not parse_json_answer(ans):
            causes.append("E4_FORMAT_NOT_JSON")

        # 输入层
        if r.get("input_status") == "error_no_report":
            causes.append("I1_NO_REPORT")
        if qid in KNOWN_CTX_DEFECT_QUESTIONS:
            causes.append("I2_CTX_SECTION_DEFECT")
        if kc == "K2":
            snap = web_snap.get(qid)
            # 运行时0结果，或当前快照0结果（重跑时将踩坑），任一命中即标记
            if (r.get("web_search_count") or 0) == 0 or (snap and (snap.get("result_count") or 0) == 0):
                causes.append("I3_WEB_EMPTY")
            if snap and r.get("web_search_hash") and r["web_search_hash"] != snap.get("result_hash"):
                causes.append("I5_WEB_SNAPSHOT_DRIFT")
        if kc == "K3":
            # 指令型证据在v3_4候选快照中被整体移除（而非打标记），故在v3_3中找"v3_4里已消失的证据"
            s33 = {h.get("source_file") for h in rag33.get(qid, [])}
            s34 = {h.get("source_file") for h in rag34.get(qid, [])}
            removed = s33 - s34
            if removed:
                causes.append("I4_RAG_INSTRUCTION")

        # 协议层（全局）
        causes.append("P1_PROMPT_CHANGED")
        # 评分层（全局）
        causes.append("S1_GOLD_UNCONFIRMED")
        if qid in KNOWN_GOLD_SUSPECT:
            causes.append("S2_GOLD_SUSPECT")

        per_run.append({
            "run_id": r["run_id"], "question_id": qid, "task_type": r.get("task_type", ""),
            "model": r.get("model_id", ""), "kc": kc, "status": status,
            "input_status": r.get("input_status", ""),
            "output_tokens": r.get("output_tokens"),
            "answer_chars": len(ans),
            "causes": causes,
            "is_valid_data": (not any(c.startswith(("E", "I")) for c in causes)),
        })

    # ---------- 按题聚合 ----------
    by_q = defaultdict(list)
    for p in per_run:
        by_q[p["question_id"]].append(p)

    question_rows = []
    for qid in sorted(by_q):
        rs = by_q[qid]
        cause_counter = Counter(c for p in rs for c in p["causes"] if not c.startswith(("P", "S")))
        input_defects = sorted({c for p in rs for c in p["causes"] if c.startswith("I")})
        valid = sum(1 for p in rs if p["is_valid_data"])

        if any(c in input_defects for c in ("I1_NO_REPORT", "I2_CTX_SECTION_DEFECT", "I3_WEB_EMPTY", "I4_RAG_INSTRUCTION", "I5_WEB_SNAPSHOT_DRIFT")):
            verdict = "先修输入再重跑"
        else:
            verdict = "脚本升级后直接重跑"

        prereq = []
        if "I1_NO_REPORT" in input_defects:
            prereq.append("修复报告JSON加载")
        if "I2_CTX_SECTION_DEFECT" in input_defects:
            prereq.append("修复PL010章节分类")
        if "I3_WEB_EMPTY" in input_defects:
            prereq.append("重写Web搜索query并重新冻结快照")
        if "I4_RAG_INSTRUCTION" in input_defects:
            prereq.append("启用RAG v3_4过滤快照")
        if "I5_WEB_SNAPSHOT_DRIFT" in input_defects:
            prereq.append("重新冻结Web快照并对齐hash")
        if not prereq:
            prereq.append("无（仅需脚本升级+金标确认")

        question_rows.append({
            "question_id": qid,
            "task_type": rs[0]["task_type"],
            "runs": len(rs),
            "valid_runs": valid,
            "truncated": cause_counter.get("E2_TRUNC_EMPTY", 0) + cause_counter.get("E3_TRUNC_PARTIAL", 0),
            "empty_truncated": cause_counter.get("E2_TRUNC_EMPTY", 0),
            "format_bad": cause_counter.get("E4_FORMAT_NOT_JSON", 0),
            "no_report": cause_counter.get("I1_NO_REPORT", 0),
            "input_defects": ";".join(input_defects),
            "verdict": verdict,
            "prerequisites": ";".join(prereq),
        })

    # ---------- 可续用判定（validation_5，按run自身的知识条件判断） ----------
    # I5快照漂移只影响K2且重跑读新快照时自动对齐，不作run级阻断
    KC_RELEVANT_DEFECTS = {
        "K1": {"I1_NO_REPORT", "I2_CTX_SECTION_DEFECT"},
        "K2": {"I1_NO_REPORT", "I2_CTX_SECTION_DEFECT", "I3_WEB_EMPTY"},
        "K3": {"I1_NO_REPORT", "I2_CTX_SECTION_DEFECT", "I4_RAG_INSTRUCTION"},
    }
    q_input_defects = {q["question_id"]: set(q["input_defects"].split(";")) - {""} for q in question_rows}
    v5 = load_jsonl(VALIDATION_5)
    v5_reusable = []
    for v in v5:
        qid, mk = v["run_id"].rsplit("__", 1)      # mk形如 A1_K3
        kc = mk.split("_", 1)[1] if "_" in mk else mk
        defects = q_input_defects.get(qid, set())
        relevant = KC_RELEVANT_DEFECTS.get(kc, set())
        if v.get("is_valid_json") and v.get("status") == "OK" and not (defects & relevant):
            v5_reusable.append(f"{v['run_id']}（prompt_hash {v['prompt_hash'][:12]}）")

    # ---------- 输出 ----------
    out_run_csv = REPAIR_DIR / "17_failure_diagnosis_per_run.csv"
    with open(out_run_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(per_run[0].keys()))
        w.writeheader()
        for p in per_run:
            w.writerow({**p, "causes": ";".join(p["causes"])})
    print(f"\n逐run诊断 → {out_run_csv.name} ({len(per_run)}行)")

    out_q_csv = REPAIR_DIR / "18_question_redo_plan.csv"
    with open(out_q_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(question_rows[0].keys()))
        w.writeheader()
        w.writerows(question_rows)
    print(f"题目重跑计划 → {out_q_csv.name} ({len(question_rows)}行)")

    # ---------- 控制台摘要 ----------
    print("\n" + "=" * 78)
    print("失败原因总览（153条唯一run，多标签）")
    print("=" * 78)
    all_causes = Counter(c for p in per_run for c in p["causes"])
    for c, n in all_causes.most_common():
        print(f"  {c:<24} {n:>4} 条 ({n/len(per_run)*100:.1f}%)")

    print("\n" + "=" * 78)
    print("题目裁决表（17题）")
    print("=" * 78)
    for q in question_rows:
        flag = "🔴" if q["verdict"] == "先修输入再重跑" else "🟢"
        print(f"{flag} {q['question_id']:<32} {q['task_type'][:12]:<14} "
              f"有效{q['valid_runs']}/9 | 截断{q['truncated']} 格式坏{q['format_bad']} 无报告{q['no_report']}")
        if q["prerequisites"] != "无（仅需脚本升级+金标确认":
            print(f"     └ 前置: {q['prerequisites']}")

    n_fix_first = sum(1 for q in question_rows if q["verdict"] == "先修输入再重跑")
    print(f"\n先修输入再重跑: {n_fix_first} 题 | 脚本升级后直接重跑: {len(question_rows)-n_fix_first} 题")
    print(f"\n可续用的已验证run（v3协议+输入无缺陷+有效JSON）: {len(v5_reusable)} 条")
    for s in v5_reusable:
        print(f"  ✅ {s}")


if __name__ == "__main__":
    main()
