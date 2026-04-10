#!/usr/bin/env python3
"""
Mentivis - FINAL with ACTUAL TENDER LINKS (not site homepage!)
"""

import os
import re
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup


INCLUDE = [
    "formation",
    "education",
    "training",
    "skills",
    "tvet",
    "university",
    "ecole",
]
EXCLUDE = [
    "oil",
    "fuel",
    "construction",
    "road",
    "server",
    "computer",
    "furniture",
    "vehicle",
]

COUNTRIES = {
    "senegal": "Senegal",
    "cote d_ivoire": "Côte d'Ivoire",
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
}


def get_undp_tenders():
    """Get ACTUAL UNDP tender links with IDs"""
    results = []
    base = "https://procurement-notices.undp.org"

    for kw in ["education", "formation", "training", "skills"]:
        try:
            url = f"{base}/search.cfm?search={kw}"
            r = requests.get(url, timeout=15, verify=False)
            soup = BeautifulSoup(r.text, "lxml")

            links = soup.find_all("a", href=True)
            for link in links:
                href = link.get("href", "")
                title = link.get_text(strip=True)

                if "nego_id=" in href and title and len(title) > 15:
                    # Extract ID
                    match = re.search(r"nego_id=(\d+)", href)
                    if match:
                        nid = match.group(1)
                        full_url = f"{base}/view_negotiation.cfm?nego_id={nid}"

                        # Filter education
                        title_lower = title.lower()
                        if not any(inc in title_lower for inc in INCLUDE):
                            continue
                        if any(ex in title_lower for ex in EXCLUDE):
                            continue

                        # Detect country
                        country = ""
                        for ckey, cname in COUNTRIES.items():
                            if ckey in title_lower:
                                country = cname
                                break

                        results.append(
                            {
                                "title": title[:100],
                                "organization": "UNDP",
                                "country": country,
                                "url": full_url,
                                "source": "UNDP",
                            }
                        )
        except:
            continue

    return results[:50]


def get_afd_tenders():
    """Get AFD actual tender links"""
    results = []
    base = "https://www.afd.fr"

    try:
        r = requests.get(f"{base}/fr/appels-a-projets", timeout=15)
        soup = BeautifulSoup(r.text, "lxml")

        links = soup.find_all("a", href=True)
        for link in links:
            href = link.get("href", "")
            title = link.get_text(strip=True)

            # Look for actual project links
            if "/projet/" in href or "/appel-" in href or "project" in href:
                if title and len(title) > 15:
                    title_lower = title.lower()
                    if any(inc in title_lower for inc in INCLUDE):
                        full_url = f"{base}{href}" if href.startswith("/") else href

                        country = ""
                        for ckey, cname in COUNTRIES.items():
                            if ckey in title_lower:
                                country = cname
                                break

                        results.append(
                            {
                                "title": title[:100],
                                "organization": "AFD",
                                "country": country,
                                "url": full_url,
                                "source": "AFD",
                            }
                        )
    except:
        pass

    return results[:30]


