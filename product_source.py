from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from company_profile import CompanyProfile

logger = logging.getLogger(__name__)

USER_AGENT = "SCEC-Agent/1.0"
WIKI_SECTION_KEYWORDS = ("사업", "제품", "서비스", "생산", "사업부", "라인업", "공급", "Solution")
WIKI_LANGS = ("ko", "en", "ja", "zh")


@dataclass
class ProductRecord:
    name: str
    source: str
    evidence: str


def _clean(text: str) -> str:
    return " ".join(text.split())


def _wiki_summary(term: str, lang: str) -> Optional[dict]:
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(term)}"
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception as exc:  # pragma: no cover - network guard
        logger.warning("Failed to fetch wikipedia summary for %s: %s", term, exc)
        return None


def _wiki_mobile_html(title: str, lang: str) -> Optional[str]:
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/mobile-html/{quote(title)}"
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if response.status_code != 200:
            return None
        return response.text
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to fetch wikipedia HTML for %s: %s", title, exc)
        return None


def _extract_wiki_items(html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    items: List[str] = []
    for section in soup.select("section"):
        heading = section.find(["h2", "h3", "h4"])
        heading_text = heading.get_text(strip=True) if heading else ""
        if not heading_text:
            continue
        if not any(keyword in heading_text for keyword in WIKI_SECTION_KEYWORDS):
            continue
        for li in section.find_all("li"):
            text = _clean(li.get_text(" ", strip=True))
            if len(text) < 5 or len(text) > 160:
                continue
            if text in items:
                continue
            items.append(text)
            if len(items) >= 20:
                return items
    return items


def _summarize_item(text: str) -> tuple[str, str]:
    for separator in (":", "-", "–", "—"):
        if separator in text:
            head, tail = text.split(separator, 1)
            head = head.strip()
            if head:
                return head, text
    snippet = text.split("(")[0].strip()
    if len(snippet) > 60:
        snippet = snippet[:60] + "…"
    return snippet or text[:60], text


def _wiki_records(profile: CompanyProfile) -> List[ProductRecord]:
    candidates = []
    if profile.official_name:
        candidates.append(profile.official_name)
    if profile.query and profile.query not in candidates:
        candidates.append(profile.query)
    for candidate in candidates:
        for lang in WIKI_LANGS:
            summary = _wiki_summary(candidate, lang)
            if not summary:
                continue
            title = summary.get("title") or candidate
            html = _wiki_mobile_html(title, lang)
            if not html:
                continue
            entries = _extract_wiki_items(html)
            if not entries:
                continue
            records: List[ProductRecord] = []
            for entry in entries[:12]:
                name, evidence = _summarize_item(entry)
                records.append(
                    ProductRecord(
                        name=name,
                        source=f"Wikipedia-{lang}",
                        evidence=evidence,
                    )
                )
            if records:
                return records
    return []


def gather_product_records(profile: CompanyProfile) -> List[ProductRecord]:
    records: List[ProductRecord] = []
    seen: set[str] = set()

    for product in profile.products:
        cleaned = _clean(product)
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        records.append(
            ProductRecord(
                name=cleaned,
                source="KIND",
                evidence=f"KRX KIND 주요제품: {cleaned}",
            )
        )

    wiki_records = _wiki_records(profile)
    for record in wiki_records:
        if record.name in seen:
            continue
        seen.add(record.name)
        records.append(record)

    return records
