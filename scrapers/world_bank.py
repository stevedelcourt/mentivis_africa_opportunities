import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
from config import SCRAPER_SETTINGS


URL = "https://projects.worldbank.org/en/projects-operations/project-by-country"


def scrape_world_bank():
    opportunities = []

    user_agent = random.choice(SCRAPER_SETTINGS["user_agents"])
    headers = {"User-Agent": user_agent}

    countries = [
        ("senegal", "Senegal"),
        ("cote-d-ivoire", "Côte d'Ivoire"),
        ("morocco", "Morocco"),
        ("tunisia", "Tunisia"),
        ("cameroon", "Cameroon"),
        ("mali", "Mali"),
        ("burkina-faso", "Burkina Faso"),
        ("benin", "Benin"),
        ("togo", "Togo"),
        ("niger", "Niger"),
    ]

    for country_code, country_name in countries[:5]:
        try:
            country_url = f"https://projects.worldbank.org/en/projects-operations/project-by-country/{country_code.upper()}"
            res = requests.get(country_url, headers=headers, timeout=10)

            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.text, "lxml")

            all_links = soup.find_all("a", href=True)
            project_links = [
                a
                for a in all_links
                if "/projects/" in a.get("href", "") and a.get_text(strip=True)
            ][:10]

            for link in project_links:
                title = link.get_text(strip=True)
                if title and len(title) > 10:
                    href = link.get("href", "")
                    if not href.startswith("http"):
                        href = "https://projects.worldbank.org" + href

                    opportunities.append(
                        {
                            "title": title,
                            "description": title,
                            "organization": "World Bank",
                            "organization_type": "multilateral",
                            "country": country_name,
                            "budget": "",
                            "deadline": "",
                            "url": href,
                            "date": datetime.today().strftime("%Y-%m-%d"),
                            "source": "world_bank",
                        }
                    )
        except Exception as e:
            print(f"World Bank scraping error: {e}")

    return opportunities


if __name__ == "__main__":
    data = scrape_world_bank()
    print(f"Found {len(data)} opportunities from World Bank")
