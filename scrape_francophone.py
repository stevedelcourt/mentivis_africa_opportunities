#!/usr/bin/env python3
"""
Mentivis - Francophone Africa Tender Scraper
Focus: Education/Formation projects with DIRECT tender URLs
"""

import os
import re
import time
import random
from datetime import datetime
from urllib.parse import urljoin
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Try to import selenium
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# ========== CONFIG ==========
INCLUDE = [
    "formation",
    "education",
    "training",
    "apprentissage",
    "elearning",
    "e-learning",
    "tvet",
    "skills",
    "competences",
    "capacity building",
    "capacity development",
    "teacher",
    "curriculum",
    "learning",
    "pedagogy",
    "university",
    "ecole",
    "employability",
    "youth employment",
    "job training",
    "career",
    "academic",
    "pedagog",
    "didactic",
    "AI training",
    "AI platform",
    "digital learning",
    "online learning",
    "learning platform",
    "partenariat",
    "partnership",
    "chercheur",
    "research",
    "developpement",
    "development",
    "projet",
    "projets",
    "insertion",
    "emploi",
    "jeunes",
    "youth",
    "femme",
    "genre",
    "concours",
    "appel",
    "avis",
    "recrutement",
    "bourse",
    "formation professionnelle",
    "superieur",
    "superieure",
    "higher education",
    "enseigner",
    "educational",
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
    "who-we-are",
    "/about",
    "/contact",
    "/faq",
    "filtres",
    "/news/",
    "/events/",
    "/blog/",
]

