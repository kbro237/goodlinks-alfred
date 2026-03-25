import json
import urllib.request
import urllib.error
import sys

# GoodLinks local API endpoint
BASE_URL = "http://localhost:9428/api/v1/lists/all"

def fetch_all_links():
    """Extracts ALL links from GoodLinks via local REST API by following pagination."""
    all_links = []
    offset = 0
    limit = 1000 # Fetch in large chunks
    
    try:
        while True:
            url = f"{BASE_URL}?limit={limit}&offset={offset}"
            with urllib.request.urlopen(url) as response:
                if response.status != 200:
                    raise Exception(f"API returned status code {response.status}")
                
                data = json.loads(response.read().decode('utf-8'))
                links = data.get("data", [])
                all_links.extend(links)
                
                if not data.get("hasMore"):
                    break
                
                offset += limit
            
        is_tag_search = "--tag-search" in sys.argv
        
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
