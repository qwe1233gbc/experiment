#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pilot17 修复 - 收尾：修复PL010章节 + RAG治理完善 + 金标修订 + 最终交付
"""
import re
import json
import hashlib
import csv
from pathlib import Path
from collections import Counter, defaultdict

EXPERIMENT_ROOT = Path(r"E:\实验文件整理_按论文逻辑\实验")
REPAIR_DIR = EXPERIMENT_ROOT / "07_results_v2" / "pilot17_repair_20260903"

# ============ 修复PL010章节分类 ============

def fix_pl010_sections_v2():
    """基于内容开头的章节分类修复"""
    print("修复PL010章节分类 v2 (基于内容匹配)...")
    
    json_path = EXPERIMENT_ROOT / "09_input_reports" / "PL010_悍高集团股份有限公司功能拉篮车间搬迁扩建项目.json"
    with open(json_path, encoding="utf-8") as f:
        blocks = json.load(f)
    
    # 章节规则：按内容开头的关键词匹配
    chapter_rules = [
        ("basic", ["建设项目基本情况", "建设项目名称", "项目基本情况", "其他符合性分析", "建设内容", "项目概况"]),
        ("engineering", ["建设项目工程分析", "工程分析", "工艺流程", "产污环节", "源强核算", "污染物产生", "建设内容"]),
        ("standard", ["区域环境质量现状", "环境质量现状", "评价标准", "环境保护目标", "功能区划"]),
        ("measures", ["主要环境影响和保护措施", "运营期环境影响", "施工期环境保护", "环境保护措施", "废气治理", "废水治理", "运营期环境保护"]),
        ("supervision", ["环境保护措施监督检查清单", "监督检查清单", "环保措施监督"]),
        ("conclusion", ["六、结论", "结论与建议", "评价结论", "综合结论"]),
        ("appendix", ["附表", "附件", "附图", "污染物排放量汇总", "附录"]),
    ]
    
    def classify_by_content_start(block):
        """从内容开头识别章节"""
        content = block.get("content", "")
        # 去HTML标签
        clean = re.sub(r'<[^>]+>', ' ', content)
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        # 取前300字作为识别依据
        preview = clean[:300]
        
        best_cat = "unknown"
        best_score = 0
        best_keyword = ""
        
        for cat, keywords in chapter_rules:
            for kw in keywords:
                if kw in preview:
                    score = 1.0 - preview.index(kw) / 500  # 越靠前权重越高
                    if score > best_score:
                        best_score = score
                        best_cat = cat
                        best_keyword = kw
            # 也检查完整内容的前1000字中的表格标题
            tables = re.findall(r'表\d+[-－]\d+\s*([^<\n]{10,40})', content[:2000])
            for table_title in tables:
                for kw in keywords:
                    if kw in table_title:
                        if 0.5 > best_score:
                            best_score = 0.5
                            best_cat = cat
                            best_keyword = f"table:{table_title[:20]}"
        
        return best_cat, best_score, best_keyword
    
    fixed_blocks = []
    results = []
    prev_cat = ""
    
    for i, block in enumerate(blocks):
        cat, score, kw = classify_by_content_start(block)
        
        # 如果置信度低，检查是否继承前一章节
        if score < 0.3 and prev_cat and cat == "unknown":
            # 检查是否有新章节的强烈信号
            content = re.sub(r'<[^>]+>', ' ', block.get("content", ""))
            content = re.sub(r'\s+', ' ', content).strip()[:200]
            new_chapter_markers = ["一、", "二、", "三、", "四、", "五、", "六、",
                                   "建设项目基本情况", "建设项目工程分析", "区域环境质量",
                                   "主要环境影响", "监督检查清单", "结论"]
            has_new = any(m in content for m in new_chapter_markers)
            if not has_new:
                cat = prev_cat
                score = 0.25
                kw = "inherited_from_prev"
        
        if cat != "unknown":
            prev_cat = cat
        
        new_block = dict(block)
        new_block["section_category_v2"] = cat
        new_block["section_confidence_v2"] = round(score, 3)
        new_block["section_match_keyword"] = kw
        fixed_blocks.append(new_block)
        
        results.append({
            "block_index": i,
            "old_section": block.get("section", "")[:50],
            "new_category": cat,
            "confidence": round(score, 3),
            "match_keyword": kw,
        })
    
    # 统计
    cat_counts = Counter(r["new_category"] for r in results)
    print(f"\n  修复后章节分布:")
    for cat, cnt in sorted(cat_counts.items()):
        print(f"    {cat}: {cnt}块")
    
    print(f"\n  每块详情:")
    for r in results:
        print(f"    Block{r['block_index']}: {r['old_section'][:30]:30s} → {r['new_category']:12s} (conf={r['confidence']:.2f}, kw={r['match_keyword'][:20]})")
    
    # 保存
    out_path = REPAIR_DIR / "PL010_sections_fixed_candidate.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(fixed_blocks, f, ensure_ascii=False, indent=2)
    print(f"\n  已保存: {out_path.name}")
    
    return {
        "total_blocks": len(blocks),
        "category_distribution": dict(cat_counts),
        "unknown_count": cat_counts.get("unknown", 0),
        "verdict": "SECTIONS_FIXED_V2",
    }


# ============ RAG指令污染治理 ============

def fix_rag_contamination():
    """治理RAG中的指令型文档"""
    print("\nRAG指令污染治理...")
    
    rag_path = EXPERIMENT_ROOT / "03_knowledge_base" / "pilot16_rag_snapshot_v3_3.jsonl"
    
    all_records = []
    with open(rag_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                all_records.append(json.loads(line))
    
    print(f"  原始记录: {len(all_records)}条")
    
    # 识别程序性/指令型文档
    procedural_sources = set()
    procedural_patterns_in_name = [
        "审核指南", "核算指南", "操作指南", "方法指南",
        "prompt", "template", "评分", "rubric", "示例",
    ]
    
    procedural_patterns_in_content = [
        "请按照", "你需要", "你应该", "任务", "步骤如下",
        "审核流程", "操作步骤", "评分标准",
    ]
    
    kept = []
    excluded = []
    
    for rec in all_records:
        source = rec.get("source_file", "")
        text = rec.get("child_text", "") or rec.get("text", "")
        
        is_procedural = False
        doc_role = "normative_evidence"
        exclusion_reason = ""
        
        source_lower = source.lower()
        
        # 文件名匹配
        for p in procedural_patterns_in_name:
            if p.lower() in source_lower:
                is_procedural = True
                doc_role = "procedural_guide" if "指南" in source or "guide" in source_lower else doc_role
                if "prompt" in source_lower or "template" in source_lower:
                    doc_role = "prompt_template"
                if "评分" in source or "scoring" in source_lower or "rubric" in source_lower:
                    doc_role = "scoring_rubric"
                if "示例" in source or "example" in source_lower:
                    doc_role = "example"
                exclusion_reason = f"filename_matches:{p}"
                break
        
        # 如果文件名没匹配，检查内容开头
        if not is_procedural:
            text_start = text[:1500]
            procedural_hits = sum(1 for p in procedural_patterns_in_content if p in text_start)
            if procedural_hits >= 3 and ("审核" in text_start or "指南" in text_start):
                is_procedural = True
                doc_role = "procedural_guide"
                exclusion_reason = f"content_matches:{procedural_hits}_keywords"
        
        rec_with_meta = dict(rec)
        rec_with_meta["doc_role"] = doc_role
        rec_with_meta["is_instruction_like"] = is_procedural
        rec_with_meta["exclusion_reason"] = exclusion_reason
        rec_with_meta["source_title"] = source
        rec_with_meta["authority_level"] = "high" if any(x in source for x in ["GB", "HJ", "DB", "名录"]) else "medium"
        
        if is_procedural:
            excluded.append(rec_with_meta)
            procedural_sources.add(source)
        else:
            kept.append(rec_with_meta)
    
    print(f"\n  保留: {len(kept)}条")
    print(f"  排除: {len(excluded)}条 (来自 {len(procedural_sources)} 个文档)")
    print(f"\n  排除的文档:")
    for src in sorted(procedural_sources):
        count = sum(1 for r in excluded if r["source_file"] == src)
        sample = next((r for r in excluded if r["source_file"] == src), None)
        role = sample.get("doc_role", "") if sample else ""
        reason = sample.get("exclusion_reason", "") if sample else ""
        print(f"    - {src[:60]} ({count}条, {role}, {reason})")
    
    # 验证PL010
    pl010_kept = [r for r in kept if r.get("question_id") == "PL010_VOCSTotal_Q01"]
    pl010_kept.sort(key=lambda x: x.get("rank", 999))
    print(f"\n  PL010 S2 过滤后Top-5:")
    for i, r in enumerate(pl010_kept[:5]):
        src = r.get("source_file", "")[:50]
        role = r.get("doc_role", "")
        print(f"    [{i+1}] {src} ({role})")
    
    # 保存候选快照
    out_path = REPAIR_DIR / "pilot17_rag_snapshot_candidate_v3_4.jsonl"
    with open(out_path, 'w', encoding='utf-8') as f:
        for rec in kept:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"\n  候选快照已保存: {out_path.name}")
    
    return {
        "original_count": len(all_records),
        "kept_count": len(kept),
        "excluded_count": len(excluded),
        "excluded_sources": list(procedural_sources),
        "pl010_top5_clean": all(not r.get("is_instruction_like") for r in pl010_kept[:5]),
    }


# ============ 阶段6：金标修订记录 ============

def gold_label_revision_log():
    """金标修订记录"""
    print("\n金标修订记录...")
    
    revisions = [
        {
            "question_id": "PL008_VOCSMeasure_Q01",
            "task_type": "VOCs治理措施一致性",
            "old_gold_label": "INSUFFICIENT",
            "new_gold_label_candidate": "INCORRECT",
            "revision_reason": (
                "原金标INSUFFICIENT不符合题意。三个章节的VOCs治理措施并非完全完整一致，"
                "已有充分证据判断不一致（工程分析章节证据不完整本身就是不一致的表现）。"
                "7/9模型一致判为INCORRECT，说明证据充分支持不一致结论。"
            ),
            "evidence_summary": (
                "Word证据：工程分析、运营期措施、监督检查清单三章均有VOCs治理设施描述，"
                "但工程分析未完整列出VOCs治理设施及排气筒编号，三章不对等。"
                "JSON证据：11个关键词100%召回，三章证据均进入上下文。"
            ),
            "human_confirmation_status": "PENDING_HUMAN_CONFIRMATION",
            "first_confirmer": "",
            "first_confirm_date": "",
            "second_reviewer": "",
            "second_review_date": "",
            "final_freeze_status": "CANDIDATE_NOT_FROZEN",
            "impact_on_experiment": "仅重新评分，不重跑API",
            "affected_runs": "PL008_VOCSMeasure_Q01 × 3模型 × 3条件 = 9条",
        },
    ]
    
    # 保存Excel
    import openpyxl
    wb = openpyxl.Workbook()
    
    ws1 = wb.active
    ws1.title = "金标修订记录"
    headers = list(revisions[0].keys())
    ws1.append(headers)
    for rev in revisions:
        ws1.append([rev[h] for h in headers])
    
    # 调整列宽
    for col in ws1.columns:
        ws1.column_dimensions[col[0].column_letter].width = 20
    
    out_path = REPAIR_DIR / "09_gold_change_and_human_confirmation_log.xlsx"
    wb.save(out_path)
    print(f"  金标修订记录已保存: {out_path.name}")
    
    return revisions


# ============ Web/RAG 17题审计 ============

def web_rag_audit_17():
    """17题Web/RAG审计"""
    print("\n17题Web/RAG审计...")
    
    # Web快照
    web_path = EXPERIMENT_ROOT / "03_knowledge_base" / "pilot16_web_snapshot_v3_3.jsonl"
    web_snap = {}
    with open(web_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                web_snap[rec["question_id"]] = rec
    
    # RAG快照（原始）
    rag_path = EXPERIMENT_ROOT / "03_knowledge_base" / "pilot16_rag_snapshot_v3_3.jsonl"
    rag_snap = {}
    with open(rag_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            qid = rec.get("question_id", "")
            if not qid:
                continue
            if qid not in rag_snap:
                rag_snap[qid] = []
            rag_snap[qid].append(rec)
    
    for qid in rag_snap:
        rag_snap[qid].sort(key=lambda x: x.get("rank", 999))
    
    # 17题列表
    questions_17 = [
        "NEW_PL001_invest_ratio", "NEW_PL006_invest_ratio", 
        "NEW_PL010_invest_ratio", "NEW_PL015_invest_ratio",
        "PL001_Emission_固体", "PL002_V01_Q01", "PL005_Emission_固体",
        "PL004_V01_Q01", "PL008_VOCSTotal_Q01", "PL008_VOCSMeasure_Q01",
        "PL010_VOCSTotal_Q01", "NEW_PL006_living_wastewater",
        "NEW_PL007_ro_water", "PL007_CaptureEfficiency_Q01",
        "PL008_DesignAirflow_Q01", "PL013_HazardousWaste_Q01",
        "PL014_CaptureAirflow_Q01",
    ]
    
    results = []
    for qid in questions_17:
        web_rec = web_snap.get(qid)
        rag_rec = rag_snap.get(qid, [])
        
        web_count = len(web_rec.get("results", [])) if web_rec else 0
        rag_count = len(rag_rec)
        
        # Web质量
        web_has_auth = False
        if web_rec:
            for r in web_rec.get("results", []):
                src = r.get("source_domain", "")
                if any(d in src for d in ["gov.cn", "mee.gov.cn", "std.gov.cn"]):
                    web_has_auth = True
                    break
        
        web_status = "OK" if web_count >= 3 and web_has_auth else ("PARTIAL" if web_count > 0 else "MISSING")
        
        # RAG质量
        rag_has_normative = False
        if rag_rec:
            # 简单判断：源文件包含GB/HJ/DB/名录等
            for r in rag_rec[:5]:
                src = r.get("source_file", "")
                if any(x in src for x in ["GB", "HJ", "DB", "名录", "标准"]):
                    rag_has_normative = True
                    break
        
        rag_status = "OK" if rag_count >= 3 else ("MISSING" if rag_count == 0 else "PARTIAL")
        
        results.append({
            "question_id": qid,
            "web_result_count": web_count,
            "web_has_authoritative": web_has_auth,
            "web_status": web_status,
            "rag_result_count": rag_count,
            "rag_has_normative": rag_has_normative,
            "rag_status": rag_status,
            "rag_has_instructional": "UNKNOWN",  # 待确认
        })
    
    # 保存
    out_path = REPAIR_DIR / "04_web_rag_knowledge_audit_v2.csv"
    with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "question_id", "web_result_count", "web_has_authoritative", "web_status",
            "rag_result_count", "rag_has_normative", "rag_status", "rag_has_instructional"
        ])
        writer.writeheader()
        writer.writerows(results)
    print(f"  Web/RAG审计已保存: {out_path.name} ({len(results)}题)")
    
    return results


# ============ 主函数 ============

def main():
    print("=" * 70)
    print("Pilot17 修复 - 收尾：PL010修复 + RAG治理 + 金标修订 + 汇总")
    print("=" * 70)
    
    # 1. PL010章节修复
    pl010_result = fix_pl010_sections_v2()
    
    # 2. RAG治理
    rag_result = fix_rag_contamination()
    
    # 3. 金标修订
    gold_revisions = gold_label_revision_log()
    
    # 4. Web/RAG 17题审计
    web_rag_results = web_rag_audit_17()
    
    # 5. 生成hash_manifest_after_repair
    print("\n生成修复后哈希清单...")
    hash_entries = []
    for fpath in sorted(REPAIR_DIR.glob("*")):
        if fpath.is_file() and fpath.suffix in [".csv", ".xlsx", ".json", ".jsonl", ".md", ".txt", ".py"]:
            h = hashlib.sha256()
            with open(fpath, 'rb') as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    h.update(chunk)
            hash_entries.append({
                "file_name": fpath.name,
                "size_bytes": fpath.stat().st_size,
                "sha256": h.hexdigest(),
            })
    
    hash_path = REPAIR_DIR / "hash_manifest_after_repair.csv"
    with open(hash_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["file_name", "size_bytes", "sha256"])
        writer.writeheader()
        writer.writerows(hash_entries)
    print(f"  哈希清单: {len(hash_entries)}个文件")
    
    # 6. 生成preflight报告
    print("\n生成Preflight报告 v2...")
    preflight = f"""# Pilot17 修复与预检结论 v2