COUNTRIES = {
    "senegal": "Senegal",
    "cote d'ivoire": "Côte d'Ivoire",
    "morocco": "Maroc",
    "maroc": "Maroc",
    "tunisia": "Tunisie",
    "cameroon": "Cameroun",
    "cameroun": "Cameroun",
    "mali": "Mali",
    "burkina": "Burkina Faso",
    "benin": "Benin",
    "togo": "Togo",
    "niger": "Niger",
    "guinea": "Guinée",
    "gabon": "Gabon",
    "madagascar": "Madagascar",
    "chad": "Tchad",
    "congo": "Congo",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# ========== UTILS ==========
def is_valid_tender_url(url, title=""):
    """Check URL is specific tender, not generic page"""
    if not url:
        return False

    url_lower = url.lower()
    title_lower = title.lower() if title else ""

    # INVALID patterns
    invalid = [
        "/about",
        "/who-we-are",
        "/contact",
        "/faq",
        "/home",
        "/index",
        "/news",
        "/events",
        "/blog",
        "/careers",
        "/jobs",
        "filtres",
        "type=projets",
        "val=",
        "/annonce",
        "/actualite",
        "/fr/notre-",
        "/fr/les-",
    ]
    for inv in invalid:
        if inv in url_lower:
            return False

    # Must have education in title
    if title:
        if not any(kw in title_lower for kw in INCLUDE):
            return False

    # Must have tender-like patterns or ID
    valid_patterns = [
        "nego_id=",
        "tender",
        "procurement",
        "bid",
        "rfq",
        "ref_no=",
        "ref=",
        "notice",
        "request_for",
        "spg=",
        "cn=",
        "view_notice",
        "opportunity",
        "project_id=",
        "/projet/",
        "/appel/",
        "article?id=",
        "/appels-a-projets/",
        "/calls-for-projects",
        "/procurement-notices",
        "/index.php/",
    ]

    for pat in valid_patterns:
        if pat in url_lower:
            return True

    # Has numeric ID parameter = likely specific page
    if re.search(r"[?&][a-z_]*id=\d+", url_lower):
        return True

    return False


def detect_country(text):
    """Detect Francophone Africa country"""
    text_lower = text.lower()
    for ckey, cname in COUNTRIES.items():
        if ckey in text_lower:
            return cname
    return ""


def fix_url(href, base):
    """Fix URL to be absolute"""
    if not href:
        return base
    href = href.strip()
    if href.startswith("http"):
        return href
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return base.rstrip("/") + href
    return base + "/" + href


def random_delay():
    """Random delay to avoid blocking"""
    time.sleep(random.uniform(1, 3))


# ========== SCRAPERS ==========
def scrape_undp():
    """UNDP - WORKS - uses search"""
    results = []
    base = "https://procurement-notices.undp.org"

    for kw in ["education", "formation", "training", "skills"]:
        try:
            url = f"{base}/search.cfm?search={kw}"
            r = requests.get(url, headers=HEADERS, timeout=15, verify=False)
            random_delay()

            soup = BeautifulSoup(r.text, "lxml")
            links = soup.find_all("a", href=True)

            for link in links:
                href = link.get("href", "")
                title = link.get_text(strip=True)

                if "nego_id=" in href and title and len(title) > 15:
                    match = re.search(r"nego_id=(\d+)", href)
                    if match:
                        full_url = (
                            f"{base}/view_negotiation.cfm?nego_id={match.group(1)}"
                        )

                        title_lower = title.lower()
                        if not any(inc in title_lower for inc in INCLUDE):
                            continue
                        if any(ex in title_lower for ex in EXCLUDE):
                            continue

                        results.append(
                            {
                                "title": title[:100],
                                "organization": "UNDP",
                                "country": detect_country(title),
                                "url": full_url,
                                "source": "UNDP",
                            }
                        )
        except Exception as e:
            print(f"UNDP error: {e}")
            continue

    return results[:50]


def scrape_afd():
    """AFD - Returns list pages, need to extract actual projects"""
    results = []
    base = "https://www.afd.fr"

    urls = [
        "https://www.afd.fr/fr/appels-a-projets/liste?status%5Bongoing%5D=ongoing&status%5Bclosed%5D=closed",
        "https://www.afd.fr/en/calls-for-projects/list",
    ]

    # Try with Selenium for JS-rendered content
    if SELENIUM_AVAILABLE:
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(options=options)

            for url in urls:
                try:
                    driver.get(url)
                    time.sleep(3)

                    soup = BeautifulSoup(driver.page_source, "lxml")
                    links = soup.find_all("a", href=True)

                    seen = set()
                    for link in links:
                        href = link.get("href", "")
                        title = link.get_text(strip=True)

                        # Skip duplicates and list pages
                        if href in seen:
                            continue
                        seen.add(href)

                        # Look for specific project URLs
                        if (
                            "/appels-a-projets/" in href
                            and "liste" not in href
                            and len(title) > 20
                        ):
                            full_url = fix_url(href, base)

                            title_lower = title.lower()
                            if not any(inc in title_lower for inc in INCLUDE):
                                continue

                            results.append(
                                {
                                    "title": title[:100],
                                    "organization": "AFD",
                                    "country": detect_country(title),
                                    "url": full_url,
                                    "source": "AFD",
                                }
                            )
                except Exception as e:
                    print(f"AFD Selenium error: {e}")
                    continue

            driver.quit()
        except Exception as e:
            print(f"AFD Selenium init error: {e}")

    # Fallback to requests - use closed projects too
    if len(results) < 3:
        test_urls = [
            "https://www.afd.fr/fr/appels-a-projets/liste?status%5Bongoing%5D=ongoing&status%5Bclosed%5D=closed",
        ]

        for url in test_urls:
            try:
                r = requests.get(url, headers=HEADERS, timeout=15)
                random_delay()

                soup = BeautifulSoup(r.text, "lxml")
                links = soup.find_all("a", href=True)

                seen = set()
                for link in links:
                    href = link.get("href", "")
                    title = link.get_text(strip=True)

                    if href in seen:
                        continue
                    seen.add(href)

                    if (
                        "/appels-a-projets/" in href
                        and "liste" not in href
                        and len(title) > 20
                    ):
                        full_url = fix_url(href, base)

                        title_lower = title.lower()
                        if not any(inc in title_lower for inc in INCLUDE):
                            continue

                        # Avoid duplicates
                        if not any(r["url"] == full_url for r in results):
                            results.append(
                                {
                                    "title": title[:100],
                                    "organization": "AFD",
                                    "country": detect_country(title),
                                    "url": full_url,
                                    "source": "AFD",
                                }
                            )
            except Exception as e:
                print(f"AFD error: {e}")
                continue

    return results[:30]


def scrape_armp_cameroon():
    """ARMP Cameroon - Returns articles"""
    results = []
    base = "https://www.armp.cm"

    try:
        r = requests.get(base, headers=HEADERS, timeout=15)
        random_delay()

        soup = BeautifulSoup(r.text, "lxml")
        links = soup.find_all("a", href=True)

        for link in links:
            href = link.get("href", "")
            title = link.get_text(strip=True)

            # Look for article pages
            if "article" in href and len(title) > 20:
                full_url = fix_url(href, base)

                title_lower = title.lower()
                if not any(inc in title_lower for inc in INCLUDE):
                    continue

                results.append(
                    {
                        "title": title[:100],
                        "organization": "ARMP Cameroon",
                        "country": "Cameroun",
                        "url": full_url,
                        "source": "ARMP Cameroon",
                    }
                )
    except Exception as e:
        print(f"ARMP Cameroon error: {e}")

    return results[:20]


def scrape_minesup_cameroon():
    """MINESUP Cameroon"""
    results = []
    base = "https://www.minesup.gov.cm"

    try:
        r = requests.get(base, headers=HEADERS, timeout=15)
        random_delay()

        soup = BeautifulSoup(r.text, "lxml")
        links = soup.find_all("a", href=True)

        for link in links:
            href = link.get("href", "")
            title = link.get_text(strip=True)

            if len(title) > 20:
                full_url = fix_url(href, base)

                title_lower = title.lower()
                if not any(inc in title_lower for inc in INCLUDE):
                    continue

                results.append(
                    {
                        "title": title[:100],
                        "organization": "MINESUP Cameroon",
                        "country": "Cameroun",
                        "url": full_url,
                        "source": "MINESUP Cameroon",
                    }
                )
    except Exception as e:
        print(f"MINESUP error: {e}")

    return results[:20]


def scrape_minesup_cameroon():
    """MINESUP Cameroon"""
    results = []
    base = "https://www.minesup.gov.cm"

    try:
        r = requests.get(base, headers=HEADERS, timeout=15)
        random_delay()

        soup = BeautifulSoup(r.text, "lxml")
        links = soup.find_all("a", href=True)

        for link in links:
            href = link.get("href", "")
            title = link.get_text(strip=True)

            if len(title) > 20 and (
                "concours" in href or "avis" in href or "appel" in href
            ):
                full_url = fix_url(href, base)

                title_lower = title.lower()
                if not any(inc in title_lower for inc in INCLUDE):
                    continue

                results.append(
                    {
                        "title": title[:100],
                        "organization": "MINESUP Cameroon",
                        "country": "Cameroun",
                        "url": full_url,
                        "source": "MINESUP Cameroon",
                    }
                )
    except Exception as e:
        print(f"MINESUP error: {e}")

    return results[:20]


def scrape_ministere_tunisie():
    """Ministere Education Tunisia - try different pages"""
    results = []
    base = "https://www.education.gov.tn"

    # Try different page paths
    urls = [
        "https://www.education.gov.tn/?page_id=12",  # النفاذ إلى المعلومة
        "https://www.education.gov.tn/?page_id=321",  # أخلاقيات العون العمومي
    ]

    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            random_delay()

            soup = BeautifulSoup(r.text, "lxml")
            links = soup.find_all("a", href=True)

            for link in links:
                href = link.get("href", "")
                title = link.get_text(strip=True)

                if len(title) > 20 and "page_id" in href:
                    full_url = fix_url(href, base)

                    title_lower = title.lower()
                    if not any(inc in title_lower for inc in INCLUDE):
                        continue

                    results.append(
                        {
                            "title": title[:100],
                            "organization": "Ministere Education TN",
                            "country": "Tunisie",
                            "url": full_url,
                            "source": "Ministere Tunisia",
                        }
                    )
        except Exception as e:
            print(f"Ministere TN error: {e}")
            continue

    # Try with Selenium for JS content
    if not results and SELENIUM_AVAILABLE:
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(options=options)

            url = "https://www.education.gov.tn"
            driver.get(url)
            time.sleep(3)

            soup = BeautifulSoup(driver.page_source, "lxml")
            links = soup.find_all("a", href=True)

            for link in links:
                href = link.get("href", "")
                title = link.get_text(strip=True)

                if len(title) > 20:
                    full_url = fix_url(href, base)

                    title_lower = title.lower()
                    if not any(inc in title_lower for inc in INCLUDE):
                        continue

                    if "/?" in href or "page_id" in href:
                        results.append(
                            {
                                "title": title[:100],
                                "organization": "Ministere Education TN",
                                "country": "Tunisie",
                                "url": full_url,
                                "source": "Ministere Tunisia",
                            }
                        )

            driver.quit()
        except Exception as e:
            print(f"Ministere TN Selenium error: {e}")

    return results[:20]


def scrape_reliefweb():
    """ReliefWeb jobs - use Selenium for JS content"""
    results = []
    base = "https://reliefweb.int"

    # Try with Selenium first
    if SELENIUM_AVAILABLE:
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            driver = webdriver.Chrome(options=options)

            url = "https://reliefweb.int/jobs"
            driver.get(url)
            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, "lxml")
            links = soup.find_all("a", href=True)

            for link in links:
                href = link.get("href", "")
                title = link.get_text(strip=True)

                if len(title) > 20 and "/job/" in href:
                    full_url = fix_url(href, base)

                    title_lower = title.lower()
                    if not any(inc in title_lower for inc in INCLUDE):
                        continue

                    results.append(
                        {
                            "title": title[:100],
                            "organization": "ReliefWeb",
                            "country": detect_country(title),
                            "url": full_url,
                            "source": "ReliefWeb",
                        }
                    )

            driver.quit()
        except Exception as e:
            print(f"ReliefWeb Selenium error: {e}")

    # Fallback to requests
    if not results:
        try:
            url = "https://reliefweb.int/jobs"
            r = requests.get(url, headers=HEADERS, timeout=15)
            random_delay()

            soup = BeautifulSoup(r.text, "lxml")
            links = soup.find_all("a", href=True)

            for link in links:
                href = link.get("href", "")
                title = link.get_text(strip=True)

                if len(title) > 20 and "/job/" in href:
                    full_url = fix_url(href, base)

                    title_lower = title.lower()
                    if not any(inc in title_lower for inc in INCLUDE):
                        continue

                    results.append(
                        {
                            "title": title[:100],
                            "organization": "ReliefWeb",
                            "country": detect_country(title),
                            "url": full_url,
                            "source": "ReliefWeb",
                        }
                    )
        except Exception as e:
            print(f"ReliefWeb error: {e}")

    return results[:20]


