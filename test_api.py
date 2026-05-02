#!/usr/bin/env python3
"""Test script for goodlinks_api.py - verifies API endpoints and measures response times."""

import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse

BASE_URL = "http://localhost:9428/api/v1"
TOKEN = os.environ.get("GOODLINKS_API_TOKEN", "")

passed = 0
failed = 0
times = []

def headers():
    return {"Authorization": f"Bearer {TOKEN}"}

def test(name, url, expected_status=200):
    global passed, failed
    start = time.time()
    try:
        req = urllib.request.Request(url, headers=headers())
        resp = urllib.request.urlopen(req)
        elapsed = time.time() - start
        times.append(elapsed)
        data = json.loads(resp.read().decode('utf-8'))
        count = len(data.get("data", []))
        if resp.status == expected_status:
            passed += 1
            print(f"  PASS  {name} - {count} results in {elapsed:.3f}s")
        else:
            failed += 1
            print(f"  FAIL  {name} - expected {expected_status}, got {resp.status}")
    except Exception as e:
        failed += 1
        print(f"  FAIL  {name} - {e}")

def test_empty_query():
    """Test empty query returns unread links."""
    global passed, failed
    start = time.time()
    try:
        req = urllib.request.Request(f"{BASE_URL}/lists/unread?limit=10", headers=headers())
        resp = urllib.request.urlopen(req)
        elapsed = time.time() - start
        times.append(elapsed)
        data = json.loads(resp.read().decode('utf-8'))
        count = len(data.get("data", []))
        if count <= 10:
            passed += 1
            print(f"  PASS  empty query (unread) - {count} results in {elapsed:.3f}s")
        else:
            failed += 1
            print(f"  FAIL  empty query - got {count} results, expected <= 10")
    except Exception as e:
        failed += 1
        print(f"  FAIL  empty query - {e}")

def test_search_endpoint():
    """Test /links?search= endpoint."""
    test("search 'python'", f"{BASE_URL}/links?search=python&limit=10")
    test("search 'test'", f"{BASE_URL}/links?search=test&limit=10")
    test("search single char 'a'", f"{BASE_URL}/links?search=a&limit=10")

def test_tag_endpoint():
    """Test /links?tag= endpoint."""
    # Get a real tag first
    try:
        req = urllib.request.Request(f"{BASE_URL}/tags", headers=headers())
        resp = urllib.request.urlopen(req)
        tags = json.loads(resp.read().decode('utf-8'))
        if tags:
            tag = tags[0]
            test(f"tag '{tag}'", f"{BASE_URL}/links?tag={urllib.parse.quote(tag)}&limit=10")
        else:
            print("  SKIP  no tags available")
    except Exception as e:
        print(f"  FAIL  tag endpoint - {e}")

def test_unread_endpoint():
    """Test /lists/unread endpoint."""
    test("unread list", f"{BASE_URL}/lists/unread?limit=10")

def test_auth():
    """Test auth error handling."""
    global passed, failed
    try:
        req = urllib.request.Request(f"{BASE_URL}/lists/unread?limit=1")
        resp = urllib.request.urlopen(req)
        failed += 1
        print(f"  FAIL  auth - expected 401, got {resp.status}")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            passed += 1
            print(f"  PASS  auth - correctly returns 401 without token")
        else:
            failed += 1
            print(f"  FAIL  auth - expected 401, got {e.code}")

if not TOKEN:
    print("ERROR: GOODLINKS_API_TOKEN not set")
    sys.exit(1)

print(f"\nTesting GoodLinks API (limit=10 per request)\n")

test_auth()
print()
test_empty_query()
print()
test_search_endpoint()
print()
test_tag_endpoint()
print()
test_unread_endpoint()

print(f"\n{'='*40}")
print(f"Results: {passed} passed, {failed} failed")
if times:
    avg = sum(times) / len(times)
    print(f"Avg response time: {avg:.3f}s")
    print(f"Min response time: {min(times):.3f}s")
    print(f"Max response time: {max(times):.3f}s")
