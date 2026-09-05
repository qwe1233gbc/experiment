# VOCs 废气收集效率取值表

- **标准编号**：STD-DIFY-12-001
- **知识类型**：threshold
- **领域**：废气收集

## 来源依据

  - 广东省工业源VOCs减排量核算方法(2023修订版) 表23；Dify 收集效率判定指南

## 适用范围

用于审核报告采用的收集效率是否高于对应收集方式上限。

## 规范性要求

  - 单层密闭负压 95%。
  - 单层密闭正压 85%。
  - 双层密闭空间 99%。
  - 设备排气口直连 95%。
  - 包围式风速≥0.5m/s 为 80%。
  - 包围式风速0.3–0.5m/s 为 60%。
  - 外部式风速≥0.5m/s 为 40%。
  - 外部式风速0.3–0.5m/s 为 20%–40%。
  - 无收集设施 0%。

## 限值/阈值

  - collection_type: 单层密闭负压；efficiency: 95%
  - collection_type: 单层密闭正压；efficiency: 85%
  - collection_type: 双层密闭空间；efficiency: 99%
  - collection_type: 设备排气口直连；efficiency: 95%
  - collection_type: 包围式，风速≥0.5m/s；efficiency: 80%
  - collection_type: 包围式，风速0.3-0.5m/s；efficiency: 60%
  - collection_type: 外部式，风速≥0.5m/s；efficiency: 40%
  - collection_type: 外部式，风速0.3-0.5m/s；efficiency: 20%-40%
  - collection_type: 无收集设施；efficiency: 0%

## 检查逻辑

  - 提取报告收集效率和收集方式。
  - 按收集方式检索效率上限。
  - 报告效率高于标准卡上限时判为不合理。
  - 密闭负压、直连、包围式均需对应证据，不应只写结论。

## 需核实的证据字段

  - 收集方式
  - 密闭证据
  - 控制风速
  - 报告收集效率
  - 治理设施

## 输出字段

  - standard_id
  - matched_evidence
  - judgement
  - risk_level
  - reason
  - suggested_revision

## 触发关键词

  - 收集效率
  - 单层密闭负压
  - 双层密闭
  - 设备排气口直连
  - 包围式
  - 外部式
  - 无收集设施

