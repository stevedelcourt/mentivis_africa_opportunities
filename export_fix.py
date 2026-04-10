#!/usr/bin/env python3
"""
Mentivis - Export Education/Formation - URL CORRIGÉ
"""

import re
import os
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import random


BASE_URL = "https://procurement-notices.undp.org"
BASE_URL_AFD = "https://www.afd.fr"
BASE_URL_AFDB = "https://www.afdb.org"
BASE_URL_TOT = "https://www.tendersontime.com"

INCLUDE = [
    "formation",
    "education",
    "formation professionnelle",
    "insertion",
    "ecole",
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
]

EXCLUDE = [
    "oil",
    "fuel",
    "construction",
    "works",
    "road",
    "bridge",
    "server",
    "computer",
    "furniture",
    "vehicle",
    "car",
    "truck",
    "medical",
    "pharmaceutical",
]

COUNTRIES = {
    "senegal": "Senegal",
    "cote d'ivoire": "Côte d'Ivoire",
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
    "congo": "Congo",
}


def fix_url(href, base):
    """Corrige URL - ajoute / si manquant"""
    if not href:
        return base
    href = href.strip()
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return base + href
    return base + "/" + href


def scrape_undp():
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

    for term in ["education", "formation", "training", "skills", "tvet"]:
        url = f"{BASE_URL}/search.cfm?search={term}"
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

                title_lower = title.lower()
                if any(ex in title_lower for ex in EXCLUDE):
                    continue
                if not any(inc in title_lower for inc in INCLUDE):
                    continue

                href = link.get("href", "")
                full_url = fix_url(href, BASE_URL)

                country = ""
                for c_key, c_name in COUNTRIES.items():
                    if c_key in title_lower:
                        country = c_name
                        break

                results.append(
                    {
                        "Issuer": "UNDP",
                        "Title": title[:120],
                        "Country": country,
                        "Deadline": "",
                        "URL": full_url,
                        "Source": "UNDP",
                    }
                )

        except:
            continue

    return results


def scrape_afd():
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"{BASE_URL_AFD}/fr/appels-a-projets"

    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, "lxml")
        links = soup.find_all("a", href=True)

        for link in links:
            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                continue

            title_lower = title.lower()
            if any(ex in title_lower for ex in EXCLUDE):
                continue
            if not any(inc in title_lower for inc in INCLUDE):
                continue

            href = link.get("href", "")
            full_url = fix_url(href, BASE_URL_AFD)

            country = ""
            for c_key, c_name in COUNTRIES.items():
                if c_key in title_lower:
                    country = c_name
                    break

            results.append(
                {
                    "Issuer": "AFD",
                    "Title": title[:120],
                    "Country": country,
                    "Deadline": "",
                    "URL": full_url,
                    "Source": "AFD",
                }
            )

    except:
        pass

    return results


def scrape_bad():
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"{BASE_URL_AFDB}/en/projects-and-operations/procurement"

    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, "lxml")
        links = soup.find_all("a", href=True)

        for link in links:
            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                continue

            title_lower = title.lower()
            if any(ex in title_lower for ex in EXCLUDE):
                continue
            if not any(inc in title_lower for inc in INCLUDE):
                continue

            href = link.get("href", "")
            full_url = fix_url(href, BASE_URL_AFDB)

            country = ""
            for c_key, c_name in COUNTRIES.items():
                if c_key in title_lower:
                    country = c_name
                    break

            results.append(
                {
                    "Issuer": "AfDB",
                    "Title": title[:120],
                    "Country": country,
                    "Deadline": "",
                    "URL": full_url,
                    "Source": "AfDB",
                }
            )

    except:
        pass

    return results


def scrape_tenders():
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"{BASE_URL_TOT}/africa-tenders"

    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, "lxml")
        links = soup.find_all("a", href=True)

        for link in links:
            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                continue

            title_lower = title.lower()
            if any(ex in title_lower for ex in EXCLUDE):
                continue
            if not any(inc in title_lower for inc in INCLUDE):
                continue

            href = link.get("href", "")
            full_url = fix_url(href, BASE_URL_TOT)

            country = ""
            for c_key, c_name in COUNTRIES.items():
                if c_key in title_lower:
                    country = c_name
                    break

            results.append(
                {
                    "Issuer": "TendersOnTime",
                    "Title": title[:120],
                    "Country": country,
                    "Deadline": "",
                    "URL": full_url,
                    "Source": "TendersOnTime",
                }
            )

    except:
        pass

    return results


def main():
    print("=== MENTIVIS - Education/Formation Export ===\n")

    scrapers = [
        ("UNDP", scrape_undp),
        ("AFD", scrape_afd),
        ("AfDB", scrape_bad),
        ("TendersOnTime", scrape_tenders),
    ]

    all_data = []

    for name, func in scrapers:
        try:
            print(f"Scraping {name}...", end=" ", flush=True)
            data = func()
            print(f"{len(data)}")
            all_data.extend(data)
        except Exception as e:
            print(f"Error: {e}")

    # Deduplicate
    seen = set()
    unique = []
    for op in all_data:
        url = op.get("URL", "")
        if url and url not in seen:
            seen.add(url)
            if op.get("Title"):
                unique.append(op)

    all_data = unique

    print(f"\nTotal: {len(all_data)} opportunities")

    # Export
    df = pd.DataFrame(all_data)

    if not df.empty:
        df.insert(0, "Number", range(1, len(df) + 1))

        cols = ["Number", "Issuer", "Title", "Country", "Deadline", "URL", "Source"]
        for col in cols:
            if col not in df.columns:
                df[col] = ""
        df = df[cols]

        os.makedirs("data/processed", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/processed/education_formation_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")

        print(f"\n=== EXPORTED ===")
        print(f"File: {filename}")
        print(f"Total: {len(df)}\n")

        # Show sample with correct URLs
        print("=== SAMPLE ===")
        for i, row in df.head(10).iterrows():
            print(f"{row['Number']}. {row['Issuer']} | {row['Country']} | {row['URL']}")

        print("\n=== BY COUNTRY ===")
        print(df["Country"].value_counts().to_string())

    return filename, len(df)


if __name__ == "__main__":
    main()
