# AGENTS.md

## Repository Type
Alfred workflow (Python-based). Single-purpose: search GoodLinks.app via local REST API.

## Key Files
- `goodlinks_api.py` - Main script, fetches links and outputs Alfred JSON
- `info.plist` - Workflow metadata, keywords, triggers, configuration

## Prerequisites
- GoodLinks 3.2+ must be running on the Mac
- GoodLinks **Settings > API** - enable Local API and copy the API token
- API token must be set as workflow environment variable `GOODLINKS_API_TOKEN`
- API defaults to port `9428`

## Token Configuration
Set `GOODLINKS_API_TOKEN` environment variable in the workflow's script filter inspector (click script filter → Environment Variables section).

## Keywords
- `link` - Search by title, summary, and tags (server-side via API)
- `linkt` - Search strictly by tags only (uses `--tag-search` flag)

## API Authentication
Requires `Authorization: Bearer <token>` header on all requests. Token read from `GOODLINKS_API_TOKEN` environment variable.

## Script Details
- Uses server-side search via API (`/links?search=` or `/links?tag=`) - limit 20 results
- Empty query shows 20 unread links
- `alfredfiltersresults` is disabled - Alfred calls script on each keystroke
- Script uses `"$1"` in plist to pass query arg (not `{query}` which doesn't work in this Alfred version)

## Alfred JSON Output
- `uid` - Link ID
- `title` - Link title
- `subtitle` - Summary or URL
- `arg` - URL (action on selection)
- `autocomplete` - Title for refinements
- `quicklookurl` - Preview URL
- `match` - Searchable text

## Error Handling
- 401: Invalid token - check token in environment variable
- 404: Check GoodLinks version (3.2+ required)
- Connection error: API not reachable - ensure GoodLinks is running