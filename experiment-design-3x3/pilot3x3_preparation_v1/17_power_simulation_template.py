"""
Power Simulation Template
基于混合效应逻辑回归的效力模拟模板
Pilot 实验完成后，用 Pilot 数据估计参数后运行此脚本

用法：
1. 从 Pilot 数据估计 baseline, OR, ICC, variance 参数
2. 修改下方 PARAMETERS 部分
3. 运行脚本
"""

import numpy as np
from scipy.special import expit, logit

# ============================================================
# PARAMETERS（Pilot 后填充）
# ============================================================

# 基线正确率（K1 + A1）
BASELINE_ACC = 0.45  # 待 Pilot 估计

# 知识效应 OR（K3 vs K1，总体）
OR_KNOWLEDGE = 3.0  # 待 Pilot 估计

# 模型效应 OR（A3 vs A1，K1 条件下）
OR_MODEL = 3.0  # 待 Pilot 估计

# Model × Knowledge 交互 OR
# 即：强模型的知识效应是弱模型的多少倍
# <1 = 递减（强模型知识效应更小），1 = 无交互，>1 = 递增
OR_INTERACTION = 0.5  # 待 Pilot 估计，假设递减

# 题目随机效应 SD（logit 尺度）
SD_QUESTION = 1.0  # 待 Pilot 估计

# 项目随机效应 SD（logit 尺度）
SD_PROJECT = 0.3  # 待 Pilot 估计

# 残差 SD（二元数据中固定为 π/sqrt(3) ≈ 1.81）
SD_RESIDUAL = np.pi / np.sqrt(3)

# EP 类别分布（4类均衡）
EP_DISTRIBUTION = {"E0P0": 0.25, "E0P1": 0.25, "E1P0": 0.25, "E1P1": 0.25}

# E 维度的知识效应调节系数（E1 比 E0 的 OR 倍数）
OR_KNOWLEDGE_E1_VS_E0 = 2.0  # E1 类知识效应更大

# P 维度的知识效应调节系数（P1 比 P0 的 OR 倍数）
OR_KNOWLEDGE_P1_VS_P0 = 0.7  # P1 类知识效应可能较小

# ============================================================
# SIMULATION SETTINGS
# ============================================================

N_SIM = 500  # 模拟次数
ALPHA = 0.05  # 显著性水平

# 待检验的样本量
N_QUESTIONS_LIST = [20, 40, 60, 80]


def simulate_one_dataset(n_questions, n_models=3, n_knowledge=3):
    """
    模拟一个数据集
    返回：X (固定效应设计矩阵), y (正确率), question_id, project_id
    """
    n_obs = n_questions * n_models * n_knowledge

    # 题目随机效应
    question_effects = np.random.normal(0, SD_QUESTION, n_questions)

    # 项目随机效应（假设每题来自不同项目，项目效应为题效应的一部分）
    project_effects = np.random.normal(0, SD_PROJECT, n_questions)

    # 构造数据
    y = np.zeros(n_obs)
    question_ids = np.zeros(n_obs, dtype=int)
    model_ids = np.zeros(n_obs, dtype=int)
    knowledge_ids = np.zeros(n_obs, dtype=int)
    e_labels = np.zeros(n_obs, dtype=int)
    p_labels = np.zeros(n_obs, dtype=int)

    idx = 0
    for q in range(n_questions):
        # 随机分配 EP 类别
        ep = np.random.choice(list(EP_DISTRIBUTION.keys()),
                              p=list(EP_DISTRIBUTION.values()))
        e = 1 if ep.startswith("E1") else 0
        p = 1 if ep.endswith("P1") else 0

        for m in range(n_models):
            for k in range(n_knowledge):
                # 基线 logit
                logit_p = logit(BASELINE_ACC)

                # 模型主效应（m=0 为 A1，m=2 为 A3）
                if m > 0:
                    # 假设近似线性梯度
                    model_effect = (m / 2.0) * np.log(OR_MODEL)
                    logit_p += model_effect

                # 知识主效应（k=0 为 K1）
                if k > 0:
                    # K2 效应约为 K3 的一半（假设）
                    k_effect = (k / 2.0) * np.log(OR_KNOWLEDGE)

                    # E 调节
                    if e == 1:
                        k_effect *= np.log(OR_KNOWLEDGE_E1_VS_E0) / np.log(OR_KNOWLEDGE) + 0.5
                        # 简化：E1 知识效应乘以 OR_KNOWLEDGE_E1_VS_E0
                        k_effect = np.log(OR_KNOWLEDGE) * (k / 2.0) * OR_KNOWLEDGE_E1_VS_E0

                    # P 调节
                    if p == 1:
                        k_effect *= OR_KNOWLEDGE_P1_VS_P0

                    logit_p += k_effect

                # Model × Knowledge 交互
                if m > 0 and k > 0:
                    # 交互效应：随模型能力递增而递减
                    interaction_strength = (m / 2.0) * (k / 2.0)
                    # OR_INTERACTION < 1 表示递减
                    logit_p += interaction_strength * np.log(OR_INTERACTION)

                # 随机效应
                logit_p += question_effects[q]
                logit_p += project_effects[q]

                # 生成二元结果
                prob = expit(logit_p)
                y[idx] = np.random.binomial(1, prob)

                question_ids[idx] = q
                model_ids[idx] = m
                knowledge_ids[idx] = k
                e_labels[idx] = e
                p_labels[idx] = p
                idx += 1

    return {
        "y": y,
        "question_id": question_ids,
        "model": model_ids,
        "knowledge": knowledge_ids,
        "E": e_labels,
        "P": p_labels,
    }


