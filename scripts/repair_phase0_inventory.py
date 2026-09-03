#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pilot17 修复 - 阶段0：备份、盘点和版本隔离
建立修复目录，生成所有关键对象的文件清单和SHA-256
"""
import os
import json
import hashlib
import datetime
import csv
from pathlib import Path

EXPERIMENT_ROOT = Path(r"E:\实验文件整理_按论文逻辑\实验")
REPAIR_DIR = EXPERIMENT_ROOT / "07_results_v2" / "pilot17_repair_20260903"
REPAIR_DIR.mkdir(parents=True, exist_ok=True)

REPAIR_TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
REPAIR_VERSION = "v3.4_repair_20260903"

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def get_file_info(filepath, category, object_type, object_id=""):
    stat = filepath.stat()
    return {
        "category": category,
        "object_type": object_type,
        "object_id": object_id,
        "file_path": str(filepath),
        "file_name": filepath.name,
        "size_bytes": stat.st_size,
        "modified_time": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "sha256": sha256_file(filepath),
    }

def main():
    print("=" * 70)
    print(f"Pilot17 修复 - 阶段0：盘点与版本隔离 [{REPAIR_VERSION}]")
    print("=" * 70)
    print(f"修复目录: {REPAIR_DIR}")
    print(f"时间戳: {REPAIR_TIMESTAMP}")
    print()
    
    all_files = []
    
    # ===== 1. 17题金标表 =====
    print("[1] 盘点17题金标表...")
    gold_files = [
        ("pilot16_questions_v2.xlsx", "gold_master", "questions_v2"),
        ("pilot17_gold_freeze_template.xlsx", "gold_template", "gold_freeze_template"),
        ("Pilot17_金标原文核验_AI预核查版_20260902.xlsx", "gold_ai_checked", "gold_ai_precheck_20260902"),
        ("pilot17_gold_ai_prechecked.xlsx", "gold_ai_checked", "gold_ai_prechecked"),
        ("pilot16_gold_review_v2.xlsx", "gold_historical", "gold_review_v2"),
    ]
    eval_dir = EXPERIMENT_ROOT / "02_evaluation_set"
    for fname, otype, oid in gold_files:
        fpath = eval_dir / fname
        if fpath.exists():
            info = get_file_info(fpath, "gold_label", otype, oid)
            all_files.append(info)
            print(f"  ✅ {fname} ({info['size_bytes']:,} bytes)")
    
    # ===== 2. 11份原始Word =====
    print("\n[2] 盘点11份原始Word...")
    word_dir = EXPERIMENT_ROOT / "09_input_reports" / "原始Word版"
    for fpath in sorted(word_dir.glob("*.docx")):
        # 提取项目ID
        fname = fpath.name
        # 从文件名提取PL编号
        import re
        m = re.match(r'(PL\d+)', fname)
        pid = m.group(1) if m else "unknown"
        info = get_file_info(fpath, "original_word", "word_report", pid)
        all_files.append(info)
        print(f"  ✅ {fname[:50]} ({info['size_bytes']:,} bytes)")
    
    # ===== 3. 11份解析JSON =====
    print("\n[3] 盘点11份解析JSON...")
    json_dir = EXPERIMENT_ROOT / "09_input_reports"
    for fpath in sorted(json_dir.glob("*.json")):
        fname = fpath.name
        import re
        m = re.match(r'(PL\d+)', fname)
        pid = m.group(1) if m else "unknown"
        info = get_file_info(fpath, "parsed_json", "json_report", pid)
        all_files.append(info)
        print(f"  ✅ {fname[:50]} ({info['size_bytes']:,} bytes)")
    
    # ===== 4. 17题报告上下文 =====
    print("\n[4] 盘点报告上下文...")
    ctx_file = EXPERIMENT_ROOT / "03_knowledge_base" / "report_context_v3.jsonl"
    if ctx_file.exists():
        info = get_file_info(ctx_file, "report_context", "context_snapshot", "v3")
        all_files.append(info)
        print(f"  ✅ report_context_v3.jsonl ({info['size_bytes']:,} bytes)")
    
    # 从v3.3_abc_experiment读取Prompt中的上下文
    abc_prompt_dir = EXPERIMENT_ROOT / "07_results_v2" / "v3.3_abc_experiment" / "prompts"
    if abc_prompt_dir.exists():
        prompt_count = len(list(abc_prompt_dir.glob("*.txt")))
        print(f"  ℹ️  v3.3_abc prompts: {prompt_count}个文件")
    
    # ===== 5. Web与RAG快照 =====
    print("\n[5] 盘点Web与RAG快照...")
    kb_dir = EXPERIMENT_ROOT / "03_knowledge_base"
    snap_files = [
        ("pilot16_web_snapshot_v3_3.jsonl", "web_snapshot", "web_v3_3"),
        ("pilot16_rag_snapshot_v3_3.jsonl", "rag_snapshot", "rag_v3_3"),
        ("pilot16_rag_manifest.json", "rag_manifest", "rag_manifest_v3"),
        ("rag_manifest_v3.json", "rag_manifest", "rag_manifest_v3_alt"),
    ]
    for fname, otype, oid in snap_files:
        fpath = kb_dir / fname
        if fpath.exists():
            info = get_file_info(fpath, "knowledge_base", otype, oid)
            all_files.append(info)
            print(f"  ✅ {fname} ({info['size_bytes']:,} bytes)")
    
    # ===== 6. 153份候选Prompt =====
    print("\n[6] 盘点153份候选Prompt...")
    prompt_counts = {}
    for result_dir in ["v3.3_abc_experiment", "v3.3_3x3_experiment"]:
        pdir = EXPERIMENT_ROOT / "07_results_v2" / result_dir / "prompts"
        if pdir.exists():
            count = len(list(pdir.glob("*.txt")))
            prompt_counts[result_dir] = count
            print(f"  {result_dir}: {count}个Prompt文件")
    
    # 记录manifest
    manifest_file = EXPERIMENT_ROOT / "07_results_v2" / "pilot17_targeted_retest" / "prompt_manifest.jsonl"
    if manifest_file.exists():
        info = get_file_info(manifest_file, "prompt_manifest", "manifest_retest27", "targeted_retest_27")
        all_files.append(info)
        print(f"  ✅ 定向重测prompt_manifest ({info['size_bytes']:,} bytes)")
    
    # ===== 7. 27次定向测试原始响应和评分 =====
    print("\n[7] 盘点27次定向测试结果...")
    retest_dir = EXPERIMENT_ROOT / "07_results_v2" / "pilot17_targeted_retest"
    retest_files = [
        ("raw_outputs_27.jsonl", "raw_output", "raw_retest_27"),
        ("raw_outputs_27_backup.jsonl", "raw_output_backup", "raw_retest_27_backup"),
        ("scoring_results_27.xlsx", "scoring_result", "score_retest_27"),
        ("auto_pre_scoring.jsonl", "auto_scoring", "autoscore_retest_27"),
        ("run_config_frozen.json", "run_config", "config_retest_27"),
    ]
    for fname, otype, oid in retest_files:
        fpath = retest_dir / fname
        if fpath.exists():
            info = get_file_info(fpath, "experiment_result", otype, oid)
            all_files.append(info)
            print(f"  ✅ {fname} ({info['size_bytes']:,} bytes)")
    
    # ===== 8. 核心脚本和设计文件 =====
    print("\n[8] 盘点核心脚本和设计文件...")
    core_files = [
        ("EXPERIMENT_CANONICAL.md", "design", "canonical_v3"),
        ("05_scripts/frozen_config.py", "config", "frozen_config"),
        ("05_scripts/build_report_context_v3_3.py", "script", "context_builder_v33"),
        ("05_scripts/run_pilot16_abc.py", "script", "runner_abc"),
        ("05_scripts/auto_pre_score_abc.py", "script", "scorer_abc"),
        ("04_prompts/system_prompt_FROZEN_v2.txt", "prompt", "system_prompt_v2"),
    ]
    for fpath_rel, otype, oid in core_files:
        fpath = EXPERIMENT_ROOT / fpath_rel
        if fpath.exists():
            info = get_file_info(fpath, "core_code", otype, oid)
            all_files.append(info)
            print(f"  ✅ {fpath_rel} ({info['size_bytes']:,} bytes)")
    
    # ===== 保存清单 =====
    print(f"\n{'='*70}")
    print(f"总计: {len(all_files)} 个文件")
    
    # 按类别统计
    from collections import Counter
    cat_counts = Counter(f["category"] for f in all_files)
    for cat, count in sorted(cat_counts.items()):
        print(f"  {cat}: {count}个")
    
    # 保存CSV
    csv_path = REPAIR_DIR / "00_repair_input_inventory_and_hashes.csv"
    fieldnames = [
        "category", "object_type", "object_id", "file_path", "file_name",
        "size_bytes", "modified_time", "sha256"
    ]
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_files)
    
    print(f"\n输入清单已保存: {csv_path}")
    
    # 保存修复元数据
    meta = {
        "repair_version": REPAIR_VERSION,
        "repair_timestamp": REPAIR_TIMESTAMP,
        "repair_dir": str(REPAIR_DIR),
        "experiment_root": str(EXPERIMENT_ROOT),
        "audit_scope_before": "PARTIAL_3_OF_17",
        "benchmark_decision_before": "BENCHMARK_NOT_READY",
        "total_files_inventoried": len(all_files),
        "input_inventory_hash": sha256_file(csv_path),
    }
    meta_path = REPAIR_DIR / "repair_metadata.json"
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"修复元数据已保存: {meta_path}")
    
    print(f"\n阶段0完成")
    return all_files, meta

if __name__ == "__main__":
    main()
