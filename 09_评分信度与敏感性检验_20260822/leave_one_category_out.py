#!/usr/bin/env python3
"""B2: Leave-one-task-category-out sensitivity for the 48-question 2x2 analysis.

For each of the 14 frozen task_type categories, recompute the three factorial
effects (common_3d_score) on the remaining questions. Purpose: test whether the
headline interaction (+0.396, p=0.0016) is driven by any single category.

Input : 08_2x2析因统计_48题_20260822\02_analysis_dataset\question_level_effects.csv (frozen)
Output: 09_评分信度与敏感性检验_20260822\leave_one_category_out_sensitivity.csv
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from scipy import stats

ROOT = Path(r'E:\实验文件整理_按论文逻辑')
QLE = ROOT / '08_2x2析因统计_48题_20260822' / '02_analysis_dataset' / 'question_level_effects.csv'
OUT = ROOT / '09_评分信度与敏感性检验_20260822' / 'leave_one_category_out_sensitivity.csv'


def effects(df: pd.DataFrame) -> dict:
    out = {}
    for eff in ('c3_rag_main', 'c3_skill_main', 'c3_interaction'):
        s = df[eff]
        t, p = stats.ttest_1samp(s, 0)
        out[eff] = s.mean()
        out[eff.replace('c3_', '') + '_t'] = float(t)
        out[eff.replace('c3_', '') + '_p'] = float(p)
    return out


def main() -> None:
    df = pd.read_csv(QLE)
    base = effects(df)
    rows = [{'excluded_category': '(none / full 48)', 'n_excluded': 0, 'n_kept': 48, **base}]
    for cat in sorted(df.task_type.unique()):
        sub = df[df.task_type != cat]
        rows.append({'excluded_category': cat, 'n_excluded': int((df.task_type == cat).sum()),
                     'n_kept': len(sub), **effects(sub)})
    res = pd.DataFrame(rows)
    for c in res.columns:
        if res[c].dtype.kind == 'f':
            res[c] = res[c].round(4)
    res.to_csv(OUT, index=False, encoding='utf-8-sig')
    pd.set_option('display.width', 220)
    print(res.to_string(index=False))
    # verdict
    full = res.iloc[0]
    inter = res[res.excluded_category != '(none / full 48)']
    stable = ((inter.c3_interaction > 0).all(), (inter.interaction_p < 0.05).sum(), len(inter))
    print(f"\ninteraction>0 in all {stable[2]} leave-one-out runs: {stable[0]}; "
          f"p<0.05 in {stable[1]}/{stable[2]} runs (full-sample p={full.interaction_p})")


if __name__ == '__main__':
    main()
