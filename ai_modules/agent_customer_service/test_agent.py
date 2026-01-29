#!/usr/bin/env python
"""
Test script for CustomerServiceAgent
Run: python ai_modules/agent_customer_service/test_agent.py
"""
import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai_modules.agent_customer_service.agent import CustomerServiceAgent

def test_agent_without_db():
    """
    Test agent với db=None
    Chỉ test RAG functionality (không cần DB)
    """
    print("=" * 60)
    print("Testing CustomerServiceAgent (RAG only, no DB)")
    print("=" * 60)
    
    # Create agent with db=None (RAG still works)
    agent = CustomerServiceAgent(db=None)
    
    test_queries = [
        ("Laptop gaming tầm 20 triệu", "product_search"),
        ("Chính sách đổi trả như thế nào?", "rag_query"),
        ("Laptop nào phù hợp cho lập trình?", "product_recommend"),
    ]
    
    for query, expected_intent in test_queries:
        print(f"\n[QUERY] {query}")
        print("-" * 40)
        
        try:
            result = agent.process_query(query, user_id=1)
            print(f"Success: {result.success}")
            print(f"Tool: {result.tool_used}")
            print(f"Intent (expected: {expected_intent})")
            if result.message:
                # Truncate long messages
                msg = result.message[:400] + "..." if len(result.message) > 400 else result.message
                print(f"Message: {msg}")
            if result.data:
                if "products" in result.data:
                    print(f"Products: {len(result.data['products'])} items")
                if "sources" in result.data:
                    print(f"Sources: {len(result.data['sources'])} docs")
                if "actions" in result.data:
                    actions = [a.get("label") for a in result.data["actions"]]
                    print(f"Actions: {actions}")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


def test_rag_service_direct():
    """Test RAGService directly"""
    print("=" * 60)
    print("Testing RAGService directly")
    print("=" * 60)
    
    from ai_modules.agent_customer_service.rag import RAGService
    
    rag = RAGService()
    
    queries = [
        "Laptop gaming tầm 20 triệu",
        "Chính sách bảo hành",
        "Laptop văn phòng cho sinh viên"
    ]
    
    for q in queries:
        print(f"\n[QUERY] {q}")
        print("-" * 40)
        result = rag.query(q)
        print(f"Sources: {len(result.get('sources', []))}")
        print(f"Confidence: {result.get('confidence', 0):.2f}")
        print(f"Answer: {result.get('answer', 'N/A')[:300]}...")


if __name__ == "__main__":
    # Test RAG first
    test_rag_service_direct()
    
    print("\n\n")
    
    # Test agent
    test_agent_without_db()
