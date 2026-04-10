import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
from config import SCRAPER_SETTINGS


def scrape_with_selenium_fallback(url, source_name, country_hints=None):
    """Fallback: try requests first"""
    opportunities = []
    user_agent = random.choice(SCRAPER_SETTINGS["user_agents"])
    headers = {"User-Agent": user_agent}

    try:
        res = requests.get(url, headers=headers, timeout=20)
        if res.status_code != 200:
            return opportunities, False

        soup = BeautifulSoup(res.text, "lxml")

        all_links = soup.find_all("a", href=True)

        for link in all_links:
            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                continue

            href = link.get("href", "")
            if not href:
                continue
            if not href.startswith("http"):
                href = url + href

            country = ""
            if country_hints:
                for hint, c in country_hints.items():
                    if hint.lower() in title.lower():
                        country = c
                        break

            opportunities.append(
                {
                    "title": title[:200],
                    "description": title[:300],
                    "organization": "World Bank",
                    "organization_type": "multilateral",
                    "country": country,
                    "budget": "",
                    "deadline": "",
                    "url": href,
                    "date": datetime.today().strftime("%Y-%m-%d"),
                    "source": source_name,
                }
            )

    except Exception as e:
        print(f"{source_name} error: {e}")

    return opportunities, len(opportunities) > 0


def scrape_world_bank():
    opportunities = []

    country_hints = {
        "senegal": "Sénégal",
        "cote d'ivoire": "Côte d'Ivoire",
        "ivory coast": "Côte d'Ivoire",
        "morocco": "Maroc",
        "maroc": "Maroc",
        "tunisia": "Tunisie",
        "tunisie": "Tunisie",
        "cameroon": "Cameroun",
        "cameroun": "Cameroun",
        "mali": "Mali",
        "burkina": "Burkina Faso",
        "benin": "Bénin",
        "togo": "Togo",
        "niger": "Niger",
        "guinea": "Guinée",
    }

    urls = [
        "https://www.worldbank.org/en/projects-operations/procurement",
        "https://projects.worldbank.org/en/projects-operations",
    ]

    for url in urls:
        data, success = scrape_with_selenium_fallback(url, "world_bank", country_hints)
        opportunities.extend(data)
        if success:
            break

    return opportunities


if __name__ == "__main__":
    data = scrape_world_bank()
    print(f"Found {len(data)} opportunities from World Bank")
