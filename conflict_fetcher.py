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


def fetch_guardian_headlines(limit: int = 25) -> List[str]:
    url = "https://www.theguardian.com/world/rss"
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


def fetch_dw_headlines(limit: int = 25) -> List[str]:
    url = "https://rss.dw.com/rdf/rss-en-all"
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


def fetch_nyt_headlines(limit: int = 25) -> List[str]:
    url = "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
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


def fetch_voa_headlines(limit: int = 25) -> List[str]:
    url = "https://www.voanews.com/rss"
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


def fetch_cnn_headlines(limit: int = 25) -> List[str]:
    url = "https://rss.cnn.com/rss/edition_world.rss"
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


def fetch_npr_headlines(limit: int = 25) -> List[str]:
    url = "https://www.npr.org/rss/rss.php?id=1004"
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


def fetch_sky_headlines(limit: int = 25) -> List[str]:
    url = "https://feeds.skynews.com/feeds/rss/world.xml"
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


def fetch_nhk_headlines(limit: int = 25) -> List[str]:
    url = "https://www3.nhk.or.jp/rss/news/cat0.xml"
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


CURATED_CONFLICTS: List[dict] = [
    {
        "pair": "중국–대만",
        "source": "지정학 라이브러리",
        "headline": "대만해협 군사훈련으로 파운드리·서플라이 체인 차질 위험이 상시 존재합니다.",
    },
    {
        "pair": "중국–일본",
        "source": "지정학 라이브러리",
        "headline": "희토류/정밀부품 수출 허가 이슈로 한중일 제조업에 영향.",
    },
    {
        "pair": "미국–중국",
        "source": "지정학 라이브러리",
        "headline": "첨단 반도체 및 AI 칩 수출 통제가 확대되고 있습니다.",
    },
    {
        "pair": "러시아–우크라이나",
        "source": "지정학 라이브러리",
        "headline": "전쟁 장기화로 에너지·곡물·네온가스 공급 제약이 지속됩니다.",
    },
    {
        "pair": "이스라엘–팔레스타인",
        "source": "지정학 라이브러리",
        "headline": "가자지구 충돌이 중동 물류와 석유/가스 공급망에 파급.",
    },
    {
        "pair": "인도–중국",
        "source": "지정학 라이브러리",
        "headline": "히말라야 국경 마찰과 희토류/배터리 원료 경쟁이 격화.",
    },
]


def gather_conflict_pairs(max_pairs: int = 8) -> List[dict]:
    candidates: List[dict] = []
    seen_pairs = set()

    feeds = [
        (fetch_reddit_headlines, "Reddit r/worldnews"),
        (fetch_bbc_headlines, "BBC World RSS"),
        (fetch_reuters_headlines, "Reuters World"),
        (fetch_ap_headlines, "AP International"),
        (fetch_aljazeera_headlines, "Al Jazeera"),
        (fetch_yonhap_headlines, "Yonhap News"),
        (fetch_guardian_headlines, "The Guardian"),
        (fetch_dw_headlines, "Deutsche Welle"),
        (fetch_nyt_headlines, "New York Times World"),
        (fetch_voa_headlines, "VOA World"),
        (fetch_cnn_headlines, "CNN World"),
        (fetch_npr_headlines, "NPR World"),
        (fetch_sky_headlines, "Sky News World"),
        (fetch_nhk_headlines, "NHK World"),
    ]

    for fetcher, label in feeds:
        for headline in fetcher():
            for entry in _headline_pairs(headline, label):
                if entry["pair"] in seen_pairs:
                    continue
                candidates.append(entry)
                seen_pairs.add(entry["pair"])
                if len(candidates) >= max_pairs:
                    break
        if len(candidates) >= max_pairs:
            break

    for entry in CURATED_CONFLICTS:
        if len(candidates) >= max_pairs:
            break
        if entry["pair"] in seen_pairs:
            continue
        candidates.append(entry)
        seen_pairs.add(entry["pair"])

    if candidates:
        return candidates[:max_pairs]

    return CURATED_CONFLICTS[:max_pairs]
