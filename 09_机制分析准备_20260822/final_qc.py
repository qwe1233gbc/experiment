#!/usr/bin/env python3
"""最终QC + manifest补全 + 临时文件清理。"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

ROOT = Path(r'E:\实验文件整理_按论文逻辑')
OUT = ROOT / '09_机制分析准备_20260822'
SCORE_DIR = ROOT / '07_评分与对比分析' / '48题_正式评分_20260822'
STAT = ROOT / '08_2x2析因统计_48题_20260822'
DIMS3 = ['correctness', 'evidence_use', 'actionability']


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


score = pd.read_csv(SCORE_DIR / '04_formal_scoring_results.csv', keep_default_na=False, na_values=['', 'N/A', 'NA'])
score['c3'] = score[DIMS3].sum(axis=1)

checks = []
def chk(name, ok, detail=''):
    checks.append((name, 'PASS' if ok else 'FAIL', detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")

# QC清单
chk('N=48', score.question_id.nunique() == 48, f"unique={score.question_id.nunique()}")
chk('n=192', len(score) == 192)
vc = score.condition.value_counts()
chk('A/B/C/D各48', all(vc.get(g) == 48 for g in 'ABCD'))
chk('SourceStrength=0', (score.task_type == 'SourceStrength').sum() == 0)
excl13 = ['PL006_ActivatedCarbon_Q01', 'PL006_SourceStrength_Q01', 'PL007_SourceStrength_Q01',
          'PL008_SourceStrength_Q01', 'PL009_Construction_Q01', 'PL010_SourceStrength_Q01',
          'PL011_ActivatedCarbon_Q01', 'PL012_HazardousWaste_Q01', 'PL012_VOCSTotal_Q01',
          'PL013_SourceStrength_Q01', 'PL014_DesignAirflow_Q01', 'PL014_VOCSTotal_Q01',
          'PL015_HazardousWaste_Q01']
chk('13题未进入', not any(q in set(score.question_id) for q in excl13))
chk('192评分来自正式评分目录', True, '输入=04_formal_scoring_results.csv')
chk('task_type冻结14类', score.task_type.nunique() == 14, f"{score.task_type.nunique()}类")
chk('N/A未填0', score.regulatory_basis.isna().sum() == 97 and score.skill_workflow.isna().sum() == 96,
    f"reg_na={score.regulatory_basis.isna().sum()}, skill_na={score.skill_workflow.isna().sum()}")

# 输出文件完整性
expected = ['01_实验设计与样本形成.xlsx', '02_正式评分结果汇总.xlsx', '03_2x2析因结果汇总.xlsx',
            '04_三维能力分解.xlsx', '05_任务异质性.xlsx', '06_典型题ABCD对照.md',
            '07_实验过程与方法边界.md', '08_GPT深度分析输入包.md', 'source_manifest.csv']
for f in expected:
    chk(f'输出存在:{f}', (OUT / f).exists())

# 08中的数字抽查（与冻结统计一致）
t8 = (OUT / '08_GPT深度分析输入包.md').read_text(encoding='utf-8')
chk('08含Interaction=+0.396', '0.396' in t8)
chk('08含Skill main=-0.219', '-0.219' in t8 or '-0.219' in t8.replace('−', '-'))
chk('08来源标记数量', t8.count('【来源：') >= 40, f"共{t8.count('【来源：')}处")

# 06典型题：验证10题对照包含四组评分
t6 = (OUT / '06_典型题ABCD对照.md').read_text(encoding='utf-8')
chk('06含20个题块(4类×5题)', t6.count('### ') == 20, f"{t6.count('### ')}个")

# manifest补全（06/07/08的来源）
mani = pd.read_csv(OUT / 'source_manifest.csv')
extra = [
    {'output_section': '06_典型题ABCD对照', 'source_file': str(ROOT / '01_final_analysis_dataset_v2.xlsx'),
     'sheet_or_table': 'final_analysis_dataset_v2', 'fields_used': 'gold_answer_path/parsed_path', 'hash': sha256(ROOT / '01_final_analysis_dataset_v2.xlsx')},
    {'output_section': '06_典型题ABCD对照', 'source_file': str(ROOT / '05_QA测试集与样本' / '第二阶段_21题正式评价集_冻结版_20260812.json'),
     'sheet_or_table': 'records', 'fields_used': 'reference_answer(旧21题Gold)', 'hash': sha256(ROOT / '05_QA测试集与样本' / '第二阶段_21题正式评价集_冻结版_20260812.json')},
    {'output_section': '06_典型题ABCD对照', 'source_file': str(ROOT / '05_QA测试集与样本' / '40题Gold最终人工核验_20260820' / '40题Gold证据索引_20260820.json'),
     'sheet_or_table': 'list', 'fields_used': 'gold_full/verdict(新27题Gold)', 'hash': sha256(ROOT / '05_QA测试集与样本' / '40题Gold最终人工核验_20260820' / '40题Gold证据索引_20260820.json')},
    {'output_section': '06_典型题ABCD对照', 'source_file': str(SCORE_DIR / '04_formal_scoring_results.csv'),
     'sheet_or_table': '全表', 'fields_used': '三维评分/rationale', 'hash': sha256(SCORE_DIR / '04_formal_scoring_results.csv')},
    {'output_section': '07/08_方法边界与GPT包', 'source_file': str(ROOT / '02_final_dataset_integrity_report.md'),
     'sheet_or_table': '全文', 'fields_used': '样本构成/剔除规则/参数冻结', 'hash': sha256(ROOT / '02_final_dataset_integrity_report.md')},
    {'output_section': '08_GPT包_信度数据', 'source_file': str(ROOT / '09_评分信度与敏感性检验_20260822' / 'test_retest_dimension_stats.csv'),
     'sheet_or_table': '全表', 'fields_used': 'ICC/一致率', 'hash': sha256(ROOT / '09_评分信度与敏感性检验_20260822' / 'test_retest_dimension_stats.csv')},
    {'output_section': '08_GPT包_敏感性数据', 'source_file': str(ROOT / '09_评分信度与敏感性检验_20260822' / 'leave_one_category_out_sensitivity.csv'),
     'sheet_or_table': '全表', 'fields_used': 'leave-one-out结果', 'hash': sha256(ROOT / '09_评分信度与敏感性检验_20260822' / 'leave_one_category_out_sensitivity.csv')},
    {'output_section': '08_GPT包_MixedLM', 'source_file': str(STAT / '04_factorial_analysis' / 'mixedlm_common3d.csv'),
     'sheet_or_table': '全表', 'fields_used': 'MixedLM p值', 'hash': sha256(STAT / '04_factorial_analysis' / 'mixedlm_common3d.csv')},
]
mani = pd.concat([mani, pd.DataFrame(extra)], ignore_index=True)
mani.to_csv(OUT / 'source_manifest.csv', index=False, encoding='utf-8-sig')

# 清理临时文件
for f in ['_tmp_excl13.csv', '_tmp_qsheet.csv', '_tmp_typical.csv']:
    p = OUT / f
    if p.exists():
        p.unlink()

n_fail = sum(1 for _, s, _ in checks if s == 'FAIL')
print(f"\nQC: {len(checks) - n_fail}/{len(checks)} PASS")
print('manifest总行数:', len(mani))

# 最终文件清单
print('\n=== 输出目录清单 ===')
for f in sorted(OUT.iterdir()):
    print(f"  {f.name}  ({f.stat().st_size // 1024}KB)")
