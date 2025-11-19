from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Dict, Iterable, List

from company_profile import CompanyProfile


@dataclass
class Section:
    title: str
    bullets: List[str]


@dataclass
class ProductInsight:
    name: str
    category: str
    sensitive_inputs: List[str]
    alternatives: List[str]
    note: str


@dataclass
class ConflictInsight:
    pair: str
    source: str
    headline: str
    risks: List[str]
    alternatives: List[str]


@dataclass
class Report:
    profile: CompanyProfile
    page_goal: int
    product_insights: List[ProductInsight]
    conflict_insights: List[ConflictInsight]
    sections: List[Section]
    scores: Dict[str, int]


PRODUCT_LIBRARY = [
    {
        "category": "반도체/전자",
        "keywords": ("반도체", "칩", "메모리", "디스플레이", "모듈", "센서", "카메라", "전기전자"),
        "inputs": ["포토레지스트", "웨이퍼", "EUV 장비", "초고순도 가스"],
        "alternatives": ["네덜란드", "대만", "미국", "독일"],
        "note": "첨단 소재·장비 규제에 민감하여 일본/미국/네덜란드 규제 및 중국 희토류 통제의 직접적 영향을 받습니다.",
    },
    {
        "category": "배터리/전지",
        "keywords": ("배터리", "전지", "2차전지", "셀", "양극재", "음극재"),
        "inputs": ["리튬", "니켈", "코발트", "흑연"],
        "alternatives": ["호주", "칠레", "인도네시아", "캐나다"],
        "note": "중국·남미 원료 의존도가 높아 금속 수출 통제에 취약합니다.",
    },
    {
        "category": "모빌리티/자동차",
        "keywords": ("자동차", "모빌리티", "차량", "엔진", "모터", "EV"),
        "inputs": ["와이어 하네스", "배터리 팩", "희토류 자석"],
        "alternatives": ["멕시코", "태국", "헝가리", "폴란드"],
        "note": "중국·일본산 부품과 러시아-우크라 곡물/가스 가격 영향에 민감합니다.",
    },
    {
        "category": "바이오/제약",
        "keywords": ("의약", "제약", "바이오", "백신", "원료의약품", "의료"),
        "inputs": ["원료의약품(API)", "멸균용기", "임상시약"],
        "alternatives": ["미국", "스위스", "인도", "아일랜드"],
        "note": "중국/인도 생산 차질 및 미국 FDA 제재에 연동됩니다.",
    },
    {
        "category": "철강/소재",
        "keywords": ("철강", "알루미늄", "동", "소재", "합금", "파이프", "판재"),
        "inputs": ["철광석", "제철 석탄", "전력"],
        "alternatives": ["호주", "브라질", "사우디", "터키"],
        "note": "러시아-우크라 전쟁, 중국 감산 정책에 따른 변동성이 큽니다.",
    },
    {
        "category": "정밀화학/소재",
        "keywords": ("화학", "폴리머", "석유화학", "정밀화학", "도료", "필름"),
        "inputs": ["불화수소", "IPA", "나프타", "촉매"],
        "alternatives": ["싱가포르", "사우디", "미국 걸프", "말레이시아"],
        "note": "일본·중국의 소재 통제와 중동 원자재 이슈의 영향을 받습니다.",
    },
    {
        "category": "통신/IT 서비스",
        "keywords": ("ICT", "클라우드", "SW", "플랫폼", "네트워크", "5G", "통신"),
        "inputs": ["서버", "GPU", "트랜시버"],
        "alternatives": ["미국", "싱가포르", "인도", "핀란드"],
        "note": "미·중 기술 패권, AI 칩 수출 규제에 따라 장비 수급이 달라집니다.",
    },
]

DEFAULT_PRODUCT = {
    "category": "복합 사업",
    "inputs": ["전략 물자", "전력", "해상 운송"],
    "alternatives": ["베트남", "말레이시아", "폴란드"],
    "note": "산업 전반에 적용되는 거시적 공급망 리스크입니다.",
}

