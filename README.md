# SCEC – 공급망 분쟁 리스크 스캐너

기업명을 입력하면 KRX KIND 전자공시(국내) 또는 Wikipedia REST API(글로벌)에서 추출한 제품·서비스 근거를 바탕으로 품목을 식별하고,
Reddit · BBC · Reuters · AP · Al Jazeera · Yonhap 등 다중 뉴스 피드에서 감지한 분쟁 국가쌍과 자동 매칭해 공급망 리스크 리포트를 만들어 주는 로컬 웹 앱입니다.

## 실행 방법

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

브라우저에서 `http://localhost:5000` 에 접속하여 기업명과 원하는 리포트 길이만 입력하면 됩니다.
앱은 다음 절차를 자동으로 수행합니다.

1. KIND/KRX 상장사 전체 목록을 스크래핑하여 국내 기업을 매칭하고, 미매칭 시 Wikipedia(ko/en/ja/zh) REST API에서 글로벌 기업 프로필을 조회합니다.
2. 전자공시/위키 근거 문장을 추출해 제품·서비스 리스트를 구성하고, 공급망 블루프린트를 결합해 수입선/수요처/물류 경로를 추정합니다.
3. Reddit r/worldnews, BBC, Reuters, AP, Al Jazeera, 연합뉴스 영문 RSS 헤드라인에서 국가 키워드를 감지해 분쟁 국가쌍을 생성합니다.
4. 품목–분쟁 매칭을 통해 위험 포인트, 대체 공급국, 수입선 의존도, 경보 메시지를 계산합니다.
5. 결과를 현대식 반응형 UI로 시각화하고, 공급망 요약·대체 전략·실행 권고 섹션을 포함한 리포트를 제공합니다.

## 구성

- `app.py` – Flask 진입점. 기업명/페이지 길이 입력만 받고 나머지 파이프라인은 자동 실행됩니다.
- `company_profile.py` – KIND/KRX HTML 테이블과 Wikipedia(ko/en/ja/zh) REST를 조합하여 국내·해외 기업 프로필을 반환합니다.
- `conflict_fetcher.py` – Reddit/BBC/Reuters/AP/Al Jazeera/연합뉴스 RSS 헤드라인에서 국가 키워드를 탐지해 분쟁 국가쌍을 구성합니다.
- `product_source.py` – KIND, Wikipedia 멀티랭 데이터를 결합해 제품/서비스 설명을 수집합니다.
- `supply_chain.py` – 품목 카테고리별 대표 수입선·수요처·물류 경로·경보 메시지를 생성합니다.
- `report_generator.py` – 품목/분쟁 매칭, 대체 공급 제안, 수입·수출·물류 추적, 정량 점수를 수행하고 리포트 섹션을 만듭니다.
- `templates/index.html` & `static/style.css` – 단일 페이지 UI, 기업/품목/분쟁 카드 및 리포트 섹션을 시각화합니다.
- `requirements.txt` – Flask + requests + BeautifulSoup 등 의존성 정의.

## 확장 아이디어

- OpenDART API 키를 연동하면 KIND/Wikipedia 조합 외에 전자공시 전문까지 분석하여 제품/공급망 단서를 확장할 수 있습니다.
- Celery/Redis를 붙여 대량 기업 분석을 비동기 처리하거나, PDF 생성기(WeasyPrint 등)와 연계해 다운로드 기능을 제공할 수 있습니다.
- SaaS 모드로 확장 시, 분쟁 신호를 주기적으로 저장하고 기업별 구독 알림/웹훅 기능을 제공할 수 있습니다.
