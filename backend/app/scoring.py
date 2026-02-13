from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re
from typing import Iterable


FIT_KEYWORDS = {
    "interior": 8,
    "interior design": 10,
    "lighting": 8,
    "furniture": 8,
    "decor": 6,
    "staging": 9,
    "hospitality": 9,
    "architecture": 6,
    "ffe": 10,
    "procurement": 9,
    "model home": 9,
}

INTENT_KEYWORDS = {
    "vendor": 4,
    "sourcing": 4,
    "preferred vendor": 5,
    "specifies": 3,
    "centralized furnishing": 5,
    "recurring": 4,
    "bundle": 3,
    "qualification": 3,
}

NEGATIVE_KEYWORDS = {
    "auto": -10,
    "automotive": -10,
    "dental": -10,
    "landscaping": -8,
    "maintenance": -7,
    "events": -5,
}

SERVICE_BONUS = {
    "interior design": 8,
    "lighting design": 8,
    "furniture procurement": 10,
    "ffe consulting": 10,
    "staging": 7,
    "hospitality design": 8,
    "interior architecture": 8,
}


@dataclass
class ScoreBreakdown:
    industry_fit: int
    product_match: int
    digital_signal: int
    scale_signal: int
    intent_signal: int
    penalties: int

    @property
    def total(self) -> int:
        raw = (
            self.industry_fit
            + self.product_match
            + self.digital_signal
            + self.scale_signal
            + self.intent_signal
            + self.penalties
        )
        return max(0, min(100, raw))


def normalize_text(*parts: str) -> str:
    return " ".join((p or "").strip().lower() for p in parts if p).strip()


def parse_services(raw: str) -> list[str]:
    return [s.strip().lower() for s in (raw or "").split(";") if s.strip()]


def contains_keyword(text: str, keyword: str) -> bool:
    if " " in keyword:
        return keyword in text
    pattern = rf"\b{re.escape(keyword)}\b"
    return re.search(pattern, text) is not None


def keyword_points(text: str, mapping: dict[str, int], cap: int) -> int:
    points = 0
    for key, weight in mapping.items():
        if contains_keyword(text, key):
            points += weight
    return min(cap, points)


def to_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def choose_tier(score: int) -> str:
    if score >= 75:
        return "A"
    if score >= 55:
        return "B"
    return "C"


def pick_offer_angle(text: str, language: str = "EN") -> str:
    cn = language.upper() == "CN"

    if "hospitality" in text or "hotel" in text:
        return "酒店与商业空间 FF&E 配套，支持多项目复用" if cn else "a hospitality FF&E package with repeat property rollout"
    if "staging" in text or "model home" in text:
        return "高周转样板间/软装组合，支持稳定补货" if cn else "fast-turn staging bundles with predictable replenishment"
    if "lighting" in text:
        return "灯具与家具一体化组合方案，保证风格一致" if cn else "lighting-plus-furniture bundles for cohesive project design"
    return "可落地的批发价格与家具/灯具组合采购方案" if cn else "trade pricing and curated furniture/lighting bundles"


def template_outreach(company: str, city: str, angle: str, brand_name: str, language: str = "EN") -> tuple[str, str]:
    if language.upper() == "CN":
        subject = f"{company}：家具与灯具 B2B 供货合作建议"
        body = (
            f"{company} 团队您好，\n\n"
            f"我关注到你们在 {city} 的项目，想分享一个合作思路：{brand_name} 可以通过“{angle}”支持你们的交付。"
            "我们专注中高端家具与灯具，可按你们常见项目类型做组合打包与标准化供货。\n\n"
            "如果方便，我可以先发一版样例方案和价格结构，供你们快速评估。\n\n"
            "谢谢，\n"
            "Alan"
        )
        return subject, body

    subject = f"{company}: B2B furniture + lighting sourcing idea"
    body = (
        f"Hi {company} team,\n\n"
        f"I noticed your work in {city} and wanted to share a quick idea: {brand_name} can support your projects through {angle}. "
        "We focus on mid-to-high-end furniture and lighting, and can package products around your typical project needs.\n\n"
        "If useful, I can send a short sample package and pricing structure for one project type you handle most often.\n\n"
        "Best,\n"
        "Alan"
    )
    return subject, body


def score_row(row: dict[str, str], target_states: Iterable[str], language: str = "EN") -> tuple[ScoreBreakdown, list[str], str]:
    description = row.get("description", "")
    services = row.get("services", "")
    text = normalize_text(description, services)
    service_list = parse_services(services)

    industry_fit = keyword_points(text, FIT_KEYWORDS, cap=40)

    product_match = 0
    if "lighting" in text:
        product_match += 10
    if "furniture" in text:
        product_match += 10
    if "decor" in text:
        product_match += 4
    product_match = min(20, product_match)

    has_website = 1 if row.get("website", "").startswith("http") else 0
    has_trade = 1 if row.get("has_trade_program", "").strip().lower() == "yes" else 0
    has_procurement = 1 if row.get("has_procurement_page", "").strip().lower() == "yes" else 0
    digital_signal = min(15, has_website * 5 + has_trade * 5 + has_procurement * 5)

    employees = to_int(row.get("employee_estimate", "0"))
    projects = to_int(row.get("project_count", "0"))

    scale_signal = 0
    if 10 <= employees <= 80:
        scale_signal += 8
    elif employees > 80:
        scale_signal += 5

    if projects >= 100:
        scale_signal += 7
    elif projects >= 60:
        scale_signal += 4
    scale_signal = min(15, scale_signal)

    if target_states and row.get("state", "").upper() in target_states:
        scale_signal = min(15, scale_signal + 2)

    intent_signal = keyword_points(text, INTENT_KEYWORDS, cap=10)
    penalties = keyword_points(text, NEGATIVE_KEYWORDS, cap=0)

    for service, bonus in SERVICE_BONUS.items():
        if service in service_list:
            industry_fit = min(40, industry_fit + bonus)

    cn = language.upper() == "CN"

    reasons: list[str] = []
    if industry_fit >= 26:
        reasons.append("行业匹配度高（设计/FF&E/软装）" if cn else "Strong vertical fit (design/FF&E/staging)")
    if product_match >= 14:
        reasons.append("与家具/灯具需求高度相关" if cn else "Clear furniture/lighting relevance")
    if digital_signal >= 10:
        reasons.append("数字化采购信号明确（trade/procurement 页面）" if cn else "Good digital buying signals (trade/procurement pages)")
    if intent_signal >= 6:
        reasons.append("采购意向信号强（在找供应商）" if cn else "Intent signals suggest active vendor sourcing")
    if penalties < 0:
        reasons.append("存在低相关业务信号" if cn else "Contains low-relevance business signals")

    return (
        ScoreBreakdown(
            industry_fit=industry_fit,
            product_match=product_match,
            digital_signal=digital_signal,
            scale_signal=scale_signal,
            intent_signal=intent_signal,
            penalties=penalties,
        ),
        reasons,
        text,
    )


def summarize_state_tiers(states: list[str]) -> list[dict[str, int]]:
    counter = Counter(states)
    return [{state: count} for state, count in counter.most_common(5)]