def scrape_devex():
    """Devex - use Selenium for JS content"""
    results = []
    base = "https://www.devex.com"

    urls = ["https://www.devex.com/jobs", "https://www.devex.com/funding"]

    # Try with Selenium first
    if SELENIUM_AVAILABLE:
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            driver = webdriver.Chrome(options=options)

            for url in urls:
                try:
                    driver.get(url)
                    time.sleep(5)

                    soup = BeautifulSoup(driver.page_source, "lxml")
                    links = soup.find_all("a", href=True)

                    for link in links:
                        href = link.get("href", "")
                        title = link.get_text(strip=True)

                        if len(title) > 20 and ("job" in href or "project" in href):
                            full_url = fix_url(href, base)

                            title_lower = title.lower()
                            if not any(inc in title_lower for inc in INCLUDE):
                                continue

                            results.append(
                                {
                                    "title": title[:100],
                                    "organization": "Devex",
                                    "country": detect_country(title),
                                    "url": full_url,
                                    "source": "Devex",
                                }
                            )
                except Exception as e:
                    print(f"Devex URL error: {e}")
                    continue

            driver.quit()
        except Exception as e:
            print(f"Devex Selenium init error: {e}")

    # Fallback to requests
    if not results:
        for url in urls:
            try:
                r = requests.get(url, headers=HEADERS, timeout=15)
                random_delay()

                soup = BeautifulSoup(r.text, "lxml")
                links = soup.find_all("a", href=True)

                for link in links:
                    href = link.get("href", "")
                    title = link.get_text(strip=True)

                    if len(title) > 20 and ("job" in href or "project" in href):
                        full_url = fix_url(href, base)

                        title_lower = title.lower()
                        if not any(inc in title_lower for inc in INCLUDE):
                            continue

                        results.append(
                            {
                                "title": title[:100],
                                "organization": "Devex",
                                "country": detect_country(title),
                                "url": full_url,
                                "source": "Devex",
                            }
                        )
            except Exception as e:
                print(f"Devex error: {e}")
                continue

    return results[:20]


