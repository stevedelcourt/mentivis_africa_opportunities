import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
from config import SCRAPER_SETTINGS


URL = "https://www.menetfp.ci"


def scrape_menetfp_civ():
    opportunities = []

    user_agent = random.choice(SCRAPER_SETTINGS["user_agents"])
    headers = {"User-Agent": user_agent}

    try:
        res = requests.get(URL, headers=headers, timeout=SCRAPER_SETTINGS["timeout"])

        if res.status_code != 200:
            print(f"MENETFP: Status {res.status_code}")
            return opportunities

        soup = BeautifulSoup(res.text, "lxml")

        items = soup.select(
            "div.news, article, .appel-offre, .marche, .project, .programme"
        )

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
                        "organization": "MENETFP Côte d'Ivoire",
                        "organization_type": "ministere",
                        "country": "Côte d'Ivoire",
                        "budget": "",
                        "deadline": "",
                        "url": href,
                        "date": datetime.today().strftime("%Y-%m-%d"),
                        "source": "menetfp_civ",
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
                            "organization": "MENETFP Côte d'Ivoire",
                            "organization_type": "ministere",
                            "country": "Côte d'Ivoire",
                            "budget": "",
                            "deadline": "",
                            "url": link or URL,
                            "date": datetime.today().strftime("%Y-%m-%d"),
                            "source": "menetfp_civ",
                        }
                    )

    except Exception as e:
        print(f"MENETFP scraping error: {e}")

    return opportunities


if __name__ == "__main__":
    data = scrape_menetfp_civ()
    print(f"Found {len(data)} opportunities from MENETFP")
