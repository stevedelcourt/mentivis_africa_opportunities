#!/usr/bin/env python3
"""
Mentivis - Framework de détection d'opportunités projets Afrique francophone
Interface CLI
"""

import os
import sys
import json
from datetime import datetime

from config import SOURCES
from processing.scorer import score_opportunity
from processing.cleaner import (
    deduplicate,
    filter_by_score,
    filter_by_country,
    sort_by_score,
)
from processing.enricher import detect_country, mentivis_angle
from processing.classifier import classify_project
from output.exporter import export_csv, export_history
from output.history import init_db, save_run, compare_with_previous, get_stats

SCRAPERS = {
    "world_bank": "scrapers.world_bank",
    "bad": "scrapers.bad",
    "afd": "scrapers.afd",
    "eu_ted": "scrapers.eu_ted",
    "armp_senegal": "scrapers.armp_senegal",
    "portal_maroc": "scrapers.portal_maroc",
    "tendersinfo": "scrapers.tendersinfo",
    "tendersontime": "scrapers.tendersontime",
    "globaltenders": "scrapers.globaltenders",
    "tuneps": "scrapers.tuneps",
    "sigmap_civ": "scrapers.sigmap_civ",
    "armp_cameroon": "scrapers.armp_cameroon",
    "ministere_maroc": "scrapers.ministere_maroc",
    "ministere_tunisie": "scrapers.ministere_tunisie",
    "menetfp_civ": "scrapers.menetfp_civ",
    "minesup_cameroon": "scrapers.minesup_cameroon",
    "boad": "scrapers.boad",
    "bdeac": "scrapers.bdeac",
    "reliefweb": "scrapers.reliefweb",
    "devex": "scrapers.devex",
    "unicef": "scrapers.unicef",
    "undp": "scrapers.undp",
    "unesco": "scrapers.unesco",
    "isdb": "scrapers.isdb",
    "badea": "scrapers.badea",
}


def import_scraper(name):
    module = __import__(SCRAPERS[name], fromlist=[""])
    return getattr(module, f"scrape_{name}", None)


def run_scraper(source_name):
    scraper_func = import_scraper(source_name)
    if scraper_func:
        return scraper_func()
    return []


def process_opportunities(opportunities):
    processed = []

    for op in opportunities:
        op = detect_country(op)
        op = classify_project(op)
        op = score_opportunity(op)
        op = mentivis_angle(op)
        processed.append(op)

    processed = deduplicate(processed)
    processed = sort_by_score(processed)

    return processed


def print_opportunity(op, idx):
    print(f"\n--- Opportunity #{idx} ---")
    print(f"  Titre: {op.get('title', 'N/A')[:80]}")
    print(f"  Organisation: {op.get('organization', 'N/A')}")
    print(f"  Pays: {op.get('country', 'N/A')}")
    print(f"  Score: {op.get('score', 0)} ({op.get('tag', 'N/A')})")
    print(f"  Type: {op.get('project_type', 'N/A')}")
    print(f"  Angle: {op.get('mentivis_angle', 'N/A')[:60]}")
    if op.get("url"):
        print(f"  URL: {op.get('url', 'N/A')[:60]}")


def show_stats():
    stats = get_stats()
    if stats:
        print("\n=== STATISTIQUES ===")
        print(f"  Runs effectués: {stats.get('total_runs', 0)}")
        print(f"  Opportunités totales: {stats.get('total_opportunities', 0)}")
        print(f"  Total scrapé: {stats.get('total_scraped', 0)}")
        print(f"  Haute priorité: {stats.get('total_high', 0)}")
    else:
        print("Aucune statistique disponible.")


def run_all_sources():
    print("\n=== LANCEMENT SCRAPING (TOUTES SOURCES) ===\n")

    all_data = []
    sources_count = len(SCRAPERS)

    for idx, source_name in enumerate(SCRAPERS.keys(), 1):
        source_info = SOURCES.get(source_name, {})
        source_label = source_info.get("name", source_name)
        priority = source_info.get("priority", 99)

        print(
            f"[{idx}/{sources_count}] {source_label} (priority {priority})...",
            end=" ",
            flush=True,
        )

        try:
            data = run_scraper(source_name)
            all_data.extend(data)
            print(f"✓ {len(data)} opportunités")
        except Exception as e:
            print(f"✗ Erreur: {e}")

    print(f"\nTotal brut: {len(all_data)} opportunités")

    if not all_data:
        print("Aucune donnée trouvée.")
        return []

    processed = process_opportunities(all_data)

    print(f"Après traitement: {len(processed)} opportunitésuniques")

    high = len([o for o in processed if o.get("tag") == "high"])
    medium = len([o for o in processed if o.get("tag") == "medium"])
    print(f"  - High: {high}")
    print(f"  - Medium: {medium}")

    init_db()
    save_run("all", processed)

    return processed


