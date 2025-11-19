from __future__ import annotations

from flask import Flask, render_template, request

from company_profile import lookup_company
from conflict_fetcher import gather_conflict_pairs
from report_generator import build_report

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    conflict_pairs = gather_conflict_pairs()

    if request.method == "POST":
        company = request.form.get("company", "").strip()
        length = int(request.form.get("length", 10))

        if not company:
            error = "기업명을 입력하면 최신 분쟁 국가쌍과 매칭된 공급망 리포트를 자동 생성합니다."
            return render_template(
                "index.html",
                error=error,
                conflict_pairs=conflict_pairs,
                company_value=company,
                length_value=length,
            )

        profile = lookup_company(company)
        if not profile:
            error = "상장사 및 위키 문서를 찾지 못했습니다. 공식 명칭/영문명을 다시 입력해주세요."
            return render_template(
                "index.html",
                error=error,
                conflict_pairs=conflict_pairs,
                company_value=company,
                length_value=length,
            )

        report = build_report(profile, conflict_pairs, length)
        return render_template(
            "index.html",
            report=report,
            conflict_pairs=conflict_pairs,
            company_value=profile.official_name,
            length_value=length,
            error=None,
        )

    return render_template(
        "index.html",
        conflict_pairs=conflict_pairs,
        company_value="",
        length_value=10,
        error=None,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
