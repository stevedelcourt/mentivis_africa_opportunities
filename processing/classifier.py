def classify_project(op):
    text = (op.get("title", "") + " " + op.get("description", "")).lower()

    project_type = "other"

    if (
        "digital" in text
        or "e-learning" in text
        or "online learning" in text
        or "elearning" in text
    ):
        project_type = "digital education"
    elif "university" in text or "higher education" in text or "academic" in text:
        project_type = "higher education"
    elif "training" in text or "skills" in text or "capacity building" in text:
        project_type = "capacity building"
    elif "tvet" in text or "vocational" in text or "professional" in text:
        project_type = "tvet"
    elif (
        "infrastructure" in text
        or "construction" in text
        or "building" in text
        or "school" in text
    ):
        project_type = "infrastructure"
    elif "curriculum" in text or "program" in text or "syllabus" in text:
        project_type = "curriculum"
    elif "research" in text or "study" in text:
        project_type = "research"
    elif "scholarship" in text or "student" in text or "fellowship" in text:
        project_type = "scholarship"
    elif (
        "teacher" in text
        or "teaching" in text
        or "pedagogy" in text
        or "formateur" in text
    ):
        project_type = "teacher training"
    elif "reform" in text or "réforme" in text:
        project_type = "reform"

    op["project_type"] = project_type
    return op


def classify_batch(opportunities):
    return [classify_project(op) for op in opportunities]


def estimate_project_size(op):
    budget = op.get("budget", "")
    size = "unknown"

    if budget:
        budget_clean = (
            budget.replace(",", "")
            .replace(" ", "")
            .replace("€", "")
            .replace("$", "")
            .replace("XAF", "")
            .replace("XOF", "")
        )
        try:
            amount = float(budget_clean)
            if amount < 50000:
                size = "small"
            elif amount < 500000:
                size = "medium"
            else:
                size = "large"
        except:
            pass

    if budget:
        if "million" in budget.lower():
            size = "large"
        elif "thousand" in budget.lower():
            size = "small"
        elif "-" in budget:
            parts = budget.split("-")
            try:
                first = float(parts[0].replace(",", ""))
                if first < 50000:
                    size = "small"
                elif first < 500000:
                    size = "medium"
                else:
                    size = "large"
            except:
                pass

    op["project_size"] = size
    return op