def scrape_unesco():
    """UNESCO - career opportunities"""
    results = []
    base = "https://en.unesco.org"

    urls = [
        "https://en.unesco.org/careers",
        "https://en.unesco.org/careers/jobs",
    ]

    if SELENIUM_AVAILABLE:
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(options=options)

            for url in urls:
                try:
                    driver.get(url)
                    time.sleep(3)

                    soup = BeautifulSoup(driver.page_source, "lxml")
                    links = soup.find_all("a", href=True)

                    for link in links:
                        href = link.get("href", "")
                        title = link.get_text(strip=True)

                        if len(title) > 20 and (
                            "job" in href or "career" in href or "vacancy" in href
                        ):
                            full_url = fix_url(href, base)

                            title_lower = title.lower()
                            if not any(inc in title_lower for inc in INCLUDE):
                                continue

                            results.append(
                                {
                                    "title": title[:100],
                                    "organization": "UNESCO",
                                    "country": detect_country(title),
                                    "url": full_url,
                                    "source": "UNESCO",
                                }
                            )
                except Exception as e:
                    continue

            driver.quit()
        except Exception as e:
            print(f"UNESCO Selenium error: {e}")

    if not results:
        for url in urls:
            try:
                r = requests.get(url, headers=HEADERS, timeout=15)
                random_delay()

                soup = BeautifulSoup(r.text, "lxml")
                links = soup.find_all("a", href=True)

                for link in links:
                    href = link.get("href", "")
                    title = link.get_text(strip=True)

                    if len(title) > 20 and ("job" in href or "vacancy" in href):
                        full_url = fix_url(href, base)

                        title_lower = title.lower()
                        if not any(inc in title_lower for inc in INCLUDE):
                            continue

                        results.append(
                            {
                                "title": title[:100],
                                "organization": "UNESCO",
                                "country": detect_country(title),
                                "url": full_url,
                                "source": "UNESCO",
                            }
                        )
            except Exception as e:
                continue

    return results[:20]


