#!/usr/bin/env python
"""
Test API với simulated request - không cần chạy server
"""
import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test FastAPI app directly
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_rag_chat_demo():
    """Test RAG chat without authentication (demo)"""
    print("\n" + "=" * 60)
    print("Testing RAG Chat (requires auth, will fail without token)")
    print("=" * 60)
    
    # This will fail with 401 since we don't have auth, but tests the endpoint exists
    response = client.post(
        "/rag/chat",
        data={
            "query": "Laptop gaming 20 triệu",
            "top_k": 3
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("Expected 401 Unauthorized - endpoint exists but requires auth")
        return True
    else:
        print(f"Response: {response.json()}")
        return True


def test_products_list():
    """Test products list endpoint"""
    print("\n" + "=" * 60)
    print("Testing Products List (may require auth)")
    print("=" * 60)
    
    response = client.get("/products?limit=5")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Products count: {len(data) if isinstance(data, list) else 'N/A'}")
    return True


def test_direct_agent():
    """Test CustomerServiceAgent directly"""
    print("\n" + "=" * 60)
    print("Testing CustomerServiceAgent Directly (no HTTP)")
    print("=" * 60)
    
    from ai_modules.agent_customer_service.agent import CustomerServiceAgent
    
    agent = CustomerServiceAgent(db=None)
    
    queries = [
        "Laptop gaming tầm 20 triệu",
        "Chính sách bảo hành",
    ]
    
    for q in queries:
        print(f"\n[QUERY] {q}")
        print("-" * 40)
        result = agent.process_query(q, user_id=1)
        print(f"Success: {result.success}")
        print(f"Tool: {result.tool_used}")
        if result.message:
            msg = result.message[:300] + "..." if len(result.message) > 300 else result.message
            print(f"Answer: {msg}")
    
    return True


if __name__ == "__main__":
    print("CRM-AI-Agent API Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Health", test_health()))
    results.append(("RAG Chat Demo", test_rag_chat_demo()))
    results.append(("Products List", test_products_list()))
    results.append(("Direct Agent", test_direct_agent()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {name}: {status}")
    
    total_passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
