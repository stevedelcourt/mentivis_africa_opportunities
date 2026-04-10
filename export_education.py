#!/usr/bin/env python3
"""
Mentivis - Export Education/Formation Projects Only
Filtered CSV with deadline
"""

import re
from datetime import datetime
import pandas as pd
from scrapers.undp import scrape_undp
from scrapers.afd import scrape_afd
from scrapers.bad import scrape_bad
from scrapers.eu_ted import scrape_eu_ted
from scrapers.portal_maroc import scrape_portal_maroc
from scrapers.globaltenders import scrape_globaltenders
from scrapers.tendersontime import scrape_tendersontime
from scrapers.armp_cameroon import scrape_armp_cameroon
from scrapers.ministere_tunisie import scrape_ministere_tunisie
from scrapers.minesup_cameroon import scrape_minesup_cameroon
from scrapers.boad import scrape_boad
from scrapers.reliefweb import scrape_reliefweb
from scrapers.isdb import scrape_isdb
from scrapers.badea import scrape_badea


# Keywords to INCLUDE (education/formation)
INCLUDE_KEYWORDS = [
    "formation",
    "education",
    "formation professionnelle",
    "insertion professionnelle",
    "emploi",
    "ecole professionnelle",
    "university",
    "universite",
    "'enseignement",
    "skills",
    "competences",
    "tvet",
    "vocational",
    "pedagog",
    "curriculum",
    "learning",
    "teacher",
    "teaching",
    "student",
    "scholarship",
    "formation continue",
    "apprentissage",
]

# Keywords to EXCLUDE
EXCLUDE_KEYWORDS = [
    "oil",
    "fuel",
    "petrol",
    "gaz",
    "hydrocarbure",
    "construction",
    "works",
    "road",
    "bridge",
    "building",
    "it equipment",
    "server",
    "hardware",
    "computer",
    "laptop",
    "furniture",
    "supplies",
    "stationery",
    "vehicle",
    "car",
    "truck",
    "bus",
    "medical",
    "pharmaceutical",
    "medicament",
    "cleaning",
    "janitor",
    "security",
    "guard",
]

# African French-speaking countries
AFRICA_FR = [
    "senegal",
    "cote d'ivoire",
    "ivory coast",
    "morocco",
    "maroc",
    "tunisia",
    "tunisie",
    "cameroon",
    "cameroun",
    "mali",
    "burkina",
    "burkina faso",
    "benin",
    "togo",
    "niger",
    "guinea",
    "guinee",
    "congo",
    "gabon",
    "madagascar",
    "chad",
]


def is_education_related(title, description):
    """Check if project is education/formation related"""
    text = (title + " " + description).lower()

    # Must include at least one education keyword
    has_education = any(kw in text for kw in INCLUDE_KEYWORDS)
    if not has_education:
        return False

    # Must NOT have exclude keywords
    has_exclude = any(kw in text for kw in EXCLUDE_KEYWORDS)
    if has_exclude:
        return False

    return True


def detect_country(title, description):
    """Detect country from title/description"""
    text = (title + " " + description).lower()

    for country in AFRICA_FR:
        if country in text:
            # Map to proper name
            country_map = {
                "senegal": "Senegal",
                "cote d'ivoire": "Côte d'Ivoire",
                "ivory coast": "Côte d'Ivoire",
                "morocco": "Maroc",
                "maroc": "Maroc",
                "tunisia": "Tunisie",
                "tunisie": "Tunisie",
                "cameroon": "Cameroun",
                "cameroun": "Cameroun",
                "mali": "Mali",
                "burkina": "Burkina Faso",
                "burkina faso": "Burkina Faso",
                "benin": "Benin",
                "togo": "Togo",
                "niger": "Niger",
                "guinea": "Guinee",
                "guinee": "Guinee",
                "congo": "Congo",
                "gabon": "Gabon",
                "madagascar": "Madagascar",
            }
            return country_map.get(country, country.title())

    return ""


