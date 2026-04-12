#!/usr/bin/env python3
"""
Authenticated Scraper for Government Portals
Attempts login-based scraping for restricted tender portals
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}


# ========== AUTHENTICATED PORTALS ==========
PORTALS = [
    {
        "name": "Marchés Publics Senegal",
        "base_url": "https://www.marchespublics.sn",
        "login_url": "https://www.marchespublics.sn/login",
        "username_field": "username",
        "password_field": "password",
        "submit_button": "submit-login",
        "tender_paths": ["/appels-offres", "/avis", "/projets"],
        "requires_auth": True,
    },
    {
        "name": "SIGMAP Côte d'Ivoire",
        "base_url": "https://www.sigmap.org",
        "login_url": "https://www.sigmap.org/user/login",
        "username_field": "edit-name",
        "password_field": "edit-pass",
        "submit_button": "edit-submit",
        "tender_paths": ["/procurement", "/appels-d-offres"],
        "requires_auth": True,
    },
    {
        "name": "DGMP Niger",
        "base_url": "https://www.dgmp.ne",
        "login_url": "https://www.dgmp.ne/login",
        "username_field": "username",
        "password_field": "password",
        "submit_button": "submit",
        "tender_paths": ["/marches", "/avis"],
        "requires_auth": True,
    },
    {
        "name": "ARMPS Burkina",
        "base_url": "https://www.armps.bf",
        "login_url": "https://www.armps.bf/connexion",
        "username_field": "username",
        "password_field": "password",
        "submit_button": "submit",
        "tender_paths": ["/appels-d-offres", "/marches"],
        "requires_auth": True,
    },
]


class AuthenticatedScraper:
    """Handle authenticated scraping for government portals"""

    def __init__(self, credentials=None):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.driver = None
        self.credentials = credentials or {}

    def init_selenium(self):
        """Initialize Selenium for JS-heavy sites"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(options=options)

    def close(self):
        """Cleanup resources"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

    def try_requests_login(self, portal):
        """Try login via requests (for simple auth)"""
        try:
            # First get login page to get tokens
            r = self.session.get(portal["login_url"], timeout=15)
            soup = BeautifulSoup(r.text, "lxml")

            # Find hidden form fields
            form_data = {}
            for input_tag in soup.find_all("input", type="hidden"):
                name = input_tag.get("name")
                value = input_tag.get("value")
                if name:
                    form_data[name] = value or ""

            # Add credentials
            form_data[portal["username_field"]] = self.credentials.get("username", "")
            form_data[portal["password_field"]] = self.credentials.get("password", "")

            # Find form action
            form = soup.find("form")
            if not form:
                return False

            action = form.get("action", "")
            if not action.startswith("http"):
                action = portal["base_url"] + action

            # Submit login
            r = self.session.post(action, data=form_data, timeout=15)

            # Check if logged in
            if "login" not in r.url.lower() or "error" in r.text.lower():
                return True

        except Exception as e:
            print(f"Requests login failed: {e}")

        return False

    def try_selenium_login(self, portal):
        """Try login via Selenium (for JS auth)"""
        if not self.driver:
            self.init_selenium()

        try:
            self.driver.get(portal["login_url"])
            time.sleep(3)

            # Wait for login form
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, portal["username_field"]))
                )
            except:
                return False

            # Fill username
            username_input = self.driver.find_element(By.NAME, portal["username_field"])
            username_input.clear()
            username_input.send_keys(self.credentials.get("username", ""))

            # Fill password
            password_input = self.driver.find_element(By.NAME, portal["password_field"])
            password_input.clear()
            password_input.send_keys(self.credentials.get("password", ""))

            # Submit
            submit_btn = self.driver.find_element(By.ID, portal["submit_button"])
            submit_btn.click()

            time.sleep(3)

            # Check if logged in
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                return True

        except Exception as e:
            print(f"Selenium login failed: {e}")

        return False

    def scrape_authenticated(self, portal):
        """Scrape after authentication"""
        tenders = []

        try:
            # Use Selenium for JS content
            if not self.driver:
                self.init_selenium()

            # Try each tender path
            for path in portal["tender_paths"]:
                url = portal["base_url"] + path
                self.driver.get(url)
                time.sleep(3)

                soup = BeautifulSoup(self.driver.page_source, "lxml")
                links = soup.find_all("a", href=True)

                for link in links:
                    href = link.get("href", "")
                    title = link.get_text(strip=True)

                    # Look for tender-like links
                    if len(title) > 15 and any(
                        x in href.lower()
                        for x in ["tender", "appel", "march", "offre", "avis", "projet"]
                    ):
                        if href.startswith("/"):
                            href = portal["base_url"] + href

                        tenders.append(
                            {
                                "title": title[:150],
                                "organization": portal["name"],
                                "url": href,
                                "source": portal["name"] + " (authenticated)",
                            }
                        )

        except Exception as e:
            print(f"Scraping error: {e}")

        return tenders


def try_public_portals():
    """Try portals that might work without auth"""
    print("=== Trying Public Portals (No Auth) ===\n")

    results = []

    # Test each portal without auth
    test_urls = [
        ("Marches Publics Senegal", "https://www.marchespublics.sn"),
        ("SIGMAP Ivory Coast", "https://www.sigmap.org"),
        ("DGMP Niger", "https://www.dgmp.ne"),
        ("ARMPS Burkina", "https://www.armps.bf"),
        ("DGMP Togo", "https://www.dgmp.tg"),
        ("Marches Benin", "https://www.marchespublics.bj"),
    ]

    for name, url in test_urls:
        print(f"Testing {name}...")
        try:
            r = requests.get(url, timeout=10, headers=HEADERS)
            print(f"  Status: {r.status_code}")

            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "lxml")
                links = soup.find_all("a", href=True)

                tender_links = []
                for link in links:
                    href = link.get("href", "")
                    title = link.get_text(strip=True)

                    if len(title) > 15 and any(
                        x in href.lower()
                        for x in [
                            "tender",
                            "appel",
                            "march",
                            "offre",
                            "avis",
                            "projet",
                            "procurement",
                        ]
                    ):
                        full_url = url + href if href.startswith("/") else href
                        tender_links.append((title[:50], full_url))
                        results.append(
                            {
                                "title": title[:150],
                                "organization": name,
                                "url": full_url,
                                "source": name,
                            }
                        )

                if tender_links:
                    print(f"  Found {len(tender_links)} tender links")
                    for t, u in tender_links[:2]:
                        print(f"    - {t}: {u[:60]}")
                else:
                    print(f"  No tender links found")
            elif r.status_code == 403:
                print(f"  BLOCKED - Requires authentication")
            elif r.status_code == 404:
                print(f"  Not found")
            else:
                print(f"  Unknown status")

        except requests.exceptions.Timeout:
            print(f"  TIMEOUT")
        except requests.exceptions.ConnectionError:
            print(f"  CONNECTION ERROR")
        except Exception as e:
            print(f"  ERROR: {str(e)[:50]}")

        print()

    return results


def try_with_auth(credentials=None):
    """Try authenticated scraping"""
    if not credentials:
        print("No credentials provided - skipping authenticated scraping")
        return []

    print("=== Trying Authenticated Portals ===\n")

    scraper = AuthenticatedScraper(credentials)
    results = []

    for portal in PORTALS:
        print(f"Trying {portal['name']}...")

        # Try requests login first
        if scraper.try_requests_login(portal):
            print(f"  Requests login succeeded")
            tenders = scraper.scrape_authenticated(portal)
            results.extend(tenders)
        else:
            print(f"  Trying Selenium login...")
            if scraper.try_selenium_login(portal):
                print(f"  Selenium login succeeded")
                tenders = scraper.scrape_authenticated(portal)
                results.extend(tenders)
            else:
                print(f"  Login failed")

        print()

    scraper.close()
    return results


if __name__ == "__main__":
    import sys

    # Try public portals first
    public_results = try_public_portals()
    print(f"\n=== Public portals: {len(public_results)} results ===\n")

    # If credentials provided, try authenticated
    if len(sys.argv) > 2:
        credentials = {"username": sys.argv[1], "password": sys.argv[2]}
        auth_results = try_with_auth(credentials)
        print(f"\n=== Authenticated: {len(auth_results)} results ===\n")
        public_results.extend(auth_results)

    # Print all results
    print("=== ALL RESULTS ===")
    for r in public_results:
        print(f"{r['organization']}: {r['url']}")
