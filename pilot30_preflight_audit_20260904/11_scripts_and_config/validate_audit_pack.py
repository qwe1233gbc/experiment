#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pilot30 预飞审计包验证脚本
只做确定性检查，不做质量判断。
"""
import json
import csv
import hashlib
from pathlib import Path
from collections import Counter

AUDIT = Path(r'E:\实验文件整理_按论文逻辑\pilot30_preflight_audit_20260904')

def check_json_parseable(path):
    try:
        json.loads(path.read_text(encoding='utf-8'))
        return True, ""
    except Exception as e:
        return False, str(e)

def check_jsonl_parseable(path):
    try:
        lines = path.read_text(encoding='utf-8').strip().splitlines()
        for i, l in enumerate(lines):
            if l.strip():
                json.loads(l)
        return True, ""
    except Exception as e:
        return False, f"line {i+1}: {e}"

def check_csv_fields(path, required_fields):
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames or []
            rows = list(reader)
        missing = [f for f in required_fields if f not in fields]
        if missing:
            return False, f"缺少字段: {missing}", rows, fields
        return True, "", rows, fields
    except Exception as e:
        return False, str(e), [], []

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def main():
    results = {
        "checks": [],
        "passed": 0,
        "failed": 0,
        "errors": [],
    }
    
    def add_check(name, passed, detail=""):
        results["checks"].append({"name": name, "passed": passed, "detail": detail})
        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["errors"].append(f"{name}: {detail}")
    
    # 1. 25个唯一 question_id
    q_csv = AUDIT / "01_questions" / "current_25_questions.csv"
    ok, err, rows, fields = check_csv_fields(q_csv, ["question_id", "project_id", "current_gold_verdict", "experiment_status"])
    if ok:
        qids = [r["question_id"] for r in rows]
        unique = len(set(qids))
        add_check(f"25个唯一question_id", unique == 25, f"实际{unique}个")
        
        # 16+7+2 状态数量
        exp_done = sum(1 for r in rows if r["experiment_status"].startswith("EXPERIMENT"))
        heldout = sum(1 for r in rows if r["experiment_status"].startswith("HELDOUT"))
        deferred = sum(1 for r in rows if r["experiment_status"].startswith("EVIDENCE"))
        add_check(f"16+7+2状态数量正确", exp_done==16 and heldout==7 and deferred==2,
                   f"已实验{exp_done}, heldout{heldout}, 暂缓{deferred}")
    else:
        add_check("question CSV解析", False, err)
    
    # 2. 文件SHA-256可复算
    test_files = [
        AUDIT / "05_rag_knowledge_base" / "pilot17_rag_snapshot_v3_4.jsonl",
        AUDIT / "08_model_outputs" / "pilot17_v3_5_full_results_144.jsonl",
    ]
    for tf in test_files:
        if tf.exists():
            h = sha256_file(tf)
            add_check(f"SHA256可复算: {tf.name}", True, h[:16] + "...")
        else:
            add_check(f"SHA256: {tf.name}", False, "文件不存在")
    
    # 3. 项目—报告映射无错配
    rep_csv = AUDIT / "02_original_reports" / "report_registry.csv"
    ok, err, rep_rows, rep_fields = check_csv_fields(rep_csv, ["project_id", "file_name", "sha256"])
    if ok:
        projs = set(r["project_id"] for r in rep_rows)
        q_projs = set(r["project_id"] for r in rows)
        mismatch = q_projs - projs
        add_check(f"项目-报告映射完整", len(mismatch) == 0,
                   f"题目项目{len(q_projs)}个, 登记项目{len(projs)}个, 缺{len(mismatch)}个: {mismatch}")
    else:
        add_check("report_registry.csv", False, err)
    
    # 4. 运行记录理论144条
    result_f = AUDIT / "08_model_outputs" / "pilot17_v3_5_full_results_144.jsonl"
    if result_f.exists():
        runs = [json.loads(l) for l in result_f.read_text(encoding='utf-8').strip().splitlines() if l.strip()]
        add_check(f"运行记录数", len(runs) == 144, f"实际{len(runs)}条")
        
        statuses = Counter(r.get("status", "UNKNOWN") for r in runs)
        excluded = statuses.get("EXCLUDED_HARD", 0)
        add_check(f"排除记录数≤2", excluded <= 2, f"实际{excluded}条")
        
        # 3模型×3条件
        models = set(r["model_id"] for r in runs)
        kcs = set(r["knowledge_condition"] for r in runs)
        add_check(f"3模型×3知识条件", len(models)==3 and len(kcs)==3,
                   f"模型{len(models)}个: {models}, 知识条件{len(kcs)}个: {kcs}")
    else:
        add_check("运行记录文件", False, "不存在")
    
    # 5. JSON/JSONL可解析
    json_files = [
        AUDIT / "05_rag_knowledge_base" / "kb_snapshot_manifest.json",
        AUDIT / "09_scoring_and_gold" / "scoring_status.json",
        AUDIT / "12_logs" / "missing_materials.json",
    ]
    for jf in json_files:
        ok, err = check_json_parseable(jf)
        add_check(f"JSON可解析: {jf.name}", ok, err)
    
    jsonl_files = [
        AUDIT / "05_rag_knowledge_base" / "pilot17_rag_snapshot_v3_4.jsonl",
        AUDIT / "08_model_outputs" / "pilot17_v3_5_full_results_144.jsonl",
    ]
    for jf in jsonl_files:
        ok, err = check_jsonl_parseable(jf)
        add_check(f"JSONL可解析: {jf.name}", ok, err)
    
    # 6. 每道需外部知识的题都有预期知识源
    kb_csv = AUDIT / "10_audit_tables" / "qa_kb_coverage.csv"
    ok, err, kb_rows, kb_fields = check_csv_fields(kb_csv, ["question_id", "kb_coverage_verdict"])
    if ok:
        kb_qids = set(r["question_id"] for r in kb_rows)
        q_qids = set(qids)
        add_check(f"KB覆盖表覆盖全部题目", kb_qids == q_qids,
                   f"表中{len(kb_qids)}题, 题目清单{len(q_qids)}题, 差异{kb_qids ^ q_qids}")
    else:
        add_check("qa_kb_coverage.csv", False, err)
    
    # 7. CSV字段齐全检查（关键表）
    key_csvs = [
        ("01_questions/current_25_questions.csv", ["question_id", "project_id", "current_gold_verdict"]),
        ("10_audit_tables/question_root_cause_matrix.csv", ["question_id", "candidate_root_cause"]),
        ("09_scoring_and_gold/gold_version_lineage.csv", ["question_id", "human_confirmed"]),
    ]
    for rel_path, req_fields in key_csvs:
        p = AUDIT / rel_path
        ok, err, csv_rows, fields = check_csv_fields(p, req_fields)
        add_check(f"CSV字段齐全: {rel_path}", ok, 
                   f"缺{[f for f in req_fields if f not in fields]} ({len(csv_rows)}行)" if not ok else f"{len(csv_rows)}行")
    
    # 8. README存在
    readme = AUDIT / "README_FOR_GPT.md"
    add_check("README_FOR_GPT.md存在", readme.exists(), 
               "size: " + str(readme.stat().st_size) if readme.exists() else "不存在")
    
    # 9. 所有MISSING/NOT_LOGGED均进入缺失清单
    add_check("缺失清单存在", (AUDIT / "12_logs" / "missing_materials.json").exists(), "已生成")
    
    # 汇总
    total = results["passed"] + results["failed"]
    status = "PASS" if results["failed"] == 0 else "FAIL"
    
    report = {
        "validation_status": status,
        "total_checks": total,
        "passed": results["passed"],
        "failed": results["failed"],
        "checks": results["checks"],
        "errors": results["errors"],
    }
    
    # 写JSON报告
    with open(AUDIT / "12_logs" / "validation_report.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 写MD报告
    md = f"# 审计包验证报告\n\n"
    md += f"- **验证状态**: {status}\n"
    md += f"- **总检查项**: {total}\n"
    md += f"- **通过**: {results['passed']}\n"
    md += f"- **失败**: {results['failed']}\n\n"
    
    if results["errors"]:
        md += "## 失败项\n\n"
        for e in results["errors"]:
            md += f"- ❌ {e}\n"
        md += "\n"
    
    md += "## 全部检查项\n\n"
    for c in results["checks"]:
        icon = "✅" if c["passed"] else "❌"
        md += f"- {icon} {c['name']}: {c['detail']}\n"
    
    md += "\n---\n\n"
    md += "**重要说明**：验证通过仅代表审计包结构完整、文件可解析、数量匹配。"
    md += "**不代表题目证据充分或实验可运行**。\n"
    md += "具体证据质量和根因判定需由 GPT 结合原文逐题审计。\n"
    
    with open(AUDIT / "12_logs" / "validation_report.md", 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"验证状态: {status}")
    print(f"通过: {results['passed']}/{total}")
    if results["errors"]:
        print(f"失败项 ({len(results['errors'])}):")
        for e in results["errors"]:
            print(f"  - {e}")
    print(f"\n报告: 12_logs/validation_report.md")
    return status

if __name__ == '__main__':
    main()
