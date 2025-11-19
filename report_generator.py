from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Section:
    title: str
    bullets: List[str]


@dataclass
class Report:
    company: str
    conflict: str
    page_goal: int
    sections: List[Section]
    scores: Dict[str, int]


def _score(seed: int, offset: int, scale: int = 40) -> int:
    random.seed(seed + offset)
    return min(100, max(5, int(random.random() * scale + 55)))


def build_report(company: str, conflict: str, pages: int, seed: int) -> Report:
    random.seed(seed)
    primary_markets = ["반도체", "배터리", "정밀기계", "바이오", "철강", "모빌리티"]
    core_market = random.choice(primary_markets)

    supply_nodes = [
        "DART 사업보고서에서 추출한 제품군을 텍스트 청크 단위로 정규화",
        "전자공시 PDF를 OCR 후 LLM으로 요약하여 원/부자재 문장 획득",
        "관세청·무역협회 데이터를 HS Code 기준으로 매핑",
        "UN Comtrade 대체 지표를 활용해 수출입 비중 산정",
    ]

    llm_pipeline = [
        "LangChain 기반 문서 로더로 사업보고서 섹션 분리",
        "Embedding + 벡터DB(FAISS)로 공급망 관련 문장 검색",
        "리스크 키워드 사전을 적용해 관세·수출규제 언급 자동 태깅",
        "LLM Function Call로 제품-국가 의존도를 구조화된 JSON으로 변환",
    ]

    risk_matches = [
        f"{conflict} 분쟁 시 {company}의 {core_market} 핵심 소재 공급 중단 시나리오",
        "희토류·불화수소 등 전략 물자에 대한 단일 국가 의존 비중 계산",
        "관세/수출입 규제 강화로 리드타임 지연 및 원가 상승 추정",
        "대체 공급국(인도, 베트남, EU) 전환 비용과 기간 평가",
    ]

    scores = {
        "공급망 의존도": _score(seed, 1),
        "위험 품목 비중": _score(seed, 2),
        "대체 가능성": _score(seed, 3),
        "단기 충격": _score(seed, 4),
        "종합 리스크": _score(seed, 5),
    }

    sections = [
        Section(
            "데이터 파이프라인 설계",
            [
                "DART/전자공시 API를 통한 최근 5년치 사업보고서 수집",
                "산업분류(KSIC)와 HS Code를 크로스 매핑하여 품목-국가 테이블 구축",
                "관세청·UN Comtrade 데이터를 결합해 국가별 수출입 의존도 계산",
                "S3 Lakehouse에 적재 후 Glue Crawler로 스키마 자동화",
            ],
        ),
        Section("LLM 분석 파이프라인", llm_pipeline),
        Section("분쟁 리스크 매칭", risk_matches),
        Section(
            "정량화 모델",
            [
                "의존도: 국가별 공급 비중 * 분쟁 강도 가중치",
                "위험 품목: 전략물자 리스트와 교집합 비율",
                "대체 가능성: 공급처 다양성 + 리드타임 + 전환 CAPEX",
                "충격도: 시나리오별 매출/영업이익 영향 추정",
            ],
        ),
        Section(
            "PDF 리포트 구조",
            [
                "기업 개요 / 사업구조",
                "품목별 위험도 및 매트릭스 시각화",
                "분쟁 영향 요약 + 시나리오",
                "대체 공급처와 실행 로드맵",
                "요약 및 의사결정 가이드",
            ],
        ),
        Section(
            "서비스 UX/API",
            [
                "입력: 기업명, 사업자등록번호, 리포트 길이 (분쟁 국가는 뉴스 피드에서 자동 탐지)",
                "분쟁 소스: Reddit/BBC 등 공신력 있는 헤드라인에서 국가쌍 후보 추출",
                "분석 API: /analyze -> 비동기 태스크 큐(Celery)로 처리",
                "결과 JSON: 섹션, 점수, 추천 전략 포함",
                "PDF 생성: WeasyPrint 기반 템플릿에서 다운로드 링크 반환",
            ],
        ),
        Section(
            "확장 전략",
            [
                "중·일 MVP 이후 미·중/러·EU/중동 갈등으로 국가쌍 확대",
                "고객사별 커스터마이징을 위한 멀티테넌트 SaaS",
                "API 기반 파트너십(은행, 컨설팅)으로 추가 수익",
                "리스크 지수화를 통한 정기 구독 모델",
            ],
        ),
    ]

    sections.append(
        Section(
            "샘플 대응 전략",
            [
                f"{company} 핵심 품목 중 {conflict} 리스크가 높은 부분을 우선 식별",
                "Tier-1 공급사를 분산하고 세이프티 스톡 정책 재정비",
                "관세/통제 변화에 대비한 규제 모니터링 자동화",
                "공급망 대체 로드맵을 분기별로 검증하고 보고",
            ],
        )
    )

    return Report(company=company, conflict=conflict, page_goal=pages, sections=sections, scores=scores)
