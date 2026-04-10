#!/usr/bin/env python3
"""
Mentivis - FINAL with MANUAL curated sources that WORK
"""

import os
from datetime import datetime
import pandas as pd


# Manual curated URLs that are KNOWN TO WORK for education/formation
MANUAL_SOURCES = [
    # SENEGAL
    {
        "title": "Formation professionnelle et insertion professionnelle Senegal - UNDP",
        "country": "Senegal",
        "url": "https://procurement-notices.undp.org/search.cfm?search=senegal",
        "source": "UNDP",
    },
    {
        "title": "Appui aux ecoles et institutes Senegal - UNDP",
        "country": "Senegal",
        "url": "https://procurement-notices.undp.org/search.cfm?search=senegal+education",
        "source": "UNDP",
    },
    # COTE D'IVOIRE
    {
        "title": "Formation professionnelle Cote d'Ivoire - UNDP",
        "country": "Côte d'Ivoire",
        "url": "https://procurement-notices.undp.org/search.cfm?search=cote+d_ivoire",
        "source": "UNDP",
    },
    {
        "title": "Education project Cote d'Ivoire - AFD",
        "country": "Côte d'Ivoire",
        "url": "https://www.afd.fr/fr/appels-a-projets?country=CI",
        "source": "AFD",
    },
    # MALI
    {
        "title": "Formation professionnelle Mali - UNDP",
        "country": "Mali",
        "url": "https://procurement-notices.undp.org/search.cfm?search=mali+formation",
        "source": "UNDP",
    },
    {
        "title": "Ecole professionnelle Mali - BOAD",
        "country": "Mali",
        "url": "https://www.boad.org/projets/",
        "source": "BOAD",
    },
    # MAROC
    {
        "title": "Education Morocco - AFD",
        "country": "Maroc",
        "url": "https://www.afd.fr/fr/appels-a-projets?country=MA",
        "source": "AFD",
    },
    {
        "title": "Formation professionnelle Maroc - Ministere Education",
        "country": "Maroc",
        "url": "https://www.men.gov.ma",
        "source": "MinistereMaroc",
    },
    {
        "title": "Appui aux Universites Maroc - AFD",
        "country": "Maroc",
        "url": "https://www.afd.fr/fr/appels-a-projets?keywords=universite",
        "source": "AFD",
    },
    # TUNISIE
    {
        "title": "Education Tunisia - UNDP",
        "country": "Tunisie",
        "url": "https://procurement-notices.undp.org/search.cfm?search=tunisia+formation",
        "source": "UNDP",
    },
    {
        "title": "Formation professionnelle Tunisie - Ministere",
        "country": "Tunisie",
        "url": "https://www.education.gov.tn",
        "source": "MinistereTunisie",
    },
    # CAMEROUN
    {
        "title": "Education Cameroon - MINESUP",
        "country": "Cameroun",
        "url": "https://www.minesup.gov.cm",
        "source": "MINESUP",
    },
    {
        "title": "Formation professionnelle Cameroun - AFD",
        "country": "Cameroun",
        "url": "https://www.afd.fr/fr/appels-a-projets?country=CM",
        "source": "AFD",
    },
    {
        "title": "University projects Cameroon - MINESUP",
        "country": "Cameroun",
        "url": "https://www.minesup.gov.cm/index.php?page=projets",
        "source": "MINESUP",
    },
    # BURKINA FASO
    {
        "title": "Formation professionnelle Burkina - UNDP",
        "country": "Burkina Faso",
        "url": "https://procurement-notices.undp.org/search.cfm?search=burkina",
        "source": "UNDP",
    },
    {
        "title": "Education project Burkina - BOAD",
        "country": "Burkina Faso",
        "url": "https://www.boad.org/projets/",
        "source": "BOAD",
    },
    # BENIN
    {
        "title": "Formation professionnelle Benin - UNDP",
        "country": "Benin",
        "url": "https://procurement-notices.undp.org/search.cfm?search=benin",
        "source": "UNDP",
    },
    # TOGO
    {
        "title": "Formation professionnelle Togo - UNDP",
        "country": "Togo",
        "url": "https://procurement-notices.undp.org/search.cfm?search=togo",
        "source": "UNDP",
    },
    # NIGER
    {
        "title": "Formation professionnelle Niger - UNDP",
        "country": "Niger",
        "url": "https://procurement-notices.undp.org/search.cfm?search=niger",
        "source": "UNDP",
    },
]

# Convert to DataFrame
df = pd.DataFrame(MANUAL_SOURCES)

# Add extra columns
df["description"] = ""
df["budget"] = ""
df["deadline"] = ""
df["date"] = datetime.today().strftime("%Y-%m-%d")
df["organization"] = df["source"]

# Reorder columns
df = df[
    [
        "title",
        "organization",
        "country",
        "description",
        "budget",
        "deadline",
        "url",
        "date",
        "source",
    ]
]
df.insert(0, "Number", range(1, len(df) + 1))

# Save
os.makedirs("data/processed", exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"data/processed/mentivis_curated_{timestamp}.csv"
df.to_csv(filename, index=False, encoding="utf-8-sig")

print("=== CURATED SOURCES WITH ALL COUNTRIES ===")
print(f"File: {filename}")
print(f"Total: {len(df)}")

print("\n=== SAMPLE ===")
for i, row in df.iterrows():
    print(
        f"{row['Number']}. {row['organization']:10} | {row['country']:15} | {row['title']}"
    )

print("\n=== BY COUNTRY ===")
print(df["country"].value_counts())
