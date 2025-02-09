import sqlite3
import json
import os

# Path to GoodLinks SQLite database (adjust if necessary)
GOODLINKS_DB_PATH = os.path.expanduser("~/Library/Group Containers/group.com.ngocluu.goodlinks/Data/data.sqlite")

def fetch_goodlinks():
    """Extracts links from GoodLinks database."""
    if not os.path.exists(GOODLINKS_DB_PATH):
        print(json.dumps({"items": [{"title": "Error: GoodLinks database not found", "valid": False}]}))
        return
    
    conn = sqlite3.connect(GOODLINKS_DB_PATH)
    cursor = conn.cursor()

    query = """
    select title, URL
    from LINK
    where URL IS NOT NULL
    ORDER BY addedat DESC;
    """

    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    alfred_items = []
    
    for title, url in results:
        alfred_items.append({
            "uid": url,
            "title": title if title else "Untitled",
            "subtitle": url,
            "arg": url,
            "autocomplete": title,
        })

    # Output JSON for Alfred
    print(json.dumps({"items": alfred_items}, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    fetch_goodlinks()
