"""ABCD四组实验分数分析 — 对齐Zhou论文指标体系。
输出：
1. 各组各维度代理得分（0-2分制）
2. 转换为5分制Likert量表（与Zhou论文Table 4可比）
3. 交叉对比汇总CSV
4. 可视化对比图
"""
from __future__ import annotations
import csv
import json
import statistics
from pathlib import Path
from collections import defaultdict

# ─── 路径 ───
REPO = Path(r"E:\华南理工项目\环评文件汇总\01_GitHub项目与研究文档\eia-openclaw-sync-chen2026\10_消融实验设计")
CSV_PATHS = {
    "A": REPO / r"06_Qwen3.8Max_A组_20260806\run_20260806_222338\run_matrix_a.csv",
    "B": REPO / r"07_Qwen3.8Max_B组_20260807\run_20260807_215254\run_matrix_b.csv",
    "C": REPO / r"05_Qwen3.8Max_CD重跑_20260806\run_20260806_164352\run_matrix_cd.csv",  # C和D在同一文件
    "D": REPO / r"05_Qwen3.8Max_CD重跑_20260806\run_20260806_164352\run_matrix_cd.csv",
}
OUTPUT_DIR = Path(r"C:\Users\ylx\AppData\Roaming\TRAE SOLO CN\ModularData\ai-agent\work-mode-projects\6a789bcfc2e5f7d2fcd33cd3\实验文件整理_按论文逻辑")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_rows(csv_path: Path, group_filter: str = None) -> list[dict]:
    """读取CSV并解析output_json字段。"""
    rows = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if group_filter and r.get("group", "") != group_filter:
                continue
            # 解析output_json
            oj_str = r.get("output_json", "")
            try:
                oj = json.loads(oj_str) if oj_str else {}
            except json.JSONDecodeError:
                oj = {}
            r["_json"] = oj
            rows.append(r)
    return rows


def score_correctness(oj: dict) -> float:
    """判断正确性 (0-2) → Zhou's Correctness。
    基于judgement和answer_mode的代理评分。
    """
    judgement = oj.get("final_answer", {}).get("judgement", "")
    answer_mode = oj.get("answer_mode", "")
    
    # definitive judgment + complete process
    if judgement in ("正确", "存在问题") and answer_mode == "full_validation":
        return 2.0
    # definitive judgment + internal only (no external needed or performed)
    if judgement in ("正确", "存在问题") and answer_mode == "determinate_internal":
        return 1.5
    # partial completion
    if judgement == "部分完成":
        return 1.0
    # needs manual review but did some work
    if judgement == "待人工复核" and answer_mode in ("partial_internal", "full_validation"):
        return 0.5
    # couldn't complete
    return 0.0


def score_evidence(oj: dict) -> float:
    """证据使用 (0-2) → Zhou's Completeness。
    基于evidence数组长度。
    """
    evidence = oj.get("report_internal_result", {}).get("evidence", [])
    n = len(evidence) if isinstance(evidence, list) else 0
    if n >= 2:
        return 2.0
    elif n == 1:
        return 1.0
    return 0.0


def score_actionability(oj: dict) -> float:
    """审核意见可执行性 (0-2) → Zhou's Clarity。
    基于checks完成数和issues识别数。
    """
    checks = oj.get("report_internal_result", {}).get("checks", [])
    issues = oj.get("report_internal_result", {}).get("issues", [])
    n_checks = len(checks) if isinstance(checks, list) else 0
    n_issues = len(issues) if isinstance(issues, list) else 0
    
    if n_checks >= 2 and n_issues >= 1:
        return 2.0
    elif n_checks >= 2 or n_issues >= 1:
        return 1.5
    elif n_checks >= 1:
        return 1.0
    return 0.0


def score_regulatory(oj: dict) -> float:
    """法规依据使用 (0-2) → Zhou's Compliance。
    基于external_validation_result。
    """
    ext = oj.get("external_validation_result", {})
    status = ext.get("status", "")
    refs = ext.get("references_used", [])
    n_refs = len(refs) if isinstance(refs, list) else 0
    
    if status == "verified" and n_refs >= 2:
        return 2.0
    elif status == "verified" and n_refs >= 1:
        return 1.5
    elif status == "not_required":
        return 1.5
    elif status == "insufficient_reference" and n_refs >= 1:
        return 1.0
    elif status == "insufficient_reference":
        return 0.5
    # not_performed
    return 0.0


