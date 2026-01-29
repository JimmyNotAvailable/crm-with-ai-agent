"""
CRM-AI-Agent Complete API Test Suite
Tests all main functionality after database configuration fix
"""
import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import requests
import json
import time

BASE = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("1. HEALTH ENDPOINT")
    print("=" * 60)
    try:
        r = requests.get(f"{BASE}/health", timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Response: {json.dumps(r.json(), indent=2)}")
        return r.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login():
    """Test authentication"""
    print()
    print("=" * 60)
    print("2. AUTH LOGIN (test@example.com)")
    print("=" * 60)
    try:
        r = requests.post(f"{BASE}/auth/login", data={
            "username": "test@example.com",
            "password": "password123"
        }, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            token = data.get("access_token", "")
            print(f"Token: {token[:50]}...")
            print(f"User: {data.get('user', {}).get('email')}")
            return token
        else:
            print(f"Error: {r.text[:200]}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_rag_query(token):
    """Test RAG query endpoint"""
    print()
    print("=" * 60)
    print("3. RAG QUERY - Laptop tầm 20 triệu")
    print("=" * 60)
    if not token:
        print("SKIP - No token")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.post(f"{BASE}/rag/query",
            headers=headers,
            data={"query": "Laptop gaming tầm 20 triệu", "top_k": 5},
            timeout=60
        )
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            result = r.json()
            print(f"Success: {result.get('success')}")
            print(f"Tool: {result.get('tool_used')}")
            print(f"Answer preview: {result.get('answer', '')[:200]}...")
            return True
        else:
            print(f"Error: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_rag_policy(token):
    """Test RAG query for policy"""
    print()
    print("=" * 60)
    print("4. RAG QUERY - Chính sách bảo hành")
    print("=" * 60)
    if not token:
        print("SKIP - No token")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.post(f"{BASE}/rag/query",
            headers=headers,
            data={"query": "Chính sách bảo hành như thế nào?", "top_k": 5},
            timeout=60
        )
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            result = r.json()
            print(f"Success: {result.get('success')}")
            print(f"Tool: {result.get('tool_used')}")
            print(f"Answer preview: {result.get('answer', '')[:200]}...")
            return True
        else:
            print(f"Error: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    print("CRM-AI-Agent Complete API Test Suite")
    print("=" * 60)
    print("Make sure the server is running on http://127.0.0.1:8000")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Health", test_health()))
    token = test_login()
    results.append(("Login", token is not None))
    results.append(("RAG Query (Laptop)", test_rag_query(token)))
    results.append(("RAG Query (Policy)", test_rag_policy(token)))
    
    # Summary
    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {name}: {status}")
    
    total_passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
