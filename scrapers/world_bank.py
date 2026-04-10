import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
from config import SCRAPER_SETTINGS


URL = "https://projects.worldbank.org/en/projects-operations/projects-list?lang=en&country=AFR"


def scrape_world_bank():
    opportunities = []

    user_agent = random.choice(SCRAPER_SETTINGS["user_agents"])
    headers = {"User-Agent": user_agent}

    try:
        res = requests.get(URL, headers=headers, timeout=SCRAPER_SETTINGS["timeout"])

        if res.status_code != 200:
            print(f"World Bank: Status {res.status_code}")
            return opportunities

        soup = BeautifulSoup(res.text, "lxml")

        projects = soup.select(
            "div.project-item, div.wb-item, article.project, div.results-row"
        )

        if not projects:
            projects = soup.select("tr.data-row, div.project-row")

        if not projects:
            all_links = soup.find_all("a", href=True)
            project_links = [a for a in all_links if "/projects/" in a.get("href", "")][
                :20
            ]

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
                            "country": "Africa",
                            "budget": "",
                            "deadline": "",
                            "url": href,
                            "date": datetime.today().strftime("%Y-%m-%d"),
                            "source": "world_bank",
                        }
                    )
        else:
            for p in projects[:30]:
                title_elem = p.select_one("h2, h3, .title, .project-title, a")
                desc_elem = p.select_one("p, .description, .summary")
                country_elem = p.select_one(".country, .location")
                budget_elem = p.select_one(".amount, .budget")

                title = title_elem.get_text(strip=True) if title_elem else ""
                desc = desc_elem.get_text(strip=True) if desc_elem else ""
                country = (
                    country_elem.get_text(strip=True) if country_elem else "Africa"
                )
                budget = budget_elem.get_text(strip=True) if budget_elem else ""

                if title and len(title) > 5:
                    link = (
                        title_elem.get("href")
                        if title_elem and title_elem.name == "a"
                        else ""
                    )
                    if not link.startswith("http") and link:
                        link = "https://projects.worldbank.org" + link

                    opportunities.append(
                        {
                            "title": title,
                            "description": desc or title,
                            "organization": "World Bank",
                            "organization_type": "multilateral",
                            "country": country,
                            "budget": budget,
                            "deadline": "",
                            "url": link or URL,
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
