import sqlite3
import os
from datetime import datetime


DB_PATH = "data/mentivis_history.db"


def init_db():
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date TEXT,
            source TEXT,
            opportunities_count INTEGER,
            high_count INTEGER,
            medium_count INTEGER,
            low_count INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            title TEXT,
            organization TEXT,
            country TEXT,
            budget TEXT,
            deadline TEXT,
            score INTEGER,
            tag TEXT,
            url TEXT,
            date TEXT,
            FOREIGN KEY (run_id) REFERENCES runs(id)
        )
    """)

    conn.commit()
    conn.close()


def save_run(source, opportunities):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    run_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    high = len([o for o in opportunities if o.get("tag") == "high"])
    medium = len([o for o in opportunities if o.get("tag") == "medium"])
    low = len([o for o in opportunities if o.get("tag") == "low"])

    c.execute(
        """
        INSERT INTO runs (run_date, source, opportunities_count, high_count, medium_count, low_count)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (run_date, source, len(opportunities), high, medium, low),
    )

    run_id = c.lastrowid

    for op in opportunities:
        c.execute(
            """
            INSERT INTO opportunities 
            (run_id, title, organization, country, budget, deadline, score, tag, url, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                run_id,
                op.get("title", ""),
                op.get("organization", ""),
                op.get("country", ""),
                op.get("budget", ""),
                op.get("deadline", ""),
                op.get("score", 0),
                op.get("tag", ""),
                op.get("url", ""),
                op.get("date", ""),
            ),
        )

    conn.commit()
    conn.close()

    return run_id


def get_runs(limit=10):
    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()

    conn.close()

    return rows


def compare_with_previous(opportunities):
    if not os.path.exists(DB_PATH):
        return {"new": opportunities, "duplicates": []}

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT title FROM opportunities ORDER BY id DESC LIMIT 1000")
    existing = set([row[0] for row in c.fetchall()])

    conn.close()

    new = []
    duplicates = []

    for op in opportunities:
        if op.get("title") in existing:
            duplicates.append(op)
        else:
            new.append(op)

    return {"new": new, "duplicates": duplicates}


def get_stats():
    if not os.path.exists(DB_PATH):
        return {}

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM runs")
    total_runs = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM opportunities")
    total_opps = c.fetchone()[0]

    c.execute("SELECT SUM(opportunities_count) FROM runs")
    total_scraped = c.fetchone()[0] or 0

    c.execute("SELECT SUM(high_count) FROM runs")
    total_high = c.fetchone()[0] or 0

    conn.close()

    return {
        "total_runs": total_runs,
        "total_opportunities": total_opps,
        "total_scraped": total_scraped,
        "total_high": total_high,
    }
