from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from bs4 import BeautifulSoup
import time
import random


_driver = None


def get_selenium_driver():
    global _driver
    if _driver:
        return _driver

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    try:
        _driver = webdriver.Chrome(options=options)
        return _driver
    except Exception as e:
        print(f"Selenium init error: {e}")
        return None


def close_driver():
    global _driver
    if _driver:
        try:
            _driver.quit()
        except:
            pass
        _driver = None


def scrape_with_selenium(
    url,
    org_name="Organization",
    source_name="source",
    country_hints=None,
    max_results=50,
    wait_time=10,
):
    """
    Generic Selenium scraper for JS-heavy sites
    """
    opportunities = []
    driver = None

    if country_hints is None:
        country_hints = {}

    try:
        driver = get_selenium_driver()
        if not driver:
            return opportunities

        driver.get(url)
        time.sleep(wait_time)

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
                href = url.rstrip("/") + href

            country = ""
            for hint, country_name in country_hints.items():
                if hint.lower() in title.lower():
                    country = country_name
                    break

            opportunities.append(
                {
                    "title": title[:200],
                    "description": title[:300],
                    "organization": org_name,
                    "organization_type": "multilateral",
                    "country": country,
                    "budget": "",
                    "deadline": "",
                    "url": href,
                    "date": datetime.today().strftime("%Y-%m-%d"),
                    "source": source_name,
                }
            )

            if max_results and len(opportunities) >= max_results:
                break

    except Exception as e:
        print(f"Selenium scrape error: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

    return opportunities


def scrape_multiple_sources(
    urls, org_name, source_name, country_hints=None, max_per_source=30
):
    """Scrape multiple URLs with same org"""
    all_data = []

    for url in urls:
        data = scrape_with_selenium(
            url, org_name, source_name, country_hints, max_per_source
        )
        all_data.extend(data)
        if data:
            break

    return all_data
