# Pilot30 预飞审计 - 导航页

> **GPT 审计入口**：请先阅读 `pilot30_preflight_audit_20260904/README_FOR_GPT.md`

## 仓库结构

```
/
├── pilot30_preflight_audit_20260904/    ← 审计包主目录（GPT从此开始）
│   ├── README_FOR_GPT.md                 ← 审计说明 + 阅读顺序
│   ├── 00_inventory/                     ← 文件清单与哈希
│   ├── 01_questions/                     ← 25题清单
│   ├── 02_original_reports/              ← 原始报告登记（缺原始Word）
│   ├── 03_parsed_reports/                ← 解析文本登记
│   ├── 04_report_chunks/                 ← chunk登记
│   ├── 05_rag_knowledge_base/            ← RAG/Web快照 + 清单
│   ├── 06_retrieval_snapshots/           ← 检索快照
│   ├── 07_actual_prompts/                ← Prompt模板
│   ├── 08_model_outputs/                 ← 144条模型输出
│   ├── 09_scoring_and_gold/              ← 金标世代表 + 评分状态
│   ├── 10_audit_tables/                  ← 5张审计表（候选状态）
│   ├── 11_scripts_and_config/            ← 验证脚本 + 核心实验脚本
│   └── 12_logs/                          ← 验证报告 + 缺失清单 + 隐私扫描
│
├── 09_input_reports/                     ← 旧版：11个项目的解析JSON（报告全文）
├── 03_knowledge_base/                    ← 旧版：pilot16 RAG知识库 + 检索索引
├── 04_prompts/                           ← 旧版：Prompt模板
├── 05_scripts/                           ← 旧版：pilot16脚本
├── 02_evaluation_set/                    ← 旧版：pilot16题目
├── 01_experiment_design/                 ← 旧版：实验设计文档
├── 06_calibration/                       ← 旧版：校准实验
├── 08_reference/                         ← 旧版：文献参考
└── config/                               ← 配置示例（无密钥）
```

## 审计任务

请按 `pilot30_preflight_audit_20260904/README_FOR_GPT.md` 的说明，
对 25 道环评问答进行全链路审计，判断：
1. 每道题是否有足够的证据支撑（报告证据 + 外部知识证据）
2. 如果实验失败/效果不好，问题出在哪个环节：解析→切分→检索→Prompt→模型→评分

## 重要说明

- 本仓库仅用于审计，**不授权修改金标、补库或重跑 API**
- 审计表中的候选根因为 Trae 初步标记，**非最终审判**
- 原始 Word 报告因含企业敏感信息未上传（见 PRIVATE_FILES_NOT_PUSHED.md）
