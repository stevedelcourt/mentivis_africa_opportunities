import hashlib


def deduplicate(opportunities):
    seen = set()
    unique = []

    for op in opportunities:
        key = (
            op.get("title", "")
            + "|"
            + op.get("organization", "")
            + "|"
            + op.get("url", "")
        ).strip()
        if not key or key == "||":
            continue
        h = hashlib.md5(key.encode()).hexdigest()

        if h not in seen:
            seen.add(h)
            unique.append(op)

    return unique


def filter_by_score(opportunities, min_score=0):
    return [op for op in opportunities if op.get("score", 0) >= min_score]


def filter_by_country(opportunities, countries):
    filtered = []
    for op in opportunities:
        country = op.get("country", "")
        if not country or country == "Unknown":
            continue
        if any(c.lower() in country.lower() for c in countries):
            filtered.append(op)
    return filtered


def filter_by_tag(opportunities, tag):
    return [op for op in opportunities if op.get("tag") == tag]


def sort_by_score(opportunities, reverse=True):
    return sorted(opportunities, key=lambda x: x.get("score", 0), reverse=reverse)