# ========== MAIN ==========
def main():
    print("=== Francophone Africa Tender Scraper ===\n")

    scrapers = [
        ("UNDP", scrape_undp),
        ("AFD", scrape_afd),
        ("ARMP Cameroon", scrape_armp_cameroon),
        ("MINESUP", scrape_minesup_cameroon),
        ("Ministere Tunisia", scrape_ministere_tunisie),
        ("ReliefWeb", scrape_reliefweb),
        ("Devex", scrape_devex),
        ("UNESCO", scrape_unesco),
    ]

    all_data = []

    for name, func in scrapers:
        try:
            print(f"Scraping {name}...")
            data = func()
            print(f"  -> {len(data)} results")
            all_data.extend(data)
        except Exception as e:
            print(f"  -> ERROR: {e}")

    # Deduplicate by URL
    seen = set()
    unique = []
    for op in all_data:
        url = op.get("url", "")
        if url and url not in seen:
            seen.add(url)
            unique.append(op)

    all_data = unique

    # Final filter - only valid tender URLs
    filtered = [
        op
        for op in all_data
        if is_valid_tender_url(op.get("url", ""), op.get("title", ""))
    ]
    removed = len(all_data) - len(filtered)
    all_data = filtered

    print(f"\n=== Total: {len(all_data)} tenders (removed {removed} invalid) ===\n")

    # Create DataFrame
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

    # Save
    os.makedirs("data/processed", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/processed/tenders_francophone_{timestamp}.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")

    print(f"Saved: {filename}")
    print(f"Total: {len(df)} tenders\n")

    # Sample
    print("=== SAMPLE (first 5) ===")
    for i, row in df.head(5).iterrows():
        print(f"{row['Number']}. {row['organization']}")
        print(f"   {row['url']}")
        print()

    print("=== BY ORGANIZATION ===")
    print(df["organization"].value_counts())


if __name__ == "__main__":
    main()
