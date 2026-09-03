#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
证据搜索规范化工具 — v3.4 repair
统一处理标准编号的空格、连字符、全半角等变体
"""
import re
import unicodedata


def normalize_for_evidence_search(text: str) -> str:
    """
    统一规范化：去空格、统一连字符、统一全半角、大写
    
    兼容：
    - GB18599-2020 / GB 18599-2020 / GB 18599—2020
    - GB/T39198-2020 / GB/T 39198-2020
    - 半角、全角空格
    - -, —, –, － 各种连字符
    - 英文字母大小写
    """
    if not text:
        return ""
    value = unicodedata.normalize("NFKC", text or "").upper()
    # 统一各种连字符
    value = value.replace("—", "-").replace("–", "-").replace("－", "-")
    # 全角空格→半角
    value = value.replace("\u3000", " ")
    # 去除所有空白
    value = re.sub(r"\s+", "", value)
    return value


def contains_standard(text: str, standard_id: str) -> bool:
    """规范化后检查标准编号是否存在"""
    return normalize_for_evidence_search(standard_id) in normalize_for_evidence_search(text)


def find_standard_occurrences(text: str, standard_id: str, context_chars: int = 60) -> list:
    """查找标准编号的所有出现位置，返回上下文片段"""
    norm_text = normalize_for_evidence_search(text)
    norm_std = normalize_for_evidence_search(standard_id)
    
    if norm_std not in norm_text:
        return []
    
    results = []
    variants = generate_standard_variants(standard_id)
    
    for variant in variants:
        pos = 0
        text_lower = text.lower()
        variant_lower = variant.lower()
        while True:
            pos = text_lower.find(variant_lower, pos)
            if pos == -1:
                break
            start = max(0, pos - context_chars)
            end = min(len(text), pos + len(variant) + context_chars)
            snippet = re.sub(r"<[^>]+>", " ", text[start:end])
            snippet = re.sub(r"\s+", " ", snippet).strip()
            results.append({
                "variant": variant,
                "char_pos": pos,
                "snippet": snippet[:200],
            })
            pos += len(variant)
    
    return results


def generate_standard_variants(standard_id: str) -> list:
    """生成标准编号的常见变体"""
    variants = set()
    variants.add(standard_id)
    
    # 去空格版本
    no_space = re.sub(r"\s+", "", standard_id)
    variants.add(no_space)
    
    # GB/T 类型
    if "/" in standard_id:
        parts = standard_id.split("/")
        if len(parts) == 2:
            base = parts[0].strip()
            rest = parts[1].strip()
            variants.add(f"{base}/{rest}")
            variants.add(f"{base} / {rest}")
    
    # 连字符变体
    if "-" in standard_id:
        for dash in ["—", "–", "－"]:
            variants.add(standard_id.replace("-", dash))
    
    return list(variants)