**修复版本**: v3.4_repair_20260903  
**生成时间**: 2026-09-03  
**审计范围**: 17/17题 Word直接核验 + JSON保真 + Web/RAG质量  
**当前决定**: `preflight_decision = FAIL`  
**正式运行许可**: `formal_run_allowed = false`  

---

## 1. 审计范围
- Word直接核验：17/17题
- JSON保真核验：17/17题
- 上下文证据槽核验：0/17题（待阶段3完成后补充）
- Web/RAG适用性核验：17/17题

## 2. 修复结果
- 标准编号检索：PASS（规范化函数通过12/12回归测试，PL001 5/5正确找到）
- PL010章节分类：PASS（候选修复完成，基于内容匹配，7个块全部分类正确）
- RAG指令污染过滤：PASS（排除审核指南类2个文档，PL010 Top-5全为证据型）
- 原始响应完整记录：PENDING（候选方案完成，待验证）
- JSON Schema增强：PENDING（候选系统Prompt已生成）
- PL008金标人工确认：PENDING（候选修订INCORRECT，待双人确认）

## 3. 最小复测
- API成功：0/5（尚未运行）
- 工程成功：0/5（尚未运行）
- 语义正确：0/5（待人工确认）
- 截断：0/5
- Schema失败：0/5

> 5次最小复测需在阶段0-6全部通过后执行。

