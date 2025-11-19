from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Set

from company_profile import CompanyProfile
from product_source import ProductRecord, gather_product_records
from supplier_network import PartnerRecord, map_supply_network
from supply_chain import build_supply_chain_overlay
from supply_directory import lookup_category_directory


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
    imports: List[str]
    exports: List[str]
    logistics: List[str]
    alerts: List[str]
    supplier_companies: List[str]
    alternative_companies: List[str]


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
    supply_partners: List[PartnerRecord]
    alternative_partners: List[PartnerRecord]
    supply_lanes: List[str]
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


def _shorten(text: str, limit: int = 90) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


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
        overlay = build_supply_chain_overlay(entry["category"], record.evidence)
        directory = lookup_category_directory(entry["category"])
        overlay["logistics"].extend(directory.get("routes", []))
        overlay["alerts"].extend(directory.get("alerts", []))
        for key in ("imports", "exports", "logistics", "alerts"):
            unique = []
            for item in overlay.get(key, []):
                if item not in unique:
                    unique.append(item)
            overlay[key] = unique
        insight = ProductInsight(
            name=record.name,
            description=record.evidence,
            source=record.source,
            category=entry["category"],
            sensitive_inputs=entry["inputs"],
            alternatives=entry["alternatives"],
            note=entry["note"],
            imports=overlay.get("imports", []),
            exports=overlay.get("exports", []),
            logistics=overlay.get("logistics", []),
            alerts=overlay.get("alerts", []),
            supplier_companies=list(directory.get("suppliers", [])),
            alternative_companies=list(directory.get("alternatives", [])),
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
            imports=["글로벌 원자재 스팟"],
            exports=["주요 고객 다변화"],
            logistics=["복합 운송"],
            alerts=["전사적 환율/정책 리스크"],
            supplier_companies=["지역별 공급사 조사 필요"],
            alternative_companies=["동일 산업 대체 제조사 탐색"],
        )
    ]


def _format_partner(node: PartnerRecord) -> str:
    note = _shorten(node.note, 80)
    country = node.country or "국가 미확인"
    return f"{node.name}({country}) – {note}" if note else f"{node.name}({country})"


def _attach_partner_examples(products: List[ProductInsight], network: dict) -> None:
    for product in products:
        tokens = {product.name.lower()}
        tokens.add(product.category.lower())
        supplier_hits: List[str] = []
        for node in network["suppliers"]:
            haystack = f"{node.name} {node.note}".lower()
            if any(token and token in haystack for token in tokens):
                supplier_hits.append(_format_partner(node))
        if not supplier_hits:
            supplier_hits = [_format_partner(node) for node in network["suppliers"][:2]]
        if supplier_hits:
            merged = supplier_hits + [item for item in product.supplier_companies if item not in supplier_hits]
            product.supplier_companies = merged[:5]
        else:
            product.supplier_companies = product.supplier_companies[:5]

        alt_hits: List[str] = []
        for node in network["alternatives"]:
            haystack = f"{node.name} {node.note}".lower()
            if any(token and token in haystack for token in tokens):
                alt_hits.append(_format_partner(node))
        if not alt_hits:
            alt_hits = [_format_partner(node) for node in network["alternatives"][:2]]
        if alt_hits:
            merged_alt = alt_hits + [item for item in product.alternative_companies if item not in alt_hits]
            product.alternative_companies = merged_alt[:5]
        else:
            product.alternative_companies = product.alternative_companies[:5]


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
    network = map_supply_network(profile, records)
    _attach_partner_examples(products, network)
    sampled_conflicts = conflicts[:3] if conflicts else [
        {"pair": "중국–일본", "source": "Fallback", "headline": "최근 데이터를 불러오지 못했습니다."}
    ]
    conflict_insights = [_conflict_risks(conflict, products) for conflict in sampled_conflicts]
    scores = _compute_scores(products, conflict_insights)

    supplier_highlights = [
        f"{node.name}({node.country or '국가 미확인'}): {_shorten(node.note)}" for node in network["suppliers"]
    ]
    alternative_highlights = [
        f"{node.name}({node.country or '국가 미확인'}): {_shorten(node.note)}" for node in network["alternatives"]
    ]

    top_products = ", ".join(product.name for product in products[:3])
    category_counts: Dict[str, int] = {}
    for product in products:
        category_counts[product.category] = category_counts.get(product.category, 0) + 1
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    category_summary = ", ".join(f"{cat} {count}건" for cat, count in sorted_categories[:3])

    risk_focus = []
    for product in products[:3]:
        alert = product.alerts[0] if product.alerts else "글로벌 공급망 모니터링"
        supplier = product.supplier_companies[0] if product.supplier_companies else "공급선 미확보"
        risk_focus.append(f"{product.name}: {alert} / 핵심 공급선 {supplier}")

    conflict_summary = []
    for conflict in conflict_insights:
        focus = ", ".join(conflict.matched_products[:2]) or "간접 영향"
        conflict_summary.append(f"{conflict.pair} → {focus}")

    alt_summary = []
    for product in products[:3]:
        if product.alternative_companies:
            alt_summary.append(f"{product.name}: {product.alternative_companies[0]}")
        else:
            alt_summary.append(f"{product.name}: {', '.join(product.alternatives[:3])}")

    action_items = [
        "조달 다변화: 실명 파트너 기준 우선순위 재조정 및 가격/리드타임 재협상",
        "분쟁 직접 타격 품목에 대해 최소 2곳의 세컨더리 공급사 가동 준비",
        "물류 경로 리던던시 확보(해상+항공) 및 재고 커버리지 1.5배 확대",
        "헤드라인 감지 시 자동 리포트/PDF 생성 후 이해관계자 공유",
    ]
    if network["suppliers"]:
        action_items.insert(0, f"핵심 공급사 {network['suppliers'][0].name}와(과) 비상 시나리오 협상")
    if network["alternatives"]:
        action_items.append(f"대체 공급선 1순위: {network['alternatives'][0].name} 온보딩")

    sections = [
        Section(
            "공급망 요약",
            [
                f"{profile.official_name} ({profile.industry}) – 데이터 출처: {profile.source}",
                f"주요 사업 지역: {profile.region} / 리포트 목표 {pages}p",
                f"주요 품목: {top_products or '미확인'}",
                f"카테고리 분포: {category_summary or '단일 품목'}",
            ],
        ),
        Section(
            "위험 품목 우선순위",
            risk_focus or ["가용 데이터 부족"],
        ),
        Section(
            "분쟁 영향 매핑",
            conflict_summary or ["최근 헤드라인과 직접 연계된 품목 없음"],
        ),
        Section(
            "대체 공급 전략",
            alt_summary or ["대체 공급처 데이터 부족"],
        ),
        Section(
            "실제 공급 파트너",
            supplier_highlights[:4] or ["위키/뉴스 기반 공급사 데이터를 확보하지 못했습니다."],
        ),
        Section(
            "대안 공급 기업",
            alternative_highlights[:4] or ["동일 산업 대체 기업 정보 부족"],
        ),
        Section(
            "주요 운송/조달 경로",
            network["lanes"] or ["실명 공급사가 확보되면 운송 경로를 노출합니다."],
        ),
        Section(
            "실행 권고",
            action_items,
        ),
    ]

    return Report(
        profile=profile,
        page_goal=pages,
        product_insights=products,
        conflict_insights=conflict_insights,
        supply_partners=network["suppliers"],
        alternative_partners=network["alternatives"],
        supply_lanes=network["lanes"],
        sections=sections,
        scores=scores,
    )
