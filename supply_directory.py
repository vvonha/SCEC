from __future__ import annotations

from typing import Dict

CATEGORY_SUPPLY_DIRECTORY: Dict[str, dict] = {
    "반도체/전자": {
        "suppliers": [
            "ASML (네덜란드) – EUV/DUV 노광 장비 유지보수",
            "Tokyo Electron (일본) – 증착·식각 라인 장비",
            "SUMCO (일본) – 300mm 실리콘 웨이퍼",
            "TSMC (대만) – 첨단 파운드리 공동개발",
            "Applied Materials (미국) – 공정 장비·서비스",
        ],
        "alternatives": [
            "GlobalFoundries (미국) – 12/14nm 파운드리",
            "UMC (대만) – 범용 파운드리",
            "Micron (미국) – 메모리 전략 제휴",
            "SMIC (중국) – 레거시 공정 백업",
        ],
        "routes": [
            "네덜란드 스키폴 → 인천 항공 화물 (장비/부품)",
            "도쿄/나고야 → 부산 해상 LCL",
            "타이베이 → 김포/인천 반도체 전용 항공",
        ],
        "alerts": [
            "미·중 첨단 칩 수출통제, 일본 포토레지스트 라이선스",
        ],
    },
    "배터리/전지": {
        "suppliers": [
            "Albemarle (미국) – 리튬 정제",
            "SQM (칠레) – 염호 리튬",
            "POSCO Future M (한국) – 양극재",
            "CATL (중국) – 배터리 셀 공급·기술교류",
            "EcoPro BM (한국) – 하이니켈 양극재",
        ],
        "alternatives": [
            "LG Energy Solution Poland – 유럽 팩 공급",
            "Northvolt (스웨덴) – 프리미엄 배터리",
            "AESC (일본/미국) – OEM 팩",
            "BYD (중국) – LFP 셀",
        ],
        "routes": [
            "칠레 안토파가스타 → 광양 벌크선",
            "상하이 → 울산/부산 컨테이너 (셀/소재)",
            "폴란드 브로츠와프 → 유럽 OEM 철도",
        ],
        "alerts": [
            "IRA 북미 조립 요건, 중국 흑연 수출허가",
        ],
    },
    "모빌리티/자동차": {
        "suppliers": [
            "Aptiv (멕시코/폴란드) – 와이어 하네스",
            "Bosch (독일) – 전장/ADAS",
            "Denso (일본) – 파워트레인/반도체",
            "CATL (중국) – EV 배터리",
            "Hyundai Mobis (한국) – 모듈",
        ],
        "alternatives": [
            "Magna (캐나다) – 전장·차체",
            "Valeo (프랑스) – ADAS 대체",
            "Jabil (태국/말레이시아) – 전장 EMS",
            "VinFast Suppliers (베트남) – KD 모듈",
        ],
        "routes": [
            "멕시코 → 부산/광양 Ro-Ro",
            "독일 → 평택 CKD 물류",
            "태국 → 인천 항공 긴급 운송",
        ],
        "alerts": [
            "러-우 전쟁으로 철강/와이어 공급 변동",
        ],
    },
    "정밀화학/소재": {
        "suppliers": [
            "Shin-Etsu Chemical (일본) – 불화수소/포토레지스트",
            "JSR Corporation (일본) – CMP 슬러리",
            "BASF (독일) – 촉매/용제",
            "LOTTE Fine Chemical (한국) – 고순도 소재",
        ],
        "alternatives": [
            "Merck Group (독일) – 전자 소재",
            "Entegris (미국) – 특수가스",
            "Mitsubishi Chemical (일본) – 필름",
            "OCI Company (한국) – 폴리실리콘",
        ],
        "routes": [
            "나고야 → 울산 벌크 화학",
            "프랑크푸르트 → 인천 항공 위험물",
        ],
        "alerts": [
            "중동 정세에 따른 나프타/에너지 변동",
        ],
    },
    "통신/IT 서비스": {
        "suppliers": [
            "Cisco (미국) – 네트워크 장비",
            "Nokia (핀란드) – 5G 장비",
            "Samsung SDS (한국) – 클라우드/물류 IT",
            "Equinix (미국) – 데이터센터 파트너",
        ],
        "alternatives": [
            "Huawei (중국) – 통신 장비",
            "Rakuten Symphony (일본) – Open RAN",
            "Tata Communications (인도) – 글로벌 회선",
        ],
        "routes": [
            "미국 서부 → 서울 해저케이블",
            "싱가포르 → 부산 케이블 육상 연결",
        ],
        "alerts": [
            "미·중 기술 분쟁, 데이터 현지화 규제",
        ],
    },
}

DEFAULT_DIRECTORY = {
    "suppliers": ["지역별 전략 협력사 발굴 필요"],
    "alternatives": ["동남아·중동 신규 제조사 탐색"],
    "routes": ["복합 운송 루트 TBD"],
    "alerts": ["주요 거점의 정치/물류 리스크 점검"],
}


def lookup_category_directory(category: str) -> dict:
    return CATEGORY_SUPPLY_DIRECTORY.get(category, DEFAULT_DIRECTORY)
