import json
import os
import urllib.request
import urllib.error
import urllib.parse
import sys
import time

BASE_URL = "http://localhost:9428/api/v1"
CACHE_DIR = os.path.expanduser("~/Library/Caches/com.runningwithcrayons.Alfred/Workflow Data/org.netfull.goodlinks-alfred")
CACHE_FILE = os.path.join(CACHE_DIR, "links_cache.json")
CACHE_TTL = 300  # 5 minutes

def get_api_token():
    return os.environ.get("GOODLINKS_API_TOKEN", "")

def fetch_all_links_from_api():
    """Fetch all links from GoodLinks API."""
    api_token = get_api_token()
    headers = {"Authorization": f"Bearer {api_token}"}

    all_links = []
    offset = 0
    limit = 1000

    while True:
        url = f"{BASE_URL}/lists/all?limit={limit}&offset={offset}"
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode('utf-8'))
            links = data.get("data", [])
            all_links.extend(links)

            if not data.get("hasMore"):
                break

            offset += limit
            if offset > 100000:
                raise Exception("Too many links fetched (possible infinite loop)")

    return all_links

def save_cache(links):
    """Save links to cache file."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_data = {
        "timestamp": time.time(),
        "links": links
    }
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False)

def load_cache():
    """Load links from cache file."""
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("links", []), data.get("timestamp", 0)
    except Exception:
        return [], 0

def build_alfred_items(links, is_tag_search):
    """Build Alfred JSON items from links."""
    alfred_items = []
    for link in links:
        url = link.get("url")
        title = link.get("title") or "Untitled"
        summary = link.get("summary") or ""
        tags = link.get("tags") or []

        if is_tag_search and not tags:
            continue

        if is_tag_search:
            match = " ".join(tags)
        else:
            match = f"{title} {summary} {' '.join(tags)}"

        item = {
            "uid": link.get("id"),
            "title": title,
            "subtitle": summary if summary else url,
            "arg": url,
            "autocomplete": title,
            "quicklookurl": url,
            "match": match
        }

        alfred_items.append(item)

    return alfred_items

def show_error(title, subtitle):
    """Show error message."""
    print(json.dumps({
        "items": [{
            "title": f"Error: {title}",
            "subtitle": subtitle,
            "valid": False
        }]
    }))

def main():
    api_token = get_api_token()
    if not api_token:
        show_error("API token not configured", "Set GOODLINKS_API_TOKEN in Workflow Settings")
        return

    is_refresh = "--refresh" in sys.argv
    is_tag_search = "--tag-search" in sys.argv

    if is_refresh:
        try:
            links = fetch_all_links_from_api()
            save_cache(links)
            print(json.dumps({
                "items": [{
                    "title": f"Cache refreshed - {len(links)} links loaded",
                    "subtitle": "Use 'link' or 'linkt' to search",
                    "valid": False
                }]
            }))
        except urllib.error.HTTPError as e:
            if e.code == 401:
                show_error("Invalid API token", "Check token in Workflow Settings")
            elif e.code == 404:
                show_error("API not found", "Check GoodLinks version (3.2+ required)")
            else:
                show_error(f"HTTP {e.code}", str(e))
        except urllib.error.URLError as e:
            show_error("API not reachable", "Ensure GoodLinks is running and API is enabled")
        except Exception as e:
            show_error("Failed to fetch links", str(e))
        return

    links, timestamp = load_cache()
    cache_age = time.time() - timestamp

    if not links:
        try:
            links = fetch_all_links_from_api()
            save_cache(links)
        except Exception as e:
            show_error("Failed to fetch links", str(e))
            return

    items = build_alfred_items(links, is_tag_search)

    if cache_age > CACHE_TTL:
        items.insert(0, {
            "title": "⚠ Cache expired - run 'linkrefresh' to update",
            "subtitle": f"Cache is {int(cache_age/60)}min old (refreshes every {CACHE_TTL//60}min)",
            "valid": False
        })

    print(json.dumps({"items": items}, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
