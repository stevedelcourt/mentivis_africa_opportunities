#!/usr/bin/env python3
"""
Mentivis - FINAL EXPORT with ALL FIXED SCRAPERS
Education/formation filtered with proper URLs
"""

import os
from datetime import datetime
import pandas as pd
import random

from scrapers.fixed_scrapers import (
    scrape_undp,
    scrape_afd,
    scrape_bad,
    scrape_boad,
    scrape_badea,
    scrape_isdb,
    scrape_reliefweb,
    scrape_tendersontime,
    scrape_globaltenders,
    scrape_portal_maroc,
    scrape_armp_cameroon,
    scrape_minesup_cameroon,
    scrape_ministere_tunisie,
    scrape_devex,
    scrape_unesco,
    scrape_unicef,
)

# All scrapers
SCRAPERS = [
    ("UNDP", scrape_undp),
    ("AFD", scrape_afd),
    ("AfDB", scrape_bad),
    ("BOAD", scrape_boad),
    ("BADEA", scrape_badea),
    ("IsDB", scrape_isdb),
    ("ReliefWeb", scrape_reliefweb),
    ("TendersOnTime", scrape_tendersontime),
    ("GlobalTenders", scrape_globaltenders),
    ("Maroc Portal", scrape_portal_maroc),
    ("ARMP Cameroon", scrape_armp_cameroon),
    ("MINESUP Cameroon", scrape_minesup_cameroon),
    ("Ministere Tunisie", scrape_ministere_tunisie),
    ("Devex", scrape_devex),
    ("UNESCO", scrape_unesco),
    ("UNICEF", scrape_unicef),
]


def deduplicate(data):
    """Remove duplicates by URL"""
    seen = set()
    unique = []
    for op in data:
        url = op.get("url", "")
        if url and url not in seen:
            seen.add(url)
            if op.get("title"):
                unique.append(op)
    return unique


def export():
    print("=== MENTIVIS - FINAL EXPORT ===\n")

    all_data = []

    for name, func in SCRAPERS:
        try:
            print(f"Scraping {name}...", end=" ", flush=True)
            data = func()
            print(f"{len(data)}")
            all_data.extend(data)
        except Exception as e:
            print(f"Error: {str(e)[:40]}")

    # Deduplicate
    all_data = deduplicate(all_data)
    print(f"\nTotal: {len(all_data)}")

    if not all_data:
        print("No data!")
        return None

    # Create DataFrame
    df = pd.DataFrame(all_data)

    # Ensure columns exist
    cols = [
        "title",
        "organization",
        "country",
        "description",
        "budget",
        "deadline",
        "url",
        "date",
        "source",
    ]
    for col in cols:
        if col not in df.columns:
            df[col] = ""

    # Select and reorder columns
    df = df[
        [
            "title",
            "organization",
            "country",
            "description",
            "budget",
            "deadline",
            "url",
            "date",
            "source",
        ]
    ]

    # Add number
    df.insert(0, "Number", range(1, len(df) + 1))

    # Save
    os.makedirs("data/processed", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/processed/mentivis_education_{timestamp}.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")

    print(f"\n=== EXPORTED ===")
    print(f"File: {filename}")
    print(f"Total: {len(df)}")

    print("\n=== SAMPLE ===")
    for i, row in df.head(10).iterrows():
        print(
            f"{row['Number']}. {row['organization']:12} | {row['country']:15} | {row['title'][:40]}..."
        )
        print(f"   URL: {row['url']}\n")

    print("=== BY ORGANIZATION ===")
    print(df["organization"].value_counts().to_string())

    print("\n=== BY COUNTRY ===")
    print(df["country"].value_counts().to_string())

    return filename


if __name__ == "__main__":
    export()
