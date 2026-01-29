"""Test login API"""
import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import requests
import json

BASE = "http://127.0.0.1:8000"

def test_login():
    """Test login with test user"""
    print("Testing login with test@example.com...")
    r = requests.post(f"{BASE}/auth/login", data={
        "username": "test@example.com",
        "password": "password123"
    }, timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print("LOGIN SUCCESS!")
        token = data.get("access_token", "")
        print(f"Token: {token[:50]}...")
        user = data.get("user", {})
        print(f"User email: {user.get('email')}")
        print(f"User type: {user.get('user_type')}")
        
        # Test RAG query with token (simple endpoint)
        print()
        print("Testing RAG /query endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        r2 = requests.post(f"{BASE}/rag/query", 
            headers=headers,
            data={"query": "Laptop gaming tầm 20 triệu", "top_k": 5},
            timeout=60
        )
        print(f"RAG Status: {r2.status_code}")
        if r2.status_code == 200:
            result = r2.json()
            print(f"Success: {result.get('success')}")
            print(f"Tool: {result.get('tool_used')}")
            answer = result.get('answer', '')
            print(f"Answer preview: {answer[:300]}...")
            return True
        else:
            print(f"RAG Error: {r2.text[:500]}")
            return False
    else:
        print(f"Response: {r.text[:500]}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Login API Test")
    print("=" * 60)
    print("Make sure the server is running on http://127.0.0.1:8000")
    print()
    
    success = test_login()
    print()
    print("=" * 60)
    print(f"Result: {'✓ PASSED' if success else '✗ FAILED'}")
    print("=" * 60)
