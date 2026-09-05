#!/usr/bin/env python3
"""生成"环评LLM RAG×Skill 2×2正式实验分析资料包"第一部分：01-05 xlsx。

只读冻结文件，零复算（common_3d为标记的derived变量）。
输出 -> E:\实验文件整理_按论文逻辑\09_机制分析准备_20260822\
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r'E:\实验文件整理_按论文逻辑')
SCORE_DIR = ROOT / '07_评分与对比分析' / '48题_正式评分_20260822'
STAT = ROOT / '08_2x2析因统计_48题_20260822'
OUT = ROOT / '09_机制分析准备_20260822'
OUT.mkdir(exist_ok=True)

DIMS3 = ['correctness', 'evidence_use', 'actionability']
GROUPS = ['A', 'B', 'C', 'D']
GLABEL = {'A': 'LLM', 'B': 'LLM+RAG', 'C': 'LLM+Skill', 'D': 'LLM+RAG+Skill'}
manifest_rows = []


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def msrc(output_section, path: Path, sheet, fields):
    manifest_rows.append({'output_section': output_section, 'source_file': str(path),
                          'sheet_or_table': sheet, 'fields_used': fields, 'hash': sha256(path)})


def main() -> None:
    # ============ 载入冻结数据 ============
    score = pd.read_csv(SCORE_DIR / '04_formal_scoring_results.csv',
                        keep_default_na=False, na_values=['', 'N/A', 'NA'])
    score['common_3d_score'] = score[DIMS3].sum(axis=1)
    score['common_3d_percent'] = score['common_3d_score'] / 6 * 100
    qle = pd.read_csv(STAT / '02_analysis_dataset' / 'question_level_effects.csv')
    desc = pd.read_csv(STAT / '03_descriptive' / '02_descriptive_statistics.csv')
    me = pd.read_csv(STAT / '04_factorial_analysis' / 'main_effects_common3d.csv')
    be = pd.read_csv(STAT / '05_bootstrap' / 'bootstrap_effects_common3d.csv')
    pw = pd.read_csv(STAT / '06_pairwise' / 'pairwise_holm_common3d.csv')
    het = pd.read_csv(STAT / '07_task_heterogeneity' / 'task_heterogeneity_common3d.csv')
    rob = pd.read_csv(STAT / '08_robustness' / 'robustness_three_scales.csv')
    dd = pd.read_csv(STAT / '08_robustness' / 'dimension_decomposition.csv')
    v2 = pd.read_excel(ROOT / '01_final_analysis_dataset_v2.xlsx', sheet_name='final_analysis_dataset_v2')

    # ============ 01 实验设计与样本形成 ============
    s1 = pd.DataFrame([
        {'condition': 'A', '配置': 'LLM', 'RAG': 0, 'Skill': 0, 'n_responses': 48,
         '说明': '基线：通用LLM直接审核，无外部证据注入，无程序约束'},
        {'condition': 'B', '配置': 'LLM+RAG', 'RAG': 1, 'Skill': 0, 'n_responses': 48,
         '说明': '注入冻结RAG Top-5证据（73源知识库混合检索）'},
        {'condition': 'C', '配置': 'LLM+Skill', 'RAG': 0, 'Skill': 1, 'n_responses': 48,
         '说明': '注入路由的单一主任务Skill（15个审核程序模块之一）'},
        {'condition': 'D', '配置': 'LLM+RAG+Skill', 'RAG': 1, 'Skill': 1, 'n_responses': 48,
         '说明': '同时注入RAG Top-5证据与Skill程序约束'},
    ])
    s2 = pd.DataFrame([
        {'阶段': '21题预实验闭环', '日期': '08-08~08-12', '题目数': 21, '任务类型数': 7, '完成状态': '完成',
         '主要文件': '第二阶段_21题正式评价集_冻结版_20260812.json; 第五阶段_qwen3.8-max_冻结实验_20260812; 第六阶段_正式评分_20260812',
         '变化原因': '建立评分协议与析因范式（协议模板）'},
        {'阶段': 'QA样本扩展', '日期': '08-19', '题目数': 61, '任务类型数': 14, '完成状态': '完成',
         '主要文件': '61题人工审阅记录表_剩余40题人工Gold完善版_20260819.xlsx', '变化原因': '新增40题（PL006-PL015）扩充任务类型覆盖'},
        {'阶段': 'RAG知识库扩展+Top-5冻结', '日期': '08-19~08-20', '题目数': 61, '任务类型数': 14, '完成状态': '完成',
         '主要文件': '正式实验RAG知识库_61题扩展版_20260819; 40题冻结RAG快照_20260820', '变化原因': '73源/401父块/3438子块，B/D共用同一Top-5'},
        {'阶段': 'A/B/C/D输入冻结', '日期': '08-20 21:43', '题目数': 61, '任务类型数': 14, '完成状态': '完成',
         '主要文件': '新增40题_正式输入冻结_20260820\\input_freeze_manifest.json', '变化原因': '160份prompt冻结，25项验收全PASS，Gold零泄漏'},
        {'阶段': '160实验任务执行', '日期': '08-20~08-21', '题目数': '40题×4=160', '任务类型数': '8(新增题类)', '完成状态': '初始119/160成功',
         '主要文件': '06_ABCD四组实验结果\\新增40题_qwen3.8-max_正式实验_20260820', '变化原因': '41个任务技术失败（HTTP503上游饱和/连接中断/HTTP200空响应）'},
        {'阶段': '技术失败救援', '日期': '08-21~08-22', '题目数': '41补跑+17成功', '任务类型数': '-', '完成状态': '完成',
         '主要文件': '正式实验技术失败与样本剔除报告.md; final_rerun.log', '变化原因': '三轮救援；00:33中间状态为17题剔除/N=44，02:10-02:53最后救援恢复4题→最终13题剔除'},
        {'阶段': '最终样本冻结', '日期': '08-22 12:58', '题目数': 48, '任务类型数': 14, '完成状态': '冻结',
         '主要文件': '01_final_analysis_dataset_v2.xlsx; 02_final_dataset_integrity_report.md', '变化原因': '21旧+27新=48题；13题按complete-case规则剔除；SourceStrength 5/5退出'},
        {'阶段': '192条正式评分', '日期': '08-22', '题目数': '48×4=192', '任务类型数': 14, '完成状态': '完成 192/192',
         '主要文件': '07_评分与对比分析\\48题_正式评分_20260822', '变化原因': '复用20260812评分协议；QC 15/15 PASS'},
        {'阶段': '2×2析因统计', '日期': '08-22', '题目数': 48, '任务类型数': 14, '完成状态': '完成',
         '主要文件': '08_2x2析因统计_48题_20260822', '变化原因': '主效应+bootstrap+MixedLM+任务异质性+稳健性'},
    ])

    # 13题剔除表（权威推导：中间17题清单 ∩ 不在最终48题集）
    d17 = pd.read_csv(ROOT / '06_ABCD四组实验结果' / '新增40题_qwen3.8-max_正式实验_20260820' / '技术失败剔除题清单.csv')
    final48 = set(score.question_id.unique())
    excl13 = d17[~d17.question_id.isin(final48)].copy()
    excl13['task_type'] = excl13.question_id.str.split('_').str[1]
    rescued4 = d17[d17.question_id.isin(final48)].question_id.tolist()
    s3 = excl13[['question_id', 'task_type', '失败组', '最后错误类型', 'attempt次数', '剔除原因']].rename(
        columns={'失败组': '失败group', '最后错误类型': '原始失败类型', 'attempt次数': 'attempts', '剔除原因': '剔除原因(complete-case规则)'})
    s3['最终救援结果'] = '三轮救援后仍失败'
    s3['原始失败类型'] = s3['原始失败类型'].str[:80]
    with pd.ExcelWriter(OUT / '01_实验设计与样本形成.xlsx', engine='openpyxl') as xw:
        s1.to_excel(xw, sheet_name='Sheet1_实验设计', index=False)
        s2.to_excel(xw, sheet_name='Sheet2_样本形成过程', index=False)
        s3.to_excel(xw, sheet_name='Sheet3_13道剔除题', index=False)
        ss_stats = pd.DataFrame([
            {'统计项': 'SourceStrength总数(新增40题中)', '值': 5},
            {'统计项': 'SourceStrength保留数', '值': 0},
            {'统计项': 'SourceStrength剔除数', '值': 5},
            {'统计项': '13题中失败group含D组的题数', '值': int((s3['失败group'].str.contains('D')).sum())},
            {'统计项': '中间状态(00:33)剔除17题中被救回', '值': '; '.join(rescued4)},
        ])
        ss_stats.to_excel(xw, sheet_name='Sheet4_SourceStrength统计', index=False)
    msrc('01_Sheet1/2', SCORE_DIR / '04_formal_scoring_results.csv', '-', 'condition/n(校验)')
    msrc('01_Sheet3', ROOT / '06_ABCD四组实验结果' / '新增40题_qwen3.8-max_正式实验_20260820' / '技术失败剔除题清单.csv',
         '全表', 'question_id/失败组/最后错误类型/attempt次数/剔除原因')
    msrc('01_Sheet2', ROOT / '02_final_dataset_integrity_report.md', '全文', '阶段数字与剔除规则')

    # ============ 02 正式评分结果汇总 ============
    keep_cols = ['question_id', 'project_id', 'task_type', 'condition', 'condition_label', 'RAG', 'Skill',
                 'correctness', 'evidence_use', 'actionability', 'regulatory_basis', 'skill_workflow',
                 'common_3d_score', 'common_3d_percent', 'normalized_100', 'applicable_max', 'question_source']
    s192 = score[keep_cols].copy()
    desc6 = desc[desc.outcome.isin(DIMS3 + ['common_3d_score', 'common_3d_percent', 'normalized_100'])].copy()
    na_rows = []
    for metric in ['regulatory_basis', 'skill_workflow']:
        for g in GROUPS:
            sub = score.loc[score.condition == g, metric]
            valid = sub.dropna()
            na_rows.append({
                'metric': metric, 'group': g, 'n_total': 48, 'n_valid': len(valid),
                'n_NA': int(sub.isna().sum()),
                'N/A性质': ('设计性N/A（A组无RAG无法规依据可评）' if g == 'A' and metric == 'regulatory_basis'
                           else '设计性N/A（C组无RAG，judge裁量N/A 46/48）' if g == 'C' and metric == 'regulatory_basis'
                           else '设计性N/A（A/B组无Skill可评）' if g in 'AB' and metric == 'skill_workflow'
                           else '设计性N/A（无Skill可评）' if metric == 'skill_workflow'
                           else 'judge裁量N/A（该回答未给出法规依据结论）'),
                'mean_有效内': round(valid.mean(), 3) if len(valid) else np.nan,
                'SD_有效内': round(valid.std(ddof=1), 3) if len(valid) > 1 else np.nan})
    with pd.ExcelWriter(OUT / '02_正式评分结果汇总.xlsx', engine='openpyxl') as xw:
        s192.to_excel(xw, sheet_name='Sheet1_192条正式评分', index=False)
        desc6.to_excel(xw, sheet_name='Sheet2_ABCD描述统计', index=False)
        pd.DataFrame(na_rows).to_excel(xw, sheet_name='Sheet3_NA结构', index=False)
    msrc('02_Sheet1', SCORE_DIR / '04_formal_scoring_results.csv', '全表192行',
         'question_id/task_type/condition/五维评分/normalized_100/applicable_max')
    msrc('02_Sheet2', STAT / '03_descriptive' / '02_descriptive_statistics.csv', '全表', 'N/mean/SD/median/IQR/CI')

    # ============ 03 2x2析因结果汇总 ============
    # Sheet1: 5个outcome × 3效应
    me_rows = []
    keymap = {'rag_main': 'RAG main', 'skill_main': 'Skill main', 'interaction': 'Interaction'}
    for outcome in ['common_3d_score', 'common_3d_percent', 'normalized_100']:
        sub = rob[rob.outcome.str.startswith(outcome)]
        for key, label in keymap.items():
            r = sub[sub.effect == key].iloc[0]
            me_rows.append({'Outcome': outcome, 'Effect': label, 'estimate': r.estimate,
                            't_CI95_low': r.CI95_low, 't_CI95_high': r.CI95_high,
                            'boot_CI95_low': r.boot_CI95_low, 'boot_CI95_high': r.boot_CI95_high,
                            'p_value': r.p_value, 'cohen_dz': r.cohen_dz,
                            'source': 'robustness_three_scales.csv'})
    dim_label = {'correctness (0-2)': 'correctness', 'evidence_use (0-2)': 'evidence_use',
                 'actionability (0-2)': 'actionability'}
    for _, r in dd.iterrows():
        if r.effect not in keymap:
            continue
        me_rows.append({'Outcome': dim_label[r.outcome], 'Effect': keymap[r.effect], 'estimate': r.estimate,
                        't_CI95_low': r.CI95_low, 't_CI95_high': r.CI95_high,
                        'boot_CI95_low': r.boot_CI95_low, 'boot_CI95_high': r.boot_CI95_high,
                        'p_value': r.p_value, 'cohen_dz': r.cohen_dz,
                        'source': 'dimension_decomposition.csv'})
    me_df = pd.DataFrame(me_rows)

    pw_df = pw[['effect', 'estimate', 'CI95_low', 'CI95_high', 'p_value', 'p_holm', 'cohen_dz', 'reject_holm_0.05']].rename(
        columns={'effect': 'contrast', 'CI95_low': 'CI95_low(t)', 'CI95_high': 'CI95_high(t)',
                 'p_value': 'p_raw', 'p_holm': 'p_Holm', 'cohen_dz': 'cohen_dz'})

    # Sheet3: 逐题interaction分布
    cols_q = ['question_id', 'task_type', 'question_source']
    wide = score.pivot_table(index='question_id', columns='condition', values='common_3d_score')
    wide.columns = [f'{c}' for c in wide.columns]
    qw = qle.set_index('question_id')[['c3_B_minus_A', 'c3_C_minus_A', 'c3_D_minus_B', 'c3_D_minus_C',
                                       'c3_interaction', 'c3_rag_main', 'c3_skill_main']].rename(
        columns={'c3_B_minus_A': 'B-A', 'c3_C_minus_A': 'C-A', 'c3_D_minus_B': 'D-B',
                 'c3_D_minus_C': 'D-C', 'c3_interaction': 'Interaction(D-B-C+A)',
                 'c3_rag_main': 'RAG_main', 'c3_skill_main': 'Skill_main'})
    qsheet = wide.join(qw).join(qle.set_index('question_id')[['task_type', 'question_source']]).reset_index()
    qsheet = qsheet.sort_values('Interaction(D-B-C+A)', ascending=False)
    with pd.ExcelWriter(OUT / '03_2x2析因结果汇总.xlsx', engine='openpyxl') as xw:
        me_df.to_excel(xw, sheet_name='Sheet1_主效应(5个outcome)', index=False)
        pw_df.to_excel(xw, sheet_name='Sheet2_简单效应_Holm', index=False)
        qsheet.to_excel(xw, sheet_name='Sheet3_逐题Interaction分布', index=False)
    msrc('03_Sheet1', STAT / '08_robustness' / 'robustness_three_scales.csv', '全表', 'estimate/CI/p/dz(3口径)')
    msrc('03_Sheet1', STAT / '08_robustness' / 'dimension_decomposition.csv', '全表', '三维效应')
    msrc('03_Sheet2', STAT / '06_pairwise' / 'pairwise_holm_common3d.csv', '全表', '5 contrasts+Holm')
    msrc('03_Sheet3', STAT / '02_analysis_dataset' / 'question_level_effects.csv', '全表', 'c3_*逐题效应')
    msrc('03_Sheet3', SCORE_DIR / '04_formal_scoring_results.csv', '全表', 'common_3d(derived)')

    # ============ 04 三维能力分解 ============
    dd_rows = []
    for dim in DIMS3:
        for _, r in dd[dd.outcome == f'{dim} (0-2)'].iterrows():
            if r.effect in keymap:
                dd_rows.append({'dimension': dim, 'effect': keymap[r.effect], 'estimate': r.estimate,
                                'boot_CI95_low': r.boot_CI95_low, 'boot_CI95_high': r.boot_CI95_high,
                                'p_value': r.p_value, 'cohen_dz': r.cohen_dz})
    dd_out = pd.DataFrame(dd_rows)
    # 天花板统计
    ceil_rows = []
    for dim in DIMS3 + ['common_3d_score']:
        for g in GROUPS:
            vals = score.loc[score.condition == g, dim] if dim in score.columns else score.loc[score.condition == g].eval('correctness+evidence_use+actionability')
            mx = 2 if dim in DIMS3 else 6
            ceil_rows.append({'dimension': dim, 'group': g, '满分比例(=max)': round((vals == mx).mean() * 100, 1),
                              '零方差(全组同分)': bool(vals.std(ddof=1) == 0),
                              'mean': round(vals.mean(), 3), 'SD': round(vals.std(ddof=1), 3)})
    ceil_df = pd.DataFrame(ceil_rows)
    with pd.ExcelWriter(OUT / '04_三维能力分解.xlsx', engine='openpyxl') as xw:
        dd_out.to_excel(xw, sheet_name='Sheet1_三维效应', index=False)
        desc[desc.outcome.isin(DIMS3)].to_excel(xw, sheet_name='Sheet2_ABCD各维描述', index=False)
        ceil_df.to_excel(xw, sheet_name='Sheet3_天花板与方差统计', index=False)
        pd.DataFrame([
            {'维度': 'evidence_use', '事实': '四组满分率均为93.8%(45/48)；B/D组均值1.979(仅1题非满分)；A/C组均值1.958(2题非满分)；该维度在48题中仅4题未满分，方差接近0'},
            {'维度': 'correctness', '事实': 'A组满分率58.3%；C组满分率37.5%；C组0分题数多于A组(3 vs 1)'},
            {'维度': 'actionability', '事实': 'A组满分率93.8%；C组满分率77.1%；D组满分率91.7%'},
        ]).to_excel(xw, sheet_name='Sheet4_关键事实(只陈述)', index=False)
    msrc('04_Sheet1', STAT / '08_robustness' / 'dimension_decomposition.csv', '全表', '三维×三效应')
    msrc('04_Sheet2', STAT / '03_descriptive' / '02_descriptive_statistics.csv', '三维行', '描述统计')

    # ============ 05 任务异质性 ============
    het['interaction_rank'] = het.interaction.rank(ascending=False, method='min').astype(int)
    het_sorted = het.sort_values('interaction_rank')
    # 简单效应按task（从qle计算类内均值——与het同算法）
    simple = qle.groupby('task_type').agg(
        n_questions=('question_id', 'count'),
        B_minus_A=('c3_B_minus_A', 'mean'), C_minus_A=('c3_C_minus_A', 'mean'),
        D_minus_B=('c3_D_minus_B', 'mean'), D_minus_C=('c3_D_minus_C', 'mean')).reset_index()
    het_final = het_sorted.merge(simple, on='task_type', suffixes=('', '_simple'))
    het_final = het_final[['task_type', 'n_questions', 'A_mean_pct', 'B_mean_pct', 'C_mean_pct', 'D_mean_pct',
                           'rag_main', 'rag_main_boot_CI95', 'skill_main', 'skill_main_boot_CI95',
                           'interaction', 'interaction_boot_CI95',
                           'B_minus_A', 'C_minus_A', 'D_minus_B', 'D_minus_C', 'interaction_rank']]
    het_final.to_excel(OUT / '05_任务异质性.xlsx', sheet_name='14类task_type', index=False, engine='openpyxl')
    msrc('05', STAT / '07_task_heterogeneity' / 'task_heterogeneity_common3d.csv', '全表',
         'task_type/n/ABCD均值/三效应+bootstrapCI')
    msrc('05', STAT / '02_analysis_dataset' / 'question_level_effects.csv', '全表', '简单效应类内均值')

    # 保存13题剔除表与逐题interaction的中间产物供后续md使用
    excl13.to_csv(OUT / '_tmp_excl13.csv', index=False, encoding='utf-8-sig')
    qsheet.to_csv(OUT / '_tmp_qsheet.csv', index=False, encoding='utf-8-sig')
    pd.DataFrame(manifest_rows).to_csv(OUT / 'source_manifest.csv', index=False, encoding='utf-8-sig')
    print('01-05 xlsx 完成')
    print('01:', len(s1), len(s2), len(s3), '| 02:', len(s192), len(desc6), len(na_rows))
    print('03:', len(me_df), len(pw_df), len(qsheet), '| 04:', len(dd_out), '| 05:', len(het_final))
    print('manifest:', len(manifest_rows))


if __name__ == '__main__':
    main()
