# -*- coding: utf-8 -*-
"""#23-#30 新增知识检索验证（81源版，正式实验参数 candidate_top_k=30 final_top_k=5 rerank开）"""
import json, os, sys
from pathlib import Path
sys.path.insert(0, r"E:\实验文件整理_按论文逻辑\自建脚本_统一管理")
from hybrid_retrieval import HybridRetriever

INDEX = Path(r"E:\实验文件整理_按论文逻辑\04_知识库构建\正式实验RAG知识库_81源扩展版_20260820\03_RAG全文级检索_81知识源\03_混合检索索引")
OUT = Path(r"E:\实验文件整理_按论文逻辑\04_知识库构建\81源知识库入库执行记录_20260820\检索验证_23-30_20260820.json")

F23 = "#23_机械行业产污系数手册摘录_33-37_431-434.md"
F24 = "#24_电子电气行业产污系数手册摘录_38-40.md"
F25 = "#25_涂料制造行业产污系数手册摘录_2641.md"
F26 = "#26_废弃资源综合利用行业系数摘录_4220.md"
F27 = "#27_污染物源强产生收集处理排放闭合核算指南.md"
F28 = "#28_活性炭吸附治理参数核算审核指南.md"
F29 = "#29_VOCs排放核算与总量一致性审核指南.md"
F30 = "#30_废气收集形式与排风量计算审核指南.md"

TESTS = [
    {"test_id":"T01","query":"喷塑工序颗粒物产污系数是多少？","expect":[F23],"note":"目标300 kg/t-原料"},
    {"test_id":"T02","query":"钻铣车削能否直接套用下料5.30kg/t颗粒物系数？","expect":[F23],"note":"机械加工边界"},
    {"test_id":"T03","query":"机械行业下料工段颗粒物产污系数是多少？","expect":[F23],"note":"目标5.30 kg/t-原料"},
    {"test_id":"T04","query":"无铅锡条波峰焊颗粒物产污系数是多少？","expect":[F24],"note":"目标4.134e-1 g/kg-焊料"},
    {"test_id":"T05","query":"无铅锡膏回流焊颗粒物产污系数是多少？","expect":[F24],"note":"目标3.638e-1 g/kg-焊料"},
    {"test_id":"T06","query":"水性工业涂料VOCs产污系数是多少？","expect":[F25],"note":"目标2.00 kg/t-产品"},
    {"test_id":"T07","query":"2641涂料制造手册是否有UV光固化涂料专门系数？","expect":[F25],"note":"UV无条目负证据"},
    {"test_id":"T08","query":"废PS/ABS干法破碎颗粒物产污系数是多少？","expect":[F26],"note":"目标425 g/t-原料"},
    {"test_id":"T09","query":"企业自身注塑边角料破碎回用能否直接套用4220系数？","expect":[F26],"note":"4220适用边界"},
    {"test_id":"T10","query":"污染物产生量、收集量、治理削减量和排放量如何闭合？","expect":[F27],"note":"闭合链条"},
    {"test_id":"T11","query":"两级治理设施的综合治理效率能否直接相加？","expect":[F27],"note":"η总=1-(1-η1)(1-η2)"},
    {"test_id":"T12","query":"串联治理设施综合效率如何计算？","expect":[F27],"note":"串联公式"},
    {"test_id":"T13","query":"广东2023活性炭吸附比例建议取多少？","expect":[F28],"note":"目标15%"},
    {"test_id":"T14","query":"20%能否作为通用活性炭吸附比例？","expect":[F28],"note":"20%边界"},
    {"test_id":"T15","query":"VOCs总排放量与有组织、无组织是什么关系？","expect":[F29,F27],"note":"总排放=有组织+无组织"},
    {"test_id":"T16","query":"报告内部总量算术一致是否等于符合行政总量政策？","expect":[F29],"note":"内部核算与政策分层"},
    {"test_id":"T17","query":"HJ2026对吸附治理设施设计风量有什么要求？","expect":[F30,F28],"note":"设计风量120%"},
    {"test_id":"T18","query":"Q=1.4×P×H×V×3600能否说成GB/T16758规定公式？","expect":[F30],"note":"周长法边界"},
    {"test_id":"T19","query":"喷粉房60次/h换气次数能否作为国标统一要求？","expect":[F30],"note":"换气次数边界"},
]

def main():
    key = os.environ.get("DASHSCOPE_API_KEY", "")
    retriever = HybridRetriever(INDEX, key)
    report = {
        "title": "#23-#30 新增知识检索验证（81源版）",
        "index_dir": str(INDEX),
        "params": "candidate_top_k=30, final_top_k=5, rerank=gte-rerank-v2（与正式实验一致）",
        "tests": [],
    }
    summary = {"total": len(TESTS), "hit_in_top5": 0, "hit_in_top3": 0, "miss": []}
    for t in TESTS:
        result = retriever.retrieve(t["query"], candidate_top_k=30, final_top_k=5, use_rerank=True)
        hits = []
        target_rank = None
        for h in result["hits"]:
            is_target = h["source_file"] in t["expect"]
            if is_target and target_rank is None:
                target_rank = h["rank"]
            hits.append({
                "rank": h["rank"],
                "source_file": h["source_file"],
                "source_id": h["source_id"],
                "child_id": h["child_id"],
                "parent_id": h["parent_id"],
                "score": round(h["score"], 5),
                "child_content": h["child_content"],
                "is_target": is_target,
            })
        hit = target_rank is not None
        if hit:
            summary["hit_in_top5"] += 1
            if target_rank <= 3:
                summary["hit_in_top3"] += 1
        else:
            summary["miss"].append(t["test_id"])
        report["tests"].append({
            "test_id": t["test_id"],
            "query": t["query"],
            "note": t["note"],
            "expected_source": t["expect"],
            "target_hit": hit,
            "target_rank": target_rank,
            "top5": hits,
        })
        print(f'== {t["test_id"]} == hit={hit} rank={target_rank} | {t["query"]}')
        for h in hits:
            mark = "  <== TARGET" if h["is_target"] else ""
            print(f'  R{h["rank"]} [{h["score"]:.4f}] {h["source_file"]} | {h["child_id"]}{mark}')
    report["summary"] = summary
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\nSUMMARY:", json.dumps(summary, ensure_ascii=False))
    print("saved:", OUT)

if __name__ == "__main__":
    main()