def run_single_source(source_name):
    if source_name not in SCRAPERS:
        print(f"Source inconnue: {source_name}")
        print(f"Sources disponibles: {', '.join(SCRAPERS.keys())}")
        return []

    source_info = SOURCES.get(source_name, {})
    source_label = source_info.get("name", source_name)

    print(f"\n=== SCRAPING: {source_label} ===\n")

    data = run_scraper(source_name)
    print(f"Trouvé: {len(data)} opportunités")

    if not data:
        return []

    processed = process_opportunities(data)

    high = len([o for o in processed if o.get("tag") == "high"])
    print(f"High priority: {high}")

    init_db()
    save_run(source_name, processed)

    return processed


def list_sources():
    print("\n=== SOURCES DISPONIBLES ===\n")

    sources_by_priority = {}
    for name, info in SOURCES.items():
        priority = info.get("priority", 99)
        if priority not in sources_by_priority:
            sources_by_priority[priority] = []
        sources_by_priority[priority].append((name, info.get("name", name)))

    for priority in sorted(sources_by_priority.keys()):
        print(f"\n--- Priority {priority} ---")
        for name, label in sources_by_priority[priority]:
            print(f"  {name}: {label}")


def show_menu():
    print("""
╔══════════════════════════════════════════════════════════════╗
║     MENTIVIS - Détection Opportunités Afrique              ║
║     Framework de scraping projets éducatifs                 ║
╚══════════════════════════════════════════════════════════════╝

1. Lancer scraping (TOUTES les sources)
2. Lancer scraping (source spécifique)
3. Voir les résultats (filtrés)
4. Exporter CSV
5. Statistiques
6. Liste des sources
7. Config (afficher/modifier)
8. Quitter
""")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir:
        os.chdir(script_dir)

    results_cache = []

    while True:
        show_menu()
        choice = input("\n> Veuillez choisir une option: ").strip()

        if choice == "1":
            results_cache = run_all_sources()

        elif choice == "2":
            list_sources()
            source = input("\nNom de la source: ").strip().lower()
            if source in SCRAPERS:
                results_cache = run_single_source(source)
            else:
                print(f"Source '{source}' non trouvée.")

        elif choice == "3":
            if not results_cache:
                print("Aucun résultat en mémoire. Lancez d'abord un scraping.")
                continue

            print("\n=== FILTRES ===")
            print("a) Par score minimum")
            print("b) Par pays")
            print("c) Par tag (high/medium/low)")
            print("d) Afficher tous")

            filter_choice = input("\n> Filtre: ").strip().lower()

            if filter_choice == "a":
                try:
                    min_score = int(input("Score minimum: "))
                    filtered = filter_by_score(results_cache, min_score)
                except:
                    filtered = results_cache
            elif filter_choice == "b":
                country = input("Pays: ").strip()
                filtered = filter_by_country(results_cache, [country])
            elif filter_choice == "c":
                tag = input("Tag (high/medium/low): ").strip().lower()
                filtered = [o for o in results_cache if o.get("tag") == tag]
            else:
                filtered = results_cache

            print(f"\n{len(filtered)} opportunités après filtre")

            max_show = 20
            for idx, op in enumerate(filtered[:max_show], 1):
                print_opportunity(op, idx)

            if len(filtered) > max_show:
                print(f"\n... et {len(filtered) - max_show} autres")

        elif choice == "4":
            if not results_cache:
                print("Aucun résultat à exporter.")
                continue

            filename = export_csv(results_cache)
            if filename:
                print(f"✓ Exporté vers: {filename}")
            else:
                print("✗ Erreur lors de l'export.")

        elif choice == "5":
            show_stats()

        elif choice == "6":
            list_sources()

        elif choice == "7":
            from config import KEYWORDS, SCORING, AFRICA_COUNTRIES

            print("\n=== MOTS-CLÉS ===")
            print(", ".join(KEYWORDS[:15]))
            print("\n=== SCORING ===")
            for k, v in SCORING.items():
                print(f"  {k}: {v}")
            print("\n=== PAYS AFRICAINS ===")
            print(", ".join(list(AFRICA_COUNTRIES.values())[:10]))

        elif choice == "8":
            print("\nAu revoir!")
            break

        else:
            print("Option invalide.")

        input("\n[Entrée pour continuer]")


if __name__ == "__main__":
    main()
