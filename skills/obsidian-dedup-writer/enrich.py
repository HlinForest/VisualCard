"""归一化富化：电话/邮箱 + region/industry/role_type + aliases。支撑“华东地区电脑销售”。"""
import re
from rapidfuzz import fuzz

EAST = {"上海", "江苏", "浙江", "安徽", "福建", "江西", "山东", "杭州", "苏州", "南京", "宁波", "合肥", "福州", "济南", "青岛"}
CITY2REGION = {"上海": "华东", "杭州": "华东", "苏州": "华东", "南京": "华东", "宁波": "华东",
               "合肥": "华东", "福州": "华东", "济南": "华东", "青岛": "华东",
               "北京": "华北", "深圳": "华南", "广州": "华南"}
SALES_WORDS = {"销售", "客户经理", "大客户", "渠道", "商务", "售前", "销售总监"}
COMPUTER_WORDS = {"电脑", "笔记本", "台式", "工作站", "整机", "PC", "服务器"}


def norm_phone(p: str) -> str:
    d = re.sub(r"\D", "", p or "")
    return d[-11:] if len(d) >= 11 else d


def norm_email(e: str) -> str:
    return (e or "").strip().lower()


def region_of(city: str) -> str:
    city = (city or "").strip()
    if city in CITY2REGION:
        return CITY2REGION[city]
    for prov in ["江苏", "浙江", "安徽", "福建", "江西", "山东"]:
        if prov in city:
            return "华东"
    if city in EAST:
        return "华东"
    return ""


def role_type_of(role: str) -> str:
    return "销售" if any(w in (role or "") for w in SALES_WORDS) else ""


def industry_of(hint: str) -> str:
    return "电脑" if any(w in (hint or "") for w in COMPUTER_WORDS) else ""


def enrich(raw: dict, meet_event: str = "", meet_date: str = "") -> dict:
    phones = [norm_phone(p) for p in raw.get("phones", [])]
    phones = [p for p in phones if p]
    emails = [norm_email(e) for e in raw.get("emails", [])]
    emails = [e for e in emails if e]
    name, company = raw.get("name", ""), raw.get("company", "")
    aliases = [a for a in [name, f"{company}{name}" if company and name else ""] if a]
    return {"name": name, "aliases": aliases, "company": company, "role": raw.get("role", ""),
            "role_type": role_type_of(raw.get("role", "")),
            "phones": phones, "emails": emails,
            "region": region_of(raw.get("city", "")),
            "industry": industry_of(raw.get("product_hint", "")),
            "product_keywords": [raw.get("product_hint", "")] if raw.get("product_hint") else [],
            "tags": ["contact"], "meet_event": meet_event, "meet_date": meet_date,
            "career_history": []}


def same_name(a: str, b: str) -> bool:
    return bool(a and b) and (a == b or fuzz.ratio(a, b) >= 90)
