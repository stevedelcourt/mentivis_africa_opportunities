import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
from config import SCRAPER_SETTINGS


URL = "https://www.unesco.org/en/vacancies"


def scrape_unesco():
    opportunities = []

    user_agent = random.choice(SCRAPER_SETTINGS["user_agents"])
    headers = {"User-Agent": user_agent}

    try:
        res = requests.get(URL, headers=headers, timeout=15)

        if res.status_code != 200:
            return opportunities

        soup = BeautifulSoup(res.text, "lxml")

        all_links = soup.find_all("a", href=True)
        links = [
            a
            for a in all_links
            if a.get_text(strip=True) and len(a.get_text(strip=True)) > 15
        ][:40]

        for link in links:
            title = link.get_text(strip=True)
            href = link.get("href", "")
            if href and not href.startswith("http"):
                href = "https://www.unesco.org" + href

            opportunities.append(
                {
                    "title": title,
                    "description": title,
                    "organization": "UNESCO",
                    "organization_type": "onu",
                    "country": "",
                    "budget": "",
                    "deadline": "",
                    "url": href,
                    "date": datetime.today().strftime("%Y-%m-%d"),
                    "source": "unesco",
                }
            )

    except Exception as e:
        print(f"UNESCO error: {e}")

    return opportunities


if __name__ == "__main__":
    data = scrape_unesco()
    print(f"Found {len(data)} opportunities from UNESCO")
