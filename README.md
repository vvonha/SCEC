# SCEC – 공급망 분쟁 리스크 스캐너

기업명을 입력하면 KRX KIND 전자공시에서 추출한 업종/주요제품 정보를 바탕으로 제품군을 식별하고,
Reddit · BBC World RSS에서 실시간으로 감지한 분쟁 국가쌍과 매칭해 공급망 리스크 리포트를 만들어 주는 로컬 웹 앱입니다.

## 실행 방법

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

브라우저에서 `http://localhost:5000` 에 접속하여 기업명과 원하는 리포트 길이만 입력하면 됩니다.
앱은 다음 절차를 자동으로 수행합니다.

1. KIND/KRX 상장사 전체 목록을 스크래핑하여 입력한 기업명과 가장 유사한 기업을 매칭합니다.
2. 해당 기업의 업종/주요제품/지역 데이터를 추출해 품목별 리스크 템플릿을 구성합니다.
3. Reddit r/worldnews, BBC World RSS에서 최신 헤드라인을 가져와 국가명을 감지하고 분쟁 국가쌍을 생성합니다.
4. 품목–국가 매칭을 통해 위험 포인트와 대체 공급국 제안을 자동으로 서술형 리포트로 생성합니다.

## 구성

- `app.py` – Flask 진입점. 기업명/페이지 길이 입력만 받고 나머지 파이프라인은 자동 실행됩니다.
- `company_profile.py` – KIND/KRX HTML 테이블을 스크래핑하여 기업 프로필(업종, 주요 제품, 대표자 등)을 반환합니다.
- `conflict_fetcher.py` – Reddit/BBC 헤드라인에서 국가 키워드를 탐지하여 분쟁 국가쌍을 구성합니다.
- `report_generator.py` – 실제 품목별 리스크 매칭, 대체 공급 제안, LLM 파이프라인 설명, 점수 산출을 수행합니다.
- `templates/index.html` & `static/style.css` – 단일 페이지 UI, 기업/품목/분쟁 카드 및 리포트 섹션을 시각화합니다.
- `requirements.txt` – Flask + requests + BeautifulSoup 등 의존성 정의.

## 확장 아이디어

- OpenDART API 키를 연동하면 KIND 데이터 외에도 최신 사업보고서 전문을 LLM 파이프라인에 투입할 수 있습니다.
- Celery/Redis를 붙여 대량 기업 분석을 비동기 처리하거나, PDF 생성기(WeasyPrint 등)와 연계해 다운로드 기능을 제공할 수 있습니다.
- SaaS 모드로 확장 시, 분쟁 신호를 주기적으로 저장하고 기업별 구독 알림/웹훅 기능을 제공할 수 있습니다.
