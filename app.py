# """Веб-калькулятор НДС по странам мира."""
# from flask import Flask, render_template, request, jsonify
# from collections import Counter

# from vat_data import (
#     COUNTRIES, find, fmt_rate, fmt_rate_full,
#     parse_amount, calc, GENERIC_SCOPE, EXPORT_NOTE,
# )

# app = Flask(__name__)

# DEFAULT_COMPARE = [
#     "Германия", "Франция", "Италия", "Испания",
#     "Великобритания", "Швеция", "Дания", "Венгрия",
#     "Россия", "США", "ОАЭ", "Китай",
# ]


# @app.route("/", methods=["GET", "POST"])
# def index():
#     query = request.form.get("country", "").strip()
#     amount_raw = request.form.get("amount", "").strip()

#     result = None
#     error = None
#     ambiguous = None

#     if query:
#         amount = parse_amount(amount_raw) if amount_raw else None
#         if amount_raw and amount is None:
#             error = "Не удалось разобрать сумму."
#         found, exact = find(query)
#         if not found:
#             error = "Страна не найдена. Попробуйте другое название."
#         elif exact or len(found) == 1:
#             ru = found[0]
#             c = COUNTRIES[ru]
#             result = {
#                 "ru": c["ru"],
#                 "en": c["en"],
#                 "rate": c["rate"],
#                 "rate_str": fmt_rate_full(c) if c["rate"] is not None else None,
#                 "note": c["note"],
#                 "scope": c["scope"] or GENERIC_SCOPE,
#                 "future": c["future"],
#                 "amount": None,
#             }
#             if amount is not None and c["rate"] is not None:
#                 result["amount"] = calc(ru, amount)
#         else:
#             ambiguous = found

#     all_countries = [
#         {
#             "ru": ru,
#             "rate_str": fmt_rate_full(COUNTRIES[ru]),
#         }
#         for ru in sorted(COUNTRIES)
#     ]

#     return render_template(
#         "index.html",
#         query=query,
#         amount_raw=amount_raw,
#         result=result,
#         error=error,
#         ambiguous=ambiguous,
#         all_countries=all_countries,
#     )


# @app.route("/api/compare")
# def api_compare():
#     """Сравнение итоговой цены для суммы в разных странах."""
#     amount = parse_amount(request.args.get("amount", "1000")) or 1000

#     names = request.args.get("countries", "").strip()
#     if names:
#         selected = []
#         for t in (n.strip() for n in names.split(",") if n.strip()):
#             found, _ = find(t)
#             if found:
#                 selected.append(found[0])
#     else:
#         selected = DEFAULT_COMPARE

#     data = []
#     for ru in selected:
#         c = COUNTRIES[ru]
#         if c["rate"] is None:
#             continue
#         k = c["rate"] / 100
#         data.append({
#             "country": ru,
#             "rate": c["rate"],
#             "net": amount,
#             "vat": round(amount * k, 2),
#             "gross": round(amount * (1 + k), 2),
#         })
#     data.sort(key=lambda x: x["gross"])
#     return jsonify({"amount": amount, "items": data})


# @app.route("/api/distribution")
# def api_distribution():
#     """Сколько стран с каждой ставкой."""
#     rates = [c["rate"] for c in COUNTRIES.values() if c["rate"] is not None]
#     counter = Counter(rates)
#     items = sorted(counter.items())
#     return jsonify({
#         "labels": [f"{r:g}%" for r, _ in items],
#         "values": [n for _, n in items],
#     })

# @app.route("/api/search")
# def api_search():
#     query = request.args.get("q", "").strip()
#     if not query:
#         return jsonify([])

#     # Ищем совпадения (используем вашу функцию find)
#     found, _ = find(query)
    
#     # Ограничиваем вывод, чтобы не перегружать интерфейс
#     results = []
#     for ru in found[:8]:
#         c = COUNTRIES[ru]
#         results.append({
#             "ru": ru,
#             "en": c["en"],
#             "rate_str": fmt_rate_full(c)
#         })
#     return jsonify(results)

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5001)


"""Веб-калькулятор НДС по странам мира."""
from flask import Flask, render_template, request, jsonify
from collections import Counter
from vat_data import (
    COUNTRIES, find, fmt_rate, fmt_rate_full,
    parse_amount, calc, GENERIC_SCOPE, ISO_CODES
)

app = Flask(__name__)

DEFAULT_COMPARE = [
    "Германия", "Франция", "Италия", "Испания",
    "Великобритания", "Швеция", "Дания", "Венгрия",
    "Россия", "США", "ОАЭ", "Китай",
]

@app.route("/", methods=["GET", "POST"])
def index():
    query = request.form.get("country", "").strip()
    amount_raw = request.form.get("amount", "").strip()
    result = None
    error = None
    ambiguous = None

    if query:
        amount = parse_amount(amount_raw) if amount_raw else None
        if amount_raw and amount is None:
            error = "Не удалось разобрать сумму."
        found, exact = find(query)
        if not found:
            error = "Страна не найдена. Попробуйте другое название."
        elif exact or len(found) == 1:
            ru = found[0]
            c = COUNTRIES[ru]
            result = {
                "ru": c["ru"], "en": c["en"], "rate": c["rate"],
                "rate_str": fmt_rate_full(c) if c["rate"] is not None else None,
                "note": c["note"], "scope": c["scope"] or GENERIC_SCOPE,
                "future": c["future"], "amount": None,
            }
            if amount is not None and c["rate"] is not None:
                result["amount"] = calc(ru, amount)
        else:
            ambiguous = found

    all_countries = [
        {"ru": ru, "rate_str": fmt_rate_full(COUNTRIES[ru])}
        for ru in sorted(COUNTRIES)
    ]

    return render_template(
        "index.html", query=query, amount_raw=amount_raw,
        result=result, error=error, ambiguous=ambiguous, all_countries=all_countries
    )

@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])
    found, _ = find(query)
    results = []
    for ru in found[:8]:
        c = COUNTRIES[ru]
        results.append({"ru": ru, "en": c["en"], "rate_str": fmt_rate_full(c)})
    return jsonify(results)

@app.route("/api/compare")
def api_compare():
    amount = parse_amount(request.args.get("amount", "1000")) or 1000
    names = request.args.get("countries", "").strip()
    if names:
        selected = []
        for t in (n.strip() for n in names.split(",") if n.strip()):
            found, _ = find(t)
            if found: selected.append(found[0])
    else:
        selected = DEFAULT_COMPARE

    data = []
    for ru in selected:
        c = COUNTRIES[ru]
        if c["rate"] is None: continue
        k = c["rate"] / 100
        data.append({
            "country": ru, "rate": c["rate"],
            "net": amount, "vat": round(amount * k, 2),
            "gross": round(amount * (1 + k), 2),
        })
    data.sort(key=lambda x: x["gross"])
    return jsonify({"amount": amount, "items": data})

@app.route("/api/distribution")
def api_distribution():
    rates = [c["rate"] for c in COUNTRIES.values() if c["rate"] is not None]
    counter = Counter(rates)
    items = sorted(counter.items())
    return jsonify({
        "labels": [f"{r:g}%" for r, _ in items],
        "values": [n for _, n in items],
    })

@app.route("/api/map_data")
def api_map_data():
    rows = []
    for ru, c in COUNTRIES.items():
        if c["rate"] is None or ru not in ISO_CODES:
            continue
        rows.append({"iso": ISO_CODES[ru], "country": ru, "rate": c["rate"]})
    return jsonify(rows)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)