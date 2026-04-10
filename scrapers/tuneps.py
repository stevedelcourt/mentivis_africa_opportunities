import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
from config import SCRAPER_SETTINGS


URLS = [
    "https://www.tuneps.tn",
    "https://tuneps.tn",
]


def scrape_tuneps():
    opportunities = []

    user_agent = random.choice(SCRAPER_SETTINGS["user_agents"])
    headers = {"User-Agent": user_agent}

    for URL in URLS:
        try:
            res = requests.get(URL, headers=headers, timeout=15)
            if res.status_code == 200:
                break
        except:
            continue

    try:
        if res.status_code != 200:
            return opportunities

        soup = BeautifulSoup(res.text, "lxml")

        all_links = soup.find_all("a", href=True)
        links = [
            a
            for a in all_links
            if a.get_text(strip=True) and len(a.get_text(strip=True)) > 10
        ][:30]

        for link in links:
            title = link.get_text(strip=True)
            href = link.get("href", "")
            if not href.startswith("http"):
                href = URL + href

            opportunities.append(
                {
                    "title": title,
                    "description": title,
                    "organization": "TUNEPS Tunisia",
                    "organization_type": "gouvernement",
                    "country": "Tunisie",
                    "budget": "",
                    "deadline": "",
                    "url": href,
                    "date": datetime.today().strftime("%Y-%m-%d"),
                    "source": "tuneps",
                }
            )
    except Exception as e:
        print(f"TUNEPS error: {e}")

    return opportunities


if __name__ == "__main__":
    data = scrape_tuneps()
    print(f"Found {len(data)} opportunities from TUNEPS")