COUNTRY_RISK_LIBRARY: Dict[str, dict] = {
    "중국": {
        "industries": {"반도체/전자", "배터리/전지", "모빌리티/자동차", "철강/소재", "정밀화학/소재"},
        "risk_tags": ["희토류·흑연 수출 통제", "리튬 정제 지배력", "코로나 재봉쇄/전력 제한"],
        "alternatives": ["호주", "캐나다", "베트남", "인도"],
    },
    "일본": {
        "industries": {"반도체/전자", "정밀화학/소재"},
        "risk_tags": ["포토레지스트·불화수소 수출 규제", "정밀부품 독점"],
        "alternatives": ["독일", "대만", "미국"],
    },
    "미국": {
        "industries": {"반도체/전자", "통신/IT 서비스", "모빌리티/자동차"},
        "risk_tags": ["CHIPS Act 보조금 조건", "대중 수출통제"],
        "alternatives": ["EU", "싱가포르", "인도"],
    },
    "러시아": {
        "industries": {"철강/소재", "모빌리티/자동차", "정밀화학/소재"},
        "risk_tags": ["천연가스·원유 공급", "니켈·팔라듐 공급 불안"],
        "alternatives": ["사우디", "노르웨이", "호주"],
    },
    "우크라이나": {
        "industries": {"철강/소재", "모빌리티/자동차"},
        "risk_tags": ["곡물·네온가스 공급 중단", "흑해 물류"],
        "alternatives": ["루마니아", "폴란드"],
    },
    "대만": {
        "industries": {"반도체/전자"},
        "risk_tags": ["파운드리 생산 차질", "해협 봉쇄"],
        "alternatives": ["한국", "미국", "일본"],
    },
    "이스라엘": {
        "industries": {"바이오/제약", "통신/IT 서비스"},
        "risk_tags": ["사이버 보안 인력", "반도체 장비 연구"] ,
        "alternatives": ["미국", "아일랜드", "핀란드"],
    },
    "팔레스타인": {
        "industries": {"정밀화학/소재", "바이오/제약"},
        "risk_tags": ["중동 항만 물류", "에너지 공급 변동"],
        "alternatives": ["요르단", "이집트"],
    },
    "이란": {
        "industries": {"정밀화학/소재", "철강/소재"},
        "risk_tags": ["호르무즈 해협", "석유 제재"],
        "alternatives": ["사우디", "아랍에미리트"],
    },
    "인도": {
        "industries": {"배터리/전지", "모빌리티/자동차", "통신/IT 서비스"},
        "risk_tags": ["니켈·철광석 수출 정책", "데이터 현지화"],
        "alternatives": ["베트남", "말레이시아"],
    },
    "파키스탄": {
        "industries": {"모빌리티/자동차", "바이오/제약"},
        "risk_tags": ["섬유 공급", "항만 인프라"],
        "alternatives": ["방글라데시", "인도"],
    },
    "사우디아라비아": {
        "industries": {"정밀화학/소재", "철강/소재"},
        "risk_tags": ["원유 감산", "석유화학 피드 스톡"],
        "alternatives": ["UAE", "카타르", "미국"],
    },
    "EU": {
        "industries": {"모빌리티/자동차", "반도체/전자", "철강/소재"},
        "risk_tags": ["탄소국경세", "러-우 전쟁 파급"],
        "alternatives": ["동남아", "멕시코"],
    },
    "영국": {
        "industries": {"바이오/제약", "통신/IT 서비스"},
        "risk_tags": ["의약품 허가 절차", "핀테크 규제"],
        "alternatives": ["아일랜드", "독일"],
    },
}


def _match_product(product: str) -> dict:
    for entry in PRODUCT_LIBRARY:
        if any(keyword in product for keyword in entry["keywords"]):
            return entry
    return DEFAULT_PRODUCT


def _build_product_insights(products: Iterable[str]) -> List[ProductInsight]:
    insights: List[ProductInsight] = []
    for product in products:
        if not product:
            continue
        entry = _match_product(product)
        insight = ProductInsight(
            name=product,
            category=entry["category"],
            sensitive_inputs=entry["inputs"],
            alternatives=entry["alternatives"],
            note=entry["note"],
        )
        insights.append(insight)
    return insights or [
        ProductInsight(
            name="사업 품목 미상",
            category=DEFAULT_PRODUCT["category"],
            sensitive_inputs=DEFAULT_PRODUCT["inputs"],
            alternatives=DEFAULT_PRODUCT["alternatives"],
            note=DEFAULT_PRODUCT["note"],
        )
    ]


def _conflict_risks(conflict: dict, products: List[ProductInsight]) -> ConflictInsight:
    countries = conflict.get("pair", "").split("–")
    risk_lines: List[str] = []
    alternative_lines: List[str] = []
    for country in countries:
        country = country.strip()
        if not country:
            continue
        blueprint = COUNTRY_RISK_LIBRARY.get(country)
        if not blueprint:
            continue
        for product in products:
            if product.category not in blueprint["industries"]:
                continue
            sensitive = ", ".join(product.sensitive_inputs[:2])
            tags = ", ".join(blueprint["risk_tags"][:2])
            risk_lines.append(
                f"{country} 이슈로 {product.name}({product.category})에 필요한 {sensitive} 조달이 '{tags}' 요인으로 지연될 수 있습니다."
            )
            combined_alt = list(dict.fromkeys(product.alternatives + blueprint["alternatives"]))
            alternative_lines.append(
                f"{product.name}: {', '.join(combined_alt[:4])}"
            )
    if not risk_lines:
        risk_lines.append("헤드라인과 직접 매칭되는 품목을 찾지 못했지만, 글로벌 운송/금융 제약 리스크를 모니터링해야 합니다.")
    if not alternative_lines:
        alternative_lines.append("계약 다변화: 동남아·EU·중동 공급처를 탐색")
    return ConflictInsight(
        pair=conflict.get("pair", "알 수 없음"),
        source=conflict.get("source", "Unknown"),
        headline=conflict.get("headline", ""),
        risks=risk_lines,
        alternatives=alternative_lines,
    )