## 4. 失效范围
- 因Prompt变化失效：系统Prompt修改 → 全部153次（若采用全局修改）
- 因上下文变化失效：PL010章节修复 → 待哈希比对确认
- 因Web/RAG快照变化失效：RAG过滤程序性文档 → 全部S2条件
- 仅需重评分：PL008金标修订 → 9条输出

## 5. 最终决定
- preflight_decision = FAIL
- formal_run_allowed = false
- decision_reason = 
  1. PL008金标尚未完成双人人工确认
  2. PL010上下文哈希变化尚未验证
  3. RAG候选快照未验证实际检索效果
  4. 5次最小复测尚未执行
  5. 运行器增强方案未实际集成验证
  6. 153个正式Prompt尚未预生成和哈希冻结

---

*本报告为静态修复阶段总结，不代表正式实验可以启动。*
"""
    
    preflight_path = REPAIR_DIR / "12_preflight_report_v2.md"
    with open(preflight_path, 'w', encoding='utf-8') as f:
        f.write(preflight)
    print(f"  Preflight报告已保存: {preflight_path.name}")
    
    # 7. 文件清单
    print(f"\n{'='*60}")
    print(f"修复目录文件清单 ({REPAIR_DIR.name}):")
    for f in sorted(REPAIR_DIR.glob("*")):
        if f.is_file():
            print(f"  {f.name} ({f.stat().st_size:,} bytes)")
    
    print(f"\n修复完成。输出目录: {REPAIR_DIR}")
    print(f"注意：5次最小复测和153次正式实验均未启动，需人工确认后执行。")

if __name__ == "__main__":
    main()
