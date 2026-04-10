import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
from config import SCRAPER_SETTINGS


URL = "https://ted.europa.eu/en/search?fsr=true&page=200"


def scrape_eu_ted():
    opportunities = []

    user_agent = random.choice(SCRAPER_SETTINGS["user_agents"])
    headers = {"User-Agent": user_agent}

    try:
        res = requests.get(URL, headers=headers, timeout=SCRAPER_SETTINGS["timeout"])

        if res.status_code != 200:
            print(f"EU TED: Status {res.status_code}")
            return opportunities

        soup = BeautifulSoup(res.text, "lxml")

        notices = soup.select(
            "div.search-result, article.result, div.tender-item, .notice"
        )

        if not notices:
            notices = soup.select("div[class*=result], li[class*=item]")

        if not notices:
            all_links = soup.find_all("a", href=True)
            links = [
                a
                for a in all_links
                if "search" not in a.get("href", "")
                and a.get_text(strip=True)
                and len(a.get_text(strip=True)) > 20
            ][:50]

            for link in links:
                title = link.get_text(strip=True)
                href = link.get("href", "")
                if not href.startswith("http"):
                    href = "https://ted.europa.eu" + href

                opportunities.append(
                    {
                        "title": title,
                        "description": title,
                        "organization": "EU TED",
                        "organization_type": "institution",
                        "country": "",
                        "budget": "",
                        "deadline": "",
                        "url": href,
                        "date": datetime.today().strftime("%Y-%m-%d"),
                        "source": "eu_ted",
                    }
                )
        else:
            for notice in notices[:20]:
                title_elem = notice.select_one("h3, h4, a, .title, .notice-title")
                desc_elem = notice.select_one("p, .summary, .description")
                country_elem = notice.select_one(".country, .country-code")

                title = title_elem.get_text(strip=True) if title_elem else ""
                desc = desc_elem.get_text(strip=True) if desc_elem else ""
                country = country_elem.get_text(strip=True) if country_elem else ""

                if title and len(title) > 10:
                    link = (
                        title_elem.get("href")
                        if title_elem and title_elem.name == "a"
                        else ""
                    )
                    if link and not link.startswith("http"):
                        link = "https://ted.europa.eu" + link

                    opportunities.append(
                        {
                            "title": title[:200],
                            "description": desc[:500] or title,
                            "organization": "EU TED",
                            "organization_type": "institution",
                            "country": country,
                            "budget": "",
                            "deadline": "",
                            "url": link or URL,
                            "date": datetime.today().strftime("%Y-%m-%d"),
                            "source": "eu_ted",
                        }
                    )

    except Exception as e:
        print(f"EU TED scraping error: {e}")

    return opportunities


if __name__ == "__main__":
    data = scrape_eu_ted()
    print(f"Found {len(data)} opportunities from EU TED")
