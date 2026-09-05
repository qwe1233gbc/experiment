"""计算各组的关键率指标：幻觉率、弃权率、完整验证率、人工复核率、证据回查率。"""
import csv
import json
import statistics
from pathlib import Path

REPO = Path(r"E:\华南理工项目\环评文件汇总\01_GitHub项目与研究文档\eia-openclaw-sync-chen2026\10_消融实验设计")
CSV_PATHS = {
    "A": (REPO / r"06_Qwen3.8Max_A组_20260806\run_20260806_222338\run_matrix_a.csv", None),
    "B": (REPO / r"07_Qwen3.8Max_B组_20260807\run_20260807_215254\run_matrix_b.csv", None),
    "C": (REPO / r"05_Qwen3.8Max_CD重跑_20260806\run_20260806_164352\run_matrix_cd.csv", "C"),
    "D": (REPO / r"05_Qwen3.8Max_CD重跑_20260806\run_20260806_164352\run_matrix_cd.csv", "D"),
}
OUTPUT_DIR = Path(r"C:\Users\ylx\AppData\Roaming\TRAE SOLO CN\ModularData\ai-agent\work-mode-projects\6a789bcfc2e5f7d2fcd33cd3\实验文件整理_按论文逻辑")


def load_rows(csv_path, group_filter=None):
    rows = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if group_filter and r.get("group", "") != group_filter:
                continue
            try:
                r["_json"] = json.loads(r.get("output_json", "") or "{}")
            except:
                r["_json"] = {}
            rows.append(r)
    return rows


def pct(n, total):
    return f"{n}/{total} ({n/total*100:.1f}%)" if total else "0/0"


