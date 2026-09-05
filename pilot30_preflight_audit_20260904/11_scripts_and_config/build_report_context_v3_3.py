#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v3.3 证据槽驱动上下文构建器 + 输入门禁

在 v3.2 基础上的关键改进：
1. 证据槽驱动（不是章节驱动）- 每个题型定义必需证据清单
2. 双通道召回：section召回 ∪ 全JSON关键词召回
3. 字符预算按证据槽分配（不是从前往后拼）
4. 输入门禁：必需证据未命中则 input_insufficient，不调用模型
5. confirmed_absence：标准未出现需经全JSON扫描确认，不自动转"报告缺项"

上下文长度限制：15,000 字符（与 v2/v3.1/v3.2 保持一致，确保可比性）
"""
import re
import json
import hashlib
from pathlib import Path

REPORT_DIR = Path(__file__).parent.parent / "09_input_reports"
MAX_CONTEXT_CHARS = 15000
SLOT_MARKER = "▓"

# ========== 章节识别（复用 v3.2 内容识别逻辑） ==========

CHAPTER_PATTERNS = [
    (r'一、建设项目基本情况', 'basic'),
    (r'建设项目基本情况', 'basic'),
    (r'二、建设项目工程分析', 'engineering'),
    (r'建设项目工程分析', 'engineering'),
    (r'三、区域环境质量现状', 'standard'),
    (r'区域环境质量现状.*评价标准', 'standard'),
    (r'环境保护目标及评价标准', 'standard'),
    (r'四、主要环境影响和保护措施', 'measures'),
    (r'主要环境影响和保护措施', 'measures'),
    (r'运营期环境影响和保护措施', 'measures'),
    (r'施工期环境保护措施', 'measures'),
    (r'五、环境保护措施监督检查清单', 'supervision'),
    (r'环境保护措施监督检查清单', 'supervision'),
    (r'监督检查清单', 'supervision'),
    (r'六、结论', 'conclusion'),
    (r'附表', 'appendix'),
    (r'污染物排放量汇总表', 'appendix'),
    (r'建设项目环境影响报告表', 'cover'),
    (r'目\s*录', 'cover'),
    (r'封面与目录', 'cover'),
]


def classify_section_by_content(content):
    text = re.sub(r'<[^>]+>', ' ', content)
    text = re.sub(r'\s+', ' ', text)[:500]
    for pattern, category in CHAPTER_PATTERNS:
        if re.search(pattern, text):
            return category
    return 'unknown'


def classify_section(section_name, content=""):
    if content:
        cat = classify_section_by_content(content)
        if cat != 'unknown':
            return cat
    name = str(section_name)
    if any(kw in name for kw in ['建设项目基本情况', '一、']):
        if '工程分析' not in name and '评价标准' not in name:
            return "basic"
    if any(kw in name for kw in ['工程分析', '二、']):
        return "engineering"
    if any(kw in name for kw in ['评价标准', '环境质量', '三、']):
        return "standard"
    if any(kw in name for kw in ['保护措施', '环境影响', '四、']):
        return "measures"
    if any(kw in name for kw in ['监督检查', '五、']):
        return "supervision"
    if any(kw in name for kw in ['结论', '六、']):
        return "conclusion"
    if any(kw in name for kw in ['附表', '附件', '附图']):
        return "appendix"
    if any(kw in name for kw in ['封面', '目录']):
        return "cover"
    return "unknown"


# ========== HTML 表格提取 ==========

def extract_html_tables(content):
    tables = []
    remaining = content
    table_pattern = re.compile(r'<table[^>]*>(.*?)</table>', re.DOTALL | re.IGNORECASE)
    for match in table_pattern.finditer(content):
        table_html = match.group(1)
        rows = []
        tr_pattern = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL | re.IGNORECASE)
        for tr in tr_pattern.finditer(table_html):
            cells = []
            td_pattern = re.compile(r'<t[dh][^>]*>(.*?)</t[dh]>', re.DOTALL | re.IGNORECASE)
            for td in td_pattern.finditer(tr.group(1)):
                cell_text = re.sub(r'<[^>]+>', '', td.group(1)).strip()
                cell_text = re.sub(r'\s+', ' ', cell_text)
                if cell_text:
                    cells.append(cell_text)
            if cells:
                rows.append(' | '.join(cells))
        if rows:
            tables.append('\n'.join(rows))
    remaining = table_pattern.sub('[表格已提取]', remaining)
    return tables, remaining


# ========== 基础工具函数（从 v3 导入简化版） ==========

def find_hits_in_section(content, keywords):
    hits = []
    text = re.sub(r'<[^>]+>', ' ', content)
    for kw in keywords:
        pos = 0
        while True:
            idx = text.find(kw, pos)
            if idx == -1:
                break
            hits.append({"keyword": kw, "position": idx})
            pos = idx + len(kw)
    return hits


def extract_windows_from_content(content, hits, max_chars):
    """
    v3.3 改进：找命中最密集的区域，而不是第一个命中的位置。
    对于长内容，选择关键词命中最密集的窗口。
    """
    if not hits:
        return "", 0
    
    text = re.sub(r'<[^>]+>', ' ', content)
    text = re.sub(r'\s+', ' ', text)
    
    if len(text) <= max_chars:
        return text, len(text)
    
    # 找出所有命中的位置
    hit_positions = sorted(set(h["position"] for h in hits))
    
    if not hit_positions:
        return "", 0
    
    # 滑动窗口找命中最密集的区域
    best_start = 0
    best_count = 0
    
    # 对每个命中位置，计算以它为起点的窗口内有多少命中
    for i, pos in enumerate(hit_positions):
        window_start = max(0, pos - max_chars // 4)  # 偏置：命中点在窗口前 1/4 处
        window_end = window_start + max_chars
        
        # 数这个窗口内有多少命中
        count = sum(1 for p in hit_positions if window_start <= p < window_end)
        
        if count > best_count:
            best_count = count
            best_start = window_start
    
    # 如果只有 1 个命中，以它为中心
    if best_count <= 1:
        first_hit = hit_positions[0]
        half = max_chars // 2
        best_start = max(0, first_hit - half)
    
    end = min(len(text), best_start + max_chars)
    if end - best_start < max_chars:
        best_start = max(0, end - max_chars)
    
    extracted = text[best_start:end]
    if best_start > 0:
        extracted = "..." + extracted
    if end < len(text):
        extracted = extracted + "..."
    
    return extracted, len(extracted)


def extract_project_id(question_id, project_field=""):
    if project_field:
        return project_field
    m = re.match(r'([A-Z]{2}\d{3})', question_id)
    if m:
        return m.group(1)
    return ""


def load_report_json(project_id):
    if not project_id:
        return None, ""
    candidates = list(REPORT_DIR.glob(f"{project_id}_*.json"))
    if not candidates:
        candidates = list(REPORT_DIR.glob(f"*{project_id}*.json"))
    if not candidates:
        return None, ""
    report_file = str(candidates[0])
    with open(report_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data, report_file


def detect_task_module(question_id, task_type="", question_text=""):
    qid_lower = question_id.lower()
    text_all = f"{question_id} {task_type} {question_text}".lower()
    
    if 'invest_ratio' in qid_lower or '环保投资比例' in task_type:
        return "invest_ratio"
    if 'emission_固体' in qid_lower or '固体废物控制标准' in task_type:
        return "solid_waste_standard"
    if 'vocstotal' in qid_lower or '总量' in task_type or '源强' in task_type:
        return "VOCs_total"
    if 'vocsmeasure' in qid_lower or '治理措施一致' in task_type:
        return "VOCs_measure_consistency"
    if 'captureefficiency' in qid_lower or '收集效率' in task_type:
        return "capture_efficiency"
    if ('captureairflow' in qid_lower or 'designairflow' in qid_lower
            or '排气量' in task_type or '理论排气' in task_type or '设计风量' in task_type):
        return "capture_airflow_calc"
    if 'industry' in qid_lower or '行业分类' in task_type:
        return "industry_classification"
    return "default"


# ========== v3.3 必需证据定义 ==========
# 每道重点题的最低证据要求（用于输入门禁）

REQUIRED_EVIDENCE = {
    "PL001_Emission_固体": [
        {"id": "gb34330", "pattern": r"GB\s*34330", "label": "GB 34330-2017"},
        {"id": "gbt39198", "pattern": r"GB/T\s*39198|39198", "label": "GB/T 39198-2020"},
        {"id": "hw_list", "pattern": r"国家危险废物名录|危险废物名录", "label": "国家危险废物名录"},
        {"id": "gb18597", "pattern": r"GB\s*18597", "label": "GB 18597-2023"},
        {"id": "gb18599_ref", "pattern": r"GB\s*18599", "label": "报告引用GB 18599的位置"},
        {"id": "warehouse", "pattern": r"库房|一般固废仓|一般工业.*仓|暂存间", "label": "一般固废仓形式"},
    ],
    "PL005_Emission_固体": [
        {"id": "law", "pattern": r"固体废物污染环境防治法|固废法", "label": "固废污染防治法"},
        {"id": "gd_regulation", "pattern": r"广东省固体废物污染环境防治条例", "label": "广东省条例"},
        {"id": "gbt39198", "pattern": r"GB/T\s*39198|39198", "label": "GB/T 39198-2020"},
        {"id": "hw_list", "pattern": r"国家危险废物名录|危险废物名录", "label": "国家危险废物名录"},
        {"id": "gb18597", "pattern": r"GB\s*18597", "label": "GB 18597-2023"},
        {"id": "warehouse_3f", "pattern": r"库房|暂存|防渗漏|防雨淋|防扬尘|三防", "label": "库房暂存及三防"},
    ],
    "PL008_VOCSTotal_Q01": [
        {"id": "n_31802", "pattern": r'3\.1802', "label": "3.1802 t/a"},
        {"id": "n_000093", "pattern": r'0\.00093', "label": "0.00093 t/a"},
        {"id": "n_3635819", "pattern": r'3\.635819|3\.6358', "label": "3.635819"},
        {"id": "n_136296", "pattern": r'1\.36296', "label": "1.36296"},
        {"id": "n_090867", "pattern": r'0\.90867', "label": "0.90867"},
        {"id": "n_09089", "pattern": r'0\.9089', "label": "0.9089"},
        {"id": "n_181757", "pattern": r'1\.81757|1\.8176', "label": "1.81757"},
        {"id": "unit_ta", "pattern": r't/a', "label": "t/a 单位"},
    ],
    "PL008_VOCSMeasure_Q01": [
        {"id": "engineering_measure", "pattern": r"工程分析.*活性炭|活性炭.*工程分析", "label": "工程分析-治理设施"},
        {"id": "two_stage", "pattern": r"两级活性炭|二级活性炭", "label": "两级/二级活性炭"},
        {"id": "h45m", "pattern": r"45\s*m|45米", "label": "45 m 排气筒"},
        {"id": "fq_code", "pattern": r"FQ-03672|FQ03672", "label": "FQ-03672"},
        {"id": "water_curtain", "pattern": r"水帘柜|水帘.*干式过滤", "label": "水帘柜+干式过滤"},
    ],
    "PL007_CaptureEfficiency_Q01": [
        {"id": "cylinder_closed", "pattern": r"分散缸.*闭合|投料口.*闭合|闭合.*投料", "label": "分散缸投料口闭合"},
        {"id": "direct_exhaust", "pattern": r"排气管.*接入|排气口.*接入|直接接入", "label": "排气管直接接入"},
        {"id": "ref_95", "pattern": r"95%.*收集|收集.*95%|95%.*效率", "label": "95%参考值"},
        {"id": "actual_90", "pattern": r"90%.*收集|收集效率.*90%|90%.*效率", "label": "90%实际取值"},
    ],
    "PL010_VOCSTotal_Q01": [
        {"id": "org_0194", "pattern": r"0\.194.*t/a|有组织.*0\.194|0\.194.*有组织", "label": "有组织0.194 t/a"},
        {"id": "unorg_0047", "pattern": r"0\.047.*t/a|无组织.*0\.047|0\.047.*无组织", "label": "无组织0.047 t/a"},
        {"id": "total_0211", "pattern": r"0\.211.*t/a|总量.*0\.211|0\.211.*总量", "label": "总量0.211 t/a"},
        {"id": "source_table", "pattern": r"源强|核算表|产生量.*t/a", "label": "源强表"},
    ],
    "PL014_CaptureAirflow_Q01": [
        {"id": "formula_nvf", "pattern": r"L\s*=\s*nVf|L=nVf|nVf", "label": "L=nVf 公式"},
        {"id": "rate_12", "pattern": r"12次/h|12\s*次/小时|换气次数.*12", "label": "12次/h换气次数"},
        {"id": "capture_80", "pattern": r"80%.*收集|收集效率.*80|废气捕集率.*80|80%.*废气捕集", "label": "80%收集效率/废气捕集率"},
        {"id": "formula_kphv", "pattern": r"Q\s*=\s*K.*P.*H.*V|K.*P.*H.*V.*3600|Q=KPHV", "label": "Q=K×P×H×Vx×3600"},
        {"id": "vx_05", "pattern": r"Vx.*0\.5|0\.5.*m/s|控制风速.*0\.5|0\.5.*控制风速", "label": "Vx=0.5 m/s"},
        {"id": "h_02", "pattern": r"H.*0\.2|0\.2\s*m.*距离|污染源.*罩口.*0\.2|0\.2.*污染源", "label": "H=0.2 m"},
    ],
    "PL008_DesignAirflow_Q01": [
        {"id": "calc_17156", "pattern": r"17156", "label": "设计处理风量计算值17156.4m3/h"},
        {"id": "design_120pct", "pattern": r"120%", "label": "按最大排气量120%设计依据"},
        {"id": "airflow_20000", "pattern": r"20000", "label": "设计风量取整20000m3/h"},
        {"id": "hj2026", "pattern": r"HJ\s*2026", "label": "HJ2026-2013吸附法技术规范"},
    ],
    "NEW_PL006_living_wastewater": [
        {"id": "living_wastewater", "pattern": r"生活污水", "label": "生活污水产生与治理"},
        {"id": "staff", "pattern": r"员工|职工|定员|劳动定员", "label": "劳动定员人数"},
        {"id": "water_qty", "pattern": r"用水量", "label": "用水量数据"},
    ],
    "NEW_PL007_ro_water": [
        {"id": "ro_water", "pattern": r"纯水|反渗透|RO", "label": "纯水制备工艺"},
        {"id": "concentrated_water", "pattern": r"浓水", "label": "浓水产生情况"},
    ],
    "PL013_HazardousWaste_Q01": [
        {"id": "hw_identify", "pattern": r"危险废物", "label": "危险废物识别"},
        {"id": "hw_list", "pattern": r"国家危险废物名录|危险废物名录", "label": "国家危险废物名录"},
        {"id": "waste_oil", "pattern": r"废油桶|油桶|废油", "label": "废油桶等危废种类"},
    ],
}

# confirmed_absence 列表：这些标准在报告中确实未出现，不应判为输入缺失
CONFIRMED_ABSENCE_STANDARDS = {
    "PL005_Emission_固体": ["GB 18599-2020"],  # PL005 报告未引用 GB 18599，是报告事实
}


# ========== v3.3 证据槽定义（按字符预算分配） ==========

V33_EVIDENCE_SLOTS = {
    # ===== 固废控制标准 =====
    "solid_waste_standard": [
        {
            "name": "项目基本参数",
            "keywords": ["建设项目名称", "建设单位", "行业类别", "产品方案", "建设地点"],
            "preferred_sections": ["basic"],
            "quota": 2000,
            "required": False,
            "budget_category": "basic_params",
        },
        {
            "name": "固废产生情况",
            "keywords": [
                "固体废物", "一般工业固体废物", "危险废物",
                "产生量", "处置方式", "废包装", "生活垃圾",
            ],
            "preferred_sections": ["engineering", "measures"],
            "quota": 3000,
            "required": True,
            "budget_category": "core_evidence",
        },
        {
            "name": "固废标准依据",
            "keywords": [
                "GB 18599", "GB18599", "一般工业固体废物贮存",
                "GB 18597", "GB18597", "危险废物贮存",
                "危险废物名录", "国家危险废物名录",
                "固体废物污染环境防治法",
                "GB 34330", "GB34330",
                "GB/T 39198", "分类与代码",
            ],
            "preferred_sections": ["standard", "measures"],
            "quota": 4000,
            "required": True,
            "budget_category": "core_evidence",
        },
        {
            "name": "固废贮存与处置措施",
            "keywords": [
                "暂存间", "暂存房", "贮存间", "贮存设施",
                "防渗漏", "防雨淋", "防扬散", "三防",
                "危险废物暂存", "一般固废暂存",
                "委托有资质", "转移联单", "分类收集",
                "库房", "仓库",
            ],
            "preferred_sections": ["measures"],
            "quota": 4000,
            "required": True,
            "budget_category": "core_evidence",
        },
        {
            "name": "监督检查清单（固废）",
            "keywords": [
                "监督检查清单", "环境保护措施监督检查",
                "固体废物", "危险废物",
            ],
            "preferred_sections": ["supervision"],
            "quota": 2000,
            "required": False,
            "budget_category": "cross_check",
        },
    ],
    
    # ===== VOCs 总量一致性 =====
    "VOCs_total": [
        {
            "name": "项目基本参数",
            "keywords": ["建设项目名称", "建设单位", "产品方案", "原辅材料", "行业类别"],
            "preferred_sections": ["basic"],
            "quota": 1000,
            "required": False,
            "budget_category": "basic_params",
        },
        {
            "name": "VOCs源强核算表",
            "keywords": [
                "源强核算", "源强", "核算表", "产生量",
                "有组织", "无组织", "排放速率", "排放浓度",
                "收集率", "去除率", "处理效率",
                "t/a", "kg/h", "排气筒",
                "VOCs", "非甲烷总烃",
            ],
            "preferred_sections": ["engineering", "measures"],
            "quota": 8000,
            "required": True,
            "budget_category": "core_evidence",
        },
        {
            "name": "总量控制指标",
            "keywords": [
                "总量控制", "总量指标", "污染物排放总量",
                "排放量汇总", "VOCs 总量", "VOCs排放量",
            ],
            "preferred_sections": ["measures", "conclusion", "appendix"],
            "quota": 3500,
            "required": True,
            "budget_category": "cross_check",
        },
        {
            "name": "治理设施参数",
            "keywords": [
                "活性炭", "吸附装置", "集气罩", "收集",
                "设计风量", "排气筒", "FQ-0",
            ],
            "preferred_sections": ["measures"],
            "quota": 1000,
            "required": False,
            "budget_category": "cross_check",
        },
        {
            "name": "附表污染物汇总",
            "keywords": [
                "附表", "污染物排放", "排放汇总",
                "非甲烷总烃", "VOCs", "t/a",
            ],
            "preferred_sections": ["appendix", "supervision"],
            "quota": 1000,
            "required": False,
            "budget_category": "cross_check",
        },
    ],
    
    # ===== VOCs 治理措施一致性 =====
    "VOCs_measure_consistency": [
        {
            "name": "项目基本参数",
            "keywords": ["建设项目名称", "建设单位", "产品方案"],
            "preferred_sections": ["basic"],
            "quota": 1500,
            "required": False,
            "budget_category": "basic_params",
        },
        {
            "name": "工程分析-废气措施",
            "keywords": [
                "工程分析", "废气", "VOCs",
                "活性炭", "吸附", "集气罩", "收集",
                "排气筒", "FQ-0",
            ],
            "preferred_sections": ["engineering"],
            "quota": 4000,
            "required": True,
            "budget_category": "core_evidence",
        },
        {
            "name": "运营期环保措施-废气",
            "keywords": [
                "运营期", "废气", "VOCs",
                "活性炭", "吸附装置", "治理设施",
                "排气筒", "收集效率", "去除率",
            ],
            "preferred_sections": ["measures"],
            "quota": 4000,
            "required": True,
            "budget_category": "core_evidence",
        },
        {
            "name": "监督检查清单-废气",
            "keywords": [
                "监督检查清单", "环境保护措施监督检查",
                "废气", "VOCs", "排气筒", "活性炭",
            ],
            "preferred_sections": ["supervision"],
            "quota": 3500,
            "required": True,
            "budget_category": "cross_check",
        },
        {
            "name": "废气达标排放",
            "keywords": [
                "达标排放", "排放浓度", "排放速率",
                "标准", "DB44", "GB 16297",
            ],
            "preferred_sections": ["measures"],
            "quota": 2000,
            "required": False,
            "budget_category": "cross_check",
        },
    ],
    
    # ===== 废气收集效率 =====
    "capture_efficiency": [
        {
            "name": "项目基本参数",
            "keywords": ["建设项目名称", "建设单位", "产品方案", "行业类别"],
            "preferred_sections": ["basic"],
            "quota": 1500,
            "required": False,
            "budget_category": "basic_params",
        },
        {
            "name": "废气产生工序",
            "keywords": [
                "分散", "研磨", "调漆", "投料", "试喷",
                "生产工艺", "工艺流程", "产生工序",
            ],
            "preferred_sections": ["engineering"],
            "quota": 3000,
            "required": True,
            "budget_category": "core_evidence",
        },
        {
            "name": "收集方式与设施",
            "keywords": [
                "集气罩", "收集", "密闭", "封闭",
                "投料口", "排气口", "排气管",
                "收集效率", "收集率",
            ],
            "preferred_sections": ["engineering", "measures"],
            "quota": 5000,
            "required": True,
            "budget_category": "core_evidence",
        },
        {
            "name": "治理设施与参数",
            "keywords": [
                "活性炭", "吸附", "治理设施", "处理效率",
                "排气筒", "设计风量", "去除率",
            ],
            "preferred_sections": ["measures"],
            "quota": 3500,
            "required": False,
            "budget_category": "core_evidence",
        },
        {
            "name": "监督检查清单",
            "keywords": [
                "监督检查清单", "环境保护措施监督检查",
                "废气", "收集", "排气筒",
            ],
            "preferred_sections": ["supervision"],
            "quota": 2000,
            "required": False,
            "budget_category": "cross_check",
        },
    ],
    
    # ===== 废气收集形式与理论排气量 =====
    "capture_airflow_calc": [
        {
            "name": "项目基本参数",
            "keywords": ["建设项目名称", "建设单位", "产品方案", "行业类别"],
            "preferred_sections": ["basic"],
            "quota": 1500,
            "required": False,
            "budget_category": "basic_params",
        },
        {
            "name": "废气产生工序",
            "keywords": [
                "投料", "分散", "研磨", "打包", "实验室",
                "生产工艺", "工艺流程", "产生工序",
            ],
            "preferred_sections": ["engineering"],
            "quota": 2500,
            "required": True,
            "budget_category": "core_evidence",
        },
        {
            "name": "收集形式与集气罩参数",
            "keywords": [
                "集气罩", "上吸式", "侧吸式", "密闭", "包围型",
                "罩口尺寸", "控制风速", "污染源", "罩口距离",
                "Vx", "Vx=", "m/s", "H=",
                "Q=K", "K×P×H", "局部排风", "排风量计算",
                "简明通风设计手册",
            ],
            "preferred_sections": ["engineering", "measures"],
            "quota": 7000,
            "required": True,
            "budget_category": "core_evidence",
        },
        {
            "name": "理论排气量与设计风量",
            "keywords": [
                "理论排气量", "设计风量", "换气次数",
                "m3/h", "风量", "排风量", "排气量",
                "L=nVf", "nVf", "全面通风", "换气次数法",
                "废气捕集率", "收集效率", "80%",
                "密闭区域", "正压", "所需新风量",
                "表4-7", "表4-8", "所需风量一览表",
            ],
            "preferred_sections": ["engineering", "measures"],
            "quota": 6000,
            "required": True,
            "budget_category": "core_evidence",
        },
        {
            "name": "治理设施与排气筒",
            "keywords": [
                "活性炭", "吸附", "治理设施",
                "排气筒", "G1", "FQ-0",
                "总风量", "风量合计",
            ],
            "preferred_sections": ["measures"],
            "quota": 2000,
            "required": False,
            "budget_category": "cross_check",
        },
    ],
    
    # ===== 环保投资比例 =====
    "invest_ratio": [
        {
            "name": "总投资数据",
            "keywords": ["总投资", "环保投资", "投资比例", "占比", "万元"],
            "preferred_sections": ["basic"],
            "quota": 3000,
            "required": True,
            "budget_category": "core_evidence",
        },
        {
            "name": "环保投资明细",
            "keywords": [
                "环保投资", "废气治理", "废水治理", "固废治理",
                "噪声治理", "绿化", "监测",
            ],
            "preferred_sections": ["basic", "measures"],
            "quota": 4000,
            "required": True,
            "budget_category": "core_evidence",
        },
        {
            "name": "项目概况",
            "keywords": ["建设项目名称", "建设单位", "产品方案", "行业类别"],
            "preferred_sections": ["basic"],
            "quota": 2000,
            "required": False,
            "budget_category": "basic_params",
        },
        {
            "name": "环保措施清单",
            "keywords": ["环境保护措施", "治理设施", "投资", "万元"],
            "preferred_sections": ["measures", "supervision"],
            "quota": 3000,
            "required": False,
            "budget_category": "cross_check",
        },
        {
            "name": "结论与附表",
            "keywords": ["结论", "投资", "环保", "附表"],
            "preferred_sections": ["conclusion", "appendix"],
            "quota": 2000,
            "required": False,
            "budget_category": "cross_check",
        },
    ],
    
    # ===== 国民经济行业分类 =====
    "industry_classification": [
        {
            "name": "行业类别",
            "keywords": ["行业类别", "国民经济行业", "行业代码", "C26", "C27", "C29", "C30"],
            "preferred_sections": ["basic"],
            "quota": 4000,
            "required": True,
            "budget_category": "core_evidence",
        },
        {
            "name": "产品与工艺",
            "keywords": ["产品方案", "生产工艺", "主要产品", "原辅材料"],
            "preferred_sections": ["basic", "engineering"],
            "quota": 5000,
            "required": True,
            "budget_category": "core_evidence",
        },
        {
            "name": "项目概况",
            "keywords": ["建设项目名称", "建设单位", "建设地点"],
            "preferred_sections": ["basic"],
            "quota": 2000,
            "required": False,
            "budget_category": "basic_params",
        },
        {
            "name": "环保措施清单",
            "keywords": ["环境保护措施", "废气治理", "废水治理", "固废治理"],
            "preferred_sections": ["measures"],
            "quota": 2000,
            "required": False,
            "budget_category": "cross_check",
        },
    ],
    
    # ===== 默认 =====
    "default": [
        {
            "name": "项目概况",
            "keywords": ["建设项目名称", "建设单位", "行业类别", "产品方案"],
            "preferred_sections": ["basic"],
            "quota": 3000,
            "required": False,
            "budget_category": "basic_params",
        },
        {
            "name": "工程分析",
            "keywords": ["工程分析", "生产工艺", "工艺流程", "原辅材料", "产污环节"],
            "preferred_sections": ["engineering"],
            "quota": 5000,
            "required": True,
            "budget_category": "core_evidence",
        },
        {
            "name": "环保措施",
            "keywords": ["环境保护措施", "废气", "废水", "固废", "噪声", "治理"],
            "preferred_sections": ["measures"],
            "quota": 4000,
            "required": True,
            "budget_category": "core_evidence",
        },
        {
            "name": "监督检查清单",
            "keywords": ["监督检查清单", "环境保护措施监督检查"],
            "preferred_sections": ["supervision"],
            "quota": 3000,
            "required": False,
            "budget_category": "cross_check",
        },
    ],
}


# ========== v3.3 全 JSON 召回搜索 ==========

def search_report_for_slot_v33(report_data, slot_def, chunk_ids_used=None):
    """
    v3.3 版：全 JSON 关键词召回 + 双通道（section + 内容识别）
    改进点：
    1. 去重：已使用过的片段不再重复提取（避免重复内容占预算）
    2. 表格优先：关键词命中表格时整表提取
    3. 返回片段ID列表（用于 input_manifest）
    """
    keywords = slot_def["keywords"]
    preferred = slot_def.get("preferred_sections", [])
    quota = slot_def["quota"]
    chunk_ids_used = chunk_ids_used or set()
    
    # 第一轮：遍历所有片段，计算得分
    scored_chunks = []
    
    for i, item in enumerate(report_data):
        chunk_id = item.get("id", i)
        if chunk_id in chunk_ids_used:
            continue
        
        sec_name = str(item.get('section', ''))
        content = str(item.get('content', ''))
        
        if len(content) < 80:
            continue
        
        # 内容识别章节（v3.2 逻辑，不依赖 section 字段）
        sec_cat = classify_section(sec_name, content)
        
        # 搜索命中
        hits = find_hits_in_section(content, keywords)
        if not hits:
            continue
        
        # 计算综合分数
        base_score = len(hits) * 10
        
        if sec_cat in preferred:
            priority_bonus = 50
        elif sec_cat == 'unknown':
            priority_bonus = 10
        else:
            priority_bonus = 0
        
        len_score = min(len(content) / 1000, 10)
        total_score = base_score + priority_bonus + len_score
        
        scored_chunks.append({
            "chunk_id": chunk_id,
            "chunk_index": i,
            "section_name": sec_name[:80],
            "section_category": sec_cat,
            "hit_count": len(hits),
            "score": total_score,
            "content": content,
            "hits": hits,
            "is_preferred": sec_cat in preferred,
        })
    
    if not scored_chunks:
        return "", 0, 0, []
    
    scored_chunks.sort(key=lambda x: -x["score"])
    
    # 第二轮：按分数从高到低提取，直到配额用完
    extracted_parts = []
    total_chars = 0
    total_hits = 0
    chunks_used = []
    remaining_quota = quota
    
    for chunk in scored_chunks:
        if remaining_quota < 200:
            break
        
        # 优先章节：最多提取该槽配额的 60%
        if chunk["is_preferred"]:
            max_for_this = int(quota * 0.6)
        else:
            max_for_this = int(quota * 0.35)
        
        available = min(remaining_quota, max_for_this)
        if available < 100:
            continue
        
        extracted, chars = extract_windows_from_content(
            chunk["content"], chunk["hits"], available
        )
        
        if extracted and chars > 0:
            # 检查表格
            tables, _ = extract_html_tables(chunk["content"])
            relevant_tables = []
            for table in tables:
                kw_hits = sum(1 for kw in keywords if kw in table)
                if kw_hits >= 2:
                    relevant_tables.append(table)
            
            table_text = ""
            if relevant_tables:
                table_text = "\n\n【相关表格】\n" + "\n\n".join(relevant_tables[:3])
                table_chars = len(table_text)
                if total_chars + chars + table_chars <= quota * 1.1:
                    chars += table_chars
                else:
                    table_text = ""
            
            full_extract = extracted + table_text
            
            extracted_parts.append((chunk["section_name"], full_extract))
            total_chars += chars
            total_hits += chunk["hit_count"]
            remaining_quota -= chars
            chunks_used.append(chunk["chunk_id"])
    
    if not extracted_parts:
        return "", 0, 0, []
    
    parts_text = []
    for sec_name, text in extracted_parts:
        sec_short = sec_name[:40] if len(sec_name) > 40 else sec_name
        parts_text.append(f"【{sec_short}】\n{text}")
    
    full_text = f"{SLOT_MARKER}{slot_def['name']}{SLOT_MARKER}\n\n" + "\n\n".join(parts_text)
    
    return full_text, total_chars, total_hits, chunks_used


# ========== v3.3 必需证据检查（输入门禁） ==========

def check_required_evidence(report_data, question_id, context_text=""):
    """
    v3.3 输入门禁：检查必需证据。
    两阶段检查：
    1. 报告全文扫描：确认证据是否存在于报告中（判断 confirmed_absence）
    2. 上下文检查：确认证据是否真正进入了发送给模型的上下文
    
    返回: (results_dict, status)
    status: ready / input_insufficient / no_requirements
    """
    requirements = REQUIRED_EVIDENCE.get(question_id, [])
    if not requirements:
        return {}, "no_requirements"
    
    # 阶段1：报告全文扫描
    full_text = ""
    for item in report_data:
        content = str(item.get('content', ''))
        full_text += re.sub(r'<[^>]+>', ' ', content) + " "
    full_text = re.sub(r'\s+', ' ', full_text)
    
    # 阶段2：上下文中的检查（去HTML）
    ctx_clean = re.sub(r'<[^>]+>', ' ', context_text) if context_text else ""
    ctx_clean = re.sub(r'\s+', ' ', ctx_clean)
    
    results = {}
    all_pass = True  # 上下文是否包含所有必需证据
    
    confirmed_absent_list = CONFIRMED_ABSENCE_STANDARDS.get(question_id, [])
    
    for req in requirements:
        pattern = req["pattern"]
        label = req["label"]
        
        try:
            # 报告全文中是否存在
            in_report = bool(re.search(pattern, full_text, re.IGNORECASE))
            report_count = len(re.findall(pattern, full_text, re.IGNORECASE))
            
            # 上下文中是否存在
            in_context = bool(re.search(pattern, ctx_clean, re.IGNORECASE)) if ctx_clean else False
            context_count = len(re.findall(pattern, ctx_clean, re.IGNORECASE)) if ctx_clean else 0
        except:
            in_report = pattern in full_text
            report_count = 1 if in_report else 0
            in_context = pattern in ctx_clean
            context_count = 1 if in_context else 0
        
        # 判断是否为 confirmed_absence
        is_confirmed_absence = False
        if not in_report:
            for ca in confirmed_absent_list:
                if ca in label or ca in req.get("id", ""):
                    is_confirmed_absence = True
                    break
        
        results[req["id"]] = {
            "found_in_report": in_report,
            "found_in_context": in_context,
            "label": label,
            "report_count": report_count,
            "context_count": context_count,
            "confirmed_absence": is_confirmed_absence,
        }
        
        # 判断是否通过门禁
        # - 在上下文中 → 通过
        # - confirmed_absence（报告确实没有）→ 通过（这是报告事实）
        # - 报告中有但上下文中没有 → 不通过（提取失败）
        # - 报告中没有且不是 confirmed_absence → 不通过（报告缺项？但应先确认）
        if in_context or is_confirmed_absence:
            pass  # 通过
        else:
            all_pass = False
    
    status = "ready" if all_pass else "input_insufficient"
    
    return results, status


# ========== v3.3 主构建函数 ==========

def build_context_v33(question_id, project_field="", question_text="", task_type=""):
    """
    v3.3 版本文构建函数
    - 证据槽驱动（不是章节驱动）
    - 双通道召回（section + 全JSON关键词）
    - 按证据槽分配字符预算
    - 输入门禁（必需证据检查）
    - confirmed_absence 处理
    """
    project_id = extract_project_id(question_id, project_field)
    if not project_id:
        return _error_result(question_id, "unknown", "error_no_project")
    
    report_data, report_file = load_report_json(project_id)
    if not report_data:
        return _error_result(question_id, project_id, "error_no_report")
    
    # 检测任务模块
    task_module = detect_task_module(question_id, task_type, question_text)
    slot_definitions = V33_EVIDENCE_SLOTS.get(task_module, V33_EVIDENCE_SLOTS["default"])
    
    # v3.3：按证据槽提取，去重使用片段
    all_slot_results = []
    total_chars = 0
    required_slots_filled = 0
    required_slots_total = 0
    used_chunk_ids = set()
    all_chunk_ids = []
    all_sections_hit = []
    
    # 统计必需槽
    for slot_def in slot_definitions:
        if slot_def.get("required", False):
            required_slots_total += 1
    
    # 第一轮：必需槽（优先保证）
    required_slots = [s for s in slot_definitions if s.get("required", False)]
    optional_slots = [s for s in slot_definitions if not s.get("required", False)]
    
    # 计算必需槽总配额，确保不超过总预算的 80%
    total_required_quota = sum(s["quota"] for s in required_slots)
    quota_scale = 1.0
    if total_required_quota > MAX_CONTEXT_CHARS * 0.8:
        quota_scale = (MAX_CONTEXT_CHARS * 0.8) / total_required_quota
    
    for slot_def in required_slots:
        scaled_quota = int(slot_def["quota"] * quota_scale)
        slot_def_scaled = dict(slot_def)
        slot_def_scaled["quota"] = scaled_quota
        
        text, chars, hits, chunk_ids = search_report_for_slot_v33(
            report_data, slot_def_scaled, used_chunk_ids
        )
        
        has_content = chars > 50
        if has_content:
            required_slots_filled += 1
            used_chunk_ids.update(chunk_ids)
            all_chunk_ids.extend(chunk_ids)
        
        # 记录命中的章节
        secs = set()
        for cid in chunk_ids:
            for item in report_data:
                if item.get("id") == cid or (isinstance(cid, int) and report_data.index(item) == cid):
                    secs.add(str(item.get('section', ''))[:60])
                    break
        
        all_slot_results.append({
            "slot_name": slot_def["name"],
            "required": True,
            "has_content": has_content,
            "char_count": chars,
            "hit_count": hits,
            "chunk_ids": chunk_ids,
            "sections": list(secs),
            "text": text,
        })
        total_chars += chars
    
    # 第二轮：可选槽（用剩余配额）
    remaining_chars = MAX_CONTEXT_CHARS - total_chars
    
    for slot_def in optional_slots:
        if remaining_chars < 200:
            break
        
        available = min(slot_def["quota"], remaining_chars)
        slot_def_scaled = dict(slot_def)
        slot_def_scaled["quota"] = available
        
        text, chars, hits, chunk_ids = search_report_for_slot_v33(
            report_data, slot_def_scaled, used_chunk_ids
        )
        
        has_content = chars > 50
        if has_content:
            used_chunk_ids.update(chunk_ids)
            all_chunk_ids.extend(chunk_ids)
        
        secs = set()
        for cid in chunk_ids:
            for i, item in enumerate(report_data):
                if i == cid or item.get("id") == cid:
                    secs.add(str(item.get('section', ''))[:60])
                    break
        
        all_slot_results.append({
            "slot_name": slot_def["name"],
            "required": False,
            "has_content": has_content,
            "char_count": chars,
            "hit_count": hits,
            "chunk_ids": chunk_ids,
            "sections": list(secs),
            "text": text,
        })
        total_chars += chars
        remaining_chars -= chars
    
    # 组装上下文
    context_parts = []
    for slot in all_slot_results:
        if slot["text"]:
            context_parts.append(slot["text"])
    
    report_context = "\n\n".join(context_parts)
    
    # ===== v3.3 新增：必需证据回溯补充 =====
    # 第一轮提取后，检查哪些必需证据没进入上下文
    # 找到这些证据在报告中的位置，专门补充进去
    requirements = REQUIRED_EVIDENCE.get(question_id, [])
    if requirements:
        ctx_clean = re.sub(r'<[^>]+>', ' ', report_context)
        ctx_clean = re.sub(r'\s+', ' ', ctx_clean)
        
        missing_evidence = []
        for req in requirements:
            pattern = req["pattern"]
            label = req["label"]
            try:
                in_context = bool(re.search(pattern, ctx_clean, re.IGNORECASE))
            except:
                in_context = pattern in ctx_clean
            
            if not in_context:
                # 检查是否为 confirmed_absence
                confirmed_list = CONFIRMED_ABSENCE_STANDARDS.get(question_id, [])
                is_confirmed = any(ca in label or ca in req.get("id", "") for ca in confirmed_list)
                if not is_confirmed:
                    missing_evidence.append(req)
        
        if missing_evidence:
            # 找包含缺失证据的片段，补充关键内容
            supplement_parts = []
            supplement_chars = 0
            supplement_chunk_ids = []
            
            remaining_quota = MAX_CONTEXT_CHARS - len(report_context)
            
            for req in missing_evidence:
                if remaining_quota < 200:
                    break
                
                pattern = req["pattern"]
                label = req["label"]
                
                # 在所有片段中找
                for i, item in enumerate(report_data):
                    chunk_id = item.get("id", i)
                    
                    content = re.sub(r'<[^>]+>', ' ', str(item.get('content', '')))
                    content = re.sub(r'\s+', ' ', content)
                    
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        # 根据剩余配额动态调整提取长度
                        # 剩余多就多取，剩余少就少取（最少 300 字）
                        target_size = min(1000, max(300, remaining_quota - 100))
                        before = target_size // 3
                        after = target_size - before
                        
                        pos = match.start()
                        start = max(0, pos - before)
                        end = min(len(content), pos + after)
                        excerpt = content[start:end]
                        if start > 0:
                            excerpt = "..." + excerpt
                        if end < len(content):
                            excerpt = excerpt + "..."
                        
                        excerpt_chars = len(excerpt)
                        if excerpt_chars <= remaining_quota:
                            sec_name = str(item.get('section', ''))[:40]
                            supplement_parts.append(
                                f"【补充证据·{label}】\n【{sec_name}】\n{excerpt}"
                            )
                            supplement_chars += excerpt_chars
                            supplement_chunk_ids.append(chunk_id)
                            remaining_quota -= excerpt_chars
                            used_chunk_ids.add(chunk_id)
                            all_chunk_ids.append(chunk_id)
                            break  # 每个缺失证据只补一次
            
            if supplement_parts:
                # 补充到上下文末尾
                report_context += "\n\n" + "\n\n".join(supplement_parts)
                
                # 更新总字符数
                total_chars = len(report_context)
    
    # 最终长度检查
    if len(report_context) > MAX_CONTEXT_CHARS:
        report_context = report_context[:MAX_CONTEXT_CHARS] + "\n...（上下文已达长度上限）"
    
    context_hash = hashlib.sha256(report_context.encode("utf-8")).hexdigest()
    
    # 输入门禁：必需证据检查
    required_evidence_hits, evidence_status = check_required_evidence(
        report_data, question_id, report_context
    )
    
    # 综合输入状态
    if evidence_status == "no_requirements":
        # 没有特别定义必需证据，用必填槽判断
        if required_slots_total == 0:
            input_status = "ready"
        elif required_slots_filled == required_slots_total:
            input_status = "ready"
        else:
            input_status = "input_insufficient"
    else:
        input_status = evidence_status
    
    # 报告质量
    if input_status == "ready":
        quality = "good"
    elif required_slots_filled >= required_slots_total * 0.5:
        quality = "partial"
    else:
        quality = "poor"
    
    # 准备证据槽输出（去掉 text）
    evidence_slots = []
    for slot in all_slot_results:
        evidence_slots.append({
            "slot_name": slot["slot_name"],
            "required": slot["required"],
            "has_content": slot["has_content"],
            "char_count": slot["char_count"],
            "hit_count": slot["hit_count"],
            "chunk_ids": slot["chunk_ids"],
            "sections": slot["sections"],
        })
    
    # 生成 input_manifest
    selected_sections = list(set(sec for slot in all_slot_results for sec in slot["sections"]))
    
    input_manifest = {
        "question_id": question_id,
        "project_id": project_id,
        "source_json": report_file or f"{project_id}.json",
        "selected_chunk_ids": sorted(list(set(all_chunk_ids))),
        "selected_sections": selected_sections,
        "char_count": len(report_context),
        "truncated": len(report_context) >= MAX_CONTEXT_CHARS - 100,
        "required_evidence_hits": required_evidence_hits,
        "input_status": input_status,
        "task_module": task_module,
        "context_builder_version": "v3.3",
        "context_hash": context_hash,
        "required_slots_filled": required_slots_filled,
        "required_slots_total": required_slots_total,
        "evidence_slot_count": len(evidence_slots),
    }
    
    return {
        "question_id": question_id,
        "project_id": project_id,
        "report_file": report_file or f"{project_id}.json",
        "task_module": task_module,
        "report_context": report_context,
        "report_context_hash": context_hash,
        "report_quality": quality,
        "input_status": input_status,
        "evidence_slots": evidence_slots,
        "context_builder_version": "v3.3",
        "extraction_rule": "v3.3_evidence_slot_driven + dual_channel_recall + evidence_gate",
        "total_chars": len(report_context),
        "required_slots_filled": required_slots_filled,
        "required_slots_total": required_slots_total,
        "input_manifest": input_manifest,
        "required_evidence_hits": required_evidence_hits,
    }


def _error_result(question_id, project_id, error_code):
    return {
        "question_id": question_id,
        "project_id": project_id,
        "report_file": "",
        "task_module": "unknown",
        "report_context": "",
        "report_context_hash": "",
        "report_quality": "no_report",
        "input_status": error_code,
        "evidence_slots": [],
        "context_builder_version": "v3.3",
        "extraction_rule": "v3.3_evidence_slot_driven",
        "total_chars": 0,
        "required_slots_filled": 0,
        "required_slots_total": 0,
        "input_manifest": {
            "question_id": question_id,
            "input_status": error_code,
        },
        "required_evidence_hits": {},
    }


# 向后兼容
build_context = build_context_v33


def main():
    """快速测试：7道重点题"""
    test_cases = [
        ("PL001_Emission_固体", "PL001", "固体废物控制标准"),
        ("PL005_Emission_固体", "PL005", "固体废物控制标准"),
        ("PL008_VOCSTotal_Q01", "PL008", "VOCs源强与总量数值一致性"),
        ("PL008_VOCSMeasure_Q01", "PL008", "VOCs治理措施一致性"),
        ("PL007_CaptureEfficiency_Q01", "PL007", "废气收集效率"),
        ("PL010_VOCSTotal_Q01", "PL010", "VOCs总量控制与一致性"),
        ("PL014_CaptureAirflow_Q01", "PL014", "废气收集形式与理论排气量"),
    ]
    
    print("v3.3 上下文构建器 - 7题快速测试")
    print("=" * 70)
    
    all_pass = True
    for qid, proj, ttype in test_cases:
        result = build_context_v33(qid, proj, "", ttype)
        status = result["input_status"]
        manifest = result["input_manifest"]
        req_hits = result["required_evidence_hits"]
        
        status_icon = "✅" if status == "ready" else "❌"
        if status != "ready":
            all_pass = False
        
        print(f"\n{status_icon} {qid}")
        print(f"   任务模块: {result['task_module']}")
        print(f"   输入状态: {status}")
        print(f"   上下文: {result['total_chars']} 字")
        print(f"   必填槽: {result['required_slots_filled']}/{result['required_slots_total']}")
        
        if req_hits:
            print(f"   必需证据:")
            for rid, r in req_hits.items():
                if r.get("found_in_context"):
                    icon = "✅📥"
                elif r.get("confirmed_absence"):
                    icon = "🔍确认缺失"
                elif r.get("found_in_report"):
                    icon = "⚠️报告有但未入上下文"
                else:
                    icon = "❌报告无"
                print(f"     {icon} {r['label']} (报告:{r['report_count']}次 / 上下文:{r['context_count']}次)")
    
    print(f"\n{'='*70}")
    print(f"总体: {'全部通过 ✅' if all_pass else '存在未通过项 ❌'}")


if __name__ == "__main__":
    main()
