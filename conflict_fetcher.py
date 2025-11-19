from __future__ import annotations

import logging
from typing import Dict, List, Sequence
from xml.etree import ElementTree

import requests

logger = logging.getLogger(__name__)

COUNTRY_KEYWORDS: Dict[str, Sequence[str]] = {
    "중국": ("china", "chinese", "beijing", "prc"),
    "일본": ("japan", "japanese", "tokyo"),
    "미국": ("united states", "u.s.", "us ", "usa", "american", "washington"),
    "러시아": ("russia", "russian", "moscow"),
    "우크라이나": ("ukraine", "ukrainian", "kyiv", "kiev"),
    "이스라엘": ("israel", "israeli"),
    "팔레스타인": ("palestine", "palestinian", "gaza", "west bank"),
    "이란": ("iran", "iranian", "tehran"),
    "대만": ("taiwan", "taipei", "taiwanese"),
    "북한": ("north korea", "dprk", "pyongyang"),
    "대한민국": ("south korea", "seoul", "republic of korea", "south korean"),
    "인도": ("india", "indian", "new delhi"),
    "파키스탄": ("pakistan", "pakistani", "islamabad"),
    "베트남": ("vietnam", "vietnamese", "hanoi"),
    "필리핀": ("philippines", "philippine", "manila"),
    "사우디아라비아": ("saudi", "riyadh", "saudi arabia"),
    "예멘": ("yemen", "yemeni"),
    "시리아": ("syria", "syrian", "damascus"),
    "이라크": ("iraq", "iraqi", "baghdad"),
    "터키": ("turkey", "turkish", "ankara"),
    "아르메니아": ("armenia", "armenian"),
    "아제르바이잔": ("azerbaijan", "azerbaijani", "baku"),
    "프랑스": ("france", "french", "paris"),
    "독일": ("germany", "german", "berlin"),
    "영국": ("britain", "british", "united kingdom", "uk ", "london"),
    "EU": ("eu ", "european union", "brussels"),
}


def _get_json(url: str, headers: Dict[str, str]) -> Dict:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as exc:  # pragma: no cover - defensive network handling
        logger.warning("Failed to fetch JSON from %s: %s", url, exc)
        return {}


def _get_xml(url: str) -> ElementTree.Element | None:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return ElementTree.fromstring(response.content)
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to fetch XML from %s: %s", url, exc)
        return None


def _extract_countries(text: str) -> List[str]:
    normalized = text.lower()
    matches: List[str] = []
    for country, keywords in COUNTRY_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            matches.append(country)
    deduped: List[str] = []
    for country in matches:
        if country not in deduped:
            deduped.append(country)
        if len(deduped) == 3:
            break
    return deduped


def _headline_pairs(headline: str, source: str) -> List[dict]:
    countries = _extract_countries(headline)
    if len(countries) < 2:
        return []
    pair = "–".join(sorted(countries[:2]))
    return [{"pair": pair, "source": source, "headline": headline}]


def fetch_reddit_headlines(limit: int = 25) -> List[str]:
    url = "https://www.reddit.com/r/worldnews/.json"
    payload = _get_json(url, headers={"User-Agent": "SCEC-Agent/1.0"})
    headlines: List[str] = []
    children = payload.get("data", {}).get("children", [])
    for child in children[:limit]:
        title = child.get("data", {}).get("title")
        if title:
            headlines.append(title)
    return headlines


def fetch_bbc_headlines(limit: int = 25) -> List[str]:
    url = "https://feeds.bbci.co.uk/news/world/rss.xml"
    root = _get_xml(url)
    if root is None:
        return []
    headlines: List[str] = []
    for item in root.findall(".//item"):
        title = item.findtext("title")
        if title:
            headlines.append(title)
        if len(headlines) >= limit:
            break
    return headlines


def fetch_reuters_headlines(limit: int = 25) -> List[str]:
    url = "https://www.reuters.com/world/rss"
    root = _get_xml(url)
    if root is None:
        return []
    headlines: List[str] = []
    for item in root.findall(".//item"):
        title = item.findtext("title")
        if title:
            headlines.append(title)
        if len(headlines) >= limit:
            break
    return headlines


def fetch_ap_headlines(limit: int = 25) -> List[str]:
    url = "https://apnews.com/hub/apf-intlnews?format=xml"
    root = _get_xml(url)
    if root is None:
        return []
    headlines: List[str] = []
    for item in root.findall(".//item"):
        title = item.findtext("title")
        if title:
            headlines.append(title)
        if len(headlines) >= limit:
            break
    return headlines


def fetch_aljazeera_headlines(limit: int = 25) -> List[str]:
    url = "https://www.aljazeera.com/xml/rss/all.xml"
    root = _get_xml(url)
    if root is None:
        return []
    headlines: List[str] = []
    for item in root.findall(".//item"):
        title = item.findtext("title")
        if title:
            headlines.append(title)
        if len(headlines) >= limit:
            break
    return headlines


def fetch_yonhap_headlines(limit: int = 25) -> List[str]:
    url = "https://en.yna.co.kr/RSS/news060601.xml"
    root = _get_xml(url)
    if root is None:
        return []
    headlines: List[str] = []
    for item in root.findall(".//item"):
        title = item.findtext("title")
        if title:
            headlines.append(title)
        if len(headlines) >= limit:
            break
    return headlines


def gather_conflict_pairs(max_pairs: int = 6) -> List[dict]:
    candidates: List[dict] = []
    seen_pairs = set()

    feeds = [
        (fetch_reddit_headlines, "Reddit r/worldnews"),
        (fetch_bbc_headlines, "BBC World RSS"),
        (fetch_reuters_headlines, "Reuters World"),
        (fetch_ap_headlines, "AP International"),
        (fetch_aljazeera_headlines, "Al Jazeera"),
        (fetch_yonhap_headlines, "Yonhap News"),
    ]

    for fetcher, label in feeds:
        for headline in fetcher():
            for entry in _headline_pairs(headline, label):
                if entry["pair"] in seen_pairs:
                    continue
                candidates.append(entry)
                seen_pairs.add(entry["pair"])
                if len(candidates) >= max_pairs:
                    return candidates

    if candidates:
        return candidates

    return [
        {
            "pair": "중국–일본",
            "source": "Fallback",
            "headline": "네트워크 오류로 최신 데이터를 가져오지 못했습니다.",
        }
    ]
