"""Save and load past queries (simple CSV file)."""
import csv
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path("queries_history.csv")
FIELDS = ["timestamp", "query", "articles", "summary"]


def save_query(query, summary, n_articles):
    """Append one search to the history file."""
    new_file = not HISTORY_FILE.exists()
    with HISTORY_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query": query.strip(),
            "articles": n_articles,
            "summary": summary,
        })


def load_history():
    """Return all saved searches (oldest first) as a list of dicts."""
    if not HISTORY_FILE.exists():
        return []
    with HISTORY_FILE.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def clear_history():
    """Delete the history file."""
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
