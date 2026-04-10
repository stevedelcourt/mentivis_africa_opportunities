import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
from config import SCRAPER_SETTINGS


URLS = [
    "https://www.afd.fr/fr/appels-a-projets",
    "https://www.afd.fr/en/calls-for-projects",
]


def scrape_afd():
    opportunities = []

    user_agent = random.choice(SCRAPER_SETTINGS["user_agents"])
    headers = {"User-Agent": user_agent}

    for base_url in URLS:
        try:
            res = requests.get(base_url, headers=headers, timeout=15)

            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.text, "lxml")

            all_links = soup.find_all("a", href=True)
            links = [
                a
                for a in all_links
                if a.get_text(strip=True) and len(a.get_text(strip=True)) > 15
            ][:40]

            for link in links:
                title = link.get_text(strip=True)
                if "appels" in title.lower() or "projet" in title.lower():
                    href = link.get("href", "")
                    if href and not href.startswith("http"):
                        href = "https://www.afd.fr" + href

                    opportunities.append(
                        {
                            "title": title,
                            "description": title,
                            "organization": "AFD",
                            "organization_type": "bailleur",
                            "country": "",
                            "budget": "",
                            "deadline": "",
                            "url": href,
                            "date": datetime.today().strftime("%Y-%m-%d"),
                            "source": "afd",
                        }
                    )
        except Exception as e:
            print(f"AFD error: {e}")

    return opportunities


if __name__ == "__main__":
    data = scrape_afd()
    print(f"Found {len(data)} opportunities from AFD")
