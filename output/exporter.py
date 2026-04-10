import pandas as pd
import os
from datetime import datetime


def export_csv(data, custom_filename=None):
    if not data:
        return None

    df = pd.DataFrame(data)

    cols = [
        "title",
        "country",
        "organization",
        "organization_type",
        "description",
        "budget",
        "deadline",
        "date",
        "score",
        "tag",
        "project_type",
        "mentivis_angle",
        "source_type",
        "keywords_found",
        "url",
    ]

    for col in cols:
        if col not in df.columns:
            df[col] = ""

    df = df[cols]

    if custom_filename:
        filename = custom_filename
    else:
        filename = f"opportunities_{datetime.today().strftime('%Y%m%d')}.csv"

    os.makedirs("data/processed", exist_ok=True)
    filepath = f"data/processed/{filename}"
    df.to_csv(filepath, index=False, encoding="utf-8")

    return filepath


def export_history(data, run_id=None):
    if not data:
        return None

    df = pd.DataFrame(data)

    if run_id is None:
        run_id = datetime.today().strftime("%Y%m%d_%H%M%S")

    os.makedirs("data/raw", exist_ok=True)
    filepath = f"data/raw/run_{run_id}.csv"
    df.to_csv(filepath, index=False, encoding="utf-8")

    return filepath


def load_csv(filepath):
    if not os.path.exists(filepath):
        return []

    df = pd.read_csv(filepath)
    return df.to_dict("records")


def load_latest():
    files = [f for f in os.listdir("data/processed") if f.endswith(".csv")]
    if not files:
        return []

    files.sort(reverse=True)
    return load_csv(f"data/processed/{files[0]}")