def score_skill_workflow(oj: dict, group: str) -> float:
    """技能流程使用 (0-2) — 本实验特有维度，Zhou论文无直接对应。
    A组/B组：无Skill输入，记为N/A。
    C组/D组：基于skill_id存在性和结构化输出质量。
    """
    if group in ("A", "B"):
        return float("nan")  # N/A
    
    skill_id = oj.get("skill_id", "")
    checks = oj.get("report_internal_result", {}).get("checks", [])
    calcs = oj.get("report_internal_result", {}).get("calculations", [])
    n_checks = len(checks) if isinstance(checks, list) else 0
    n_calcs = len(calcs) if isinstance(calcs, list) else 0
    
    if skill_id and n_checks >= 2 and n_calcs >= 1:
        return 2.0
    elif skill_id and n_checks >= 1:
        return 1.5
    elif skill_id:
        return 1.0
    return 0.0


def to_likert5(score_2pt: float) -> float:
    """将0-2分制转换为1-5分Likert量表（与Zhou论文Table 4可比）。
    0→1, 0.5→2, 1→3, 1.5→4, 2→5
    """
    if score_2pt != score_2pt:  # NaN check
        return float("nan")
    return 1.0 + (score_2pt / 2.0) * 4.0


# ─── Zhou论文参考数据 ───
ZHOU_EXPERT = {
    # model: {Correctness, Completeness, Compliance, Clarity, Average}
    "GPT-4o":    {"Correctness": 3.7, "Completeness": 4.1, "Compliance": 3.1, "Clarity": 4.4, "Average": 3.83},
    "Qwen3-8B":  {"Correctness": 4.0, "Completeness": 3.7, "Compliance": 3.7, "Clarity": 4.0, "Average": 3.85},
    "FT":        {"Correctness": 4.0, "Completeness": 3.8, "Compliance": 3.9, "Clarity": 4.0, "Average": 3.93},
    "RAG":       {"Correctness": 4.2, "Completeness": 3.7, "Compliance": 4.0, "Clarity": 3.9, "Average": 3.95},
    "RAG+FT":    {"Correctness": 4.2, "Completeness": 3.9, "Compliance": 4.1, "Clarity": 4.1, "Average": 4.08},
}

# 映射：我们的组 → Zhou论文对应模型
GROUP_TO_ZHOU = {
    "A": "Qwen3-8B",   # LLM only (baseline)
    "B": "RAG",        # LLM + RAG
    "C": "FT",         # LLM + Skill (domain adaptation)
    "D": "RAG+FT",     # LLM + RAG + Skill
}

DIMENSION_MAP = {
    "判断正确性": ("Correctness", score_correctness),
    "证据使用": ("Completeness", score_evidence),
    "审核意见可执行性": ("Clarity", score_actionability),
    "法规依据使用": ("Compliance", score_regulatory),
    "技能流程使用": ("Skill_Workflow", score_skill_workflow),  # 无Zhou对应
}