def test_interaction_significant(data):
    """
    检验 Model × Knowledge 交互是否显著
    简化版：用近似方法（实际应用中应拟合 GLMM）
    """
    # 简化：计算各组正确率，看交互效应的方向和大小
    # 实际模拟中应使用 lme4/glmmTMB 拟合 GLMM 并做 LRT
    # 这里用一个近似的交互效应检测

    # 计算各组正确率
    groups = {}
    for i in range(len(data["y"])):
        key = (data["model"][i], data["knowledge"][i])
        if key not in groups:
            groups[key] = []
        groups[key].append(data["y"][i])

    acc = {k: np.mean(v) for k, v in groups.items()}

    # 计算 K3-K1 差值在各模型上
    diff_a1 = acc.get((2, 2), 0) - acc.get((2, 0), 0)  # 应该是 m=0 vs m=2
    # 简化版：直接计算交互项的量级
    # 实际应用中用 GLMM

    # 这里返回一个占位符（始终 True），
    # 真实模拟需要拟合 GLMM 并做似然比检验
    return True  # 占位符，实际使用时替换


def run_power_analysis():
    """运行效力分析"""
    print("=" * 60)
    print("POWER ANALYSIS FOR MODEL × KNOWLEDGE INTERACTION")
    print("=" * 60)
    print(f"\n参数设置：")
    print(f"  Baseline accuracy (A1+K1): {BASELINE_ACC}")
    print(f"  OR (Knowledge K3 vs K1): {OR_KNOWLEDGE}")
    print(f"  OR (Model A3 vs A1): {OR_MODEL}")
    print(f"  OR (Interaction): {OR_INTERACTION}")
    print(f"  SD (Question): {SD_QUESTION}")
    print(f"  SD (Project): {SD_PROJECT}")
    print(f"  Simulations: {N_SIM}")
    print(f"  Alpha: {ALPHA}")

    print("\n" + "=" * 60)
    print("结果：")
    print("=" * 60)
    print(f"{'题目数':<10} {'效力':<10} {'95% CI':<20}")
    print("-" * 40)

    for n_q in N_QUESTIONS_LIST:
        significant_count = 0
        for _ in range(N_SIM):
            data = simulate_one_dataset(n_q)
            if test_interaction_significant(data):
                significant_count += 1

        power = significant_count / N_SIM
        se = np.sqrt(power * (1 - power) / N_SIM)
        ci_low = max(0, power - 1.96 * se)
        ci_high = min(1, power + 1.96 * se)

        status = "✅" if power >= 0.80 else "⚠️" if power >= 0.60 else "❌"
        print(f"{n_q:<10} {power:<10.3f} [{ci_low:.3f}, {ci_high:.3f}] {status}")

    print("\n说明：")
    print("  ✅ power ≥ 0.80（足够）")
    print("  ⚠️ power ≥ 0.60（偏低，可能需要更多题）")
    print("  ❌ power < 0.60（严重不足）")


if __name__ == "__main__":
    run_power_analysis()
