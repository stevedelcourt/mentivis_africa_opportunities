#!/usr/bin/env python3
"""
Mentivis - FINAL UNIFIED EXPORT WITH ALL WORKING SCRAPERS
"""

from datetime import datetime
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup


def fix_url(href, base):
    if not href:
        return base
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return base + href
    return base + "/" + href


def scrape_undp():
    results = []
    base = "https://procurement-notices.undp.org"
    for kw in ["education", "formation", "training", "skills"]:
        try:
            res = requests.get(
                f"{base}/search.cfm?search={kw}", timeout=10, verify=False
            )
            soup = BeautifulSoup(res.text, "lxml")
            for link in soup.find_all("a", href=True):
                title = link.get_text(strip=True)
                if title and len(title) > 15:
                    results.append(
                        {
                            "title": title[:100],
                            "organization": "UNDP",
                            "country": "",
                            "url": fix_url(link.get("href"), base),
                        }
                    )
        except:
            pass
    return results[:50]


def scrape_afd():
    results = []
    base = "https://www.afd.fr"
    try:
        res = requests.get(f"{base}/fr/appels-a-projets", timeout=10)
        soup = BeautifulSoup(res.text, "lxml")
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            if title and len(title) > 15:
                results.append(
                    {
                        "title": title[:100],
                        "organization": "AFD",
                        "country": "",
                        "url": fix_url(link.get("href"), base),
                    }
                )
    except:
        pass
    return results[:30]


def scrape_bad_fallback():
    # Manual curated since site is blocked (403)
    return [
        {
            "title": "AfDB Procurement - use manual search",
            "organization": "AfDB",
            "country": "Africa",
            "url": "https://www.afdb.org/en/projects-and-operations/procurement",
        },
    ]


def scrape_boad():
    results = []
    base = "https://www.boad.org"
    try:
        res = requests.get(base, timeout=10)
        soup = BeautifulSoup(res.text, "lxml")
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            if title and len(title) > 15:
                results.append(
                    {
                        "title": title[:100],
                        "organization": "BOAD",
                        "country": "West Africa",
                        "url": fix_url(link.get("href"), base),
                    }
                )
    except:
        pass
    return results[:20]


def scrape_badea():
    results = []
    base = "https://www.badea.org"
    try:
        res = requests.get(base, timeout=10)
        soup = BeautifulSoup(res.text, "lxml")
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            if title and len(title) > 15:
                results.append(
                    {
                        "title": title[:100],
                        "organization": "BADEA",
                        "country": "",
                        "url": fix_url(link.get("href"), base),
                    }
                )
    except:
        pass
    return results[:20]


def scrape_isdb():
    results = []
    base = "https://www.isdb.org"
    try:
        res = requests.get(base, timeout=10)
        soup = BeautifulSoup(res.text, "lxml")
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            if title and len(title) > 15:
                results.append(
                    {
                        "title": title[:100],
                        "organization": "IsDB",
                        "country": "",
                        "url": fix_url(link.get("href"), base),
                    }
                )
    except:
        pass
    return results[:20]


def scrape_tendersontime():
    results = []
    base = "https://www.tendersontime.com"
    try:
        res = requests.get(f"{base}/africa-tenders", timeout=10)
        soup = BeautifulSoup(res.text, "lxml")
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            if title and len(title) > 15:
                results.append(
                    {
                        "title": title[:100],
                        "organization": "TendersOnTime",
                        "country": "",
                        "url": fix_url(link.get("href"), base),
                    }
                )
    except:
        pass
    return results[:30]


def scrape_globaltenders():
    results = []
    base = "https://www.globaltenders.com"
    try:
        res = requests.get(base, timeout=10)
        soup = BeautifulSoup(res.text, "lxml")
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            if title and len(title) > 15:
                results.append(
                    {
                        "title": title[:100],
                        "organization": "GlobalTenders",
                        "country": "",
                        "url": fix_url(link.get("href"), base),
                    }
                )
    except:
        pass
    return results[:30]


def scrape_tendersinfo():
    results = []
    base = "https://www.tendersinfo.com"
    try:
        res = requests.get(f"{base}/global-Africa-tenders.php", timeout=10)
        soup = BeautifulSoup(res.text, "lxml")
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            if title and len(title) > 15:
                results.append(
                    {
                        "title": title[:100],
                        "organization": "TendersInfo",
                        "country": "",
                        "url": fix_url(link.get("href"), base),
                    }
                )
    except:
        pass
    return results[:20]


