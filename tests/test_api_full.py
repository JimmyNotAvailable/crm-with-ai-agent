"""
Full API Test Suite for CRM-AI-Agent
Tests all endpoints: Health, Auth, RAG Chat
"""
import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("1. HEALTH ENDPOINT")
    print("=" * 60)
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Response: {json.dumps(r.json(), indent=2)}")
        return r.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login():
    """Test authentication login"""
    print()
    print("=" * 60)
    print("2. AUTH LOGIN")
    print("=" * 60)
    try:
        r = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data={
                "username": "customer@example.com",
                "password": "password123"
            },
            timeout=10
        )
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            token_data = r.json()
            token = token_data.get("access_token", "")
            print(f"Token: {token[:50]}..." if len(token) > 50 else f"Token: {token}")
            return token
        else:
            print(f"Response: {r.text[:300]}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_rag_chat(token: str):
    """Test RAG chat endpoint"""
    print()
    print("=" * 60)
    print("3. RAG CHAT ENDPOINT")
    print("=" * 60)
    
    if not token:
        print("SKIP - No token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.post(
            f"{BASE_URL}/api/v1/rag/chat",
            headers=headers,
            data={"query": "Laptop gaming tầm 20 triệu"},
            timeout=30
        )
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            result = r.json()
            answer = result.get("answer", str(result))
            print(f"Answer preview: {answer[:300]}...")
            return True
        else:
            print(f"Response: {r.text[:500]}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_rag_chat_no_auth():
    """Test RAG chat without authentication"""
    print()
    print("=" * 60)
    print("4. RAG CHAT (NO AUTH)")
    print("=" * 60)
    
    try:
        r = requests.post(
            f"{BASE_URL}/api/v1/rag/chat",
            data={"query": "Chính sách bảo hành như thế nào?"},
            timeout=30
        )
        print(f"Status: {r.status_code}")
        
        if r.status_code == 401:
            print("Expected: 401 Unauthorized (auth required)")
            return True
        elif r.status_code == 200:
            result = r.json()
            answer = result.get("answer", str(result))
            print(f"Answer preview: {answer[:300]}...")
            return True
        else:
            print(f"Response: {r.text[:500]}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    print("CRM-AI-Agent Full API Test Suite")
    print("=" * 60)
    print("Make sure the server is running on http://127.0.0.1:8000")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Health", test_health()))
    token = test_login()
    results.append(("Login", token is not None))
    results.append(("RAG Chat (Auth)", test_rag_chat(token)))
    results.append(("RAG Chat (No Auth)", test_rag_chat_no_auth()))
    
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
