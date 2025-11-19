from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import get_close_matches
from functools import lru_cache
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

KIND_URL = "https://kind.krx.co.kr/corpgeneral/corpList.do?method=searchCorpList&currentPageSize=5000"


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


@lru_cache(maxsize=1)
def _download_corp_table() -> List[dict]:
    response = requests.get(KIND_URL, timeout=20)
    response.raise_for_status()
    response.encoding = "euc-kr"
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


def lookup_company(name: str) -> Optional[CompanyProfile]:
    if not name:
        return None
    records = _download_corp_table()
    names = [record["name"] for record in records]
    matches = get_close_matches(name.strip(), names, n=1, cutoff=0.4)
    record: Optional[dict] = None
    if matches:
        target = matches[0]
        for candidate in records:
            if candidate["name"] == target:
                record = candidate
                break
    else:
        for candidate in records:
            if name.strip() in candidate["name"]:
                record = candidate
                break
    if not record:
        return None
    products = record["products"] or [record["industry"]]
    return CompanyProfile(
        query=name,
        official_name=record["name"],
        industry=record["industry"],
        products=products,
        listing_date=record["listing"],
        fiscal_month=record["fiscal"],
        ceo=record["ceo"],
        region=record["region"],
        website=record["website"],
    )
