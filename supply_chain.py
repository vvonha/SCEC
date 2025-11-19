from __future__ import annotations

from typing import Dict, List

GEO_KEYWORDS: Dict[str, List[str]] = {
    "중국": ["중국", "china", "prc", "상하이", "베이징"],
    "일본": ["일본", "japan", "tokyo", "nagoya"],
    "미국": ["미국", "usa", "u.s.", "silicon valley", "캘리포니아", "texas"],
    "유럽": ["유럽", "europe", "eu", "독일", "france", "uk"],
    "대만": ["대만", "taiwan", "tsmc", "taipei"],
    "베트남": ["베트남", "vietnam", "호치민"],
    "인도": ["인도", "india", "bangalore"],
    "중동": ["uae", "사우디", "중동", "카타르", "사우디아라비아"],
}

SUPPLY_CHAIN_BLUEPRINTS: Dict[str, dict] = {
    "반도체/전자": {
        "imports": ["일본 포토레지스트", "네덜란드/미국 리소그래피 장비", "대만 웨이퍼 파운드리"],
        "exports": ["중국·베트남 세트 메이커", "미국/유럽 데이터센터"],
        "logistics": ["인천-닝보 컨테이너", "김해-산호세 항공 화물"],
        "alerts": ["미국 대중 수출 규제", "중국 희토류 통제"],
    },
    "배터리/전지": {
        "imports": ["호주·칠레 리튬", "콩고 코발트", "중국 흑연"],
        "exports": ["북미/유럽 완성차 OEM", "중국 ESS 벤더"],
        "logistics": ["광양-상하이 벌크선", "울산-헝가리 철도"],
        "alerts": ["IRA 북미 조립 요건", "중국 흑연 수출허가"],
    },
    "모빌리티/자동차": {
        "imports": ["일본 정밀부품", "중국 와이어하네스", "멕시코 전장"],
        "exports": ["북미/유럽 판매법인", "중동 조립 KD"],
        "logistics": ["평택-로테르담 선적", "광양-엘에이 Ro-Ro"],
        "alerts": ["러-우 전쟁으로 철강/와이어 공급 차질", "중국 전력 제한"],
    },
    "정밀화학/소재": {
        "imports": ["중동 나프타", "일본 고순도 화학", "중국 불화수소"],
        "exports": ["한국/중국 반도체 공정사", "유럽 전기차 소재"],
        "logistics": ["여수-사우디 유조선", "울산-나고야 벌크"],
        "alerts": ["중동 정세로 인한 유가 변동", "일본 수출허가"],
    },
    "통신/IT 서비스": {
        "imports": ["미국 GPU", "핀란드 통신 장비", "대만 서버"],
        "exports": ["글로벌 클라우드 고객", "동남아 통신사"],
        "logistics": ["해저케이블 백홀", "싱가포르 데이터센터 링크"],
        "alerts": ["미·중 기술 분쟁", "해저케이블 단절 위험"],
    },
    "바이오/제약": {
        "imports": ["인도 API", "미국 임상시약", "유럽 완제 설비"],
        "exports": ["미국 FDA 시장", "중국 위탁생산"],
        "logistics": ["인천-멤피스 항공 콜드체인", "부산-로테르담 냉장"],
        "alerts": ["FDA/EMA 규제", "중국 봉쇄로 임상 지연"],
    },
    "철강/소재": {
        "imports": ["호주 철광석", "브라질 펠릿", "러시아 코크스"],
        "exports": ["동남아 조선사", "미국 건설/에너지"],
        "logistics": ["포항-상하이 벌크", "광양-시애틀 컨테이너"],
        "alerts": ["러-우 전쟁 운임 급등", "중국 감산"],
    },
}

DEFAULT_BLUEPRINT = {
    "imports": ["글로벌 원자재 스팟 구매"],
    "exports": ["주요 고객사 다변화 필요"],
    "logistics": ["해상/항공 복합"],
    "alerts": ["거시적 환율/물류 리스크"]
}


def _geo_mentions(text: str) -> List[str]:
    normalized = text.lower()
    found: List[str] = []
    for geo, hints in GEO_KEYWORDS.items():
        if any(hint.lower() in normalized for hint in hints):
            found.append(geo)
    return found


def build_supply_chain_overlay(category: str, evidence: str) -> dict:
    blueprint = SUPPLY_CHAIN_BLUEPRINTS.get(category, DEFAULT_BLUEPRINT)
    overlay = {key: list(values) for key, values in blueprint.items()}
    mentions = _geo_mentions(evidence)
    if mentions:
        for geo in mentions:
            overlay.setdefault("alerts", []).append(f"{geo} 관련 현지 규제/물류 체크 필요")
            overlay.setdefault("exports", []).append(f"{geo}향 매출 계약 모니터링")
    for key in ("imports", "exports", "logistics", "alerts"):
        unique: List[str] = []
        for item in overlay.get(key, []):
            if item not in unique:
                unique.append(item)
        overlay[key] = unique
    return overlay
