from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import get_close_matches
from functools import lru_cache
from typing import List, Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

KIND_URL = "https://kind.krx.co.kr/corpgeneral/corpList.do?method=searchCorpList&currentPageSize=5000"
WIKI_LANG_ORDER = ("ko", "en", "ja", "zh")
LANG_REGION = {
    "ko": "대한민국/국문 위키",
    "ja": "일본 위키", 
    "zh": "중국 위키",
    "en": "글로벌",
}
USER_AGENT = "SCEC-Agent/1.0"


@dataclass
class CompanyProfile:
    query: str
    official_name: str
    industry: str
    products: List[str]
    listing_date: str
    fiscal_month: str
    ceo: str
    region: str
    website: str
    source: str


def _split_products(text: str) -> List[str]:
    if not text:
        return []
    normalized = re.sub(r"\s+", " ", text)
    parts = re.split(r"[,/·;ㆍ|]", normalized)
    cleaned: List[str] = []
    for part in parts:
        item = part.strip()
        if item and item not in cleaned:
            cleaned.append(item)
    return cleaned


def _wiki_summary(term: str, lang: str) -> Optional[dict]:
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(term)}"
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if response.status_code != 200:
            return None
        payload = response.json()
        if payload.get("type") == "https://mediawiki.org/wiki/HyperSwitch/errors/not_found":
            return None
        return payload
    except Exception:
        return None


def _build_wiki_profile(summary: dict, query: str) -> CompanyProfile:
    title = summary.get("title") or query
    description = summary.get("description") or "산업 정보 미확인"
    extract = summary.get("extract") or summary.get("displaytitle") or title
    industry = description.split(",")[0]
    if not industry and extract:
        industry = extract.split(".")[0][:60]
    website = summary.get("content_urls", {}).get("desktop", {}).get("page", "")
    lang = summary.get("lang")
    region = LANG_REGION.get(lang, "글로벌")
    return CompanyProfile(
        query=query,
        official_name=title,
        industry=industry,
        products=[],
        listing_date="-",
        fiscal_month="-",
        ceo="-",
        region=region,
        website=website,
        source="Wikipedia",
    )


@lru_cache(maxsize=1)
def _download_corp_table() -> List[dict]:
    response = requests.get(KIND_URL, timeout=20)
    response.raise_for_status()
    # KIND switched to UTF-8 output in 2024 even though legacy docs still
    # reference EUC-KR. For safety we follow the server-provided encoding and
    # only fall back to requests' chardet guess when it is missing.
    encoding = response.encoding or response.apparent_encoding or "utf-8"
    try:
        response.encoding = encoding
    except LookupError:
        response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("table.list tbody tr")
    records: List[dict] = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 8:
            continue
        homepage_link = cells[6].find("a")
        homepage = ""
        if homepage_link and homepage_link.get("href") and homepage_link.get("href") != "#":
            homepage = homepage_link.get("href").strip()
        else:
            homepage = cells[6].get_text(strip=True)
        record = {
            "name": cells[0].get_text(strip=True).replace("\xa0", " "),
            "industry": cells[1].get_text(strip=True),
            "products": _split_products(cells[2].get_text(strip=True)),
            "listing": cells[3].get_text(strip=True),
            "fiscal": cells[4].get_text(strip=True),
            "ceo": cells[5].get_text(strip=True),
            "website": homepage,
            "region": cells[7].get_text(strip=True),
        }
        records.append(record)
    return records


def _match_kind(name: str) -> Optional[dict]:
    records = _download_corp_table()
    names = [record["name"] for record in records]
    matches = get_close_matches(name.strip(), names, n=1, cutoff=0.4)
    if matches:
        target = matches[0]
        for candidate in records:
            if candidate["name"] == target:
                return candidate
    for candidate in records:
        if name.strip() in candidate["name"]:
            return candidate
    return None


def _build_kind_profile(record: dict, query: str) -> CompanyProfile:
    products = record["products"] or [record["industry"]]
    return CompanyProfile(
        query=query,
        official_name=record["name"],
        industry=record["industry"],
        products=products,
        listing_date=record["listing"],
        fiscal_month=record["fiscal"],
        ceo=record["ceo"],
        region=record["region"],
        website=record["website"],
        source="KIND",
    )


def _lookup_wiki_fallback(name: str) -> Optional[CompanyProfile]:
    for lang in WIKI_LANG_ORDER:
        summary = _wiki_summary(name, lang)
        if summary:
            summary["lang"] = lang
            return _build_wiki_profile(summary, name)
    return None


def lookup_company(name: str) -> Optional[CompanyProfile]:
    if not name:
        return None
    record = _match_kind(name)
    if record:
        return _build_kind_profile(record, name)
    return _lookup_wiki_fallback(name)
