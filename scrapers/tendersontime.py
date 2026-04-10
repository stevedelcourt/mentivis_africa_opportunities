import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
from config import SCRAPER_SETTINGS


URL = "https://www.tendersontime.com/africa-tenders"


def scrape_tendersontime():
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
            if not href.startswith("http"):
                href = "https://www.tendersontime.com" + href

            opportunities.append(
                {
                    "title": title,
                    "description": title,
                    "organization": "TendersOnTime",
                    "organization_type": "aggregator",
                    "country": "",
                    "budget": "",
                    "deadline": "",
                    "url": href,
                    "date": datetime.today().strftime("%Y-%m-%d"),
                    "source": "tendersontime",
                }
            )
    except Exception as e:
        print(f"TendersOnTime error: {e}")

    return opportunities


if __name__ == "__main__":
    data = scrape_tendersontime()
    print(f"Found {len(data)} opportunities from TendersOnTime")
