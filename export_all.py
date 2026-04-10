#!/usr/bin/env python3
"""
Mentivis - Structured Export with Source URLs
Creates clean CSV with direct links to each source page
"""

import os
from datetime import datetime


# All sources with their URLs (for reference/click-through)
SOURCES_DIRECT = [
    {
        "name": "UNDP Procurement",
        "url": "https://procurement-notices.undp.org/",
        "description": "UNDP procurement notices - Africa filter available",
        "organization": "UNDP",
        "country": "Multiple Africa",
    },
    {
        "name": "World Bank Projects",
        "url": "https://projects.worldbank.org/en/projects-operations",
        "description": "World Bank projects in Africa",
        "organization": "World Bank",
        "country": "Multiple Africa",
    },
    {
        "name": "AfDB Procurement",
        "url": "https://www.afdb.org/en/projects-and-operations/procurement",
        "description": "African Development Bank procurement",
        "organization": "AfDB",
        "country": "Multiple Africa",
    },
    {
        "name": "AFD Projects",
        "url": "https://www.afd.fr/fr/appels-a-projets",
        "description": "AFD calls for projects",
        "organization": "AFD",
        "country": "Francophone Africa",
    },
    {
        "name": "EU TED",
        "url": "https://ted.europa.eu/en/search?fsr=true",
        "description": "EU Tenders Electronic Daily",
        "organization": "EU",
        "country": "Multiple",
    },
    {
        "name": "Marchés Publics Maroc",
        "url": "https://www.marchespublics.gov.ma",
        "description": "Morocco public procurement",
        "organization": "Morocco Government",
        "country": "Morocco",
    },
    {
        "name": "TendersOnTime Africa",
        "url": "https://www.tendersontime.com/africa-tenders",
        "description": "Africa tenders aggregator",
        "organization": "TendersOnTime",
        "country": "Multiple Africa",
    },
    {
        "name": "GlobalTenders",
        "url": "https://www.globaltenders.com",
        "description": "Global tenders",
        "organization": "GlobalTenders",
        "country": "Multiple",
    },
    {
        "name": "ARMP Cameroon",
        "url": "https://www.armp.cm",
        "description": "Cameroon public procurement",
        "organization": "ARMP Cameroon",
        "country": "Cameroon",
    },
    {
        "name": "Ministère Education Tunisie",
        "url": "https://www.education.gov.tn",
        "description": "Tunisia Ministry of Education",
        "organization": "Tunisia Government",
        "country": "Tunisia",
    },
    {
        "name": "MINESUP Cameroon",
        "url": "https://www.minesup.gov.cm",
        "description": "Cameroon Higher Education",
        "organization": "MINESUP Cameroon",
        "country": "Cameroon",
    },
    {
        "name": "BOAD",
        "url": "https://www.boad.org",
        "description": "West Africa Development Bank",
        "organization": "BOAD",
        "country": "West Africa",
    },
    {
        "name": "BADEA",
        "url": "https://www.badea.org",
        "description": "Arab Bank for Economic Development in Africa",
        "organization": "BADEA",
        "country": "Multiple Africa",
    },
    {
        "name": "Islamic Development Bank",
        "url": "https://www.isdb.org",
        "description": "Islamic Development Bank projects",
        "organization": "IsDB",
        "country": "Multiple Africa",
    },
    {
        "name": "ReliefWeb",
        "url": "https://reliefweb.int/jobs",
        "description": "Humanitarian jobs and tenders",
        "organization": "UN/OCHA",
        "country": "Multiple",
    },
]


def export_sources_csv():
    """Export direct source URLs for manual exploration"""
    import csv

    os.makedirs("data/processed", exist_ok=True)
    filename = f"data/processed/sources_url_{datetime.now().strftime('%Y%m%d')}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Source Name", "URL", "Description", "Organization", "Country"]
        )

        for source in SOURCES_DIRECT:
            writer.writerow(
                [
                    source["name"],
                    source["url"],
                    source["description"],
                    source["organization"],
                    source["country"],
                ]
            )

    return filename


def export_sample_data():
    """Export sample with existing scraped data"""
    from scrapers.undp import scrape_undp
    from scrapers.afd import scrape_afd
    from scrapers.bad import scrape_bad
    from scrapers.eu_ted import scrape_eu_ted
    from scrapers.portal_maroc import scrape_portal_maroc
    from scrapers.globaltenders import scrape_globaltenders
    from scrapers.tendersontime import scrape_tendersontime
    from scrapers.armp_cameroon import scrape_armp_cameroon
    from scrapers.ministere_tunisie import scrape_ministere_tunisie
    from scrapers.minesup_cameroon import scrape_minesup_cameroon
    from scrapers.boad import scrape_boad
    from scrapers.reliefweb import scrape_reliefweb
    from scrapers.isdb import scrape_isdb
    from scrapers.badea import scrape_badea

    scrapers = [
        ("UNDP", scrape_undp),
        ("AFD", scrape_afd),
        ("AfDB", scrape_bad),
        ("EU TED", scrape_eu_ted),
        ("Maroc Portal", scrape_portal_maroc),
        ("GlobalTenders", scrape_globaltenders),
        ("TendersOnTime", scrape_tendersontime),
        ("ARMP Cameroon", scrape_armp_cameroon),
        ("Ministère Tunisie", scrape_ministere_tunisie),
        ("MINESUP Cameroon", scrape_minesup_cameroon),
        ("BOAD", scrape_boad),
        ("ReliefWeb", scrape_reliefweb),
        ("IsDB", scrape_isdb),
        ("BADEA", scrape_badea),
    ]

    all_data = []

    print("Scraping sources...")
    for name, func in scrapers:
        try:
            print(f"  {name}...", end=" ", flush=True)
            data = func()
            print(f"{len(data)}")

            for op in data:
                op["source"] = name
            all_data.extend(data)
        except Exception as e:
            print(f"Error: {e}")

    if not all_data:
        print("No data scraped")
        return None

    # Deduplicate
    seen = set()
    unique = []
    for op in all_data:
        key = op.get("title", "")[:100]
        if key not in seen:
            seen.add(key)
            unique.append(op)

    all_data = unique

    # Export
    import pandas as pd

    os.makedirs("data/processed", exist_ok=True)
    filename = (
        f"data/processed/opportunities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    df = pd.DataFrame(all_data)

    cols = ["title", "organization", "country", "description", "url", "source", "date"]
    for col in cols:
        if col not in df.columns:
            df[col] = ""

    df = df[cols]
    df.to_csv(filename, index=False, encoding="utf-8-sig")

    return filename, len(all_data)


if __name__ == "__main__":
    print("=== Mentivis Export ===\n")

    # Export sources URL reference
    sources_file = export_sources_csv()
    print(f"Sources URL reference: {sources_file}\n")

    # Try scrape and export
    result = export_sample_data()
    if result:
        filename, count = result
        print(f"\nScraped data: {filename}")
        print(f"Total opportunities: {count}")
