import json
import os
import urllib.request
import urllib.error
import urllib.parse
import sys

BASE_URL = "http://localhost:9428/api/v1"

def fetch_all_links():
    """Fetch links from GoodLinks via local REST API."""
    api_token = os.environ.get("GOODLINKS_API_TOKEN", "")
    
    if not api_token:
        print(json.dumps({
            "items": [{
                "title": "Error: API token not configured",
                "subtitle": "Set GOODLINKS_API_TOKEN in Workflow Settings",
                "valid": False
            }]
        }))
        return

    is_tag_search = "--tag-search" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--tag-search"]
    query = args[0] if args else ""

    headers = {"Authorization": f"Bearer {api_token}"}

    if query:
        if is_tag_search:
            url = f"{BASE_URL}/links?tag={urllib.parse.quote(query)}&limit=20"
        else:
            url = f"{BASE_URL}/links?search={urllib.parse.quote(query)}&limit=20"
    else:
        url = f"{BASE_URL}/lists/unread?limit=20"

    try:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            if response.status != 200:
                raise Exception(f"API returned status code {response.status}")
            
            data = json.loads(response.read().decode('utf-8'))
            all_links = data.get("data", [])

        alfred_items = []
        for link in all_links:
            url = link.get("url")
            title = link.get("title") or "Untitled"
            summary = link.get("summary")
            tags = link.get("tags") or []
            
            # Skip links without tags if strictly searching by tags
            if is_tag_search and not tags:
                continue
            
            item = {
                "uid": link.get("id"),
                "title": title,
                "subtitle": summary if summary else url,
                "arg": url,
                "autocomplete": title,
                "quicklookurl": url
            }
            
            # If tag search, only match against tags. Otherwise include title, summary, and tags.
            if is_tag_search:
                item["match"] = " ".join(tags)
            else:
                item["match"] = f"{title} {summary or ''} {' '.join(tags)}"
                
            alfred_items.append(item)
        
        # Output JSON for Alfred
        print(json.dumps({"items": alfred_items}, indent=2, ensure_ascii=False))
            
    except urllib.error.HTTPError as e:
        if e.code == 401:
            error_msg = "Invalid API token. Check token in Workflow Settings."
        elif e.code == 404:
            error_msg = "API endpoint not found. Check GoodLinks version (3.2+ required)."
        else:
            error_msg = f"HTTP error {e.code}"
        print(json.dumps({
            "items": [{
                "title": "Error: " + error_msg,
                "subtitle": str(e),
                "valid": False
            }]
        }))
    except urllib.error.URLError as e:
        error_msg = "GoodLinks API not reachable. Ensure GoodLinks is running and API is enabled in Settings."
        print(json.dumps({
            "items": [{
                "title": "Error: " + error_msg,
                "subtitle": str(e),
                "valid": False
            }]
        }))
    except Exception as e:
        print(json.dumps({
            "items": [{
                "title": "Error: Failed to fetch links",
                "subtitle": str(e),
                "valid": False
            }]
        }))

if __name__ == "__main__":
    fetch_all_links()
