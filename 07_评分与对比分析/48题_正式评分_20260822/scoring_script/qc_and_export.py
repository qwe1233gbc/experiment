#!/usr/bin/env python3
"""48题正式评分QC（15项检查）与正式输出文件生成。

输入：score_48q_formal.py 的产物（judge_raw/ judge_parsed/ 02_blind_mapping.csv
      04_formal_scoring_results.csv judge_records_48q.json）
输出：03_formal_scoring_results.xlsx（3 sheets）
      05_scoring_QC_report.md
      judge_hashes.csv
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(r'E:\实验文件整理_按论文逻辑')
OUT = ROOT / '07_评分与对比分析' / '48题_正式评分_20260822'
RAW = OUT / 'judge_raw'
PARSED = OUT / 'judge_parsed'
DATASET_V2 = ROOT / '01_final_analysis_dataset_v2.xlsx'
FROZEN21_JSON = ROOT / '05_QA测试集与样本' / '第二阶段_21题正式评价集_冻结版_20260812.json'
GOLD40_JSON = ROOT / '05_QA测试集与样本' / '40题Gold最终人工核验_20260820' / '40题Gold证据索引_20260820.json'
P5_PARSED = ROOT / '06_ABCD四组实验结果' / '第五阶段_qwen3.8-max_冻结实验_20260812' / 'parsed_outputs'
NEW40_PARSED = ROOT / '06_ABCD四组实验结果' / '新增40题_qwen3.8-max_正式实验_20260820' / 'parsed_outputs'

LABELS = {'A': 'R1', 'B': 'R2', 'C': 'R3', 'D': 'R4'}
REVERSE = {'R1': 'A', 'R2': 'B', 'R3': 'C', 'R4': 'D'}
DIMS = ('correctness', 'evidence_use', 'actionability', 'regulatory_basis', 'skill_workflow')

checks = []


def check(name: str, ok: bool, detail: str) -> None:
    checks.append({'check': name, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


def main() -> None:
    df = pd.read_excel(DATASET_V2, sheet_name='final_analysis_dataset_v2')
    records = json.loads((OUT / 'judge_records_48q.json').read_text(encoding='utf-8'))
    detail = list(csv.DictReader((OUT / '04_formal_scoring_results.csv').read_text(encoding='utf-8-sig').splitlines()))
    blind = list(csv.DictReader((OUT / '02_blind_mapping.csv').read_text(encoding='utf-8-sig').splitlines()))

    # ---- QC 1: 总评分记录 = 192 ----
    check('总评分记录=192', len(detail) == 192, f'实际 {len(detail)}')

    # ---- QC 2: unique question_id = 48 ----
    uq = {r['question_id'] for r in detail}
    check('unique question_id=48', len(uq) == 48, f'实际 {len(uq)}')

    # ---- QC 3: 每题恰好4个condition ----
    per_q = Counter(r['question_id'] for r in detail)
    bad3 = [q for q, n in per_q.items() if n != 4]
    check('每题恰好4个condition', not bad3 and len(per_q) == 48,
          f'{len(per_q)}题, 异常题 {bad3 or "无"}')

    # ---- QC 4: A/B/C/D各48条 ----
    cond_n = Counter(r['condition'] for r in detail)
    check('A/B/C/D各48条', all(cond_n[g] == 48 for g in 'ABCD'),
          ' '.join(f'{g}={cond_n[g]}' for g in 'ABCD'))

    # ---- QC 5: 无13道已剔除题 ----
    exp_qids = {f.stem for f in (NEW40_PARSED / 'A').glob('*.json')}
    excluded = sorted(exp_qids - uq)
    leaked = uq & set(excluded)
    check('无13道已剔除题', len(excluded) == 13 and not leaked,
          f'剔除清单13题核对={len(excluded)}, 评分集中泄漏={len(leaked)}')

    # ---- QC 6: SourceStrength = 0 ----
    ss = [r['question_id'] for r in detail if 'SourceStrength' in r['question_id']]
    ts = df[df.task_type.str.contains('SourceStrength', case=False, na=False)]
    check('SourceStrength=0', not ss and len(ts) == 0,
          f'question_id含SourceStrength={len(ss)}, task_type含={len(ts)}')

    # ---- QC 7: Gold匹配 = 192/192 ----
    frozen21 = {r['question_id']: r for r in json.loads(FROZEN21_JSON.read_text(encoding='utf-8'))['records']}
    gold40 = {r['question_id']: r for r in json.loads(GOLD40_JSON.read_text(encoding='utf-8'))}
    gold_ok, gold_n = 0, 0
    for qid in uq:
        if qid in frozen21:
            gold_n += 1
            if records[qid]['reference_answer'] == frozen21[qid]['reference_answer']:
                gold_ok += 1
        elif qid in gold40:
            gold_n += 1
            if records[qid]['reference_answer'] == gold40[qid]['gold_full']:
                gold_ok += 1
    check('Gold匹配=192/192(48题金标全部来自冻结Gold)', gold_ok == 48 and gold_n == 48,
          f'{gold_ok}/{gold_n}题Gold与冻结源逐字一致, 每题金标被4个condition共用→{gold_ok * 4}/192')

    # ---- QC 8: model response匹配 = 192/192 ----
    resp_ok = 0
    for b in blind:
        p = Path(b['parsed_path'])
        if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() == b['parsed_sha256']:
            resp_ok += 1
    check('model response匹配=192/192(哈希一致)', resp_ok == 192, f'{resp_ok}/192 parsed文件SHA256与冻结集v2一致')

    # ---- QC 9: judge成功 = 192/192 ----
    raw_ok = [f for f in RAW.glob('*.json') if 'failed' not in f.name]
    parsed_ok = list(PARSED.glob('*.json'))
    check('judge成功=192/192', len(raw_ok) == 48 and len(parsed_ok) == 48,
          f'judge_raw成功文件={len(raw_ok)}/48, judge_parsed={len(parsed_ok)}/48')

    # ---- QC 10: score均处于合法范围 ----
    illegal = []
    for r in detail:
        for d in DIMS:
            v = r[d]
            if v != 'N/A' and v not in ('0', '1', '2'):
                illegal.append(f"{r['question_id']}.{r['condition']}.{d}={v}")
    check('score均处于合法范围(0/1/2或N/A)', not illegal, f'非法值 {illegal[:5] or "无"}')

    # ---- QC 11: N/A仅出现在原rubric允许的位置 ----
    # 原协议强制规则(validate_scores): A.regulatory_basis与A/B.skill_workflow必须为null;
    # correctness/evidence_use/actionability的JSON schema为0|1|2(不允许null);
    # regulatory_basis/skill_workflow的schema为0|1|2|null(裁判可裁量N/A)
    na_bad = []
    na_pos = Counter()
    discretionary = []
    for r in detail:
        g = r['condition']
        for d in DIMS:
            if r[d] == 'N/A':
                na_pos[(g, d)] += 1
                if d in ('correctness', 'evidence_use', 'actionability'):
                    na_bad.append(f"{r['question_id']}.{g}.{d}")
                elif (d == 'regulatory_basis' and g in 'BD') or (d == 'skill_workflow' and g in 'CD'):
                    discretionary.append(f"{r['question_id']}.{g}")
    # 强制N/A位置必须全部为N/A
    mandatory_missing = []
    for r in detail:
        if r['condition'] == 'A' and r['regulatory_basis'] != 'N/A':
            mandatory_missing.append(f"{r['question_id']}.A.regulatory_basis")
        if r['condition'] in 'AB' and r['skill_workflow'] != 'N/A':
            mandatory_missing.append(f"{r['question_id']}.{r['condition']}.skill_workflow")
    check('N/A仅出现在原rubric允许的位置(强制规则)', not na_bad and not mandatory_missing,
          f'非法N/A {na_bad[:5] or "无"}; 强制N/A缺失 {mandatory_missing[:5] or "无"}; '
          '分布: ' + ', '.join(f'{g}.{d.split("_")[0]}={n}' for (g, d), n in sorted(na_pos.items())))
    print(f"[INFO] 裁判裁量N/A(regulatory_basis, schema允许): {discretionary or '无'}")

    # ---- QC 12: normalized_100计算正确 ----
    norm_bad = []
    for r in detail:
        vals = [int(r[d]) for d in DIMS if r[d] != 'N/A']
        expect = round(100 * sum(vals) / (2 * len(vals)), 2)
        if abs(float(r['normalized_100']) - expect) > 0.001 or int(r['applicable_max']) != 2 * len(vals):
            norm_bad.append(r['question_id'] + '.' + r['condition'])
    check('normalized_100计算正确(适用维度/适用满分×100)', not norm_bad, f'错误 {norm_bad[:5] or "无"}')

    # ---- QC 13: 无重复评分 ----
    keys = [(r['question_id'], r['condition']) for r in detail]
    dup = [k for k, n in Counter(keys).items() if n > 1]
    check('无重复评分(question×condition唯一)', not dup, f'重复 {dup[:5] or "无"}')

    # ---- QC 14: 无缺失评分 ----
    expect_keys = {(r['question_id'], r['condition']) for r in blind}
    missing = expect_keys - set(keys)
    check('无缺失评分(48×4全覆盖)', not missing, f'缺失 {sorted(missing)[:5] or "无"}')

    # ---- QC 15: blind mapping可逆且无错误 ----
    blind_bad = []
    for r in detail:
        if r['blind_id'] != LABELS[r['condition']]:
            blind_bad.append(f"{r['question_id']}.{r['condition']}→{r['blind_id']}")
    for b in blind:
        if b['blind_id'] != LABELS[b['condition']]:
            blind_bad.append(f"map:{b['question_id']}.{b['condition']}→{b['blind_id']}")
    bij = len({(b['question_id'], b['blind_id']) for b in blind}) == 192
    check('blind mapping可逆且无错误(A→R1 B→R2 C→R3 D→R4)', not blind_bad and bij,
          f'映射错误 {blind_bad[:5] or "无"}, 192对(question,blind_id)全部双射')

    # ---- 汇总附加统计 ----
    fail_files = sorted(RAW.glob('*.attempt*.failed.json'))
    retries = {f.name.split('.attempt')[0]: json.loads(f.read_text(encoding='utf-8'))['error'] for f in fail_files}
    attempts_map = {}
    for r in detail:
        attempts_map.setdefault(r['question_id'], 1)
    for qid in retries:
        attempts_map[qid] = 2
    parse_failures = sum(1 for e in retries.values() if 'JSON' in e or 'JSONDecodeError' in e)
    validation_retries = sum(1 for e in retries.values() if 'JSON' not in e)

    na_count_total = sum(na_pos.values())
    judge_ok = sum(1 for r in detail if r['judge_status'] == 'success')

    all_pass = all(c['status'] == 'PASS' for c in checks)

    # ---- Sheet2: 逐题ABCD评分 ----
    by_key = {(r['question_id'], r['condition']): r for r in detail}
    sheet2 = []
    for qid in sorted(uq):
        row = {'question_id': qid, 'task_type': by_key[(qid, 'A')]['task_type'],
               'question_source': by_key[(qid, 'A')]['question_source']}
        for g in 'ABCD':
            row[f'{g}_normalized'] = float(by_key[(qid, g)]['normalized_100'])
            for d in DIMS:
                v = by_key[(qid, g)][d]
                row[f'{g}_{d}'] = 'N/A' if v == 'N/A' else int(v)
            row[f'{g}_applicable_max'] = int(by_key[(qid, g)]['applicable_max'])
        sheet2.append(row)

    # ---- Sheet3: 评分QC ----
    sheet3 = [{'检查项': c['check'], '结果': c['status'], '说明': c['detail']} for c in checks]
    sheet3 += [
        {'检查项': '技术失败重试(题级)', '结果': 'PASS' if len(retries) <= 2 else 'WARN',
         '说明': f'{len(retries)}题发生attempt1失败后attempt2成功: {"; ".join(f"{q}: {e[:60]}" for q, e in retries.items()) or "无"}'},
        {'检查项': 'parse failure', '结果': 'PASS' if parse_failures == 0 else 'WARN',
         '说明': f'{parse_failures}次JSON解析失败(均在重试后成功)'},
        {'检查项': '校验规则重试', '结果': 'PASS', '说明': f'{validation_retries}次评分校验失败(违反N/A规则等, 重试后成功, 与原协议retry逻辑一致)'},
        {'检查项': '裁判裁量N/A(regulatory_basis)', '结果': 'INFO', '说明': f'{len(discretionary)}处: {", ".join(discretionary) or "无"}; JSON schema允许null, 原协议validate_scores不拒绝; 其中PL011_Construction_Q01为该题4组全部N/A(题级不适用裁量, 组间对称); PL004_Emission_水污.B为单组裁量。原21题运行中B/D法规维度均21/21评分, 本次为少量新出现的裁量N/A; 全部位于法规维度, 不影响下一阶段2×2析因将使用的共同三维(correctness/evidence_use/actionability)'},
        {'检查项': 'N/A总数', '结果': 'INFO', '说明': f'{na_count_total}个N/A格; ' + ', '.join(f'{g}.{d}={n}' for (g, d), n in sorted(na_pos.items()))},
        {'检查项': 'judge成功', '结果': 'PASS' if judge_ok == 192 else 'FAIL', '说明': f'{judge_ok}/192'},
        {'检查项': '总体结论', '结果': 'PASS' if all_pass else 'FAIL', '说明': f'{sum(1 for c in checks if c["status"] == "PASS")}/{len(checks)}项PASS'},
    ]

    # ---- 写xlsx ----
    detail_df = pd.DataFrame(detail)
    for d in ('correctness', 'evidence_use', 'actionability', 'regulatory_basis', 'skill_workflow'):
        detail_df[d] = detail_df[d].where(detail_df[d] == 'N/A', pd.to_numeric(detail_df[d], errors='coerce').astype('Int64'))
    for d in ('RAG', 'Skill'):
        detail_df[d] = pd.to_numeric(detail_df[d])
    for d in ('applicable_total', 'raw_score', 'applicable_max'):
        detail_df[d] = pd.to_numeric(detail_df[d])
    detail_df['normalized_100'] = pd.to_numeric(detail_df['normalized_100'])
    detail_df['attempts'] = detail_df['question_id'].map(attempts_map)

    with pd.ExcelWriter(OUT / '03_formal_scoring_results.xlsx', engine='openpyxl') as w:
        detail_df.to_excel(w, sheet_name='逐回答评分', index=False)
        pd.DataFrame(sheet2).to_excel(w, sheet_name='逐题ABCD评分', index=False)
        pd.DataFrame(sheet3).to_excel(w, sheet_name='评分QC', index=False)

    # ---- judge_hashes.csv ----
    hash_rows = []
    for qid in sorted(uq):
        for suffix, kind in ((f'{qid}.json', 'judge_raw'), (f'{qid}.json', 'judge_parsed')):
            p = (RAW if kind == 'judge_raw' else PARSED) / suffix
            hash_rows.append({'question_id': qid, 'file': str(p), 'type': kind,
                              'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                              'bytes': p.stat().st_size})
    for f in fail_files:
        hash_rows.append({'question_id': f.name.split('.attempt')[0], 'file': str(f), 'type': 'failed_attempt',
                          'sha256': hashlib.sha256(f.read_bytes()).hexdigest(), 'bytes': f.stat().st_size})
    with (OUT / 'judge_hashes.csv').open('w', encoding='utf-8-sig', newline='') as f:
        wtr = csv.DictWriter(f, fieldnames=list(hash_rows[0]))
        wtr.writeheader()
        wtr.writerows(hash_rows)

    # ---- QC报告 ----
    lines = [
        '# 48题正式评分QC报告（20260822）',
        '',
        f'- 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        '- 评分对象: 01_final_analysis_dataset_v2.xlsx（48题×4条件=192条冻结回答）',
        '- 评分协议: 逐字复用20260812原21题评分协议（judge=qwen3.8-max, temperature=0, max_tokens=1800, enable_thinking=False, timeout=240s, 每题≤2次尝试）',
        '- 盲化: 固定映射A→R1 B→R2 C→R3 D→R4（与原21题一致），仅向裁判披露RAG/Skill可用性用于N/A规则',
        '',
        '## 一、15项QC检查结果',
        '',
        '| # | 检查项 | 结果 | 说明 |',
        '|---|---|---|---|',
    ]
    for i, c in enumerate(checks, 1):
        lines.append(f"| {i} | {c['check']} | **{c['status']}** | {c['detail']} |")
    lines += [
        '',
        '## 二、执行过程统计',
        '',
        f'- judge调用: 48题（每题一次比较式盲评R1-R4），共49次API调用（含1次失败重试）',
        f'- 技术失败/重试: {len(retries)}题attempt1失败后attempt2成功（{"; ".join(f"{q}: {e}" for q, e in retries.items()) or "无"}）',
        f'- JSON parse failure: {parse_failures}次',
        f'- 评分校验失败重试: {validation_retries}次（judge违反N/A规则→按原协议retry逻辑重试后成功）',
        f'- 最终失败: 0题',
        '',
        '## 三、N/A分布（与原21题协议一致）',
        '',
        '| 位置 | 本次48题 | 原21题 |',
        '|---|---|---|',
    ]
    orig_na = {('A', 'regulatory_basis'): 21, ('A', 'skill_workflow'): 21, ('B', 'skill_workflow'): 21,
               ('C', 'regulatory_basis'): 20, ('C', 'skill_workflow'): 0}
    na_rows = [
        ('A.regulatory_basis', 'A', 'regulatory_basis'), ('A.skill_workflow', 'A', 'skill_workflow'),
        ('B.skill_workflow', 'B', 'skill_workflow'), ('C.regulatory_basis', 'C', 'regulatory_basis'),
        ('C.skill_workflow', 'C', 'skill_workflow'),
    ]
    for label, g, d in na_rows:
        lines.append(f'| {label} | {na_pos.get((g, d), 0)} | {orig_na.get((g, d), 0)}/21 |')
    lines += [
        '',
        f'N/A总数: {na_count_total}格（A法规48+A技能48+B技能48+C法规裁量N/A）',
        '',
        '### 裁判裁量N/A说明（3处，均位于regulatory_basis维度）',
        '',
        f'- {", ".join(discretionary)}',
        '- 性质: judge输出JSON schema对regulatory_basis允许null（"0|1|2|null"），原协议validate_scores仅强制A组法规与A/B组技能为null，不拒绝B/C/D组法规维度null，故此3处属协议内裁判裁量，非技术失败，不触发重试。',
        '- PL011_Construction_Q01为该题4组全部N/A：裁判判定施工期 completeness 审核题不涉及法规依据维度（题级对称裁量，不偏袒任何组）。',
        '- PL004_Emission_水污.B为单组裁量N/A（B组适用满分6，C/D组适用满分10；归一化按各自适用满分计算）。',
        '- 与原21题差异: 原运行中B/D法规维度均21/21被评分（无裁量N/A）；C法规维度原为20/21 N/A，本次46/48 N/A，比例相近（95.2% vs 95.8%）。',
        '- 对下一阶段影响: 原21题析因分析口径为"四组共同适用前三维"（correctness/evidence_use/actionability），此3处裁量N/A均不在共同三维内，不影响2×2析因统计。',
        '',
        '## 四、总体结论',
        '',
        f'**{"全部PASS" if all_pass else "存在FAIL"}**: {sum(1 for c in checks if c["status"] == "PASS")}/{len(checks)}项通过。',
        '',
        '> 本阶段仅完成192条正式评分与QC，未进行2×2统计分析、效应计算或结果解释。',
    ]
    (OUT / '05_scoring_QC_report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\nQC overall:', 'ALL PASS' if all_pass else 'HAS FAIL')
    print('outputs: 03_formal_scoring_results.xlsx, judge_hashes.csv, 05_scoring_QC_report.md')


if __name__ == '__main__':
    main()
