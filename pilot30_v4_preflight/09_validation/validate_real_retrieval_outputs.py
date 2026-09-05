#!/usr/bin/env python3
"""拒绝把空文件、注释或 PENDING_RETRIEVAL 当作真实检索结果。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


EXPECTED = {
    "01_bm25_top20.jsonl": 20,
    "02_dense_top20.jsonl": 20,
    "03_rrf_top20.jsonl": 20,
    "04_rerank_top10.jsonl": 10,
    "05_final_top5.jsonl": 5,
}
REQUIRED_KEYS = {"rank", "child_id", "source_id", "source_title", "content_sha256"}


def read_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    errors: list[str] = []
    if not path.exists():
        return records, [f"MISSING {path}"]
    raw = path.read_text(encoding="utf-8-sig")
    if "PENDING_RETRIEVAL" in raw:
        errors.append(f"PLACEHOLDER {path}")
    for line_no, line in enumerate(raw.splitlines(), 1):
        text = line.strip()
        if not text or text.startswith("//") or text.startswith("#"):
            continue
        try:
            item = json.loads(text)
        except json.JSONDecodeError as exc:
            errors.append(f"INVALID_JSON {path}:{line_no} {exc}")
            continue
        if not isinstance(item, dict):
            errors.append(f"NOT_OBJECT {path}:{line_no}")
            continue
        records.append(item)
    if not records:
        errors.append(f"NO_REAL_RECORDS {path}")
    return records, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    base = args.repo_root.resolve() / "pilot30_v4_preflight"
    questions_file = base / "01_questions" / "formal_questions.csv"
    snapshots = base / "06_retrieval_snapshots"
    errors: list[str] = []

    with questions_file.open("r", encoding="utf-8-sig", newline="") as handle:
        questions = list(csv.DictReader(handle))
    rag_questions = [q for q in questions if q.get("analysis_role") == "RAG_PRIMARY"]
    if len(rag_questions) != 14:
        errors.append(f"RAG_PRIMARY_COUNT expected=14 actual={len(rag_questions)}")

    for question in rag_questions:
        qid = question["question_id"]
        qdir = snapshots / qid
        query_path = qdir / "00_query.json"
        if not query_path.exists():
            errors.append(f"MISSING {query_path}")
        else:
            raw = query_path.read_text(encoding="utf-8-sig")
            if "PENDING_RETRIEVAL" in raw:
                errors.append(f"PLACEHOLDER {query_path}")
            try:
                query = json.loads(raw)
                if not isinstance(query, dict) or not query.get("query"):
                    errors.append(f"QUERY_EMPTY {query_path}")
            except json.JSONDecodeError as exc:
                errors.append(f"INVALID_JSON {query_path} {exc}")

        for filename, minimum in EXPECTED.items():
            records, file_errors = read_jsonl(qdir / filename)
            errors.extend(file_errors)
            if len(records) < minimum:
                errors.append(f"TOO_FEW {qdir / filename} expected>={minimum} actual={len(records)}")
            for index, record in enumerate(records, 1):
                missing = REQUIRED_KEYS - record.keys()
                if missing:
                    errors.append(
                        f"MISSING_KEYS {qdir / filename}:{index} {','.join(sorted(missing))}"
                    )
                if not (record.get("child_text") or record.get("context_text")):
                    errors.append(f"NO_TEXT {qdir / filename}:{index}")

    status = "PASS" if not errors else "FAIL"
    print(f"validation_status={status}")
    print(f"rag_primary_count={len(rag_questions)}")
    print(f"error_count={len(errors)}")
    for error in errors:
        print(error)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
