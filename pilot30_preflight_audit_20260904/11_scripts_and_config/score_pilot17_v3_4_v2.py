#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pilot17 v3.4 评分器 v2（GPT金标修订版）
- 基于GPT独立复核结果修订金标映射（2026-09-04）
- 新增 label_text_consistency 修正：标签与推理文字矛盾时降级处理
- 支持 --exclude 排除指定题目（如复合题）
- 新增 16 题正式统计（H1-H4 检验维度）

用法:
  python score_pilot17_v3_4_v2.py --all
  python score_pilot17_v3_4_v2.py --all --exclude PL010_VOCSTotal_Q01
"""
import argparse
import json
import re
from pathlib import Path
from collections import defaultdict

BASE = Path(r"E:\实验文件整理_按论文逻辑\实验")
RESULTS_DIR = BASE / "07_results_v2" / "pilot17_v3_4_experiment"

# ============ 金标映射 v2（GPT复核修订版，2026-09-04） ============
# 修订说明：
# - PL007_CaptureEfficiency_Q01: CORRECT → INCORRECT（打样间95%缺乏密闭负压/开口控制证据，属核心参数错误）
# - PL013_HazardousWaste_Q01: 保留 INCORRECT，但核心依据从"废机油桶代码错误"改为"危废识别完整性不足+数据矛盾"
# - PL014_CaptureAirflow_Q01: 维持 INCORRECT，补充正压/负压矛盾依据
# - PL008_DesignAirflow_Q01: 维持 PARTIALLY_CORRECT，理由从"设计不足"改为"正文与表格理论风量冲突"
# - PL010_VOCSTotal_Q01: 标记为复合题，建议从主分析排除
# - NEW_PL010_invest_ratio: 维持 INCORRECT（金标正确，模型是标签锚定问题）
# - PL005_Emission_固体: 维持 CORRECT（金标正确，模型是标准适用范围误判）
GOLD_CONCLUSION_MAP = {
    "NEW_PL001_invest_ratio":      "CORRECT",
    "NEW_PL006_invest_ratio":      "CORRECT",
    "NEW_PL015_invest_ratio":      "CORRECT",
    "NEW_PL007_ro_water":          "CORRECT",
    "NEW_PL006_living_wastewater": "CORRECT",
    "PL002_V01_Q01":               "CORRECT",
    "PL004_V01_Q01":               "CORRECT",
    "PL005_Emission_固体":          "CORRECT",
    "PL007_CaptureEfficiency_Q01": "INCORRECT",  # ← 修订：CORRECT→INCORRECT
    "PL008_VOCSMeasure_Q01":       "CORRECT",
    "NEW_PL010_invest_ratio":      "INCORRECT",
    "PL008_VOCSTotal_Q01":         "INCORRECT",
    "PL010_VOCSTotal_Q01":         "INCORRECT",  # 复合题，建议排除
    "PL013_HazardousWaste_Q01":    "INCORRECT",  # ← 依据修订（标签不变）
    "PL014_CaptureAirflow_Q01":    "INCORRECT",  # ← 依据补充（标签不变）
    "PL001_Emission_固体":          "PARTIALLY_CORRECT",
    "PL008_DesignAirflow_Q01":     "PARTIALLY_CORRECT",  # ← 理由修订（标签不变）
}
GOLD_MAP_STATUS = "GPT_REVISED_20260904"
COMPOUND_QUESTIONS = {"PL010_VOCSTotal_Q01"}  # 复合题，待拆分

# ============ conclusion 匹配矩阵 ============
MATCH_MATRIX = {
    "CORRECT": {
        "CORRECT": 5.0, "PARTIALLY_CORRECT": 4.0, "INCORRECT": 1.0, "INSUFFICIENT": 2.5,
    },
    "PARTIALLY_CORRECT": {
        "PARTIALLY_CORRECT": 5.0, "CORRECT": 3.0, "INCORRECT": 3.0, "INSUFFICIENT": 2.5,
    },
    "INCORRECT": {
        "INCORRECT": 5.0, "PARTIALLY_CORRECT": 4.0, "CORRECT": 1.0, "INSUFFICIENT": 2.5,
    },
    "INSUFFICIENT": {
        "INSUFFICIENT": 5.0, "CORRECT": 1.5, "INCORRECT": 1.5, "PARTIALLY_CORRECT": 1.5,
    },
}

VALID_ENUMS = {"CORRECT", "INCORRECT", "PARTIALLY_CORRECT", "INSUFFICIENT"}

# 标签-文字一致性检测：负面/正面判定词
NEG_JUDGMENT_WORDS = [
    '错误', '有误', '不一致', '不准确', '不合理', '应修正', '应改为',
    '应补充', '需修正', '不完整', '不充分', '缺乏依据', '不足', '缺陷',
    '偏差', '矛盾', '问题', '缺失', '遗漏', '未引用', '未明确',
]
POS_JUDGMENT_WORDS = [
    '正确', '合理', '一致', '完整', '充分', '适用', '符合',
    '基本正确', '基本合理', '恰当',
]


def detect_label_text_mismatch(conclusion, reasoning, review_opinion):
    """检测标签与推理文字是否矛盾
    返回 (is_mismatch, adjusted_label, reason)
    """
    text = f"{reasoning} {review_opinion}"
    neg = sum(text.count(w) for w in NEG_JUDGMENT_WORDS)
    pos = sum(text.count(w) for w in POS_JUDGMENT_WORDS)

    # CORRECT标签但文字负面词远多于正面 → 降级为PARTIALLY_CORRECT
    if conclusion == "CORRECT" and neg >= 2 and neg > pos + 1:
        return True, "PARTIALLY_CORRECT", f"标签CORRECT但推理含{neg}个负面判定词，疑似标签锚定误用，降级为PARTIALLY_CORRECT"
    # INCORRECT标签但文字正面词远多于负面 → 升级为PARTIALLY_CORRECT
    if conclusion == "INCORRECT" and pos >= 2 and pos > neg + 1:
        return True, "PARTIALLY_CORRECT", f"标签INCORRECT但推理以正面判定为主（{pos}个正面词），修正为PARTIALLY_CORRECT"
    return False, conclusion, ""


def score_conclusion(ans_conclusion, gold_conclusion):
    if ans_conclusion not in VALID_ENUMS:
        return 0.0, f"无效枚举值: {ans_conclusion}"
    s = MATCH_MATRIX[gold_conclusion][ans_conclusion]
    if s == 5.0:
        note = "完全匹配"
    elif s >= 4.0:
        note = "方向正确偏保守"
    elif s >= 3.0:
        note = "部分识别"
    elif s == 2.5:
        note = "未判断"
    else:
        note = "方向偏差"
    return s, note


def score_evidence(parsed, kid):
    ev = parsed.get("evidence", [])
    if not isinstance(ev, list):
        return 0.0, "evidence字段非列表"
    score = 0.0
    notes = []
    report_ev = [e for e in ev if isinstance(e, dict) and e.get("source_type") == "REPORT"]
    if report_ev:
        score += 2.0
        has_quote = any(str(e.get("quote", "")).strip() for e in report_ev)
        has_loc = any(str(e.get("location", "")).strip() for e in report_ev)
        if has_quote and has_loc:
            score += 1.0
            notes.append("报告证据含引文+位置")
    if len(ev) >= 2:
        score += 1.0
        notes.append(f"{len(ev)}条证据")
    if kid in ("K2", "K3"):
        st = "WEB" if kid == "K2" else "RAG"
        if any(isinstance(e, dict) and e.get("source_type") == st for e in ev):
            score += 1.0
            notes.append(f"利用{st}证据")
    return min(score, 5.0), "; ".join(notes) if notes else "证据薄弱"


def load_records():
    all_records = []
    for fname in ["pilot17_v3_4_batch1_raw_results.jsonl", "pilot17_v3_4_batch2_raw_results.jsonl"]:
        fpath = RESULTS_DIR / fname
        if not fpath.exists():
            continue
        for line in open(fpath, encoding="utf-8"):
            if line.strip():
                all_records.append(json.loads(line))
    # 去重：同run_id取最后一条
    rows = {}
    for r in all_records:
        rows[r["run_id"]] = r
    return list(rows.values())


def score_all(exclude_questions=None, enable_label_fix=True):
    exclude = set(exclude_questions or [])
    runs = load_records()
    scored = []
    mismatch_count = 0

    for r in runs:
        qid = r["question_id"]
        if qid in exclude:
            continue
        kid = r.get("knowledge_condition", "")
        gold = GOLD_CONCLUSION_MAP.get(qid, "UNKNOWN")
        ans = r.get("raw_answer", "")

        parsed = None
        if r.get("is_valid_json") and ans.strip():
            try:
                parsed = json.loads(ans)
            except json.JSONDecodeError:
                pass

        if r.get("status") == "SKIPPED":
            cs, cn = 0.0, "输入跳过"
            es, en = 0.0, ""
            ans_conc = "-"
            label_fix_note = ""
        elif parsed is None:
            cs, cn = 0.0, "JSON解析失败" if ans.strip() else "空输出"
            es, en = 0.0, ""
            ans_conc = "-"
            label_fix_note = ""
        else:
            ans_conc_raw = str(parsed.get("conclusion", "")).strip()
            reasoning = str(parsed.get("reasoning", ""))
            review_op = str(parsed.get("review_opinion", ""))

            if enable_label_fix:
                is_mismatch, ans_conc, fix_reason = detect_label_text_mismatch(
                    ans_conc_raw, reasoning, review_op)
                if is_mismatch:
                    mismatch_count += 1
                    label_fix_note = f"[标签修正] {fix_reason}"
                else:
                    label_fix_note = ""
            else:
                ans_conc = ans_conc_raw
                label_fix_note = ""

            cs, cn = score_conclusion(ans_conc, gold)
            es, en = score_evidence(parsed, kid)

        scored.append({
            "run_id": r["run_id"], "question_id": qid,
            "model_id": r.get("model_id", ""), "model_name": r.get("model_name", ""),
            "knowledge_condition": kid,
            "status": r.get("status", ""), "finish_reason": r.get("finish_reason", ""),
            "gold_conclusion": gold,
            "answer_conclusion_raw": (parsed or {}).get("conclusion", "-") if parsed else "-",
            "answer_conclusion": ans_conc if parsed else "-",
            "conclusion_score": cs, "conclusion_note": cn,
            "label_fix_note": label_fix_note,
            "evidence_score": es, "evidence_note": en,
            "confidence": (parsed or {}).get("confidence", "-") if parsed else "-",
            "output_tokens": r.get("output_tokens"),
            "input_tokens": r.get("input_tokens"),
            "latency": r.get("latency"),
        })

    return scored, mismatch_count


def print_summary(scored, mismatch_count, exclude):
    ok_runs = [s for s in scored if s["status"] in ("OK", "TRUNCATED")]
    n_ok = len(ok_runs)
    n_total = len(scored)

    print("=" * 90)
    print(f"Pilot17 v3.4 重评分结果（金标 v2: {GOLD_MAP_STATUS}）")
    print("=" * 90)
    print(f"总run数: {n_total}  |  可评分: {n_ok}  |  排除题目: {exclude or '无'}")
    print(f"标签-文字不一致修正: {mismatch_count} 条")

    # 模型 × 知识条件 矩阵
    print("\n" + "=" * 90)
    print("conclusion_score 均值矩阵（模型 × 知识条件）")
    print("=" * 90)
    models = sorted({s["model_id"] for s in ok_runs})
    kcs = sorted({s["knowledge_condition"] for s in ok_runs})
    header = f"{'模型':<8}" + "".join(f"{k:<10}" for k in kcs) + "均值"
    print(header)
    for m in models:
        row = f"{m:<8}"
        vals = []
        for k in kcs:
            cell = [s["conclusion_score"] for s in ok_runs if s["model_id"] == m and s["knowledge_condition"] == k]
            if cell:
                avg = sum(cell) / len(cell)
                vals.append(avg)
                row += f"{avg:<10.2f}"
            else:
                row += f"{'—':<10}"
        row += f"{sum(vals)/len(vals):.2f}" if vals else ""
        print(row)

    # 知识条件增益（跨模型平均）
    print("\n" + "=" * 90)
    print("知识条件增益（K2/K3 vs K1 提升）")
    print("=" * 90)
    kc_avg = {}
    for k in kcs:
        vals = [s["conclusion_score"] for s in ok_runs if s["knowledge_condition"] == k]
        kc_avg[k] = sum(vals) / len(vals) if vals else 0
    for k in kcs:
        if k == "K1":
            print(f"  {k}: {kc_avg[k]:.2f} （基准）")
        else:
            delta = kc_avg[k] - kc_avg.get("K1", 0)
            pct = (delta / kc_avg.get("K1", 1)) * 100 if kc_avg.get("K1") else 0
            print(f"  {k}: {kc_avg[k]:.2f} （+{delta:+.2f}, {pct:+.1f}%）")

    # 题目维度
    print("\n" + "=" * 90)
    print("题目维度：各题平均conclusion_score（从低到高）")
    print("=" * 90)
    q_avg = {}
    for qid in sorted({s["question_id"] for s in ok_runs}):
        vals = [s["conclusion_score"] for s in ok_runs if s["question_id"] == qid]
        q_avg[qid] = sum(vals) / len(vals) if vals else 0
    for qid, avg in sorted(q_avg.items(), key=lambda x: x[1]):
        gold = GOLD_CONCLUSION_MAP.get(qid, "?")
        vals = [s["conclusion_score"] for s in ok_runs if s["question_id"] == qid]
        perfect = sum(1 for v in vals if v == 5.0)
        print(f"  {qid:<40s} 金标{gold:<19s} 均分 {avg:.2f}  完全匹配 {perfect}/{len(vals)}")

    # 证据评分
    print("\n" + "=" * 90)
    print("evidence_score 均值")
    print("=" * 90)
    for m in models:
        for k in kcs:
            cell = [s["evidence_score"] for s in ok_runs if s["model_id"] == m and s["knowledge_condition"] == k]
            if cell:
                avg = sum(cell) / len(cell)
                print(f"  {m} {k}: {avg:.2f}")

    # 质量门禁
    print("\n" + "=" * 90)
    print("质量门禁")
    print("=" * 90)
    if n_ok:
        trunc = sum(1 for s in ok_runs if s["status"] == "TRUNCATED")
        bad_json = sum(1 for s in ok_runs if s["answer_conclusion"] == "-")
        empty = sum(1 for s in ok_runs if not s["output_tokens"])
        avg_c = sum(s["conclusion_score"] for s in ok_runs) / n_ok
        avg_e = sum(s["evidence_score"] for s in ok_runs) / n_ok
        checks = [
            ("截断率 < 5%", trunc / n_ok < 0.05, f"{trunc}/{n_ok} ({trunc/n_ok*100:.1f}%)"),
            ("JSON可解析率 = 100%", bad_json == 0, f"{n_ok-bad_json}/{n_ok}"),
            ("无空输出", empty == 0, f"{empty}/{n_ok}"),
            ("平均conclusion分 > 2.5", avg_c > 2.5, f"{avg_c:.2f}"),
            ("平均evidence分 > 2.0", avg_e > 2.0, f"{avg_e:.2f}"),
        ]
        all_pass = True
        for name, ok, detail in checks:
            print(f"  {'✅' if ok else '🔴'} {name}: {detail}")
            all_pass = all_pass and ok
        print(f"\n{'🟢 全部通过' if all_pass else '🔴 存在问题'}")

    return {
        "n_total": n_total, "n_ok": n_ok,
        "mismatch_count": mismatch_count,
        "models": models, "kcs": kcs,
    }


def h_tests(scored):
    """H1-H4 统计检验（简化版：均值比较 + 效应量）"""
    ok = [s for s in scored if s["status"] in ("OK", "TRUNCATED")]
    print("\n" + "=" * 90)
    print("假设检验初步结果（H1-H4，基于均值差）")
    print("=" * 90)

    # H1: 模型能力梯度（A3 > A2 > A1）
    models = sorted({s["model_id"] for s in ok})
    m_score = {}
    for m in models:
        vals = [s["conclusion_score"] for s in ok if s["model_id"] == m]
        m_score[m] = sum(vals) / len(vals) if vals else 0
    print(f"\nH1（模型能力梯度）: ", end="")
    if len(models) >= 3:
        ordered = sorted(m_score.items(), key=lambda x: -x[1])
        print(" → ".join(f"{m}={v:.2f}" for m, v in ordered))
        # 检查是否A3>A2>A1
        ids = ["A1", "A2", "A3"]
        scores = [m_score.get(m, 0) for m in ids]
        if scores[2] >= scores[1] >= scores[0]:
            print("  ✅ 符合预期梯度 A3≥A2≥A1")
        else:
            print("  ⚠️ 不符合严格梯度（轻量模型反超旗舰，符合之前发现）")

    # H2: 知识条件增益（K3 > K2 > K1）
    kcs = sorted({s["knowledge_condition"] for s in ok})
    k_score = {}
    for k in kcs:
        vals = [s["conclusion_score"] for s in ok if s["knowledge_condition"] == k]
        k_score[k] = sum(vals) / len(vals) if vals else 0
    print(f"\nH2（知识条件增益）: ", end="")
    ordered = sorted(k_score.items(), key=lambda x: -x[1])
    print(" → ".join(f"{k}={v:.2f}" for k, v in ordered))
    if len(kcs) >= 3:
        if k_score.get("K3", 0) >= k_score.get("K2", 0) >= k_score.get("K1", 0):
            print("  ✅ 符合预期 K3≥K2≥K1")
        else:
            print("  ⚠️ 知识条件增益不完全符合预期")

    # H3: 模型×知识交互（强模型从知识中获益更少）
    print(f"\nH3（模型×知识交互）: ")
    for m in models:
        k1 = [s["conclusion_score"] for s in ok if s["model_id"] == m and s["knowledge_condition"] == "K1"]
        k3 = [s["conclusion_score"] for s in ok if s["model_id"] == m and s["knowledge_condition"] == "K3"]
        if k1 and k3:
            gain = (sum(k3)/len(k3)) - (sum(k1)/len(k1))
            print(f"  {m}: K3-K1 = {gain:+.2f}")

    # H4: 任务类型差异
    # 按task_module粗分：计算类、标准类、一致性类、识别类
    print(f"\nH4（任务类型差异）: ")
    task_types = defaultdict(list)
    for s in ok:
        qid = s["question_id"]
        if "invest_ratio" in qid or "DesignAirflow" in qid or "CaptureAirflow" in qid:
            t = "计算/核算类"
        elif "Emission" in qid or "HazardousWaste" in qid:
            t = "标准/识别类"
        elif "VOCSTotal" in qid or "VOCSMeasure" in qid or "CaptureEfficiency" in qid:
            t = "一致性/参数判断类"
        elif "V01" in qid or "living_wastewater" in qid or "ro_water" in qid:
            t = "分类判断类"
        else:
            t = "其他"
        task_types[t].append(s["conclusion_score"])
    for t, vals in sorted(task_types.items(), key=lambda x: -sum(x[1])/len(x[1])):
        avg = sum(vals) / len(vals)
        print(f"  {t}: {avg:.2f} (n={len(vals)})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="评分全部批次")
    parser.add_argument("--exclude", default="", help="排除题目，逗号分隔")
    parser.add_argument("--no-label-fix", action="store_true", help="禁用标签-文字一致性修正")
    args = parser.parse_args()

    exclude = [q.strip() for q in args.exclude.split(",") if q.strip()] if args.exclude else []
    enable_fix = not args.no_label_fix

    scored, mismatch = score_all(exclude_questions=exclude, enable_label_fix=enable_fix)
    stats = print_summary(scored, mismatch, exclude)
    h_tests(scored)

    # 输出
    suffix = "v2"
    if exclude:
        suffix += f"_exclude_{len(exclude)}q"
    if not enable_fix:
        suffix += "_nolabelfix"
    out_json = RESULTS_DIR / f"pilot17_v3_4_full_scored_{suffix}.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "gold_map_status": GOLD_MAP_STATUS,
            "scorer_version": "v2_gpt_revised",
            "label_text_fix": enable_fix,
            "excluded_questions": exclude,
            "stats": stats,
            "runs": scored,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n评分结果 → {out_json.name}")


if __name__ == "__main__":
    main()
