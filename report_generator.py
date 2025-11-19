from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Set

from company_profile import CompanyProfile
from product_source import ProductRecord, gather_product_records


@dataclass
class Section:
    title: str
    bullets: List[str]


@dataclass
class ProductInsight:
    name: str
    description: str
    source: str
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
    matched_products: List[str]


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


def _match_product(text: str) -> dict:
    normalized = text.lower()
    for entry in PRODUCT_LIBRARY:
        if any(keyword.lower() in normalized for keyword in entry["keywords"]):
            return entry
    return DEFAULT_PRODUCT


def _build_product_insights(records: Iterable[ProductRecord]) -> List[ProductInsight]:
    insights: List[ProductInsight] = []
    for record in records:
        if not record.name:
            continue
        entry = _match_product(f"{record.name} {record.evidence}")
        insight = ProductInsight(
            name=record.name,
            description=record.evidence,
            source=record.source,
            category=entry["category"],
            sensitive_inputs=entry["inputs"],
            alternatives=entry["alternatives"],
            note=entry["note"],
        )
        insights.append(insight)
    if insights:
        return insights
    return [
        ProductInsight(
            name="사업 품목 미상",
            description="전자공시에서 제품 정보를 찾지 못했습니다. 업종 기반 기본 위험도를 제공합니다.",
            source="Fallback",
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
    matched: List[str] = []
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
            if product.name not in matched:
                matched.append(product.name)
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
        matched_products=matched,
    )


def _compute_scores(products: List[ProductInsight], conflicts: List[ConflictInsight]) -> Dict[str, int]:
    total_products = max(1, len(products))
    matched: Set[str] = set()
    conflict_density = 0
    for conflict in conflicts:
        matched.update(conflict.matched_products)
        conflict_density += len(conflict.risks)

    matched_ratio = min(1.0, len(matched) / total_products)
    sensitive_load = min(1.0, sum(len(p.sensitive_inputs) for p in products) / (total_products * 4))
    alternative_depth = min(1.0, sum(len(p.alternatives) for p in products) / (total_products * 5))
    conflict_intensity = min(1.0, conflict_density / max(3, len(conflicts) * 2))

    dependency = min(100, int(35 + matched_ratio * 45 + sensitive_load * 15))
    risk_share = min(100, int(30 + sensitive_load * 50 + conflict_intensity * 20))
    alternative_score = max(15, min(95, int(80 - matched_ratio * 35 + alternative_depth * 25)))
    short_term = min(100, int(25 + matched_ratio * 40 + conflict_intensity * 35))
    total_score = min(100, int((dependency + risk_share + short_term) / 3))

    return {
        "공급망 의존도": dependency,
        "위험 품목 비중": risk_share,
        "대체 가능성": alternative_score,
        "단기 충격": short_term,
        "종합 리스크": total_score,
    }


def build_report(profile: CompanyProfile, conflicts: List[dict], pages: int) -> Report:
    records = gather_product_records(profile)
    products = _build_product_insights(records)
    sampled_conflicts = conflicts[:3] if conflicts else [
        {"pair": "중국–일본", "source": "Fallback", "headline": "최근 데이터를 불러오지 못했습니다."}
    ]
    conflict_insights = [_conflict_risks(conflict, products) for conflict in sampled_conflicts]
    scores = _compute_scores(products, conflict_insights)

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
                "KIND/KRX 공시 테이블을 실시간 수집해 공식 업종·주요제품·사업지 정보를 확보",
                "Wikipedia REST API와 HTML 파서를 이용해 사업보고서의 제품/사업부 설명을 문장 단위로 추출",
                "전자공시 원문과 뉴스 헤드라인을 함께 적재하여 품목-국가-리스크 3자 매핑을 구축",
                "S3 혹은 로컬 캐시(.dart_cache)를 활용해 반복 호출 시 응답 시간을 단축",
            ],
        ),
        Section(
            "LLM 분석 파이프라인",
            [
                "파싱된 제품 설명에서 2차전지/반도체/정밀화학 등 도메인 카테고리를 분류",
                "중국·일본·미국 등 분쟁 국가 키워드를 정규화하여 제품별 리스크 태그를 연결",
                "LangChain/RAG를 통해 사업보고서 문장과 무역 데이터, 뉴스 요약본을 QA 페이로드로 변환",
                "Function Calling으로 제품-원자재-대체 공급처 구조를 JSON 스키마에 맞춰 적재",
            ],
        ),
        Section(
            "정량화 모델",
            [
                "의존도 지수: 분쟁과 직접 매칭된 품목 비중 + 핵심 투입재 복잡도를 가중",
                "위험 품목 지수: 품목별 민감 소재 개수와 헤드라인 경보 횟수를 누적",
                "대체 가능성: 대체 공급처 다양성과 지역 분산도를 계산하여 점수화",
                "충격도: 단기(물류·관세)와 중기(투자·인증) 변수로 별도 스코어 산출",
            ],
        ),
        Section(
            "PDF/리포트 구성",
            [
                "1) 기업 개요, 2) KIND+Wikipedia 제품 라인업, 3) 분쟁 영향 매핑",
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