def extract_deadline(text):
    """Extract deadline from text"""
    # Common patterns
    patterns = [
        r"(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})",
        r"(\d{1,2}\s+(?:Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{2,4})",
        r"deadline[:\s]+(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    return ""


def scrape_all():
    """Scrape all sources"""
    scrapers = [
        ("UNDP", scrape_undp),
        ("AFD", scrape_afd),
        ("AfDB", scrape_bad),
        ("EU TED", scrape_eu_ted),
        ("Maroc", scrape_portal_maroc),
        ("GlobalTenders", scrape_globaltenders),
        ("TendersOnTime", scrape_tendersontime),
        ("ARMP Cameroon", scrape_armp_cameroon),
        ("Ministre Tunisie", scrape_ministere_tunisie),
        ("MINESUP Cameroon", scrape_minesup_cameroon),
        ("BOAD", scrape_boad),
        ("ReliefWeb", scrape_reliefweb),
        ("IsDB", scrape_isdb),
        ("BADEA", scrape_badea),
    ]

    all_data = []

    print("=== SCRAPING ALL SOURCES ===\n")

    for name, func in scrapers:
        try:
            print(f"{name}...", end=" ", flush=True)
            data = func()
            print(f"{len(data)}")

            for op in data:
                op["source"] = name
                all_data.append(op)
        except Exception as e:
            print(f"Error: {e}")

    return all_data


def filter_education(data):
    """Filter only education/formation projects"""
    filtered = []

    print("\n=== FILTERING EDUCATION/FORMATION ===\n")

    for op in data:
        title = op.get("title", "")
        desc = op.get("description", "")

        if is_education_related(title, desc):
            # Extract country
            country = detect_country(title, desc) or op.get("country", "")

            # Extract deadline
            deadline = extract_deadline(title + " " + desc) or op.get("deadline", "")

            filtered.append(
                {
                    "Issuer": op.get("organization", ""),
                    "Title": title[:150],
                    "Country": country,
                    "Deadline": deadline,
                    "URL": op.get("url", ""),
                    "Source": op.get("source", ""),
                }
            )

    return filtered


def export_csv(filtered_data):
    """Export to CSV"""
    import os

    os.makedirs("data/processed", exist_ok=True)

    # Create DataFrame
    df = pd.DataFrame(filtered_data)

    # Add number column
    df.insert(0, "Number", range(1, len(df) + 1))

    # Reorder columns
    cols = ["Number", "Issuer", "Title", "Country", "Deadline", "URL", "Source"]
    for col in cols:
        if col not in df.columns:
            df[col] = ""
    df = df[cols]

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/processed/education_formation_{timestamp}.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")

    return filename, df


def main():
    print("=== MENTIVIS - EDUCATION/FORMATION EXPORT ===\n")

    # Step 1: Scrape all
    all_data = scrape_all()
    print(f"\nTotal scraped: {len(all_data)}")

    # Step 2: Filter education only
    filtered = filter_education(all_data)
    print(f"Education/Formation: {len(filtered)}")

    # Step 3: Export
    filename, df = export_csv(filtered)
    print(f"\n=== EXPORTED ===")
    print(f"File: {filename}")
    print(f"Total: {len(df)} opportunities")

    # Show sample
    print("\n=== SAMPLE ===")
    for i, row in df.head(10).iterrows():
        print(f"{row['Number']}. {row['Issuer']}: {row['Title'][:50]}...")
        print(f"   Country: {row['Country']} | Deadline: {row['Deadline']}")
        print(f"   URL: {row['URL'][:60]}...")
        print()

    # By country summary
    print("=== BY COUNTRY ===")
    countries = df["Country"].value_counts()
    for country, count in countries.items():
        if country:
            print(f"  {country}: {count}")

    return filename, len(df)


if __name__ == "__main__":
    main()