def main():
    # 加载所有组数据
    all_rows = {}
    all_rows["A"] = load_rows(CSV_PATHS["A"])
    all_rows["B"] = load_rows(CSV_PATHS["B"])
    all_rows["C"] = load_rows(CSV_PATHS["C"], "C")
    all_rows["D"] = load_rows(CSV_PATHS["D"], "D")
    
    print(f"各组题目数: A={len(all_rows['A'])}, B={len(all_rows['B'])}, C={len(all_rows['C'])}, D={len(all_rows['D'])}")
    
    # 计算每题每维度得分
    per_question_scores = {}  # {group: [{question_id, scores...}]}
    for group, rows in all_rows.items():
        per_question_scores[group] = []
        for r in rows:
            oj = r["_json"]
            qid = r.get("question_id", "")
            
            scores = {}
            for dim_name, (zhou_name, scorer) in DIMENSION_MAP.items():
                if dim_name == "技能流程使用":
                    raw = scorer(oj, group)
                else:
                    raw = scorer(oj)
                scores[dim_name] = raw
                scores[f"{dim_name}_5pt"] = to_likert5(raw)
            
            per_question_scores[group].append({
                "question_id": qid,
                "group": group,
                **scores,
            })
    
    # 计算各组各维度平均分
    print("\n" + "="*80)
    print("各组各维度平均得分（0-2分制）")
    print("="*80)
    
    group_avg_2pt = {}  # {group: {dim: avg}}
    group_avg_5pt = {}
    
    for group in ["A", "B", "C", "D"]:
        group_avg_2pt[group] = {}
        group_avg_5pt[group] = {}
        
        for dim_name in DIMENSION_MAP:
            scores_2pt = [q[dim_name] for q in per_question_scores[group] 
                         if q[dim_name] == q[dim_name]]  # filter NaN
            scores_5pt = [q[f"{dim_name}_5pt"] for q in per_question_scores[group]
                         if q[f"{dim_name}_5pt"] == q[f"{dim_name}_5pt"]]
            
            if scores_2pt:
                avg_2pt = statistics.mean(scores_2pt)
                group_avg_2pt[group][dim_name] = avg_2pt
                group_avg_5pt[group][dim_name] = to_likert5(avg_2pt)
                n = len(scores_2pt)
                sd = statistics.stdev(scores_2pt) if len(scores_2pt) > 1 else 0
                print(f"  {group}组 {dim_name}: {avg_2pt:.2f} (5pt: {to_likert5(avg_2pt):.2f}) [n={n}, SD={sd:.2f}]")
            else:
                group_avg_2pt[group][dim_name] = float("nan")
                group_avg_5pt[group][dim_name] = float("nan")
                print(f"  {group}组 {dim_name}: N/A")
        
        # 计算可比4维度平均（排除技能流程使用）
        comparable_dims = ["判断正确性", "证据使用", "审核意见可执行性", "法规依据使用"]
        comp_scores_5pt = [group_avg_5pt[group][d] for d in comparable_dims 
                          if group_avg_5pt[group][d] == group_avg_5pt[group][d]]
        if comp_scores_5pt:
            avg_4 = statistics.mean(comp_scores_5pt)
            print(f"  {group}组 可比4维度平均(5pt): {avg_4:.2f}")
        
        # 全5维度平均（包括技能流程使用，仅C/D）
        all_dims = list(DIMENSION_MAP.keys())
        all_scores_5pt = [group_avg_5pt[group][d] for d in all_dims 
                         if group_avg_5pt[group][d] == group_avg_5pt[group][d]]
        if all_scores_5pt:
            avg_all = statistics.mean(all_scores_5pt)
            print(f"  {group}组 全维度平均(5pt): {avg_all:.2f}")
        print()
    
    # ─── 输出对比表 ───
    print("\n" + "="*80)
    print("与Zhou论文Table 4对比（5分制Likert）")
    print("="*80)
    
    # 对应Zhou的4维度
    zhou_dims = ["判断正确性", "证据使用", "审核意见可执行性", "法规依据使用"]
    zhou_dim_names = ["Correctness", "Completeness", "Clarity", "Compliance"]
    
    print(f"\n{'组别':<6} {'对应Zhou模型':<12} {'Correctness':>12} {'Completeness':>12} {'Compliance':>12} {'Clarity':>12} {'Average':>10}")
    print("-" * 80)
    
    for group in ["A", "B", "C", "D"]:
        zhou_model = GROUP_TO_ZHOU[group]
        zhou_data = ZHOU_EXPERT[zhou_model]
        
        our_scores = [group_avg_5pt[group][d] for d in zhou_dims]
        our_avg = statistics.mean(our_scores) if all(s == s for s in our_scores) else float("nan")
        
        print(f"{group}组(我们) {'':>12} {our_scores[0]:>12.2f} {our_scores[1]:>12.2f} {our_scores[3]:>12.2f} {our_scores[2]:>12.2f} {our_avg:>10.2f}")
        print(f"  ↕Zhou {zhou_model:>12} {zhou_data['Correctness']:>12.1f} {zhou_data['Completeness']:>12.1f} {zhou_data['Compliance']:>12.1f} {zhou_data['Clarity']:>12.1f} {zhou_data['Average']:>10.2f}")
        print()
    
    # ─── 输出详细CSV ───
    # 1. 每题得分
    detail_path = OUTPUT_DIR / "abcd_per_question_scores.csv"
    with detail_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        header = ["question_id", "group", 
                  "判断正确性_2pt", "判断正确性_5pt",
                  "证据使用_2pt", "证据使用_5pt",
                  "审核意见可执行性_2pt", "审核意见可执行性_5pt",
                  "法规依据使用_2pt", "法规依据使用_5pt",
                  "技能流程使用_2pt", "技能流程使用_5pt",
                  "可比4维度均值_5pt"]
        writer.writerow(header)
        
        for group in ["A", "B", "C", "D"]:
            for q in per_question_scores[group]:
                comp_dims_5pt = [q[f"{d}_5pt"] for d in ["判断正确性", "证据使用", "审核意见可执行性", "法规依据使用"]
                                if q[f"{d}_5pt"] == q[f"{d}_5pt"]]
                avg_4 = statistics.mean(comp_dims_5pt) if comp_dims_5pt else ""
                
                writer.writerow([
                    q["question_id"], q["group"],
                    f"{q['判断正确性']:.1f}", f"{q['判断正确性_5pt']:.2f}",
                    f"{q['证据使用']:.1f}", f"{q['证据使用_5pt']:.2f}",
                    f"{q['审核意见可执行性']:.1f}", f"{q['审核意见可执行性_5pt']:.2f}",
                    f"{q['法规依据使用']:.1f}", f"{q['法规依据使用_5pt']:.2f}",
                    f"{q['技能流程使用']:.1f}" if q['技能流程使用'] == q['技能流程使用'] else "N/A",
                    f"{q['技能流程使用_5pt']:.2f}" if q['技能流程使用_5pt'] == q['技能流程使用_5pt'] else "N/A",
                    f"{avg_4:.2f}" if avg_4 else "",
                ])
    print(f"\n每题得分已保存: {detail_path}")
    
    # 2. 组级汇总
    summary_path = OUTPUT_DIR / "abcd_group_summary.csv"
    with summary_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        header = ["group", "对应Zhou模型",
                  "Correctness_5pt", "Completeness_5pt", "Clarity_5pt", "Compliance_5pt", "Skill_5pt",
                  "可比4维度均值_5pt", "Zhou_Average",
                  "Correctness_差值", "Completeness_差值", "Clarity_差值", "Compliance_差值", "均值差值"]
        writer.writerow(header)
        
        for group in ["A", "B", "C", "D"]:
            zhou_model = GROUP_TO_ZHOU[group]
            zhou_data = ZHOU_EXPERT[zhou_model]
            
            our = group_avg_5pt[group]
            comp_dims = ["判断正确性", "证据使用", "审核意见可执行性", "法规依据使用"]
            comp_scores = [our[d] for d in comp_dims if our[d] == our[d]]
            our_avg = statistics.mean(comp_scores) if comp_scores else float("nan")
            
            zhou_avg = zhou_data["Average"]
            
            diffs = {
                "Correctness": our["判断正确性"] - zhou_data["Correctness"],
                "Completeness": our["证据使用"] - zhou_data["Completeness"],
                "Clarity": our["审核意见可执行性"] - zhou_data["Clarity"],
                "Compliance": our["法规依据使用"] - zhou_data["Compliance"],
            }
            
            writer.writerow([
                group, zhou_model,
                f"{our['判断正确性']:.2f}", f"{our['证据使用']:.2f}",
                f"{our['审核意见可执行性']:.2f}", f"{our['法规依据使用']:.2f}",
                f"{our['技能流程使用']:.2f}" if our['技能流程使用'] == our['技能流程使用'] else "N/A",
                f"{our_avg:.2f}", f"{zhou_avg:.2f}",
                f"{diffs['Correctness']:+.2f}", f"{diffs['Completeness']:+.2f}",
                f"{diffs['Clarity']:+.2f}", f"{diffs['Compliance']:+.2f}",
                f"{our_avg - zhou_avg:+.2f}",
            ])
    print(f"组级汇总已保存: {summary_path}")
    
    # 3. Zhou论文自动指标参考（Table 3）
    zhou_auto_path = OUTPUT_DIR / "zhou_table3_auto_metrics.csv"
    with zhou_auto_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Type", "GPT-4o", "Qwen3-8B", "RAG", "FT", "RAG+FT"])
        auto_data = [
            ("ROUGE-1", "N-grams", 0.1818, 0.1920, 0.2198, 0.2857, 0.3353),
            ("ROUGE-2", "N-grams", 0.0823, 0.1172, 0.1229, 0.1738, 0.2175),
            ("ROUGE-L", "N-grams", 0.1698, 0.1844, 0.2105, 0.2871, 0.2997),
            ("BLEU", "N-grams", 0.0017, 0.0027, 0.0026, 0.0031, 0.0034),
            ("Precision", "Token", 0.0259, 0.0446, 0.0387, 0.0542, 0.0690),
            ("Recall", "Token", 0.1313, 0.1436, 0.1563, 0.2218, 0.2436),
            ("F1", "Token", 0.0383, 0.0655, 0.0622, 0.0725, 0.1139),
            ("Cosine", "Semantic", 0.8648, 0.8628, 0.9117, 0.8913, 0.9196),
            ("BERT-P", "Semantic", 0.6351, 0.6804, 0.7438, 0.7128, 0.7915),
            ("BERT-R", "Semantic", 0.7294, 0.7366, 0.7628, 0.7486, 0.7930),
            ("BERT-F1", "Semantic", 0.6780, 0.7060, 0.7526, 0.7292, 0.7911),
        ]
        for row in auto_data:
            writer.writerow(row)
    print(f"Zhou自动指标已保存: {zhou_auto_path}")
    
    # 4. 我们的结构化代理指标
    proxy_path = OUTPUT_DIR / "abcd_structured_proxy_metrics.csv"
    with proxy_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["group", "question_id", 
                         "judgement", "answer_mode", "report_status", "external_status",
                         "n_evidence", "n_checks", "n_calculations", "n_issues",
                         "n_ext_refs", "n_missing_refs",
                         "skill_id_present", "manual_review_needed",
                         "used_unprovided_knowledge", "report_evidence_backcheck"])
        
        for group in ["A", "B", "C", "D"]:
            for r in all_rows[group]:
                oj = r["_json"]
                ri = oj.get("report_internal_result", {})
                ev = oj.get("external_validation_result", {})
                fa = oj.get("final_answer", {})
                sf = oj.get("safety_flags", {})
                
                writer.writerow([
                    group, r.get("question_id", ""),
                    fa.get("judgement", ""), oj.get("answer_mode", ""),
                    ri.get("status", ""), ev.get("status", ""),
                    len(ri.get("evidence", []) or []),
                    len(ri.get("checks", []) or []),
                    len(ri.get("calculations", []) or []),
                    len(ri.get("issues", []) or []),
                    len(ev.get("references_used", []) or []),
                    len(ev.get("missing_references", []) or []),
                    bool(oj.get("skill_id", "")),
                    sf.get("manual_review_needed", ""),
                    sf.get("used_unprovided_external_knowledge", ""),
                    r.get("report_evidence_backcheck", ""),
                ])
    print(f"结构化代理指标已保存: {proxy_path}")
    
    # ─── 打印最终对比汇总 ───
    print("\n" + "=" * 80)
    print("最终对比汇总（5分制Likert，与Zhou论文Table 4对齐）")
    print("=" * 80)
    print(f"\n{'组别':<8} {'配置':<25} {'Zhou对应':<12} {'Correct':>8} {'Complete':>8} {'Comply':>8} {'Clarity':>8} {'Avg':>8} {'Zhou Avg':>9} {'差值':>7}")
    print("-" * 105)
    
    configs = {
        "A": "LLM only",
        "B": "LLM + RAG",
        "C": "LLM + Skill",
        "D": "LLM + RAG + Skill",
    }
    
    for group in ["A", "B", "C", "D"]:
        zhou_model = GROUP_TO_ZHOU[group]
        zhou_data = ZHOU_EXPERT[zhou_model]
        our = group_avg_5pt[group]
        
        comp_dims = ["判断正确性", "证据使用", "审核意见可执行性", "法规依据使用"]
        comp_scores = [our[d] for d in comp_dims if our[d] == our[d]]
        our_avg = statistics.mean(comp_scores) if comp_scores else 0
        zhou_avg = zhou_data["Average"]
        
        print(f"{group}组{'':>5} {configs[group]:<25} {zhou_model:<12} "
              f"{our['判断正确性']:>8.2f} {our['证据使用']:>8.2f} "
              f"{our['法规依据使用']:>8.2f} {our['审核意见可执行性']:>8.2f} "
              f"{our_avg:>8.2f} {zhou_avg:>9.2f} {our_avg - zhou_avg:>+7.2f}")
    
    print(f"\n注：")
    print(f"  Correct = 判断正确性, Complete = 证据使用, Comply = 法规依据使用, Clarity = 审核意见可执行性")
    print(f"  5分制Likert转换公式: 1 + (原始分/2) × 4")
    print(f"  差值 = 我们得分 - Zhou论文对应模型得分")


if __name__ == "__main__":
    main()