def main():
    print("=" * 90)
    print("各组关键率指标（Zhou论文未覆盖的实验特有指标）")
    print("=" * 90)
    
    print(f"\n{'指标':<25} {'A组(LLM)':<18} {'B组(+RAG)':<18} {'C组(+Skill)':<18} {'D组(+RAG+Skill)':<18}")
    print("-" * 95)
    
    results = {}
    for group in ["A", "B", "C", "D"]:
        csv_path, gf = CSV_PATHS[group]
        rows = load_rows(csv_path, gf)
        n = len(rows)
        
        # 幻觉率：used_unprovided_external_knowledge=True
        hallucination = sum(1 for r in rows 
                           if str(r["_json"].get("safety_flags", {}).get("used_unprovided_external_knowledge", "")).lower() == "true")
        
        # 弃权率：whole_task_abstention=True
        abstention = sum(1 for r in rows 
                        if str(r["_json"].get("safety_flags", {}).get("whole_task_abstention", "")).lower() == "true")
        
        # 完整验证率：answer_mode=full_validation
        full_validation = sum(1 for r in rows 
                            if r["_json"].get("answer_mode", "") == "full_validation")
        
        # 人工复核率：manual_review_needed=True
        manual_review = sum(1 for r in rows 
                          if str(r["_json"].get("safety_flags", {}).get("manual_review_needed", "")).lower() == "true")
        
        # 证据回查率：report_evidence_backcheck=True
        evidence_backcheck = sum(1 for r in rows 
                                if str(r.get("report_evidence_backcheck", "")).lower() == "true")
        
        # RAG证据回查率（仅B/D组）
        rag_backcheck = sum(1 for r in rows 
                           if str(r.get("rag_evidence_backcheck", "")).lower() == "true") if group in ("B", "D") else None
        
        # 判定分布
        judgement_dist = {}
        for r in rows:
            j = r["_json"].get("final_answer", {}).get("judgement", "")
            judgement_dist[j] = judgement_dist.get(j, 0) + 1
        
        # 外部验证状态分布
        ext_dist = {}
        for r in rows:
            s = r["_json"].get("external_validation_result", {}).get("status", "")
            ext_dist[s] = ext_dist.get(s, 0) + 1
        
        # answer_mode分布
        mode_dist = {}
        for r in rows:
            m = r["_json"].get("answer_mode", "")
            mode_dist[m] = mode_dist.get(m, 0) + 1
        
        results[group] = {
            "n": n,
            "hallucination": hallucination,
            "abstention": abstention,
            "full_validation": full_validation,
            "manual_review": manual_review,
            "evidence_backcheck": evidence_backcheck,
            "rag_backcheck": rag_backcheck,
            "judgement_dist": judgement_dist,
            "ext_dist": ext_dist,
            "mode_dist": mode_dist,
        }
    
    # 打印率指标
    metrics = [
        ("幻觉率", "hallucination"),
        ("整体弃权率", "abstention"),
        ("完整验证率", "full_validation"),
        ("人工复核率", "manual_review"),
        ("报告证据回查率", "evidence_backcheck"),
    ]
    
    for name, key in metrics:
        vals = []
        for group in ["A", "B", "C", "D"]:
            r = results[group]
            vals.append(pct(r[key], r["n"]))
        print(f"{name:<25} {vals[0]:<18} {vals[1]:<18} {vals[2]:<18} {vals[3]:<18}")
    
    # RAG证据回查率（仅B/D）
    vals = []
    for group in ["A", "B", "C", "D"]:
        r = results[group]
        if r["rag_backcheck"] is not None:
            vals.append(pct(r["rag_backcheck"], r["n"]))
        else:
            vals.append("N/A")
    print(f"{'RAG证据回查率':<25} {vals[0]:<18} {vals[1]:<18} {vals[2]:<18} {vals[3]:<18}")
    
    # 判定分布
    print(f"\n{'='*90}")
    print("判定分布（judgement）")
    print(f"{'='*90}")
    all_judgements = set()
    for group in ["A", "B", "C", "D"]:
        all_judgements.update(results[group]["judgement_dist"].keys())
    
    print(f"\n{'判定':<15} {'A组':<15} {'B组':<15} {'C组':<15} {'D组':<15}")
    print("-" * 75)
    for j in sorted(all_judgements):
        vals = []
        for group in ["A", "B", "C", "D"]:
            cnt = results[group]["judgement_dist"].get(j, 0)
            vals.append(f"{cnt}/{results[group]['n']}")
        print(f"{j:<15} {vals[0]:<15} {vals[1]:<15} {vals[2]:<15} {vals[3]:<15}")
    
    # 外部验证状态分布
    print(f"\n{'='*90}")
    print("外部验证状态分布（external_validation_result.status）")
    print(f"{'='*90}")
    all_ext = set()
    for group in ["A", "B", "C", "D"]:
        all_ext.update(results[group]["ext_dist"].keys())
    
    print(f"\n{'状态':<25} {'A组':<15} {'B组':<15} {'C组':<15} {'D组':<15}")
    print("-" * 85)
    for s in sorted(all_ext):
        vals = []
        for group in ["A", "B", "C", "D"]:
            cnt = results[group]["ext_dist"].get(s, 0)
            vals.append(f"{cnt}/{results[group]['n']}")
        print(f"{s:<25} {vals[0]:<15} {vals[1]:<15} {vals[2]:<15} {vals[3]:<15}")
    
    # answer_mode分布
    print(f"\n{'='*90}")
    print("应答模式分布（answer_mode）")
    print(f"{'='*90}")
    all_modes = set()
    for group in ["A", "B", "C", "D"]:
        all_modes.update(results[group]["mode_dist"].keys())
    
    print(f"\n{'模式':<25} {'A组':<15} {'B组':<15} {'C组':<15} {'D组':<15}")
    print("-" * 85)
    for m in sorted(all_modes):
        vals = []
        for group in ["A", "B", "C", "D"]:
            cnt = results[group]["mode_dist"].get(m, 0)
            vals.append(f"{cnt}/{results[group]['n']}")
        print(f"{m:<25} {vals[0]:<15} {vals[1]:<15} {vals[2]:<15} {vals[3]:<15}")
    
    # 保存率指标CSV
    rates_path = OUTPUT_DIR / "abcd_rate_metrics.csv"
    with rates_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["group", "config", "n", "hallucination_rate", "abstention_rate", 
                     "full_validation_rate", "manual_review_rate", "evidence_backcheck_rate",
                     "rag_backcheck_rate"])
        configs = {"A": "LLM only", "B": "LLM+RAG", "C": "LLM+Skill", "D": "LLM+RAG+Skill"}
        for group in ["A", "B", "C", "D"]:
            r = results[group]
            rb = r["rag_backcheck"]
            w.writerow([
                group, configs[group], r["n"],
                f"{r['hallucination']/r['n']*100:.1f}%",
                f"{r['abstention']/r['n']*100:.1f}%",
                f"{r['full_validation']/r['n']*100:.1f}%",
                f"{r['manual_review']/r['n']*100:.1f}%",
                f"{r['evidence_backcheck']/r['n']*100:.1f}%",
                f"{rb/r['n']*100:.1f}%" if rb is not None else "N/A",
            ])
    print(f"\n率指标已保存: {rates_path}")


if __name__ == "__main__":
    main()
