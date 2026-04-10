from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
from bs4 import BeautifulSoup
import time
import re


def get_selenium_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    )

    try:
        return webdriver.Chrome(options=options)
    except:
        return None


def scrape_undp():
    """Scrape UNDP procurement notices - extract actual tenders"""
    opportunities = []
    driver = None

    african_countries = {
        "senegal": "Sénégal",
        "cote d'ivoire": "Côte d'Ivoire",
        "ivory coast": "Côte d'Ivoire",
        "morocco": "Maroc",
        "tunisia": "Tunisie",
        "cameroon": "Cameroun",
        "mali": "Mali",
        "burkina": "Burkina Faso",
        "benin": "Bénin",
        "togo": "Togo",
        "niger": "Niger",
        "guinea": "Guinée",
        "congo": "Congo",
        "gabon": "Gabon",
        "madagascar": "Madagascar",
    }

    try:
        driver = get_selenium_driver()
        if not driver:
            return opportunities

        # Try to filter by Africa
        driver.get("https://procurement-notices.undp.org/")
        time.sleep(8)

        # Find Africa filter button
        try:
            africa_link = driver.find_element(
                By.XPATH, "//a[contains(text(), 'Africa')]"
            )
            africa_link.click()
            time.sleep(3)
        except:
            pass

        soup = BeautifulSoup(driver.page_source, "lxml")

        # Find all notice entries - they have title spans
        titles = soup.select("span.title, div.title, h3, a[href*='notice']")

        if not titles:
            # Try finding tables with tender data
            rows = soup.select("table tbody tr, div.notice-row")
            for row in rows:
                title_elem = row.select_one("span.title, td:first-child, a")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                if not title or len(title) < 10:
                    continue

                # Get parent link for URL
                link = title_elem.find_parent("a")
                href = link.get("href", "") if link else ""

                # Extract ref number
                ref_match = re.search(r"(UNDP-[A-Z]{3}-\d+)", title)
                ref = ref_match.group(1) if ref_match else ""

                # Determine deadline
                deadline = ""
                deadline_elem = row.select_one("span.deadline, td:nth-child(5)")
                if deadline_elem:
                    deadline = deadline_elem.get_text(strip=True)

                # Extract country
                country = ""
                title_lower = title.lower()
                for hint, c in african_countries.items():
                    if hint in title_lower:
                        country = c
                        break

                if href and not href.startswith("http"):
                    href = "https://procurement-notices.undp.org" + href

                opportunities.append(
                    {
                        "title": title[:200],
                        "description": f"Ref: {ref}" if ref else title[:300],
                        "organization": "UNDP",
                        "organization_type": "onu",
                        "country": country,
                        "budget": "",
                        "deadline": deadline,
                        "url": href or "https://procurement-notices.undp.org/",
                        "date": datetime.today().strftime("%Y-%m-%d"),
                        "source": "undp",
                    }
                )

        # Extract from links if no table found
        all_links = soup.find_all("a", href=True)
        for link in all_links:
            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                continue

            # Skip navigation links
            nav_words = [
                "about",
                "supplier",
                "training",
                "strategy",
                "principle",
                "eligibility",
                "protest",
                "faq",
                "statistics",
                "guidance",
                "conduct",
                "sanction",
            ]
            if any(w in title.lower() for w in nav_words):
                continue

            href = link.get("href", "")
            if href.startswith("/"):
                href = "https://procurement-notices.undp.org" + href

            # Check if this is a notice link
            if "notice" not in href.lower() and "procurement" not in href.lower():
                continue

            # Extract country
            country = ""
            title_lower = title.lower()
            for hint, c in african_countries.items():
                if hint in title_lower:
                    country = c
                    break

            # Extract ref number
            ref_match = re.search(r"(UNDP-[A-Z]{3}-\d+)", title)
            ref = ref_match.group(1) if ref_match else ""

            opportunities.append(
                {
                    "title": title[:200],
                    "description": f"Ref: {ref}" if ref else title[:300],
                    "organization": "UNDP",
                    "organization_type": "onu",
                    "country": country,
                    "budget": "",
                    "deadline": "",
                    "url": href,
                    "date": datetime.today().strftime("%Y-%m-%d"),
                    "source": "undp",
                }
            )

            if len(opportunities) >= 40:
                break

    except Exception as e:
        print(f"UNDP error: {e}")
    finally:
        if driver:
            driver.quit()

    return opportunities


def scrape_bad():
    """Scrape AfDB procurement"""
    opportunities = []
    driver = None

    african_countries = {
        "senegal": "Sénégal",
        "cote d'ivoire": "Côte d'Ivoire",
        "morocco": "Maroc",
        "tunisia": "Tunisie",
        "cameroon": "Cameroun",
        "mali": "Mali",
    }

    try:
        driver = get_selenium_driver()
        if not driver:
            return opportunities

        url = "https://www.afdb.org/en/projects-and-operations/procurement"
        driver.get(url)
        time.sleep(8)

        soup = BeautifulSoup(driver.page_source, "lxml")

        all_links = soup.find_all("a", href=True)

        for link in all_links:
            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                continue

            href = link.get("href", "")
            if not href:
                continue

            if href.startswith("/"):
                href = "https://www.afdb.org" + href

            # Filter for project/procurement links only
            if "project" not in href.lower() and "procurement" not in href.lower():
                continue

            # Extract country
            country = ""
            title_lower = title.lower()
            for hint, c in african_countries.items():
                if hint in title_lower:
                    country = c
                    break

            opportunities.append(
                {
                    "title": title[:200],
                    "description": title[:300],
                    "organization": "AfDB (BAD)",
                    "organization_type": "multilateral",
                    "country": country,
                    "budget": "",
                    "deadline": "",
                    "url": href,
                    "date": datetime.today().strftime("%Y-%m-%d"),
                    "source": "bad",
                }
            )

            if len(opportunities) >= 40:
                break

    except Exception as e:
        print(f"AfDB error: {e}")
    finally:
        if driver:
            driver.quit()

    return opportunities


if __name__ == "__main__":
    print("UNDP:", len(scrape_undp()))
    print("AfDB:", len(scrape_bad()))
