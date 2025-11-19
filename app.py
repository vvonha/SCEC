from __future__ import annotations

import hashlib
from flask import Flask, render_template, request

from conflict_fetcher import gather_conflict_pairs
from report_generator import build_report

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    conflict_pairs = gather_conflict_pairs()
    default_conflict = conflict_pairs[0]["pair"] if conflict_pairs else "중국–일본"

    if request.method == "POST":
        company = request.form.get("company", "").strip()
        conflict = request.form.get("conflict", default_conflict).strip()
        length = int(request.form.get("length", 10))

        if not company:
            error = "기업명을 입력하면 최신 분쟁 국가쌍을 자동으로 적용합니다."
            return render_template(
                "index.html",
                error=error,
                conflict_pairs=conflict_pairs,
                selected_conflict=conflict,
                company_value=company,
                length_value=length,
            )

        seed = int(hashlib.sha256(f"{company}{conflict}{length}".encode()).hexdigest(), 16)
        report = build_report(company, conflict, length, seed)
        return render_template(
            "index.html",
            report=report,
            conflict_pairs=conflict_pairs,
            selected_conflict=conflict,
            company_value=company,
            length_value=length,
        )

    return render_template(
        "index.html",
        conflict_pairs=conflict_pairs,
        selected_conflict=default_conflict,
        company_value="",
        length_value=10,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