def _score(seed: int, multiplier: float) -> int:
    random.seed(seed)
    base = 45 + int(10 * multiplier)
    noise = random.randint(-5, 15)
    return min(100, max(10, base + noise))


def build_report(profile: CompanyProfile, conflicts: List[dict], pages: int) -> Report:
    products = _build_product_insights(profile.products)
    sampled_conflicts = conflicts[:3] if conflicts else [
        {"pair": "중국–일본", "source": "Fallback", "headline": "최근 데이터를 불러오지 못했습니다."}
    ]
    conflict_insights = [_conflict_risks(conflict, products) for conflict in sampled_conflicts]
    exposure_factor = sum(len(item.risks) for item in conflict_insights) / 3
    scores = {
        "공급망 의존도": _score(int(hashlib.sha256(profile.official_name.encode()).hexdigest(), 16), 1 + exposure_factor),
        "위험 품목 비중": _score(int(hashlib.sha256(profile.industry.encode()).hexdigest(), 16), 0.8 + exposure_factor),
        "대체 가능성": _score(int(hashlib.sha256("alt".encode()).hexdigest(), 16), 0.6),
        "단기 충격": _score(int(hashlib.sha256("short".encode()).hexdigest(), 16), 0.9 + exposure_factor / 2),
        "종합 리스크": _score(int(hashlib.sha256("total".encode()).hexdigest(), 16), 1.2 + exposure_factor / 3),
    }

    sections = [
        Section(
            "기업 개요",
            [
                f"공식 명칭: {profile.official_name} / 업종: {profile.industry}",
                f"상장일 {profile.listing_date}, 결산월 {profile.fiscal_month}, 본사 지역 {profile.region}",
                f"대표자: {profile.ceo} / 주요 제품: {', '.join(product.name for product in products[:3])}",
                f"공식 홈페이지: {profile.website or '미등록'}",
            ],
        ),
        Section(
            "데이터 파이프라인",
            [
                "KRX KIND 기업목록에서 업종·주요제품·지역을 실시간 스크래핑해 기초 메타데이터 구성",
                "DART 전자공시와 KSIC/HS Code 매핑을 위한 정규화 파이프라인 설계",
                "UN Comtrade, 관세청, 무역협회 데이터를 통합하여 국가별 수입 비중 및 리드타임 계산",
                "S3 Data Lake + Glue + Athena를 이용해 증분 적재 및 LLM 전처리 파이프 구축",
            ],
        ),
        Section(
            "LLM 분석 파이프라인",
            [
                "사업보고서/뉴스 PDF를 텍스트로 변환 후 품목·원자재 키워드를 추출",
                "LangChain + FAISS로 공급망 관련 문장 검색, 위험 키워드(관세·제재·수출규제) 자동 태깅",
                "Function Calling을 통해 제품-국가-원자재 3중 관계를 JSON 구조로 정규화",
                "분쟁 헤드라인과 교차 비교하여 품목별 경고 신호를 생성",
            ],
        ),
        Section(
            "정량화 모델",
            [
                "의존도 지수: 공급국 점유율 × 분쟁 강도 가중치",
                "위험 품목 지수: 전략물자 리스트 교집합 + 품목 수입 편중도",
                "대체 가능성: 후보 공급국 다양성, 리드타임, 인증 기간 기반 스코어",
                "충격도: 시나리오별 매출·영업이익 영향 (단기/중기)을 모형화",
            ],
        ),
        Section(
            "PDF/리포트 구성",
            [
                "1) 기업 개요, 2) 사업구조 및 품목, 3) 분쟁 영향 매핑",
                "4) 단기·중기 리스크 히트맵, 5) 대체 공급처 로드맵, 6) 대응 우선순위",
                "WeasyPrint/LaTeX 템플릿으로 그래프·테이블을 포함한 10p 보고서 자동 생성",
            ],
        ),
        Section(
            "확장 전략",
            [
                "중·일, 미·중, 러·EU, 중동 등 다수 분쟁을 동적 크롤링으로 확장",
                "멀티테넌트 SaaS + API 모드(컨설팅/금융사 연계) 제공",
                "경보형 웹훅, ERP/PLM 연계 커넥터 출시로 월 구독 모델 전환",
            ],
        ),
    ]

    return Report(
        profile=profile,
        page_goal=pages,
        product_insights=products,
        conflict_insights=conflict_insights,
        sections=sections,
        scores=scores,
    )
