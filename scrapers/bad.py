from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from bs4 import BeautifulSoup
import time


def get_selenium_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    )

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
    except:
        pass

    return driver


def scrape_with_selenium(url, wait_selector=None, timeout=15):
    """Scrape using Selenium for JS-heavy sites"""
    opportunities = []
    driver = None

    try:
        driver = get_selenium_driver()
        if not driver:
            return opportunities

        driver.get(url)

        if wait_selector:
            try:
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
                )
            except:
                pass

        time.sleep(3)

        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")

        all_links = soup.find_all("a", href=True)

        for link in all_links:
            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                continue

            href = link.get("href", "")
            if not href:
                continue

            if href.startswith("/"):
                href = url + href

            if not any(
                x in href.lower()
                for x in ["project", "procurement", "tender", "notice", "opportunity"]
            ):
                continue

            opportunities.append(
                {
                    "title": title[:200],
                    "description": title[:300],
                    "organization": "World Bank",
                    "organization_type": "multilateral",
                    "country": "",
                    "budget": "",
                    "deadline": "",
                    "url": href,
                    "date": datetime.today().strftime("%Y-%m-%d"),
                    "source": "world_bank",
                }
            )

    except Exception as e:
        print(f"Selenium error: {e}")
    finally:
        if driver:
            driver.quit()

    return opportunities


def scrape_world_bank():
    opportunities = []

    urls = [
        "https://projects.worldbank.org/en/projects-operations",
        "https://www.worldbank.org/en/projects-operations/procurement",
    ]

    for url in urls:
        data = scrape_with_selenium(url, "a[href*='/project/']", 10)
        if data:
            opportunities.extend(data)
            break

    return opportunities[:50]


def scrape_bad():
    opportunities = []

    urls = [
        "https://www.afdb.org/en/projects-and-operations/procurement",
    ]

    for url in urls:
        data = scrape_with_selenium(url, "a[href*='/project/']", 10)
        if data:
            for op in data:
                op["organization"] = "AfDB (BAD)"
            opportunities.extend(data)
            break

    return opportunities[:50]


if __name__ == "__main__":
    print("World Bank:", len(scrape_world_bank()))
    print("AfDB:", len(scrape_bad()))
