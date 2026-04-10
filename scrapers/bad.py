import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
from config import SCRAPER_SETTINGS


URLS = [
    "https://www.afdb.org/en/projects-and-operations/procurement",
    "https://www.afdb.org/en/projects-operations",
]


def scrape_bad():
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
            project_links = [
                a
                for a in all_links
                if (
                    "/project/" in a.get("href", "")
                    or "/procurement/" in a.get("href", "")
                )
                and a.get_text(strip=True)
                and len(a.get_text(strip=True)) > 10
            ][:30]

            for link in project_links:
                title = link.get_text(strip=True)
                href = link.get("href", "")
                if not href.startswith("http"):
                    href = "https://www.afdb.org" + href

                opportunities.append(
                    {
                        "title": title,
                        "description": title,
                        "organization": "AfDB (BAD)",
                        "organization_type": "multilateral",
                        "country": "Africa",
                        "budget": "",
                        "deadline": "",
                        "url": href,
                        "date": datetime.today().strftime("%Y-%m-%d"),
                        "source": "bad",
                    }
                )
        except Exception as e:
            print(f"AfDB error: {e}")
            continue

    return opportunities


if __name__ == "__main__":
    data = scrape_bad()
    print(f"Found {len(data)} opportunities from AfDB")
