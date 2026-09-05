#!/usr/bin/env python3
"""48题×A/B/C/D正式评分（192条）。

逐字复用原21题评分协议（score_phase6_llm_judge.py, 20260812）：
- judge模型/参数/prompt模板/rubric/N-A规则/JSON解析/校验/重试 全部一致
- 盲化复用原固定映射 A→R1 B→R2 C→R3 D→R4
- 评分对象来自冻结集v2（旧21题=第五阶段正式实验；新增27题=新增40题正式实验20260820）
- Gold：旧21题=第二阶段冻结评价集；新增27题=40题Gold证据索引(人工核验冻结版)
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import time
from pathlib import Path

import requests

ROOT = Path(r'E:\实验文件整理_按论文逻辑')
OUT = ROOT / '07_评分与对比分析' / '48题_正式评分_20260822'
P5_PARSED = ROOT / '06_ABCD四组实验结果' / '第五阶段_qwen3.8-max_冻结实验_20260812' / 'parsed_outputs'
NEW40_PARSED = ROOT / '06_ABCD四组实验结果' / '新增40题_qwen3.8-max_正式实验_20260820' / 'parsed_outputs'
FROZEN21_JSON = ROOT / '05_QA测试集与样本' / '第二阶段_21题正式评价集_冻结版_20260812.json'
GOLD40_JSON = ROOT / '05_QA测试集与样本' / '40题Gold最终人工核验_20260820' / '40题Gold证据索引_20260820.json'
INPUT_FREEZE = ROOT / '06_ABCD四组实验结果' / '新增40题_正式输入冻结_20260820' / 'prompts_A.jsonl'
DATASET_V2 = ROOT / '01_final_analysis_dataset_v2.xlsx'

LABELS = {'A': 'R1', 'B': 'R2', 'C': 'R3', 'D': 'R4'}
REVERSE = {v: k for k, v in LABELS.items()}
DIMENSIONS = ('correctness', 'evidence_use', 'actionability', 'regulatory_basis', 'skill_workflow')


def extract_json(text: str) -> dict:
    clean = re.sub(r'^```(?:json)?\s*|\s*```$', '', text.strip(), flags=re.IGNORECASE)
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        for pos, char in enumerate(clean):
            if char == '{':
                try:
                    value, _ = decoder.raw_decode(clean[pos:])
                    return value
                except json.JSONDecodeError:
                    pass
    raise ValueError('裁判响应无可解析JSON')


def compact_response(row: dict, rag: bool, skill: bool) -> dict:
    internal = row.get('report_internal_result', {})
    external = row.get('external_validation_result', {})
    final = row.get('final_answer', {})
    return {
        'rag_available': rag,
        'skill_available': skill,
        'judgement': final.get('judgement'),
        'analysis': str(final.get('analysis', ''))[:900],
        'scope_note': str(final.get('scope_note', ''))[:240],
        'report_evidence': [
            {'fact': str(x.get('fact', ''))[:240], 'source_location': x.get('source_location')}
            for x in internal.get('evidence', [])[:3]
        ],
        'checks': [
            {'check_name': x.get('check_name'), 'result': x.get('result'),
             'explanation': str(x.get('explanation', ''))[:240]}
            for x in internal.get('checks', [])[:4]
        ],
        'issues': [str(x)[:240] for x in internal.get('issues', [])[:3]],
        'external_status': external.get('status'),
        'references_used': [str(x)[:180] for x in external.get('references_used', [])[:4]],
        'missing_references': [str(x)[:180] for x in external.get('missing_references', [])[:4]],
        'answer_mode': row.get('answer_mode'),
        'safety_flags': row.get('safety_flags', {}),
    }


def make_prompt(record: dict, responses: dict) -> str:
    blinded = {
        LABELS[g]: compact_response(responses[g], rag=g in 'BD', skill=g in 'CD')
        for g in 'ABCD'
    }
    rubric = {
        'correctness': '2=结论及关键理由与参考答案一致；1=主要方向部分一致但有实质遗漏/过度结论；0=关键结论相反或没有回答',
        'evidence_use': '2=使用了与判断直接相关、可定位的报告证据；1=有证据但不完整或定位模糊；0=无有效报告证据',
        'actionability': '2=问题存在时给出具体可执行修改/核验动作；无问题时明确保持项和边界也可得2；1=仅方向性建议；0=无可执行意见',
        'regulatory_basis': '2=法规/标准依据正确且足以支持结论；1=依据部分充分或条款不完整；0=依据错误/缺失；rag_available=false且标签为R1时必须为null（不适用），R3仍按实际输出评分',
        'skill_workflow': '2=完整体现该审核类型的分步核查、证据链和边界；1=部分体现；0=未体现；skill_available=false时必须为null（不适用）',
    }
    required = {
        'scores': [
            {
                'response_id': 'R1|R2|R3|R4',
                'correctness': '0|1|2',
                'evidence_use': '0|1|2',
                'actionability': '0|1|2',
                'regulatory_basis': '0|1|2|null',
                'skill_workflow': '0|1|2|null',
                'rationale': '不超过120字',
            }
        ]
    }
    return (
        '你是独立实验评分员。按同一尺度盲评四个匿名回答，不推断或偏袒实验组。'
        '参考答案是评分金标，但若模型指出报告证据支持的额外真实问题，不应仅因参考答案未展开而扣分。'
        '只能输出JSON。\n\n'
        f"【题号】{record['question_id']}\n【审核类型】{record['audit_type']}\n"
        f"【问题】{record['question']}\n【参考答案】{str(record['reference_answer'])[:1200]}\n"
        f"【报告金标证据】{json.dumps(record['report_evidence'][:4], ensure_ascii=False)[:1600]}\n\n"
        f"【评分规则】{json.dumps(rubric, ensure_ascii=False)}\n\n"
        f"【匿名回答】{json.dumps(blinded, ensure_ascii=False)}\n\n"
        f"【输出结构】{json.dumps(required, ensure_ascii=False)}"
    )


def validate_scores(payload: dict) -> list[dict]:
    rows = payload.get('scores', [])
    if len(rows) != 4 or {row.get('response_id') for row in rows} != set(REVERSE):
        raise ValueError('裁判必须返回R1-R4四条评分')
    by_id = {row['response_id']: row for row in rows}
    for label, row in by_id.items():
        for dim in DIMENSIONS:
            value = row.get(dim)
            if value is not None and value not in (0, 1, 2):
                raise ValueError(f'{label}.{dim}非法: {value}')
        group = REVERSE[label]
        if group == 'A' and row.get('regulatory_basis') is not None:
            raise ValueError('R1法规依据必须为null')
        if group in 'AB' and row.get('skill_workflow') is not None:
            raise ValueError(f'{label}技能流程必须为null')
    return [by_id[label] for label in ('R1', 'R2', 'R3', 'R4')]


def load_dataset():
    import pandas as pd
    df = pd.read_excel(DATASET_V2, sheet_name='final_analysis_dataset_v2')
    assert len(df) == 192 and df['question_id'].nunique() == 48
    return df


def build_records(df) -> dict:
    frozen21 = {r['question_id']: r for r in json.loads(FROZEN21_JSON.read_text(encoding='utf-8'))['records']}
    gold40 = {r['question_id']: r for r in json.loads(GOLD40_JSON.read_text(encoding='utf-8'))}
    questions_new = {}
    for line in INPUT_FREEZE.read_text(encoding='utf-8').splitlines():
        d = json.loads(line)
        questions_new[d['question_id']] = d['question']

    records = {}
    for qid in sorted(df['question_id'].unique()):
        if qid in frozen21:
            r = frozen21[qid]
            records[qid] = {
                'question_id': qid, 'audit_type': r['audit_type'], 'question': r['question'],
                'reference_answer': r['reference_answer'], 'report_evidence': r['report_evidence'],
                'source': 'old21_phase5_frozen',
            }
        else:
            g = gold40[qid]
            records[qid] = {
                'question_id': qid, 'audit_type': g['audit_type'], 'question': questions_new[qid],
                'reference_answer': g['gold_full'],
                'report_evidence': [{'section': g.get('pages', ''), 'excerpt': g.get('key_evidence', '')}],
                'source': 'new40_gold20260820',
            }
    return records


def parsed_path_for(qid: str, group: str, df) -> Path:
    row = df[(df.question_id == qid) & (df.condition == group)].iloc[0]
    return Path(row['parsed_path'])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', default='qwen3.8-max')
    parser.add_argument('--url', default='https://one-hub.hycx-gd.cn/v1/chat/completions')
    parser.add_argument('--concurrency', type=int, default=3)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--limit', type=int, default=0, help='仅评分前N题（0=全部）')
    parser.add_argument('--resume', action='store_true', help='跳过已有成功评分的题')
    args = parser.parse_args()

    key = os.environ.get('COMPANY_API_KEY', '')
    if not key and not args.prepare_only:
        raise RuntimeError('缺少COMPANY_API_KEY')

    raw_dir = OUT / 'judge_raw'
    parsed_dir = OUT / 'judge_parsed'
    raw_dir.mkdir(parents=True, exist_ok=True)
    parsed_dir.mkdir(parents=True, exist_ok=True)

    df = load_dataset()
    records = build_records(df)
    assert len(records) == 48

    task_type = dict(zip(df.question_id, df.task_type))
    project_id = dict(zip(df.question_id, df.project_id))
    cond_label = {(r.question_id, r.condition): r.condition_label for r in df.itertuples()}
    ragflag = {(r.question_id, r.condition): int(r.RAG) for r in df.itertuples()}
    skillflag = {(r.question_id, r.condition): int(r.Skill) for r in df.itertuples()}

    # 盲化映射（复用原固定映射 A→R1 B→R2 C→R3 D→R4）
    blind_rows = []
    for r in df.itertuples():
        blind_rows.append({
            'question_id': r.question_id, 'condition': r.condition, 'blind_id': LABELS[r.condition],
            'rag_available': 'true' if r.condition in 'BD' else 'false',
            'skill_available': 'true' if r.condition in 'CD' else 'false',
            'parsed_path': r.parsed_path, 'parsed_sha256': r.parsed_sha256,
        })
    import csv
    with (OUT / '02_blind_mapping.csv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(blind_rows[0]))
        w.writeheader()
        w.writerows(blind_rows)
    (OUT / 'judge_records_48q.json').write_text(
        json.dumps(records, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'blind mapping saved: {len(blind_rows)} rows; records: {len(records)}')

    if args.prepare_only:
        return

    qids = sorted(records)
    if args.limit:
        qids = qids[:args.limit]

    def judge(qid: str) -> dict:
        responses = {g: json.loads(parsed_path_for(qid, g, df).read_text(encoding='utf-8')) for g in 'ABCD'}
        prompt = make_prompt(records[qid], responses)
        last = ''
        for attempt in (1, 2):
            try:
                started = time.perf_counter()
                resp = requests.post(
                    args.url,
                    headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
                    json={'model': args.model, 'messages': [{'role': 'user', 'content': prompt}],
                          'temperature': 0, 'max_tokens': 1800, 'enable_thinking': False},
                    timeout=240,
                )
                if not resp.ok:
                    raise RuntimeError(f'HTTP {resp.status_code}: {resp.text[:800]}')
                payload = resp.json()
                content = payload.get('choices', [{}])[0].get('message', {}).get('content', '')
                scores = validate_scores(extract_json(content))
                raw_dir.joinpath(f'{qid}.json').write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
                parsed_dir.joinpath(f'{qid}.json').write_text(
                    json.dumps({'question_id': qid, 'prompt_chars': len(prompt), 'scores': scores},
                               ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
                return {'question_id': qid, 'scores': scores, 'attempt': attempt,
                        'elapsed': round(time.perf_counter() - started, 3), 'error': '',
                        'prompt_chars': len(prompt)}
            except Exception as exc:
                last = f'{type(exc).__name__}: {exc}'
                try:
                    raw_dir.joinpath(f'{qid}.attempt{attempt}.failed.json').write_text(
                        json.dumps({'question_id': qid, 'attempt': attempt, 'error': last},
                                   ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
                except Exception:
                    pass
        return {'question_id': qid, 'scores': [], 'attempt': 2, 'elapsed': 0, 'error': last, 'prompt_chars': 0}

    todo = [q for q in qids if not (args.resume and (raw_dir / f'{q}.json').exists())]
    print(f'judging {len(todo)} questions (skipped {len(qids) - len(todo)} already done)...')
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {pool.submit(judge, q): q for q in todo}
        for n, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            row = fut.result()
            results.append(row)
            print(f"[{n}/{len(todo)}] {row['question_id']} "
                  f"{'success' if row['scores'] else 'FAILED: ' + row['error'][:120]}", flush=True)

    failures = [r for r in results if not r['scores']]
    if failures:
        (OUT / 'judge_failures.json').write_text(
            json.dumps(failures, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'裁判失败 {len(failures)} 题，详见 judge_failures.json')
    else:
        (OUT / 'judge_failures.json').write_text('[]\n', encoding='utf-8')

    # 明细（无论是否有失败都写出已成功的部分）
    detail = []
    for qid in qids:
        rawf = raw_dir / f'{qid}.json'
        if not rawf.exists():
            continue
        parsed = json.loads((parsed_dir / f'{qid}.json').read_text(encoding='utf-8'))
        for score in parsed['scores']:
            group = REVERSE[score['response_id']]
            numeric = [score[d] for d in DIMENSIONS if score[d] is not None]
            detail.append({
                'question_id': qid, 'project_id': project_id[qid], 'task_type': task_type[qid],
                'condition': group, 'condition_label': cond_label[(qid, group)],
                'blind_id': score['response_id'], 'RAG': ragflag[(qid, group)], 'Skill': skillflag[(qid, group)],
                'correctness': score['correctness'], 'evidence_use': score['evidence_use'],
                'actionability': score['actionability'],
                'regulatory_basis': score['regulatory_basis'] if score['regulatory_basis'] is not None else 'N/A',
                'skill_workflow': score['skill_workflow'] if score['skill_workflow'] is not None else 'N/A',
                'applicable_total': sum(numeric), 'raw_score': sum(numeric),
                'applicable_max': 2 * len(numeric),
                'normalized_100': round(100 * sum(numeric) / (2 * len(numeric)), 2),
                'rationale': score.get('rationale', ''), 'judge_reason': score.get('rationale', ''),
                'judge_status': 'success', 'attempts': parsed.get('attempts', ''),
                'question_source': records[qid]['source'],
            })
    if detail:
        with (OUT / '04_formal_scoring_results.csv').open('w', encoding='utf-8-sig', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(detail[0]))
            w.writeheader()
            w.writerows(detail)
        print(f'detail rows: {len(detail)}')

    manifest = {
        'status': 'complete' if not failures else 'incomplete',
        'questions_total': len(qids), 'scored_outputs': len(detail),
        'model': args.model,
        'temperature': 0, 'max_tokens': 1800, 'enable_thinking': False,
        'concurrency': args.concurrency, 'timeout_s': 240, 'max_attempts': 2,
        'blinding': 'A/B/C/D hidden as R1/R2/R3/R4 (fixed mapping, same as 20260812); only RAG/Skill availability disclosed for N/A rules',
        'dataset': '01_final_analysis_dataset_v2.xlsx (old21=phase5 frozen experiment, new27=20260820 experiment)',
        'failures': len(failures),
    }
    (OUT / 'judge_execution_manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
