from config import SCORING, AFRICA_COUNTRIES, KEYWORDS


def score_opportunity(op):
    text = (op.get("title", "") + " " + op.get("description", "")).lower()
    score = 0

    for word, value in SCORING.items():
        if word in text:
            score += value

    if op.get("country") and op.get("country") != "Unknown":
        if op.get("country") in AFRICA_COUNTRIES.values():
            score += 3

    keywords_found = []
    for kw in KEYWORDS:
        if kw in text:
            keywords_found.append(kw)
    op["keywords_found"] = ", ".join(keywords_found) if keywords_found else ""

    if score >= 10:
        op["tag"] = "high"
    elif score >= 5:
        op["tag"] = "medium"
    else:
        op["tag"] = "low"

    op["score"] = score
    return op


def score_batch(opportunities):
    return [score_opportunity(op) for op in opportunities]