def get_boad_tenders():
    """BOAD actual project links"""
    results = []
    base = "https://www.boad.org"

    try:
        r = requests.get(base, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")

        links = soup.find_all("a", href=True)
        for link in links:
            href = link.get("href", "")
            title = link.get_text(strip=True)

            if "/projet" in href or "project" in href:
                if title and len(title) > 15:
                    full_url = f"{base}{href}" if href.startswith("/") else href
                    results.append(
                        {
                            "title": title[:100],
                            "organization": "BOAD",
                            "country": "West Africa",
                            "url": full_url,
                            "source": "BOAD",
                        }
                    )
    except:
        pass

    return results[:20]


def get_badea_tenders():
    """BADEA actual project links"""
    results = []
    base = "https://www.badea.org"

    try:
        r = requests.get(base, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")

        links = soup.find_all("a", href=True)
        for link in links:
            href = link.get("href", "")
            title = link.get_text(strip=True)

            if href and len(title) > 15:
                full_url = f"{base}{href}" if href.startswith("/") else href
                results.append(
                    {
                        "title": title[:100],
                        "organization": "BADEA",
                        "country": "",
                        "url": full_url,
                        "source": "BADEA",
                    }
                )
    except:
        pass

    return results[:20]


def get_isdb_tenders():
    """IsDB actual project links"""
    results = []
    base = "https://www.isdb.org"

    try:
        r = requests.get(base, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")

        links = soup.find_all("a", href=True)
        for link in links:
            href = link.get("href", "")
            title = link.get_text(strip=True)

            if href and len(title) > 15:
                full_url = f"{base}{href}" if href.startswith("/") else href
                results.append(
                    {
                        "title": title[:100],
                        "organization": "IsDB",
                        "country": "",
                        "url": full_url,
                        "source": "IsDB",
                    }
                )
    except:
        pass

    return results[:20]


def get_tendersontime():
    """TendersOnTime actual links"""
    results = []
    base = "https://www.tendersontime.com"

    try:
        r = requests.get(f"{base}/africa-tenders", timeout=15)
        soup = BeautifulSoup(r.text, "lxml")

        links = soup.find_all("a", href=True)
        for link in links:
            href = link.get("href", "")
            title = link.get_text(strip=True)

            if title and len(title) > 15 and href:
                full_url = f"{base}{href}" if href.startswith("/") else href
                results.append(
                    {
                        "title": title[:100],
                        "organization": "TendersOnTime",
                        "country": "",
                        "url": full_url,
                        "source": "TendersOnTime",
                    }
                )
    except:
        pass

    return results[:30]


def get_globaltenders():
    """GlobalTenders actual links"""
    results = []
    base = "https://www.globaltenders.com"

    try:
        r = requests.get(base, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")

        links = soup.find_all("a", href=True)
        for link in links:
            href = link.get("href", "")
            title = link.get_text(strip=True)

            if title and len(title) > 15 and href:
                full_url = f"{base}{href}" if href.startswith("/") else href
                results.append(
                    {
                        "title": title[:100],
                        "organization": "GlobalTenders",
                        "country": "",
                        "url": full_url,
                        "source": "GlobalTenders",
                    }
                )
    except:
        pass

    return results[:30]


def get_minesup():
    """MINESUP Cameroon actual links"""
    results = []
    base = "https://www.minesup.gov.cm"

    try:
        r = requests.get(base, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")

        links = soup.find_all("a", href=True)
        for link in links:
            href = link.get("href", "")
            title = link.get_text(strip=True)

            if title and len(title) > 15 and href:
                full_url = f"{base}{href}" if href.startswith("/") else href
                results.append(
                    {
                        "title": title[:100],
                        "organization": "MINESUP",
                        "country": "Cameroun",
                        "url": full_url,
                        "source": "MINESUP",
                    }
                )
    except:
        pass

    return results[:30]


def get_armp_cm():
    """ARMP Cameroon actual links"""
    results = []
    base = "https://www.armp.cm"

    try:
        r = requests.get(base, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")

        links = soup.find_all("a", href=True)
        for link in links:
            href = link.get("href", "")
            title = link.get_text(strip=True)

            if title and len(title) > 15 and href:
                full_url = f"{base}{href}" if href.startswith("/") else href
                results.append(
                    {
                        "title": title[:100],
                        "organization": "ARMP Cameroon",
                        "country": "Cameroun",
                        "url": full_url,
                        "source": "ARMP Cameroon",
                    }
                )
    except:
        pass

    return results[:30]


def get_ministere_tunisie():
    """Ministere Tunisia actual links"""
    results = []
    base = "https://www.education.gov.tn"

    try:
        r = requests.get(base, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")

        links = soup.find_all("a", href=True)
        for link in links:
            href = link.get("href", "")
            title = link.get_text(strip=True)

            if title and len(title) > 15 and href:
                full_url = f"{base}{href}" if href.startswith("/") else href
                results.append(
                    {
                        "title": title[:100],
                        "organization": "Ministere Tunis",
                        "country": "Tunisie",
                        "url": full_url,
                        "source": "Ministere Tunis",
                    }
                )
    except:
        pass

    return results[:30]


def get_reliefweb():
    """ReliefWeb actual job links"""
    results = []
    base = "https://reliefweb.int"

    try:
        r = requests.get(f"{base}/jobs", timeout=15)
        soup = BeautifulSoup(r.text, "lxml")

        links = soup.find_all("a", href=True)
        for link in links:
            href = link.get("href", "")
            title = link.get_text(strip=True)

            if title and len(title) > 15 and href:
                full_url = f"{base}{href}" if href.startswith("/") else href
                results.append(
                    {
                        "title": title[:100],
                        "organization": "ReliefWeb",
                        "country": "",
                        "url": full_url,
                        "source": "ReliefWeb",
                    }
                )
    except:
        pass

    return results[:20]


# MAIN
def main():
    print("=== FINAL WITH ACTUAL TENDER LINKS ===\n")

    scrapers = [
        ("UNDP", get_undp_tenders),
        ("AFD", get_afd_tenders),
        ("BOAD", get_boad_tenders),
        ("BADEA", get_badea_tenders),
        ("IsDB", get_isdb_tenders),
        ("TendersOnTime", get_tendersontime),
        ("GlobalTenders", get_globaltenders),
        ("MINESUP", get_minesup),
        ("ARMP Cameroon", get_armp_cm),
        ("Ministere Tunis", get_ministere_tunisie),
        ("ReliefWeb", get_reliefweb),
    ]

    all_data = []

    for name, func in scrapers:
        try:
            data = func()
            print(f"{name}: {len(data)}")
            all_data.extend(data)
        except Exception as e:
            print(f"{name}: ERROR")

    # Deduplicate
    seen = set()
    unique = []
    for op in all_data:
        url = op.get("url", "")
        if url and url not in seen:
            seen.add(url)
            unique.append(op)

    all_data = unique

    print(f"\nTotal: {len(all_data)}")

    # Export
    df = pd.DataFrame(all_data)
    df.insert(0, "Number", range(1, len(df) + 1))
    df["description"] = ""
    df["budget"] = ""
    df["deadline"] = ""
    df["date"] = datetime.today().strftime("%Y-%m-%d")

    cols = [
        "Number",
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
    df = df[cols]

    os.makedirs("data/processed", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/processed/mentivis_tenders_{timestamp}.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")

    print(f"\n=== SAVED ===")
    print(f"File: {filename}")
    print(f"Total: {len(df)}")

    print("\n=== SAMPLE (VERIFY URLs) ===")
    for i, row in df.head(10).iterrows():
        print(f"{row['Number']}. {row['organization']}")
        print(f"   {row['url']}")
        print()

    print("=== BY ORGANIZATION ===")
    print(df["organization"].value_counts())


if __name__ == "__main__":
    main()