def scrape_portal_maroc_fallback():
    return [
        {
            "title": "Maroc Marches Publics - use direct URL",
            "organization": "MarocPortal",
            "country": "Maroc",
            "url": "https://www.marchespublics.gov.ma",
        },
    ]


def scrape_armp_cameroon():
    results = []
    base = "https://www.armp.cm"
    try:
        res = requests.get(base, timeout=10)
        soup = BeautifulSoup(res.text, "lxml")
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            if title and len(title) > 15:
                results.append(
                    {
                        "title": title[:100],
                        "organization": "ARMP Cameroon",
                        "country": "Cameroun",
                        "url": fix_url(link.get("href"), base),
                    }
                )
    except:
        pass
    return results[:30]


def scrape_minesup_cameroon():
    results = []
    base = "https://www.minesup.gov.cm"
    try:
        res = requests.get(base, timeout=10)
        soup = BeautifulSoup(res.text, "lxml")
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            if title and len(title) > 15:
                results.append(
                    {
                        "title": title[:100],
                        "organization": "MINESUP",
                        "country": "Cameroun",
                        "url": fix_url(link.get("href"), base),
                    }
                )
    except:
        pass
    return results[:30]


def scrape_ministere_tunisie():
    results = []
    base = "https://www.education.gov.tn"
    try:
        res = requests.get(base, timeout=10)
        soup = BeautifulSoup(res.text, "lxml")
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            if title and len(title) > 15:
                results.append(
                    {
                        "title": title[:100],
                        "organization": "Ministere Tunis",
                        "country": "Tunisie",
                        "url": fix_url(link.get("href"), base),
                    }
                )
    except:
        pass
    return results[:30]


def scrape_reliefweb():
    results = []
    base = "https://reliefweb.int"
    try:
        res = requests.get(f"{base}/jobs", timeout=10)
        soup = BeautifulSoup(res.text, "lxml")
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            if title and len(title) > 15:
                results.append(
                    {
                        "title": title[:100],
                        "organization": "ReliefWeb",
                        "country": "",
                        "url": fix_url(link.get("href"), base),
                    }
                )
    except:
        pass
    return results[:20]


def scrape_unesco():
    results = []
    base = "https://en.unesco.org"
    try:
        res = requests.get(f"{base}/career", timeout=10)
        soup = BeautifulSoup(res.text, "lxml")
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            if title and len(title) > 15:
                results.append(
                    {
                        "title": title[:100],
                        "organization": "UNESCO",
                        "country": "",
                        "url": fix_url(link.get("href"), base),
                    }
                )
    except:
        pass
    return results[:10]


# MAIN
def main():
    print("=== FINAL UNIFIED EXPORT ===\n")

    scrapers = [
        ("UNDP", scrape_undp),
        ("AFD", scrape_afd),
        ("AfDB", scrape_bad_fallback),
        ("BOAD", scrape_boad),
        ("BADEA", scrape_badea),
        ("IsDB", scrape_isdb),
        ("TendersOnTime", scrape_tendersontime),
        ("GlobalTenders", scrape_globaltenders),
        ("TendersInfo", scrape_tendersinfo),
        ("MarocPortal", scrape_portal_maroc_fallback),
        ("ARMP Cameroon", scrape_armp_cameroon),
        ("MINESUP Cameroon", scrape_minesup_cameroon),
        ("Ministere Tunis", scrape_ministere_tunisie),
        ("ReliefWeb", scrape_reliefweb),
        ("UNESCO", scrape_unesco),
    ]

    all_data = []
    total_scraped = 0

    for name, func in scrapers:
        try:
            data = func()
            print(f"{name}: {len(data)}")
            total_scraped += len(data)
            for op in data:
                op["source"] = name
            all_data.extend(data)
        except Exception as e:
            print(f"{name}: ERROR")

    # Deduplicate by URL
    seen = set()
    unique = []
    for op in all_data:
        url = op.get("url", "")
        if url and url not in seen:
            seen.add(url)
            unique.append(op)

    all_data = unique

    print(f"\nTotal raw: {total_scraped}")
    print(f"After dedup: {len(all_data)}")

    # Export
    df = pd.DataFrame(all_data)
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
    df = df[cols]
    df.insert(0, "Number", range(1, len(df) + 1))

    os.makedirs("data/processed", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/processed/mentivis_all_{timestamp}.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")

    print(f"\n=== SAVED ===")
    print(f"File: {filename}")
    print(f"Total: {len(df)}")

    print("\n=== BY ORGANIZATION ===")
    print(df["organization"].value_counts())


if __name__ == "__main__":
    main()
