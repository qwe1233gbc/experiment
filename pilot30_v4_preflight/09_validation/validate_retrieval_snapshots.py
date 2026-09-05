"""
Pilot30 V4 - 检索快照质量与金标泄漏快速验证
检查：占位符文件、JSON合法性、必填字段、金标泄漏
"""
import json
import re
from pathlib import Path

V4 = Path(__file__).parent.parent.resolve()
SNAPSHOT_DIR = V4 / '06_retrieval_snapshots'

# 金标泄漏关键词（不应出现在 query 中）
GOLD_LEAKAGE_PATTERNS = [
    r"正确答案",
    r"金标",
    r"gold.*standard",
    r"900-041-49",  # 具体危废代码（如果不在题干里就是泄漏）
    r"900-249-08",
    r"GB 18599.*适用范围.*不适用",  # 结论性描述
    r"CORRECT|INCORRECT|PARTIALLY",  # 结论标签
]


def check_jsonl_valid(path):
    """检查JSONL是否合法，返回 (ok, count, errors)"""
    if not path.exists():
        return False, 0, ["文件不存在"]
    try:
        lines = path.read_text(encoding='utf-8').strip().splitlines()
        if not lines:
            return False, 0, ["空文件"]
        # 检查是否是占位符
        first = lines[0]
        if "PENDING_RETRIEVAL" in first or "占位" in first or "// 状态" in first:
            return False, 0, ["占位符文件"]
        # 解析每行
        count = 0
        errors = []
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            try:
                json.loads(line)
                count += 1
            except json.JSONDecodeError as e:
                errors.append(f"第{i+1}行JSON错误: {e}")
        return len(errors) == 0, count, errors
    except Exception as e:
        return False, 0, [str(e)]


def check_gold_leakage(query_file):
    """检查query是否含金标泄漏"""
    if not query_file.exists():
        return True, 0, ["文件不存在"]
    try:
        data = json.loads(query_file.read_text(encoding='utf-8'))
        query = data.get('query', '')
        leakage_count = 0
        leakage_items = []
        for pattern in GOLD_LEAKAGE_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                leakage_count += 1
                leakage_items.append(pattern)
        return leakage_count == 0, leakage_count, leakage_items
    except Exception as e:
        return False, -1, [str(e)]


def main():
    issues = []
    placeholder_count = 0
    invalid_json_count = 0
    leakage_count = 0
    bm25_done = 0
    total_q = 0
    
    for qdir in sorted(SNAPSHOT_DIR.iterdir()):
        if not qdir.is_dir():
            continue
        qid = qdir.name
        total_q += 1
        
        # 检查 BM25
        bm25_file = qdir / "01_bm25_top20.jsonl"
        ok, count, errors = check_jsonl_valid(bm25_file)
        if not ok:
            if "占位符文件" in str(errors):
                placeholder_count += 1
            else:
                invalid_json_count += 1
            issues.append(f"{qid}/01_bm25_top20.jsonl: {errors}")
        else:
            if count >= 5:  # 至少有5条才算有效
                bm25_done += 1
        
        # 检查 query 泄漏
        query_file = qdir / "00_query.json"
        if query_file.exists():
            no_leak, leak_n, leak_items = check_gold_leakage(query_file)
            if not no_leak and leak_n > 0:
                leakage_count += 1
                issues.append(f"{qid}/00_query.json: 金标泄漏 {leak_n} 处: {leak_items}")
    
    print(f"题目总数: {total_q}")
    print(f"BM25完成: {bm25_done}/{total_q}")
    print(f"占位符文件: {placeholder_count}")
    print(f"非法JSON: {invalid_json_count}")
    print(f"金标泄漏: {leakage_count}")
    
    if issues:
        print(f"\n问题列表 ({len(issues)} 项):")
        for issue in issues[:20]:
            print(f"  - {issue}")
        if len(issues) > 20:
            print(f"  ... 还有 {len(issues)-20} 项")
    
    # 返回状态
    all_ok = placeholder_count == 0 and invalid_json_count == 0 and leakage_count == 0 and bm25_done == total_q
    print(f"\n总体状态: {'PASS' if all_ok else 'FAIL'}")
    return all_ok


if __name__ == '__main__':
    main()
