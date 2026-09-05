#!/usr/bin/env python3
"""B1: Judge test-retest reliability analysis.

Same judge (qwen3.8-max, temperature=0, max_tokens=1800, enable_thinking=False),
same protocol (verbatim reuse), same blind mapping (A->R1..D->R4), same 84 frozen
responses (old 21 questions x 4 conditions, hash-verified) scored twice:
  Round 1 (R1): 20260812 第六阶段正式评分
  Round 2 (R2): 20260822 48题正式评分 (old21 subset)

Statistics per dimension: exact agreement, within-1 agreement, quadratic weighted
kappa, ICC(2,1), mean difference (R2-R1) with paired t / Wilcoxon.
common_3d_score: agreement, ICC, Pearson r, Bland-Altman LoA.
N/A dimensions: N/A-consistency + numeric-only agreement (never imputed).
Old21-subset factorial effects recomputed in both rounds (conclusion stability).

Outputs -> E:\实验文件整理_按论文逻辑\09_评分信度与敏感性检验_20260822\
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(r'E:\实验文件整理_按论文逻辑')
OUT = ROOT / '09_评分信度与敏感性检验_20260822'
OUT.mkdir(exist_ok=True)

F1 = ROOT / '07_评分与对比分析' / '第六阶段_正式评分_20260812' / '每题得分明细.csv'
F2 = ROOT / '07_评分与对比分析' / '48题_正式评分_20260822' / '04_formal_scoring_results.csv'

DIMS3 = ['correctness', 'evidence_use', 'actionability']
DIMS_NA = ['regulatory_basis', 'skill_workflow']
CONDITIONS = ['A', 'B', 'C', 'D']


def qwk(y1: np.ndarray, y2: np.ndarray) -> float:
    """Quadratic weighted kappa (manual implementation, categories = sorted union)."""
    cats = sorted(set(y1) | set(y2))
    k = len(cats)
    idx = {c: i for i, c in enumerate(cats)}
    o = np.zeros((k, k))
    for a, b in zip(y1, y2):
        o[idx[a], idx[b]] += 1
    n = o.sum()
    w = np.array([[(i - j) ** 2 / (k - 1) ** 2 if k > 1 else 0.0
                   for j in range(k)] for i in range(k)])
    e = np.outer(o.sum(axis=1), o.sum(axis=0)) / n
    denom = (w * e).sum()
    return 1.0 - (w * o).sum() / denom if denom > 0 else np.nan


def icc_2_1(x1: np.ndarray, x2: np.ndarray) -> tuple[float, float, float, float]:
    """ICC(2,1): two-way random, absolute agreement, single measure. Returns (icc, F, df1, df2)."""
    m = np.column_stack([x1, x2])
    n, k = m.shape
    grand = m.mean()
    row_means = m.mean(axis=1)
    col_means = m.mean(axis=0)
    ssr = k * ((row_means - grand) ** 2).sum()
    ssc = n * ((col_means - grand) ** 2).sum()
    sst = ((m - grand) ** 2).sum()
    sse = sst - ssr - ssc
    msr = ssr / (n - 1)
    msc = ssc / (k - 1)
    mse = sse / ((n - 1) * (k - 1))
    denom = msr + (k - 1) * mse + k * (msc - mse) / n
    icc = (msr - mse) / denom if denom != 0 else np.nan
    f = msr / mse if mse > 0 else np.nan
    return icc, f, n - 1, (n - 1) * (k - 1)


def main() -> None:
    d1 = pd.read_csv(F1)                       # round 1 (20260812)
    d1 = d1.rename(columns={'group': 'condition'})
    src = pd.read_csv(F2, keep_default_na=False, na_values=['', 'N/A', 'NA'])
    d2 = src[src.question_source == 'old21_phase5_frozen'].copy()  # round 2 (20260822)
    mg = d1.merge(d2, on=['question_id', 'condition'], suffixes=('_r1', '_r2'))
    assert len(mg) == 84, f'配对失败: {len(mg)}'

    rows = []
    # ---- three common dimensions + common_3d ----
    mg['c3_r1'] = mg[[f'{d}_r1' for d in DIMS3]].sum(axis=1)
    mg['c3_r2'] = mg[[f'{d}_r2' for d in DIMS3]].sum(axis=1)

    for dim in DIMS3 + ['c3']:
        x1 = mg[f'{dim}_r1'].to_numpy(float)
        x2 = mg[f'{dim}_r2'].to_numpy(float)
        diff = x2 - x1
        exact = (x1 == x2).mean()
        within1 = (np.abs(diff) <= 1).mean()
        kap = qwk(x1.astype(int), x2.astype(int))
        icc, f, df1, df2 = icc_2_1(x1, x2)
        r_p = stats.pearsonr(x1, x2)
        r_s = stats.spearmanr(x1, x2)
        t_p = stats.ttest_rel(x2, x1).pvalue
        w_p = stats.wilcoxon(x2, x1, zero_method='wilcox').pvalue if np.any(diff != 0) else 1.0
        sd_diff = diff.std(ddof=1)
        rows.append({
            'dimension': 'common_3d_score' if dim == 'c3' else dim,
            'n_pairs': len(x1),
            'exact_agreement': round(exact, 4),
            'within_1_agreement': round(within1, 4),
            'quadratic_weighted_kappa': round(kap, 4),
            'ICC_2_1': round(icc, 4), 'ICC_F': round(f, 1),
            'pearson_r': round(r_p.statistic, 4), 'spearman_rho': round(r_s.statistic, 4),
            'mean_r1': round(x1.mean(), 3), 'mean_r2': round(x2.mean(), 3),
            'mean_diff_r2_minus_r1': round(diff.mean(), 4),
            'sd_diff': round(sd_diff, 4),
            'paired_t_p': round(t_p, 4), 'wilcoxon_p': round(w_p, 4),
        })

    # ---- N/A dimensions ----
    for dim in DIMS_NA:
        v1 = mg[f'{dim}_r1']
        v2 = mg[f'{dim}_r2']
        na1, na2 = v1.isna(), v2.isna()
        both_na = (na1 & na2).sum()
        na_flip = (na1 != na2).sum()
        both_num = (~na1) & (~na2)
        x1 = v1[both_num].to_numpy(float)
        x2 = v2[both_num].to_numpy(float)
        rec = {
            'dimension': dim, 'n_pairs': len(v1),
            'both_NA': int(both_na), 'NA_status_flips': int(na_flip),
            'n_both_numeric': int(both_num.sum())}
        if len(x1) >= 3:
            diff = x2 - x1
            rec.update({
                'exact_agreement': round((x1 == x2).mean(), 4),
                'within_1_agreement': round((np.abs(diff) <= 1).mean(), 4),
                'quadratic_weighted_kappa': round(qwk(x1.astype(int), x2.astype(int)), 4),
                'ICC_2_1': round(icc_2_1(x1, x2)[0], 4),
                'mean_diff_r2_minus_r1': round(diff.mean(), 4)})
        rows.append(rec)

    detail = pd.DataFrame(rows)
    detail.to_csv(OUT / 'test_retest_dimension_stats.csv', index=False, encoding='utf-8-sig')

    # ---- disagreement inventory (common 3 dims) ----
    inv_rows = []
    for _, r in mg.iterrows():
        dd = {d: r[f'{d}_r2'] - r[f'{d}_r1'] for d in DIMS3}
        if any(abs(v) >= 1 for v in dd.values()):
            inv_rows.append({'question_id': r.question_id, 'condition': r.condition,
                             **{f'{d}_r1': r[f'{d}_r1'] for d in DIMS3},
                             **{f'{d}_r2': r[f'{d}_r2'] for d in DIMS3},
                             'c3_r1': r.c3_r1, 'c3_r2': r.c3_r2,
                             'rationale_r2': str(r.rationale_r2)[:120] if 'rationale_r2' in r else ''})
    inv = pd.DataFrame(inv_rows)
    inv.to_csv(OUT / 'disagreement_inventory.csv', index=False, encoding='utf-8-sig')

    # ---- old21-subset factorial effects in both rounds ----
    def factorial(df, col):
        w = df.pivot(index='question_id', columns='condition', values=col)
        A, B, C, D = (w[g] for g in CONDITIONS)
        return {'rag_main': ((B - A) + (D - C)) / 2,
                'skill_main': ((C - A) + (D - B)) / 2,
                'interaction': D - C - B + A}

    eff_rows = []
    for name, dfr, col in [('R1_20260812', d1, 'c3_r1'), ('R2_20260822', mg, 'c3_r2')]:
        base = d1 if dfr is d1 else mg
        val_col = col if dfr is not d1 else None
        if dfr is d1:
            d1['c3_r1'] = d1[DIMS3].sum(axis=1)
            fx = factorial(d1, 'c3_r1')
        else:
            fx = factorial(mg, 'c3_r2')
        for k, series in fx.items():
            t, p = stats.ttest_1samp(series, 0)
            eff_rows.append({'round': name, 'effect': k, 'n': len(series),
                             'estimate': round(series.mean(), 4),
                             't': round(float(t), 3), 'p': round(float(p), 4)})
    eff = pd.DataFrame(eff_rows)
    eff.to_csv(OUT / 'old21_subset_factorial_both_rounds.csv', index=False, encoding='utf-8-sig')

    # ---- Bland-Altman for common_3d ----
    x1, x2 = mg.c3_r1.to_numpy(float), mg.c3_r2.to_numpy(float)
    diff = x2 - x1
    mean_d, sd_d = diff.mean(), diff.std(ddof=1)
    ba = {'mean_diff': round(mean_d, 4), 'sd_diff': round(sd_d, 4),
          'LoA_low': round(mean_d - 1.96 * sd_d, 4),
          'LoA_high': round(mean_d + 1.96 * sd_d, 4)}

    pd.set_option('display.width', 250)
    print('=== Test-retest dimension stats ===')
    print(detail.to_string(index=False))
    print(f'\n=== Bland-Altman (common_3d_score) === {ba}')
    print(f'\n=== Disagreements (any common dim |diff|>=1): {len(inv)}/84 rows ===')
    if len(inv):
        print(inv[['question_id', 'condition', 'correctness_r1', 'correctness_r2',
                   'evidence_use_r1', 'evidence_use_r2', 'actionability_r1',
                   'actionability_r2', 'c3_r1', 'c3_r2']].to_string(index=False))
    print('\n=== old21-subset factorial effects, both rounds ===')
    print(eff.to_string(index=False))

    # save merged data for audit
    mg.to_csv(OUT / 'merged_two_round_scores_old21.csv', index=False, encoding='utf-8-sig')
    print(f'\noutputs -> {OUT}')


if __name__ == '__main__':
    main()
