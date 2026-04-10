#!/usr/bin/env python3
"""
Mentivis - Enhanced export WITH Senegal-specific search
"""

import os
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup


INCLUDE_KEYWORDS = [
    "formation",
    "education",
    "formation professionnelle",
    "insertion professionnelle",
    "ecole",
    "universite",
    "university",
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
    "cfp",
    "centre formation",
]

EXCLUDE_KEYWORDS = [
    "oil",
    "fuel",
    "petrol",
    "construction",
    "works",
    "road",
    "bridge",
    "server",
    "computer",
    "laptop",
    "furniture",
    "vehicle",
    "car",
    "truck",
    "pharmaceutical",
    "medicament",
    "medical",
    "security",
    "guard",
]

COUNTRIES = {
    "senegal": "Senegal",
    "cote d_ivoire": "Côte d'Ivoire",
    "ivory coast": "Côte d'Ivoire",
    "morocco": "Maroc",
    "maroc": "Maroc",
    "tunisia": "Tunisie",
    "tunisie": "Tunisie",
    "cameroon": "Cameroun",
    "cameroun": "Cameroun",
    "mali": "Mali",
    "burkina": "Burkina Faso",
    "benin": "Benin",
    "togo": "Togo",
    "niger": "Niger",
    "guinea": "Guinée",
}


def fix_url(href, base_url):
    if not href:
        return base_url
    href = href.strip()
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return base_url + href
    return base_url + "/" + href


def detect_country(text):
    text_lower = text.lower()
    for ckey, cname in COUNTRIES.items():
        if ckey in text_lower:
            return cname
    return ""


def filter_education(title):
    text = title.lower()
    if not any(kw in text for kw in INCLUDE_KEYWORDS):
        return False
    if any(kw in text for kw in EXCLUDE_KEYWORDS):
        return False
    return True


def scrape_undp():
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}

    # ADD Senegal-specific search
    searches = [
        "education",
        "formation",
        "training",
        "skills",
        "tvet",
        "senegal",
        "cote d_ivoire",
        "morocco",
    ]

    for term in searches:
        url = f"https://procurement-notices.undp.org/search.cfm?search={term}"
        try:
            res = requests.get(url, headers=headers, timeout=15, verify=False)
            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.text, "lxml")
            links = soup.find_all("a", href=True)

            for link in links:
                title = link.get_text(strip=True)
                if not title or len(title) < 15:
                    continue

                if not filter_education(title):
                    continue

                href = link.get("href", "")
                full_url = fix_url(href, "https://procurement-notices.undp.org")
                country = detect_country(title)

                results.append(
                    {
                        "title": title[:150],
                        "organization": "UNDP",
                        "country": country,
                        "description": "",
                        "budget": "",
                        "deadline": "",
                        "url": full_url,
                        "date": datetime.today().strftime("%Y-%m-%d"),
                        "source": "undp",
                    }
                )

        except:
            continue

    return results


def main():
    print("=== ENHANCED MENTIVIS EXPORT WITH ALL COUNTRIES ===\n")

    print("Scraping UNDP...")
    data = scrape_undp()
    print(f"Total: {len(data)}")

    # Deduplicate
    seen = set()
    unique = []
    for op in data:
        url = op.get("url", "")
        if url and url not in seen:
            seen.add(url)
            if op.get("title"):
                unique.append(op)

    data = unique
    print(f"Unique: {len(data)}")

    # Export
    df = pd.DataFrame(data)
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
    df.insert(0, "Number", range(1, len(df) + 1))

    os.makedirs("data/processed", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/processed/mentivis_final_{timestamp}.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")

    print(f"\n=== EXPORTED ===")
    print(f"File: {filename}")
    print(f"Total: {len(df)}")

    print("\n=== BY COUNTRY ===")
    print(df["country"].value_counts())


if __name__ == "__main__":
    main()
