# SCEC – 공급망 분쟁 리스크 스캐너

이 저장소는 "기업명"만 입력하면 Reddit / BBC World RSS에서 자동으로 수집한 분쟁 국가쌍을 매칭해 리포트 초안을 만들어 주는 로컬 웹 애플리케이션 예제입니다. 오픈 API 키 없이도 동작하며, 샘플 알고리즘이 데이터를 생성합니다.

## 실행 방법

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

브라우저에서 `http://localhost:5000` 에 접속한 뒤 기업명만 입력하면 최신 뉴스 기반 분쟁 국가쌍 후보가 자동으로 표시되고 선택할 수 있습니다.

## 구성

- `app.py` – Flask 웹 서버 (폼 + 결과 화면)
- `conflict_fetcher.py` – Reddit/BBC 헤드라인에서 분쟁 국가쌍 자동 수집
- `report_generator.py` – 리포트 템플릿 및 점수 생성 로직
- `templates/index.html` – 단일 페이지 UI
- `static/style.css` – 간단한 스타일
- `requirements.txt` – 의존성 목록

향후 실제 LLM API 또는 데이터 수집 파이프라인을 연결하여 고도화할 수 있습니다.
