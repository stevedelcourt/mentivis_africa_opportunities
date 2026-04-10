import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
from config import SCRAPER_SETTINGS


URL = "https://www.boad.org"


def scrape_boad():
    opportunities = []

    user_agent = random.choice(SCRAPER_SETTINGS["user_agents"])
    headers = {"User-Agent": user_agent}

    try:
        res = requests.get(URL, headers=headers, timeout=SCRAPER_SETTINGS["timeout"])

        if res.status_code != 200:
            print(f"BOAD: Status {res.status_code}")
            return opportunities

        soup = BeautifulSoup(res.text, "lxml")

        items = soup.select("div.project, article, .projet, .appel-offre, .tender")

        if not items:
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
                    href = URL + href

                opportunities.append(
                    {
                        "title": title,
                        "description": title,
                        "organization": "BOAD",
                        "organization_type": "banque_regionale",
                        "country": "West Africa",
                        "budget": "",
                        "deadline": "",
                        "url": href,
                        "date": datetime.today().strftime("%Y-%m-%d"),
                        "source": "boad",
                    }
                )
        else:
            for item in items[:30]:
                title_elem = item.select_one("h2, h3, h4, a, .title")
                desc_elem = item.select_one("p, .description")

                title = title_elem.get_text(strip=True) if title_elem else ""
                desc = desc_elem.get_text(strip=True) if desc_elem else ""

                if title and len(title) > 5:
                    link = (
                        title_elem.get("href")
                        if title_elem and title_elem.name == "a"
                        else ""
                    )
                    if link and not link.startswith("http"):
                        link = URL + link

                    opportunities.append(
                        {
                            "title": title,
                            "description": desc or title,
                            "organization": "BOAD",
                            "organization_type": "banque_regionale",
                            "country": "West Africa",
                            "budget": "",
                            "deadline": "",
                            "url": link or URL,
                            "date": datetime.today().strftime("%Y-%m-%d"),
                            "source": "boad",
                        }
                    )

    except Exception as e:
        print(f"BOAD scraping error: {e}")

    return opportunities


if __name__ == "__main__":
    data = scrape_boad()
    print(f"Found {len(data)} opportunities from BOAD")
