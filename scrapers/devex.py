import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
from config import SCRAPER_SETTINGS


URL = "https://www.devex.com"


def scrape_devex():
    opportunities = []

    user_agent = random.choice(SCRAPER_SETTINGS["user_agents"])
    headers = {"User-Agent": user_agent}

    paths = ["/funding", "/jobs", "/organizations"]

    for path in paths:
        try:
            res = requests.get(URL + path, headers=headers, timeout=15)

            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.text, "lxml")

            all_links = soup.find_all("a", href=True)
            links = [
                a
                for a in all_links
                if a.get_text(strip=True) and len(a.get_text(strip=True)) > 20
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
                        "organization": "Devex",
                        "organization_type": "platform",
                        "country": "",
                        "budget": "",
                        "deadline": "",
                        "url": href,
                        "date": datetime.today().strftime("%Y-%m-%d"),
                        "source": "devex",
                    }
                )
        except Exception as e:
            continue

    return opportunities


if __name__ == "__main__":
    data = scrape_devex()
    print(f"Found {len(data)} opportunities from Devex")
