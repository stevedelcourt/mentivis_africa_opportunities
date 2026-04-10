#!/usr/bin/env python3
"""
Mentivis - ALL Scrapers WITH FIXED URLs + EDUCATION FILTER

Fixed scrapers with:
- Proper URL slashes
- Country detection
- Education/formation filter
- Exclude unwanted categories
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
import re


# ========= CONFIG =========
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
    "guinea": "Guinée",
    "guinee": "Guinée",
    "congo": "Congo",
    "gabon": "Gabon",
    "madagascar": "Madagascar",
}


def fix_url(href, base_url):
    """Fix URL with proper slash"""
    if not href:
        return base_url
    href = href.strip()
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return base_url + href
    return base_url + "/" + href


def detect_country(text):
    """Detect country from text"""
    text_lower = text.lower()
    for ckey, cname in COUNTRIES.items():
        if ckey in text_lower:
            return cname
    return ""


def filter_education(title, description):
    """Filter for education/formation only"""
    text = (title + " " + description).lower()

    # Must include education keyword
    if not any(kw in text for kw in INCLUDE_KEYWORDS):
        return False

    # Must not have exclude keyword
    if any(kw in text for kw in EXCLUDE_KEYWORDS):
        return False

    return True


# ========= SCRAPER TEMPLATE =========
def create_scraper(name, base_url, paths=None):
    """Create a fixed scraper"""
    if paths is None:
        paths = [""]

    def scrape():
        results = []
        headers = {"User-Agent": "Mozilla/5.0"}

        for path in paths:
            url = fix_url(path, base_url)
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

                    # Filter education only
                    if not filter_education(title, title):
                        continue

                    href = link.get("href", "")
                    full_url = fix_url(href, base_url)
                    country = detect_country(title)

                    results.append(
                        {
                            "title": title[:150],
                            "organization": name,
                            "country": country,
                            "description": "",
                            "budget": "",
                            "deadline": "",
                            "url": full_url,
                            "date": datetime.today().strftime("%Y-%m-%d"),
                            "source": name,
                        }
                    )

            except:
                continue

        return results

    return scrape


# ========= INDIVIDUAL SCRAPERS =========


def scrape_afd():
    return create_scraper(
        "AFD", "https://www.afd.fr", ["/fr/appels-a-projets", "/en/calls-for-projects"]
    )()


def scrape_bad():
    return create_scraper(
        "AfDB", "https://www.afdb.org", ["/en/projects-and-operations/procurement"]
    )()


def scrape_undp():
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}

    searches = ["education", "formation", "training", "skills", "tvet"]
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

                if not filter_education(title, title):
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


def scrape_world_bank():
    return create_scraper(
        "World Bank",
        "https://projects.worldbank.org",
        ["/en/projects-operations", "/en/projects-operations/procurement"],
    )()


def scrape_boad():
    return create_scraper("BOAD", "https://www.boad.org", [""])()


def scrape_badea():
    return create_scraper("BADEA", "https://www.badea.org", [""])()


def scrape_isdb():
    return create_scraper("IsDB", "https://www.isdb.org", [""])()


def scrape_reliefweb():
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://reliefweb.int/jobs"

    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, "lxml")
        links = soup.find_all("a", href=True)

        for link in links:
            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                continue

            if not filter_education(title, title):
                continue

            href = link.get("href", "")
            full_url = fix_url(href, "https://reliefweb.int")
            country = detect_country(title)

            results.append(
                {
                    "title": title[:150],
                    "organization": "ReliefWeb",
                    "country": country,
                    "description": "",
                    "budget": "",
                    "deadline": "",
                    "url": full_url,
                    "date": datetime.today().strftime("%Y-%m-%d"),
                    "source": "reliefweb",
                }
            )

    except:
        pass

    return results


def scrape_tendersontime():
    return create_scraper(
        "TendersOnTime", "https://www.tendersontime.com", ["/africa-tenders"]
    )()


def scrape_globaltenders():
    return create_scraper("GlobalTenders", "https://www.globaltenders.com", [""])()


def scrape_tendersinfo():
    return create_scraper(
        "TendersInfo", "https://www.tendersinfo.com", ["/global-Africa-tenders.php"]
    )()


def scrape_portal_maroc():
    return create_scraper("Maroc Portal", "https://www.marchespublics.gov.ma", [""])()


def scrape_armp_cameroon():
    return create_scraper("ARMP Cameroon", "https://www.armp.cm", [""])()


def scrape_armp_senegal():
    return create_scraper("ARMP Senegal", "https://www.marchespublics.sn", [""])()


def scrape_sigmap_civ():
    return create_scraper("SIGMAP", "https://www.sigmap.org", [""])()


def scrape_tuneps():
    return create_scraper("TUNEPS", "https://www.tuneps.tn", [""])()


def scrape_ministere_maroc():
    return create_scraper("Ministere Maroc", "https://www.men.gov.ma", [""])()


def scrape_ministere_tunisie():
    return create_scraper("Ministere Tunisie", "https://www.education.gov.tn", [""])()


def scrape_minesup_cameroon():
    return create_scraper("MINESUP", "https://www.minesup.gov.cm", [""])()


def scrape_menetfp_civ():
    return create_scraper("MENETFP", "https://www.menetfp.ci", [""])()


def scrape_devex():
    return create_scraper("Devex", "https://www.devex.com", ["/funding", "/jobs"])()


def scrape_unicef():
    return create_scraper(
        "UNICEF", "https://www.unicef.org", ["/supply/procurement", "/about-us"]
    )()


def scrape_unesco():
    return create_scraper("UNESCO", "https://en.unesco.org", ["/career", "/jobs"])()


def scrape_bdeac():
    return create_scraper("BDEAC", "https://www.bdeac.int", [""])()


# ========= TEST =========
if __name__ == "__main__":
    print("=== Testing scrapers ===")
    for name in ["undp", "afd", "boad", "relieweb"]:
        try:
            func = eval(f"scrape_{name}")
            data = func()
            print(f"{name}: {len(data)}")
        except:
            print(f"{name}: ERROR")
