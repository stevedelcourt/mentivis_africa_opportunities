import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
from config import SCRAPER_SETTINGS


URL = "https://www.tendersontime.com/northern-africa-tenders/"


def scrape_tendersontime():
    opportunities = []

    user_agent = random.choice(SCRAPER_SETTINGS["user_agents"])
    headers = {"User-Agent": user_agent}

    try:
        res = requests.get(URL, headers=headers, timeout=SCRAPER_SETTINGS["timeout"])

        if res.status_code != 200:
            print(f"TendersOnTime: Status {res.status_code}")
            return opportunities

        soup = BeautifulSoup(res.text, "lxml")

        items = soup.select("div.tender, article, .tender-item, .tenders-list-item")

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
        else:
            for item in items[:30]:
                title_elem = item.select_one("a, h3, h4, .title")
                desc_elem = item.select_one("p, .description")
                country_elem = item.select_one(".country")
                deadline_elem = item.select_one(".deadline")

                title = title_elem.get_text(strip=True) if title_elem else ""
                desc = desc_elem.get_text(strip=True) if desc_elem else ""
                country = country_elem.get_text(strip=True) if country_elem else ""
                deadline = deadline_elem.get_text(strip=True) if deadline_elem else ""

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
                            "organization": "TendersOnTime",
                            "organization_type": "aggregator",
                            "country": country,
                            "budget": "",
                            "deadline": deadline,
                            "url": link or URL,
                            "date": datetime.today().strftime("%Y-%m-%d"),
                            "source": "tendersontime",
                        }
                    )

    except Exception as e:
        print(f"TendersOnTime scraping error: {e}")

    return opportunities


if __name__ == "__main__":
    data = scrape_tendersontime()
    print(f"Found {len(data)} opportunities from TendersOnTime")
