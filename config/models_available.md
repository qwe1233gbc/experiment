# 可用模型清单

> 最后验证：2026-09-01
> API端点：https://one-hub.hycx-gd.cn/v1

## Qwen 系列（推荐用于本实验）

| 模型名 | 定位 | 能力估计 | 延迟参考 |
|--------|------|---------|---------|
| qwen3.8-flash | 轻量版 | 高（天花板） | ~38s/题 |
| qwen3.8-max | 当前旗舰 | 高（天花板） | ~87s/题 |
| qwen3.7-max | 上一代旗舰 | 高 | ~31s/题 |
| qwen3.7-plus | 上一代中间档 | 待验证 | - |
| qwen3.6-plus | 3.6代中间档 | 待验证 | - |
| qwen3.6-flash | 3.6代轻量版 | 待验证 | - |

## 模型能力操纵检查结果

**结论：Qwen 3.x 系列在环境工程基础题和一般推理上天花板效应严重。**

- 第一轮 20 道基础题：三模型全部 100%
- 第二轮 15 道高难题：三模型接近 100%（97.8%-100%）
- 无法建立 A1 < A2 < A3 的能力梯度

**建议采用"模型规格/代际差异"而非"能力梯度"作为研究设计。**

## GPT 系列

gpt-5.6, gpt-5.6-sol, gpt-5.6-terra, gpt-5.6-luna, gpt-5.5, gpt-5.4, gpt-5.4-mini

## Claude 系列

claude-opus-5, claude-sonnet-5, claude-opus-4.8, claude-sonnet-4.6 等

## DeepSeek 系列

deepseek-v4-pro, deepseek-v3.2, deepseek-v4-flash 等

## Gemini 系列

gemini-3.7-flash, gemini-3.5-flash, gemini-3.1-pro 等

## 其他

MiniMax (M2/M2.5/M2.7/M3), Kimi (k2.5/k2.6/k2.7-code), GLM (glm-5/5.1/5.2), Grok (grok-4.5/4.6)
