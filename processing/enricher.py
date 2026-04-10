from config import AFRICA_COUNTRIES


def detect_country(op):
    text = (op.get("title", "") + " " + op.get("description", "")).lower()

    for key, val in AFRICA_COUNTRIES.items():
        if key in text:
            op["country"] = val
            return op

    country_field = op.get("country", "")
    if country_field:
        for key, val in AFRICA_COUNTRIES.items():
            if key in country_field.lower():
                op["country"] = val
                return op

    op["country"] = "Unknown"
    return op


def detect_country_batch(opportunities):
    return [detect_country(op) for op in opportunities]


def mentivis_angle(op):
    project_type = op.get("type", "")
    angle = ""

    if project_type == "digital education":
        angle = "Positionnement plateformes pédagogiques LMS, formation digitale"
    elif project_type == "higher education":
        angle = "Structuration offre académique, gouvernance universitaire"
    elif project_type == "capacity building":
        angle = "Ingénierie de formation, déploiement opérationnel"
    elif project_type == "tvet":
        angle = "Formation professionnelle, certification de compétences"
    elif project_type == "infrastructure":
        angle = "Construction/réhabilitation établissements scolaires"
    elif project_type == "research":
        angle = "Partenariats recherche, projets académiques"
    else:
        angle = "Exploration - analyser le contexte"

    if op.get("score", 0) >= 10:
        angle = "PRIORITÉ - " + angle

    op["mentivis_angle"] = angle
    return op


def enrich_batch(opportunities):
    return [mentivis_angle(op) for op in opportunities]


def add_source_type(op):
    source = op.get("source", "").lower()
    stype = "tender"

    if "pipeline" in source or "plan" in source:
        stype = "pipeline"
    elif "grant" in source or "funding" in source:
        stype = "grant"
    elif "strategy" in source:
        stype = "strategy"
    elif "procurement" in source:
        stype = "procurement"

    op["source_type"] = stype
    return op
