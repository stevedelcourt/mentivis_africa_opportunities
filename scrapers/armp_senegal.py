import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
from config import SCRAPER_SETTINGS
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


URL = "https://www.marchespublics.sn"


def scrape_armp_senegal():
    opportunities = []

    user_agent = random.choice(SCRAPER_SETTINGS["user_agents"])
    headers = {"User-Agent": user_agent}
    res = None

    for attempt in range(3):
        try:
            res = requests.get(URL, headers=headers, timeout=15, verify=False)
            if res.status_code == 200:
                break
        except:
            continue

    if not res or res.status_code != 200:
        return opportunities

    soup = BeautifulSoup(res.text, "lxml")
    all_links = soup.find_all("a", href=True)
    links = [
        a
        for a in all_links
        if a.get_text(strip=True) and len(a.get_text(strip=True)) > 10
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
                "organization": "ARMP Senegal",
                "organization_type": "gouvernement",
                "country": "Sénégal",
                "budget": "",
                "deadline": "",
                "url": href,
                "date": datetime.today().strftime("%Y-%m-%d"),
                "source": "armp_senegal",
            }
        )

    return opportunities


if __name__ == "__main__":
    data = scrape_armp_senegal()
    print(f"Found {len(data)} opportunities from ARMP Senegal")
