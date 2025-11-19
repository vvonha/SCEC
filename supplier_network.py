from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple
from urllib.parse import quote

import requests

from company_profile import CompanyProfile
from product_source import ProductRecord

logger = logging.getLogger(__name__)

USER_AGENT = "SCEC-Agent/1.0"
SUPPLY_HINTS = ("supplier", "supplies", "module", "contract", "fabricat", "components", "oem", "odm", "foundry")
ALTERNATIVE_HINTS = ("manufacturer", "maker", "producer", "competitor", "rival", "foundry", "builder")

COUNTRY_HINTS: Dict[str, Tuple[str, ...]] = {
    "대한민국": ("south korea", "korea", "seoul", "korean"),
    "일본": ("japan", "japanese", "tokyo", "nagoya"),
    "중국": ("china", "chinese", "beijing", "shanghai", "shenzhen"),
    "대만": ("taiwan", "taipei", "taichung", "kaohsiung"),
    "미국": ("united states", "usa", "u.s.", "american", "california", "texas", "arizona"),
    "독일": ("germany", "german", "berlin", "munich"),
    "프랑스": ("france", "french", "paris"),
    "영국": ("united kingdom", "uk", "britain", "british", "london"),
    "캐나다": ("canada", "canadian", "toronto", "vancouver"),
    "호주": ("australia", "australian", "sydney", "melbourne"),
    "베트남": ("vietnam", "hanoi", "ho chi minh"),
    "인도": ("india", "indian", "bangalore", "new delhi"),
    "멕시코": ("mexico", "mexican", "monterrey"),
    "폴란드": ("poland", "polish", "warsaw"),
    "헝가리": ("hungary", "hungarian", "budapest"),
}


@dataclass
class PartnerRecord:
    name: str
    country: str
    relation: str
    note: str
    source: str
    url: str


def _clean_html_snippet(value: str | None) -> str:
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", text).strip()


def _detect_country(text: str) -> str:
    lowered = text.lower()
    for country, hints in COUNTRY_HINTS.items():
        if any(hint in lowered for hint in hints):
            return country
    return ""


def _wiki_search(query: str, lang: str, limit: int = 6) -> List[dict]:
    url = f"https://{lang}.wikipedia.org/w/rest.php/v1/search/page?q={quote(query)}&limit={limit}"
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        response.raise_for_status()
        payload = response.json()
        return payload.get("pages", [])
    except Exception as exc:  # pragma: no cover - network safety
        logger.warning("Wikipedia search failed for %s (%s): %s", query, lang, exc)
        return []


def _wiki_summary(title: str, lang: str) -> dict:
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if response.status_code != 200:
            return {}
        return response.json()
    except Exception as exc:  # pragma: no cover - network guard
        logger.warning("Wikipedia summary failed for %s (%s): %s", title, lang, exc)
        return {}


def _build_partner(page: dict, relation: str, lang: str) -> PartnerRecord:
    snippet = _clean_html_snippet(page.get("excerpt") or page.get("description"))
    summary = _wiki_summary(page.get("title") or page.get("key", ""), lang)
    description = summary.get("description") or summary.get("extract") or snippet
    note = snippet or description or "세부 설명 없음"
    country = _detect_country(" ".join(filter(None, [note, description])))
    url = summary.get("content_urls", {}).get("desktop", {}).get("page")
    if not url:
        title = quote(page.get("key") or page.get("title", ""))
        url = f"https://{lang}.wikipedia.org/wiki/{title}" if title else ""
    return PartnerRecord(
        name=page.get("title") or page.get("key", "미확인"),
        country=country,
        relation=relation,
        note=note,
        source=f"Wikipedia-{lang}",
        url=url,
    )


def _filter_pages(pages: Iterable[dict], relation: str, keywords: Tuple[str, ...]) -> List[dict]:
    filtered: List[dict] = []
    for page in pages:
        text = _clean_html_snippet(page.get("excerpt") or page.get("description", "")).lower()
        if not any(keyword in text for keyword in keywords):
            continue
        filtered.append(page)
    return filtered


def _merge_partners(candidates: Iterable[PartnerRecord], limit: int) -> List[PartnerRecord]:
    results: List[PartnerRecord] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = candidate.name.lower()
        if not candidate.name or key in seen:
            continue
        seen.add(key)
        results.append(candidate)
        if len(results) >= limit:
            break
    return results


def map_supply_network(
    profile: CompanyProfile, products: List[ProductRecord], max_nodes: int = 6
) -> dict:
    suppliers: List[PartnerRecord] = []
    alternatives: List[PartnerRecord] = []

    product_names = [record.name for record in products[:4] if record.name]
    company_terms = [profile.official_name, profile.query]

    supply_queries: List[Tuple[str, str]] = []
    for term in company_terms:
        if not term:
            continue
        supply_queries.append((f"{term} supplier", "en"))
        supply_queries.append((f"{term} supply chain", "en"))
        supply_queries.append((f"{term} 부품", "ko"))
    for name in product_names:
        supply_queries.append((f"{name} supplier", "en"))
    alt_queries: List[Tuple[str, str]] = []
    for name in product_names:
        alt_queries.append((f"{name} manufacturer", "en"))
        alt_queries.append((f"{name} competitor", "en"))
        alt_queries.append((f"{name} 기업", "ko"))

    for query, lang in supply_queries:
        for page in _filter_pages(_wiki_search(query, lang), "supplier", SUPPLY_HINTS):
            suppliers.append(_build_partner(page, "supplier", lang))
    for query, lang in alt_queries:
        for page in _filter_pages(_wiki_search(query, lang), "alternative", ALTERNATIVE_HINTS):
            alternatives.append(_build_partner(page, "alternative", lang))

    supplier_nodes = _merge_partners(suppliers, max_nodes)
    alternative_nodes = _merge_partners(alternatives, max_nodes)

    lanes: List[str] = []
    for node in supplier_nodes:
        if node.country and profile.region:
            lane = f"{node.country} → {profile.region} ({node.name})"
            if lane not in lanes:
                lanes.append(lane)
    return {
        "suppliers": supplier_nodes,
        "alternatives": alternative_nodes,
        "lanes": lanes,
    }
