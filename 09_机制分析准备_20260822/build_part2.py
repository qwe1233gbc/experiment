#!/usr/bin/env python3
"""Part 2: 生成06_典型题ABCD对照.md（客观记录，零解释）。"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(r'E:\实验文件整理_按论文逻辑')
SCORE_DIR = ROOT / '07_评分与对比分析' / '48题_正式评分_20260822'
STAT = ROOT / '08_2x2析因统计_48题_20260822'
OUT = ROOT / '09_机制分析准备_20260822'
DIMS3 = ['correctness', 'evidence_use', 'actionability']


def load_gold(qid: str, gold_old: dict, gold_new: list) -> str:
    if qid in gold_old['records_idx']:
        r = gold_old['records_idx'][qid]
        return str(r['reference_answer'])[:500]
    for g in gold_new:
        if g['question_id'] == qid:
            v = g.get('gold_full') or g.get('gold') or ''
            verdict = g.get('verdict', '')
            return f'{str(v)[:450]}' + (f' ｜[verdict] {str(verdict)[:120]}' if verdict else '')
    return '(未找到)'


def load_response(parsed_path: str) -> dict:
    p = json.loads(Path(parsed_path).read_text(encoding='utf-8'))
    fa = p.get('final_answer', {}) or {}
    ext = p.get('external_validation_result', {}) or {}
    internal = p.get('report_internal_result', {}) or {}
    refs = ext.get('references_used', []) or []
    ev = internal.get('evidence', []) or []
    checks = internal.get('checks', []) or []
    return {
        'judgement': str(fa.get('judgement', ''))[:150],
        'analysis': str(fa.get('analysis', ''))[:350],
        'scope_note': str(fa.get('scope_note', ''))[:150],
        'answer_mode': p.get('answer_mode', ''),
        'references_used': [str(x)[:80] for x in refs[:4]],
        'ext_status': ext.get('status', ''),
        'report_evidence_count': len(ev),
        'checks_count': len(checks),
        'issues': [str(x)[:100] for x in (internal.get('issues', []) or [])[:3]],
    }


def main() -> None:
    score = pd.read_csv(SCORE_DIR / '04_formal_scoring_results.csv',
                        keep_default_na=False, na_values=['', 'N/A', 'NA'])
    score['common_3d_score'] = score[DIMS3].sum(axis=1)
    qle = pd.read_csv(STAT / '02_analysis_dataset' / 'question_level_effects.csv')
    v2 = pd.read_excel(ROOT / '01_final_analysis_dataset_v2.xlsx', sheet_name='final_analysis_dataset_v2')

    gold_old_raw = json.loads((ROOT / '05_QA测试集与样本' / '第二阶段_21题正式评价集_冻结版_20260812.json').read_text(encoding='utf-8'))
    gold_old = {'records_idx': {r['question_id']: r for r in gold_old_raw['records']}}
    gold_new_raw = json.loads((ROOT / '05_QA测试集与样本' / '40题Gold最终人工核验_20260820' / '40题Gold证据索引_20260820.json').read_text(encoding='utf-8'))

    qmap = v2.set_index(['question_id', 'condition'])

    def sel(df, col, asc, n=5):
        return df.sort_values(col, ascending=asc).head(n)[['question_id', 'task_type', col]].values.tolist()

    groups = {
        'A. Interaction最高的5题': sel(qle, 'c3_interaction', False),
        'B. Interaction最低的5题': sel(qle, 'c3_interaction', True),
        'C. Skill导致下降最明显的5题(C-A)': sel(qle, 'c3_skill_no_rag', True),
        'D. RAG使Skill恢复最明显的5题(D-C)': sel(qle, 'c3_rag_with_skill', False),
    }

    lines = ['# 典型题ABCD对照（客观记录版）', '',
             '> 性质：只记录事实（评分数值、回答判定、引用证据、judge理由原文），不写任何机制解释。',
             '> 每题字段：Gold摘要、A/B/C/D回答摘要、三维评分、judge理由、组间客观差异点。',
             '> 数据来源：02_final_gold(v2数据集gold_answer_path)、parsed_outputs(冻结parsed_path)、04_formal_scoring_results.csv。', '']

    for gname, qlist in groups.items():
        lines += [f'## {gname}', '']
        for qid, ttype, val in qlist:
            col = gname.split('(')[-1].rstrip(')') if '(' in gname else 'c3_interaction'
            sc = score[score.question_id == qid].set_index('condition')
            lines += [f'### {qid} ｜ task_type={ttype} ｜ {gname.split(".")[0]}值={val}', '',
                      f'**Gold摘要**：{load_gold(qid, gold_old, gold_new_raw)}', '', '**四组回答与评分：**', '']
            for cond in 'ABCD':
                r = qmap.loc[(qid, cond)]
                resp = load_response(r.parsed_path)
                s = sc.loc[cond]
                lines += [
                    f'- **{cond}组**（c3={s.common_3d_score:.0f}/6；correctness={s.correctness:.0f}, evidence_use={s.evidence_use:.0f}, actionability={s.actionability:.0f}）',
                    f'  - 判定：{resp["judgement"]}',
                    f'  - 分析摘要：{resp["analysis"]}',
                ]
                if resp['scope_note']:
                    lines.append(f'  - 范围说明：{resp["scope_note"]}')
                if resp['references_used']:
                    lines.append(f'  - 引用外部证据：{"; ".join(resp["references_used"])}')
                else:
                    lines.append(f'  - 引用外部证据：（无）  [ext_status={resp["ext_status"]}]')
                lines.append(f'  - 报告证据条数：{resp["report_evidence_count"]}；核查项数：{resp["checks_count"]}；answer_mode={resp["answer_mode"]}')
                if resp['issues']:
                    lines.append(f'  - 报告内部问题列表：{"; ".join(resp["issues"])}')
                lines.append(f'  - judge理由：{str(s.rationale)[:200]}')
            # 客观差异点（只陈述数值与事实）
            qrow = qle[qle.question_id == qid].iloc[0]
            lines += ['', '**组间客观差异（数值）**：',
                      f'- B-A={qrow.c3_B_minus_A}；C-A={qrow.c3_C_minus_A}；D-B={qrow.c3_D_minus_B}；D-C={qrow.c3_D_minus_C}；Interaction(D-B-C+A)={qrow.c3_interaction}',
                      f'- 四组judgement是否一致：{sc.judge_status.nunique() == 1 and "judgement字段为同构评分" or "见上方各组判定"}',
                      '']
            # 引用差异事实
            ref_counts = {}
            for cond in 'ABCD':
                r = qmap.loc[(qid, cond)]
                resp = load_response(r.parsed_path)
                ref_counts[cond] = len(resp['references_used'])
            lines += [f'- 各组引用外部证据条数：A={ref_counts["A"]}, B={ref_counts["B"]}, C={ref_counts["C"]}, D={ref_counts["D"]}', '']

    (OUT / '06_典型题ABCD对照.md').write_text('\n'.join(lines), encoding='utf-8')
    print('06 完成:', len(lines), '行')
    # 输出典型题清单供08使用
    pd.DataFrame([{'category': g, 'question_id': q, 'task_type': t, 'value': v}
                  for g, qlist in groups.items() for q, t, v in qlist]).to_csv(
        OUT / '_tmp_typical.csv', index=False, encoding='utf-8-sig')


if __name__ == '__main__':
    main()
