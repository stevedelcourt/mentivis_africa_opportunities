from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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


def normalize_url(href, base_url="https://procurement-notices.undp.org"):
    """Ensure URL is complete"""
    if not href:
        return base_url
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return base_url + href
    return base_url + "/" + href


def scrape_undp():
    """Scrape UNDP with proper full URLs"""
    opportunities = []
    driver = None

    BASE_URL = "https://procurement-notices.undp.org"

    african_countries = {
        "senegal": "Sénégal",
        "cote d'ivoire": "Côte d'Ivoire",
        "morocco": "Maroc",
        "tunisia": "Tunisie",
        "cameroon": "Cameroun",
        "mali": "Mali",
        "burkina": "Burkina Faso",
        "benin": "Bénin",
        "togo": "Togo",
        "niger": "Niger",
        "guinea": "Guinée",
    }

    try:
        driver = get_selenium_driver()
        if not driver:
            return opportunities

        driver.get(BASE_URL + "/")
        time.sleep(8)

        soup = BeautifulSoup(driver.page_source, "lxml")

        # Find all notice links - usually in tables or with notice_id
        all_links = soup.find_all("a", href=True)

        for link in all_links:
            href = link.get("href", "")
            title = link.get_text(strip=True)

            if not title or len(title) < 15:
                continue

            # Skip navigation
            if any(
                w in title.lower()
                for w in ["about", "supplier", "training", "faq", "principle"]
            ):
                continue

            # Check if it's a notice link
            if "notice" in href or "view" in href or "notice_id" in href:
                full_url = normalize_url(href, BASE_URL)

                # Extract country
                country = ""
                for hint, c in african_countries.items():
                    if hint in title.lower():
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
                        "url": full_url,
                        "date": datetime.today().strftime("%Y-%m-%d"),
                        "source": "undp",
                    }
                )

            if len(opportunities) >= 50:
                break

    except Exception as e:
        print(f"UNDP error: {e}")
    finally:
        if driver:
            driver.quit()

    return opportunities


if __name__ == "__main__":
    print("UNDP:", len(scrape_undp()))
