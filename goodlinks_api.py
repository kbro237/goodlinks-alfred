import json
import urllib.request
import urllib.error
import sys

# GoodLinks local API endpoint
API_URL = "http://localhost:9428/api/v1/lists/all"

def fetch_goodlinks():
    """Extracts links from GoodLinks via local REST API."""
    try:
        with urllib.request.urlopen(API_URL) as response:
            if response.status != 200:
                raise Exception(f"API returned status code {response.status}")
            
            data = json.loads(response.read().decode('utf-8'))
            links = data.get("data", [])
            
            alfred_items = []
            for link in links:
                url = link.get("url")
                title = link.get("title") or "Untitled"
                summary = link.get("summary")
                
                alfred_items.append({
                    "uid": link.get("id"),
                    "title": title,
                    "subtitle": summary if summary else url,
                    "arg": url,
                    "autocomplete": title,
                    "quicklookurl": url
                })
            
            # Output JSON for Alfred
            print(json.dumps({"items": alfred_items}, indent=2, ensure_ascii=False))
            
    except urllib.error.URLError as e:
        # Check if it's a connection error (API probably not enabled or app not running)
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
    fetch_goodlinks()
