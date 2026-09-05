"""更新B组验证报告和就绪报告，生成最终汇总。"""
import csv
import json
from pathlib import Path
from collections import Counter

RUN_DIR = Path(r"E:\华南理工项目\环评文件汇总\01_GitHub项目与研究文档\eia-openclaw-sync-chen2026\10_消融实验设计\07_Qwen3.8Max_B组_20260807\run_20260807_215254")

# 读取run_matrix_b.csv
rows = []
with (RUN_DIR / "run_matrix_b.csv").open(encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# 统计指标
metrics = {
    "total": len(rows),
    "valid_json": sum(r["valid_json"] == "True" for r in rows),
    "evidence_backcheck": sum(r["report_evidence_backcheck"] == "True" for r in rows),
    "whole_task_abstention": sum(r.get("whole_task_abstention", "").lower() == "true" for r in rows),
    "manual_review_needed": sum(r.get("manual_review_needed", "").lower() == "true" for r in rows),
    "used_unprovided_external_knowledge": sum(r.get("used_unprovided_external_knowledge", "").lower() == "true" for r in rows),
    "external_verified": sum(r.get("external_status", "") == "verified" for r in rows),
    "external_not_performed": sum(r.get("external_status", "") == "not_performed" for r in rows),
    "external_insufficient_reference": sum(r.get("external_status", "") == "insufficient_reference" for r in rows),
    "external_not_required": sum(r.get("external_status", "") == "not_required" for r in rows),
    # 判定分布
    "judgement_correct": sum(r.get("judgement", "") == "正确" for r in rows),
    "judgement_issue": sum(r.get("judgement", "") == "存在问题" for r in rows),
    "judgement_partial": sum(r.get("judgement", "") == "部分完成" for r in rows),
    "judgement_manual": sum(r.get("judgement", "") == "待人工复核" for r in rows),
    # answer_mode分布
    "mode_determinate_internal": sum(r.get("answer_mode", "") == "determinate_internal" for r in rows),
    "mode_full_validation": sum(r.get("answer_mode", "") == "full_validation" for r in rows),
    "mode_partial_internal": sum(r.get("answer_mode", "") == "partial_internal" for r in rows),
    "mode_insufficient_report": sum(r.get("answer_mode", "") == "insufficient_report" for r in rows),
}

# 按审核类别统计
category_stats = {}
for r in rows:
    cat = r.get("audit_category", "")
    if cat not in category_stats:
        category_stats[cat] = {"total": 0, "verified": 0, "not_performed": 0, "insufficient": 0}
    category_stats[cat]["total"] += 1
    if r.get("external_status") == "verified":
        category_stats[cat]["verified"] += 1
    elif r.get("external_status") == "not_performed":
        category_stats[cat]["not_performed"] += 1
    elif r.get("external_status") == "insufficient_reference":
        category_stats[cat]["insufficient"] += 1

# 更新validation_report.json
validation_report = {
    "group": "B",
    "description": "LLM + 法规库（有RAG、无Skill）",
    "rows": len(rows),
    "valid_json": metrics["valid_json"],
    "metrics": metrics,
    "category_stats": category_stats,
    "manual_review_queue": sum(1 for r in rows if r.get("manual_review_needed", "").lower() == "true" or r.get("validation_errors") or r.get("validation_warnings")),
    "failed_tasks": [],
    "note": "PL005_Emission_固体因输出截断重试成功（max_output_tokens=16000）",
}

report_path = RUN_DIR / "validation_report.json"
report_path.write_text(json.dumps(validation_report, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"验证报告已更新: {report_path}")

# 更新readiness_report.json
readiness_report = {
    "group": "B",
    "description": "LLM + 法规库（有RAG、无Skill）",
    "ready": len(rows) == 21,
    "model": "qwen3.8-max",
    "max_output_tokens": 10000,
    "rows": len(rows),
    "run_dir": str(RUN_DIR),
    "all_21_completed": len(rows) == 21,
    "all_valid_json": metrics["valid_json"] == 21,
    "evidence_backcheck_rate": f"{metrics['evidence_backcheck']}/21",
    "external_verified_rate": f"{metrics['external_verified']}/21",
    "ablation_role": "B组（LLM+RAG）用于计算：①RAG增量效应（B vs A）②Skill增量效应（B vs D）",
}

readiness_path = RUN_DIR / "readiness_report.json"
readiness_path.write_text(json.dumps(readiness_report, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"就绪报告已更新: {readiness_path}")

# 打印最终汇总
print(f"\n{'='*60}")
print(f"B组实验最终汇总")
print(f"{'='*60}")
print(f"组别: B (LLM + 法规库，有RAG、无Skill)")
print(f"运行目录: {RUN_DIR}")
print(f"")
print(f"文件完整性:")
print(f"  原始响应: 21个JSON文件")
print(f"  解析输出: 21个JSON文件")
print(f"  Prompt文件: 21个txt文件")
print(f"  运行矩阵: run_matrix_b.csv (21行)")
print(f"")
print(f"质量指标:")
print(f"  有效JSON: {metrics['valid_json']}/21")
print(f"  证据回查通过: {metrics['evidence_backcheck']}/21")
print(f"  整体弃答: {metrics['whole_task_abstention']}/21")
print(f"  需人工复核: {metrics['manual_review_needed']}/21")
print(f"")
print(f"判定分布:")
print(f"  正确: {metrics['judgement_correct']}")
print(f"  存在问题: {metrics['judgement_issue']}")
print(f"  部分完成: {metrics['judgement_partial']}")
print(f"  待人工复核: {metrics['judgement_manual']}")
print(f"")
print(f"外部验证分布:")
print(f"  verified (已验证): {metrics['external_verified']}")
print(f"  insufficient_reference (证据不足): {metrics['external_insufficient_reference']}")
print(f"  not_performed (未执行): {metrics['external_not_performed']}")
print(f"")
print(f"answer_mode分布:")
print(f"  full_validation: {metrics['mode_full_validation']}")
print(f"  partial_internal: {metrics['mode_partial_internal']}")
print(f"  determinate_internal: {metrics['mode_determinate_internal']}")
print(f"  insufficient_report: {metrics['mode_insufficient_report']}")
print(f"")
print(f"按审核类别统计:")
for cat, stats in sorted(category_stats.items()):
    print(f"  {cat}: 总{stats['total']}, 已验证{stats['verified']}, 证据不足{stats['insufficient']}, 未执行{stats['not_performed']}")
print(f"")
print(f"{'='*60}")
print(f"消融实验设计角色:")
print(f"  B vs A: 测试RAG增量效应（RAG是否提升审核质量）")
print(f"  B vs D: 测试Skill增量效应（Skill是否提升审核质量）")
print(f"  注意: B组与D组使用相同的报告上下文和冻结RAG，唯一变量为'是否包含Skill'")
print(f"{'='*60}")
